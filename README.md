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