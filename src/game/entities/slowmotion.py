from OpenGL.GL import *
import random
import math
import time
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox
from src.game.entities.base_drawable import DrawableGameObject


class SlowMotionPowerUp(DrawableGameObject):
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do power-up de slow motion na pista."""
        # Tamanho do power-up, similar aos outros elementos
        width = LANE_WIDTH * 0.9  # 90% da largura da faixa
        height = 70
        self.speed_multiplier = speed_multiplier
        self.points = 0  # Não dá pontos, apenas efeito

        road_x_start_total = (GAME_WIDTH - ROAD_WIDTH) / 2
        if lane_index is None:
            # Pode aparecer em qualquer faixa
            self.lane_index = random.randint(0, LANE_COUNT_PER_DIRECTION * 2 - 1)
        else:
            self.lane_index = lane_index

        # Velocidade do power-up deve ser EXATAMENTE igual à velocidade do scrolling da pista
        # para parecer fixo no chão
        self.speed_y = PLAYER_SPEED * speed_multiplier  # Será ajustada para a velocidade atual do scrolling

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        # Centraliza melhor o power-up na faixa
        x = lane_x_start + (LANE_WIDTH - width) / 2
        y = SCREEN_HEIGHT

        # Chama o construtor da classe base
        super().__init__(texture_id, x, y, width, height)

    def update(self, scroll_speed=None):
        """Move o power-up para baixo usando a velocidade atual do scrolling."""
        if self.active:
            if scroll_speed is not None:
                # Usa a velocidade de rolagem passada como parâmetro
                # Nota: scroll_speed é negativo (para baixo), então somamos para que o power-up desça
                self.y += scroll_speed
            else:
                # Usa a velocidade original se nenhuma velocidade de rolagem for fornecida
                self.y -= self.speed_y

    def check_collision(self, truck):
        """Verifica se o caminhão colidiu com o power-up usando hitboxes mais precisas."""
        if not self.active:
            return False

        # Calcula a hitbox efetiva do power-up
        powerup_hitbox_width = self.width / 1.6  # ← AJUSTÁVEL (mais generoso)
        powerup_hitbox_height = self.height / 1.6  # ← AJUSTÁVEL (mais generoso)

        powerup_hitbox_x = self.x + (self.width - powerup_hitbox_width) / 2
        powerup_hitbox_y = self.y + (self.height - powerup_hitbox_height) / 2

        # Calcula a hitbox efetiva do caminhão (usando os mesmos valores do truck.py)
        truck_hitbox_width = truck.width / 1.3  # Atualizado para coincidir com o truck.py
        truck_hitbox_height = truck.height / 1.2  # Atualizado para coincidir com o truck.py

        truck_hitbox_x = truck.x + (truck.width - truck_hitbox_width) / 2
        truck_hitbox_y = truck.y + (truck.height - truck_hitbox_height) / 2

        # Verifica sobreposição dos retângulos das hitboxes
        return (powerup_hitbox_x < truck_hitbox_x + truck_hitbox_width and
                powerup_hitbox_x + powerup_hitbox_width > truck_hitbox_x and
                powerup_hitbox_y < truck_hitbox_y + truck_hitbox_height and
                powerup_hitbox_y + powerup_hitbox_height > truck_hitbox_y)

    def get_collision_rect(self):
        """Retorna um retângulo (x, y, width, height) para detecção de colisão."""
        # Segue o mesmo padrão dos outros elementos do jogo
        powerup_hitbox_width = self.width / 1.6  # ← AJUSTÁVEL (mais generoso)
        powerup_hitbox_height = self.height / 1.6  # ← AJUSTÁVEL (mais generoso)

        powerup_hitbox_x = self.x + (self.width - powerup_hitbox_width) / 2
        powerup_hitbox_y = self.y + (self.height - powerup_hitbox_height) / 2
        
        return {
            'x': powerup_hitbox_x,
            'y': powerup_hitbox_y,
            'width': powerup_hitbox_width,
            'height': powerup_hitbox_height
        }

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        if not self.active:
            return

        # Desenha o contorno do power-up (roxo para slow motion)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(0.8, 0.0, 0.8, 0.8), line_width=2)
        
        if show_collision_area:
            # Segue o mesmo padrão dos outros elementos do jogo
            powerup_hitbox_width = self.width / 1.6  # ← AJUSTÁVEL (mais generoso)
            powerup_hitbox_height = self.height / 1.6  # ← AJUSTÁVEL (mais generoso)
            
            powerup_hitbox_x = self.x + (self.width - powerup_hitbox_width) / 2
            powerup_hitbox_y = self.y + (self.height - powerup_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (roxo brilhante para slow motion power-up)
            draw_real_hitbox(powerup_hitbox_x, powerup_hitbox_y, powerup_hitbox_width, powerup_hitbox_height,
                           color=(1.0, 0.0, 1.0, 1.0))

    def collect(self):
        """Marca o power-up como coletado e inativo."""
        if self.active:
            self.active = False
            return self.points
        return 0


class SlowMotionEffect:
    def __init__(self, duration=3.0, slowdown_factor=0.3):
        """
        Inicializa o efeito de slow motion.
        
        Args:
            duration: Duração do efeito em segundos (padrão: 2.0)
            slowdown_factor: Fator de desaceleração (0.3 = 30% da velocidade normal)
        """
        self.duration = duration
        self.slowdown_factor = slowdown_factor
        self.active = False
        self.start_time = 0.0
        self.remaining_time = 0.0

    def activate(self, current_time):
        """Ativa o efeito de slow motion."""
        self.active = True
        self.start_time = current_time
        self.remaining_time = self.duration

    def update(self, current_time):
        """Atualiza o estado do efeito de slow motion."""
        if self.active:
            elapsed_time = current_time - self.start_time
            self.remaining_time = max(0.0, self.duration - elapsed_time)
            
            if self.remaining_time <= 0.0:
                self.active = False
                return False
        return self.active

    def deactivate(self):
        """Desativa o efeito de slow motion."""
        self.active = False
        self.remaining_time = 0.0

    def is_active(self):
        """Retorna se o efeito está ativo."""
        return self.active

    def get_speed_multiplier(self):
        """Retorna o multiplicador de velocidade atual."""
        return self.slowdown_factor if self.active else 1.0

    def get_remaining_time(self):
        """Retorna o tempo restante do efeito."""
        return self.remaining_time

    def draw_overlay(self, screen_width, screen_height):
        """Desenha o filtro azulado na tela quando o efeito está ativo."""
        # Filtro visual removido - mantém apenas a funcionalidade de slow motion
        return
