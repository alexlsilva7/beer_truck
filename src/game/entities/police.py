# Ficheiro: police.py
from OpenGL.GL import *
from src.game.entities.road import SCREEN_HEIGHT, ROAD_WIDTH, GAME_WIDTH, PLAYER_SPEED
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox
import random
import threading
import src.game.managers.audio_manager as audio_manager

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
                self._player = audio_manager.SoundPlayer(self.sound_path, use_loop=sound_loop, volume=0.7)
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
        # Calcula as hitboxes efetivas da polícia
        police_hitbox_width = self.width / 1.3  # Ajustável
        police_hitbox_height = self.height / 1.1  # ← SINCRONIZADO COM O CAMINHÃO
        police_hitbox_x = self.x + (self.width - police_hitbox_width) / 2
        police_hitbox_y = self.y + (self.height - police_hitbox_height) / 2
        
        # Calcula as hitboxes efetivas do alvo
        target_hitbox_width = target.width / 1.3
        target_hitbox_height = target.height / 1.1  # ← SINCRONIZADO COM O CAMINHÃO
        target_hitbox_x = target.x + (target.width - target_hitbox_width) / 2
        target_hitbox_y = target.y + (target.height - target_hitbox_height) / 2
        
        # Verifica sobreposição das hitboxes
        return (police_hitbox_x < target_hitbox_x + target_hitbox_width and
                police_hitbox_x + police_hitbox_width > target_hitbox_x and
                police_hitbox_y < target_hitbox_y + target_hitbox_height and
                police_hitbox_y + police_hitbox_height > target_hitbox_y)

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        # Desenha o retângulo completo do sprite (azul para polícia)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(0.0, 0.0, 1.0, 0.8), line_width=2)
        
        if show_collision_area:
            # Calcula a hitbox REAL que é usada para colisão
            police_hitbox_width = self.width / 1.3  # ← VOCÊ PODE ALTERAR AQUI
            police_hitbox_height = self.height / 1.1  # ← SINCRONIZADO COM A COLISÃO REAL
            police_hitbox_x = self.x + (self.width - police_hitbox_width) / 2
            police_hitbox_y = self.y + (self.height - police_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (azul brilhante para polícia)
            draw_real_hitbox(police_hitbox_x, police_hitbox_y, police_hitbox_width, police_hitbox_height,
                           color=(0.0, 0.5, 1.0, 1.0))

    def update(self, player_truck, all_enemies, scroll_speed):
        if self.crashed:
            try:
                self.stop_audio()
            except Exception:
                pass
            self.y += scroll_speed
            return None

        self._animate()

        # Extrai o multiplicador de velocidade do scroll_speed se for diferente do valor padrão
        speed_multiplier = 1.0
        default_scroll = -PLAYER_SPEED
        if abs(scroll_speed) > abs(default_scroll):
            speed_multiplier = abs(scroll_speed / default_scroll)

        # Movimento vertical e perseguição horizontal com velocidade ajustada
        self.y += self.speed_y * speed_multiplier
        target_x = player_truck.x
        self.x += (target_x - self.x) * self.chase_speed_x * speed_multiplier

        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        min_x = road_x_start
        max_x = road_x_start + ROAD_WIDTH - self.width
        if self.x < min_x: self.x = min_x
        if self.x > max_x: self.x = max_x

        potential_targets = all_enemies + [player_truck]
        for target in potential_targets:
            if self._check_rear_end_collision(target):
                if target is player_truck:
                    # Só processa colisão com o jogador se ele não estiver invulnerável (exceto quando blindado)
                    if not target.invulnerable or target.armored:
                        target.take_damage()
                        self.crashed = True
                        try:
                            self.stop_audio()
                        except Exception:
                            pass
                        try:
                            audio_manager.play_one_shot("assets/sound/crash.wav")
                        except Exception as e:
                            print(f"Failed to play crash sound for police: {e}")
                        
                        # Retorna informação de pontuação se o jogador está blindado
                        if target.armored:
                            return {"points_awarded": True, "points": 100, "x": self.x, "y": self.y}
                        else:
                            target.crashed = True
                            return None
                else:
                    target.crashed = True
                    try:
                        self.stop_audio()
                    except Exception:
                        pass
                    try:
                        audio_manager.play_one_shot("assets/sound/crash.wav")
                    except Exception as e:
                        print(f"Failed to play crash sound for police: {e}")
                break
        
        return None