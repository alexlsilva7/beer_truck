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

# --- Variáveis Globais ---
scroll_pos = 0.0
scroll_speed = -PLAYER_SPEED
safety_distance = 180  # Distância mínima para spawnar um novo inimigo na mesma faixa


def key_callback(window, key, scancode, action, mods):
    """Função chamada quando uma tecla é pressionada."""
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def draw_text(text, x, y):
    """Desenha um texto na tela."""
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Garante que o texto seja branco
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    # Não habilitar texturas aqui, cada função de desenho deve gerir o seu estado


def main():
    """Função principal que inicializa e executa o loop com GLFW."""
    global scroll_pos

    if not glfw.init():
        sys.exit("Não foi possível inicializar o GLFW.")

    glutInit(sys.argv)

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Beer Truck", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Não foi possível criar a janela GLFW.")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    # --- Carrega as texturas ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    truck_texture_path = os.path.join(script_dir, "assets/sprite_racing.png")
    truck_texture = load_texture(truck_texture_path)

    enemy_textures_up = []
    enemy_asset_names_up = ["up_black.png", "up_green.png", "up_red.png", "up_yellow.png"]
    for asset_name in enemy_asset_names_up:
        path = os.path.join(script_dir, "assets", asset_name)
        texture = load_texture(path)
        if texture:
            enemy_textures_up.append(texture)

    enemy_textures_down = []
    enemy_asset_names_down = ["down_black.png", "down_green.png", "down_red.png", "down_yellow.png"]
    for asset_name in enemy_asset_names_down:
        path = os.path.join(script_dir, "assets", asset_name)
        texture = load_texture(path)
        if texture:
            enemy_textures_down.append(texture)

    if not truck_texture or not enemy_textures_up or not enemy_textures_down:
        glfw.terminate()
        sys.exit("Falha ao carregar uma ou mais texturas.")

    player_truck = Truck(truck_texture)

    enemies_up = []
    enemies_down = []
    spawn_timer_up = 0
    spawn_timer_down = 0
    spawn_rate = 1000

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # --- Lógica de Controlo do Jogador ---
        if not player_truck.crashed:
            dx, dy = 0.0, 0.0
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                dx -= 0.1
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                dx += 0.1
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                dy = scroll_speed / player_truck.speed_y
            elif glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                dy = 0.1
            player_truck.move(dx, dy)
        else:
            # Se o caminhão colidiu, ele é "levado" pela pista
            player_truck.y += scroll_speed
            # Verifica se o caminhão saiu da tela para resetar
            if player_truck.y + player_truck.height < 0:
                player_truck.reset()

        scroll_pos += scroll_speed

        # --- Lógica de Geração de Inimigos ---
        spawn_timer_up += 0.1
        if spawn_timer_up >= spawn_rate:
            spawn_timer_up = 0
            # Encontrar faixas livres para up
            up_lanes = range(LANE_COUNT_PER_DIRECTION, LANE_COUNT_PER_DIRECTION * 2)
            possible_lanes = []
            for lane in up_lanes:
                max_y_in_lane = max((e.y for e in enemies_up if e.lane_index == lane), default=0)
                if SCREEN_HEIGHT - (max_y_in_lane + safety_distance) > 0:
                    possible_lanes.append(lane)
            if possible_lanes:
                chosen_lane = random.choice(possible_lanes)
                random_texture = random.choice(enemy_textures_up)
                new_enemy = Enemy(random_texture, lane_index=chosen_lane)
                enemies_up.append(new_enemy)

        spawn_timer_down += 0.15
        if spawn_timer_down >= spawn_rate:
            spawn_timer_down = 0
            # Encontrar faixas livres para down
            down_lanes = range(0, LANE_COUNT_PER_DIRECTION)
            possible_lanes = []
            for lane in down_lanes:
                max_y_in_lane = max((e.y for e in enemies_down if e.lane_index == lane), default=0)
                if SCREEN_HEIGHT - (max_y_in_lane + safety_distance) > 0:
                    possible_lanes.append(lane)
            if possible_lanes:
                chosen_lane = random.choice(possible_lanes)
                random_texture = random.choice(enemy_textures_down)
                new_enemy = EnemyDown(random_texture, lane_index=chosen_lane)
                enemies_down.append(new_enemy)

        # --- Atualização e Colisão dos Inimigos ---
        all_enemies = enemies_up + enemies_down
        for enemy in all_enemies:
            enemy.update(all_enemies)
            # Verifica colisão
            if not player_truck.crashed and not enemy.crashed:
                if player_truck.check_collision(enemy):
                    player_truck.crashed = True
                    enemy.crashed = True

        # Move os inimigos que colidiram junto com a pista
        for enemy in all_enemies:
            if enemy.crashed:
                enemy.y += scroll_speed

        enemies_up = [enemy for enemy in enemies_up if enemy.y > -enemy.height]
        enemies_down = [enemy for enemy in enemies_down if enemy.y > -enemy.height]

        # --- Desenho ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(1.0, 1.0, 1.0) # Garante que a cor padrão seja branca

        # --- Viewport do Jogo ---
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

        # --- Viewport do Painel ---
        glViewport(GAME_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, PANEL_WIDTH, 0, SCREEN_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        draw_rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT, COLOR_PANEL)

        time_elapsed = glfw.get_time()
        speed = abs(scroll_speed * 400)
        score = abs(scroll_pos * 0.1)

        info_text_time = f"Tempo: {int(time_elapsed)}"
        info_text_speed = f"Velocidade: {speed:.0f} km/h"
        info_text_score = f"Pontos: {int(score)}"

        draw_text(info_text_time, 10, SCREEN_HEIGHT - 30)
        draw_text(info_text_speed, 10, SCREEN_HEIGHT - 60)
        draw_text(info_text_score, 10, SCREEN_HEIGHT - 90)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()