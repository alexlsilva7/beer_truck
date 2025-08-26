import json
import os

class HighScoreManager:
    def __init__(self, file_path="highscores.json"):
        self.file_path = file_path
        self.high_scores = []
        self.load_high_scores()

    def load_high_scores(self):
        """Carrega os high scores do arquivo."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.high_scores = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # Se o arquivo estiver corrompido ou vazio, inicializa com lista vazia
                self.high_scores = []
        else:
            # Arquivo não existe, inicializa com lista vazia
            self.high_scores = []
            self.save_high_scores()

    def save_high_scores(self):
        """Salva os high scores no arquivo."""
        with open(self.file_path, 'w') as f:
            json.dump(self.high_scores, f, indent=2)

    def add_high_score(self, name, score):
        """Adiciona um novo high score à lista e reordena."""
        self.high_scores.append({"name": name, "score": score})
        # Ordena por pontuação em ordem decrescente
        self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)
        # Mantém apenas os top 10
        if len(self.high_scores) > 10:
            self.high_scores = self.high_scores[:10]
        self.save_high_scores()

    def get_top_scores(self, limit=10):
        """Retorna os melhores scores até o limite especificado."""
        return self.high_scores[:limit]

    def get_highest_score(self):
        """Retorna a maior pontuação."""
        if self.high_scores:
            return self.high_scores[0]
        return {"name": "---", "score": 0}

    def is_high_score(self, score):
        """Verifica se a pontuação é um novo high score."""
        if len(self.high_scores) < 10:
            return True
        return score > min([hs["score"] for hs in self.high_scores])
