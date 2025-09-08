import os
import json
import base64
import os
from cryptography.fernet import Fernet
from utils.caminhos import get_pasta_cofre
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from tkinter import messagebox

pasta_cofre = get_pasta_cofre()

ARQUIVO_CHAVE = os.path.join(pasta_cofre, ".chave_aes")
ARQUIVO_DADOS = os.path.join(pasta_cofre, "._dados.sjson")

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)

backend = default_backend()


# ========== GERAR OU OBTER CHAVE AES ==========
def obter_chave():
    if not os.path.exists(ARQUIVO_CHAVE):
        chave = os.urandom(32)  # 256 bits
        with open(ARQUIVO_CHAVE, "wb") as f:
            f.write(chave)
    else:
        with open(ARQUIVO_CHAVE, "rb") as f:
            chave = f.read()
    return chave


# ========== CRIPTOGRAFAR ==========
def criptografar(dado):
    chave = obter_chave()
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    dado_preenchido = padder.update(dado.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    criptografado = encryptor.update(dado_preenchido) + encryptor.finalize()

    return base64.b64encode(iv + criptografado).decode()


# ========== DESCRIPTOGRAFAR ==========
def descriptografar(dado_base64):
    chave = obter_chave()
    dado_bytes = base64.b64decode(dado_base64)
    iv = dado_bytes[:16]
    criptografado = dado_bytes[16:]

    cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    dados_preenchidos = decryptor.update(criptografado) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(dados_preenchidos) + unpadder.finalize()).decode()


def gerar_fernet(chave_hex: str):
    key_bytes = bytes.fromhex(chave_hex)
    key_hash = hashlib.sha256(key_bytes).digest()
    key_b64 = base64.urlsafe_b64encode(key_hash)
    return Fernet(key_b64)


def criptografar_com_chave(dados_bytes: bytes, chave_hex: str) -> bytes:
    f = gerar_fernet(chave_hex)
    return f.encrypt(dados_bytes)


def descriptografar_com_chave(dados_bytes: bytes, chave_hex: str) -> bytes:
    f = gerar_fernet(chave_hex)
    return f.decrypt(dados_bytes)


# ========== ARMAZENAR ==========
def armazenar_senha(keyword, conteudo):
    try:
        dados = {}
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r") as f:
                dados = json.load(f)

        criptografado = criptografar(conteudo)
        if keyword not in dados:
            dados[keyword] = []
        dados[keyword].append(criptografado)

        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(dados, f, indent=2)

        messagebox.showinfo("Sucesso", "Senha salva com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")


# ========== CONSULTAR ==========
def consultar_por_palavra_chave(keyword):
    try:
        if not os.path.exists(ARQUIVO_DADOS):
            return []

        with open(ARQUIVO_DADOS, "r") as f:
            dados = json.load(f)

        resultados = []
        for chave, valores in dados.items():
            if keyword.lower() in chave.lower():
                for v in valores:
                    try:
                        resultados.append(descriptografar(v))
                    except:
                        continue  # dado corrompido ou chave inválida

        return resultados
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao consultar: {str(e)}")
        return []
