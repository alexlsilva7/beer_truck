import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24
from road import SCREEN_WIDTH, SCREEN_HEIGHT, draw_rect
import high_score_manager  # Importa o gerenciador de recordes

# --- Cores para o Menu ---
COLOR_MENU_BG_TOP = (0.1, 0.1, 0.2)
COLOR_MENU_BG_BOTTOM = (0.2, 0.3, 0.5)
COLOR_TITLE = (1.0, 0.8, 0.2)
COLOR_BUTTON = (0.2, 0.6, 0.8)
COLOR_BUTTON_HOVER = (0.3, 0.7, 0.9)
COLOR_BUTTON_PRESSED = (0.1, 0.5, 0.7)
COLOR_TEXT = (1.0, 1.0, 1.0)
COLOR_HIGH_SCORE = (0.9, 0.9, 0.4)
COLOR_NEW_HIGH_SCORE = (1.0, 0.5, 0.3)
COLOR_INPUT_BOX = (0.1, 0.1, 0.1)
COLOR_INPUT_TEXT = (1.0, 1.0, 1.0)

# --- Estado do Menu ---
class MenuState:
    def __init__(self):
        self.selected_button = 0
        self.active_menu = "main"  # "main", "instructions", "game_over", "settings"
        self.mouse_pressed = False

def draw_text(text, x, y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_TEXT):
    """Desenha um texto na tela com coordenadas estáveis."""
    glDisable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    w = SCREEN_WIDTH
    h = SCREEN_HEIGHT
    glOrtho(0, w, 0, h, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Usa coordenadas inteiras para evitar vibração
    x = int(x)
    y = int(y)

    glColor3f(color[0], color[1], color[2])
    glRasterPos2i(x, y)  # Usa RasterPos2i em vez de RasterPos2f

    for character in text:
        glutBitmapCharacter(font, ord(character))

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)

def draw_text_centered(text, center_x, y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_TEXT):
    """Desenha texto centralizado horizontalmente com posição estável."""
    text_bytes = text.encode('utf-8')
    text_ptr = (ctypes.c_ubyte * len(text_bytes))(*text_bytes)
    text_width = glutBitmapLength(font, text_ptr)
    # Arredonda todas as coordenadas para valores inteiros
    x = int(center_x - text_width / 2)
    y = int(y)
    draw_text(text, x, y, font, color)

def draw_lives(lives, x, y, invulnerable=False):
    """Desenha as vidas do jogador usando símbolos simples."""
    # Desenha símbolos cheios para vidas restantes
    for i in range(lives):
        if invulnerable:
            # Pisca durante invulnerabilidade
            import time
            blink = int(time.time() * 6) % 2  # Pisca mais rápido
            color = (1.0, 1.0, 0.3) if blink else (1.0, 0.3, 0.3)  # Alterna entre amarelo e vermelho
        else:
            color = (1.0, 0.3, 0.3)  # Vermelho normal
        draw_text("*", x + i * 15, y, color=color)
    
    # Desenha símbolos vazios para vidas perdidas (máximo 3)
    for i in range(lives, 3):
        draw_text("o", x + i * 15, y, color=(0.5, 0.5, 0.5))

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


def draw_start_menu(menu_state, mouse_x, mouse_y, high_score_data=None):
    """Desenha a tela inicial do menu."""
    draw_menu_background()
    draw_title()

    # Exibe o Top 3
    draw_text_centered("TOP 3 RECORDES", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 180, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_HIGH_SCORE)

    if high_score_data and high_score_data["scores"]:
        positions = ["1º", "2º", "3º"]
        for i, score in enumerate(high_score_data["scores"]):
            y_pos = SCREEN_HEIGHT - 220 - (i * 30)
            score_text = f"{positions[i]}: {score['name']} - {score['score']}"
            draw_text_centered(score_text, SCREEN_WIDTH / 2, y_pos, color=COLOR_HIGH_SCORE)
    else:
        draw_text_centered("Nenhum recorde ainda! Seja o primeiro!", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 220, color=COLOR_HIGH_SCORE)

    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    
    # Ajusta a posição dos botões para ficarem abaixo dos recordes
    button_base_y = SCREEN_HEIGHT / 2 - 50

    buttons = [
        {"text": "INICIAR JOGO", "y": button_base_y, "action": "start"},
        {"text": "COMO JOGAR", "y": button_base_y - 70, "action": "instructions"},
        {"text": "CONFIGURACOES", "y": button_base_y - 140, "action": "settings"},
        {"text": "SAIR", "y": button_base_y - 210, "action": "quit"}
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

    # **CORREÇÃO APLICADA AQUI**
    is_hovered = (button_x <= mouse_x <= button_x + button_width and
                  button_y <= mouse_y <= button_y + button_height)
    is_pressed = is_hovered and menu_state.mouse_pressed

    draw_button(button_x, button_y, button_width, button_height, "VOLTAR", is_hovered, is_pressed)

    if is_hovered:
        return "main"
    return None


def draw_game_over_menu(score, menu_state, mouse_x, mouse_y, top_scores=None, is_new_high_score=False, player_name=""):
    """Desenha a tela de game over."""
    draw_menu_background()

    title_y = SCREEN_HEIGHT - 150
    draw_text_centered("GAME OVER", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1.0, 0.3, 0.3))

    # Pontuação atual
    score_y = title_y - 60
    draw_text_centered(f"Sua pontuação: {int(score)}", SCREEN_WIDTH / 2, score_y, font=GLUT_BITMAP_HELVETICA_18)

    # Top 3 recordes
    if top_scores:
        positions = ["1º", "2º", "3º"]
        high_score_y = score_y - 40
        draw_text_centered("TOP 3 RECORDES", SCREEN_WIDTH / 2, high_score_y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_HIGH_SCORE)

        for i, score_data in enumerate(top_scores):
            y_pos = high_score_y - 30 - (i * 30)
            score_text = f"{positions[i]}: {score_data['name']} - {score_data['score']}"
            draw_text_centered(score_text, SCREEN_WIDTH / 2, y_pos, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_HIGH_SCORE)

    # Destaque para novo high score
    if is_new_high_score:
        new_hs_y = high_score_y - 120  # Ajustado para ficar abaixo do top 3
        draw_text_centered("NOVO RECORDE!", SCREEN_WIDTH / 2, new_hs_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_NEW_HIGH_SCORE)
        instructions_y = new_hs_y - 40
        if not player_name:  # Só mostra a mensagem se o jogador ainda não começou a digitar
            draw_text_centered("Digite seu nome e pressione ENTER", SCREEN_WIDTH / 2, instructions_y, font=GLUT_BITMAP_HELVETICA_18)

    # Botões
    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2

    # Ajusta a posição dos botões se for um novo high score
    button_offset = 0
    if is_new_high_score:
        button_offset = -80

    buttons = [
        {"text": "JOGAR NOVAMENTE", "y": SCREEN_HEIGHT / 2 - 50 + button_offset, "action": "restart"},
        {"text": "MENU PRINCIPAL", "y": SCREEN_HEIGHT / 2 - 120 + button_offset, "action": "main"}
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

def draw_high_scores_screen(high_scores, menu_state, mouse_x, mouse_y):
    """Desenha a tela de high scores."""
    draw_menu_background()

    title_y = SCREEN_HEIGHT - 150
    draw_text_centered("HIGH SCORES", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

    # Exibe os high scores
    for i, score in enumerate(high_scores):
        score_y = title_y - 50 - i * 30
        draw_text_centered(f"{i + 1}. {score}", SCREEN_WIDTH / 2, score_y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_HIGH_SCORE)

    # Destaque para nova pontuação mais alta
    if len(high_scores) > 0 and high_scores[-1] == max(high_scores):
        new_high_score_y = title_y - 50 - len(high_scores) * 30
        draw_text_centered("Novo Recorde!", SCREEN_WIDTH / 2, new_high_score_y, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_NEW_HIGH_SCORE)

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

def draw_name_input_screen(menu_state, mouse_x, mouse_y, input_text=""):
    """Desenha a tela de entrada de nome para o high score."""
    draw_menu_background()

    title_y = SCREEN_HEIGHT - 150
    draw_text_centered("SEU NOME", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

    # Caixa de entrada de texto
    input_box_x = (SCREEN_WIDTH - 400) / 2
    input_box_y = SCREEN_HEIGHT / 2 - 25
    draw_rect(input_box_x, input_box_y, 400, 50, COLOR_INPUT_BOX)

    # Texto do input
    draw_text_centered(input_text, SCREEN_WIDTH / 2, input_box_y + 10, font=GLUT_BITMAP_HELVETICA_18, color=COLOR_INPUT_TEXT)

    # Botões
    button_width = 200
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_y = 100

    # **CORREÇÃO APLICADA AQUI**
    is_hovered_confirm = (button_x <= mouse_x <= button_x + button_width and
                          button_y <= mouse_y <= button_y + button_height)
    is_pressed_confirm = is_hovered_confirm and menu_state.mouse_pressed

    draw_button(button_x, button_y, button_width, button_height, "CONFIRMAR", is_hovered_confirm, is_pressed_confirm)

    if is_hovered_confirm:
        return "high_scores"

    # Botão de Voltar
    is_hovered_back = (button_x <= mouse_x <= button_x + button_width and
                       button_y + 70 <= mouse_y <= button_y + 70 + button_height)
    is_pressed_back = is_hovered_back and menu_state.mouse_pressed

    draw_button(button_x, button_y + 70, button_width, button_height, "VOLTAR", is_hovered_back, is_pressed_back)

    if is_hovered_back:
        return "main"

    return None