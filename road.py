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


def draw_road(scroll_offset):
    """Desenha todos os elementos da estrada."""

    # --- Fundo e Asfalto ---
    draw_rect(0, 0, GAME_WIDTH, SCREEN_HEIGHT, COLOR_GRASS)
    road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
    draw_rect(road_x_start, 0, ROAD_WIDTH, SCREEN_HEIGHT, COLOR_ASPHALT)

    # --- Linhas Contínuas ---
    line_width = 5
    draw_rect(road_x_start, 0, line_width, SCREEN_HEIGHT, COLOR_WHITE)
    draw_rect(road_x_start + ROAD_WIDTH - line_width, 0, line_width, SCREEN_HEIGHT, COLOR_WHITE)

    center_line_gap = 10
    center_x = GAME_WIDTH / 2
    draw_rect(center_x - center_line_gap / 2 - line_width, 0, line_width, SCREEN_HEIGHT, COLOR_YELLOW)
    draw_rect(center_x + center_line_gap / 2, 0, line_width, SCREEN_HEIGHT, COLOR_YELLOW)

    # --- Linhas Tracejadas das Faixas ---
    dash_height = 50
    gap_height = 30
    total_segment_height = dash_height + gap_height

    start_y = (scroll_offset % total_segment_height) - total_segment_height
    num_dashes = SCREEN_HEIGHT // total_segment_height + 2

    for i in range(1, TOTAL_LANES):
        if i == LANE_COUNT_PER_DIRECTION:
            continue

        lane_line_x = road_x_start + (i * LANE_WIDTH) - (line_width / 2)

        for j in range(num_dashes):
            y_pos = start_y + j * total_segment_height
            draw_rect(lane_line_x, y_pos, line_width, dash_height, COLOR_WHITE)
