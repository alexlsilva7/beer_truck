from OpenGL.GL import *

class DrawableGameObject:
    """
    Classe base para objetos do jogo que podem ser desenhados na tela.
    Fornece funcionalidade comum de renderização para reduzir duplicação de código.
    """
    def __init__(self, texture_id, x, y, width, height):
        self.texture_id = texture_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True

    def draw(self):
        """Desenha o objeto na tela usando sua textura."""
        if not self.active:
            return

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Garante que a cor está resetada
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height)
        glEnd()

        # Reseta a cor para não afetar outros elementos
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
