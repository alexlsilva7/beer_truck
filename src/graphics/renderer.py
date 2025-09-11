from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.raw.GLUT import glutBitmapCharacter
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

from src.game.entities.road import draw_road


def draw_game_elements(game_vp, base_game_width, base_height, e_scroll_pos, e_holes, e_oil_stains, e_beer_collectibles,
                       e_score_indicators, e_invulnerability_powerups, e_player_truck, e_enemies_up, e_enemies_down, e_police_car, e_slowmotion_powerups):
    # Configuração da viewport e projeção
    glViewport(game_vp[0], game_vp[1], game_vp[2], game_vp[3])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, base_game_width, 0, base_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_road(e_scroll_pos)

    # Desenha os buracos e manchas primeiro (para ficarem "abaixo" dos carros)
    for hole in e_holes:
        hole.draw()

    # Desenha as manchas de óleo
    for oil_stain in e_oil_stains:
        oil_stain.draw()

    # Desenha as cervejas colecionáveis
    for beer in e_beer_collectibles:
        beer.draw()

    # Desenha os indicadores de pontos
    for indicator in e_score_indicators:
        indicator.draw()

    # Desenha os power-ups de invulnerabilidade
    for powerup in e_invulnerability_powerups:
        powerup.draw()

    # Desenha os power-ups de slow motion
    for powerup in e_slowmotion_powerups:
        powerup.draw()

    e_player_truck.draw()
    for enemy in e_enemies_up:
        enemy.draw()
    for enemy in e_enemies_down:
        enemy.draw()

    # Desenha o carro da polícia se ele existir
    if e_police_car:
        e_police_car.draw()


def draw_panel_stats(scroll_pos, beer_bonus_points, time_elapsed, displayed_speed, screen_height):
    """Desenha as informações de estatísticas no painel lateral do jogo"""
    score = abs(scroll_pos * 0.1) + beer_bonus_points

    draw_text(f"Time: {int(time_elapsed)}", 12, screen_height - 28)
    draw_text(f"Speed: {displayed_speed:.0f} km/h", 12, screen_height - 52)
    draw_text(f"Score: {int(score)}", 12, screen_height - 76)
    draw_text("Lives:", 12, screen_height - 100)
    lives_x = 80

    return score, lives_x

def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
