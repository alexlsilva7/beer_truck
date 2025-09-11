# Utilitário para desenhar hitboxes de debug
from OpenGL.GL import *

def draw_hitbox(x, y, width, height, color=(1.0, 0.0, 0.0, 1.0), line_width=3):
    """
    Desenha uma hitbox de debug na tela.
    
    Args:
        x, y: Posição da hitbox
        width, height: Dimensões da hitbox
        color: Cor da hitbox (R, G, B, A)
        line_width: Espessura da linha
    """
    # Salva estado atual
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Desabilita texturas para desenhar linhas puras
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Define a cor (mais opaca para ser mais visível)
    glColor4f(*color)
    
    # Define a espessura da linha
    glLineWidth(line_width)
    
    # Desenha um retângulo preenchido semi-transparente primeiro
    glColor4f(color[0], color[1], color[2], 0.2)  # Bem transparente
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Desenha o contorno opaco
    glColor4f(color[0], color[1], color[2], 1.0)  # Opaco
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Restaura estado
    glPopAttrib()

def draw_collision_area(center_x, center_y, max_x_distance, max_y_distance, color=(0.0, 1.0, 0.0, 0.5)):
    """
    Desenha a área de colisão baseada no centro (usado para buracos, óleo, etc.).
    
    Args:
        center_x, center_y: Centro do objeto
        max_x_distance, max_y_distance: Distâncias máximas para colisão
        color: Cor da área de colisão
    """
    # Salva estado atual
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Calcula os cantos da área de colisão
    left = center_x - max_x_distance
    right = center_x + max_x_distance
    bottom = center_y - max_y_distance
    top = center_y + max_y_distance
    
    # Desenha um retângulo preenchido semi-transparente
    glColor4f(color[0], color[1], color[2], 0.3)
    glBegin(GL_QUADS)
    glVertex2f(left, bottom)
    glVertex2f(right, bottom)
    glVertex2f(right, top)
    glVertex2f(left, top)
    glEnd()
    
    # Desenha o contorno mais visível
    glColor4f(color[0], color[1], color[2], 1.0)  # Opaco para o contorno
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(left, bottom)
    glVertex2f(right, bottom)
    glVertex2f(right, top)
    glVertex2f(left, top)
    glEnd()
    
    # Restaura estado
    glPopAttrib()

def draw_real_hitbox(x, y, width, height, color=(0.0, 1.0, 1.0, 1.0), line_width=4):
    """
    Desenha a hitbox REAL que é usada para colisão (ciano brilhante para destacar).
    
    Args:
        x, y: Posição da hitbox real
        width, height: Dimensões da hitbox real
        color: Cor da hitbox (padrão: ciano brilhante)
        line_width: Espessura da linha
    """
    # Salva estado atual
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Desabilita texturas para desenhar linhas puras
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Define a espessura da linha (mais grossa para destacar)
    glLineWidth(line_width)
    
    # Desenha um retângulo preenchido semi-transparente
    glColor4f(color[0], color[1], color[2], 0.4)  # Semi-transparente
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Desenha o contorno bem visível
    glColor4f(color[0], color[1], color[2], 1.0)  # Opaco e brilhante
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    
    # Restaura estado
    glPopAttrib()
