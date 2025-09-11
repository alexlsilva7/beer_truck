import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

from src.game.entities.road import draw_rect


def setup_menu_viewport_and_convert_mouse(content_vp, base_total_width, base_height, fb_height, offset_x, offset_y,
                                          scale, window):
    # Configura a viewport para cobrir toda a área de conteúdo
    glViewport(content_vp[0], content_vp[1], content_vp[2], content_vp[3])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, base_total_width, 0, base_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Converte as coordenadas do mouse para o sistema lógico do menu
    mouse_px, mouse_py = glfw.get_cursor_pos(window)
    inv_mouse_py = fb_height - mouse_py
    safe_scale = scale if scale and scale > 0.0 else 1e-6
    mouse_x = (mouse_px - offset_x) / safe_scale
    mouse_y = (inv_mouse_py - offset_y) / safe_scale

    return mouse_x, mouse_y


def setup_panel_viewport(panel_vp, base_panel_width, base_height, panel_width, screen_height, color_panel, scroll_speed):
    """Configura a viewport do painel lateral e desenha o fundo"""
    glViewport(panel_vp[0], panel_vp[1], panel_vp[2], panel_vp[3])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, base_panel_width, 0, base_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Painel lateral - fundo
    draw_rect(0, 0, panel_width, screen_height, color_panel)
    time_elapsed = glfw.get_time()

    # Calcula a velocidade considerando o efeito do buraco com transição suave
    base_speed = abs(scroll_speed * 400)
    return time_elapsed, base_speed