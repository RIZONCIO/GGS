import os
import hashlib
from tkinter import filedialog, messagebox, Toplevel, StringVar, simpledialog, ttk
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import pyperclip
from utils.caminhos import get_pasta_cofre

# Caminho completo para a pasta cofre
pasta_cofre = get_pasta_cofre()
ARQUIVO_DADOS = os.path.join(pasta_cofre, "._dados.sjson")

# Garante que a pasta cofre exista
if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)


def mostrar_chave_backup(chave):
    janela = Toplevel()
    janela.title("Chave do Backup")
    janela.geometry("400x150")
    janela.resizable(False, False)

    ttk.Label(janela, text="🔐 Guarde esta chave com segurança:").pack(pady=10)

    chave_var = StringVar(value=chave)
    entry = ttk.Entry(janela, textvariable=chave_var, state="readonly", width=50)
    entry.pack(pady=5)

    def copiar():
        pyperclip.copy(chave_var.get())

    ttk.Button(janela, text="Copiar chave", command=copiar).pack(pady=10)
    janela.grab_set()


def backup_e_trancar_cofre():
    try:
        if not os.path.exists(ARQUIVO_DADOS):
            messagebox.showerror(
                "Erro", f"Arquivo de dados não encontrado: {ARQUIVO_DADOS}"
            )
            return

        destino_pasta = filedialog.askdirectory(
            title="Escolha a pasta para salvar o backup"
        )
        if not destino_pasta:
            return

        senha = simpledialog.askstring(
            "Senha", "Digite uma senha para proteger o backup:", show="*"
        )
        if not senha or len(senha) < 6:
            messagebox.showerror("Erro", "Senha muito curta.")
            return

        with open(ARQUIVO_DADOS, "rb") as origem:
            dados = origem.read()

        # Geração de salt e derivação segura da chave
        salt = get_random_bytes(16)
        chave_gerada = PBKDF2(senha, salt, dkLen=32, count=100_000)

        # Criptografia com AES
        iv = get_random_bytes(16)
        cipher = AES.new(chave_gerada, AES.MODE_CBC, iv)
        dados_criptografados = iv + salt + cipher.encrypt(pad(dados, AES.block_size))

        destino_arquivo = os.path.join(destino_pasta, "._dados.sjson")
        with open(destino_arquivo, "wb") as destino:
            destino.write(dados_criptografados)

        messagebox.showinfo("Backup", "Backup criptografado e salvo com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao realizar backup: {e}")
