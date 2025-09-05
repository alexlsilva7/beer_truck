import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import settings_manager
from road import SCREEN_WIDTH, SCREEN_HEIGHT, draw_rect
import ctypes

# Simple UI primitives for sliders and checkboxes
def draw_text(text, x, y, font=GLUT_BITMAP_HELVETICA_18, color=(1,1,1)):
    glColor3f(*color)
    glRasterPos2i(int(x), int(y))
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_label(x, y, text):
    draw_text(text, x, y)

def draw_slider(x, y, w, h, v):
    # background
    draw_rect(x, y, w, h, (0.2, 0.2, 0.2))
    # filled
    draw_rect(x, y, int(w * v), h, (0.3, 0.6, 0.3))
    # knob
    knob_x = x + int(w * v)
    draw_rect(knob_x - 6, y - (h*0.5), 12, h * 2, (0.8, 0.8, 0.8))

def draw_checkbox(x, y, size, checked):
    draw_rect(x, y, size, size, (0.9, 0.9, 0.9) if checked else (0.2, 0.2, 0.2))
    if checked:
        # simple X
        glColor3f(0, 0, 0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(x + 3, y + 3)
        glVertex2f(x + size - 3, y + size - 3)
        glVertex2f(x + 3, y + size - 3)
        glVertex2f(x + size - 3, y + 3)
        glEnd()
        glLineWidth(1.0)

def draw_and_handle_slider(x, y, w, h, label, setting_key, current_value, menu_state, mouse_x, mouse_y):
    draw_label(x, y + 2, label)
    slider_x = x + 180
    draw_slider(slider_x, y, w, h, current_value)
    

    if menu_state.mouse_pressed and slider_x <= mouse_x <= slider_x + w and y - h <= mouse_y <= y + h*2:
        raw_v = (mouse_x - slider_x) / w
        snapped_v = round(raw_v / 0.05) * 0.05
        v = max(0.0, min(1.0, snapped_v))
        settings_manager.set(setting_key, v)

def draw_and_handle_toggle(x, y, size, label, setting_key, current_value, mouse_clicked, mouse_x, mouse_y):
    draw_label(x, y + 2, label)
    check_x = x + 180
    draw_checkbox(check_x, y, size, current_value)
    if mouse_clicked and check_x <= mouse_x <= check_x + size and y <= mouse_y <= y + size:
        settings_manager.set(setting_key, not current_value)

def list_joysticks():
    try:
        pygame.joystick.quit()
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        names = []
        for i in range(count):
            try:
                j = pygame.joystick.Joystick(i)
                j.init()
                # prefer GUID (get_guid) on newer pygame; fallback to None
                try:
                    guid = j.get_guid()
                    if guid is not None:
                        guid = str(guid)
                except Exception:
                    guid = None
                names.append((i, j.get_name(), guid))
            except Exception:
                pass
        return names
    except Exception:
        return []

def draw_settings_menu(menu_state, mouse_x, mouse_y, fb_height, offset_x, offset_y, scale):
    mouse_clicked = not menu_state.mouse_pressed and getattr(menu_state, '_was_mouse_pressed', False)
    menu_state._was_mouse_pressed = menu_state.mouse_pressed

    draw_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0.08, 0.08, 0.12))
    
    title_text = "CONFIGURACOES"
    title_len = len(title_text) * 10 # Approximate width
    draw_text(title_text, (SCREEN_WIDTH - title_len) / 2, SCREEN_HEIGHT - 60)

    # Layout constants
    col1_x = 50
    col2_x = SCREEN_WIDTH / 2 + 50
    start_y = SCREEN_HEIGHT - 130
    line_h = 40
    slider_w = 200
    slider_h = 8
    check_size = 20
    
    # --- Audio Column ---
    y_pos = start_y
    draw_text("Audio", col1_x, y_pos + 30, font=GLUT_BITMAP_HELVETICA_18)
    
    # Master Volume
    master_v = settings_manager.get_master_volume()
    draw_and_handle_slider(col1_x, y_pos, slider_w, slider_h, "Master Volume", "audio.master", master_v, menu_state, mouse_x, mouse_y)
    
    # Music Volume
    y_pos -= line_h
    music_v = settings_manager.get_music_volume()
    draw_and_handle_slider(col1_x, y_pos, slider_w, slider_h, "Music Volume", "audio.music", music_v, menu_state, mouse_x, mouse_y)

    # SFX Volume (unified)
    y_pos -= line_h
    sfx_v = settings_manager.get("audio.sfx", 0.8)
    draw_and_handle_slider(col1_x, y_pos, slider_w, slider_h, "SFX Volume", "audio.sfx", sfx_v, menu_state, mouse_x, mouse_y)

    # --- Toggles Column ---
    y_pos_toggles = start_y
    draw_text("Gameplay", col2_x, y_pos_toggles + 30, font=GLUT_BITMAP_HELVETICA_18)
    
    toggle_keys = ["police", "holes", "oil", "beer", "invulnerability"]
    for key in toggle_keys:
        is_on = settings_manager.get_toggle(key)
        label = f"Enable {key.title()}"
        draw_and_handle_toggle(col2_x, y_pos_toggles, check_size, label, f"toggles.{key}", is_on, mouse_clicked, mouse_x, mouse_y)
        y_pos_toggles -= line_h

    # --- Joystick Section ---
    y_pos = min(y_pos, y_pos_toggles) - 20
    draw_text("Controles", col1_x, y_pos, font=GLUT_BITMAP_HELVETICA_18)

    # Botão Atualizar ao lado do título "Controles"
    btn_refresh_x = col1_x + 220
    btn_refresh_w = 100
    btn_refresh_h = 25
    draw_rect(btn_refresh_x, y_pos, btn_refresh_w, btn_refresh_h, (0.4, 0.4, 0.6))
    draw_text("Atualizar", btn_refresh_x + 15, y_pos + 8)
    if mouse_clicked and btn_refresh_x <= mouse_x <= btn_refresh_x + btn_refresh_w and y_pos <= mouse_y <= y_pos + btn_refresh_h:
        menu_state.joysticks = list_joysticks()

    y_pos -= line_h

    if not hasattr(menu_state, 'joysticks'):
        menu_state.joysticks = list_joysticks()

    selected = settings_manager.get_selected_joystick()
    if not menu_state.joysticks:
        draw_text("Nenhum joystick encontrado.", col1_x, y_pos - 30)
    else:
        sel_guid = selected.get("selected_guid")
        for idx, (i, name, guid) in enumerate(menu_state.joysticks):
            row_y = y_pos - 30 - idx * 25
            is_sel = False
            if sel_guid is not None and guid is not None:
                try:
                    is_sel = str(sel_guid) == str(guid)
                except Exception:
                    is_sel = False
            
            check_x = col1_x
            draw_checkbox(check_x, row_y - 4, 18, is_sel)
            if mouse_clicked and check_x <= mouse_x <= check_x + 18 and row_y - 4 <= mouse_y <= row_y + 14:
                # Save by GUID when available
                try:
                    settings_manager.set_selected_joystick_guid(str(guid) if guid is not None else None)
                except Exception:
                    pass
 
            text_color = (1, 1, 0) if is_sel else (1, 1, 1)
            # Mostra nome + prefixo do GUID para diferenciar controles com o mesmo nome.
            if guid:
                display = f"{name} ({str(guid)[:8]})"
            else:
                display = f"{name} (idx {i})"
            draw_text(display[:50], col1_x + 30, row_y, color=text_color)

    # --- Bottom Buttons ---
    btn_w = 180
    btn_h = 35
    btn_y = 40
    
    # Restaurar Padrões
    btn_restore_x = SCREEN_WIDTH / 2 - btn_w - 10
    draw_rect(btn_restore_x, btn_y, btn_w, btn_h, (0.6, 0.4, 0.4))
    draw_text("Restaurar Padroes", btn_restore_x + 20, btn_y + 12)
    if mouse_clicked and btn_restore_x <= mouse_x <= btn_restore_x + btn_w and btn_y <= mouse_y <= btn_y + btn_h:
        settings_manager.reset_defaults()

    # Voltar
    btn_back_x = SCREEN_WIDTH / 2 + 10
    draw_rect(btn_back_x, btn_y, btn_w, btn_h, (0.4, 0.6, 0.4))
    draw_text("Voltar", btn_back_x + 60, btn_y + 12)
    if mouse_clicked and btn_back_x <= mouse_x <= btn_back_x + btn_w and btn_y <= mouse_y <= btn_y + btn_h:
        return "back"

    return None