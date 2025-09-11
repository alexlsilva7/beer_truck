# Ficheiro: hole.py
from OpenGL.GL import *
import random
import math
import time
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED
from src.utils.collision_utils import check_rect_collision
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox


class Hole:
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do buraco na pista."""
        self.texture_id = texture_id
        # Tamanho aumentado para ocupar mais da faixa, mas sem exagero
        self.width = LANE_WIDTH * 0.75  # 75% da largura da faixa
        self.height = 70  # Altura um pouco maior
        self.speed_multiplier = speed_multiplier
        self.active = True  # Indica se o buraco ainda está ativo (não foi "consumido")

        road_x_start_total = (GAME_WIDTH - ROAD_WIDTH) / 2
        if lane_index is None:
            # Pode aparecer em qualquer faixa
            self.lane_index = random.randint(0, LANE_COUNT_PER_DIRECTION * 2 - 1)
        else:
            self.lane_index = lane_index

        # Velocidade do buraco deve ser EXATAMENTE igual à velocidade do scrolling da pista
        # para parecer fixo no chão
        self.speed_y = PLAYER_SPEED * speed_multiplier  # Será ajustada para a velocidade atual do scrolling

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        # Centraliza melhor o buraco na faixa
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

    def update(self, scroll_speed=None):
        """Move o buraco para baixo usando a velocidade atual do scrolling."""
        if self.active:
            if scroll_speed is not None:
                # Usa a velocidade de rolagem passada como parâmetro
                # Nota: scroll_speed é negativo (para baixo), então somamos para que o buraco desça
                self.y += scroll_speed
            else:
                # Usa a velocidade original se nenhuma velocidade de rolagem for fornecida
                self.y -= self.speed_y

    def draw(self):
        """Desenha o buraco na tela usando sua textura."""
        if not self.active:
            return
            
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Removido o efeito pulsante conforme solicitado
        # Removido o fundo preto/cinza conforme solicitado
        
        # Desenha a textura do buraco normalmente
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Cor normal sem efeito de pulsação
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        glDisable(GL_BLEND)
        
    def check_collision_with_object(self, obj):
        """
        Verifica se este buraco colide com outro objeto (como uma mancha de óleo).
        
        Args:
            obj: Objeto a verificar colisão (deve ter propriedades x, y, width, height)
            
        Returns:
            True se colidir, False caso contrário
        """
        if not self.active or not obj.active:
            return False
            
        return check_rect_collision(
            self.x, self.y, self.width, self.height,
            obj.x, obj.y, obj.width, obj.height
        )

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        if not self.active:
            return
            
        # Desenha o retângulo completo do sprite (marrom para buraco)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(0.6, 0.3, 0.0, 0.8), line_width=2)
        
        if show_collision_area:
            # Para buracos, usa a área completa como hitbox (pode ser ajustado)
            hole_hitbox_width = self.width / 1.6  # ← VOCÊ PODE ALTERAR AQUI
            hole_hitbox_height = self.height / 1.5  # ← VOCÊ PODE ALTERAR AQUI
            hole_hitbox_x = self.x + (self.width - hole_hitbox_width) / 2
            hole_hitbox_y = self.y + (self.height - hole_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (marrom brilhante para buraco)
            draw_real_hitbox(hole_hitbox_x, hole_hitbox_y, hole_hitbox_width, hole_hitbox_height,
                           color=(1.0, 0.5, 0.0, 1.0))
