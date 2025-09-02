#!/usr/bin/env python3
# Teste para verificar se a mecânica de colisão está funcionando corretamente

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from truck import Truck

# Classe mock para simular um inimigo
class MockEnemy:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.crashed = False

def test_collision_mechanics():
    print("=== Teste da Mecânica de Colisão ===")
    
    # Criar truck
    truck = Truck(1, 2, 3)  # texturas mock
    truck.x = 60
    truck.y = 60
    
    # Criar inimigo que vai colidir
    enemy = MockEnemy(50, 50, 50, 100)
    
    print(f"Posição do truck: ({truck.x}, {truck.y})")
    print(f"Posição do enemy: ({enemy.x}, {enemy.y})")
    
    # Teste 1: Colisão normal (sem blindagem)
    print("\n--- Teste 1: Colisão Normal ---")
    print(f"Truck blindado: {truck.armored}")
    print(f"Truck invulnerável: {truck.invulnerable}")
    collision_detected = truck.check_collision(enemy)
    print(f"Colisão detectada: {collision_detected}")
    
    # Teste 2: Colisão com blindagem
    print("\n--- Teste 2: Colisão com Blindagem ---")
    truck.activate_invulnerability_powerup()
    print(f"Truck blindado: {truck.armored}")
    print(f"Truck invulnerável: {truck.invulnerable}")
    collision_detected = truck.check_collision(enemy)
    print(f"Colisão detectada: {collision_detected}")
    
    # Teste 3: Verificar probabilidades
    print("\n--- Teste 3: Configurações de Probabilidade ---")
    from difficulty_manager import DifficultyManager
    dm = DifficultyManager()
    print(f"Probabilidade inicial: {dm.get_current_invulnerability_spawn_probability()}")
    print(f"Probabilidade máxima: {dm.max_invulnerability_spawn_probability}")
    
    print("\n=== Teste Concluído ===")
    
    # Verificar se tudo está funcionando como esperado
    if collision_detected:
        print("✅ SUCESSO: A colisão é detectada mesmo quando blindado!")
    else:
        print("❌ ERRO: A colisão não está sendo detectada quando blindado!")
    
    return collision_detected

if __name__ == "__main__":
    test_collision_mechanics()
