# Beer Truck - Projeto OpenGL

Este é um projeto de jogo desenvolvido com Python e OpenGL.

Versão do Python: 3.13.6

Recomendado utilizar o PyCharm que possui suporte nativo para projetos Python e facilita a gestão de ambientes virtuais.

## Configuração do Ambiente Virtual

### 1. Verificar se o venv está instalado:
```cmd
python -m venv --help
```

Se o comando acima retornar erro, instale o venv:

**Ubuntu/Debian:**
```bash
sudo apt install python3-venv
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install python3-venv
# ou para versões mais recentes:
sudo dnf install python3-venv
```

**Windows/Mac:**
O venv já vem incluído com Python 3.3+

### 2. Criar o ambiente virtual:
```cmd
python -m venv .venv
```

### 3. Ativar o ambiente virtual:

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/Mac ou Git Bash:**
```bash
source .venv/bin/activate
```

### 4. Instalar dependências:
```cmd
pip install -r requirements.txt
```

### 5. Desativar o ambiente virtual:
```cmd
deactivate
```

## Dependências incluídas:
- **PyOpenGL 3.1.9** - Biblioteca para programação OpenGL
- **PyGLFW 2.7.0** - Biblioteca para criação de janelas OpenGL
- **Pillow 10.4.0** - Biblioteca para manipulação de imagens
- **numpy 2.1.1** - Biblioteca para computação científica

## Como executar:
```cmd
python main.py

## Configurações

O jogo utiliza um arquivo `settings.json` para armazenar as configurações do jogador. Este arquivo é criado automaticamente na primeira vez que o jogo é executado e é atualizado em tempo real conforme as opções são alteradas no menu de configurações.

### Estrutura do `settings.json`

O arquivo tem a seguinte estrutura:

```json
{
  "version": 1,
  "audio": {
    "master": 1.0,
    "music": 0.5,
    "sfx": 0.8
  },
  "toggles": {
    "beer": True,
    "invulnerability": True,
    "holes": True,
    "oil": False,
    "police": True
  },
  "joystick": {
    "selected_guid": "GUID_DO_CONTROLE"
  }
}
```

- **audio**: Contém os níveis de volume.
  - `master`: Volume geral do jogo.
  - `music`: Volume da música de fundo.
  - `sfx`: Volume dos efeitos sonoros.
- **toggles**: Permite ativar ou desativar elementos do jogo.
  - `beer`, `invulnerability`, `holes`, `oil`, `police`: Se `false`, o elemento correspondente não aparecerá no jogo.
- **joystick**: Armazena o controle selecionado.
  - `selected_guid`: GUID do joystick selecionado.

Se o arquivo `settings.json` for corrompido ou excluído, ele será recriado com os valores padrão na próxima inicialização do jogo.