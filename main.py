import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18  # Importação explícita para evitar erro
import sys
import os
import random

from road import draw_road, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, PANEL_WIDTH, COLOR_PANEL, draw_rect, PLAYER_SPEED, ROAD_WIDTH, LANE_COUNT_PER_DIRECTION, LANE_WIDTH
from truck import Truck
from enemy import Enemy, EnemyDown
from hole import Hole
from oil_stain import OilStain
from texture_loader import load_texture
from menu import MenuState, draw_start_menu, draw_instructions_screen, draw_game_over_menu, draw_name_input_screen, draw_lives
from difficulty_manager import DifficultyManager
from high_score_manager import HighScoreManager

# --- Estados do Jogo ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

# --- Variáveis Globais ---
scroll_pos = 0.0
scroll_speed = -PLAYER_SPEED
safety_distance = 180
difficulty_manager = DifficultyManager()
high_score_manager = HighScoreManager()
current_game_state = GAME_STATE_MENU
menu_state = MenuState()
player_name = ""
asking_for_name = False
new_high_score = False
holes = []  # Lista para armazenar os buracos na pista
hole_spawn_timer = 0  # Temporizador para spawn de buracos
oil_stains = []  # Lista para armazenar as manchas de óleo na pista
oil_stain_spawn_timer = 0  # Temporizador para spawn de manchas de óleo

# --- Callbacks de Input ---
def key_callback(window, key, scancode, action, mods):
    global current_game_state, difficulty_manager, player_name, asking_for_name, new_high_score

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        if current_game_state == GAME_STATE_PLAYING:
            current_game_state = GAME_STATE_MENU
            menu_state.active_menu = "main"
        elif current_game_state == GAME_STATE_MENU:
            if menu_state.active_menu == "instructions":
                menu_state.active_menu = "main"
            else:
                glfw.set_window_should_close(window, True)
        elif current_game_state == GAME_STATE_GAME_OVER and asking_for_name:
            # Se estiver pedindo o nome e ESC for pressionado, cancela a entrada
            asking_for_name = False
            player_name = ""

    # Controle da entrada do nome do jogador
    if asking_for_name and action == glfw.PRESS:
        if key == glfw.KEY_BACKSPACE and len(player_name) > 0:
            player_name = player_name[:-1]
        elif key == glfw.KEY_ENTER:
            # Finaliza a entrada do nome e salva o high score
            if len(player_name) > 0:
                score = abs(scroll_pos * 0.1)
                high_score_manager.add_high_score(player_name, int(score))
                asking_for_name = False
        elif 32 <= key <= 126:  # ASCII imprimível (espaço até ~)
            # Limita o tamanho do nome a 15 caracteres
            if len(player_name) < 15:
                player_name += chr(key)

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

def mouse_button_callback(window, button, action, mods):
    global current_game_state, asking_for_name

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            menu_state.mouse_pressed = True
        elif action == glfw.RELEASE:
            menu_state.mouse_pressed = False
            mouse_x, mouse_y = glfw.get_cursor_pos(window)

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
                # Se estiver pedindo o nome do jogador, não processa cliques nos botões de game over
                if asking_for_name:
                    # Verificar se o clique foi no botão de confirmar
                    input_box_x = (SCREEN_WIDTH - 400) / 2
                    input_box_y = SCREEN_HEIGHT / 2 - 25
                    if input_box_x <= mouse_x <= input_box_x + 400 and SCREEN_HEIGHT - mouse_y >= input_box_y and SCREEN_HEIGHT - mouse_y <= input_box_y + 50:
                        # Clique na caixa de entrada, não faz nada (continua esperando entrada de teclado)
                        pass
                    else:
                        # Clique em outros botões da tela de input
                        button_width = 200
                        button_x = (SCREEN_WIDTH - button_width) / 2
                        button_y = 100

                        # Botão confirmar
                        if button_x <= mouse_x <= button_x + button_width and SCREEN_HEIGHT - mouse_y >= button_y and SCREEN_HEIGHT - mouse_y <= button_y + 50:
                            if len(player_name) > 0:
                                score = abs(scroll_pos * 0.1)
                                high_score_manager.add_high_score(player_name, int(score))
                                asking_for_name = False

                        # Botão voltar
                        elif button_x <= mouse_x <= button_x + button_width and SCREEN_HEIGHT - mouse_y >= button_y + 70 and SCREEN_HEIGHT - mouse_y <= button_y + 70 + 50:
                            asking_for_name = False
                else:
                    # Comportamento normal de game over quando não está pedindo o nome
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
    # Inverte a coordenada Y do mouse para corresponder ao sistema do OpenGL
    inverted_mouse_y = SCREEN_HEIGHT - mouse_y
    buttons = [
        {"y": SCREEN_HEIGHT / 2 - 50, "action": "start"},
        {"y": SCREEN_HEIGHT / 2 - 120, "action": "instructions"},
        {"y": SCREEN_HEIGHT / 2 - 190, "action": "quit"}
    ]
    for btn in buttons:
        if button_x <= mouse_x <= button_x + button_width and btn["y"] <= inverted_mouse_y <= btn["y"] + 50:
            return btn["action"]
    return None

def get_hovered_button_instructions_menu(mouse_x, mouse_y):
    button_width = 200
    button_x = (SCREEN_WIDTH - button_width) / 2
    button_y = 100
    # Inverte a coordenada Y do mouse para corresponder ao sistema do OpenGL
    inverted_mouse_y = SCREEN_HEIGHT - mouse_y
    if button_x <= mouse_x <= button_x + button_width and button_y <= inverted_mouse_y <= button_y + 50:
        return "main"
    return None

def get_hovered_button_game_over_menu(mouse_x, mouse_y):
    button_width = 250
    button_x = (SCREEN_WIDTH - button_width) / 2
    # Inverte a coordenada Y do mouse para corresponder ao sistema do OpenGL
    inverted_mouse_y = SCREEN_HEIGHT - mouse_y
    buttons = [
        {"y": SCREEN_HEIGHT / 2 - 50, "action": "restart"},
        {"y": SCREEN_HEIGHT / 2 - 120, "action": "main"}
    ]
    for btn in buttons:
        if button_x <= mouse_x <= button_x + button_width and btn["y"] <= inverted_mouse_y <= btn["y"] + 50:
            return btn["action"]
    return None

def reset_game():
    global scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down, player_name, asking_for_name, new_high_score, holes, hole_spawn_timer, oil_stains, oil_stain_spawn_timer
    scroll_pos = 0.0
    player_truck.reset()
    enemies_up.clear()
    enemies_down.clear()
    holes.clear()
    oil_stains.clear()
    spawn_timer_up = 0
    spawn_timer_down = 0
    hole_spawn_timer = 0
    oil_stain_spawn_timer = 0
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
            heart_x = x + size * (16 * math.sin(t)**3) / 16
            heart_y = y + size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 13
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
            heart_x = x + size * (16 * math.sin(t)**3) / 16
            heart_y = y + size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 13
            glVertex2f(heart_x, heart_y)
        
        glEnd()
        glLineWidth(1.0)

def main():
    global current_game_state, scroll_pos, player_truck, enemies_up, enemies_down, spawn_timer_up, spawn_timer_down, holes, hole_spawn_timer, oil_stains, oil_stain_spawn_timer, os, sys, random

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
    hole_texture = load_texture(os.path.join(script_dir, "assets/buraco.png"))
    oil_texture = load_texture(os.path.join(script_dir, "assets/mancha_oleo.png"))

    if not all([truck_texture, truck_dead_texture, hole_texture, oil_texture] + enemy_textures_up + enemy_textures_down + enemy_dead_textures_up + enemy_dead_textures_down):
        glfw.terminate()
        sys.exit("Failed to load one or more textures.")

    player_truck = Truck(truck_texture, truck_dead_texture)
    enemies_up, enemies_down = [], []
    holes = []
    oil_stains = []
    spawn_timer_up, spawn_timer_down = 0, 0
    hole_spawn_timer = 0
    oil_stain_spawn_timer = 0
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
                # Atualiza o estado do caminhão (verifica invulnerabilidade)
                player_truck.update()
                
                dx, dy = 0.0, 0.0
                if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS: dx -= 0.1
                if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS: dx += 0.1
                if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS: dy = 0.1
                elif glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS: dy = scroll_speed / player_truck.speed_y
                player_truck.move(dx, dy)
            else:
                # Empurra o caminhão com o scroll quando está crashado
                player_truck.y += scroll_speed
                # Só encerra o jogo quando o caminhão saiu da tela E
                # todos os inimigos marcados como crashados também já tiverem saído.
                if player_truck.y + player_truck.height < 0:
                    crashed_enemies = [e for e in enemies_up + enemies_down if e.crashed]
                    # considera apenas inimigos que ainda estão visíveis na tela
                    remaining_crashed_visible = [e for e in crashed_enemies if e.y + e.height >= 0]
                    if not remaining_crashed_visible:
                        current_game_state = GAME_STATE_GAME_OVER
                        # Verifica se a pontuação atual é um novo high score
                        final_score = int(abs(scroll_pos * 0.1))
                        global new_high_score, asking_for_name
                        new_high_score = high_score_manager.is_high_score(final_score)
                        if new_high_score:
                            asking_for_name = True

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
                # Marca inimigos que colidem com o caminhão mesmo que o caminhão
                # já tenha sido marcado como crashado no mesmo frame, para suportar
                # colisões múltiplas quando o caminhão estiver entre duas faixas.
                if not enemy.crashed and player_truck.check_collision(enemy):
                    # O inimigo sempre fica crashed quando há colisão
                    enemy.crashed = True
                    # O caminhão toma dano usando o sistema de vidas
                    player_truck.take_damage()
                
                # inimigos crashados continuam sendo empurrados pelo scroll
                if enemy.crashed:
                    enemy.y += scroll_speed
                    
            # --- Hole Spawning ---
            hole_spawn_timer += 0.3  # Aumentado para incrementar mais rapidamente o timer
            hole_spawn_rate = current_spawn_rate * 0.5  # Reduzido drasticamente para buracos aparecerem muito mais frequentemente
            current_hole_probability = difficulty_manager.get_current_hole_spawn_probability()
            
            if hole_spawn_timer >= hole_spawn_rate:
                hole_spawn_timer = 0
                # Verificação de probabilidade (com probabilidade garantida a cada X tentativas)
                # Isso garante que um buraco vai aparecer eventualmente
                static_spawn_counter = getattr(difficulty_manager, 'hole_spawn_counter', 0) + 1
                difficulty_manager.hole_spawn_counter = static_spawn_counter
                
                # Força o spawn a cada 5 tentativas, independente da probabilidade
                force_spawn = (static_spawn_counter >= 5)
                if force_spawn:
                    difficulty_manager.hole_spawn_counter = 0
                
                if force_spawn or random.random() < current_hole_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Relaxamos a restrição de segurança para permitir mais buracos
                    safe_lanes = [lane for lane in all_lanes if 
                                 max((h.y for h in holes if h.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance/2]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    chosen_lane = random.choice(safe_lanes)
                    holes.append(Hole(hole_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Hole Update & Collision ---
            for hole in holes:
                hole.update(scroll_speed)  # Passa a velocidade atual de rolagem
                if hole.active and player_truck.check_hole_collision(hole):
                    # Buraco desaparece após uso
                    hole.active = False
                    # Aplica efeito de diminuição de velocidade
                    player_truck.slow_down()
            
            # Remove buracos que saíram da tela ou foram usados
            holes = [h for h in holes if h.active and h.y > -h.height]
            
            # --- Oil Stain Spawning ---
            oil_stain_spawn_timer += 0.3  # Incrementa o timer para spawn
            oil_stain_spawn_rate = current_spawn_rate * 0.6  # Taxa de spawn um pouco mais lenta que os buracos
            current_oil_stain_probability = difficulty_manager.get_current_oil_stain_spawn_probability()
            
            if oil_stain_spawn_timer >= oil_stain_spawn_rate:
                oil_stain_spawn_timer = 0
                # Verificação de probabilidade (com probabilidade garantida a cada X tentativas)
                static_spawn_counter = getattr(difficulty_manager, 'oil_stain_spawn_counter', 0) + 1
                difficulty_manager.oil_stain_spawn_counter = static_spawn_counter
                
                # Força o spawn a cada 7 tentativas, independente da probabilidade
                force_spawn = (static_spawn_counter >= 7)
                if force_spawn:
                    difficulty_manager.oil_stain_spawn_counter = 0
                
                if force_spawn or random.random() < current_oil_stain_probability:
                    # Pode aparecer em qualquer faixa
                    all_lanes = range(0, LANE_COUNT_PER_DIRECTION * 2)
                    # Relaxamos a restrição de segurança para permitir mais manchas
                    safe_lanes = [lane for lane in all_lanes if 
                                 max((o.y for o in oil_stains if o.lane_index == lane), default=0) < SCREEN_HEIGHT - safety_distance/2]
                    
                    # Se não houver faixas seguras, usa todas as faixas
                    if not safe_lanes:
                        safe_lanes = all_lanes
                        
                    chosen_lane = random.choice(safe_lanes)
                    oil_stains.append(OilStain(oil_texture, lane_index=chosen_lane, speed_multiplier=enemy_speed_multiplier))
            
            # --- Oil Stain Update & Collision ---
            for oil_stain in oil_stains:
                oil_stain.update(scroll_speed)  # Passa a velocidade atual de rolagem
                if oil_stain.active and player_truck.check_oil_stain_collision(oil_stain):
                    # Mancha desaparece após uso
                    oil_stain.active = False
                    # Aplica efeito de inversão de controles
                    player_truck.invert_controls()
            
            # Remove manchas que saíram da tela ou foram usadas
            oil_stains = [o for o in oil_stains if o.active and o.y > -o.height]

            # Propagação de colisão: inimigos crashados que ainda estão na tela
            # podem colidir com outros inimigos e marcá-los como crashados.
            def _rects_overlap(a, b):
                return (a.x < b.x + b.width and
                        a.x + a.width > b.x and
                        a.y < b.y + b.height and
                        a.y + a.height > b.y)

            for a in all_enemies:
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
                    # Obtém todos os recordes para exibir o top 3
                    top_scores = high_score_manager.get_top_scores()
                    draw_start_menu(menu_state, mouse_x, mouse_y, {"scores": top_scores, "highest": high_score_manager.get_highest_score()})
                elif menu_state.active_menu == "instructions":
                    draw_instructions_screen(menu_state, mouse_x, mouse_y)
            else:  # GAME_STATE_GAME_OVER
                final_score = abs(scroll_pos * 0.1)
                top_scores = high_score_manager.get_top_scores()

                if asking_for_name:
                    # Se estiver pedindo o nome do jogador
                    draw_name_input_screen(menu_state, mouse_x, mouse_y, player_name)
                else:
                    # Tela normal de game over
                    draw_game_over_menu(final_score, menu_state, mouse_x, mouse_y, top_scores, new_high_score, player_name)

        elif current_game_state == GAME_STATE_PLAYING:
            # --- Game Viewport ---
            glViewport(0, 0, GAME_WIDTH, SCREEN_HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, GAME_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            draw_road(scroll_pos)
            
            # Desenha os buracos e manchas primeiro (para ficarem "abaixo" dos carros)
            for hole in holes:
                hole.draw()
                
            # Desenha as manchas de óleo
            for oil_stain in oil_stains:
                oil_stain.draw()
                
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
            
            # Calcula a velocidade considerando o efeito do buraco com transição suave
            base_speed = abs(scroll_speed * 400)
            if player_truck.slowed_down:
                # Usa o fator de velocidade atual que muda gradualmente
                displayed_speed = base_speed * player_truck.current_speed_factor
            else:
                displayed_speed = base_speed
            
            score = abs(scroll_pos * 0.1)

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
                    import time
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
            os = difficulty_info.get("oil_stain_spawn_probability", 0.0)
            max_os = difficulty_manager.max_oil_stain_spawn_probability
            os_norm = clamp01(os / max_os)
            draw_text("Óleo (F10 / F11)", label_x, y0)
            draw_text(f"{os:.2f} prob.", label_x, y0 - line_height)
            y0 -= group_spacing

            # Mode / ajuda de teclas
            mode_text = "MODE: MANUAL (F7)" if difficulty_info['manual_control'] else "MODE: AUTO (F7)"
            draw_text(mode_text, 12, y0)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
