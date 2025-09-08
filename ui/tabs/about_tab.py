"""
FortiCore Sentinel - Aba Sobre
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import webbrowser


class AboutTab:
    def __init__(self, notebook):
        """Inicializa a aba sobre"""
        self.notebook = notebook

    def create(self):
        """Cria a aba sobre"""
        self.tab_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="ℹ️ Sobre")

        # Container centralizado
        center_frame = ttkb.Frame(self.tab_frame)
        center_frame.pack(expand=True, fill="both")

        content_frame = ttkb.Frame(center_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.create_header(content_frame)
        self.create_features_info(content_frame)
        self.create_technical_info(content_frame)
        self.create_action_buttons(content_frame)

    def create_header(self, parent):
        """Cria cabeçalho da aba"""
        # Logo e título
        title_label = ttkb.Label(
            parent,
            text="🛡️ FortiCore Sentinel",
            font=("Segoe UI", 26, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 5))

        version_label = ttkb.Label(
            parent,
            text="Versão 2.0.0 - KeePass Edition",
            font=("Segoe UI", 12),
            bootstyle="secondary",
        )
        version_label.pack(pady=(0, 5))

        description_label = ttkb.Label(
            parent,
            text="Gerador de Senhas Seguras & Cofre KeePass com 2FA",
            font=("Segoe UI", 11, "italic"),
            bootstyle="info",
        )
        description_label.pack(pady=(0, 25))

    def create_features_info(self, parent):
        """Cria informações de recursos"""
        features_frame = ttkb.LabelFrame(
            parent, text="🚀 Recursos Principais", padding=20
        )
        features_frame.pack(pady=(0, 20))

        features_text = """🔐 Recursos de Segurança Avançados:
• Banco KeePass (.kdbx) - Padrão da indústria
• Criptografia AES-256 com Argon2 KDF
• Verificação de integridade HMAC-SHA256
• Autenticação de dois fatores (2FA) obrigatória
• Geração criptográfica segura de senhas

💡 Interface e Usabilidade:
• Interface moderna por abas
• Indicador de força de senha em tempo real
• Busca avançada e filtros
• Backup automático com verificação
• Compatibilidade com KeePass/KeePassXC

🔄 Migração e Compatibilidade:
• Importação do sistema anterior
• Exportação para CSV (sem senhas)
• Abertura em clientes KeePass externos"""

        features_label = ttkb.Label(
            features_frame, text=features_text, font=("Segoe UI", 10), justify="left"
        )
        features_label.pack()

    def create_technical_info(self, parent):
        """Cria informações técnicas"""
        tech_frame = ttkb.LabelFrame(parent, text="⚙️ Informações Técnicas", padding=20)
        tech_frame.pack(pady=(0, 20))

        tech_text = """🛠️ Tecnologias Utilizadas:
• Python 3.8+ com ttkbootstrap
• PyKeePass para manipulação de bancos .kdbx
• Cryptography para operações criptográficas
• PyOTP para autenticação 2FA (TOTP)
• HMAC-SHA256 para verificação de integridade

🔒 Padrões de Segurança:
• AES-256-CBC (Advanced Encryption Standard)
• Argon2 Key Derivation Function
• TOTP (Time-based One-Time Password)
• HMAC (Hash-based Message Authentication Code)
• Formato KeePass KDBX v4

🌐 Compatibilidade:
• Windows 10/11, Linux, macOS
• KeePass 2.x, KeePassXC
• Apps móveis compatíveis com .kdbx"""

        tech_label = ttkb.Label(
            tech_frame, text=tech_text, font=("Consolas", 9), justify="left"
        )
        tech_label.pack()

    def create_action_buttons(self, parent):
        """Cria botões de ação"""
        buttons_frame = ttkb.Frame(parent)
        buttons_frame.pack()

        # Primeira linha de botões
        row1_frame = ttkb.Frame(buttons_frame)
        row1_frame.pack(pady=(0, 10))

        github_btn = ttkb.Button(
            row1_frame,
            text="🐙 GitHub",
            command=self.open_github,
            bootstyle="primary-outline",
            width=15,
        )
        github_btn.pack(side="left", padx=(0, 10))

        docs_btn = ttkb.Button(
            row1_frame,
            text="📖 Documentação",
            command=self.open_documentation,
            bootstyle="info-outline",
            width=18,
        )
        docs_btn.pack(side="left", padx=(0, 10))

        keepass_btn = ttkb.Button(
            row1_frame,
            text="🔧 Site KeePass",
            command=self.open_keepass_site,
            bootstyle="success-outline",
            width=15,
        )
        keepass_btn.pack(side="left")

        # Segunda linha de botões
        row2_frame = ttkb.Frame(buttons_frame)
        row2_frame.pack()

        changelog_btn = ttkb.Button(
            row2_frame,
            text="📋 Changelog",
            command=self.show_changelog,
            bootstyle="secondary-outline",
            width=15,
        )
        changelog_btn.pack(side="left", padx=(0, 10))

        license_btn = ttkb.Button(
            row2_frame,
            text="📄 Licença",
            command=self.show_license,
            bootstyle="warning-outline",
            width=12,
        )
        license_btn.pack(side="left", padx=(0, 10))

        support_btn = ttkb.Button(
            row2_frame,
            text="💬 Suporte",
            command=self.show_support,
            bootstyle="danger-outline",
            width=12,
        )
        support_btn.pack(side="left")

    def open_github(self):
        """Abre página do GitHub"""
        try:
            # Substitua pela URL real do seu repositório
            webbrowser.open("https://github.com/seu-usuario/forticore-sentinel")
        except Exception as e:
            messagebox.showinfo(
                "GitHub",
                "Repositório do projeto:\nhttps://github.com/seu-usuario/forticore-sentinel",
            )

    def open_documentation(self):
        """Abre documentação"""
        try:
            # Substitua pela URL da documentação
            webbrowser.open("https://forticore-sentinel.readthedocs.io")
        except Exception as e:
            messagebox.showinfo(
                "Documentação disponível em:\nhttps://forticore-sentinel.readthedocs.io"
            )

    def open_keepass_site(self):
        """Abre site oficial do KeePass"""
        try:
            webbrowser.open("https://keepass.info")
        except Exception as e:
            messagebox.showinfo(
                "KeePass", "Site oficial do KeePass:\nhttps://keepass.info"
            )

    def show_changelog(self):
        """Mostra changelog do projeto"""
        changelog_window = ttkb.Toplevel(self.tab_frame)
        changelog_window.title("📋 Changelog - FortiCore Sentinel")
        changelog_window.geometry("700x500")
        changelog_window.transient(self.tab_frame)
        changelog_window.grab_set()

        main_frame = ttkb.Frame(changelog_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text="📋 Histórico de Versões",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 15))

        # Área de texto com scroll
        text_frame = ttkb.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))

        changelog_text = tk.Text(
            text_frame, font=("Consolas", 10), wrap="word", state="normal"
        )

        scrollbar = ttkb.Scrollbar(
            text_frame, orient="vertical", command=changelog_text.yview
        )
        changelog_text.configure(yscrollcommand=scrollbar.set)

        # Conteúdo do changelog
        changelog_content = """
═══════════════════════════════════════════════════════════════
🛡️ FortiCore Sentinel - Changelog
═══════════════════════════════════════════════════════════════

🚀 Versão 2.0.0 - KeePass Edition (Atual)
──────────────────────────────────────────────────────────────
📅 Data: Janeiro 2025

🔄 MUDANÇAS PRINCIPAIS:
• Migração completa para formato KeePass (.kdbx)
• Nova arquitetura modular e organizada
• Interface redesenhada com ttkbootstrap

🔐 SEGURANÇA:
• ✅ Criptografia AES-256 com Argon2 KDF
• ✅ Verificação de integridade HMAC-SHA256
• ✅ Compatibilidade com padrão da indústria
• ✅ 2FA obrigatório mantido

💡 FUNCIONALIDADES:
• ✅ Interface moderna por abas
• ✅ Busca avançada em tempo real
• ✅ Editor de entradas completo
• ✅ Backup com verificação de integridade
• ✅ Importação do sistema antigo
• ✅ Exportação para CSV
• ✅ Compatibilidade com KeePass/KeePassXC

🛠️ MELHORIAS TÉCNICAS:
• ✅ Código modularizado e bem estruturado
• ✅ Tratamento robusto de erros
• ✅ Testes de integridade automáticos
• ✅ Documentação aprimorada

──────────────────────────────────────────────────────────────

📜 Versão 1.x - Sistema Original
──────────────────────────────────────────────────────────────
📅 Data: 2024

🔐 FUNCIONALIDADES ORIGINAIS:
• Sistema de criptografia AES-256 personalizado
• Autenticação 2FA com Google Authenticator
• Gerador de senhas criptograficamente seguro
• Interface tkinter básica
• Armazenamento em JSON criptografado

⚠️ LIMITAÇÕES DO SISTEMA ANTERIOR:
• Formato proprietário (não padrão)
• Sem verificação de integridade
• Interface menos moderna
• Compatibilidade limitada

🔄 RAZÕES PARA MIGRAÇÃO:
• Adotar padrão da indústria (.kdbx)
• Melhorar segurança com HMAC
• Aumentar compatibilidade
• Modernizar interface
• Facilitar manutenção do código

══════════════════════════════════════════════════════════════

🎯 ROADMAP FUTURO:
──────────────────────────────────────────────────────────────
• Plugin system para extensões
• Sincronização em nuvem segura
• App móvel companion
• Recursos avançados do KeePass
• Interface web opcional

══════════════════════════════════════════════════════════════
"""

        changelog_text.insert("1.0", changelog_content)
        changelog_text.config(state="disabled")

        changelog_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botão fechar
        close_btn = ttkb.Button(
            main_frame,
            text="Fechar",
            command=changelog_window.destroy,
            bootstyle="secondary",
            width=15,
        )
        close_btn.pack()

    def show_license(self):
        """Mostra informações de licença"""
        license_window = ttkb.Toplevel(self.tab_frame)
        license_window.title("📄 Licença - FortiCore Sentinel")
        license_window.geometry("600x400")
        license_window.transient(self.tab_frame)
        license_window.grab_set()

        main_frame = ttkb.Frame(license_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text="📄 Licença e Termos de Uso",
            font=("Segoe UI", 16, "bold"),
            bootstyle="warning",
        )
        title_label.pack(pady=(0, 15))

        # Área de texto
        text_frame = ttkb.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))

        license_text = tk.Text(
            text_frame, font=("Consolas", 10), wrap="word", state="normal"
        )

        scrollbar = ttkb.Scrollbar(
            text_frame, orient="vertical", command=license_text.yview
        )
        license_text.configure(yscrollcommand=scrollbar.set)

        license_content = """
MIT License

Copyright (c) 2025 FortiCore Sentinel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

═══════════════════════════════════════════════════════════════════════

DISCLAIMER / ISENÇÃO DE RESPONSABILIDADE:

Este software é fornecido "como está", sem garantias de qualquer tipo.
O uso é por sua própria conta e risco.

RESPONSABILIDADES DO USUÁRIO:
• Manter backups regulares de seus dados
• Lembrar-se da senha mestra (sem ela, dados são irrecuperáveis)
• Manter o dispositivo seguro e atualizado
• Usar senhas fortes e únicas

SOBRE SEGURANÇA:
• O software usa padrões de criptografia reconhecidos
• Implementa boas práticas de segurança
• Não coleta ou transmite dados pessoais
• Armazenamento é totalmente local

═══════════════════════════════════════════════════════════════════════

BIBLIOTECAS DE TERCEIROS:

Este software utiliza as seguintes bibliotecas:
• PyKeePass - Manipulação de bancos .kdbx
• Cryptography - Operações criptográficas
• ttkbootstrap - Interface moderna
• PyOTP - Autenticação 2FA
• Pillow - Processamento de imagens

Cada biblioteca tem sua própria licença. Consulte a documentação específica
para mais informações.
"""

        license_text.insert("1.0", license_content)
        license_text.config(state="disabled")

        license_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botão fechar
        close_btn = ttkb.Button(
            main_frame,
            text="Fechar",
            command=license_window.destroy,
            bootstyle="secondary",
            width=15,
        )
        close_btn.pack()

    def show_support(self):
        """Mostra informações de suporte"""
        support_window = ttkb.Toplevel(self.tab_frame)
        support_window.title("💬 Suporte - FortiCore Sentinel")
        support_window.geometry("550x450")
        support_window.transient(self.tab_frame)
        support_window.grab_set()

        main_frame = ttkb.Frame(support_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text="💬 Suporte e Ajuda",
            font=("Segoe UI", 16, "bold"),
            bootstyle="danger",
        )
        title_label.pack(pady=(0, 15))

        # Seções de suporte
        # FAQ
        faq_frame = ttkb.LabelFrame(
            main_frame, text="❓ Perguntas Frequentes", padding=15
        )
        faq_frame.pack(fill="x", pady=(0, 15))

        faq_text = """🔐 Esqueci minha senha mestra. Como recuperar?
   ❌ Infelizmente não é possível. As senhas são irrecuperáveis por design.
   💡 Solução: Use backups regulares e anote a senha em local seguro.

🔄 Posso usar meu banco em outros programas?
   ✅ Sim! O formato .kdbx é compatível com KeePass, KeePassXC e apps móveis.

📱 Como configurar 2FA no celular?
   1. Instale Google Authenticator ou similar
   2. Escaneie o QR Code na primeira configuração
   3. Use os códigos de 6 dígitos quando solicitado

💾 Com que frequência devo fazer backup?
   💡 Recomendado: Após cada adição/modificação importante de senhas."""

        faq_label = ttkb.Label(
            faq_frame, text=faq_text, font=("Segoe UI", 9), justify="left"
        )
        faq_label.pack(anchor="w")

        # Contato
        contact_frame = ttkb.LabelFrame(
            main_frame, text="📧 Contato e Suporte", padding=15
        )
        contact_frame.pack(fill="x", pady=(0, 15))

        contact_text = """🐛 Reportar bugs: GitHub Issues
📧 Email: seu-email@exemplo.com
💬 Chat: Discord/Telegram (se disponível)
📖 Documentação: Wiki do projeto

⏰ Tempo de resposta: 1-3 dias úteis
🌍 Suporte em: Português e Inglês"""

        contact_label = ttkb.Label(
            contact_frame, text=contact_text, font=("Segoe UI", 10), justify="left"
        )
        contact_label.pack(anchor="w")

        # Botões de ação
        action_frame = ttkb.Frame(main_frame)
        action_frame.pack(fill="x")

        def open_issues():
            try:
                webbrowser.open(
                    "https://github.com/seu-usuario/forticore-sentinel/issues"
                )
            except:
                messagebox.showinfo(
                    "GitHub Issues",
                    "https://github.com/seu-usuario/forticore-sentinel/issues",
                )

        def send_email():
            try:
                webbrowser.open(
                    "mailto:seu-email@exemplo.com?subject=FortiCore Sentinel - Suporte"
                )
            except:
                messagebox.showinfo("Email", "Email: seu-email@exemplo.com")

        issues_btn = ttkb.Button(
            action_frame,
            text="🐛 Reportar Bug",
            command=open_issues,
            bootstyle="danger-outline",
            width=15,
        )
        issues_btn.pack(side="left", padx=(0, 10))

        email_btn = ttkb.Button(
            action_frame,
            text="📧 Enviar Email",
            command=send_email,
            bootstyle="primary-outline",
            width=15,
        )
        email_btn.pack(side="left", padx=(0, 10))

        close_btn = ttkb.Button(
            action_frame,
            text="Fechar",
            command=support_window.destroy,
            bootstyle="secondary",
            width=10,
        )
        close_btn.pack(side="right")
