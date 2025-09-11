import json
import os

class HighScoreManager:
    def __init__(self, file_path="data/highscores.json"):
        # Se o caminho não for absoluto, torna-o relativo ao diretório do projeto
        if not os.path.isabs(file_path):
            # Encontra o diretório raiz do projeto (onde está o main.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..", "..")
            project_root = os.path.normpath(project_root)
            self.file_path = os.path.join(project_root, file_path)
        else:
            self.file_path = file_path
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
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
        # Mantém apenas os top 3
        if len(self.high_scores) > 3:
            self.high_scores = self.high_scores[:3]
        self.save_high_scores()

    def get_top_scores(self, limit=3):
        """Retorna os melhores scores até o limite especificado."""
        return self.high_scores[:limit]

    def get_highest_score(self):
        """Retorna a maior pontuação."""
        if self.high_scores:
            return self.high_scores[0]
        return {"name": "---", "score": 0}

    def is_high_score(self, score):
        """Verifica se a pontuação é um novo high score."""
        if not self.high_scores:  # Se não houver pontuações salvas
            return True

        if len(self.high_scores) < 3:  # Se há menos de 3 recordes
            return score > 0  # Aceita qualquer pontuação maior que zero

        # Se tiver 3 recordes, verifica se a pontuação é maior que o menor deles
        lowest_score = self.high_scores[-1]["score"] if self.high_scores else 0
        return score > lowest_score
    
    def change_file_path(self, new_file_path):
        """Permite alterar o caminho do arquivo de high scores."""
        # Salva os dados atuais no local antigo antes de mudar
        self.save_high_scores()
        
        # Atualiza o caminho
        if not os.path.isabs(new_file_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, "..", "..", "..")
            project_root = os.path.normpath(project_root)
            self.file_path = os.path.join(project_root, new_file_path)
        else:
            self.file_path = new_file_path
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Carrega os dados do novo local (ou cria arquivo vazio se não existir)
        self.load_high_scores()
    
    def get_current_file_path(self):
        """Retorna o caminho atual do arquivo de high scores."""
        return self.file_path
    
    def reset_high_scores(self):
        """Reseta todos os high scores (limpa a lista)."""
        self.high_scores = []
        self.save_high_scores()
