# Ficheiro: enemy.py
from OpenGL.GL import *
import random
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED


class Enemy:
    def __init__(self, texture_id, is_up_lane=True, lane_index=None):
        """Inicializa as propriedades do inimigo com uma textura específica."""
        self.texture_id = texture_id
        self.width = 50
        self.height = 100
        self.crashed = False

        road_x_start_total = (GAME_WIDTH - ROAD_WIDTH) / 2
        if lane_index is None:
            if is_up_lane:
                # Faixas da direita (contramão)
                self.lane_index = random.randint(LANE_COUNT_PER_DIRECTION, LANE_COUNT_PER_DIRECTION * 2 - 1)
            else:
                # Faixas da esquerda (mesma direção)
                self.lane_index = random.randint(0, LANE_COUNT_PER_DIRECTION - 1)
        else:
            self.lane_index = lane_index

        if is_up_lane:
            # Velocidade alta (velocidade do jogador + velocidade própria)
            self.speed_y = PLAYER_SPEED + random.uniform(0.1, 0.3)
        else:
            # Velocidade menor que a do jogador
            self.speed_y = random.uniform(0.05, PLAYER_SPEED - 0.05)

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

    def update(self, all_enemies):
        """Move o inimigo e evita colisões com outros inimigos."""
        if self.crashed:
            return

        # Lógica para evitar passar por cima de outros inimigos
        for other in all_enemies:
            if self == other or self.lane_index != other.lane_index or other.crashed:
                continue

            # Verifica se 'other' está na frente e muito perto
            if self.y > other.y:
                distance = self.y - (other.y + other.height)
                if distance < 10:  # Pequena distância de segurança
                    # Reduz a velocidade para a do carro da frente
                    if self.speed_y > other.speed_y:
                        self.speed_y = other.speed_y

        self.y -= self.speed_y

    def draw(self):
        """Desenha o inimigo na tela usando sua textura."""
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)


class EnemyDown(Enemy):
    def __init__(self, texture_id, lane_index=None):
        """Inicializa um inimigo que aparece nas faixas da esquerda."""
        super().__init__(texture_id, is_up_lane=False, lane_index=lane_index)