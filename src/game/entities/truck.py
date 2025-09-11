import time

from OpenGL.GL import *

from src.game.entities.road import ROAD_WIDTH, GAME_WIDTH, SCREEN_HEIGHT
from src.utils.debug_utils import draw_hitbox, draw_real_hitbox


class Truck:
    def __init__(self, texture_id, dead_texture_id=None, armored_texture_id=None, 
                 hole_texture_id=None, oil_texture_id=None, hole_and_oil_texture_id=None):
        """Inicializa as propriedades do caminhão."""
        self.texture_id = texture_id
        self.dead_texture_id = dead_texture_id
        self.armored_texture_id = armored_texture_id  # Textura do carro blindado
        self.hole_texture_id = hole_texture_id  # Textura do caminhão com efeito de buraco
        self.oil_texture_id = oil_texture_id  # Textura do caminhão com efeito de óleo
        self.hole_and_oil_texture_id = hole_and_oil_texture_id  # Textura do caminhão com ambos efeitos
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

        # Seleciona a textura apropriada com base no estado do caminhão
        current_texture = self.texture_id  # Textura padrão

        if self.crashed and self.dead_texture_id:
            # Caminhão batido/morto
            current_texture = self.dead_texture_id
        elif self.armored and self.armored_texture_id:
            # Caminhão blindado (invulnerável com power-up)
            current_texture = self.armored_texture_id
        elif not self.invulnerable:
            # Só aplica efeitos visuais se não estiver invulnerável
            if self.slowed_down and self.controls_inverted:
                # Ambos efeitos: buraco + óleo
                if self.hole_and_oil_texture_id:
                    current_texture = self.hole_and_oil_texture_id
            elif self.slowed_down:
                # Apenas efeito de buraco
                if self.hole_texture_id:
                    current_texture = self.hole_texture_id
            elif self.controls_inverted:
                # Apenas efeito de óleo
                if self.oil_texture_id:
                    current_texture = self.oil_texture_id
            
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
        else:
            # Estado normal - cor branca sem efeitos
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
        """Verifica a colisão com outro objeto (inimigo) usando hitboxes mais precisas."""
        # Calcula as hitboxes efetivas
        truck_hitbox_width = self.width / 1.3  # Aumentado para colisão mais realística
        truck_hitbox_height = self.height / 1.1
        
        # Centraliza a hitbox no sprite
        truck_hitbox_x = self.x + (self.width - truck_hitbox_width) / 2
        truck_hitbox_y = self.y + (self.height - truck_hitbox_height) / 2
        
        # Para o inimigo, usa os mesmos valores proporcionais
        other_hitbox_width = other.width / 1.3
        other_hitbox_height = other.height / 1.05
        
        other_hitbox_x = other.x + (other.width - other_hitbox_width) / 2
        other_hitbox_y = other.y + (other.height - other_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (truck_hitbox_x < other_hitbox_x + other_hitbox_width and
                truck_hitbox_x + truck_hitbox_width > other_hitbox_x and
                truck_hitbox_y < other_hitbox_y + other_hitbox_height and
                truck_hitbox_y + truck_hitbox_height > other_hitbox_y)

    def get_collision_rect(self):
        """Retorna um retângulo para detecção de colisão."""
        # Usa as mesmas dimensões da hitbox efetiva
        truck_hitbox_width = self.width / 1.3
        truck_hitbox_height = self.height / 1.1
        truck_hitbox_x = self.x + (self.width - truck_hitbox_width) / 2
        truck_hitbox_y = self.y + (self.height - truck_hitbox_height) / 2
        
        return {
            'x': truck_hitbox_x,
            'y': truck_hitbox_y,
            'width': truck_hitbox_width,
            'height': truck_hitbox_height
        }

    def draw_debug_hitbox(self, show_collision_area=True):
        """Desenha a hitbox de debug para visualização."""
        # Desenha o retângulo completo do sprite (vermelho)
        draw_hitbox(self.x, self.y, self.width, self.height, 
                   color=(1.0, 0.0, 0.0, 0.8), line_width=2)
        
        if show_collision_area:
            # Calcula a hitbox REAL que é usada para colisão
            truck_hitbox_width = self.width / 1.3
            truck_hitbox_height = self.height / 1.1
            truck_hitbox_x = self.x + (self.width - truck_hitbox_width) / 2
            truck_hitbox_y = self.y + (self.height - truck_hitbox_height) / 2
            
            # Desenha a hitbox REAL de colisão (ciano brilhante)
            draw_real_hitbox(truck_hitbox_x, truck_hitbox_y, truck_hitbox_width, truck_hitbox_height,
                           color=(0.0, 1.0, 1.0, 1.0))
                
    def check_hole_collision(self, hole):
        """Verifica a colisão com um buraco."""
        if not hole.active or self.crashed:
            return False

        # Usa a função auxiliar para calcular a hitbox do caminhão
        truck_hitbox_x, truck_hitbox_y, truck_hitbox_width, truck_hitbox_height = self.calculate_truck_hitbox()
        
        # Para o buraco, usa uma hitbox igual à visualização
        hole_hitbox_width = hole.width / 1.6  # ← AJUSTÁVEL
        hole_hitbox_height = hole.height / 1.5  # ← AJUSTÁVEL
        
        hole_hitbox_x = hole.x + (hole.width - hole_hitbox_width) / 2
        hole_hitbox_y = hole.y + (hole.height - hole_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (truck_hitbox_x < hole_hitbox_x + hole_hitbox_width and
                truck_hitbox_x + truck_hitbox_width > hole_hitbox_x and
                truck_hitbox_y < hole_hitbox_y + hole_hitbox_height and
                truck_hitbox_y + truck_hitbox_height > hole_hitbox_y)
        
    def check_oil_stain_collision(self, oil_stain):
        """Verifica a colisão com uma mancha de óleo."""
        if not oil_stain.active or self.crashed:
            return False

        # Usa a função auxiliar para calcular a hitbox do caminhão
        truck_hitbox_x, truck_hitbox_y, truck_hitbox_width, truck_hitbox_height = self.calculate_truck_hitbox()
        
        # Para o óleo, usa uma hitbox ligeiramente maior que a visualização
        oil_hitbox_width = oil_stain.width / 1.2  # ← AJUSTÁVEL
        oil_hitbox_height = oil_stain.height / 1.2  # ← AJUSTÁVEL
        
        oil_hitbox_x = oil_stain.x + (oil_stain.width - oil_hitbox_width) / 2
        oil_hitbox_y = oil_stain.y + (oil_stain.height - oil_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (truck_hitbox_x < oil_hitbox_x + oil_hitbox_width and
                truck_hitbox_x + truck_hitbox_width > oil_hitbox_x and
                truck_hitbox_y < oil_hitbox_y + oil_hitbox_height and
                truck_hitbox_y + truck_hitbox_height > oil_hitbox_y)
                
    def check_invulnerability_powerup_collision(self, powerup):
        """Verifica a colisão com um power-up de invulnerabilidade."""
        if not powerup.active or self.crashed:
            return False

        # Usa a função auxiliar para calcular a hitbox do caminhão
        truck_hitbox_x, truck_hitbox_y, truck_hitbox_width, truck_hitbox_height = self.calculate_truck_hitbox()
        
        # Para o power-up, usa uma hitbox generosa
        powerup_hitbox_width = powerup.width / 1.1  # ← AJUSTÁVEL
        powerup_hitbox_height = powerup.height / 1.1  # ← AJUSTÁVEL
        
        powerup_hitbox_x = powerup.x + (powerup.width - powerup_hitbox_width) / 2
        powerup_hitbox_y = powerup.y + (powerup.height - powerup_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (truck_hitbox_x < powerup_hitbox_x + powerup_hitbox_width and
                truck_hitbox_x + truck_hitbox_width > powerup_hitbox_x and
                truck_hitbox_y < powerup_hitbox_y + powerup_hitbox_height and
                truck_hitbox_y + truck_hitbox_height > powerup_hitbox_y)

    def check_slowmotion_powerup_collision(self, powerup):
        """Verifica a colisão com um power-up de slow motion."""
        if not powerup.active or self.crashed:
            return False
        
        # Calcula as hitboxes efetivas do caminhão (igual aos outros métodos)
        truck_hitbox_width = self.width / 1.3  # ← MESMO SISTEMA DE HITBOXES
        truck_hitbox_height = self.height / 1.1  # ← MESMO SISTEMA DE HITBOXES
        
        truck_hitbox_x = self.x + (self.width - truck_hitbox_width) / 2
        truck_hitbox_y = self.y + (self.height - truck_hitbox_height) / 2
        
        # Para o power-up de slow motion, usa uma hitbox mais generosa para facilitar a coleta
        powerup_hitbox_width = powerup.width / 1.6  # ← AJUSTÁVEL (mais generoso que invulnerabilidade)
        powerup_hitbox_height = powerup.height / 1.6  # ← AJUSTÁVEL (mais generoso que invulnerabilidade)
        
        powerup_hitbox_x = powerup.x + (powerup.width - powerup_hitbox_width) / 2
        powerup_hitbox_y = powerup.y + (powerup.height - powerup_hitbox_height) / 2
        
        # Verifica sobreposição dos retângulos das hitboxes
        return (truck_hitbox_x < powerup_hitbox_x + powerup_hitbox_width and
                truck_hitbox_x + truck_hitbox_width > powerup_hitbox_x and
                truck_hitbox_y < powerup_hitbox_y + powerup_hitbox_height and
                truck_hitbox_y + truck_hitbox_height > powerup_hitbox_y)

    def take_damage(self):
        """O caminhão perde uma vida e inicia a sequência de 'crash'."""
        # Não pode tomar dano se já estiver crashed, invulnerável, ou sem vidas
        if self.crashed or self.invulnerable or self.lives <= 0:
            return False  # Não tomou dano
            
        self.lives -= 1
        # Sempre marca como 'crashed' para iniciar a sequência de limpeza de tela.
        self.crashed = True
        return True  # Indica que tomou dano

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
        # Não aplica o efeito se estiver invulnerável
        if self.invulnerable:
            return False
            
        if not self.slowed_down:
            self.slowed_down = True
            self.slow_down_start_time = time.time()
            self.current_speed_factor = self.slow_down_factor  # Aplica o fator de redução imediatamente
            return True  # Indica que o efeito foi aplicado
        return False  # Já estava com velocidade reduzida
        
    def invert_controls(self):
        """O caminhão sofre um efeito de inversão de controles."""
        # Não aplica o efeito se estiver invulnerável
        if self.invulnerable:
            return False
            
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

    def calculate_truck_hitbox(self):
        """Calcula e retorna a hitbox efetiva do caminhão."""
        truck_hitbox_width = self.width / 1.3  # Hitbox mais estreita que o sprite
        truck_hitbox_height = self.height / 1.1  # Hitbox mais baixa que o sprite

        # Centraliza a hitbox no sprite
        truck_hitbox_x = self.x + (self.width - truck_hitbox_width) / 2
        truck_hitbox_y = self.y + (self.height - truck_hitbox_height) / 2

        return truck_hitbox_x, truck_hitbox_y, truck_hitbox_width, truck_hitbox_height
