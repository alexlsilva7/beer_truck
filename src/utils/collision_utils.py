# Função para verificar colisão entre dois objetos retangulares
def check_rect_collision(rect1_x, rect1_y, rect1_width, rect1_height, 
                         rect2_x, rect2_y, rect2_width, rect2_height):
    """
    Verifica se dois retângulos se sobrepõem.
    
    Args:
        rect1_x, rect1_y: Coordenadas do primeiro retângulo
        rect1_width, rect1_height: Dimensões do primeiro retângulo
        rect2_x, rect2_y: Coordenadas do segundo retângulo
        rect2_width, rect2_height: Dimensões do segundo retângulo
        
    Returns:
        True se os retângulos colidirem, False caso contrário.
    """
    # Verifica se há sobreposição nos eixos X e Y
    x_overlap = (rect1_x < rect2_x + rect2_width) and (rect1_x + rect1_width > rect2_x)
    y_overlap = (rect1_y < rect2_y + rect2_height) and (rect1_y + rect1_height > rect2_y)
    
    # Se houver sobreposição em ambos os eixos, há colisão
    return x_overlap and y_overlap
