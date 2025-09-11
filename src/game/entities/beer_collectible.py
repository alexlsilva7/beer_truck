import random

from src.game.entities.base_drawable import DrawableGameObject
from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, \
    PLAYER_SPEED
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox


class BeerCollectible(DrawableGameObject):
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do objeto de cerveja coletável."""
        # Tamanho do objeto de cerveja - aumentado horizontalmente
        width = LANE_WIDTH * 0.8  # 80% da largura da faixa (era 50%)
        height = 60  # Aumentado ligeiramente a altura também
        self.speed_multiplier = speed_multiplier
        self.points = 100  # Pontos que o jogador ganha ao coletar

        road_x_start_total = (GAME_WIDTH - ROAD_WIDTH) / 2
        if lane_index is None:
            # Pode aparecer em qualquer faixa
            self.lane_index = random.randint(0, LANE_COUNT_PER_DIRECTION * 2 - 1)
        else:
            self.lane_index = lane_index

        # Velocidade do objeto deve ser EXATAMENTE igual à velocidade do scrolling da pista
        # para parecer fixo no chão
        self.speed_y = PLAYER_SPEED * speed_multiplier  # Será ajustada para a velocidade atual do scrolling

        lane_x_start = road_x_start_total + self.lane_index * LANE_WIDTH
        # Centraliza o objeto na faixa
        x = lane_x_start + (LANE_WIDTH - width) / 2
        y = SCREEN_HEIGHT

        # Chama o construtor da classe base
        super().__init__(texture_id, x, y, width, height)

    def update(self, scroll_speed=None):
        """Move o objeto de cerveja para baixo usando a velocidade atual do scrolling."""
        if self.active:
            if scroll_speed is not None:
                # Usa a velocidade de rolagem passada como parâmetro
                # Nota: scroll_speed é negativo (para baixo), então somamos para que o objeto desça
                self.y += scroll_speed
            else:
                # Usa a velocidade original se nenhuma velocidade de rolagem for fornecida
                self.y -= self.speed_y

    def check_collision(self, truck):
        """Verifica se o caminhão colidiu com o objeto de cerveja usando hitboxes mais precisas."""
        if not self.active:
            return False
        
        # Calcula a hitbox efetiva da cerveja (usando os mesmos valores do debug)
        beer_hitbox_width = self.width / 1.4  # Aumentado de 2.5 para 1.4
        beer_hitbox_height = self.height / 1.3  # Aumentado de 2.7 para 1.3
        
        beer_hitbox_x = self.x + (self.width - beer_hitbox_width) / 2
        beer_hitbox_y = self.y + (self.height - beer_hitbox_height) / 2
        
        # Calcula a hitbox efetiva do caminhão (usando os mesmos valores do debug)
        truck_hitbox_width = truck.width / 1.3  # Atualizado para coincidir com o truck.py
        truck_hitbox_height = truck.height / 1.2  # Atualizado para coincidir com o truck.py
        
        truck_hitbox_x = truck.x + (truck.width - truck_hitbox_width) / 2
        truck_hitbox_y = truck.y + (truck.height - truck_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (beer_hitbox_x < truck_hitbox_x + truck_hitbox_width and
                beer_hitbox_x + beer_hitbox_width > truck_hitbox_x and
                beer_hitbox_y < truck_hitbox_y + truck_hitbox_height and
                beer_hitbox_y + beer_hitbox_height > truck_hitbox_y)

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        if not self.active:
            return
            
        # Desenha o retângulo completo do sprite (vermelho para cerveja)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(1.0, 0.0, 0.0, 0.8), line_width=2)
        
        if show_collision_area:
            # Calcula a hitbox REAL que é usada para colisão
            beer_hitbox_width = self.width / 1.4
            beer_hitbox_height = self.height / 1.3
            beer_hitbox_x = self.x + (self.width - beer_hitbox_width) / 2
            beer_hitbox_y = self.y + (self.height - beer_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (amarelo brilhante para cerveja)
            draw_real_hitbox(beer_hitbox_x, beer_hitbox_y, beer_hitbox_width, beer_hitbox_height,
                           color=(1.0, 1.0, 0.0, 1.0))

    def collect(self):
        """Marca o objeto como coletado e retorna os pontos."""
        if self.active:
            self.active = False
            return self.points
        return 0
