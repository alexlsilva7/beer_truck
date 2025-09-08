from OpenGL.GL import *
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT
import time


class Truck:
    def __init__(self, texture_id, dead_texture_id=None, armored_texture_id=None):
        """Inicializa as propriedades do caminhão."""
        self.texture_id = texture_id
        self.dead_texture_id = dead_texture_id
        self.armored_texture_id = armored_texture_id  # Textura do carro blindado
        self.width = 50
        self.height = 100
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.speed_x = 2.0
        self.speed_y = 3.0
        self.crashed = False
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start_time = 0 
        self.invulnerable_duration = 4.0  # Aumentado de 2.0 para 4.0 segundos
        self.armored = False  # Estado de invulnerabilidade do power-up
        # Novas propriedades para efeito do buraco
        self.slowed_down = False
        self.slow_down_start_time = 0
        self.slow_down_duration = 1.5  # Duração do efeito de diminuição de velocidade
        self.slow_down_factor = 0.5  # Reduz a velocidade para 50%
        self.current_speed_factor = 1.0  # Fator de velocidade atual (começa em 100%)
        
        # Novas propriedades para o efeito de inversão de controles (mancha de óleo)
        self.controls_inverted = False
        self.controls_inverted_start_time = 0
        self.controls_inverted_duration = 3.0  # Duração do efeito de inversão de controles (3 segundos)

    def update(self):
        """Atualiza o estado do caminhão (invulnerabilidade, diminuição de velocidade e inversão de controles)."""
        current_time = time.time()
        
        # Verifica invulnerabilidade
        if self.invulnerable:
            if current_time - self.invulnerable_start_time >= self.invulnerable_duration:
                self.invulnerable = False
                self.armored = False  # Remove o estado blindado quando a invulnerabilidade acaba
                
        # Verifica efeito de diminuição de velocidade
        if self.slowed_down:
            elapsed_time = current_time - self.slow_down_start_time
            
            if elapsed_time >= self.slow_down_duration:
                # Terminou o efeito completamente
                self.slowed_down = False
                self.current_speed_factor = 1.0
                
        # Verifica efeito de inversão de controles
        if self.controls_inverted:
            if current_time - self.controls_inverted_start_time >= self.controls_inverted_duration:
                # Terminou o efeito de inversão
                self.controls_inverted = False

    def draw(self):
        """Desenha o caminhão na tela usando sua textura."""
        # Habilita o uso de texturas e blending (para transparência)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Usa textura "dead" se o caminhão colidiu e tem textura dead
        # Usa textura "armored" se está blindado
        if self.crashed and self.dead_texture_id:
            current_texture = self.dead_texture_id
        elif self.armored and self.armored_texture_id:
            current_texture = self.armored_texture_id
        else:
            current_texture = self.texture_id
        glBindTexture(GL_TEXTURE_2D, current_texture)

        # Efeito visual baseado no estado do caminhão
        if self.invulnerable and self.armored:
            # Efeito prateado para o carro blindado
            blink_speed = 4
            silver_intensity = 0.8 + 0.2 * abs((time.time() * blink_speed) % 2 - 1)
            glColor4f(silver_intensity, silver_intensity, silver_intensity, 1.0)
        elif self.invulnerable:
            # Calcula a transparência baseada no tempo para criar efeito de piscar
            blink_speed = 6  # Velocidade do piscar
            alpha = 0.5 + 0.5 * abs((time.time() * blink_speed) % 2 - 1)
            glColor4f(1.0, 1.0, 1.0, alpha)
        elif self.slowed_down:
            # Efeito visual para quando está com velocidade reduzida (cor azulada)
            glColor4f(0.7, 0.7, 1.0, 1.0)
        elif self.controls_inverted:
            # Efeito visual para quando os controles estão invertidos (cor avermelhada)
            blink_speed = 4  # Velocidade do piscar mais lento
            red_intensity = 0.7 + 0.3 * abs((time.time() * blink_speed) % 2 - 1)
            glColor4f(1.0, 0.5 * red_intensity, 0.5 * red_intensity, 1.0)
        else:
            glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        # Define os cantos da textura e do retângulo
        # (0,1) é o canto superior esquerdo da imagem
        glTexCoord2f(0, 1)
        glVertex2f(self.x, self.y)
        glTexCoord2f(1, 1)
        glVertex2f(self.x + self.width, self.y)
        glTexCoord2f(1, 0)
        glVertex2f(self.x + self.width, self.y + self.height)
        glTexCoord2f(0, 0)
        glVertex2f(self.x, self.y + self.height)
        glEnd()

        # Reseta a cor para branco opaco para não afetar outros elementos
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def move(self, dx, dy):
        """Move o caminhão nas direções x e y."""
        # Inverte os controles se o efeito estiver ativo
        if self.controls_inverted:
            dx = -dx
            dy = -dy
            
        # Aplica o efeito de diminuição de velocidade se necessário
        actual_speed_x = self.speed_x * (self.current_speed_factor if self.slowed_down else 1.0)
        actual_speed_y = self.speed_y * (self.current_speed_factor if self.slowed_down else 1.0)
        
        self.x += dx * actual_speed_x
        road_x_start = (GAME_WIDTH - ROAD_WIDTH) / 2
        min_x = road_x_start
        max_x = road_x_start + ROAD_WIDTH - self.width
        if self.x < min_x: self.x = min_x
        if self.x > max_x: self.x = max_x

        self.y += dy * actual_speed_y

        # Lógica para quando o caminhão sai da tela
        if not self.crashed:
            # Saiu por cima
            if self.y > SCREEN_HEIGHT:
                self.lose_life_off_screen()
                if self.lives > 0:
                    self.respawn()  # Respawn imediato
                else:
                    # Game Over: move o caminhão para fora da tela para acionar a lógica em main.py
                    self.y = -self.height - 1
            # Saiu por baixo
            elif self.y + self.height < 0:
                self.take_damage()  # Comportamento original: crash e queda

    def check_collision(self, other):
        """Verifica a colisão com outro objeto (inimigo)."""
        # Sempre verifica a colisão - a proteção contra dano é tratada em outro lugar
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
                
    def check_hole_collision(self, hole):
        """Verifica a colisão com um buraco."""
        if not hole.active or self.crashed:
            return False
        
        # Usando um sistema de colisão baseado no centro e com área ajustada
        truck_center_x = self.x + self.width / 2
        truck_center_y = self.y + self.height / 2
        
        hole_center_x = hole.x + hole.width / 2
        hole_center_y = hole.y + hole.height / 2
        
        # Distância máxima para considerar colisão (ajustada para o novo tamanho)
        max_x_distance = (self.width + hole.width) / 3    # Colisão mais precisa
        max_y_distance = (self.height + hole.height) / 3.5  # Colisão mais precisa
        
        # Verifica se os centros estão próximos o suficiente
        return (abs(truck_center_x - hole_center_x) < max_x_distance and
                abs(truck_center_y - hole_center_y) < max_y_distance)
        
    def check_oil_stain_collision(self, oil_stain):
        """Verifica a colisão com uma mancha de óleo."""
        if not oil_stain.active or self.crashed:
            return False
        
        # Usando um sistema de colisão baseado no centro e com área ajustada
        truck_center_x = self.x + self.width / 2
        truck_center_y = self.y + self.height / 2
        
        oil_center_x = oil_stain.x + oil_stain.width / 2
        oil_center_y = oil_stain.y + oil_stain.height / 2
        
        # Distância máxima para considerar colisão
        max_x_distance = (self.width + oil_stain.width) / 3
        max_y_distance = (self.height + oil_stain.height) / 3
        
        return (abs(truck_center_x - oil_center_x) < max_x_distance and
                abs(truck_center_y - oil_center_y) < max_y_distance)
                
    def check_invulnerability_powerup_collision(self, powerup):
        """Verifica a colisão com um power-up de invulnerabilidade."""
        if not powerup.active or self.crashed:
            return False
        
        # Usando um sistema de colisão baseado no centro e com área ajustada
        truck_center_x = self.x + self.width / 2
        truck_center_y = self.y + self.height / 2
        
        powerup_center_x = powerup.x + powerup.width / 2
        powerup_center_y = powerup.y + powerup.height / 2
        
        # Distância máxima para considerar colisão
        max_x_distance = (self.width + powerup.width) / 3
        max_y_distance = (self.height + powerup.height) / 3
        
        return (abs(truck_center_x - powerup_center_x) < max_x_distance and
                abs(truck_center_y - powerup_center_y) < max_y_distance)

    def take_damage(self):
        """O caminhão perde uma vida e inicia a sequência de 'crash'."""
        if not self.invulnerable and self.lives > 0:
            self.lives -= 1
            # Sempre marca como 'crashed' para iniciar a sequência de limpeza de tela.
            self.crashed = True
            return True  # Indica que tomou dano
        return False  # Não tomou dano (já estava invulnerável)

    def lose_life_off_screen(self):
        """O caminhão perde uma vida por sair da tela, ignorando invulnerabilidade."""
        if self.lives > 0:
            self.lives -= 1
        
        if self.lives == 0:
            self.crashed = True

    def respawn(self):
        """Reseta a posição e o estado do caminhão para o respawn, concedendo invulnerabilidade."""
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.crashed = False
        self.invulnerable = True
        self.invulnerable_start_time = time.time()
        # Reseta também os efeitos dos obstáculos
        self.slowed_down = False
        self.controls_inverted = False
        self.current_speed_factor = 1.0
        
    def slow_down(self):
        """O caminhão sofre um efeito de diminuição de velocidade."""
        if not self.slowed_down:
            self.slowed_down = True
            self.slow_down_start_time = time.time()
            self.current_speed_factor = self.slow_down_factor  # Aplica o fator de redução imediatamente
            return True  # Indica que o efeito foi aplicado
        return False  # Já estava com velocidade reduzida
        
    def invert_controls(self):
        """O caminhão sofre um efeito de inversão de controles."""
        if not self.controls_inverted:
            self.controls_inverted = True
            self.controls_inverted_start_time = time.time()
            return True  # Indica que o efeito foi aplicado
        return False  # Já estava com controles invertidos
        
    def activate_invulnerability_powerup(self):
        """Ativa o power-up de invulnerabilidade, transformando em carro blindado."""
        self.invulnerable = True
        self.armored = True
        self.invulnerable_start_time = time.time()
        
        # Limpa os efeitos negativos
        self.slowed_down = False
        self.current_speed_factor = 1.0
        self.controls_inverted = False
        
        return True  # Indica que o power-up foi aplicado

    def reset(self):
        """Reseta o caminhão para a posição inicial."""
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.crashed = False
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start_time = 0
        self.armored = False
        self.slowed_down = False
        self.slow_down_start_time = 0
        self.current_speed_factor = 1.0
        self.controls_inverted = False
        self.controls_inverted_start_time = 0