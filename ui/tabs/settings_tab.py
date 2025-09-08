"""
FortiCore Sentinel - Aba de Configurações do Software
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os

from utils.caminhos import get_pasta_cofre


class SettingsTab:
    def __init__(self, notebook, status_bar, main_window_ref=None):
        """Inicializa a aba de configurações do software"""
        self.notebook = notebook
        self.status_bar = status_bar
        self.main_window_ref = (
            main_window_ref  # NOVO: Referência para a janela principal
        )

        # Temas disponíveis
        self.available_themes = [
            "darkly",
            "solar",
            "superhero",
            "cyborg",
            "vapor",
            "flatly",
            "journal",
            "litera",
            "lumen",
            "minty",
            "pulse",
            "sandstone",
            "united",
            "yeti",
            "morph",
            "quartz",
            "zephyr",
        ]
        self.current_theme = self.load_theme_config()

    def create(self):
        """Cria a aba de configurações do software"""
        self.tab_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="⚙️ Configurações")

        self.main_container = ttkb.Frame(self.tab_frame)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_theme_selector()

    def create_theme_selector(self):
        """Cria seção de seletor de tema"""
        theme_frame = ttkb.LabelFrame(
            self.main_container,
            text="🎨 Configurações de Aparência",
            bootstyle="warning",
            padding=20,
        )
        theme_frame.pack(fill="x", pady=(0, 15))

        # Descrição
        desc_label = ttkb.Label(
            theme_frame,
            text="Escolha o tema visual do FortiCore Sentinel:",
            font=("Segoe UI", 10),
        )
        desc_label.pack(anchor="w", pady=(0, 15))

        # Frame para seletor
        selector_frame = ttkb.Frame(theme_frame)
        selector_frame.pack(fill="x")

        # Label do seletor
        theme_label = ttkb.Label(
            selector_frame, text="🎯 Tema Atual:", font=("Segoe UI", 10, "bold")
        )
        theme_label.pack(side="left", padx=(0, 10))

        # Combobox para seleção de tema
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_combo = ttkb.Combobox(
            selector_frame,
            textvariable=self.theme_var,
            values=self.available_themes,
            state="readonly",
            width=20,
            bootstyle="primary",
        )
        self.theme_combo.pack(side="left", padx=(0, 15))

        # NOVO: Bind para aplicar tema automaticamente quando selecionado
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selected)

        # Botão para aplicar tema (mantido para compatibilidade)
        apply_theme_btn = ttkb.Button(
            selector_frame,
            text="✨ Aplicar Tema",
            command=self.apply_theme_manual,
            bootstyle="warning",
            width=15,
        )
        apply_theme_btn.pack(side="left", padx=(0, 10))

        # Botão para resetar tema
        reset_theme_btn = ttkb.Button(
            selector_frame,
            text="🔄 Resetar",
            command=self.reset_theme,
            bootstyle="secondary-outline",
            width=10,
        )
        reset_theme_btn.pack(side="left")

        # Preview dos temas
        preview_frame = ttkb.Frame(theme_frame)
        preview_frame.pack(fill="x", pady=(15, 0))

        preview_label = ttkb.Label(
            preview_frame,
            text="💡 Temas populares: darkly (escuro), flatly (claro), superhero (azul), solar (laranja)\n🚀 O tema é aplicado automaticamente ao selecionar!",
            font=("Segoe UI", 9),
            bootstyle="secondary",
        )
        preview_label.pack()

    def on_theme_selected(self, event=None):
        """NOVO: Aplicar tema automaticamente quando selecionado"""
        try:
            selected_theme = self.theme_var.get()

            if selected_theme == self.current_theme:
                return

            # Aplicar tema imediatamente
            self.apply_theme_realtime(selected_theme)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar tema: {e}")

    def apply_theme_realtime(self, theme_name):
        """NOVO: Aplica tema em tempo real sem reiniciar"""
        try:
            if not self.main_window_ref:
                # Fallback: salvar para próxima inicialização
                self.save_theme_config(theme_name)
                self.status_bar.update_status(
                    f"Tema '{theme_name}' será aplicado na próxima inicialização"
                )
                return

            # Salvar configuração primeiro
            self.save_theme_config(theme_name)

            # Aplicar tema na janela atual
            self.main_window_ref.window.style.theme_use(theme_name)

            # Atualizar tema atual
            self.current_theme = theme_name

            # Atualizar status
            self.status_bar.update_status(f"Tema alterado para: {theme_name}")

            # Mostrar notificação discreta
            self.show_theme_notification(theme_name)

        except Exception as e:
            # Em caso de erro, reverter seleção
            self.theme_var.set(self.current_theme)
            messagebox.showerror("Erro", f"Erro ao aplicar tema '{theme_name}': {e}")

    def show_theme_notification(self, theme_name):
        """NOVO: Mostra notificação discreta de mudança de tema"""
        try:
            # Criar janela de notificação temporária
            notification = ttkb.Toplevel(self.main_window_ref.window)
            notification.title("Tema Aplicado")
            notification.geometry("300x80")
            notification.resizable(False, False)

            # Posicionar no canto superior direito
            notification.geometry(
                "+{}+{}".format(
                    self.main_window_ref.window.winfo_x()
                    + self.main_window_ref.window.winfo_width()
                    - 320,
                    self.main_window_ref.window.winfo_y() + 50,
                )
            )

            # Tornar sempre no topo
            notification.attributes("-topmost", True)

            # Conteúdo da notificação
            msg_frame = ttkb.Frame(notification, padding=10)
            msg_frame.pack(fill="both", expand=True)

            icon_label = ttkb.Label(msg_frame, text="✨", font=("Segoe UI", 16))
            icon_label.pack(side="left", padx=(0, 10))

            text_label = ttkb.Label(
                msg_frame,
                text=f"Tema '{theme_name}' aplicado!",
                font=("Segoe UI", 10, "bold"),
            )
            text_label.pack(side="left")

            # Fechar automaticamente após 2 segundos
            notification.after(2000, notification.destroy)

        except Exception as e:
            print(f"Erro na notificação: {e}")

    def apply_theme_manual(self):
        """Aplicar tema manualmente (botão)"""
        selected_theme = self.theme_var.get()

        if selected_theme == self.current_theme:
            messagebox.showinfo("Tema", "Este tema já está ativo!")
            return

        self.apply_theme_realtime(selected_theme)

    def apply_theme(self):
        """MÉTODO LEGADO: Mantido para compatibilidade"""
        self.apply_theme_manual()

    def reset_theme(self):
        """Reseta para o tema padrão"""
        try:
            if messagebox.askyesno(
                "Resetar Tema", "Resetar para o tema padrão (darkly)?"
            ):
                self.theme_var.set("darkly")
                self.apply_theme_realtime("darkly")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao resetar tema: {e}")

    def save_theme_config(self, theme_name):
        """Salva configuração do tema"""
        try:
            config_path = os.path.join(get_pasta_cofre(), "theme_config.txt")
            with open(config_path, "w") as f:
                f.write(theme_name)
            self.current_theme = theme_name
        except Exception as e:
            print(f"Erro ao salvar configuração do tema: {e}")

    def load_theme_config(self):
        """Carrega configuração do tema"""
        try:
            config_path = os.path.join(get_pasta_cofre(), "theme_config.txt")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    theme = f.read().strip()
                    if theme in self.available_themes:
                        return theme
        except Exception as e:
            print(f"Erro ao carregar configuração do tema: {e}")
        return "darkly"

    def save_general_config(self):
        """Salva configurações gerais"""
        try:
            config = {
                "auto_backup": self.auto_backup_var.get(),
                "minimize_to_tray": self.minimize_to_tray_var.get(),
                "auto_lock": self.auto_lock_var.get(),
                "cache_enabled": self.cache_enabled_var.get(),
                "debug_mode": self.debug_mode_var.get(),
            }

            config_path = os.path.join(get_pasta_cofre(), "app_config.txt")
            config_str = "\n".join([f"{k}={v}" for k, v in config.items()])

            with open(config_path, "w") as f:
                f.write(config_str)

            messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")
            self.status_bar.update_status("Configurações salvas")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")

    def reset_general_config(self):
        """Reseta configurações gerais para padrão"""
        if messagebox.askyesno(
            "Reset", "Resetar todas as configurações para o padrão?"
        ):
            self.auto_backup_var.set(True)
            self.minimize_to_tray_var.set(False)
            self.auto_lock_var.set(True)
            self.cache_enabled_var.set(True)
            self.debug_mode_var.set(False)

            messagebox.showinfo("Reset", "Configurações resetadas para o padrão!")
            self.status_bar.update_status("Configurações resetadas")

    def clear_cache(self):
        """Limpa o cache da aplicação"""
        try:
            cache_path = os.path.join(get_pasta_cofre(), "cache")
            if os.path.exists(cache_path):
                import shutil

                shutil.rmtree(cache_path)

            messagebox.showinfo("Cache", "Cache limpo com sucesso!")
            self.status_bar.update_status("Cache limpo")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar cache: {e}")

    def reset_all_settings(self):
        """Reset completo de todas as configurações"""
        if messagebox.askyesno(
            "ATENÇÃO",
            "RESET COMPLETO!\n\n"
            "Isso irá resetar TODAS as configurações do software.\n"
            "Tem certeza que deseja continuar?",
        ):
            try:
                # Reset tema
                self.theme_var.set("darkly")
                self.apply_theme_realtime("darkly")

                # Reset configurações gerais
                self.reset_general_config()

                # Limpar cache
                self.clear_cache()

                messagebox.showinfo(
                    "Reset Completo",
                    "Todas as configurações foram resetadas!",
                )
                self.status_bar.update_status("Reset completo realizado")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro no reset completo: {e}")
