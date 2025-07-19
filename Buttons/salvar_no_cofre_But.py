from tkinter import messagebox
from assets.autenticacao_2fa import verificar_2fa_gui
from assets.salvar_no_cofre_window import abrir_cofre_window
from Buttons.criar_cofre_But import carregar_status


def salvar_no_cofre(keyword, senha, label_erro, mensagem_var):
    if not carregar_status():
        label_erro.config(
            text="🔐 Crie seu cofre com autenticação de 2 fatores antes de salvar senhas."
        )
        return

    if not verificar_2fa_gui():
        messagebox.showerror("Erro de autenticação", "A autenticação 2FA falhou.")
        return

    abrir_cofre_window(senha, keyword)
    mensagem_var.set("Senha salva com sucesso!")
