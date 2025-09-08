"""
FortiCore Sentinel - Componente Header
"""

import ttkbootstrap as ttkb
from ttkbootstrap.constants import *


class HeaderComponent:
    def __init__(self, parent):
        """Inicializa o componente header"""
        self.parent = parent

    def create(self):
        """Cria o cabeçalho da aplicação"""
        self.header_frame = ttkb.Frame(self.parent, bootstyle="dark")
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Logo e título
        self.create_title_section()

        # Indicadores de status
        self.create_status_indicators()

    def create_title_section(self):
        """Cria a seção do título"""
        title_frame = ttkb.Frame(self.header_frame, bootstyle="dark")
        title_frame.pack(side="left", fill="x", expand=True)

        # Título principal
        app_title = ttkb.Label(
            title_frame,
            text="🛡️ FortiCore Sentinel",
            font=("Segoe UI", 20, "bold"),
            bootstyle="light",
        )
        app_title.pack(side="left", pady=10)

        # Subtítulo
        subtitle = ttkb.Label(
            title_frame,
            text="Gerador de Senhas Seguras & Cofre KeePass com 2FA",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        )
        subtitle.pack(side="left", padx=(20, 0), pady=10)

    def create_status_indicators(self):
        """Cria indicadores de status de segurança"""
        security_frame = ttkb.Frame(self.header_frame, bootstyle="dark")
        security_frame.pack(side="right")

        # Indicador 2FA
        security_label = ttkb.Label(
            security_frame,
            text="🔒 2FA Ativo",
            font=("Segoe UI", 10, "bold"),
            bootstyle="success",
        )
        security_label.pack(side="right", padx=(0, 10), pady=10)

        # Indicador KeePass
        keepass_label = ttkb.Label(
            security_frame,
            text="🗄️ KeePass",
            font=("Segoe UI", 10, "bold"),
            bootstyle="info",
        )
        keepass_label.pack(side="right", padx=(0, 10), pady=10)

        # Indicador HMAC
        hmac_label = ttkb.Label(
            security_frame,
            text="✅ HMAC",
            font=("Segoe UI", 10, "bold"),
            bootstyle="warning",
        )
        hmac_label.pack(side="right", padx=(0, 10), pady=10)
