import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from road import SCREEN_WIDTH, SCREEN_HEIGHT, draw_rect

# --- Cores para o Menu ---
COLOR_MENU_BG_TOP = (0.1, 0.1, 0.2)
COLOR_MENU_BG_BOTTOM = (0.2, 0.3, 0.5)
COLOR_TITLE = (1.0, 0.8, 0.2)
COLOR_BUTTON = (0.2, 0.6, 0.8)
COLOR_BUTTON_HOVER = (0.3, 0.7, 0.9)
COLOR_BUTTON_PRESSED = (0.1, 0.5, 0.7)
COLOR_TEXT = (1.0, 1.0, 1.0)

# --- Estado do Menu ---
class MenuState:
    def __init__(self):
        self.selected_button = 0
        self.active_menu = "main"  # "main", "instructions", "game_over"
        self.mouse_pressed = False

def draw_text(text, x, y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_TEXT):
    """Desenha um texto na tela."""
    glDisable(GL_TEXTURE_2D)
    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(font, ord(character))
    glEnable(GL_TEXTURE_2D)

def draw_text_centered(text, center_x, y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_TEXT):
    """Desenha texto centralizado horizontalmente."""
    text_bytes = text.encode('utf-8')
    text_ptr = (ctypes.c_ubyte * len(text_bytes))(*text_bytes)
    text_width = glutBitmapLength(font, text_ptr)
    x = center_x - text_width / 2
    draw_text(text, x, y, font, color)

def draw_button(x, y, width, height, text, is_hovered=False, is_pressed=False):
    """Desenha um botão com texto e bordas arredondadas."""
    if is_pressed:
        color = COLOR_BUTTON_PRESSED
    elif is_hovered:
        color = COLOR_BUTTON_HOVER
    else:
        color = COLOR_BUTTON

    # Miolo do botão
    draw_rect(x, y, width, height, color)

    # Borda do botão
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    glLineWidth(1.0)

    # Texto do botão
    text_x = x + width / 2
    text_y = y + (height - 12) / 2  # Centraliza o texto de 18px
    draw_text_centered(text, text_x, text_y, font=GLUT_BITMAP_HELVETICA_18)


def draw_title():
    """Desenha o título do jogo."""
    title_y = SCREEN_HEIGHT - 120
    draw_text_centered("BEER TRUCK", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

def draw_menu_background():
    """Desenha o fundo do menu com um gradiente."""
    glDisable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(*COLOR_MENU_BG_TOP)
    glVertex2f(0, SCREEN_HEIGHT)
    glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
    glColor3f(*COLOR_MENU_BG_BOTTOM)
    glVertex2f(SCREEN_WIDTH, 0)
    glVertex2f(0, 0)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D)


def draw_start_menu(menu_state, mouse_x, mouse_y):
    """Desenha a tela inicial do menu."""
    draw_menu_background()
    draw_title()

    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    
    buttons = [
        {"text": "INICIAR JOGO", "y": SCREEN_HEIGHT / 2, "action": "start"},
        {"text": "COMO JOGAR", "y": SCREEN_HEIGHT / 2 - 70, "action": "instructions"},
        {"text": "SAIR", "y": SCREEN_HEIGHT / 2 - 140, "action": "quit"}
    ]

    hovered_button = None
    for i, button in enumerate(buttons):
        is_hovered = (button_x <= mouse_x <= button_x + button_width and
                      button["y"] <= mouse_y <= button["y"] + button_height)
        
        is_pressed = is_hovered and menu_state.mouse_pressed
        
        draw_button(button_x, button["y"], button_width, button_height, button["text"], is_hovered, is_pressed)
        
        if is_hovered:
            hovered_button = button["action"]

    return hovered_button

def draw_instructions_screen(menu_state, mouse_x, mouse_y):
    """Desenha a tela de instruções."""
    draw_menu_background()

    title_y = SCREEN_HEIGHT - 100
    draw_text_centered("COMO JOGAR", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

    instructions_y = SCREEN_HEIGHT / 2 + 100
    instructions = [
        "Controles:",
        "Seta ESQUERDA/DIREITA - Mover o caminhão",
        "Seta CIMA - Acelerar",
        "Seta BAIXO - Frear",
        "ESC - Pausar / Voltar ao menu",
        "",
        "Objetivo:",
        "Desvie dos carros e sobreviva o máximo que puder!",
    ]

    for i, line in enumerate(instructions):
        draw_text_centered(line, SCREEN_WIDTH / 2, instructions_y - i * 30, font=GLUT_BITMAP_HELVETICA_18)

    # Botão de Voltar
    button_width = 200
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_y = 100
    
    is_hovered = (button_x <= mouse_x <= button_x + button_width and
                  button_y <= mouse_y <= button_y + button_height)
    is_pressed = is_hovered and menu_state.mouse_pressed

    draw_button(button_x, button_y, button_width, button_height, "VOLTAR", is_hovered, is_pressed)

    if is_hovered:
        return "main"
    return None


def draw_game_over_menu(score, menu_state, mouse_x, mouse_y):
    """Desenha a tela de game over."""
    draw_menu_background()

    title_y = SCREEN_HEIGHT - 150
    draw_text_centered("GAME OVER", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1.0, 0.3, 0.3))

    score_y = title_y - 80
    draw_text_centered(f"Sua pontuação: {int(score)}", SCREEN_WIDTH / 2, score_y, font=GLUT_BITMAP_HELVETICA_18)

    # Botões
    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2

    buttons = [
        {"text": "JOGAR NOVAMENTE", "y": SCREEN_HEIGHT / 2 - 50, "action": "restart"},
        {"text": "MENU PRINCIPAL", "y": SCREEN_HEIGHT / 2 - 120, "action": "main"}
    ]
    
    hovered_button = None
    for button in buttons:
        is_hovered = (button_x <= mouse_x <= button_x + button_width and
                      button["y"] <= mouse_y <= button["y"] + button_height)
        is_pressed = is_hovered and menu_state.mouse_pressed
        draw_button(button_x, button["y"], button_width, button_height, button["text"], is_hovered, is_pressed)
        if is_hovered:
            hovered_button = button["action"]
            
    return hovered_button
