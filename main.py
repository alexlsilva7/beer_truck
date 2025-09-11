import math
import time
import random

import glfw
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18  # Importação explícita para evitar erro

import src.game.entities.police as police
import src.game.entities.road as road
import src.game.managers.audio_manager as audio_manager
from src.game.entities.beer_collectible import BeerCollectible
from src.game.entities.enemy import Enemy, EnemyDown
from src.game.entities.hole import Hole
from src.game.entities.invulnerability import InvulnerabilityPowerUp
from src.game.entities.oil_stain import OilStain
from src.game.entities.road import draw_road, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, PANEL_WIDTH, COLOR_PANEL, \
    draw_rect, PLAYER_SPEED, \
    LANE_COUNT_PER_DIRECTION
from src.game.entities.truck import Truck
from src.game.managers.difficulty_manager import DifficultyManager
from src.game.managers.high_score_manager import HighScoreManager
from src.ui.menu import MenuState, draw_start_menu, draw_instructions_screen, draw_game_over_menu, \
    draw_name_input_screen, draw_pause_menu
from src.ui.score_indicator import ScoreIndicator
from src.utils.texture_loader import load_texture

# --- Estados do Jogo ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_PAUSED = 3

# --- Debug ---
DEBUG_SHOW_HITBOXES = False  # Pressione 'H' para alternar

# --- Variáveis Globais para Toggle Borderless ---
is_borderless = False
_prev_window_pos = (0, 0)
_prev_window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

def toggle_borderless(window):
    """Alterna entre modo janela normal e borderless fullscreen (com fallbacks seguros)."""
    global is_borderless, _prev_window_pos, _prev_window_size

    monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(monitor)

    # Obtém largura, altura e refresh
    vm_width = int(video_mode.size.width)
    vm_height = int(video_mode.size.height)
    vm_refresh = int(video_mode.refresh_rate)

    if is_borderless:
        # Volta para modo janela (restaura posição/tamanho anteriores)
        glfw.set_window_monitor(window, None,
                                _prev_window_pos[0], _prev_window_pos[1],
                                _prev_window_size[0], _prev_window_size[1],
                                vm_refresh)
        glfw.set_window_attrib(window, glfw.DECORATED, glfw.TRUE)
        is_borderless = False
        print("Switched to windowed mode")
    else:
        # Salva estado atual e entra em borderless fullscreen cobrindo o monitor primário
        try:
            _prev_window_pos = glfw.get_window_pos(window)
            _prev_window_size = glfw.get_window_size(window)
        except Exception:
            _prev_window_pos = (0, 0)
            _prev_window_size = (vm_width, vm_height)

        monitor_x, monitor_y = glfw.get_monitor_pos(monitor)
        glfw.set_window_monitor(window, monitor,
                               monitor_x, monitor_y,
                               vm_width, vm_height,
                               vm_refresh)
        glfw.set_window_attrib(window, glfw.DECORATED, glfw.FALSE)
        is_borderless = True
        print("Switched to borderless fullscreen")

# --- Variáveis Globais ---
scroll_pos = 0.0
scroll_speed = -PLAYER_SPEED
safety_distance = 180
CRASH_SCROLL_MULTIPLIER = 2.0  # Multiplicador de velocidade durante respawn (2x mais rápido)
difficulty_manager = DifficultyManager()
high_score_manager = HighScoreManager("data/highscores.json")  # Especifica o caminho para a pasta data
current_game_state = GAME_STATE_MENU
menu_state = MenuState()
police_car = None  # Variável para controlar o carro da polícia

# Variáveis para cálculo de viewport e coordenadas do mouse, acessadas por callbacks
current_scale = 1.0
current_offset = (0.0, 0.0)
fb_height = SCREEN_HEIGHT

# --- Constantes da Polícia ---
POLICE_SPAWN_SCORE_THRESHOLD = 0
POLICE_COOLDOWN_SECONDS = 10  # Tempo mínimo entre dois spawns de polícia (segundos)
last_police_spawn_time = -9999.0  # Guarda o tempo do último spawn (usamos glfw.get_time())

player_name = ""
asking_for_name = False
new_high_score = False
holes = []  # Lista para armazenar os buracos na pista
hole_spawn_timer = 0  # Temporizador para spawn de buracos
oil_stains = []  # Lista para armazenar as manchas de óleo na pista
oil_stain_spawn_timer = 0  # Temporizador para spawn de manchas de óleo
beer_collectibles = []  # Lista para armazenar os objetos de cerveja coletáveis
beer_spawn_timer = 0  # Temporizador para spawn de cervejas
invulnerability_powerups = []  # Lista para armazenar os power-ups de invulnerabilidade
invulnerability_spawn_timer = 0  # Temporizador para spawn de power-ups
score_indicators = []  # Lista para armazenar os indicadores de pontos
pending_score_bonus = 0  # Pontos bônus pendentes para aplicação gradual
beer_bonus_points = 0  # Pontos ganhos com cerveja (separado do scroll_pos)

# --- Callbacks de Input ---
def key_callback(window, key, scancode, action, mods):
    global current_game_state, difficulty_manager, player_name, asking_for_name, new_high_score
    print(f"Key event: key={key}, action={action}, mods={mods}")

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        if current_game_state == GAME_STATE_PLAYING:
            current_game_state = GAME_STATE_PAUSED
        elif current_game_state == GAME_STATE_PAUSED:
            current_game_state = GAME_STATE_PLAYING
        elif current_game_state == GAME_STATE_MENU:
            if menu_state.active_menu == "instructions":
                menu_state.active_menu = "main"
            else:
                glfw.set_window_should_close(window, True)
        elif current_game_state == GAME_STATE_GAME_OVER and asking_for_name:
            asking_for_name = False
            player_name = ""

    # Controle da entrada do nome do jogador
    if asking_for_name and action == glfw.PRESS:
        if key == glfw.KEY_BACKSPACE and len(player_name) > 0:
            player_name = player_name[:-1]
        elif key == glfw.KEY_ENTER:
            # Finaliza a entrada do nome e salva o high score
            if len(player_name) > 0:
                score = abs(scroll_pos * 0.1) + beer_bonus_points
                high_score_manager.add_high_score(player_name, int(score))
                asking_for_name = False
        elif 32 <= key <= 126:  # ASCII imprimível (espaço até ~)
            # Limita o tamanho do nome a 15 caracteres
            if len(player_name) < 15:
                player_name += chr(key)

    # Buzina: tecla Espaço toca o som, salvo quando digitando o nome
    if key == glfw.KEY_SPACE and action == glfw.PRESS and not asking_for_name:
        try:
            audio_manager.play_one_shot("assets/sound/horn.mp3", volume=0.7)
        except Exception as e:
            print(f"Erro ao tocar buzina: {e}")

    # Toggle borderless fullscreen com Alt+Enter
    if action == glfw.PRESS and (mods & glfw.MOD_ALT) and key == glfw.KEY_ENTER:
        toggle_borderless(window)

    # Controles manuais para dificuldade (F1-F11)
    if action == glfw.PRESS:
        if key == glfw.KEY_F1:
            difficulty_manager.adjust_scroll_speed_multiplier(0.1)
        elif key == glfw.KEY_F2:
            difficulty_manager.adjust_scroll_speed_multiplier(-0.1)
        elif key == glfw.KEY_F3:
            # Diminuir spawn_rate_multiplier => spawn mais frequente
            difficulty_manager.adjust_spawn_rate_multiplier(-0.1)
        elif key == glfw.KEY_F4:
            difficulty_manager.adjust_spawn_rate_multiplier(0.1)
        elif key == glfw.KEY_F5:
            difficulty_manager.adjust_enemy_speed_multiplier(0.1)
        elif key == glfw.KEY_F6:
            difficulty_manager.adjust_enemy_speed_multiplier(-0.1)
        elif key == glfw.KEY_F7:
            difficulty_manager.toggle_manual_control()
        elif key == glfw.KEY_F8:
            difficulty_manager.adjust_hole_spawn_probability(0.05)
        elif key == glfw.KEY_F9:
            difficulty_manager.adjust_hole_spawn_probability(-0.05)
        elif key == glfw.KEY_F10:
            difficulty_manager.adjust_oil_stain_spawn_probability(0.05)
        elif key == glfw.KEY_F11:
            difficulty_manager.adjust_oil_stain_spawn_probability(-0.05)
        elif key == glfw.KEY_F12:
            difficulty_manager.adjust_invulnerability_spawn_probability(0.02)
        elif key == glfw.KEY_INSERT:
            difficulty_manager.adjust_invulnerability_spawn_probability(-0.02)
        elif key == glfw.KEY_B:
            # Diminuir probabilidade de spawn da cerveja
            difficulty_manager.adjust_beer_spawn_probability(-0.05)
        elif key == glfw.KEY_V:
            # Aumentar probabilidade de spawn da cerveja
            difficulty_manager.adjust_beer_spawn_probability(0.05)
        elif key == glfw.KEY_H:
            # Toggle debug hitboxes
            global DEBUG_SHOW_HITBOXES
            DEBUG_SHOW_HITBOXES = not DEBUG_SHOW_HITBOXES
            print(f"Debug hitboxes: {'ON' if DEBUG_SHOW_HITBOXES else 'OFF'}")


def mouse_button_callback(window, button, action, mods):
    global current_game_state, asking_for_name, current_scale, current_offset, fb_height

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            menu_state.mouse_pressed = True
        elif action == glfw.RELEASE:
            menu_state.mouse_pressed = False

            mouse_px, mouse_py = glfw.get_cursor_pos(window)
            inv_mouse_py = (fb_height or SCREEN_HEIGHT) - mouse_py
            scale = current_scale or 1.0
            offset_x, offset_y = current_offset or (0.0, 0.0)

            mouse_x = (mouse_px - offset_x) / scale
            mouse_y = (inv_mouse_py - offset_y) / scale

            # --- LÓGICA DE CLIQUE UNIFICADA ---
            if current_game_state == GAME_STATE_MENU or \
                    current_game_state == GAME_STATE_PAUSED or \
                    (current_game_state == GAME_STATE_GAME_OVER and not asking_for_name):

                clicked_action = None
                for area in menu_state.clickable_areas:
                    x, y, w, h = area['rect']
                    if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                        clicked_action = area['action']
                        break

                if clicked_action:
                    if clicked_action == "start":
                        current_game_state = GAME_STATE_PLAYING
                        reset_game()
                        try:
                            audio_manager.play_background_music("assets/sound/background_music_1.mp3", volume=0.5,
                                                                fade_ms=500, loop=True)
                        except Exception as e:
                            print(f"Erro ao iniciar a música de fundo: {e}")

                    elif clicked_action == "instructions":
                        menu_state.active_menu = "instructions"

                    elif clicked_action == "quit":
                        glfw.set_window_should_close(window, True)

                    elif clicked_action == "main":
                        current_game_state = GAME_STATE_MENU
                        menu_state.active_menu = "main"
                        reset_game()

                    elif clicked_action == "restart":
                        current_game_state = GAME_STATE_PLAYING
                        reset_game()
                        try:
                            audio_manager.play_background_music("assets/sound/background_music_1.mp3", volume=0.8,
                                                                fade_ms=500, loop=True)
                        except Exception as e:
                            print(f"Erro ao iniciar a música de fundo: {e}")

                    elif clicked_action == "resume":
                        current_game_state = GAME_STATE_PLAYING

def reset_game():
    global scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down, player_name, asking_for_name, new_high_score, police_car,  holes, hole_spawn_timer, oil_stains, oil_stain_spawn_timer, beer_collectibles, beer_spawn_timer, invulnerability_powerups, invulnerability_spawn_timer, score_indicators, pending_score_bonus, beer_bonus_points, last_police_spawn_time
    scroll_pos = 0.0
    player_truck.reset()
    enemies_up.clear()
    enemies_down.clear()

    # Garantir que todos os players globais de áudio sejam interrompidos
    # Isso para a sirene, músicas de fundo e outros players.
    try:
        try:
            audio_manager.stop_background_music()
        except Exception:
            pass
        audio_manager.stop_all()
    except Exception as e:
        print(f"Erro ao parar todos os áudios: {e}")

    police_car = None
    # Reset do timer de spawn da polícia
    last_police_spawn_time = -9999.0
    holes.clear()
    oil_stains.clear()
    beer_collectibles.clear()
    invulnerability_powerups.clear()
    score_indicators.clear()
    spawn_timer_up = 0
    spawn_timer_down = 0
    hole_spawn_timer = 0
    oil_stain_spawn_timer = 0
    beer_spawn_timer = 0
    invulnerability_spawn_timer = 0
    pending_score_bonus = 0
    beer_bonus_points = 0
    difficulty_manager.reset()
    player_name = ""
    asking_for_name = False
    new_high_score = False
    glfw.set_time(0) # Reseta o tempo


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

def draw_heart(x, y, size=8, color=(1.0, 0.3, 0.3), filled=True):
    """Desenha um coração usando primitivas geométricas do OpenGL"""
    glDisable(GL_TEXTURE_2D)
    glColor3f(color[0], color[1], color[2])
    
    import math
    
    if filled:
        # Coração preenchido usando uma abordagem mais precisa
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)  # Centro
        
        # Criar pontos do coração usando a equação paramétrica
        for i in range(37):  # 36 pontos + volta ao início
            t = i * 2 * math.pi / 36
            # Equação paramétrica do coração
            heart_x, heart_y = calculate_heart_point(t, x, y, size)
            glVertex2f(heart_x, heart_y)
        
        glEnd()
    else:
        # Coração vazado (apenas contorno)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        
        # Criar pontos do contorno do coração
        for i in range(36):
            t = i * 2 * math.pi / 36
            # Equação paramétrica do coração
            heart_x, heart_y = calculate_heart_point(t, x, y, size)
            glVertex2f(heart_x, heart_y)
        
        glEnd()
        glLineWidth(1.0)


def calculate_heart_point(t, x, y, size):
    heart_x = x + size * (16 * math.sin(t) ** 3) / 16
    heart_y = y + size * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 13
    return heart_x, heart_y

def main():
    global current_game_state, scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down, police_car, holes, hole_spawn_timer, oil_stains, oil_stain_spawn_timer, beer_collectibles, beer_spawn_timer, invulnerability_powerups, invulnerability_spawn_timer, score_indicators, pending_score_bonus, beer_bonus_points, sys, random, last_police_spawn_time, current_scale, current_offset, fb_height

    if not glfw.init():
        sys.exit("Could not initialize GLFW.")

    # Inicialização do mixer delegada ao audio_manager (tenta inicializar de forma segura)
    try:
        audio_manager._ensure_mixer_initialized()
    except Exception as e:
        print(f"Aviso: Falha ao inicializar o pygame mixer via audio_manager: {e}")

    glutInit(sys.argv)

    joystick = None
    try:
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Controle encontrado: {joystick.get_name()}")
        else:
            print("Nenhum controle encontrado. Usando teclado.")
    except Exception as e:
        print(f"Erro ao inicializar o controle: {e}")

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Beer Truck", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Could not create GLFW window.")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # --- Load Textures ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    truck_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/truck.png"))
    truck_dead_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/truck_dead.png"))
    truck_armored_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/armored_truck.png"))
    truck_hole_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/hole.png"))
    truck_oil_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/oil.png"))
    truck_hole_and_oil_texture = load_texture(os.path.join(script_dir, "assets/veiculos/protagonista/hole and oil.png"))
    enemy_textures_up = [load_texture(os.path.join(script_dir, f"assets/veiculos/up_{color}.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_textures_down = [load_texture(os.path.join(script_dir, f"assets/veiculos/down_{color}.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_dead_textures_up = [load_texture(os.path.join(script_dir, f"assets/veiculos/up_{color}_dead.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_dead_textures_down = [load_texture(os.path.join(script_dir, f"assets/veiculos/down_{color}_dead.png")) for color in ["black", "green", "red", "yellow"]]
    hole_texture = load_texture(os.path.join(script_dir, "assets/elementos_de_cenario/buraco.png"))
    oil_texture = load_texture(os.path.join(script_dir, "assets/elementos_de_cenario/mancha_oleo.png"))
    beer_texture = load_texture(os.path.join(script_dir, "assets/elementos_de_cenario/cerveja.png"))
    invulnerability_texture = load_texture(os.path.join(script_dir, "assets/elementos_de_cenario/invecibilidade asset.png"))

    police_textures = {
        'normal_1': load_texture(os.path.join(script_dir, "assets/veiculos/police_1.png")),
        'normal_2': load_texture(os.path.join(script_dir, "assets/veiculos/police_2.png")),
        'dead': load_texture(os.path.join(script_dir, "assets/veiculos/police_dead.png"))
    }
    
    # --- Pré-carrega os sons ---
    try:
        audio_manager.preload_sound("assets/sound/police_sound.wav", create_loop=True)
        audio_manager.preload_sound("assets/sound/background_music_1.mp3", create_loop=True)
        audio_manager.preload_sound("assets/sound/crash.wav", create_loop=False)
        audio_manager.preload_sound("assets/sound/game_over.wav", create_loop=False)
        audio_manager.preload_sound("assets/sound/beer.wav", create_loop=False)
        audio_manager.preload_sound("assets/sound/invulnerability.wav", create_loop=False)
    except Exception as e:
        print(f"Erro ao pré-carregar áudios: {e}")
    
    if not all([truck_texture, truck_dead_texture, truck_armored_texture, truck_hole_texture, truck_oil_texture, truck_hole_and_oil_texture, 
                hole_texture, oil_texture, beer_texture, invulnerability_texture] + 
               enemy_textures_up + enemy_textures_down + enemy_dead_textures_up + enemy_dead_textures_down + 
               list(police_textures.values())):
        glfw.terminate()
        sys.exit("Failed to load one or more textures.")

    player_truck = Truck(truck_texture, truck_dead_texture, truck_armored_texture,
                    truck_hole_texture, truck_oil_texture, truck_hole_and_oil_texture)
    enemies_up, enemies_down = [], []
    holes = []
    oil_stains = []
    beer_collectibles = []
    invulnerability_powerups = []
    score_indicators = []
    spawn_timer_up, spawn_timer_down = 0, 0
    hole_spawn_timer = 0
    oil_stain_spawn_timer = 0
    beer_spawn_timer = 0
    invulnerability_spawn_timer = 0
    pending_score_bonus = 0
    beer_bonus_points = 0

    enemy_up_texture_pairs = list(zip(enemy_textures_up, enemy_dead_textures_up))
    enemy_down_texture_pairs = list(zip(enemy_textures_down, enemy_dead_textures_down))

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # --- Resolution & uniform scaling (logical base coordinates) ---
        fb_size = glfw.get_framebuffer_size(window)
        fb_width = fb_size[0]
        fb_height = fb_size[1]

        # Base logical resolution (use existing imported GAME_WIDTH / PANEL_WIDTH / SCREEN_HEIGHT as reference)
        BASE_GAME_WIDTH = GAME_WIDTH
        BASE_PANEL_WIDTH = PANEL_WIDTH
        BASE_TOTAL_WIDTH = BASE_GAME_WIDTH + BASE_PANEL_WIDTH
        BASE_HEIGHT = SCREEN_HEIGHT

        # Scale uniformly to fit framebuffer while preserving aspect ratio
        scale = min(fb_width / float(BASE_TOTAL_WIDTH), fb_height / float(BASE_HEIGHT)) if BASE_TOTAL_WIDTH > 0 and BASE_HEIGHT > 0 else 1.0
        # Prevent zero or negative scale (can happen when framebuffer width/height is 0 e.g. minimized window)
        if not scale or scale <= 0.0:
            scale = 1e-6
        scaled_width = BASE_TOTAL_WIDTH * scale
        scaled_height = BASE_HEIGHT * scale
        offset_x = (fb_width - scaled_width) / 2.0
        offset_y = (fb_height - scaled_height) / 2.0

        # Integer viewports
        content_vp = (int(round(offset_x)), int(round(offset_y)), int(round(scaled_width)), int(round(scaled_height)))
        game_vp = (int(round(offset_x)), int(round(offset_y)), int(round(BASE_GAME_WIDTH * scale)), int(round(scaled_height)))
        panel_vp = (int(round(offset_x + BASE_GAME_WIDTH * scale)), int(round(offset_y)), int(round(BASE_PANEL_WIDTH * scale)), int(round(scaled_height)))

        # Make road module use logical base coords for layout calculations (keeps helper functions consistent)
        road.SCREEN_WIDTH = BASE_TOTAL_WIDTH
        road.SCREEN_HEIGHT = BASE_HEIGHT
        road.GAME_WIDTH = BASE_GAME_WIDTH
        road.PANEL_WIDTH = BASE_PANEL_WIDTH

        # Expose values for mouse mapping and other draw code
        current_scale = scale
        current_offset = (offset_x, offset_y)

        # --- Game State Logic ---
        if current_game_state == GAME_STATE_PLAYING:
            # Atualizar dificuldade baseada no tempo e pontuação
            time_elapsed = glfw.get_time()
            score = abs(scroll_pos * 0.1) + beer_bonus_points
            difficulty_manager.update(time_elapsed, score)

            # Obter valores dinâmicos de dificuldade
            current_scroll_speed = difficulty_manager.get_current_scroll_speed()
            current_spawn_rate = difficulty_manager.get_current_spawn_rate()
            enemy_speed_multiplier = difficulty_manager.get_current_enemy_speed_multiplier()

            # Aplica ao scroll_speed global (sinal negativo)
            global scroll_speed
            scroll_speed = -current_scroll_speed

            if not player_truck.crashed:
                # Atualiza o estado do caminhão (verifica invulnerabilidade)
                player_truck.update()
                
                dx, dy = 0.0, 0.0
                DEADZONE = 0.3  # Zona morta para o analógico

                # --- Controle do Joystick ---
                if joystick:
                    pygame.event.pump()  # Processa eventos internos do pygame

                    # Eixo X (esquerda/direita) do analógico esquerdo
                    axis_x = joystick.get_axis(0)
                    if abs(axis_x) > DEADZONE:
                        dx = axis_x * 0.1

                    # Eixo Y (cima/baixo) do analógico esquerdo
                    axis_y = joystick.get_axis(1)
                    if abs(axis_y) > DEADZONE:
                        # Pygame considera -1 para cima, então invertemos
                        if axis_y < 0:  # Para cima
                            dy = 0.1
                        else:  # Para baixo (freio)
                            dy = scroll_speed / player_truck.speed_y

                    # D-Pad (Hat)
                    if joystick.get_numhats() > 0:
                        hat_x, hat_y = joystick.get_hat(0)
                        if hat_x != 0:
                            dx = hat_x * 0.1
                        if hat_y != 0:
                            if hat_y > 0:  # Para cima
                                dy = 0.1
                            else:  # Para baixo (freio)
                                dy = scroll_speed / player_truck.speed_y

                    # Botão para buzina (geralmente o botão 2 é o 'X' no PS2)
                    if joystick.get_button(2):
                        try:
                            audio_manager.play_one_shot("assets/sound/horn.mp3", volume=0.7)
                        except Exception as e:
                            print(f"Erro ao tocar buzina: {e}")

                # --- Controle do Teclado (Fallback) ---
                # Se o joystick não moveu o caminhão, verifica o teclado
                if dx == 0.0:
                    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS: dx -= 0.1
                    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS: dx += 0.1

                if dy == 0.0:
                    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                        dy = 0.1
                    elif glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                        dy = scroll_speed / player_truck.speed_y

                player_truck.move(dx, dy)
            else:
                # --- LÓGICA DE CRASH / RESPAWN / GAME OVER ---
                # Empurra o caminhão com o scroll quando está crashado
                # MODIFICAÇÃO: Acelera a velocidade de scroll durante o período de crash
                player_truck.y += scroll_speed * CRASH_SCROLL_MULTIPLIER

                # Só continua para a próxima etapa (respawn ou game over) quando o caminhão saiu da tela E
                # todos os inimigos marcados como crashados também já tiverem saído.
                if player_truck.y + player_truck.height < 0:
                    crashed_enemies = [e for e in enemies_up + enemies_down if e.crashed]
                    # considera apenas inimigos que ainda estão visíveis na tela
                    remaining_crashed_visible = [e for e in crashed_enemies if e.y + e.height >= 0]

                    if not remaining_crashed_visible:
                        # Se ainda tem vidas, faz o respawn
                        if player_truck.lives > 0:
                            player_truck.respawn()
                        else:
                            # Se não tem mais vidas, é Game Over
                            current_game_state = GAME_STATE_GAME_OVER
                            # Para a música de fundo ao entrar na tela de game over
                            try:
                                audio_manager.stop_background_music()
                            except Exception:
                                pass
                            # Toca som de game over (não bloqueante)
                            try:
                                audio_manager.play_one_shot("assets/sound/game_over.wav")
                            except Exception as e:
                                print(f"Erro ao tocar som de game over: {e}")
                            # Verifica se a pontuação atual é um novo high score
                            final_score = int(abs(scroll_pos * 0.1) + beer_bonus_points)
                            global new_high_score, asking_for_name
                            new_high_score = high_score_manager.is_high_score(final_score)
                            if new_high_score:
                                asking_for_name = True
            
            # Acelera a rolagem do cenário quando o caminhão está crashado
            if player_truck.crashed:
                scroll_pos += scroll_speed * CRASH_SCROLL_MULTIPLIER
            else:
                scroll_pos += scroll_speed

            # --- Police Spawning ---
            if police_car is None and score > POLICE_SPAWN_SCORE_THRESHOLD:
                # Respeita cooldown entre spawns de polícia
                current_time = glfw.get_time()
                time_since_last = current_time - last_police_spawn_time
                if time_since_last < POLICE_COOLDOWN_SECONDS:
                    # Ainda em cooldown — não tenta spawnar
                    pass
                else:
                    # A chance aumenta com a pontuação
                    spawn_chance = random.uniform(0, 1) * (score / 500000.0)
                    if random.random() < spawn_chance:
                        print(f"Police spawn chance: {spawn_chance:.4f}")
                        print(f"Police car spawned at score {score:.0f}!")
                        # Medir tempo de inicialização para diagnosticar travamentos ao spawn
                        try:
                            police_car = police.PoliceCar(police_textures, os.path.join(script_dir, "assets/sound/police_sound.wav"))
                            # Registra o tempo do spawn para aplicar cooldown
                            last_police_spawn_time = glfw.get_time()
                        except Exception as e:
                            print(f"Failed to spawn PoliceCar: {e}")

            # --- Police Update ---
            if police_car:
                # Só acelera o carro da polícia se o jogador estiver crashado, mesmo que a polícia esteja crashada
                if player_truck.crashed:
                    police_result = police_car.update(player_truck, enemies_up + enemies_down, scroll_speed * CRASH_SCROLL_MULTIPLIER)
                else:
                    police_result = police_car.update(player_truck, enemies_up + enemies_down, scroll_speed)
                
                # Se a polícia retornou informações de pontuação (jogador blindado destruiu a polícia)
                if police_result and police_result.get("points_awarded"):
                    points_gained = police_result["points"]
                    beer_bonus_points += points_gained
                    
                    # Cria indicador visual de pontos
                    indicator_x = police_result["x"] + 25  # Centro da polícia (width/2)
                    indicator_y = police_result["y"]
                    score_indicators.append(ScoreIndicator(indicator_x, indicator_y, points_gained))
                
                # Se a polícia sair da tela por cima ou por baixo, remove-a
                if police_car.y > SCREEN_HEIGHT or police_car.y + police_car.height < 0:
                    try:
                        police_car.stop_audio()
                    except Exception:
                        pass
                    # Guarda momento de remoção para iniciar cooldown
                    last_police_spawn_time = glfw.get_time()
                    police_car = None

            # --- Enemy Spawning ---
            # Aplica o multiplicador de crash ao timer de spawn quando o player está crashado
            if player_truck.crashed:
                spawn_timer_up += 0.1 * CRASH_SCROLL_MULTIPLIER
            else:
                spawn_timer_up += 0.1
                
            if spawn_timer_up >= current_spawn_rate:
                spawn_timer_up = 0
                up_lanes = range(LANE_COUNT_PER_DIRECTION, LANE_COUNT_PER_DIRECTION * 2)
                possible_lanes = [lane for lane in up_lanes if max((e.y for e in enemies_up if e.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance]
                if possible_lanes:
                    chosen_lane = random.choice(possible_lanes)
                    normal_texture, dead_texture = random.choice(enemy_up_texture_pairs)
                    enemies_up.append(Enemy(normal_texture, dead_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))

            # Aplica o multiplicador de crash ao timer de spawn quando o player está crashado
            if player_truck.crashed:
                spawn_timer_down += 0.15 * CRASH_SCROLL_MULTIPLIER
            else:
                spawn_timer_down += 0.15
                
            if spawn_timer_down >= current_spawn_rate:
                spawn_timer_down = 0
                down_lanes = range(0, LANE_COUNT_PER_DIRECTION)
                possible_lanes = [lane for lane in down_lanes if max((e.y for e in enemies_down if e.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance]
                if possible_lanes:
                    chosen_lane = random.choice(possible_lanes)
                    normal_texture, dead_texture = random.choice(enemy_down_texture_pairs)
                    enemies_down.append(EnemyDown(normal_texture, dead_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))

            # --- Enemy Update & Collision ---
            all_enemies = enemies_up + enemies_down
            for enemy in all_enemies:
                # Passa o multiplicador de velocidade quando o player está crashado
                if player_truck.crashed:
                    enemy.update(all_enemies, CRASH_SCROLL_MULTIPLIER)
                else:
                    enemy.update(all_enemies)
                    
                # Marca inimigos que colidem com o caminhão
                if not enemy.crashed and player_truck.check_collision(enemy):
                    # Só processa colisão se o jogador não estiver invulnerável (exceto quando blindado)
                    if not player_truck.invulnerable or player_truck.armored:
                        # O inimigo fica crashed quando há colisão válida
                        enemy.crashed = True
                        # Reproduz som de colisão (reutiliza helper para evitar duplicação)
                        try:
                            audio_manager.play_one_shot("assets/sound/crash.wav", volume=0.7)
                        except Exception as e:
                            print(f"Erro ao tocar som de colisão: {e}")
                        
                        # Se o jogador está blindado (invulnerável com power-up), ganha pontos por destruir inimigos
                        if player_truck.armored:
                            points_gained = 100  # Mesmo valor que a cerveja
                            beer_bonus_points += points_gained
                            
                            # Cria indicador visual de pontos (mesmo sistema da cerveja)
                            indicator_x = enemy.x + enemy.width // 2
                            indicator_y = enemy.y
                            score_indicators.append(ScoreIndicator(indicator_x, indicator_y, points_gained))
                        else:
                            # O caminhão só toma dano se não estiver blindado
                            player_truck.take_damage()
                
                # inimigos crashados continuam sendo empurrados pelo scroll
                if enemy.crashed:
                    # Só acelera se o player estiver crashado
                    if player_truck.crashed:
                        enemy.y += scroll_speed * CRASH_SCROLL_MULTIPLIER
                    else:
                        enemy.y += scroll_speed
                    
            # --- Hole Spawning ---
            # Acelera o timer de spawn quando o player está crashado
            if player_truck.crashed:
                hole_spawn_timer += 0.3 * CRASH_SCROLL_MULTIPLIER  # Acelerado durante crash
            else:
                hole_spawn_timer += 0.3  # Timer normal
                
            hole_spawn_rate = current_spawn_rate
            current_hole_probability = difficulty_manager.get_current_hole_spawn_probability()
            
            if hole_spawn_timer >= hole_spawn_rate:
                hole_spawn_timer = 0
                # Agora usamos apenas a probabilidade para determinar o spawn
                if random.random() < current_hole_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Relaxamos a restrição de segurança para permitir mais buracos
                    safe_lanes = [lane for lane in all_lanes if 
                                  max((h.y for h in holes if h.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance/2]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    # Tenta encontrar uma lane onde o buraco não colida com manchas de óleo existentes
                    collision_free_lanes = []
                    for lane in safe_lanes:
                        # Cria um buraco temporário para verificar colisões
                        temp_hole = Hole(hole_texture, lane_index=lane, speed_multiplier=enemy_speed_multiplier)
                        
                        # Verifica se o buraco colide com alguma mancha de óleo
                        collision = False
                        for oil in oil_stains:
                            if oil.active and temp_hole.check_collision_with_object(oil):
                                collision = True
                                break
                                
                        if not collision:
                            collision_free_lanes.append(lane)
                    
                    # Se encontrou lanes sem colisão, usa-as, senão usa as lanes seguras originais
                    if collision_free_lanes:
                        chosen_lane = random.choice(collision_free_lanes)
                    else:
                        chosen_lane = random.choice(safe_lanes)
                        
                    holes.append(Hole(hole_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Hole Update & Collision ---
            for hole in holes:
                # Usa velocidade acelerada durante crash para manter todos objetos em sincronia
                if player_truck.crashed:
                    hole.update(scroll_speed * CRASH_SCROLL_MULTIPLIER)
                else:
                    hole.update(scroll_speed)
                    
                if hole.active and player_truck.check_hole_collision(hole):
                    # Buraco desaparece após uso
                    hole.active = False
                    # Aplica efeito de diminuição de velocidade somente se não estiver invulnerável
                    if not player_truck.invulnerable:
                        player_truck.slow_down()
            
            # Remove buracos que saíram da tela ou foram usados
            holes = [h for h in holes if h.active and h.y > -h.height]
            
            # --- Oil Stain Spawning ---
            # Acelera o timer durante crash
            if player_truck.crashed:
                oil_stain_spawn_timer += 0.3 * CRASH_SCROLL_MULTIPLIER
            else:
                oil_stain_spawn_timer += 0.3  # Incrementa o timer para spawn
                
            oil_stain_spawn_rate = current_spawn_rate
            current_oil_stain_probability = difficulty_manager.get_current_oil_stain_spawn_probability()
            
            if oil_stain_spawn_timer >= oil_stain_spawn_rate:
                oil_stain_spawn_timer = 0
                # Agora usamos apenas a probabilidade para determinar o spawn
                if random.random() < current_oil_stain_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Relaxamos a restrição de segurança para permitir mais manchas
                    safe_lanes = [lane for lane in all_lanes if 
                                  max((o.y for o in oil_stains if o.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance/2]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    # Tenta encontrar uma lane onde a mancha não colida com buracos existentes
                    collision_free_lanes = []
                    for lane in safe_lanes:
                        # Cria uma mancha temporária para verificar colisões
                        temp_oil = OilStain(oil_texture, lane_index=lane, speed_multiplier=enemy_speed_multiplier)
                        
                        # Verifica se a mancha colide com algum buraco
                        collision = False
                        for hole in holes:
                            if hole.active and temp_oil.check_collision_with_object(hole):
                                collision = True
                                break
                                
                        if not collision:
                            collision_free_lanes.append(lane)
                    
                    # Se encontrou lanes sem colisão, usa-as, senão usa as lanes seguras originais
                    if collision_free_lanes:
                        chosen_lane = random.choice(collision_free_lanes)
                    else:
                        chosen_lane = random.choice(safe_lanes)
                        
                    oil_stains.append(OilStain(oil_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Oil Stain Update & Collision ---
            for oil_stain in oil_stains:
                # Usa velocidade acelerada durante crash para manter todos objetos em sincronia
                if player_truck.crashed:
                    oil_stain.update(scroll_speed * CRASH_SCROLL_MULTIPLIER)
                else:
                    oil_stain.update(scroll_speed)
                    
                if oil_stain.active and player_truck.check_oil_stain_collision(oil_stain):
                    # Mancha desaparece após uso
                    oil_stain.active = False
                    # Aplica efeito de inversão de controles somente se não estiver invulnerável
                    if not player_truck.invulnerable:
                        player_truck.invert_controls()
            
            # Remove manchas que saíram da tela ou foram usadas
            oil_stains = [o for o in oil_stains if o.active and o.y > -o.height]
            
            # --- Beer Collectible Spawning ---
            # Acelera o timer durante crash
            if player_truck.crashed:
                beer_spawn_timer += 0.4 * CRASH_SCROLL_MULTIPLIER
            else:
                beer_spawn_timer += 0.4  # Incrementa o timer para spawn (um pouco mais lento)
                
            beer_spawn_rate = current_spawn_rate * 1.5  # Taxa de spawn mais lenta que buracos e óleo
            
            if beer_spawn_timer >= beer_spawn_rate:
                beer_spawn_timer = 0
                # Usa a probabilidade do difficulty manager
                current_beer_probability = difficulty_manager.get_current_beer_spawn_probability()
                
                if random.random() < current_beer_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Verifica faixas seguras para não sobrecarregar
                    safe_lanes = [lane for lane in all_lanes if 
                                  max((b.y for b in beer_collectibles if b.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    chosen_lane = random.choice(safe_lanes)
                    beer_collectibles.append(BeerCollectible(beer_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Beer Collectible Update & Collision ---
            for beer in beer_collectibles:
                # Usa velocidade acelerada durante crash para manter todos objetos em sincronia
                if player_truck.crashed:
                    beer.update(scroll_speed * CRASH_SCROLL_MULTIPLIER)
                else:
                    beer.update(scroll_speed)  # Passa a velocidade atual de rolagem
                if beer.active and beer.check_collision(player_truck):
                    # Cerveja é coletada e jogador ganha pontos
                    points_gained = beer.collect()
                    if points_gained > 0:
                        try:
                            audio_manager.play_one_shot("assets/sound/beer.wav")
                        except Exception as e:
                            print(f"Erro ao tocar som de coleta: {e}")
                        # Cria indicador visual de pontos
                        indicator_x = beer.x + beer.width // 2
                        indicator_y = beer.y
                        score_indicators.append(ScoreIndicator(indicator_x, indicator_y, points_gained))
                        
                        # Adiciona pontos ao score de forma mais suave
                        # Em vez de alterar scroll_pos drasticamente, vamos fazer pequenos incrementos
                        # que serão aplicados ao longo do tempo
                        beer_bonus_points += points_gained  # Adiciona diretamente aos pontos de cerveja
            
            # Remove cervejas que saíram da tela ou foram coletadas
            beer_collectibles = [b for b in beer_collectibles if b.active and b.y > -b.height]
            
            # --- Score Indicators Update ---
            for indicator in score_indicators:
                # Acelera a animação dos indicadores de pontuação durante o crash
                if player_truck.crashed:
                    # Acessa e modifica a velocidade diretamente para este frame
                    original_velocity = indicator.velocity_y
                    indicator.velocity_y *= CRASH_SCROLL_MULTIPLIER
                    indicator.update()
                    # Restaura a velocidade original para o próximo frame
                    indicator.velocity_y = original_velocity
                else:
                    indicator.update()
            # Remove indicadores inativos
            score_indicators = [i for i in score_indicators if i.active]
            
            # --- Invulnerability Power-Up Spawning ---
            # Acelera o timer durante crash
            if player_truck.crashed:
                invulnerability_spawn_timer += 0.2 * CRASH_SCROLL_MULTIPLIER  # Acelerado
            else:
                invulnerability_spawn_timer += 0.2  # Incrementa o timer para spawn (mais lento)
                
            invulnerability_spawn_rate = current_spawn_rate * 2.0  # Taxa de spawn muito mais lenta que outros elementos
            current_invulnerability_probability = difficulty_manager.get_current_invulnerability_spawn_probability()
            
            if invulnerability_spawn_timer >= invulnerability_spawn_rate:
                invulnerability_spawn_timer = 0
                # Verificação de probabilidade (com probabilidade garantida a cada X tentativas)
                static_spawn_counter = getattr(difficulty_manager, 'invulnerability_spawn_counter', 0) + 1
                difficulty_manager.invulnerability_spawn_counter = static_spawn_counter
                
                # Força o spawn a cada 5 tentativas, independente da probabilidade (mais frequente para testes)
                force_spawn = (static_spawn_counter >= 5)
                if force_spawn:
                    difficulty_manager.invulnerability_spawn_counter = 0
                
                if force_spawn or random.random() < current_invulnerability_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Verifica se há faixas seguras (sem outros power-ups muito próximos)
                    safe_lanes = [lane for lane in all_lanes if 
                                  max((p.y for p in invulnerability_powerups if p.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    chosen_lane = random.choice(safe_lanes)
                    invulnerability_powerups.append(InvulnerabilityPowerUp(invulnerability_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Invulnerability Power-Up Update & Collision ---
            for powerup in invulnerability_powerups:
                # Usa velocidade acelerada durante crash para manter todos objetos em sincronia
                if player_truck.crashed:
                    powerup.update(scroll_speed * CRASH_SCROLL_MULTIPLIER)
                else:
                    powerup.update(scroll_speed)  # Passa a velocidade atual de rolagem
                if powerup.active and player_truck.check_invulnerability_powerup_collision(powerup):
                    # Power-up desaparece após uso
                    powerup.active = False
                    try:
                        audio_manager.play_one_shot("assets/sound/invulnerability.wav")
                    except Exception as e:
                        print(f"Erro ao tocar som de invulnerabilidade: {e}")
                    # Ativa o efeito de invulnerabilidade e transforma em carro blindado
                    player_truck.activate_invulnerability_powerup()
            
            # Remove power-ups que saíram da tela ou foram usados
            invulnerability_powerups = [p for p in invulnerability_powerups if p.active and p.y > -p.height]

            # Propagação de colisão: inimigos crashados podem colidir com outros
            def _rects_overlap(a, b):
                return (a.x < b.x + b.width and
                        a.x + a.width > b.x and
                        a.y < b.y + b.height and
                        a.y + a.height > b.y)

            all_cars_on_road = all_enemies
            if police_car:
                all_cars_on_road.append(police_car)

            for a in all_cars_on_road:
                if not a.crashed:
                    continue
                for b in all_enemies:
                    if a is b or b.crashed:
                        continue
                    if _rects_overlap(a, b):
                        b.crashed = True

            enemies_up = [e for e in enemies_up if e.y > -e.height]
            enemies_down = [e for e in enemies_down if e.y > -e.height]

        # --- Drawing ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if current_game_state == GAME_STATE_MENU or current_game_state == GAME_STATE_GAME_OVER:
            # --- Scaled viewport for Menu / Game Over (preserve aspect ratio) ---
            glViewport(content_vp[0], content_vp[1], content_vp[2], content_vp[3])
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, BASE_TOTAL_WIDTH, 0, BASE_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Convert mouse pixel coords -> logical base coordinates
            mouse_px, mouse_py = glfw.get_cursor_pos(window)
            inv_mouse_py = fb_height - mouse_py
            # Use a safe_scale to avoid division by zero when framebuffer dimensions are zero
            safe_scale = scale if scale and scale > 0.0 else 1e-6
            mouse_x = (mouse_px - offset_x) / safe_scale
            mouse_y = (inv_mouse_py - offset_y) / safe_scale

            if current_game_state == GAME_STATE_MENU:
                if menu_state.active_menu == "main":
                    # Obtém todos os recordes para exibir o top 3
                    top_scores = high_score_manager.get_top_scores()
                    draw_start_menu(menu_state, mouse_x, mouse_y,
                                    {"scores": top_scores, "highest": high_score_manager.get_highest_score()})
                elif menu_state.active_menu == "instructions":
                    draw_instructions_screen(menu_state, mouse_x, mouse_y)
            else:  # GAME_STATE_GAME_OVER
                final_score = abs(scroll_pos * 0.1) + beer_bonus_points
                top_scores = high_score_manager.get_top_scores()

                if asking_for_name:
                    # Se estiver pedindo o nome do jogador
                    draw_name_input_screen(menu_state, mouse_x, mouse_y, player_name)
                else:
                    # Tela normal de game over
                    draw_game_over_menu(final_score, menu_state, mouse_x, mouse_y, top_scores, new_high_score,
                                        player_name)

        elif current_game_state == GAME_STATE_PLAYING:
            # --- Game Viewport (scaled) ---
            # Usar a mesma função para desenhar os elementos do jogo na tela de pausa
            draw_game_elements(game_vp, BASE_GAME_WIDTH, BASE_HEIGHT, scroll_pos, holes, oil_stains, beer_collectibles,
                               score_indicators, invulnerability_powerups, player_truck, enemies_up, enemies_down,
                               police_car)

            # --- Debug: Desenha hitboxes se ativado ---
            if DEBUG_SHOW_HITBOXES:
                # Hitbox do player truck (vermelho com área de colisão verde)
                player_truck.draw_debug_hitbox()
                
                # Hitboxes dos inimigos (azul com área de colisão amarela)
                for enemy in enemies_up:
                    enemy.draw_debug_hitbox()
                for enemy in enemies_down:
                    enemy.draw_debug_hitbox()
                
                # Hitboxes das cervejas (laranja com área de colisão ciano)
                for beer in beer_collectibles:
                    beer.draw_debug_hitbox()
                
                # Hitboxes da polícia (azul com área de colisão azul brilhante)
                if police_car:
                    police_car.draw_debug_hitbox()
                
                # Hitboxes dos buracos (marrom com área de colisão laranja)
                for hole in holes:
                    hole.draw_debug_hitbox()
                
                # Hitboxes das manchas de óleo (roxo com área de colisão magenta)
                for oil in oil_stains:
                    oil.draw_debug_hitbox()
                
                # Hitboxes dos power-ups de invulnerabilidade (verde com área de colisão verde brilhante)
                for powerup in invulnerability_powerups:
                    powerup.draw_debug_hitbox()

            # --- Panel Viewport (scaled) ---
            glViewport(panel_vp[0], panel_vp[1], panel_vp[2], panel_vp[3])
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, BASE_PANEL_WIDTH, 0, BASE_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Painel lateral - fundo
            draw_rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT, COLOR_PANEL)
            time_elapsed = glfw.get_time()

            # Calcula a velocidade considerando o efeito do buraco com transição suave
            base_speed = abs(scroll_speed * 400)
            if player_truck.slowed_down:
                # Usa o fator de velocidade atual que muda gradualmente
                displayed_speed = base_speed * player_truck.current_speed_factor
            else:
                displayed_speed = base_speed

            score = abs(scroll_pos * 0.1) + beer_bonus_points

            # Top stats
            draw_text(f"Time: {int(time_elapsed)}", 12, SCREEN_HEIGHT - 28)
            draw_text(f"Speed: {displayed_speed:.0f} km/h", 12, SCREEN_HEIGHT - 52)
            draw_text(f"Score: {int(score)}", 12, SCREEN_HEIGHT - 76)

            # Exibe as vidas usando corações desenhados geometricamente
            draw_text("Lives:", 12, SCREEN_HEIGHT - 100)
            lives_x = 80
            for i in range(player_truck.lives):
                if player_truck.invulnerable:
                    # Pisca durante invulnerabilidade
                    blink = int(time.time() * 6) % 2
                    if blink:
                        color = (1.0, 1.0, 0.3)  # Amarelo
                    else:
                        color = (1.0, 0.3, 0.3)  # Vermelho
                else:
                    color = (1.0, 0.3, 0.3)  # Vermelho normal

                draw_heart(lives_x + i * 25, SCREEN_HEIGHT - 95, size=10, color=color, filled=True)

            # Desenha corações vazios para vidas perdidas
            for i in range(player_truck.lives, 3):
                draw_heart(lives_x + i * 25, SCREEN_HEIGHT - 95, size=10, color=(0.5, 0.5, 0.5), filled=False)

            # Reseta a cor para branco
            glColor3f(1.0, 1.0, 1.0)

            title_y = SCREEN_HEIGHT - 130

            # Dados da difficulty
            difficulty_info = difficulty_manager.get_difficulty_info()
            ss = difficulty_info['scroll_speed_multiplier']
            sr = difficulty_info['spawn_rate_multiplier']
            es = difficulty_info['enemy_speed_multiplier']
            hs = difficulty_info['hole_spawn_probability']

            # Normalização usando limites do DifficultyManager (seguro se atributos existirem)
            max_ss = getattr(difficulty_manager, 'max_scroll_speed_multiplier', 3.0)
            min_sr = getattr(difficulty_manager, 'min_spawn_rate_multiplier', 0.3)
            max_es = getattr(difficulty_manager, 'max_enemy_speed_multiplier', 2.5)
            max_hs = getattr(difficulty_manager, 'max_hole_spawn_probability', 0.5)

            # Normalização dos valores
            def clamp01(v):
                return max(0.0, min(1.0, v))

            ss_norm = clamp01((ss - 1.0) / max(0.0001, (max_ss - 1.0)))
            sr_norm = clamp01((1.0 - sr) / max(0.0001, (1.0 - min_sr)))  # menor spawn_rate => maior frequência
            es_norm = clamp01((es - 1.0) / max(0.0001, (max_es - 1.0)))
            hs_norm = clamp01(hs / max_hs)

            # Difficulty values (labels with numeric values below) — adjusted for clarity
            label_x = 14
            y0 = title_y - 20
            line_height = 18
            group_spacing = 44

            # Scroll Speed
            draw_text("Scroll (F1 / F2)", label_x, y0)
            draw_text(f"x{ss:.2f}", label_x, y0 - line_height)
            y0 -= group_spacing

            # Spawn Rate
            draw_text("Spawn (F3 / F4)", label_x, y0)
            draw_text(f"x{sr:.2f}", label_x, y0 - line_height)
            draw_text("menor = mais freq.", label_x, y0 - line_height * 2)
            y0 -= group_spacing + 20

            # Enemy Speed
            draw_text("Enemy (F5 / F6)", label_x, y0)
            draw_text(f"x{es:.2f}", label_x, y0 - line_height)
            y0 -= group_spacing
            
            # Hole Spawn Probability
            draw_text("Buracos (F8 / F9)", label_x, y0)
            draw_text(f"{hs:.2f} prob.", label_x, y0 - line_height)
            y0 -= group_spacing
            
            # Oil Stain Spawn Probability
            oil_prob = difficulty_info.get("oil_stain_spawn_probability", 0.0)
            max_os = difficulty_manager.max_oil_stain_spawn_probability
            os_norm = clamp01(oil_prob / max_os)
            draw_text("Óleo (F10 / F11)", label_x, y0)
            draw_text(f"{oil_prob:.2f} prob.", label_x, y0 - line_height)
            y0 -= group_spacing
            
            # Invulnerability Power-Up Spawn Probability
            inv_prob = difficulty_info.get("invulnerability_spawn_probability", 0.0)
            max_inv = difficulty_manager.max_invulnerability_spawn_probability
            inv_norm = clamp01(inv_prob / max_inv)
            draw_text("Invuln (F12 / Ins)", label_x, y0)
            draw_text(f"{inv_prob:.2f} prob.", label_x, y0 - line_height)
            y0 -= group_spacing

            # Beer Spawn Probability
            beer_prob = difficulty_info.get("beer_spawn_probability", 0.0)
            max_beer = difficulty_manager.max_beer_spawn_probability
            beer_norm = clamp01(beer_prob / max_beer)
            draw_text("Cerveja (B / V)", label_x, y0)
            draw_text(f"{beer_prob:.2f} prob.", label_x, y0 - line_height)
            y0 -= group_spacing

            # Mode / ajuda de teclas
            mode_text = "MODE: MANUAL (F7)" if difficulty_info['manual_control'] else "MODE: AUTO (F7)"
            draw_text(mode_text, 12, y0)

        elif current_game_state == GAME_STATE_PAUSED:
            # --- 1. DESENHA O JOGO PAUSADO NO FUNDO ---
            # A lógica de desenho é a mesma do estado 'PLAYING', mas sem a lógica de update.

            # --- Game Viewport (scaled) ---
            draw_game_elements(game_vp, BASE_GAME_WIDTH, BASE_HEIGHT, scroll_pos, holes, oil_stains, beer_collectibles,
                               score_indicators, invulnerability_powerups, player_truck, enemies_up, enemies_down,
                               police_car)

            # --- Panel Viewport (scaled) ---
            glViewport(panel_vp[0], panel_vp[1], panel_vp[2], panel_vp[3])
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, BASE_PANEL_WIDTH, 0, BASE_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Re-desenha o painel lateral para que ele também fique visível
            draw_rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT, COLOR_PANEL)
            time_elapsed = glfw.get_time()
            base_speed = abs(scroll_speed * 400)
            displayed_speed = base_speed * player_truck.current_speed_factor if player_truck.slowed_down else base_speed
            score = abs(scroll_pos * 0.1) + beer_bonus_points

            draw_text(f"Time: {int(time_elapsed)}", 12, SCREEN_HEIGHT - 28)
            draw_text(f"Speed: {displayed_speed:.0f} km/h", 12, SCREEN_HEIGHT - 52)
            draw_text(f"Score: {int(score)}", 12, SCREEN_HEIGHT - 76)
            draw_text("Lives:", 12, SCREEN_HEIGHT - 100)
            lives_x = 80
            for i in range(player_truck.lives):
                draw_heart(lives_x + i * 25, SCREEN_HEIGHT - 95, size=10, color=(1.0, 0.3, 0.3), filled=True)
            for i in range(player_truck.lives, 3):
                draw_heart(lives_x + i * 25, SCREEN_HEIGHT - 95, size=10, color=(0.5, 0.5, 0.5), filled=False)
            glColor3f(1.0, 1.0, 1.0)

            # --- 2. DESENHA O MENU DE PAUSA POR CIMA ---
            # Configura a viewport para cobrir toda a área de conteúdo
            glViewport(content_vp[0], content_vp[1], content_vp[2], content_vp[3])
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, BASE_TOTAL_WIDTH, 0, BASE_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Converte as coordenadas do mouse para o sistema lógico do menu
            mouse_px, mouse_py = glfw.get_cursor_pos(window)
            inv_mouse_py = fb_height - mouse_py
            safe_scale = scale if scale and scale > 0.0 else 1e-6
            mouse_x = (mouse_px - offset_x) / safe_scale
            mouse_y = (inv_mouse_py - offset_y) / safe_scale

            draw_pause_menu(menu_state, mouse_x, mouse_y)

        glfw.swap_buffers(window)

    glfw.terminate()

def draw_game_elements(game_vp, base_game_width, base_height, scroll_pos, holes, oil_stains, beer_collectibles,
                       score_indicators, invulnerability_powerups, player_truck, enemies_up, enemies_down, police_car):
    # Configuração da viewport e projeção
    glViewport(game_vp[0], game_vp[1], game_vp[2], game_vp[3])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, base_game_width, 0, base_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_road(scroll_pos)

    # Desenha os buracos e manchas primeiro (para ficarem "abaixo" dos carros)
    for hole in holes:
        hole.draw()

    # Desenha as manchas de óleo
    for oil_stain in oil_stains:
        oil_stain.draw()

    # Desenha as cervejas colecionáveis
    for beer in beer_collectibles:
        beer.draw()

    # Desenha os indicadores de pontos
    for indicator in score_indicators:
        indicator.draw()

    # Desenha os power-ups de invulnerabilidade
    for powerup in invulnerability_powerups:
        powerup.draw()

    player_truck.draw()
    for enemy in enemies_up:
        enemy.draw()
    for enemy in enemies_down:
        enemy.draw()

    # Desenha o carro da polícia se ele existir
    if police_car:
        police_car.draw()

if __name__ == "__main__":
    main()