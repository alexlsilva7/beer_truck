import random

from src.game.entities.base_drawable import DrawableGameObject
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, \
    PLAYER_SPEED
from src.utils.collision_utils import check_rect_collision
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox


class OilStain(DrawableGameObject):
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades da mancha de óleo na pista."""
        # Tamanho da mancha de óleo, um pouco menor que o buraco
        width = LANE_WIDTH * 0.7  # 70% da largura da faixa
        height = 60
        self.speed_multiplier = speed_multiplier

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
        x = lane_x_start + (LANE_WIDTH - width) / 2
        y = SCREEN_HEIGHT

        # Chama o construtor da classe base
        super().__init__(texture_id, x, y, width, height)

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

    def check_collision_with_object(self, obj):
        """
        Verifica se esta mancha de óleo colide com outro objeto (como um buraco).
        
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

        # Desenha o retângulo completo do sprite (roxo para óleo)
        draw_hitbox(self.x, self.y, self.width, self.height,
                    color=(0.5, 0.0, 0.5, 0.8), line_width=2)

        if show_collision_area:
            # Para óleo, usa uma hitbox ligeiramente menor
            oil_hitbox_width = self.width / 1.2  # ← VOCÊ PODE ALTERAR AQUI
            oil_hitbox_height = self.height / 1.2  # ← VOCÊ PODE ALTERAR AQUI
            oil_hitbox_x = self.x + (self.width - oil_hitbox_width) / 2
            oil_hitbox_y = self.y + (self.height - oil_hitbox_height) / 2

            # Desenha a hitbox REAL de colisão (roxo brilhante para óleo)
            draw_real_hitbox(oil_hitbox_x, oil_hitbox_y, oil_hitbox_width, oil_hitbox_height,
                             color=(1.0, 0.0, 1.0, 1.0))
