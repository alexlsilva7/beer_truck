from OpenGL.GL import *
import random
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED
from src.utils.debug_utils import draw_hitbox, draw_collision_area, draw_real_hitbox
from src.game.entities.base_drawable import DrawableGameObject


class Enemy(DrawableGameObject):
    def __init__(self, texture_id, dead_texture_id=None, is_up_lane=True, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do inimigo com uma textura específica."""
        self.dead_texture_id = dead_texture_id
        self.width = 50
        self.height = 100
        self.speed_multiplier = speed_multiplier
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
            # Velocidade ajustada para inimigos na contramão (menos rápida)
            self.speed_y = random.uniform(0.02, 0.07) + (speed_multiplier * 0.03)
        else:
            # Velocidade ajustada para inimigos na mesma direção (mais rápida)
            self.speed_y = (PLAYER_SPEED + random.uniform(0.02, 0.1)) * speed_multiplier

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        x = lane_x_start + (LANE_WIDTH - self.width) / 2
        y = SCREEN_HEIGHT

        # Chama o construtor da classe base
        super().__init__(texture_id, x, y, self.width, self.height)

    def update(self, all_enemies, speed_multiplier=1.0):
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

        # Aplica o multiplicador de velocidade adicional (usado quando o player está crashado)
        self.y -= self.speed_y * speed_multiplier

    def draw(self):
        """Desenha o inimigo na tela usando sua textura."""
        # Altera a textura a ser usada se o inimigo estiver crashado e tiver uma textura 'dead'
        if self.crashed and self.dead_texture_id:
            current_texture = self.dead_texture_id
            # Salva a textura original
            original_texture = self.texture_id
            # Atualiza temporariamente a textura para desenhar
            self.texture_id = current_texture

            # Chama o metodo draw da classe base
            super().draw()

            # Restaura a textura original
            self.texture_id = original_texture
        else:
            # Se não está crashado ou não tem textura de dead, usa o draw normal da classe base
            super().draw()


    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        # Desenha o retângulo completo do sprite (azul para inimigos)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(0.0, 0.0, 1.0, 0.8), line_width=2)
        
        if show_collision_area:
            # Calcula a hitbox REAL que é usada para colisão (igual ao truck)
            enemy_hitbox_width = self.width / 1.3
            enemy_hitbox_height = self.height / 1.05
            enemy_hitbox_x = self.x + (self.width - enemy_hitbox_width) / 2
            enemy_hitbox_y = self.y + (self.height - enemy_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (magenta para inimigos)
            draw_real_hitbox(enemy_hitbox_x, enemy_hitbox_y, enemy_hitbox_width, enemy_hitbox_height,
                           color=(1.0, 0.0, 1.0, 1.0))


class EnemyDown(Enemy):
    def __init__(self, texture_id, dead_texture_id=None, lane_index=None, speed_multiplier=1.0):
        """Inicializa um inimigo que aparece nas faixas da esquerda."""
        super().__init__(texture_id, dead_texture_id, is_up_lane=False, lane_index=lane_index, speed_multiplier=speed_multiplier)