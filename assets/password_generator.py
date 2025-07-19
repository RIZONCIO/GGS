import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
import gerador_de_senha
import assets.cripto_cofre as cripto_cofre
from assets.salvar_no_cofre_window import abrir_cofre_window
from assets.autenticacao_2fa import verificar_2fa_gui
from assets.resultado_consulta import exibir_resultado
from assets.cofre_interface import adicionar_botoes_cofre
import pyperclip


def setup_ui(window):
    window.title("Gerador de Senhas")
    window.geometry("500x600")
    window.resizable(False, False)
    window.style = ttkb.Style("cosmo")

    # ========== VARIÁVEIS ==========
    custom_password_var = ttkb.BooleanVar(value=True)
    uppercase_var_chk = ttkb.BooleanVar(value=True)
    lowercase_var_chk = ttkb.BooleanVar(value=True)
    numbers_var_chk = ttkb.BooleanVar(value=True)
    symbols_var_chk = ttkb.BooleanVar(value=True)
    remove_duplicates_var = ttkb.BooleanVar(value=False)
    password_length_var = ttkb.IntVar(value=12)
    senha_var = ttkb.StringVar()
    mensagem_var = ttkb.StringVar(value="")  # Mensagem embaixo da senha

    # ========== FUNÇÕES ==========
    def generate_password():
        keyword = keyword_entry.get()
        password = gerador_de_senha.generate_password(
            keyword,
            custom_password_var.get(),
            uppercase_var_chk.get(),
            lowercase_var_chk.get(),
            numbers_var_chk.get(),
            symbols_var_chk.get(),
            remove_duplicates_var.get(),
            password_length_var.get(),
        )
        senha_var.set(password)
        mensagem_var.set("")  # Limpa mensagem anterior

    def salvar_no_cofre():
        keyword = keyword_entry.get()
        senha = senha_var.get()
        if not verificar_2fa_gui():
            messagebox.showerror(
                "Erro de autenticação", "A autenticação 2FA falhou. Operação cancelada."
            )
            return
        abrir_cofre_window(senha, keyword)

    def consultar_senhas():
        if not verificar_2fa_gui():
            messagebox.showerror(
                "Erro de autenticação", "A autenticação 2FA falhou. Operação cancelada."
            )
            return

        keyword = simpledialog.askstring(
            "Buscar no Armazém", "Digite a palavra-chave para consultar:"
        )
        if not keyword:
            return
        resultados = cripto_cofre.consultar_por_palavra_chave(keyword)
        if resultados:
            exibir_resultado(keyword, resultados)
        else:
            messagebox.showinfo(
                "Nada encontrado", "Nenhuma senha encontrada com essa palavra-chave."
            )

    def alternar_visibilidade():
        atual = password_entry.cget("show")
        if atual == "":
            password_entry.config(show="*")
            olho_btn.config(text="👁")
        else:
            password_entry.config(show="")
            olho_btn.config(text="🔒")

    def copiar_senha():
        senha = senha_var.get()
        if senha:
            pyperclip.copy(senha)
            mensagem_var.set("Senha copiada para a área de transferência!")

    def atualizar_valor(valor):
        length_label_value.config(text=str(int(float(valor))))

    # ========== INTERFACE ==========
    ttkb.Label(window, text="Palavra-chave:", font=("Segoe UI", 10, "bold")).pack(
        pady=(10, 2)
    )
    keyword_entry = ttkb.Entry(window, font=("Segoe UI", 10))
    keyword_entry.pack(pady=(0, 10))

    ttkb.Checkbutton(
        window, text="Personalizar senha", variable=custom_password_var
    ).pack(pady=(0, 10))

    opcoes_frame = ttkb.Frame(window)
    opcoes_frame.pack(pady=5)

    ttkb.Checkbutton(opcoes_frame, text="Maiúsculas", variable=uppercase_var_chk).grid(
        row=0, column=0, padx=10, pady=2
    )
    ttkb.Checkbutton(opcoes_frame, text="Minúsculas", variable=lowercase_var_chk).grid(
        row=0, column=1, padx=10, pady=2
    )
    ttkb.Checkbutton(opcoes_frame, text="Números", variable=numbers_var_chk).grid(
        row=1, column=0, padx=10, pady=2
    )
    ttkb.Checkbutton(opcoes_frame, text="Símbolos", variable=symbols_var_chk).grid(
        row=1, column=1, padx=10, pady=2
    )

    ttkb.Label(window, text="Tamanho da senha:", font=("Segoe UI", 10)).pack()

    scale_frame = ttkb.Frame(window)
    scale_frame.pack(pady=5)

    length_label_value = ttkb.Label(
        scale_frame, text=str(password_length_var.get()), font=("Segoe UI", 10, "bold")
    )
    length_label_value.pack(side="left", padx=10)

    ttkb.Scale(
        scale_frame,
        from_=8,
        to=30,
        orient="horizontal",
        length=200,
        command=atualizar_valor,
        variable=password_length_var,
    ).pack(side="left")

    ttkb.Checkbutton(
        window, text="Remover caracteres duplicados", variable=remove_duplicates_var
    ).pack(pady=10)

    ttkb.Button(
        window, text="Gerar Senha", bootstyle=PRIMARY, command=generate_password
    ).pack(pady=10)

    # === Campo de senha com botões ===
    senha_frame = ttkb.Frame(window)
    senha_frame.pack(pady=5)

    password_entry = ttkb.Entry(
        senha_frame, textvariable=senha_var, font=("Consolas", 11), width=30, show="*"
    )
    password_entry.pack(side="left", padx=(0, 5))

    olho_btn = ttkb.Button(
        senha_frame,
        text="👁",
        width=3,
        bootstyle=SECONDARY,
        command=alternar_visibilidade,
    )
    olho_btn.pack(side="left")

    copiar_btn = ttkb.Button(
        senha_frame,
        text="📋",
        width=3,
        bootstyle=SUCCESS,
        command=copiar_senha,
    )
    copiar_btn.pack(side="left")

    # Mensagem discreta (aparece após copiar)
    msg_label = ttkb.Label(
        window, textvariable=mensagem_var, font=("Segoe UI", 9), foreground="#555"
    )
    msg_label.pack(pady=(5, 0))

    # ======== Ações finais ========
    ttkb.Separator(window).pack(fill="x", pady=10)

    adicionar_botoes_cofre(window, senha_var, keyword_entry, mensagem_var)
