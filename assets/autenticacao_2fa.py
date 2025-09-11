import os
import pyotp
import qrcode
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from utils.caminhos import get_pasta_cofre

pasta_cofre = get_pasta_cofre()
ARQUIVO_CHAVE = os.path.join(pasta_cofre, "chave_2fa.txt")
ARQUIVO_CONFIG = os.path.join(pasta_cofre, "config_cofre.txt")
ARQUIVO_SENHA = os.path.join(pasta_cofre, "senha_mestre.txt")  # Para salvar senha hash
SESSAO_ATIVA = False

if not os.path.exists(pasta_cofre):
    os.makedirs(pasta_cofre)


def gerar_ou_obter_chave():
    """Gera ou obtém chave 2FA existente"""
    if os.path.exists(ARQUIVO_CHAVE):
        with open(ARQUIVO_CHAVE, "r") as f:
            return f.read()
    else:
        chave = pyotp.random_base32()
        with open(ARQUIVO_CHAVE, "w") as f:
            f.write(chave)
        return chave


def salvar_config_cofre(nome_cofre, senha_hash=None):
    """Salva configurações do cofre"""
    config_data = f"nome_cofre={nome_cofre}\nconfigurado=true"
    with open(ARQUIVO_CONFIG, "w") as f:
        f.write(config_data)

    # Salvar hash da senha se fornecido
    if senha_hash:
        with open(ARQUIVO_SENHA, "w") as f:
            f.write(senha_hash)


def obter_config_cofre():
    """Obtém configurações salvas do cofre"""
    if os.path.exists(ARQUIVO_CONFIG):
        config = {}
        with open(ARQUIVO_CONFIG, "r") as f:
            for linha in f.readlines():
                if "=" in linha:
                    chave, valor = linha.strip().split("=", 1)
                    config[chave] = valor
        return config
    return {}


def is_primeira_configuracao():
    """Verifica se é a primeira vez que o usuário está configurando"""
    config = obter_config_cofre()
    return config.get("configurado") != "true"


def hash_senha(senha):
    """Cria hash simples da senha (você pode usar bcrypt para mais segurança)"""
    import hashlib

    return hashlib.sha256(senha.encode()).hexdigest()


def verificar_senha(senha):
    """Verifica se a senha está correta"""
    if not os.path.exists(ARQUIVO_SENHA):
        return False

    with open(ARQUIVO_SENHA, "r") as f:
        senha_salva = f.read()

    return hash_senha(senha) == senha_salva


class ConfiguradorCofre:
    """Janela unificada para configuração completa do cofre"""

    def __init__(self, master, apenas_2fa=False):
        self.master = master
        self.resultado = None
        self.chave_2fa = gerar_ou_obter_chave()
        self.primeira_config = is_primeira_configuracao()
        self.apenas_2fa = apenas_2fa  # Nova flag para mostrar apenas 2FA

        # Configuração da janela
        self.janela = ttkb.Toplevel(master)
        self.janela.title("🔒 FortiCore - Autenticação")

        # CORREÇÃO: Apenas duas interfaces - removida a interface intermediária
        if self.apenas_2fa:
            self.janela.geometry("350x200")
        else:  # primeira_config
            self.janela.geometry("700x850")

        self.janela.resizable(False, False)
        self.janela.transient(master)
        self.janela.grab_set()

        # Centralizar janela
        self.janela.update_idletasks()
        x = (self.janela.winfo_screenwidth() - self.janela.winfo_width()) // 2
        y = (self.janela.winfo_screenheight() - self.janela.winfo_height()) // 2
        self.janela.geometry(f"+{x}+{y}")

        # Variáveis
        self.senha_var = tk.StringVar()
        self.confirma_senha_var = tk.StringVar()
        self.nome_cofre_var = tk.StringVar()
        self.codigo_2fa_var = tk.StringVar()

        # CORREÇÃO: Escolher interface baseada apenas em duas opções
        if self.apenas_2fa:
            self.criar_interface_apenas_2fa()
        else:
            self.criar_interface_inicial()

        # Impedir fechamento sem autenticação (apenas se não for apenas_2fa)
        if not self.apenas_2fa:
            self.janela.protocol("WM_DELETE_WINDOW", self.on_closing)
        else:
            self.janela.protocol("WM_DELETE_WINDOW", self.cancelar)

    def criar_interface_apenas_2fa(self):
        """Interface minimalista apenas para código 2FA"""
        main_frame = ttkb.Frame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Título compacto
        config = obter_config_cofre()
        nome_cofre = config.get("nome_cofre", "FortiCore")

        titulo = ttkb.Label(
            main_frame,
            text=f"🔒 {nome_cofre}",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary",
        )
        titulo.pack(pady=(0, 15))

        # Apenas código 2FA
        ttkb.Label(main_frame, text="Código 2FA:", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        codigo_entry = ttkb.Entry(
            main_frame,
            textvariable=self.codigo_2fa_var,
            font=("Consolas", 16),
            justify="center",
            width=12,
        )
        codigo_entry.pack(pady=(0, 20))

        # Validação do código
        codigo_entry.bind("<KeyRelease>", self.validar_codigo_2fa)

        # Botões compactos
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(fill="x")

        cancelar_btn = ttkb.Button(
            btn_frame,
            text="Cancelar",
            command=self.cancelar,
            bootstyle="secondary",
            width=10,
        )
        cancelar_btn.pack(side="right", padx=(10, 0))

        self.confirmar_btn = ttkb.Button(
            btn_frame,
            text="Confirmar",
            command=self.confirmar_2fa,
            bootstyle="success",
            width=12,
            state="disabled",
        )
        self.confirmar_btn.pack(side="right")

        # Focar no código
        codigo_entry.focus()

        # Monitorar campo
        self.codigo_2fa_var.trace("w", self.verificar_codigo_2fa)

        # Enter para confirmar
        self.janela.bind("<Return>", lambda e: self.confirmar_2fa())

    def criar_interface_inicial(self):
        """Interface para primeira configuração completa"""
        main_frame = ttkb.Frame(self.janela)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Título principal
        titulo = ttkb.Label(
            main_frame,
            text="🔒 Configuração Inicial do Cofre",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary",
        )
        titulo.pack(pady=(0, 20))

        # Frame para configurações
        config_frame = ttkb.LabelFrame(
            main_frame, text="Configurações Básicas", padding=15
        )
        config_frame.pack(fill="x", pady=(0, 15))

        # Nome do cofre
        ttkb.Label(
            config_frame, text="Nome do seu Cofre:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        nome_entry = ttkb.Entry(
            config_frame,
            textvariable=self.nome_cofre_var,
            font=("Segoe UI", 11),
            width=40,
        )
        nome_entry.pack(fill="x", pady=(0, 15))

        # Senha mestre
        ttkb.Label(
            config_frame,
            text="Senha Mestre (mínimo 8 caracteres):",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        senha_frame = ttkb.Frame(config_frame)
        senha_frame.pack(fill="x", pady=(0, 10))

        self.senha_entry = ttkb.Entry(
            senha_frame, textvariable=self.senha_var, font=("Segoe UI", 11), show="*"
        )
        self.senha_entry.pack(side="left", fill="x", expand=True)

        self.toggle_senha_btn = ttkb.Button(
            senha_frame,
            text="👁️",
            width=3,
            command=self.toggle_senha_visibility,
            bootstyle="outline-secondary",
        )
        self.toggle_senha_btn.pack(side="right", padx=(5, 0))

        # Confirmar senha
        ttkb.Label(
            config_frame, text="Confirmar Senha Mestre:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        confirma_frame = ttkb.Frame(config_frame)
        confirma_frame.pack(fill="x", pady=(0, 10))

        self.confirma_entry = ttkb.Entry(
            confirma_frame,
            textvariable=self.confirma_senha_var,
            font=("Segoe UI", 11),
            show="*",
        )
        self.confirma_entry.pack(side="left", fill="x", expand=True)

        self.toggle_confirma_btn = ttkb.Button(
            confirma_frame,
            text="👁️",
            width=3,
            command=self.toggle_confirma_visibility,
            bootstyle="outline-secondary",
        )
        self.toggle_confirma_btn.pack(side="right", padx=(5, 0))

        # Frame para 2FA
        tfa_frame = ttkb.LabelFrame(
            main_frame, text="Configuração 2FA (Autenticação em 2 Fatores)", padding=15
        )
        tfa_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Instruções
        instrucoes = ttkb.Label(
            tfa_frame,
            text="1. Instale o Google Authenticator no seu celular\n2. Escaneie o QR Code abaixo\n3. Digite o código de 6 dígitos gerado",
            font=("Segoe UI", 9),
            justify="left",
        )
        instrucoes.pack(anchor="w", pady=(0, 15))

        # QR Code (será gerado após preencher nome)
        self.qr_frame = ttkb.Frame(tfa_frame)
        self.qr_frame.pack(fill="x", pady=(0, 15))

        self.qr_label = ttkb.Label(
            self.qr_frame,
            text="Preencha o nome do cofre para gerar o QR Code",
            font=("Segoe UI", 10, "italic"),
            bootstyle="secondary",
        )
        self.qr_label.pack()

        # Código 2FA
        codigo_frame = ttkb.Frame(tfa_frame)
        codigo_frame.pack(fill="x")

        ttkb.Label(
            codigo_frame, text="Código 2FA (6 dígitos):", font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        codigo_entry = ttkb.Entry(
            codigo_frame,
            textvariable=self.codigo_2fa_var,
            font=("Consolas", 12),
            width=10,
            justify="center",
        )
        codigo_entry.pack(side="right")

        # Monitorar mudanças no nome para gerar QR
        self.nome_cofre_var.trace("w", self.on_nome_change)

        # Validação do código 2FA
        codigo_entry.bind("<KeyRelease>", self.validar_codigo_2fa)

        # Botões
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        cancelar_btn = ttkb.Button(
            btn_frame,
            text="Cancelar",
            command=self.cancelar,
            bootstyle="secondary",
            width=12,
        )
        cancelar_btn.pack(side="right", padx=(10, 0))

        self.configurar_btn = ttkb.Button(
            btn_frame,
            text="Configurar Cofre",
            command=self.configurar_cofre,
            bootstyle="success",
            width=15,
            state="disabled",
        )
        self.configurar_btn.pack(side="right")

        # Focar no primeiro campo
        nome_entry.focus()

        # Monitorar mudanças para habilitar botão
        for var in [
            self.senha_var,
            self.confirma_senha_var,
            self.nome_cofre_var,
            self.codigo_2fa_var,
        ]:
            var.trace("w", self.verificar_campos_completos)

    def on_nome_change(self, *args):
        """Gera QR code quando nome é preenchido"""
        nome = self.nome_cofre_var.get().strip()
        if len(nome) >= 3:
            self.gerar_qr_code(nome)

    def gerar_qr_code(self, nome):
        """Gera e exibe QR code"""
        try:
            totp = pyotp.TOTP(self.chave_2fa)
            otpauth_url = totp.provisioning_uri(
                name=nome, issuer_name="FortiCore Cofre"
            )

            # Gerar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=4,
            )
            qr.add_data(otpauth_url)
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize((200, 200), Image.Resampling.LANCZOS)

            # Converter para Tkinter
            self.qr_photo = ImageTk.PhotoImage(qr_image)

            # Limpar frame anterior
            for widget in self.qr_frame.winfo_children():
                widget.destroy()

            # Mostrar QR
            qr_display = ttkb.Label(self.qr_frame, image=self.qr_photo)
            qr_display.pack()

            info_label = ttkb.Label(
                self.qr_frame,
                text="Escaneie este código com o Google Authenticator",
                font=("Segoe UI", 9),
                bootstyle="info",
            )
            info_label.pack(pady=(10, 0))

        except Exception as e:
            print(f"Erro ao gerar QR code: {e}")

    def toggle_senha_visibility(self):
        """Alterna visibilidade da senha"""
        current = self.senha_entry.cget("show")
        if current == "":
            self.senha_entry.config(show="*")
            self.toggle_senha_btn.config(text="👁️")
        else:
            self.senha_entry.config(show="")
            self.toggle_senha_btn.config(text="🔒")

    def toggle_confirma_visibility(self):
        """Alterna visibilidade da confirmação de senha"""
        if hasattr(self, "confirma_entry"):
            current = self.confirma_entry.cget("show")
            if current == "":
                self.confirma_entry.config(show="*")
                self.toggle_confirma_btn.config(text="👁️")
            else:
                self.confirma_entry.config(show="")
                self.toggle_confirma_btn.config(text="🔒")

    def validar_codigo_2fa(self, event):
        """Valida entrada do código 2FA"""
        codigo = event.widget.get()
        # Remover caracteres não numéricos
        codigo_limpo = "".join(c for c in codigo if c.isdigit())

        if codigo != codigo_limpo:
            event.widget.delete(0, tk.END)
            event.widget.insert(0, codigo_limpo)

        # Limitar a 6 dígitos
        if len(codigo_limpo) > 6:
            event.widget.delete(6, tk.END)

    def verificar_codigo_2fa(self, *args):
        """Verifica se código 2FA está completo (apenas para interface minimalista)"""
        if hasattr(self, "confirmar_btn"):
            codigo_ok = len(self.codigo_2fa_var.get()) == 6
            if codigo_ok:
                self.confirmar_btn.config(state="normal")
            else:
                self.confirmar_btn.config(state="disabled")

    def verificar_campos_completos(self, *args):
        """Verifica se todos os campos estão preenchidos para configuração inicial"""
        nome_ok = len(self.nome_cofre_var.get().strip()) >= 3
        senha_ok = len(self.senha_var.get()) >= 8
        confirma_ok = self.senha_var.get() == self.confirma_senha_var.get() and senha_ok
        codigo_ok = len(self.codigo_2fa_var.get()) == 6

        if nome_ok and senha_ok and confirma_ok and codigo_ok:
            self.configurar_btn.config(state="normal")
        else:
            self.configurar_btn.config(state="disabled")

    def confirmar_2fa(self):
        """Confirma apenas código 2FA (para interface minimalista)"""
        codigo = self.codigo_2fa_var.get()

        if len(codigo) != 6:
            messagebox.showerror("Erro", "Código 2FA deve ter 6 dígitos!")
            return

        # Verificar código 2FA
        totp = pyotp.TOTP(self.chave_2fa)
        if not totp.verify(codigo, valid_window=1):
            messagebox.showerror("Erro", "Código 2FA inválido ou expirado!")
            return

        # Sucesso na verificação 2FA
        self.resultado = {"codigo_verificado": True, "autenticado": True}
        self.janela.destroy()

    def configurar_cofre(self):
        """Realiza configuração inicial completa"""
        nome = self.nome_cofre_var.get().strip()
        senha = self.senha_var.get()
        confirma = self.confirma_senha_var.get()
        codigo = self.codigo_2fa_var.get()

        # Validações
        if len(nome) < 3:
            messagebox.showerror(
                "Erro", "Nome do cofre deve ter pelo menos 3 caracteres!"
            )
            return

        if len(senha) < 8:
            messagebox.showerror("Erro", "Senha deve ter pelo menos 8 caracteres!")
            return

        if senha != confirma:
            messagebox.showerror("Erro", "Senhas não coincidem!")
            return

        if len(codigo) != 6:
            messagebox.showerror("Erro", "Código 2FA deve ter 6 dígitos!")
            return

        # Verificar código 2FA
        totp = pyotp.TOTP(self.chave_2fa)
        if not totp.verify(codigo, valid_window=1):
            messagebox.showerror("Erro", "Código 2FA inválido ou expirado!")
            return

        # Salvar configurações com hash da senha
        salvar_config_cofre(nome, hash_senha(senha))

        # Sucesso
        self.resultado = {"senha": senha, "nome_cofre": nome, "autenticado": True}

        messagebox.showinfo(
            "Sucesso",
            f"Cofre '{nome}' configurado com sucesso!\n\n"
            "Guarde bem sua senha mestre e mantenha o Google Authenticator configurado.",
        )

        global SESSAO_ATIVA
        SESSAO_ATIVA = True

        self.janela.destroy()

    def cancelar(self):
        """Cancela operação"""
        self.resultado = {"autenticado": False}
        self.janela.destroy()

    def on_closing(self):
        """Impede fechamento sem autenticação"""
        if messagebox.askokcancel("Sair", "Tem certeza que deseja cancelar?"):
            self.resultado = {"autenticado": False}
            self.janela.destroy()


# FUNÇÕES PRINCIPAIS CORRIGIDAS


def verificar_2fa_gui(master_window=None):
    """Função principal para verificação 2FA unificada"""
    global SESSAO_ATIVA

    if SESSAO_ATIVA:
        return True

    # Usar janela principal ou criar uma temporária
    if master_window is None:
        master_window = tk.Tk()
        master_window.withdraw()  # Ocultar janela temporária
        temp_master = True
    else:
        temp_master = False

    try:
        # CORREÇÃO: Sempre usar a configuração inicial se não estiver configurado
        configurador = ConfiguradorCofre(master_window, apenas_2fa=False)

        # Aguardar resultado
        configurador.janela.wait_window()

        resultado = configurador.resultado

        if temp_master:
            master_window.destroy()

        return resultado is not None and resultado.get("autenticado", False)

    except Exception as e:
        if temp_master:
            master_window.destroy()
        messagebox.showerror("Erro", f"Erro na autenticação: {str(e)}")
        return False


def verificar_apenas_2fa(master_window=None):
    """Função NOVA para verificar apenas código 2FA (sem senha mestre)"""
    # Não verificar se sessão já está ativa, sempre pedir 2FA quando necessário

    # Usar janela principal ou criar uma temporária
    if master_window is None:
        master_window = tk.Tk()
        master_window.withdraw()  # Ocultar janela temporária
        temp_master = True
    else:
        temp_master = False

    try:
        # Criar configurador apenas para 2FA
        configurador = ConfiguradorCofre(master_window, apenas_2fa=True)

        # Aguardar resultado
        configurador.janela.wait_window()

        resultado = configurador.resultado

        if temp_master:
            master_window.destroy()

        return resultado is not None and resultado.get("codigo_verificado", False)

    except Exception as e:
        if temp_master:
            master_window.destroy()
        messagebox.showerror("Erro", f"Erro na verificação 2FA: {str(e)}")
        return False


def obter_senha_mestre(master_window=None):
    """NOVA: Obtém senha mestre configurada (para uso no KeePassManager)"""
    # CORREÇÃO: Se já está configurado, usar interface apenas_2fa, se não, usar inicial
    if is_primeira_configuracao():
        # Primeira configuração - usar interface completa
        if master_window is None:
            master_window = tk.Tk()
            master_window.withdraw()
            temp_master = True
        else:
            temp_master = False

        try:
            configurador = ConfiguradorCofre(master_window, apenas_2fa=False)
            configurador.janela.wait_window()

            resultado = configurador.resultado

            if temp_master:
                master_window.destroy()

            if resultado and resultado.get("autenticado"):
                return resultado.get("senha")

            return None

        except Exception as e:
            if temp_master:
                master_window.destroy()
            return None
    else:
        # Já configurado - pedir apenas 2FA e retornar senha salva
        if verificar_apenas_2fa(master_window):
            # Usuário passou no 2FA, agora precisamos da senha salva
            # Vamos pedir a senha via dialog simples
            from tkinter import simpledialog

            senha = simpledialog.askstring(
                "Senha Mestre", "Digite sua senha mestre:", show="*"
            )

            if senha and verificar_senha(senha):
                return senha
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
                return None
        else:
            return None


def resetar_configuracao():
    """Reseta configuração para primeira vez (função de utilidade)"""
    arquivos_config = [ARQUIVO_CONFIG, ARQUIVO_CHAVE, ARQUIVO_SENHA]

    for arquivo in arquivos_config:
        if os.path.exists(arquivo):
            os.remove(arquivo)

    global SESSAO_ATIVA
    SESSAO_ATIVA = False

    messagebox.showinfo(
        "Reset", "Configuração resetada. Configure novamente na próxima execução."
    )


def encerrar_sessao():
    """Encerra a sessão ativa (útil para logout)"""
    global SESSAO_ATIVA
    SESSAO_ATIVA = False


# Função de compatibilidade (mantém interface antiga)
def solicitar_codigo_gui():
    """Função mantida para compatibilidade, mas redireciona para nova interface"""
    return verificar_2fa_gui()
