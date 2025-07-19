import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from tkinterdnd2 import DND_FILES, TkinterDnD
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from utils.caminhos import get_pasta_cofre
from cryptography.hazmat.backends import default_backend

pasta_cofre = get_pasta_cofre()

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)

backend = default_backend()


def abrir_janela_destrancar():
    janela = TkinterDnD.Tk()
    janela.title("🔓 Destrancar Cofre")
    janela.geometry("400x350")
    janela.resizable(False, False)

    label_info = ttk.Label(janela, text="Arraste aqui o arquivo .sjson")
    label_info.pack(pady=10)

    drop_frame = ttk.LabelFrame(janela, height=100, width=300)
    drop_frame.pack(pady=10)
    drop_frame.pack_propagate(False)

    label_status = ttk.Label(janela, text="")
    label_status.pack(pady=5)

    caminho_arquivo = {"path": None}

    def abrir_arquivo():
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de backup",
            filetypes=[("Arquivo do Cofre", "*.sjson")],
        )
        if path:
            caminho_arquivo["path"] = path
            label_status.config(text=f"Arquivo selecionado: {os.path.basename(path)}")

    def drop(event):
        caminho = event.data.strip("{}")  # Remove { } do caminho (Windows)
        if not caminho.endswith(".sjson"):
            messagebox.showerror("Erro", "Arquivo inválido. Arraste um arquivo .sjson.")
            return

        caminho_arquivo["path"] = caminho
        label_status.config(text=f"Arquivo selecionado: {os.path.basename(caminho)}")

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", drop)

    def descriptografar():
        if not caminho_arquivo["path"]:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
            return

        senha = simpledialog.askstring("Chave", "Digite a senha do backup:", show="*")
        if not senha:
            return

        try:
            with open(caminho_arquivo["path"], "rb") as f:
                iv = f.read(16)
                salt = f.read(16)
                dados_cripto = f.read()

            chave_gerada = PBKDF2(senha, salt, dkLen=32, count=100_000)

            cipher = AES.new(chave_gerada, AES.MODE_CBC, iv)
            dados = unpad(cipher.decrypt(dados_cripto), AES.block_size)

            # Caminho final do arquivo descriptografado na pasta cofre
            destino_final = os.path.join(pasta_cofre, "._dados.sjson")

            # Se já existir, exclui
            if os.path.exists(destino_final):
                os.remove(destino_final)

            with open(destino_final, "wb") as f:
                f.write(dados)

            messagebox.showinfo("Sucesso", "Cofre destrancado com sucesso!")
            janela.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao destrancar cofre: {e}")

    ttk.Button(janela, text="Selecionar Arquivo", command=abrir_arquivo).pack(pady=5)
    ttk.Button(janela, text="Descriptografar Cofre", command=descriptografar).pack(
        pady=10
    )
