# Ficheiro: police.py
from OpenGL.GL import *
from road import SCREEN_HEIGHT, ROAD_WIDTH, GAME_WIDTH
import random


class PoliceCar:
    def __init__(self, textures):
        """
        Inicializa o carro da polícia.
        textures: Dicionário com 'normal_1', 'normal_2', 'dead'.
        """
        self.textures = textures
        self.current_texture_id = self.textures['normal_1']

        self.width = 50
        self.height = 100

        # Inicia fora da tela, na parte de baixo
        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        road_x_end = road_x_start + ROAD_WIDTH - self.width
        self.x = random.uniform(road_x_start, road_x_end)
        self.y = -self.height

        self.speed_y = 0.12  # Velocidade vertical para alcançar o jogador
        self.chase_speed_x = 0.08  # Suavidade do movimento horizontal
        self.crashed = False

        # Controle de animação das luzes
        self.animation_timer = 0
        self.animation_speed = 100  # Troca de frame a cada 15 updates

    def draw(self):
        """Desenha o carro da polícia na tela."""
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Usa a textura de destruído se colidiu
        current_texture = self.textures['dead'] if self.crashed else self.current_texture_id
        glBindTexture(GL_TEXTURE_2D, current_texture)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1);
        glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1);
        glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0);
        glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0);
        glVertex2f(self.x, self.y + self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def _animate(self):
        """Alterna entre as texturas para criar o efeito de luzes piscando."""
        self.animation_timer += 1
        if self.animation_timer > self.animation_speed:
            self.animation_timer = 0
            if self.current_texture_id == self.textures['normal_1']:
                self.current_texture_id = self.textures['normal_2']
            else:
                self.current_texture_id = self.textures['normal_1']

    def _check_rear_end_collision(self, target):
        """Verifica colisão traseira. A polícia só bate por trás."""

        # 1. Verifica se estão na mesma "coluna" horizontal
        is_horizontally_aligned = (self.x < target.x + target.width and self.x + self.width > target.x)

        # 2. Verifica se a frente da polícia está prestes a tocar ou já tocou a traseira do alvo
        is_vertically_close = (self.y + self.height >= target.y and self.y < target.y)

        return is_horizontally_aligned and is_vertically_close

    def update(self, player_truck, all_enemies, scroll_speed):
        """Atualiza a posição e o estado do carro da polícia."""
        if self.crashed:
            # Se colidiu, é empurrado para fora da tela pelo scroll
            self.y += scroll_speed
            return

        self._animate()

        # --- Lógica de Perseguição ---
        # 1. Movimento vertical constante para cima
        self.y += self.speed_y

        # 2. Persegue o jogador no eixo X de forma suave
        target_x = player_truck.x
        # Interpola suavemente a posição X atual em direção ao alvo
        self.x += (target_x - self.x) * self.chase_speed_x

        # Mantém o carro dentro dos limites da pista
        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        min_x = road_x_start
        max_x = road_x_start + ROAD_WIDTH - self.width
        if self.x < min_x: self.x = min_x
        if self.x > max_x: self.x = max_x

        # --- Lógica de Colisão ---
        # A polícia pode colidir com o jogador ou com outros carros
        potential_targets = all_enemies + [player_truck]

        for target in potential_targets:
            if target.crashed:
                continue

            if self._check_rear_end_collision(target):
                # Marca o alvo como colidido
                target.crashed = True
                # Se o alvo for o jogador, a polícia também "morre" na colisão
                if target is player_truck:
                    self.crashed = True
                # Para de verificar outras colisões neste frame para evitar colisões múltiplas
                break