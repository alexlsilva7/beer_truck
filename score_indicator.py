from OpenGL.GL import *
import time

class ScoreIndicator:
    """Classe para mostrar feedback visual quando pontos são ganhos."""
    
    def __init__(self, x, y, points, duration=2.0):
        """
        Inicializa um indicador de pontos.
        
        Args:
            x, y: Posição onde o indicador aparece
            points: Quantidade de pontos ganhos
            duration: Duração em segundos que o indicador fica visível
        """
        self.x = x
        self.y = y
        self.points = points
        self.start_time = time.time()
        self.duration = duration
        self.active = True
        
        # Movimento do indicador
        self.velocity_y = -50  # Move para cima
        self.original_y = y
        
    def update(self):
        """Atualiza o indicador de pontos."""
        if not self.active:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if elapsed_time >= self.duration:
            self.active = False
            return
            
        # Move o indicador para cima
        self.y = self.original_y + (self.velocity_y * elapsed_time)
        
    def draw(self):
        """Desenha o indicador de pontos na tela."""
        if not self.active:
            return
            
        # Calcula a transparência baseada no tempo restante
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        progress = elapsed_time / self.duration
        alpha = 1.0 - progress  # Desaparece gradualmente
        
        # Salva o estado atual
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Desabilita texturas para desenhar texto simples
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Cor verde brilhante para indicar pontos positivos
        glColor4f(0.0, 1.0, 0.0, alpha)
        
        # Desenha o texto "+{pontos}"
        self._draw_text(f"+{self.points}", self.x, self.y)
        
        # Restaura o estado anterior
        glPopAttrib()
        
    def _draw_text(self, text, x, y):
        """Desenha texto simples usando linhas."""
        # Esta é uma implementação simplificada
        # Vamos desenhar apenas números e o símbolo +
        
        char_width = 10
        char_spacing = 15  # Espaçamento entre caracteres (maior que char_width para separar melhor)
        char_height = 15
        
        for i, char in enumerate(text):
            char_x = x + (i * char_spacing)  # Usa char_spacing em vez de char_width
            if char == '+':
                self._draw_plus(char_x, y, char_width, char_height)
            elif char.isdigit():
                self._draw_digit(char, char_x, y, char_width, char_height)
                
    def _draw_plus(self, x, y, width, height):
        """Desenha o símbolo +"""
        center_x = x + width // 2
        center_y = y + height // 2
        
        glBegin(GL_LINES)
        # Linha horizontal
        glVertex2f(center_x - width//4, center_y)
        glVertex2f(center_x + width//4, center_y)
        # Linha vertical
        glVertex2f(center_x, center_y - height//4)
        glVertex2f(center_x, center_y + height//4)
        glEnd()
        
    def _draw_digit(self, digit, x, y, width, height):
        """Desenha um dígito usando linhas."""
        # Implementação simplificada para alguns números
        if digit == '1':
            glBegin(GL_LINES)
            glVertex2f(x + width//2, y)
            glVertex2f(x + width//2, y + height)
            glEnd()
        elif digit == '0':
            glBegin(GL_LINE_LOOP)
            glVertex2f(x, y)
            glVertex2f(x + width, y)
            glVertex2f(x + width, y + height)
            glVertex2f(x, y + height)
            glEnd()
        elif digit == '2':
            glBegin(GL_LINE_STRIP)
            glVertex2f(x, y + height)
            glVertex2f(x, y + height//2)
            glVertex2f(x + width, y + height//2)
            glVertex2f(x + width, y)
            glVertex2f(x, y)
            glEnd()
        elif digit == '5':
            glBegin(GL_LINE_STRIP)
            glVertex2f(x + width, y + height)
            glVertex2f(x, y + height)
            glVertex2f(x, y + height//2)
            glVertex2f(x + width, y + height//2)
            glVertex2f(x + width, y)
            glVertex2f(x, y)
            glEnd()
