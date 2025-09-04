from OpenGL.GL import *
import random
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT, LANE_WIDTH, LANE_COUNT_PER_DIRECTION, PLAYER_SPEED


class BeerCollectible:
    def __init__(self, texture_id, lane_index=None, speed_multiplier=1.0):
        """Inicializa as propriedades do objeto de cerveja coletável."""
        self.texture_id = texture_id
        # Tamanho do objeto de cerveja - aumentado horizontalmente
        self.width = LANE_WIDTH * 0.8  # 80% da largura da faixa (era 50%)
        self.height = 60  # Aumentado ligeiramente a altura também
        self.speed_multiplier = speed_multiplier
        self.active = True  # Indica se o objeto ainda está ativo (não foi coletado)
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
        self.x = lane_x_start + (LANE_WIDTH - self.width) / 2
        self.y = SCREEN_HEIGHT

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
    
    def draw(self):
        """Desenha o objeto de cerveja na tela usando sua textura."""
        if not self.active:
            return
        
        # Salva o estado atual para não afetar outros objetos
        glPushMatrix()
        glPushAttrib(GL_ALL_ATTRIB_BITS)
            
        # Desabilita depth test para garantir que a transparência funcione
        glDisable(GL_DEPTH_TEST)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Desenha a textura do objeto normalmente
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Cor branca para não alterar a textura
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height)
        glEnd()

        # Restaura o estado anterior
        glPopAttrib()
        glPopMatrix()

    def check_collision(self, truck):
        """Verifica se o caminhão colidiu com o objeto de cerveja."""
        if not self.active:
            return False
            
        return (self.x < truck.x + truck.width and
                self.x + self.width > truck.x and
                self.y < truck.y + truck.height and
                self.y + self.height > truck.y)

    def collect(self):
        """Marca o objeto como coletado e retorna os pontos."""
        if self.active:
            self.active = False
            return self.points
        return 0
