import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import pyperclip

import assets.gerador_de_senha as gerador_de_senha
from core.keepass_manager import KeePassManager
from assets.autenticacao_2fa import verificar_2fa_gui


class PasswordGeneratorTab:
    def __init__(self, notebook, status_bar):
        """Inicializa a aba do gerador de senhas"""
        self.notebook = notebook
        self.status_bar = status_bar
        self.keepass_manager = KeePassManager()

        # Variáveis
        self.senha_gerada = ttkb.StringVar()
        self.keyword_var = ttkb.StringVar()
        self.custom_password_var = ttkb.BooleanVar(value=True)
        self.uppercase_var = ttkb.BooleanVar(value=True)
        self.lowercase_var = ttkb.BooleanVar(value=True)
        self.numbers_var = ttkb.BooleanVar(value=True)
        self.symbols_var = ttkb.BooleanVar(value=True)
        self.remove_duplicates_var = ttkb.BooleanVar(value=False)
        self.password_length_var = ttkb.IntVar(value=12)
        self.mensagem_var = ttkb.StringVar()
        self.password_visible = False

    def create(self):
        """Cria a aba do gerador de senhas"""
        self.tab_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="🔑 Gerador de Senhas")

        self.main_container = ttkb.Frame(self.tab_frame)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        """Cria o painel esquerdo com configurações"""
        self.left_frame = ttkb.LabelFrame(
            self.main_container,
            text="Configurações da Senha",
            bootstyle="primary",
            padding=20,
        )
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_keyword_section()
        self.create_customization_section()
        self.create_character_options()
        self.create_length_control()
        self.create_extra_options()
        self.create_generate_button()

    def create_keyword_section(self):
        """Cria seção da palavra-chave"""
        keyword_frame = ttkb.Frame(self.left_frame)
        keyword_frame.pack(fill="x", pady=(0, 15))

        ttkb.Label(
            keyword_frame,
            text="Palavra-chave (opcional):",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        self.keyword_entry = ttkb.Entry(
            keyword_frame,
            textvariable=self.keyword_var,
            font=("Segoe UI", 11),
            width=30,
        )
        self.keyword_entry.pack(fill="x", pady=(5, 0))

    def create_customization_section(self):
        """Cria seção de personalização"""
        ttkb.Checkbutton(
            self.left_frame,
            text="Personalizar senha",
            variable=self.custom_password_var,
            bootstyle="primary-round-toggle",
        ).pack(anchor="w", pady=(0, 10))

    def create_character_options(self):
        """Cria opções de tipos de caracteres"""
        char_frame = ttkb.LabelFrame(
            self.left_frame, text="Tipos de Caracteres", padding=15
        )
        char_frame.pack(fill="x", pady=(0, 15))

        options = [
            ("Maiúsculas (A-Z)", self.uppercase_var),
            ("Minúsculas (a-z)", self.lowercase_var),
            ("Números (0-9)", self.numbers_var),
            ("Símbolos (!@#$%)", self.symbols_var),
        ]

        for text, var in options:
            ttkb.Checkbutton(
                char_frame, text=text, variable=var, bootstyle="success-round-toggle"
            ).pack(anchor="w", pady=2)

    def create_length_control(self):
        """Cria controle de tamanho da senha"""
        length_frame = ttkb.Frame(self.left_frame)
        length_frame.pack(fill="x", pady=(0, 15))

        ttkb.Label(
            length_frame, text="Tamanho da senha:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        length_control_frame = ttkb.Frame(length_frame)
        length_control_frame.pack(fill="x", pady=(5, 0))

        self.length_scale = ttkb.Scale(
            length_control_frame,
            from_=6,
            to=50,
            variable=self.password_length_var,
            bootstyle="success",
            command=self.update_length_label,
        )
        self.length_scale.pack(side="left", fill="x", expand=True)

        self.length_label = ttkb.Label(
            length_control_frame,
            text="12",
            font=("Segoe UI", 10, "bold"),
            width=5,
            bootstyle="inverse-primary",
        )
        self.length_label.pack(side="right", padx=(10, 0))

    def create_extra_options(self):
        """Cria opções extras"""
        ttkb.Checkbutton(
            self.left_frame,
            text="Remover caracteres duplicados",
            variable=self.remove_duplicates_var,
            bootstyle="warning-round-toggle",
        ).pack(anchor="w", pady=(0, 15))

    def create_generate_button(self):
        """Cria botão de gerar"""
        generate_btn = ttkb.Button(
            self.left_frame,
            text="🎲 Gerar Senha",
            command=self.generate_password,
            bootstyle="success",
            width=20,
        )
        generate_btn.pack(pady=10)

    def create_right_panel(self):
        """Cria o painel direito com resultado"""
        self.right_frame = ttkb.LabelFrame(
            self.main_container, text="Senha Gerada", bootstyle="secondary", padding=20
        )
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_password_display()
        self.create_strength_indicator()
        self.create_action_buttons()
        self.create_message_display()

    def create_password_display(self):
        """Cria display da senha"""
        password_frame = ttkb.Frame(self.right_frame)
        password_frame.pack(fill="x", pady=(0, 15))

        self.password_entry = ttkb.Entry(
            password_frame,
            textvariable=self.senha_gerada,
            font=("Consolas", 12),
            state="readonly",
            show="*",
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.toggle_btn = ttkb.Button(
            password_frame,
            text="👁️",
            width=3,
            command=self.toggle_password_visibility,
            bootstyle="outline-secondary",
        )
        self.toggle_btn.pack(side="right", padx=(5, 0))

    def create_strength_indicator(self):
        """Cria indicador de força"""
        strength_frame = ttkb.Frame(self.right_frame)
        strength_frame.pack(fill="x", pady=(0, 15))

        ttkb.Label(strength_frame, text="Força da senha:").pack(anchor="w")

        self.strength_progress = ttkb.Progressbar(
            strength_frame, bootstyle="success-striped", mode="determinate"
        )
        self.strength_progress.pack(fill="x", pady=(5, 0))

        self.strength_label = ttkb.Label(strength_frame, text="", font=("Segoe UI", 9))
        self.strength_label.pack(anchor="w")

    def create_action_buttons(self):
        """Cria botões de ação"""
        action_frame = ttkb.Frame(self.right_frame)
        action_frame.pack(fill="x")

        copy_btn = ttkb.Button(
            action_frame,
            text="📋 Copiar",
            command=self.copy_password,
            bootstyle="info",
            width=12,
        )
        copy_btn.pack(side="left", padx=(0, 5))

        save_btn = ttkb.Button(
            action_frame,
            text="💾 Salvar no Cofre",
            command=self.save_to_vault,
            bootstyle="primary",
            width=15,
        )
        save_btn.pack(side="left")

    def create_message_display(self):
        """Cria display de mensagens"""
        self.message_label = ttkb.Label(
            self.right_frame,
            textvariable=self.mensagem_var,
            font=("Segoe UI", 9),
            bootstyle="success",
        )
        self.message_label.pack(pady=(10, 0))

    def update_length_label(self, value):
        """Atualiza o label do tamanho da senha"""
        self.length_label.config(text=str(int(float(value))))

    def generate_password(self):
        """Gera uma nova senha"""
        try:
            keyword = self.keyword_var.get()
            password = gerador_de_senha.generate_password(
                keyword,
                self.custom_password_var.get(),
                self.uppercase_var.get(),
                self.lowercase_var.get(),
                self.numbers_var.get(),
                self.symbols_var.get(),
                self.remove_duplicates_var.get(),
                self.password_length_var.get(),
            )
            self.senha_gerada.set(password)

            # Calcular força da senha
            strength = self.calculate_password_strength(password)
            self.strength_progress["value"] = strength

            # Define os níveis visuais
            if strength < 30:
                self.strength_label.config(text="Fraca", bootstyle="danger")
                self.strength_progress.config(bootstyle="danger-striped")
            elif strength < 60:
                self.strength_label.config(text="Média", bootstyle="warning")
                self.strength_progress.config(bootstyle="warning-striped")
            elif strength < 85:
                self.strength_label.config(text="Forte", bootstyle="success")
                self.strength_progress.config(bootstyle="success-striped")
            else:
                self.strength_label.config(text="Excelente", bootstyle="info")
                self.strength_progress.config(bootstyle="info-striped")

            self.mensagem_var.set("Senha gerada com sucesso!")
            self.status_bar.update_status("Nova senha gerada")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar senha: {str(e)}")

    def calculate_password_strength(self, password):
        """Calcula a força da senha com nível Excelente"""
        if not password:
            return 0

        score = 0

        # Pontuação pelo comprimento
        score += min(40, len(password) * 2)

        # Diversidade de caracteres
        tipos = 0
        if any(c.islower() for c in password):
            tipos += 1
            score += 15
        if any(c.isupper() for c in password):
            tipos += 1
            score += 15
        if any(c.isdigit() for c in password):
            tipos += 1
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
            tipos += 1
            score += 20

        # Penaliza repetições excessivas
        unique_chars = len(set(password))
        if unique_chars < len(password) * 0.7:
            score -= 10

        # Novo nível: "Excelente"
        if len(password) >= 25 and tipos >= 3:
            score = 100

        return min(100, max(0, score))

    def toggle_password_visibility(self):
        """Alterna visibilidade da senha"""
        if self.password_visible:
            self.password_entry.config(show="*")
            self.toggle_btn.config(text="👁️")
            self.password_visible = False
        else:
            self.password_entry.config(show="")
            self.toggle_btn.config(text="🔒")
            self.password_visible = True

    def copy_password(self):
        """Copia senha para área de transferência"""
        password = self.senha_gerada.get()
        if password:
            pyperclip.copy(password)
            self.mensagem_var.set("Senha copiada!")
            self.status_bar.update_status("Senha copiada para área de transferência")
        else:
            messagebox.showwarning("Aviso", "Nenhuma senha para copiar!")

    def save_to_vault(self):
        """Salva senha no cofre KeePass"""
        password = self.senha_gerada.get()
        keyword = self.keyword_var.get()

        if not password:
            messagebox.showwarning("Aviso", "Gere uma senha primeira!")
            return

        if not keyword:
            messagebox.showwarning("Aviso", "Digite uma palavra-chave!")
            return

        try:
            # Verificar 2FA
            if not verificar_2fa_gui():
                messagebox.showerror(
                    "Erro de autenticação",
                    "A autenticação 2FA falhou. Operação cancelada.",
                )
                return

            # Salvar no KeePass
            success = self.keepass_manager.add_entry(
                title=keyword,
                username="FortiCore User",
                password=password,
                notes=f"Gerada pelo FortiCore Sentinel\nComprimento: {len(password)} caracteres",
            )

            if success:
                self.mensagem_var.set("Senha salva no cofre!")
                self.status_bar.update_status("Senha salva no cofre KeePass")
            else:
                messagebox.showerror("Erro", "Falha ao salvar no cofre!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar no cofre: {str(e)}")
