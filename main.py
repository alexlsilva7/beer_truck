import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import os
import random

from road import draw_road, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, PANEL_WIDTH, COLOR_PANEL, draw_rect, PLAYER_SPEED, ROAD_WIDTH, LANE_COUNT_PER_DIRECTION, LANE_WIDTH
from truck import Truck
from enemy import Enemy, EnemyDown
from texture_loader import load_texture
from menu import MenuState, draw_start_menu, draw_instructions_screen, draw_game_over_menu
from difficulty_manager import DifficultyManager

# --- Estados do Jogo ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

# --- Variáveis Globais ---
scroll_pos = 0.0
scroll_speed = -PLAYER_SPEED
safety_distance = 180
difficulty_manager = DifficultyManager()
current_game_state = GAME_STATE_MENU
menu_state = MenuState()

# --- Callbacks de Input ---
def key_callback(window, key, scancode, action, mods):
    global current_game_state, difficulty_manager

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        if current_game_state == GAME_STATE_PLAYING:
            current_game_state = GAME_STATE_MENU
            menu_state.active_menu = "main"
        elif current_game_state == GAME_STATE_MENU:
            if menu_state.active_menu == "instructions":
                menu_state.active_menu = "main"
            else:
                glfw.set_window_should_close(window, True)

    # Controles manuais para dificuldade (F1-F7)
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

def mouse_button_callback(window, button, action, mods):
    global current_game_state

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            menu_state.mouse_pressed = True
        elif action == glfw.RELEASE:
            menu_state.mouse_pressed = False
            mouse_x, mouse_y = glfw.get_cursor_pos(window)
            # Inverte o Y do mouse para corresponder ao sistema de coordenadas do OpenGL
            mouse_y = SCREEN_HEIGHT - mouse_y

            if current_game_state == GAME_STATE_MENU:
                if menu_state.active_menu == "main":
                    hovered_button = get_hovered_button_main_menu(mouse_x, mouse_y)
                    if hovered_button == "start":
                        current_game_state = GAME_STATE_PLAYING
                        reset_game()
                    elif hovered_button == "instructions":
                        menu_state.active_menu = "instructions"
                    elif hovered_button == "quit":
                        glfw.set_window_should_close(window, True)
                elif menu_state.active_menu == "instructions":
                    hovered_button = get_hovered_button_instructions_menu(mouse_x, mouse_y)
                    if hovered_button == "main":
                        menu_state.active_menu = "main"

            elif current_game_state == GAME_STATE_GAME_OVER:
                hovered_button = get_hovered_button_game_over_menu(mouse_x, mouse_y)
                if hovered_button == "restart":
                    current_game_state = GAME_STATE_PLAYING
                    reset_game()
                elif hovered_button == "main":
                    current_game_state = GAME_STATE_MENU
                    menu_state.active_menu = "main"
                    reset_game()

# --- Funções Auxiliares de Menu ---
def get_hovered_button_main_menu(mouse_x, mouse_y):
    button_width = 250
    button_x = (SCREEN_WIDTH - button_width) / 2
    buttons = [
        {"y": SCREEN_HEIGHT / 2, "action": "start"},
        {"y": SCREEN_HEIGHT / 2 - 70, "action": "instructions"},
        {"y": SCREEN_HEIGHT / 2 - 140, "action": "quit"}
    ]
    for btn in buttons:
        if button_x <= mouse_x <= button_x + button_width and btn["y"] <= mouse_y <= btn["y"] + 50:
            return btn["action"]
    return None

def get_hovered_button_instructions_menu(mouse_x, mouse_y):
    button_width = 200
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_y = 100
    if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + 50:
        return "main"
    return None

def get_hovered_button_game_over_menu(mouse_x, mouse_y):
    button_width = 250
    button_x = (SCREEN_WIDTH - button_width) / 2
    buttons = [
        {"y": SCREEN_HEIGHT / 2 - 50, "action": "restart"},
        {"y": SCREEN_HEIGHT / 2 - 120, "action": "main"}
    ]
    for btn in buttons:
        if button_x <= mouse_x <= button_x + button_width and btn["y"] <= mouse_y <= btn["y"] + 50:
            return btn["action"]
    return None

def reset_game():
    global scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down
    scroll_pos = 0.0
    player_truck.reset()
    enemies_up.clear()
    enemies_down.clear()
    spawn_timer_up = 0
    difficulty_manager.reset()
    spawn_timer_down = 0
    glfw.set_time(0) # Reseta o tempo


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

def main():
    global current_game_state, scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down

    if not glfw.init():
        sys.exit("Could not initialize GLFW.")

    glutInit(sys.argv)

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Beer Truck", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Could not create GLFW window.")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # --- Load Textures ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    truck_texture = load_texture(os.path.join(script_dir, "assets/sprite_racing.png"))
    truck_dead_texture = load_texture(os.path.join(script_dir, "assets/sprite_racing_dead.png"))
    enemy_textures_up = [load_texture(os.path.join(script_dir, f"assets/up_{color}.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_textures_down = [load_texture(os.path.join(script_dir, f"assets/down_{color}.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_dead_textures_up = [load_texture(os.path.join(script_dir, f"assets/up_{color}_dead.png")) for color in ["black", "green", "red", "yellow"]]
    enemy_dead_textures_down = [load_texture(os.path.join(script_dir, f"assets/down_{color}_dead.png")) for color in ["black", "green", "red", "yellow"]]

    if not all([truck_texture, truck_dead_texture] + enemy_textures_up + enemy_textures_down + enemy_dead_textures_up + enemy_dead_textures_down):
        glfw.terminate()
        sys.exit("Failed to load one or more textures.")

    player_truck = Truck(truck_texture, truck_dead_texture)
    enemies_up, enemies_down = [], []
    spawn_timer_up, spawn_timer_down = 0, 0
    spawn_rate = 1000

    enemy_up_texture_pairs = list(zip(enemy_textures_up, enemy_dead_textures_up))
    enemy_down_texture_pairs = list(zip(enemy_textures_down, enemy_dead_textures_down))

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # --- Game State Logic ---
        if current_game_state == GAME_STATE_PLAYING:
            # Atualizar dificuldade baseada no tempo e pontuação
            time_elapsed = glfw.get_time()
            score = abs(scroll_pos * 0.1)
            difficulty_manager.update(time_elapsed, score)

            # Obter valores dinâmicos de dificuldade
            current_scroll_speed = difficulty_manager.get_current_scroll_speed()
            current_spawn_rate = difficulty_manager.get_current_spawn_rate()
            enemy_speed_multiplier = difficulty_manager.get_current_enemy_speed_multiplier()

            # Aplica ao scroll_speed global (sinal negativo)
            global scroll_speed
            scroll_speed = -current_scroll_speed

            if not player_truck.crashed:
                dx, dy = 0.0, 0.0
                if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS: dx -= 0.1
                if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS: dx += 0.1
                if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS: dy = 0.1
                elif glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS: dy = scroll_speed / player_truck.speed_y
                player_truck.move(dx, dy)
            else:
                player_truck.y += scroll_speed
                if player_truck.y + player_truck.height < 0:
                    current_game_state = GAME_STATE_GAME_OVER

            scroll_pos += scroll_speed

            # --- Enemy Spawning ---
            spawn_timer_up += 0.1
            if spawn_timer_up >= current_spawn_rate:
                spawn_timer_up = 0
                up_lanes = range(LANE_COUNT_PER_DIRECTION, LANE_COUNT_PER_DIRECTION * 2)
                possible_lanes = [lane for lane in up_lanes if max((e.y for e in enemies_up if e.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance]
                if possible_lanes:
                    chosen_lane = random.choice(possible_lanes)
                    normal_texture, dead_texture = random.choice(enemy_up_texture_pairs)
                    enemies_up.append(Enemy(normal_texture, dead_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))

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
                enemy.update(all_enemies)
                if not player_truck.crashed and not enemy.crashed and player_truck.check_collision(enemy):
                    player_truck.crashed = True
                    enemy.crashed = True
                if enemy.crashed:
                    enemy.y += scroll_speed

            enemies_up = [e for e in enemies_up if e.y > -e.height]
            enemies_down = [e for e in enemies_down if e.y > -e.height]

        # --- Drawing ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if current_game_state == GAME_STATE_MENU or current_game_state == GAME_STATE_GAME_OVER:
            # --- Fullscreen Viewport for Menu ---
            glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            mouse_x, mouse_y = glfw.get_cursor_pos(window)
            mouse_y = SCREEN_HEIGHT - mouse_y  # Adjust mouse Y

            if current_game_state == GAME_STATE_MENU:
                if menu_state.active_menu == "main":
                    draw_start_menu(menu_state, mouse_x, mouse_y)
                elif menu_state.active_menu == "instructions":
                    draw_instructions_screen(menu_state, mouse_x, mouse_y)
            else:  # GAME_STATE_GAME_OVER
                final_score = abs(scroll_pos * 0.1)
                draw_game_over_menu(final_score, menu_state, mouse_x, mouse_y)

        elif current_game_state == GAME_STATE_PLAYING:
            # --- Game Viewport ---
            glViewport(0, 0, GAME_WIDTH, SCREEN_HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, GAME_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            draw_road(scroll_pos)
            player_truck.draw()
            for enemy in enemies_up:
                enemy.draw()
            for enemy in enemies_down:
                enemy.draw()

            # --- Panel Viewport ---
            glViewport(GAME_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, PANEL_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Painel lateral - fundo
            draw_rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT, COLOR_PANEL)
            time_elapsed = glfw.get_time()
            speed = abs(scroll_speed * 400)
            score = abs(scroll_pos * 0.1)

            # Top stats
            draw_text(f"Time: {int(time_elapsed)}", 12, SCREEN_HEIGHT - 28)
            draw_text(f"Speed: {speed:.0f} km/h", 12, SCREEN_HEIGHT - 52)
            draw_text(f"Score: {int(score)}", 12, SCREEN_HEIGHT - 76)

            title_y = SCREEN_HEIGHT - 110

            # Dados da difficulty
            difficulty_info = difficulty_manager.get_difficulty_info()
            ss = difficulty_info['scroll_speed_multiplier']
            sr = difficulty_info['spawn_rate_multiplier']
            es = difficulty_info['enemy_speed_multiplier']

            # Normalização usando limites do DifficultyManager (seguro se atributos existirem)
            max_ss = getattr(difficulty_manager, 'max_scroll_speed_multiplier', 3.0)
            min_sr = getattr(difficulty_manager, 'min_spawn_rate_multiplier', 0.3)
            max_es = getattr(difficulty_manager, 'max_enemy_speed_multiplier', 2.5)

            # Normalização dos valores
            def clamp01(v):
                return max(0.0, min(1.0, v))

            ss_norm = clamp01((ss - 1.0) / max(0.0001, (max_ss - 1.0)))
            sr_norm = clamp01((1.0 - sr) / max(0.0001, (1.0 - min_sr)))  # menor spawn_rate => maior frequência
            es_norm = clamp01((es - 1.0) / max(0.0001, (max_es - 1.0)))

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

            # Mode / ajuda de teclas
            mode_text = "MODE: MANUAL (F7)" if difficulty_info['manual_control'] else "MODE: AUTO (F7)"
            draw_text(mode_text, 12, y0)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()