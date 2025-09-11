import random

def get_safe_lane_for_powerup(powerups, lane_count, screen_height, safety_dist):
    """
    Escolhe uma faixa segura para spawn de um power-up, evitando faixas com power-ups muito próximos.

    Args:
        powerups: Lista de power-ups já existentes na tela
        lane_count: Número de faixas por direção
        screen_height: Altura da tela
        safety_dist: Distância mínima de segurança entre power-ups

    Returns:
        int: Índice da faixa escolhida para spawn
    """
    all_lanes = range(0, lane_count * 2)
    # Verifica se há faixas seguras (sem outros power-ups muito próximos)
    safe_lanes = [lane for lane in all_lanes if
                  max((p.y for p in powerups if p.lane_index == lane), default=0) < screen_height - safety_dist]

    # Se não houver faixas seguras, usa todas as faixas
    if not safe_lanes:
        safe_lanes = all_lanes

    return random.choice(safe_lanes)


def get_safe_lanes_for_obstacles(oil_stains, lane_count_per_direction, screen_height, safety_distance):
    all_lanes = range(0, lane_count_per_direction * 2)
    # Relaxamos a restrição de segurança para permitir mais manchas
    safe_lanes = [lane for lane in all_lanes if
                  max((o.y for o in oil_stains if o.lane_index == lane),
                      default=0) < screen_height - safety_distance / 2]

    # Se não houver faixas seguras, usa todas as faixas
    if not safe_lanes:
        safe_lanes = all_lanes

    return safe_lanes, all_lanes