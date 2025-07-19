from tkinter import messagebox, simpledialog
from assets.autenticacao_2fa import verificar_2fa_gui
from assets.resultado_consulta import exibir_resultado
import assets.cripto_cofre as cripto_cofre
from Buttons.criar_cofre_But import carregar_status


def consultar_senhas(label_erro):
    if not carregar_status():
        label_erro.config(
            text="🔐 Crie seu cofre com autenticação de 2 fatores antes de consultar senhas."
        )
        return

    if not verificar_2fa_gui():
        messagebox.showerror("Erro de autenticação", "A autenticação 2FA falhou.")
        return

    keyword = simpledialog.askstring("Buscar no Cofre", "Digite a palavra-chave:")
    if keyword:
        resultados = cripto_cofre.consultar_por_palavra_chave(keyword)
        if resultados:
            exibir_resultado(keyword, resultados)
        else:
            messagebox.showinfo("Nada encontrado", "Nenhuma senha encontrada.")
