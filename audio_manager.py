# Gerencia pré-carregamento e reprodução de sons (pygame.mixer) de forma genérica.
# API pública:
#   preload_sound(path) -> threading.Event
#   get_preloaded_sounds(path) -> (full_sound, loop_sound, tmp_path)
#   SoundPlayer(path) -> objeto com .start(), .stop(), .is_playing()
#   stop_all() -> para todos os players ativos
import threading
import wave
import tempfile
import os
import time
import pygame

def _resolve_path(path):
    """Resolve caminhos relativos (ex: 'assets/sound/crash.wav') para base do projeto.
    Se já for absoluto, retorna inalterado.
    """
    try:
        if not path:
            return path
        if os.path.isabs(path):
            return path
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, path)
    except Exception:
        return path

_audio_cache = {}  # path -> {"full": Sound|None, "loop": Sound|None, "tmp": path|None, "ready_event": Event, "lock": Lock}
_audio_cache_lock = threading.Lock()

_players_lock = threading.Lock()
_active_players = set()


def _ensure_mixer_initialized(framerate=None, sampwidth=None, nchannels=None):
    """Inicializa pygame.mixer se necessário, tentando usar parâmetros do WAV quando disponíveis."""
    try:
        if not pygame.mixer.get_init():
            if framerate is None:
                pygame.mixer.init()
            else:
                size = -8 * sampwidth if sampwidth and sampwidth > 1 else 8
                pygame.mixer.init(frequency=framerate, size=size, channels=nchannels or 2)
    except Exception as e:
        # Falha na inicialização do mixer não deve quebrar o jogo; apenas logamos.
        print(f"Warning: pygame.mixer.init failed: {e}")


def preload_sound(path, create_loop=True):
    """
    Inicia (assíncrono) o pré-carregamento do áudio para evitar I/O bloqueante no spawn.
    Se create_loop=False, apenas carrega a versão "full" e não cria o tmp/loop.
    Retorna um threading.Event que será setado quando o som estiver pronto no cache.
    Aceita caminhos relativos ao diretório deste módulo.
    """
    path = _resolve_path(path)
    with _audio_cache_lock:
        entry = _audio_cache.get(path)
        if entry:
            return entry["ready_event"]
        ready_ev = threading.Event()
        _audio_cache[path] = {
            "full": None, "loop": None, "tmp": None,
            "ready_event": ready_ev, "lock": threading.Lock(),
            "create_loop": create_loop
        }

    def _bg_load():
        try:
            with _audio_cache[path]["lock"]:
                # Re-check
                if _audio_cache[path]["full"]:
                    _audio_cache[path]["ready_event"].set()
                    return
                # Lê header para inicializar mixer com parâmetros adequados
                try:
                    with wave.open(path, 'rb') as wf:
                        nch = wf.getnchannels()
                        sw = wf.getsampwidth()
                        fr = wf.getframerate()
                        _ensure_mixer_initialized(framerate=fr, sampwidth=sw, nchannels=nch)
                except Exception as e:
                    print(f"Failed to read wave during preload: {e}")

                # Carrega full sound
                try:
                    full = pygame.mixer.Sound(path)
                    _audio_cache[path]["full"] = full
                except Exception as e:
                    print(f"Failed to preload full sound: {e}")
                    _audio_cache[path]["full"] = None

                # Se a chamada solicitou criar loop, tenta criar o tmp/loop; caso contrário, ignora
                try:
                    if create_loop:
                        with wave.open(path, 'rb') as wf:
                            framerate = wf.getframerate()
                            nframes = wf.getnframes()
                            start_frame = int(4 * framerate)
                            if start_frame < nframes:
                                wf.setpos(start_frame)
                                loop_frames = wf.readframes(nframes - start_frame)
                                if loop_frames:
                                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                                    tmp_name = tmp.name
                                    tmp.close()
                                    with wave.open(tmp_name, 'wb') as outw:
                                        outw.setnchannels(wf.getnchannels())
                                        outw.setsampwidth(wf.getsampwidth())
                                        outw.setframerate(wf.getframerate())
                                        outw.writeframes(loop_frames)
                                    _audio_cache[path]["tmp"] = tmp_name
                                    try:
                                        loop = pygame.mixer.Sound(tmp_name)
                                        _audio_cache[path]["loop"] = loop
                                    except Exception as e:
                                        print(f"Failed to preload loop sound: {e}")
                                        _audio_cache[path]["loop"] = _audio_cache[path]["full"]
                                else:
                                    _audio_cache[path]["loop"] = _audio_cache[path]["full"]
                            else:
                                _audio_cache[path]["loop"] = _audio_cache[path]["full"]
                    else:
                        _audio_cache[path]["loop"] = _audio_cache[path]["full"]
                except Exception as e:
                    print(f"Failed to create preload loop sound: {e}")
                    _audio_cache[path]["loop"] = _audio_cache[path]["full"]
        finally:
            try:
                _audio_cache[path]["ready_event"].set()
            except Exception:
                pass

    t = threading.Thread(target=_bg_load, daemon=True)
    t.start()
    return _audio_cache[path]["ready_event"]


def get_preloaded_sounds(path):
    """Retorna (full_sound, loop_sound, tmp_path) se já estiverem carregados, senão (None, None, None)."""
    path = _resolve_path(path)
    with _audio_cache_lock:
        entry = _audio_cache.get(path)
        if not entry:
            return (None, None, None)
        return (entry.get("full"), entry.get("loop"), entry.get("tmp"))


class SoundPlayer:
    """
    Gerencia reprodução de um som:
      - Toca a versão "full" uma vez (se existir)
      - Em seguida toca a versão de "loop" repetidamente (se existir)
    O loop é reproduzido até chamar .stop()
    """

    def __init__(self, path, use_loop=True):
        path = _resolve_path(path)
        self.path = path
        self._use_loop = bool(use_loop)
        self._full = None
        self._loop = None
        self._loop_tmp = None
        self._own_tmp = False
        self._stop_event = threading.Event()
        self._audio_lock = threading.Lock()
        self._audio_channel = None
        self._thread = None

        full, loop, tmp = get_preloaded_sounds(path)
        self._full = full
        # honor use_loop: if user doesn't want loop, ignore preloaded loop
        self._loop = loop if self._use_loop else None
        self._loop_tmp = tmp if self._use_loop else None

    def _ensure_loaded_sync(self):
        """Se não estão pré-carregados, carrega de forma síncrona (menor prioridade)."""
        # Ensure full always loaded when requested
        if self._full is None:
            try:
                try:
                    with wave.open(self.path, 'rb') as wf:
                        nch = wf.getnchannels()
                        sw = wf.getsampwidth()
                        fr = wf.getframerate()
                        _ensure_mixer_initialized(framerate=fr, sampwidth=sw, nchannels=nch)
                except Exception:
                    _ensure_mixer_initialized()
                try:
                    self._full = pygame.mixer.Sound(self.path)
                except Exception as e:
                    print(f"Failed to load full sound on-demand: {e}")
                    self._full = None
            except Exception:
                pass

        # If loop not desired, skip loop creation entirely
        if not self._use_loop:
            self._loop = None
            return

        # Create loop if missing
        if self._loop is None:
            try:
                with wave.open(self.path, 'rb') as wf:
                    framerate = wf.getframerate()
                    nframes = wf.getnframes()
                    start_frame = int(4 * framerate)
                    if start_frame < nframes:
                        wf.setpos(start_frame)
                        loop_frames = wf.readframes(nframes - start_frame)
                        if loop_frames:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                            tmp_name = tmp.name
                            tmp.close()
                            with wave.open(tmp_name, 'wb') as outw:
                                outw.setnchannels(wf.getnchannels())
                                outw.setsampwidth(wf.getsampwidth())
                                outw.setframerate(wf.getframerate())
                                outw.writeframes(loop_frames)
                            self._loop_tmp = tmp_name
                            self._own_tmp = True
                            try:
                                self._loop = pygame.mixer.Sound(self._loop_tmp)
                            except Exception as e:
                                print(f"Failed to load loop sound on-demand: {e}")
                                self._loop = self._full
                        else:
                            self._loop = self._full
                    else:
                        self._loop = self._full
            except Exception as e:
                print(f"Failed to create loop sound on-demand: {e}")
                self._loop = self._full

    def _is_playing_channel(self, ch):
        try:
            return ch is not None and getattr(ch, "get_busy", lambda: False)()
        except Exception:
            return False

    def _run(self):
        self._stop_event.clear()
        try:
            # Ensure resources loaded
            self._ensure_loaded_sync()

            # play full once
            if self._full:
                try:
                    ch = self._full.play()
                    with self._audio_lock:
                        self._audio_channel = ch
                    while not self._stop_event.is_set() and self._is_playing_channel(ch):
                        time.sleep(0.1)
                except Exception as e:
                    print(f"Audio play error (full): {e}")
                finally:
                    try:
                        with self._audio_lock:
                            if self._audio_channel is ch:
                                self._audio_channel = None
                    except Exception:
                        pass

            # play loop
            if self._loop:
                try:
                    ch = self._loop.play(loops=-1)
                    with self._audio_lock:
                        self._audio_channel = ch
                    while not self._stop_event.is_set():
                        time.sleep(0.1)
                    try:
                        if ch.get_busy():
                            ch.stop()
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Audio play error (loop): {e}")
                finally:
                    try:
                        with self._audio_lock:
                            if self._audio_channel is ch:
                                self._audio_channel = None
                    except Exception:
                        pass
        finally:
            # cleanup only for own tmp
            try:
                if self._own_tmp and self._loop_tmp and os.path.isfile(self._loop_tmp):
                    try:
                        os.unlink(self._loop_tmp)
                    except Exception:
                        pass
                    self._loop_tmp = None
            except Exception:
                pass
            try:
                with self._audio_lock:
                    self._audio_channel = None
            except Exception:
                pass
            # remove from active players
            with _players_lock:
                _active_players.discard(self)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        # Register
        with _players_lock:
            _active_players.add(self)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        # Signal stop
        try:
            self._stop_event.set()
        except Exception:
            pass

        play_to_stop = None
        try:
            with self._audio_lock:
                play_to_stop = self._audio_channel
                self._audio_channel = None
        except Exception:
            play_to_stop = None

        try:
            if play_to_stop and self._is_playing_channel(play_to_stop):
                try:
                    play_to_stop.stop()
                except Exception:
                    pass
        except Exception:
            pass

    def is_playing(self):
        try:
            with self._audio_lock:
                ch = self._audio_channel
            return self._is_playing_channel(ch)
        except Exception:
            return False


# Background music helpers using pygame.mixer.music (streaming, low memory)
_bg_lock = threading.Lock()
_bg_current_path = None

def play_background_music(path, volume=0.8, fade_ms=500, loop=True):
    """
    Reproduz música de fundo usando pygame.mixer.music (streaming).
    Não reinicia se a mesma música já estiver tocando.
    Retorna True em sucesso, False caso contrário.
    Aceita caminho relativo.
    """
    global _bg_current_path
    path = _resolve_path(path)
    try:
        _ensure_mixer_initialized()
        with _bg_lock:
            try:
                if _bg_current_path == path and pygame.mixer.music.get_busy():
                    # Ajusta volume caso solicitem sem reiniciar
                    try:
                        pygame.mixer.music.set_volume(volume)
                    except Exception:
                        pass
                    return True

                # Carrega e toca
                pygame.mixer.music.load(path)
                try:
                    pygame.mixer.music.set_volume(volume)
                except Exception:
                    pass
                loops = -1 if loop else 0
                # play aceita fade_ms em pygame 2.x através de keyword em alguns sistemas;
                # usamos play + fadeout/fade como fallback onde necessário.
                try:
                    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                except TypeError:
                    # fallback se play não aceitar fade_ms
                    pygame.mixer.music.play(loops=loops)
                    if fade_ms and fade_ms > 0:
                        try:
                            pygame.mixer.music.set_volume(0.0)
                            # simple linear fade-in on a separate thread would be better; keep minimal
                            pygame.mixer.music.set_volume(volume)
                        except Exception:
                            pass

                _bg_current_path = path
                return True
            except Exception as e:
                print(f"Failed to play background music via mixer.music: {e}")
                return False
    except Exception as e:
        print(f"play_background_music error: {e}")
        return False

def stop_background_music(fade_ms=500):
    """
    Para a música de fundo. Se fade_ms > 0 tenta fadeout, senão stop direto.
    """
    global _bg_current_path
    try:
        with _bg_lock:
            try:
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    if fade_ms and fade_ms > 0:
                        try:
                            pygame.mixer.music.fadeout(fade_ms)
                        except Exception:
                            pygame.mixer.music.stop()
                    else:
                        pygame.mixer.music.stop()
            except Exception:
                pass
            _bg_current_path = None
    except Exception as e:
        print(f"stop_background_music error: {e}")

def is_background_music_playing():
    try:
        return pygame.mixer.get_init() and pygame.mixer.music.get_busy()
    except Exception:
        return False


def stop_all():
    """Para todos os players ativos."""
    with _players_lock:
        players = list(_active_players)
    for p in players:
        try:
            p.stop()
        except Exception:
            pass

def play_one_shot(path):
    """Toca um som uma vez (não em loop). Retorna o SoundPlayer ou None em falha.
    Aceita caminho relativo.
    """
    try:
        player = SoundPlayer(path, use_loop=False)  # SoundPlayer já resolve o caminho
        player.start()
        return player
    except Exception as e:
        try:
            print(f"play_one_shot error: {e}")
        except Exception:
            pass
        return None