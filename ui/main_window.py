import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os

from ui.tabs.password_generator_tab import PasswordGeneratorTab
from ui.tabs.vault_tab import VaultTab
from ui.tabs.security_tab import SecurityTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.about_tab import AboutTab
from ui.components.header import HeaderComponent
from ui.components.status_bar import StatusBarComponent


class MainWindow:
    def __init__(self):
        from utils.caminhos import get_pasta_cofre
        import os

        config_path = os.path.join(get_pasta_cofre(), "theme_config.txt")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                theme = f.read().strip()
        else:
            theme = "darkly"

        self.window = ttkb.Window(themename=theme)
        self.setup_window()
        self.create_components()

    def setup_window(self):
        """Configura a janela principal"""
        self.window.title("FortiCore Sentinel")
        self.window.geometry("1200x700")
        self.window.minsize(1000, 600)

        try:
            self.window.iconbitmap("img/logo.ico")
        except:
            pass

    def create_components(self):
        """Cria os componentes da interface"""
        self.header = HeaderComponent(self.window)
        self.header.create()

        self.notebook_frame = ttkb.Frame(self.window)
        self.notebook_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.notebook = ttkb.Notebook(self.notebook_frame, bootstyle="dark")
        self.notebook.pack(fill="both", expand=True)

        self.status_bar = StatusBarComponent(self.window)
        self.status_bar.create()

        self.create_tabs()

    def create_tabs(self):
        """Cria todas as abas da aplicação"""
        # Aba Gerador de Senhas
        self.password_tab = PasswordGeneratorTab(self.notebook, self.status_bar)
        self.password_tab.create()

        # Aba Cofre KeePass
        self.vault_tab = VaultTab(self.notebook, self.status_bar)
        self.vault_tab.create()

        # Aba Segurança (com referência ao vault_tab para integração)
        self.security_tab = SecurityTab(
            self.notebook, self.status_bar, vault_tab_ref=self.vault_tab
        )
        self.security_tab.create()

        # MODIFICADO: Aba Configurações do Software com referência à janela principal
        self.settings_tab = SettingsTab(
            self.notebook, self.status_bar, main_window_ref=self
        )
        self.settings_tab.create()

        # Aba Sobre
        self.about_tab = AboutTab(self.notebook)
        self.about_tab.create()

    def run(self):
        self.window.mainloop()
