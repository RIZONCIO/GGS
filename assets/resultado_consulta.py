import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import StringVar
import pyperclip
from tkinter import messagebox


def exibir_resultado(keyword, resultados):
    window = ttkb.Toplevel()
    window.title("Senhas Encontradas")
    window.geometry("500x500")
    window.resizable(False, False)

    ttkb.Label(
        window,
        text=f'Senhas com a palavra-chave: "{keyword}"',
        font=("Segoe UI", 12, "bold"),
    ).pack(pady=10)

    container = ttkb.Frame(window)
    container.pack(fill="both", expand=True, padx=10)

    canvas = ttkb.Canvas(container, highlightthickness=0)
    scrollbar = ttkb.Scrollbar(container, orient="vertical", command=canvas.yview)

    scrollable_frame = ttkb.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for item in resultados:
        site = email = senha = nick = ""
        linhas = item.strip().splitlines()

        for linha in linhas:
            linha = linha.strip()
            if linha.lower().startswith("site:"):
                site = linha.split(":", 1)[-1].strip()
            elif linha.lower().startswith("email:"):
                email = linha.strip()
            elif linha.lower().startswith("senha:"):
                senha = linha.split(":", 1)[-1].strip()
            elif linha.lower().startswith("nick:"):
                nick = linha.strip()

        card = ttkb.Frame(
            scrollable_frame,
            padding=10,
            relief="ridge",
            borderwidth=2,
            bootstyle="light",
        )
        card.pack(pady=5, fill="x", padx=5)

        ttkb.Label(
            card,
            text=f" Site: {site if site else 'Não informado'}",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=2)
        if email:
            ttkb.Label(card, text=email, font=("Segoe UI", 10)).pack(anchor="w")
        if nick:
            ttkb.Label(card, text=nick, font=("Segoe UI", 10, "italic")).pack(
                anchor="w"
            )

        senha_var = StringVar(value="*" * len(senha))
        frame_senha = ttkb.Frame(card)
        frame_senha.pack(anchor="w", pady=3)

        entry_senha = ttkb.Entry(
            frame_senha,
            textvariable=senha_var,
            font=("Consolas", 10),
            width=25,
            show="",
        )
        entry_senha.pack(side="left")

        def toggle_senha(var=senha_var, entrada=entry_senha):
            atual = var.get()
            if "*" in atual:
                var.set(senha)
                entrada.config(show="")
            else:
                var.set("*" * len(senha))
                entrada.config(show="*")

        ttkb.Button(frame_senha, text="👁", width=3, command=toggle_senha).pack(
            side="left", padx=5
        )

        def copiar():
            pyperclip.copy(senha)
            messagebox.showinfo(
                "Copiado", "Senha copiada para a área de transferência!"
            )

        ttkb.Button(
            frame_senha, text="📋", width=3, bootstyle=SUCCESS, command=copiar
        ).pack(side="left")

    ttkb.Button(window, text="Fechar", bootstyle=DANGER, command=window.destroy).pack(
        pady=10
    )
