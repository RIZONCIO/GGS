import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox
import assets.cripto_cofre as cripto_cofre
import re
from urllib.parse import urlparse


def abrir_cofre_window(password="", keyword=""):
    # Janela principal
    janela = ttkb.Toplevel()
    janela.title("Salvar no Cofre")
    janela.geometry("800x500")
    janela.resizable(False, False)
    style = ttkb.Style("cosmo")

    # ========== FUNÇÕES AUXILIARES ==========

    def ofuscar_email(email):
        if "@" not in email:
            return email
        nome, dominio = email.split("@")
        return nome[:4] + "***@" + dominio

    def alternar_visibilidade():
        atual = senha_entry.cget("show")
        if atual == "":
            senha_entry.config(show="*")
            olho_btn.config(text="👁")
        else:
            senha_entry.config(show="")
            olho_btn.config(text="🔒")

    # ========== FUNÇÃO PRINCIPAL DE SALVAR ==========
    def salvar():
        url_site = site_entry.get().strip()
        email = email_entry.get().strip()
        nick = nickname_entry.get().strip()
        senha = senha_entry.get().strip()

        # Verificação mínima
        if not url_site and not email and not nick:
            aviso_label.config(text="⚠️ Insira 2 Campos.")
            return

        # Validação do nome do site/serviço
        if url_site and not re.match(r"^[a-zA-Z0-9\s\-_.]+$", url_site):
            aviso_label.config(
                text="⚠️ Site/Serviço inválido. Use apenas letras e números."
            )
            return

        # Validação do email (caso tenha sido preenchido)
        if email and not re.match(
            r"^[\w\.-]+@(?:gmail|outlook|hotmail|proton|protonmail|yahoo|icloud|tuta|tutamail|tutanota|mytaemin|tuamaeaquelaursa|)\.com|me|de|io$",
            email,
        ):
            aviso_label.config(
                text="⚠️ E-mail inválido. Use @gmail.com, @hotmail.com ou @outlook.com."
            )
            return

        dominio = url_site

        # Conteúdo formatado
        email_ofuscado = (
            f"Email: {ofuscar_email(email)}" if email else "Email: Não informado"
        )
        nick_formatado = f"Nick: {nick}" if nick else "Nick: Não informado"
        senha_final = senha if senha else "Não informada"

        conteudo = (
            f"Site: {dominio.strip()}\n"
            f"{email_ofuscado.strip()}\n"
            f"{nick_formatado.strip()}\n"
            f"Senha: {senha_final.strip()}\n"
        )

        # Geração de chave de armazenamento
        if url_site:
            chave = url_site.strip().lower().replace(" ", "_")[:30]
            origem = f"Site/Serviço: {url_site.strip()}"
        elif email:
            chave = email.strip().lower().replace(" ", "_")[:30]
            origem = f"E-mail: {email.strip()}"
        elif nick:
            chave = nick.strip().lower().replace(" ", "_")[:30]
            origem = f"Nickname: {nick.strip()}"
        elif senha:
            chave = senha.strip().lower()[:10]
            origem = "Parte da sua senha"
        else:
            import uuid

            chave = "chave_" + str(uuid.uuid4())[:8]
            origem = "Chave aleatória"

        # Armazenamento no cofre
        cripto_cofre.armazenar_senha(chave, conteudo)

        aviso_label.config(
            text=f"✅ Salvo com base em: {origem}.\nUse essa informação para consultar futuramente.",
            foreground="green",
        )

        # Limpar campos
        site_entry.delete(0, "end")
        email_entry.delete(0, "end")
        nickname_entry.delete(0, "end")
        senha_entry.delete(0, "end")

    # ========== INTERFACE GRÁFICA ==========

    ttkb.Label(
        janela, text="Salvar Senha no Cofre", font=("Segoe UI", 12, "bold")
    ).pack(pady=10)

    # Campo: Site/Serviço
    site_frame = ttkb.Frame(janela)
    site_frame.pack(pady=5)
    ttkb.Label(site_frame, text="Site/Serviço:", font=("Segoe UI", 10)).pack(
        side="left"
    )

    help_icon = ttkb.Label(
        site_frame, text=" (?)", bootstyle=INFO, cursor="question_arrow"
    )
    help_icon.pack(side="left")
    help_icon.bind(
        "<Enter>", lambda e: help_icon.config(text=" Ex: Gmail, Youtube, Steam")
    )
    help_icon.bind("<Leave>", lambda e: help_icon.config(text=" (?)"))

    site_entry = ttkb.Entry(janela, width=30)
    site_entry.pack()

    email_frame = ttkb.Frame(janela)
    email_frame.pack(pady=(10, 2))

    ttkb.Label(email_frame, text="E-mail (opcional):", font=("Segoe UI", 10)).pack(
        side="left"
    )

    # Campo: e-mail
    email_help = ttkb.Label(
        email_frame, text=" (?)", bootstyle=INFO, cursor="question_arrow"
    )
    email_help.pack(side="left")

    email_help.bind(
        "<Enter>",
        lambda e: email_help.config(
            text="Domínios suportados: gmail, outlook, hotmail, protonmail, tuta, mytaemin..."
        ),
    )
    email_help.bind("<Leave>", lambda e: email_help.config(text=" (?)"))

    email_entry = ttkb.Entry(janela, width=30)
    email_entry.pack()

    # Campo: Nickname
    ttkb.Label(janela, text="Nickname (opcional):", font=("Segoe UI", 10)).pack(
        pady=(10, 2)
    )
    nickname_entry = ttkb.Entry(janela, width=30)
    nickname_entry.pack()

    # Campo: Senha
    ttkb.Label(janela, text="Senha (obrigatória):", font=("Segoe UI", 10, "bold")).pack(
        pady=(10, 2)
    )
    senha_frame = ttkb.Frame(janela)
    senha_frame.pack()

    senha_entry = ttkb.Entry(senha_frame, width=24, show="*")
    senha_entry.insert(0, password)
    senha_entry.pack(side="left", padx=(0, 5))

    olho_btn = ttkb.Button(
        senha_frame,
        text="👁",
        bootstyle=SECONDARY,
        width=3,
        command=alternar_visibilidade,
    )
    olho_btn.pack(side="left")

    # Aviso
    aviso_label = ttkb.Label(janela, text="", font=("Segoe UI", 9), foreground="red")
    aviso_label.pack(pady=(10, 5))

    # Botão de salvar
    ttkb.Button(janela, text="Salvar", bootstyle=SUCCESS, command=salvar).pack(pady=20)
