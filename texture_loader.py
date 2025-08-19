# File: texture_loader.py
from OpenGL.GL import *
from PIL import Image
import numpy as np


def load_texture(path):
    """Carrega uma imagem e a converte em uma textura OpenGL."""
    try:
        # Abre a imagem e a converte para o formato RGBA
        img = Image.open(path).convert("RGBA")
        # Converte diretamente para um array numpy (HxWx4) de uint8
        img_data = np.array(img, dtype=np.uint8)

        # Gera um ID para a textura
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Configura os parâmetros da textura para evitar que ela fique borrada
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 1. Carrega os dados da imagem para a textura
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        # 2. Gera os mipmaps DEPOIS de a imagem ter sido carregada
        glGenerateMipmap(GL_TEXTURE_2D)

        return texture_id
    except FileNotFoundError:
        print(f"Erro: Arquivo de imagem não encontrado em '{path}'")
        return None