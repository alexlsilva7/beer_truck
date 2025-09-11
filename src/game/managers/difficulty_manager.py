# Ficheiro: difficulty_manager.py
# Gerenciador de progressão de dificuldade do jogo

class DifficultyManager:
    def __init__(self):
        # Valores base (iniciais)
        self.base_scroll_speed = 0.18
        self.base_spawn_rate = 300  # Reduzido de 1000 para 300 para spawn mais frequente no início
        self.base_enemy_speed = 1.0
        self.base_hole_spawn_probability = 0.35  # Aumentado para compensar a remoção do spawn forçado
        self.base_oil_stain_spawn_probability = 0.35  # Aumentado para compensar a remoção do spawn forçado
        self.base_invulnerability_spawn_probability = 0.3  # Aumentado para 30% para facilitar testes
        self.base_beer_spawn_probability = 0.3  # 30% de chance inicial para cerveja
        self.base_slowmotion_spawn_probability = 0.5  # 50% de chance inicial para slow motion (temporário para teste)

        # Multiplicadores atuais (iniciam em 1.0 = 100%)
        self.scroll_speed_multiplier = 1.0
        self.spawn_rate_multiplier = 1.0
        self.enemy_speed_multiplier = 1.0
        self.hole_spawn_probability = self.base_hole_spawn_probability
        self.oil_stain_spawn_probability = self.base_oil_stain_spawn_probability
        self.invulnerability_spawn_probability = self.base_invulnerability_spawn_probability
        self.beer_spawn_probability = self.base_beer_spawn_probability
        self.slowmotion_spawn_probability = self.base_slowmotion_spawn_probability

        # Taxas de aumento por segundo
        self.scroll_speed_increase_rate = 0.002
        self.spawn_rate_decrease_rate = 0.005
        self.enemy_speed_increase_rate = 0.004
        self.hole_spawn_increase_rate = 0.00006  # Reduzido para progressão mais lenta
        self.oil_stain_spawn_increase_rate = 0.00006  # Reduzido para progressão mais lenta
        self.invulnerability_spawn_increase_rate = 0.0001  # Aumento gradual da chance de power-ups
        self.slowmotion_spawn_increase_rate = 0.00008  # Aumento gradual da chance de slow motion

        # Limites máximos para evitar valores extremos
        self.max_scroll_speed_multiplier = 2.0
        self.min_spawn_rate_multiplier = 0.20
        self.max_enemy_speed_multiplier = 2.5
        self.max_hole_spawn_probability = 0.5  # Máximo de 50% de chance
        self.max_oil_stain_spawn_probability = 0.4  # Máximo de 40% de chance
        self.max_invulnerability_spawn_probability = 0.8  # Aumentado para 80% para facilitar testes
        self.max_beer_spawn_probability = 0.8  # Máximo de 80% de chance, igual à invulnerabilidade
        self.max_slowmotion_spawn_probability = 0.5  # Máximo de 50% de chance para slow motion

        # Controles para ajustes manuais
        self.manual_control_enabled = False
        self.last_update_time = 0
        
        # Contadores para spawn forçado
        self.invulnerability_spawn_counter = 0
        self.slowmotion_spawn_counter = 0

    def update(self, current_time, score):
        """
        Atualiza os multiplicadores baseados no tempo e pontuação
        current_time: tempo decorrido em segundos
        score: pontuação atual do jogador
        """
        if current_time == 0:
            self.last_update_time = current_time
            return

        # Calcula o delta time
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        if not self.manual_control_enabled:
            # Atualização automática baseada no tempo
            self.scroll_speed_multiplier = min(
                self.scroll_speed_multiplier + (self.scroll_speed_increase_rate * delta_time),
                self.max_scroll_speed_multiplier
            )

            self.spawn_rate_multiplier = max(
                self.spawn_rate_multiplier - (self.spawn_rate_decrease_rate * delta_time),
                self.min_spawn_rate_multiplier
            )

            self.enemy_speed_multiplier = min(
                self.enemy_speed_multiplier + (self.enemy_speed_increase_rate * delta_time),
                self.max_enemy_speed_multiplier
            )
            
            # Atualiza a probabilidade de spawn de buracos
            self.hole_spawn_probability = min(
                self.hole_spawn_probability + (self.hole_spawn_increase_rate * delta_time),
                self.max_hole_spawn_probability
            )
            
            # Atualiza a probabilidade de spawn de manchas de óleo
            self.oil_stain_spawn_probability = min(
                self.oil_stain_spawn_probability + (self.oil_stain_spawn_increase_rate * delta_time),
                self.max_oil_stain_spawn_probability
            )
            
            # Atualiza a probabilidade de spawn de power-ups de invulnerabilidade
            self.invulnerability_spawn_probability = min(
                self.invulnerability_spawn_probability + (self.invulnerability_spawn_increase_rate * delta_time),
                self.max_invulnerability_spawn_probability
            )
            
            # Atualiza a probabilidade de spawn de power-ups de slow motion
            self.slowmotion_spawn_probability = min(
                self.slowmotion_spawn_probability + (self.slowmotion_spawn_increase_rate * delta_time),
                self.max_slowmotion_spawn_probability
            )

    def get_current_scroll_speed(self):
        """Retorna a velocidade de rolagem atual"""
        return self.base_scroll_speed * self.scroll_speed_multiplier

    def get_current_spawn_rate(self):
        """Retorna a taxa de spawn atual"""
        return self.base_spawn_rate * self.spawn_rate_multiplier

    def get_current_enemy_speed_multiplier(self):
        """Retorna o multiplicador de velocidade dos inimigos"""
        return self.enemy_speed_multiplier
    
    def get_current_hole_spawn_probability(self):
        """Retorna a probabilidade atual de spawn de buracos"""
        return self.hole_spawn_probability
        
    def get_current_oil_stain_spawn_probability(self):
        """Retorna a probabilidade atual de spawn de manchas de óleo"""
        return self.oil_stain_spawn_probability
        
    def get_current_invulnerability_spawn_probability(self):
        """Retorna a probabilidade atual de spawn de power-ups de invulnerabilidade"""
        return self.invulnerability_spawn_probability
    
    def get_current_slowmotion_spawn_probability(self):
        """Retorna a probabilidade atual de spawn de power-ups de slow motion"""
        return self.slowmotion_spawn_probability

    def adjust_scroll_speed_multiplier(self, delta):
        """Ajusta manualmente o multiplicador de velocidade de rolagem"""
        if self.manual_control_enabled:
            self.scroll_speed_multiplier = max(0.1, min(
                self.scroll_speed_multiplier + delta,
                self.max_scroll_speed_multiplier
            ))

    def adjust_spawn_rate_multiplier(self, delta):
        """Ajusta manualmente o multiplicador de taxa de spawn"""
        if self.manual_control_enabled:
            self.spawn_rate_multiplier = max(0.1, min(
                self.spawn_rate_multiplier + delta,
                2.0  # Limite superior para spawn rate
            ))

    def adjust_enemy_speed_multiplier(self, delta):
        """Ajusta manualmente o multiplicador de velocidade dos inimigos"""
        if self.manual_control_enabled:
            self.enemy_speed_multiplier = max(0.1, min(
                self.enemy_speed_multiplier + delta,
                self.max_enemy_speed_multiplier
            ))
            
    def adjust_hole_spawn_probability(self, delta):
        """Ajusta manualmente a probabilidade de spawn de buracos"""
        if self.manual_control_enabled:
            self.hole_spawn_probability = max(0.0, min(
                self.hole_spawn_probability + delta,
                self.max_hole_spawn_probability
            ))
            
    def adjust_oil_stain_spawn_probability(self, delta):
        """Ajusta manualmente a probabilidade de spawn de manchas de óleo"""
        if self.manual_control_enabled:
            self.oil_stain_spawn_probability = max(0.0, min(
                self.oil_stain_spawn_probability + delta,
                self.max_oil_stain_spawn_probability
            ))
            
    def adjust_invulnerability_spawn_probability(self, delta):
        """Ajusta manualmente a probabilidade de spawn de power-ups de invulnerabilidade"""
        if self.manual_control_enabled:
            self.invulnerability_spawn_probability = max(0.0, min(
                self.invulnerability_spawn_probability + delta,
                self.max_invulnerability_spawn_probability
            ))
    
    def adjust_slowmotion_spawn_probability(self, delta):
        """Ajusta manualmente a probabilidade de spawn de power-ups de slow motion"""
        if self.manual_control_enabled:
            self.slowmotion_spawn_probability = max(0.0, min(
                self.slowmotion_spawn_probability + delta,
                self.max_slowmotion_spawn_probability
            ))

    def reset(self):
        """Reseta todos os multiplicadores para os valores iniciais"""
        self.scroll_speed_multiplier = 1.0
        self.spawn_rate_multiplier = 1.0
        self.enemy_speed_multiplier = 1.0
        self.hole_spawn_probability = self.base_hole_spawn_probability
        self.oil_stain_spawn_probability = self.base_oil_stain_spawn_probability
        self.invulnerability_spawn_probability = self.base_invulnerability_spawn_probability
        self.beer_spawn_probability = self.base_beer_spawn_probability
        self.slowmotion_spawn_probability = self.base_slowmotion_spawn_probability
        self.invulnerability_spawn_counter = 0
        self.slowmotion_spawn_counter = 0
        self.last_update_time = 0

    def toggle_manual_control(self):
        """Alterna entre controle automático e manual"""
        self.manual_control_enabled = not self.manual_control_enabled

    def adjust_beer_spawn_probability(self, delta):
        """Ajusta manualmente a probabilidade de spawn de cerveja"""
        if self.manual_control_enabled:
            self.beer_spawn_probability = max(0.0, min(
                self.beer_spawn_probability + delta,
                self.max_beer_spawn_probability
            ))

    def get_current_beer_spawn_probability(self):
        """Retorna a probabilidade atual de spawn de cerveja"""
        return self.beer_spawn_probability

    def get_difficulty_info(self):
        """Retorna informações sobre a dificuldade atual para exibição"""
        return {
            "scroll_speed_multiplier": self.scroll_speed_multiplier,
            "spawn_rate_multiplier": self.spawn_rate_multiplier,
            "enemy_speed_multiplier": self.enemy_speed_multiplier,
            "hole_spawn_probability": self.hole_spawn_probability,
            "oil_stain_spawn_probability": self.oil_stain_spawn_probability,
            "invulnerability_spawn_probability": self.invulnerability_spawn_probability,
            "beer_spawn_probability": self.beer_spawn_probability,
            "slowmotion_spawn_probability": self.slowmotion_spawn_probability,
            "current_scroll_speed": self.get_current_scroll_speed(),
            "current_spawn_rate": self.get_current_spawn_rate(),
            "manual_control": self.manual_control_enabled
        }