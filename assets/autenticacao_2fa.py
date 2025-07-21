import os
import pyotp
import qrcode
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.caminhos import get_pasta_cofre

pasta_cofre = get_pasta_cofre()
ARQUIVO_CHAVE = os.path.join(pasta_cofre, "chave_2fa.txt")
SESSAO_ATIVA = False

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)


def gerar_ou_obter_chave():
    if os.path.exists(ARQUIVO_CHAVE):
        with open(ARQUIVO_CHAVE, "r") as f:
            return f.read()
    else:
        chave = pyotp.random_base32()
        with open(ARQUIVO_CHAVE, "w") as f:
            f.write(chave)
        return chave


def solicitar_nome_usuario():
    nome_resultado = [None]

    def confirmar():
        nome = entrada_nome.get().strip()
        if nome == "":
            messagebox.showwarning(
                "Atenção", "Obrigatório colocar um nome ou apelido para o seu Armazém."
            )
        else:
            nome_resultado[0] = nome
            janela.destroy()

    janela = tk.Toplevel()
    janela.title("Nome do Seu Cofre")
    janela.geometry("400x150")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Obrigatório colocar um nome ou apelido para o seu Cofre",
        font=("Arial", 11, "bold"),
        wraplength=380,
    ).pack(pady=10)
    entrada_nome = tk.Entry(janela, font=("Arial", 14), justify="center")
    entrada_nome.pack(pady=5)
    entrada_nome.focus()

    tk.Button(janela, text="Confirmar", command=confirmar).pack(pady=10)

    janela.wait_window()
    return nome_resultado[0]


def mostrar_qrcode_gui(otpauth_url):
    def permitir_fechar():
        janela.protocol("WM_DELETE_WINDOW", janela.destroy)
        btn_fechar.pack(pady=20)
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def impedir_fechamento():
        messagebox.showwarning(
            "Atenção", "Você precisa escanear o QR Code antes de fechar."
        )

    janela = tk.Toplevel()
    janela.title("Escaneie com o Google Authenticator")
    janela.geometry("320x450")
    janela.resizable(False, False)

    # Impede o botão de fechar
    janela.protocol("WM_DELETE_WINDOW", impedir_fechamento)

    qr = qrcode.make(otpauth_url)
    temp_path = os.path.join(pasta_cofre, "qrcode_temp.png")
    qr.save(temp_path)
    imagem = Image.open(temp_path).resize((250, 250))

    imagem_tk = ImageTk.PhotoImage(imagem)

    tk.Label(
        janela, text="🔒 Cofre Seguro", font=("Arial", 14, "bold"), fg="#004080"
    ).pack(pady=(10, 5))

    tk.Label(
        janela, text="Escaneie com o Google Authenticator", font=("Arial", 10)
    ).pack()

    label = tk.Label(janela, image=imagem_tk)
    label.image = imagem_tk
    label.pack(pady=10)

    # Botão "Fechar" escondido por padrão
    btn_fechar = tk.Button(
        janela,
        text="Fechar",
        command=janela.destroy,
        bg="#c0392b",  # vermelho escuro
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        padx=20,
        pady=10,
    )

    janela.after(9000, permitir_fechar)

    janela.grab_set()
    janela.wait_window()


def solicitar_codigo_gui():
    codigo_valido = [None]

    def validar(event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return
        if not event.char.isdigit():
            return "break"

    def confirmar():
        entrada = codigo_entry.get().strip().replace(" ", "")
        if len(entrada) == 6 and entrada.isdigit():
            codigo_valido[0] = entrada
            janela.destroy()
        else:
            messagebox.showerror(
                "Erro", "Digite um código válido com 6 dígitos numéricos."
            )

    janela = tk.Toplevel()
    janela.title("Verificação 2FA")
    janela.geometry("300x150")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(janela, text="Digite o código de 6 dígitos:").pack(pady=10)
    codigo_entry = tk.Entry(janela, font=("Consolas", 16), justify="center")
    codigo_entry.pack()
    codigo_entry.focus()
    codigo_entry.bind("<Key>", validar)
    codigo_entry.bind("<Return>", lambda e: confirmar())

    tk.Button(janela, text="Verificar", command=confirmar).pack(pady=10)
    janela.wait_window()

    return codigo_valido[0]


def verificar_2fa_gui():
    global SESSAO_ATIVA
    if SESSAO_ATIVA:
        return True

    chave = gerar_ou_obter_chave()
    totp = pyotp.TOTP(chave)

    FLAG_QRCODE = os.path.join(pasta_cofre, "qrcode_ja_mostrado.flag")
    if not os.path.exists(FLAG_QRCODE):
        nome_user = solicitar_nome_usuario()
        if not nome_user:
            return False

        url = totp.provisioning_uri(name=nome_user, issuer_name="ArmazemSeguro")
        mostrar_qrcode_gui(url)

        with open(FLAG_QRCODE, "w") as f:
            f.write("ok")

    codigo = solicitar_codigo_gui()
    if not codigo:
        return False

    if totp.verify(codigo, valid_window=1):
        SESSAO_ATIVA = True
        return True
    else:
        messagebox.showerror("Erro", "Código inválido ou expirado.")
        return False
