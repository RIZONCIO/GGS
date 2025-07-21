import os
import zipfile
from tkinter import filedialog, messagebox, simpledialog, Toplevel, StringVar, ttk
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import pyperclip
from utils.caminhos import get_pasta_cofre

pasta_cofre = get_pasta_cofre()


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


def zipar_pasta_cofre(arquivo_zip):
    with zipfile.ZipFile(arquivo_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(pasta_cofre):
            for file in files:
                caminho_absoluto = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_absoluto, pasta_cofre)
                zipf.write(caminho_absoluto, caminho_relativo)


def backup_e_trancar_cofre():
    try:
        destino_pasta = filedialog.askdirectory(title="Escolha onde salvar o backup")
        if not destino_pasta:
            return

        senha = simpledialog.askstring(
            "Senha", "Digite uma senha para o backup:", show="*"
        )
        if not senha or len(senha) < 6:
            messagebox.showerror("Erro", "Senha muito curta.")
            return

        # Caminho do .zip temporário
        zip_temp = os.path.join(destino_pasta, "backup_temp.zip")
        zipar_pasta_cofre(zip_temp)

        with open(zip_temp, "rb") as f:
            dados = f.read()

        os.remove(zip_temp)

        salt = get_random_bytes(16)
        chave = PBKDF2(senha, salt, dkLen=32, count=100_000)
        iv = get_random_bytes(16)
        cipher = AES.new(chave, AES.MODE_CBC, iv)
        criptografado = iv + salt + cipher.encrypt(pad(dados, AES.block_size))

        caminho_saida = os.path.join(destino_pasta, "backup_cofre.zip.enc")
        with open(caminho_saida, "wb") as f:
            f.write(criptografado)

        messagebox.showinfo("Sucesso", "Backup criptografado e salvo com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar backup: {e}")
