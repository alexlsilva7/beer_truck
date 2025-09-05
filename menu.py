import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24, GLUT_BITMAP_HELVETICA_12
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
        self.active_menu = "main"
        self.mouse_pressed = False
        self.clickable_areas = []

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
    """Desenha um botão com texto."""
    if is_pressed:
        color = COLOR_BUTTON_PRESSED
    elif is_hovered:
        color = COLOR_BUTTON_HOVER
    else:
        color = COLOR_BUTTON

    # Miolo preto para os botões
    draw_rect(x, y, width, height, (0, 0, 0))

    # Texto do botão (amarelo ao passar o mouse)
    text_x = x + width / 2
    text_y = y + (height - 18) / 2
    text_color = (1, 1, 0) if is_hovered else (1, 1, 1) # Amarelo se hovered, senão branco
    draw_text_centered(text, text_x, text_y, font=GLUT_BITMAP_HELVETICA_18, color=text_color)


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
    """Desenha a tela inicial do menu e registra os botões."""
    draw_menu_background()
    draw_title()
    menu_state.clickable_areas.clear()  # <-- 1. Limpa áreas da tela anterior

    # Exibe o Top 3
    draw_text_centered("TOP 3 RECORDES", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 180, font=GLUT_BITMAP_TIMES_ROMAN_24,
                       color=COLOR_HIGH_SCORE)

    if high_score_data and high_score_data["scores"]:
        positions = ["1º", "2º", "3º"]
        for i, score in enumerate(high_score_data["scores"]):
            y_pos = SCREEN_HEIGHT - 220 - (i * 30)
            score_text = f"{positions[i]}: {score['name']} - {score['score']}"
            draw_text_centered(score_text, SCREEN_WIDTH / 2, y_pos, color=COLOR_HIGH_SCORE)
    else:
        draw_text_centered("Nenhum recorde ainda! Seja o primeiro!", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 220,
                           color=COLOR_HIGH_SCORE)

    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2

    # Ajusta a posição dos botões para ficarem abaixo dos recordes
    button_base_y = SCREEN_HEIGHT / 2 - 50

    buttons = [
        {"text": "INICIAR JOGO", "y": button_base_y, "action": "start"},
        {"text": "COMO JOGAR", "y": button_base_y - 70, "action": "instructions"},
        {"text": "SAIR", "y": button_base_y - 140, "action": "quit"}
    ]

    for button in buttons:
        is_hovered = (button_x <= mouse_x <= button_x + button_width and
                      button["y"] <= mouse_y <= button["y"] + button_height)
        is_pressed = is_hovered and menu_state.mouse_pressed

        # <-- 2. Registra a área clicável de cada botão
        rect = (button_x, button["y"], button_width, button_height)
        menu_state.clickable_areas.append({'rect': rect, 'action': button['action']})

        draw_button(button_x, button["y"], button_width, button_height, button["text"], is_hovered, is_pressed)


def draw_instructions_screen(menu_state, mouse_x, mouse_y):
    """Desenha a tela de instruções em duas colunas."""
    draw_menu_background()
    menu_state.clickable_areas.clear()

    title_y = SCREEN_HEIGHT - 70
    draw_text_centered("COMO JOGAR", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

    # --- Configurações para as Colunas ---
    column_margin = 50
    column_width = (SCREEN_WIDTH / 2) - column_margin
    left_column_x = column_margin + 20 # Ajuste para o texto não colar na borda
    right_column_x = SCREEN_WIDTH / 2 + 20

    start_y = SCREEN_HEIGHT - 120
    line_height = 20
    instruction_font = GLUT_BITMAP_HELVETICA_12

    # Instruções divididas em duas listas (para as colunas)
    # Coluna Esquerda
    left_column_instructions = [
        "--- CONTROLES ---",
        "Teclado:",
        "Setas Direcionais: Mover/Acelerar/Frear",
        "Barra de Espaço: Buzina",
        "ESC: Pausar / Voltar ao Menu",
        "Alt + Enter: Alternar Tela Cheia",
        "",
        "Joystick:",
        "Analógico / D-Pad: Mover/Acelerar/Frear",
        "",
        "--- OBJETIVO ---",
        "Sobreviva o máximo possível!",
        "Desvie de carros, buracos e óleo.",
        "Colete cervejas e power-ups.",
        "Sua pontuação aumenta com a distância."
    ]

    # Coluna Direita
    right_column_instructions = [
        "--- ELEMENTOS DA PISTA ---",
        "Cerveja: Ganhe pontos extras!",
        "Mancha de Óleo: Controles invertidos por um tempo.",
        "Buraco: Velocidade reduzida temporariamente.",
        "Escudo (Power-up): Invencibilidade a batidas.",
        "",
        "--- INIMIGOS ---",
        "Outros Veículos: Desvie ou bata neles (cuidado!).",
        "Polícia: Vão te perseguir e tentar te parar!",
        "Evite colisões para não perder vidas!"
    ]

    # Desenhar Coluna Esquerda
    current_y = start_y
    for line in left_column_instructions:
        draw_text(line, left_column_x, current_y, font=instruction_font)
        current_y -= line_height

    # Desenhar Coluna Direita
    current_y = start_y
    for line in right_column_instructions:
        draw_text(line, right_column_x, current_y, font=instruction_font)
        current_y -= line_height

    # Botão de Voltar (centralizado abaixo das duas colunas)
    button_width = 200
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_y = 40

    is_hovered = (button_x <= mouse_x <= button_x + button_width and
                  button_y <= mouse_y <= button_y + button_height)
    is_pressed = is_hovered and menu_state.mouse_pressed

    rect = (button_x, button_y, button_width, button_height)
    menu_state.clickable_areas.append({'rect': rect, 'action': 'main'})

    draw_button(button_x, button_y, button_width, button_height, "VOLTAR", is_hovered, is_pressed)


def draw_game_over_menu(score, menu_state, mouse_x, mouse_y, top_scores=None, is_new_high_score=False, player_name=""):
    """Desenha a tela de game over e registra os botões."""
    draw_menu_background()
    menu_state.clickable_areas.clear()  # Limpa áreas da tela anterior

    title_y = SCREEN_HEIGHT - 150
    draw_text_centered("GAME OVER", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1.0, 0.3, 0.3))

    score_y = title_y - 60
    draw_text_centered(f"Sua pontuação: {int(score)}", SCREEN_WIDTH / 2, score_y)

    current_y = score_y - 40
    if top_scores:
        current_y -= 20
        draw_text_centered("TOP 3 RECORDES", SCREEN_WIDTH / 2, current_y, color=COLOR_HIGH_SCORE)
        current_y -= 10
        for i, score_data in enumerate(top_scores):
            current_y -= 30
            score_text = f"{i + 1}º: {score_data['name']} - {score_data['score']}"
            draw_text_centered(score_text, SCREEN_WIDTH / 2, current_y, color=COLOR_HIGH_SCORE)

    if is_new_high_score:
        current_y -= 40
        draw_text_centered("NOVO RECORDE!", SCREEN_WIDTH / 2, current_y, font=GLUT_BITMAP_TIMES_ROMAN_24,
                           color=COLOR_NEW_HIGH_SCORE)
        current_y -= 30
        if not player_name:
            draw_text_centered("Digite seu nome e pressione ENTER", SCREEN_WIDTH / 2, current_y)

    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_base_y = current_y - 80

    buttons = [
        {"text": "JOGAR NOVAMENTE", "y": button_base_y, "action": "restart"},
        {"text": "MENU PRINCIPAL", "y": button_base_y - 70, "action": "main"}
    ]

    for button in buttons:
        is_hovered = (button_x <= mouse_x <= button_x + button_width and
                      button["y"] <= mouse_y <= button["y"] + button_height)
        is_pressed = is_hovered and menu_state.mouse_pressed

        # Registra a área clicável antes de desenhar
        rect = (button_x, button["y"], button_width, button_height)
        menu_state.clickable_areas.append({'rect': rect, 'action': button['action']})

        draw_button(button_x, button["y"], button_width, button_height, button["text"], is_hovered, is_pressed)

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

def draw_pause_menu(menu_state, mouse_x, mouse_y):
    """Desenha a tela de pausa sobre o jogo."""
    menu_state.clickable_areas.clear()

    # --- Fundo semi-transparente ---
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(SCREEN_WIDTH, 0)
    glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
    glVertex2f(0, SCREEN_HEIGHT)
    glEnd()
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

    # --- Título ---
    title_y = SCREEN_HEIGHT - 200
    draw_text_centered("PAUSADO", SCREEN_WIDTH / 2, title_y, font=GLUT_BITMAP_TIMES_ROMAN_24, color=COLOR_TITLE)

    # --- Botões ---
    button_width = 250
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_base_y = SCREEN_HEIGHT / 2

    buttons = [
        {"text": "CONTINUAR", "y": button_base_y, "action": "resume"},
        {"text": "MENU PRINCIPAL", "y": button_base_y - 70, "action": "main"}
    ]

    for button in buttons:
        is_hovered = (button_x <= mouse_x <= button_x + button_width and
                      button["y"] <= mouse_y <= button["y"] + button_height)
        is_pressed = is_hovered and menu_state.mouse_pressed

        rect = (button_x, button["y"], button_width, button_height)
        menu_state.clickable_areas.append({'rect': rect, 'action': button['action']})

        draw_button(button_x, button["y"], button_width, button_height, button["text"], is_hovered, is_pressed)
