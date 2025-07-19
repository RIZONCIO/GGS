import json
import os
import sys
from tkinter import messagebox
from assets.autenticacao_2fa import verificar_2fa_gui
from utils.caminhos import get_pasta_cofre

pasta_cofre = get_pasta_cofre()

STATUS_PATH = os.path.join(pasta_cofre, "cofre_status.json")

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)


def carregar_status():
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r") as file:
            return json.load(file).get("cofre_criado", False)
    return False


def salvar_status(status):
    with open(STATUS_PATH, "w") as file:
        json.dump({"cofre_criado": status}, file)


def criar_cofre(botao_criar, label_erro):
    if verificar_2fa_gui():
        salvar_status(True)
        botao_criar.config(state="disabled")
        label_erro.config(text="")
        messagebox.showinfo(
            "Cofre criado", "Seu cofre foi ativado com autenticação 2FA!"
        )
