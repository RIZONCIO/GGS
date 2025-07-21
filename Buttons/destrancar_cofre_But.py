import os
import zipfile
from tkinter import ttk, filedialog, simpledialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from utils.caminhos import get_pasta_cofre

pasta_cofre = get_pasta_cofre()

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)


def abrir_janela_destrancar():
    janela = TkinterDnD.Tk()
    janela.title("🔓 Destrancar Cofre")
    janela.geometry("400x350")
    janela.resizable(False, False)

    label_info = ttk.Label(janela, text="Arraste aqui o backup_cofre.zip.enc")
    label_info.pack(pady=10)

    drop_frame = ttk.LabelFrame(janela, height=100, width=300)
    drop_frame.pack(pady=10)
    drop_frame.pack_propagate(False)

    label_status = ttk.Label(janela, text="")
    label_status.pack(pady=5)

    caminho_arquivo = {"path": None}

    def abrir_arquivo():
        path = filedialog.askopenfilename(filetypes=[("Backup Criptografado", "*.enc")])
        if path:
            caminho_arquivo["path"] = path
            label_status.config(text=f"Selecionado: {os.path.basename(path)}")

    def drop(event):
        caminho = event.data.strip("{}")
        if not caminho.endswith(".enc"):
            messagebox.showerror("Erro", "Arquivo inválido. Esperado: .zip.enc")
            return

        caminho_arquivo["path"] = caminho
        label_status.config(text=f"Selecionado: {os.path.basename(caminho)}")

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", drop)

    def descriptografar():
        if not caminho_arquivo["path"]:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
            return

        senha = simpledialog.askstring("Senha", "Digite a senha do backup:", show="*")
        if not senha:
            return

        try:
            with open(caminho_arquivo["path"], "rb") as f:
                iv = f.read(16)
                salt = f.read(16)
                dados_cripto = f.read()

            chave = PBKDF2(senha, salt, dkLen=32, count=100_000)
            cipher = AES.new(chave, AES.MODE_CBC, iv)
            dados_zip = unpad(cipher.decrypt(dados_cripto), AES.block_size)

            zip_temp = os.path.join(pasta_cofre, "__temp_restore.zip")
            with open(zip_temp, "wb") as f:
                f.write(dados_zip)

            with zipfile.ZipFile(zip_temp, "r") as zipf:
                zipf.extractall(pasta_cofre)

            os.remove(zip_temp)

            messagebox.showinfo("Sucesso", "Cofre restaurado com sucesso!")
            janela.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar backup: {e}")

    ttk.Button(janela, text="Selecionar Arquivo", command=abrir_arquivo).pack(pady=5)
    ttk.Button(janela, text="Descriptografar Cofre", command=descriptografar).pack(
        pady=10
    )
