# Ficheiro: oil_stain.py
from OpenGL.GL import *
import random
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED


class OilStain:
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades da mancha de óleo na pista."""
        self.texture_id = texture_id
        # Tamanho da mancha de óleo, um pouco menor que o buraco
        self.width = LANE_WIDTH * 0.7  # 70% da largura da faixa
        self.height = 60
        self.speed_multiplier = speed_multiplier
        self.active = True  # Indica se a mancha ainda está ativa (não foi "consumida")

        road_x_start_total = (GAME_WIDTH - ROAD_WIDTH) / 2
        if lane_index is None:
            # Pode aparecer em qualquer faixa
            self.lane_index = random.randint(0, LANE_COUNT_PER_DIRECTION * 2 - 1)
        else:
            self.lane_index = lane_index

        # Velocidade da mancha deve ser EXATAMENTE igual à velocidade do scrolling da pista
        # para parecer fixa no chão
        self.speed_y = PLAYER_SPEED * speed_multiplier  # Será ajustada para a velocidade atual do scrolling

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        # Centraliza melhor a mancha na faixa
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

    def update(self, scroll_speed=None):
        """Move a mancha de óleo para baixo usando a velocidade atual do scrolling."""
        if self.active:
            if scroll_speed is not None:
                # Usa a velocidade de rolagem passada como parâmetro
                # Nota: scroll_speed é negativo (para baixo), então somamos para que a mancha desça
                self.y += scroll_speed
            else:
                # Usa a velocidade original se nenhuma velocidade de rolagem for fornecida
                self.y -= self.speed_y

    def draw(self):
        """Desenha a mancha de óleo na tela usando sua textura."""
        if not self.active:
            return
            
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Desenha a textura da mancha normalmente
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Cor normal
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
