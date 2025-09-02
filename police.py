# Ficheiro: police.py
from OpenGL.GL import *
from road import SCREEN_HEIGHT, ROAD_WIDTH, GAME_WIDTH
import random
import threading
import audio_manager

def preload_police_sound(path, create_loop=True):
    return audio_manager.preload_sound(path, create_loop=create_loop)

def get_preloaded_police_sounds(path):
    return audio_manager.get_preloaded_sounds(path)

class PoliceCar:
    def __init__(self, textures, sound_path=None, sound_loop=True):
        """
        Inicializa o carro da polícia.
        textures: Dicionário com 'normal_1', 'normal_2', 'dead'.
        sound_path: caminho para o arquivo WAV.
        sound_loop: se True, reproduz a versão de loop após o segmento inicial.
        """
        self.textures = textures
        self.current_texture_id = self.textures['normal_1']

        self.width = 50
        self.height = 100

        # Inicia fora da tela
        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        road_x_end = road_x_start + ROAD_WIDTH - self.width
        self.x = random.uniform(road_x_start, road_x_end)
        self.y = -self.height

        self.speed_y = 0.12
        self.chase_speed_x = 0.08
        self.crashed = False

        # Animação
        self.animation_timer = 0
        self.animation_speed = 100

        # Áudio
        self.sound_path = sound_path
        self._player = None
        self._player_lock = threading.Lock()

        if self.sound_path:
            try:
                self._player = audio_manager.SoundPlayer(self.sound_path, use_loop=sound_loop)
                self._player.start()
            except Exception as e:
                print(f"Failed to start police sound: {e}")

    def draw(self):
        """Desenha o carro da polícia na tela."""
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        current_texture = self.textures['dead'] if self.crashed else self.current_texture_id
        glBindTexture(GL_TEXTURE_2D, current_texture)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1)
        glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0)
        glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0)
        glVertex2f(self.x, self.y + self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def _animate(self):
        self.animation_timer += 1
        if self.animation_timer > self.animation_speed:
            self.animation_timer = 0
            if self.current_texture_id == self.textures['normal_1']:
                self.current_texture_id = self.textures['normal_2']
            else:
                self.current_texture_id = self.textures['normal_1']

    def _is_playing(self):
        try:
            if not self._player:
                return False
            return self._player.is_playing()
        except Exception:
            return False

    def _start_player(self):
        try:
            if self._player and not self._player.is_playing():
                self._player.start()
        except Exception:
            pass

    def stop_audio(self):
        """Para a reprodução do som associado (se houver)."""
        try:
            if self._player:
                self._player.stop()
        except Exception:
            pass
        finally:
            self._player = None

    def _check_rear_end_collision(self, target):
        is_horizontally_aligned = (self.x < target.x + target.width and self.x + self.width > target.x)
        is_vertically_close = (self.y + self.height >= target.y and self.y < target.y)
        return is_horizontally_aligned and is_vertically_close

    def update(self, player_truck, all_enemies, scroll_speed):
        if self.crashed:
            try:
                self.stop_audio()
            except Exception:
                pass
            self.y += scroll_speed
            return

        self._animate()

        # Movimento vertical e perseguição horizontal
        self.y += self.speed_y
        target_x = player_truck.x
        self.x += (target_x - self.x) * self.chase_speed_x

        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        min_x = road_x_start
        max_x = road_x_start + ROAD_WIDTH - self.width
        if self.x < min_x: self.x = min_x
        if self.x > max_x: self.x = max_x

        potential_targets = all_enemies + [player_truck]
        for target in potential_targets:
            if target.crashed:
                continue
            if self._check_rear_end_collision(target):
                target.crashed = True
                if target is player_truck:
                    self.crashed = True
                break