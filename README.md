# Beer Truck - Projeto OpenGL 🍺🚚

Bem-vindos ao Beer Truck! Aqui você é o motorista de um caminhão de cerveja tentando cruzar a cidade sem virar estatística. A missão? Pontuar o máximo possível desviando de tudo — carros, buracos e, claro, da polícia.

A vibe é de corrida arcade com sobrevivência: quanto mais você aguenta na pista, mais caótico fica. Mais tráfego, mais buracos, mais poças de óleo… mas também mais power-ups. É um jogo de reflexo e estratégia: saber quando arriscar e quando jogar no seguro.

Seu objetivo final: entrar no Top 3 do placar. Se conseguir, o jogo pede seu nome pra registrar essa lenda.

![Screenshot do Jogo](assets/game.png)

*Este projeto foi inspirado no clássico jogo de mesmo nome. [Veja uma gameplay do original aqui](https://www.youtube.com/watch?v=HxiF3LyitWw).*

---

## Como Jogar

### Versão Executável (Windows)

A maneira mais fácil de jogar é baixando o executável. Não precisa instalar nada!

➡️ **[Baixar beer_truck.1.0.exe](https://github.com/alexlsilva7/beer_truck/releases/download/1.0/beer_truck.1.0.exe)**

### Controles

O jogo tem suporte para teclado e controle (joystick).

#### Teclado
* **Setas Direcionais:** Mover, Acelerar e Frear
* **Barra de Espaço:** Buzinar
* **ESC:** Pausar o jogo ou voltar ao menu
* **Alt + Enter:** Alternar para tela cheia

#### Controle / Joystick
* **Analógico / D-Pad:** Mover, Acelerar e Frear
* **Botão 'X' (Padrão PS2):** Buzinar

---

## Gameplay e Funcionalidades

### Itens e Obstáculos
Fique de olho nos seguintes itens e perigos na pista:

* **🍺 Cerveja:** O item mais importante! Colete para ganhar pontos extras.
* **🛡️ Escudo:** Te deixa invencível por um tempo, destruindo qualquer veículo no seu caminho.
* **⏰ Relógio:** Ativa a câmera lenta, diminuindo a velocidade de tudo ao seu redor e facilitando os desvios.
* **⚫ Mancha de Óleo:** Cuidado! Passar por ela inverte seus controles temporariamente.
* **🕳️ Buraco:** Reduz drasticamente a sua velocidade por alguns segundos.
* **🚓 Polícia:** O inimigo mais perigoso. Eles vão te perseguir ativamente pela pista!

### Principais Funcionalidades
* **Dificuldade Dinâmica:** O jogo se torna progressivamente mais difícil, aumentando a velocidade e a frequência de inimigos/obstáculos.
* **Sistema de High Score:** O jogo salva o Top 3 de melhores pontuações em um arquivo `json`.
* **Suporte a Controle (Joystick):** Totalmente compatível com controles.
* **Modo Debug:** Inclui um modo para visualizar as *hitboxes* de todos os objetos (ativado pela tecla 'H').

---

## Sobre o Projeto

### Integrantes do Grupo
* [Alex Lopes](https://github.com/alexlsilva7)
* [Victor Saraiva](https://github.com/Victor-Saraiva-P)
* [Clauderson Xavier](https://github.com/ClaudersonXavier)
* [Aline Fernanda](https://github.com/alinesors)

### Disciplina
Este projeto foi desenvolvido para a disciplina de **Computação Gráfica (2025.1)** do curso de **Ciência da Computação** da **Universidade Federal do Agreste de Pernambuco (UFAPE)**.

### Tecnologias Utilizadas
* **Python 3**
* **PyOpenGL** (para renderização)
* **GLFW** (para janela e inputs)
* **Pygame** (para áudio e suporte a controle)
* **Pillow (PIL)** (para carregar texturas)

---

## Executando pelo Código-Fonte

1.  **Crie e ative um ambiente virtual:**
    ```bash
    # Cria o ambiente
    python -m venv .venv

    # Ativa no Windows (Git Bash, Linux ou Mac)
    source .venv/bin/activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o jogo:**
    ```bash
    python main.py
    ```