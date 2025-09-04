from OpenGL.GL import *

# --- Configurações da Pista ---
PLAYER_SPEED = 0.18
GAME_WIDTH = 600
PANEL_WIDTH = 200
SCREEN_WIDTH = GAME_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = 600
ROAD_WIDTH = 500  # Largura total da pista de asfalto
LANE_COUNT_PER_DIRECTION = 3
TOTAL_LANES = LANE_COUNT_PER_DIRECTION * 2
LANE_WIDTH = ROAD_WIDTH / TOTAL_LANES

# --- Cores (formato R, G, B de 0.0 a 1.0) ---
COLOR_GRASS = (0.2, 0.6, 0.2)
COLOR_ASPHALT = (0.2, 0.2, 0.2)
COLOR_WHITE = (0.9, 0.9, 0.9)
COLOR_YELLOW = (1.0, 0.9, 0.0)
COLOR_PANEL = (0.1, 0.1, 0.1)


def draw_rect(x, y, width, height, color):
    """Desenha um retângulo com uma cor sólida."""
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()


def draw_road(scroll_offset, texture_id):
    """Desenha a pista usando uma única textura com rolagem."""

    # --- Fundo de Grama (continua igual) ---
    draw_rect(0, 0, GAME_WIDTH, SCREEN_HEIGHT, COLOR_GRASS)

    # --- Pista com Textura ---
    road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1.0, 1.0, 1.0)

    texture_y_offset = -scroll_offset / SCREEN_HEIGHT

    glBegin(GL_QUADS)
    # Canto inferior esquerdo
    glTexCoord2f(0.0, 0.0 + texture_y_offset);
    glVertex2f(road_x_start, 0)
    # Canto inferior direito
    glTexCoord2f(1.0, 0.0 + texture_y_offset);
    glVertex2f(road_x_start + ROAD_WIDTH, 0)
    # Canto superior direito
    # A coordenada Y da textura (V) é 1.0 para cobrir a tela inteira.
    glTexCoord2f(1.0, 1.0 + texture_y_offset);
    glVertex2f(road_x_start + ROAD_WIDTH, SCREEN_HEIGHT)
    # Canto superior esquerdo
    glTexCoord2f(0.0, 1.0 + texture_y_offset);
    glVertex2f(road_x_start, SCREEN_HEIGHT)
    glEnd()

    glDisable(GL_TEXTURE_2D)