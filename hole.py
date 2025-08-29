# Ficheiro: hole.py
from OpenGL.GL import *
import random
import math
import time
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED


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

        # Velocidade do buraco (mesma do scrolling para parecer fixo na pista)
        self.speed_y = PLAYER_SPEED * speed_multiplier

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        # Centraliza melhor o buraco na faixa
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

    def update(self):
        """Move o buraco para baixo."""
        if self.active:
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
