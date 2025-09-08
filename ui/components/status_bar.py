"""
FortiCore Sentinel - Componente Status Bar
"""

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *


class StatusBarComponent:
    def __init__(self, parent):
        """Inicializa a barra de status"""
        self.parent = parent

    def create(self):
        """Cria a barra de status"""
        self.status_bar = ttkb.Frame(self.parent, bootstyle="dark")
        self.status_bar.pack(side="bottom", fill="x")

        # Status principal
        self.status_label = ttkb.Label(
            self.status_bar,
            text="Pronto - FortiCore Sentinel carregado",
            font=("Segoe UI", 9),
            bootstyle="light",
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        # Contador de entradas
        self.entries_count_label = ttkb.Label(
            self.status_bar, text="", font=("Segoe UI", 9), bootstyle="info"
        )
        self.entries_count_label.pack(side="right", padx=10, pady=5)

    def update_status(self, message):
        """Atualiza o status principal"""
        self.status_label.config(text=message)

    def update_entries_count(self, count_text):
        """Atualiza o contador de entradas"""
        self.entries_count_label.config(text=count_text)
