from OpenGL.GL import *
import random
import math
import time
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox


class SlowMotionPowerUp:
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do power-up de slow motion na pista."""
        self.texture_id = texture_id
        # Tamanho do power-up, similar aos outros elementos
        self.width = LANE_WIDTH * 0.9  # 90% da largura da faixa
        self.height = 70
        self.speed_multiplier = speed_multiplier
        self.active = True  # Indica se o power-up ainda está ativo (não foi coletado)

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
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

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

    def draw(self):
        """Desenha o power-up na tela usando sua textura."""
        if not self.active:
            return

        # Salva o estado atual para não afetar outros objetos
        glPushMatrix()
        
        # Ativa blending para transparência
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Define a cor como branca para não afetar a textura
        glColor4f(1.0, 1.0, 1.0, 1.0)
        
        # Ativa o uso de texturas
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Move para a posição do power-up
        glTranslatef(self.x, self.y, 0)
        
        # Desenha o retângulo do power-up com a textura
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0, 0)
        
        glTexCoord2f(1.0, 1.0)
        glVertex2f(self.width, 0)
        
        glTexCoord2f(1.0, 0.0)
        glVertex2f(self.width, self.height)
        
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0, self.height)
        glEnd()
        
        # Desativa o uso de texturas e blending
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        
        # Restaura o estado anterior
        glPopMatrix()

    def get_collision_rect(self):
        """Retorna um retângulo (x, y, width, height) para detecção de colisão."""
        # Segue o mesmo padrão dos outros elementos do jogo
        powerup_hitbox_width = self.width / 1.0  # ← AJUSTÁVEL (mais generoso)
        powerup_hitbox_height = self.height / 1.0  # ← AJUSTÁVEL (mais generoso)
        
        powerup_hitbox_x = self.x + (self.width - powerup_hitbox_width) / 2
        powerup_hitbox_y = self.y + (self.height - powerup_hitbox_height) / 2
        
        return {
            'x': powerup_hitbox_x,
            'y': powerup_hitbox_y,
            'width': powerup_hitbox_width,
            'height': powerup_hitbox_height
        }

    def draw_hitbox(self):
        """Desenha a caixa de colisão do power-up para debug."""
        rect = self.get_collision_rect()
        draw_hitbox(rect['x'], rect['y'], rect['width'], rect['height'])

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
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
        self.active = False
        return self.points


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
        glEnable(GL_DEPTH_TEST)
