import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import ttk
from Buttons.criar_cofre_But import criar_cofre, carregar_status
from Buttons.backup_trancar_But import backup_e_trancar_cofre
from Buttons.salvar_no_cofre_But import salvar_no_cofre
from Buttons.consultar_cofre_But import consultar_senhas
from Buttons.destrancar_cofre_But import abrir_janela_destrancar


def adicionar_botoes_cofre(janela, senha_var, keyword_entry, mensagem_var):
    mensagem_erro = ttkb.Label(
        janela, text="", foreground="red", font=("Segoe UI", 9, "italic")
    )
    mensagem_erro.pack(pady=(5, 0))

    def criar_callback():
        criar_cofre(botao_criar_cofre, mensagem_erro)

    def salvar_callback():
        salvar_no_cofre(
            keyword_entry.get(), senha_var.get(), mensagem_erro, mensagem_var
        )

    def consultar_callback():
        consultar_senhas(mensagem_erro)

    botao_criar_cofre = ttkb.Button(
        janela, text="🔐 Criar Cofre", bootstyle="warning", command=criar_callback
    )
    botao_criar_cofre.pack(pady=(10, 5))
    if carregar_status():
        botao_criar_cofre.config(state="disabled")

    ttkb.Button(
        janela,
        text="🔒 Backup e Trancar Cofre",
        bootstyle="primary",
        command=backup_e_trancar_cofre,
    ).pack(pady=5)
    ttkb.Button(
        janela,
        text="🔓 Destrancar Cofre",
        bootstyle="secondary",
        command=abrir_janela_destrancar,
    ).pack(pady=5)
    ttkb.Button(
        janela, text="💾 Salvar no Cofre", bootstyle="success", command=salvar_callback
    ).pack(pady=5)
    ttkb.Button(
        janela, text="🔎 Consultar Cofre", bootstyle="info", command=consultar_callback
    ).pack(pady=5)
