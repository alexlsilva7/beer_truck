from OpenGL.GL import *
from road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT
import time


class Truck:
    def __init__(self, texture_id, dead_texture_id=None):
        """Inicializa as propriedades do caminhão."""
        self.texture_id = texture_id
        self.dead_texture_id = dead_texture_id
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
        self.invulnerable_duration = 2.0
        # Novas propriedades para efeito do buraco
        self.slowed_down = False
        self.slow_down_start_time = 0
        self.slow_down_duration = 1.5  # Duração do efeito de diminuição de velocidade
        self.slow_down_factor = 0.5  # Reduz a velocidade para 50%
        self.current_speed_factor = 1.0  # Fator de velocidade atual (começa em 100%)

    def update(self):
        """Atualiza o estado do caminhão (invulnerabilidade e efeito de diminuição de velocidade)."""
        current_time = time.time()
        
        # Verifica invulnerabilidade
        if self.invulnerable:
            if current_time - self.invulnerable_start_time >= self.invulnerable_duration:
                self.invulnerable = False
                
        # Verifica efeito de diminuição de velocidade
        if self.slowed_down:
            elapsed_time = current_time - self.slow_down_start_time
            
            if elapsed_time >= self.slow_down_duration:
                # Terminou o efeito completamente
                self.slowed_down = False
                self.current_speed_factor = 1.0
            else:
                # Cálculo do período de recuperação gradual
                recovery_start = self.slow_down_duration * 0.6  # Inicia a recuperação em 60% do tempo total
                
                if elapsed_time >= recovery_start:
                    # Cálculo do fator de velocidade durante a recuperação
                    recovery_progress = (elapsed_time - recovery_start) / (self.slow_down_duration - recovery_start)
                    # Interpola linearmente do slow_down_factor até 1.0
                    self.current_speed_factor = self.slow_down_factor + (1.0 - self.slow_down_factor) * recovery_progress
                else:
                    # Mantém o fator de desaceleração no início do efeito
                    self.current_speed_factor = self.slow_down_factor

    def draw(self):
        """Desenha o caminhão na tela usando sua textura."""
        # Habilita o uso de texturas e blending (para transparência)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Usa textura "dead" se o caminhão colidiu e tem textura dead
        current_texture = self.dead_texture_id if self.crashed and self.dead_texture_id else self.texture_id
        glBindTexture(GL_TEXTURE_2D, current_texture)

        # Efeito visual baseado no estado do caminhão
        if self.invulnerable:
            # Calcula a transparência baseada no tempo para criar efeito de piscar
            blink_speed = 6  # Velocidade do piscar
            alpha = 0.3 + 0.7 * abs((time.time() * blink_speed) % 2 - 1)
            glColor4f(1.0, 1.0, 1.0, alpha)
        elif self.slowed_down:
            # Efeito visual para quando está com velocidade reduzida (cor azulada)
            glColor4f(0.7, 0.7, 1.0, 1.0)
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

        # Reset se sair da tela
        if self.y > SCREEN_HEIGHT or self.y + self.height < 0:
            self.reset()

    def check_collision(self, other):
        """Verifica a colisão com outro objeto (inimigo)."""
        # Não verifica colisão se estiver invulnerável
        if self.invulnerable:
            return False
            
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

    def take_damage(self):
        """O caminhão perde uma vida e fica temporariamente invulnerável."""
        if not self.invulnerable and self.lives > 0:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_start_time = time.time()
            
            # Se não tem mais vidas, marca como crashed
            if self.lives <= 0:
                self.crashed = True
            
            return True  # Indica que tomou dano
        return False  # Não tomou dano (já estava invulnerável ou sem vidas)
        
    def slow_down(self):
        """O caminhão sofre um efeito de diminuição de velocidade."""
        if not self.slowed_down:
            self.slowed_down = True
            self.slow_down_start_time = time.time()
            self.current_speed_factor = self.slow_down_factor  # Aplica o fator de redução imediatamente
            return True  # Indica que o efeito foi aplicado
        return False  # Já estava com velocidade reduzida

    def reset(self):
        """Reseta o caminhão para a posição inicial."""
        self.x = (GAME_WIDTH - self.width) / 2
        self.y = 50
        self.crashed = False
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start_time = 0
        self.slowed_down = False
        self.slow_down_start_time = 0
        self.current_speed_factor = 1.0
        self.slow_down_start_time = 0