from OpenGL.GL import *
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT


class Truck:
    def __init__(self, texture_id):
        """Inicializa as propriedades do caminhão."""
        self.texture_id = texture_id
        self.width = 50
        self.height = 100
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.speed_x = 2.0
        self.speed_y = 3.0
        self.crashed = False

    def draw(self):
        """Desenha o caminhão na tela usando sua textura."""
        # Habilita o uso de texturas e blending (para transparência)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glBegin(GL_QUADS)
        # Define os cantos da textura e do retângulo
        # (0,1) é o canto superior esquerdo da imagem
        glTexCoord2f(0, 1)
        glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1)
        glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0)
        glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0)
        glVertex2f(self.x, self.y + self.height)
        glEnd()


        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def move(self, dx, dy):
        """Move o caminhão nas direções x e y."""
        self.x += dx * self.speed_x
        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        min_x = road_x_start
        max_x = road_x_start + ROAD_WIDTH - self.width
        if self.x < min_x: self.x = min_x
        if self.x > max_x: self.x = max_x

        self.y += dy * self.speed_y

        # Reset se sair da tela
        if self.y > SCREEN_HEIGHT or self.y + self.height < 0:
            self.reset()

    def check_collision(self, other):
        """Verifica a colisão com outro objeto (inimigo)."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def reset(self):
        """Reseta o caminhão para a posição inicial."""
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.crashed = False