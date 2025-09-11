import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os
import datetime

from core.keepass_manager import KeePassManager
from utils.caminhos import get_pasta_cofre


class SecurityTab:
    def __init__(self, notebook, status_bar, vault_tab_ref=None):
        self.notebook = notebook
        self.status_bar = status_bar
        self.vault_tab_ref = vault_tab_ref
        self.keepass_manager = KeePassManager()

    def create(self):
        """Cria a aba de configurações de segurança"""
        self.tab_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="🔒 Segurança")

        self.main_container = ttkb.Frame(self.tab_frame)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_security_status()
        self.create_2fa_section()
        self.create_database_management()

    def create_security_status(self):
        """Cria seção de status de segurança"""
        status_frame = ttkb.LabelFrame(
            self.main_container,
            text="🛡️ Status de Segurança Atual",
            bootstyle="success",
            padding=20,
        )
        status_frame.pack(fill="x", pady=(0, 15))

        security_info = """✅ Banco de dados KeePass (.kdbx) - Padrão da indústria
✅ Criptografia AES-256 com Argon2 KDF
✅ Verificação de integridade HMAC-SHA256
✅ Autenticação de dois fatores (2FA) obrigatória
✅ Armazenamento local seguro
✅ Backup com verificação de integridade"""

        info_label = ttkb.Label(
            status_frame,
            text=security_info,
            font=("Segoe UI", 10),
            justify="left",
            bootstyle="success",
        )
        info_label.pack(anchor="w")

        # Estatísticas do banco
        self.stats_frame = ttkb.Frame(status_frame)
        self.stats_frame.pack(fill="x", pady=(15, 0))

        self.update_database_stats()

    def test_2fa(self):
        """Testa o funcionamento do 2FA"""
        try:
            from assets.autenticacao_2fa import verificar_apenas_2fa

            if not self.keepass_manager.ensure_open():
                messagebox.showerror("Erro", "Abra o banco de dados primeiro!")
                return

            # CORREÇÃO: Usar função específica para teste de 2FA
            if verificar_apenas_2fa():
                messagebox.showinfo("2FA", "O código 2FA foi validado com sucesso!")
            else:
                messagebox.showerror("2FA", "Falha na validação do código 2FA!")

        except ImportError:
            messagebox.showerror("Erro", "Módulo de autenticação 2FA não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao testar 2FA:\n{e}")

    def reset_2fa(self):
        """Reconfigura o 2FA"""
        try:
            if not self.keepass_manager.ensure_open():
                messagebox.showerror("Erro", "Abra o banco de dados primeiro!")
                return

            if messagebox.askyesno(
                "Confirmar",
                "Deseja reconfigurar o 2FA?\nVocê precisará escanear um novo QR Code.",
            ):
                # CORREÇÃO: Usar função específica de reset
                from assets.autenticacao_2fa import resetar_configuracao

                resetar_configuracao()
                messagebox.showinfo(
                    "2FA",
                    "2FA resetado com sucesso!\nConfigure novamente na próxima abertura do cofre.",
                )

        except ImportError:
            messagebox.showerror("Erro", "Módulo de configuração 2FA não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reconfigurar 2FA:\n{e}")

    def update_database_stats(self):
        """Atualiza as estatísticas do banco de dados"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        db_path = self.keepass_manager.get_database_path()
        if db_path and os.path.exists(db_path):
            try:
                stats = self.keepass_manager.get_database_stats()

                size_kb = stats.get("database_size", 0) / 1024
                num_entries = stats.get("total_entries", 0)
                integrity_ok = stats.get("integrity_verified", False)

                if stats.get("last_modified"):
                    last_modified = datetime.datetime.fromisoformat(
                        stats["last_modified"]
                    ).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    last_modified = "Desconhecido"

                stats_text = (
                    f"📁 Banco: {os.path.basename(db_path)} | "
                    f"🔢 Entradas: {num_entries} | "
                    f"💾 Tamanho: {size_kb:.2f} KB | "
                    f"🕒 Última modificação: {last_modified} | "
                    f"🛡️ Integridade: {'✅' if integrity_ok else '❌'}"
                )
            except Exception as e:
                stats_text = f"Erro ao obter estatísticas do banco: {e}"
        else:
            stats_text = "❌ Nenhum banco de dados carregado."

        stats_label = ttkb.Label(
            self.stats_frame,
            text=stats_text,
            font=("Segoe UI", 9),
            bootstyle="info",
        )
        stats_label.pack(anchor="w")

    def create_2fa_section(self):
        """Cria seção de configurações 2FA"""
        twofa_frame = ttkb.LabelFrame(
            self.main_container,
            text="🔐 Autenticação de Dois Fatores (2FA)",
            bootstyle="primary",
            padding=20,
        )
        twofa_frame.pack(fill="x", pady=(0, 15))

        desc_label = ttkb.Label(
            twofa_frame,
            text="O 2FA está ativo e é obrigatório para todas as operações sensíveis.\nUse o Google Authenticator ou app compatível para gerar códigos.",
            font=("Segoe UI", 10),
            justify="left",
        )
        desc_label.pack(anchor="w", pady=(0, 15))

        twofa_buttons = ttkb.Frame(twofa_frame)
        twofa_buttons.pack(fill="x")

        test_2fa_btn = ttkb.Button(
            twofa_buttons,
            text="🧪 Testar 2FA",
            command=self.test_2fa,
            bootstyle="primary-outline",
            width=15,
        )
        test_2fa_btn.pack(side="left", padx=(0, 10))

        reset_2fa_btn = ttkb.Button(
            twofa_buttons,
            text="🔄 Reconfigurar 2FA",
            command=self.reset_2fa,
            bootstyle="warning-outline",
            width=20,
        )
        reset_2fa_btn.pack(side="left")

    def create_database_management(self):
        """Cria seção de gerenciamento do banco"""
        db_frame = ttkb.LabelFrame(
            self.main_container,
            text="🗄️ Gerenciamento do Banco de Dados",
            bootstyle="info",
            padding=20,
        )
        db_frame.pack(fill="x", pady=(0, 15))

        # Primeira linha - Operações básicas
        basic_ops_frame = ttkb.Frame(db_frame)
        basic_ops_frame.pack(fill="x", pady=(0, 10))

        verify_btn = ttkb.Button(
            basic_ops_frame,
            text="🔍 Verificar Integridade",
            command=self.verify_integrity,
            bootstyle="info-outline",
            width=20,
        )
        verify_btn.pack(side="left", padx=(0, 10))

        stats_btn = ttkb.Button(
            basic_ops_frame,
            text="📊 Estatísticas",
            command=self.show_detailed_stats,
            bootstyle="secondary-outline",
            width=15,
        )
        stats_btn.pack(side="left")

        # Segunda linha - Operações avançadas
        advanced_ops_frame = ttkb.Frame(db_frame)
        advanced_ops_frame.pack(fill="x")

        change_pass_btn = ttkb.Button(
            advanced_ops_frame,
            text="🔑 Alterar Senha Mestra",
            command=self.change_master_password,
            bootstyle="warning-outline",
            width=22,
        )
        change_pass_btn.pack(side="left", padx=(0, 10))

        export_btn = ttkb.Button(
            advanced_ops_frame,
            text="📤 Exportar CSV",
            command=self.export_entries_list,
            bootstyle="secondary-outline",
            width=15,
        )
        export_btn.pack(side="left", padx=(0, 10))

    def verify_integrity(self):
        """Verifica integridade do banco"""
        try:
            if self.keepass_manager._verify_database_integrity():
                messagebox.showinfo("Integridade", "✅ Banco de dados íntegro!")
                self.status_bar.update_status("Integridade verificada")
            else:
                messagebox.showerror("Integridade", "❌ Banco comprometido!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na verificação: {e}")

    def show_detailed_stats(self):
        """Mostra estatísticas detalhadas"""
        try:
            stats = self.keepass_manager.get_database_stats()

            stats_text = f"""📊 Estatísticas Detalhadas do Banco

🔢 Total de Entradas: {stats.get('total_entries', 0)}
📁 Total de Grupos: {stats.get('total_groups', 0)}
💾 Tamanho do Arquivo: {stats.get('database_size', 0) / 1024:.2f} KB
🛡️ Integridade Verificada: {'✅ Sim' if stats.get('integrity_verified') else '❌ Não'}

📅 Criado em: {stats.get('created', 'Desconhecido')}
🕒 Última Modificação: {stats.get('last_modified', 'Desconhecido')}

📂 Local do Arquivo: {self.keepass_manager.get_database_path()}"""

            messagebox.showinfo("Estatísticas", stats_text)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter estatísticas: {e}")

    def change_master_password(self):
        """CORREÇÃO: Método descomentado e implementado corretamente"""
        try:
            if not self.keepass_manager.ensure_open():
                messagebox.showerror("Erro", "Abra o banco de dados primeiro!")
                return

            # CORREÇÃO 1: Verificar 2FA antes de alterar senha
            from assets.autenticacao_2fa import verificar_apenas_2fa

            if not verificar_apenas_2fa():
                messagebox.showerror("Erro", "Verificação 2FA necessária!")
                return

            # CORREÇÃO 2: Usar interface customizada para nova senha
            dialog_result = self._show_password_change_dialog()

            if dialog_result:
                new_password, confirm_password = dialog_result

                if new_password == confirm_password:
                    if self.keepass_manager.change_master_password(new_password):
                        messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
                        self.status_bar.update_status("Senha mestra alterada")

                        # CORREÇÃO 3: Atualizar hash da senha no arquivo de configuração
                        try:
                            from assets.autenticacao_2fa import (
                                salvar_config_cofre,
                                obter_config_cofre,
                                hash_senha,
                            )

                            config = obter_config_cofre()
                            nome_cofre = config.get("nome_cofre", "FortiCore")
                            salvar_config_cofre(nome_cofre, hash_senha(new_password))
                        except Exception as e:
                            print(
                                f"Aviso: Não foi possível atualizar configuração 2FA: {e}"
                            )
                    else:
                        messagebox.showerror("Erro", "Falha ao alterar senha!")
                else:
                    messagebox.showerror("Erro", "Senhas não coincidem!")

        except ImportError:
            messagebox.showerror("Erro", "Módulo de autenticação 2FA não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar senha: {e}")

    def _show_password_change_dialog(self):
        """NOVO: Mostra diálogo personalizado para mudança de senha"""
        dialog = ttkb.Toplevel()
        dialog.title("🔑 Alterar Senha Mestra")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.tab_frame)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        result = None

        main_frame = ttkb.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text="Nova Senha Mestra",
            font=("Segoe UI", 12, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 20))

        # Nova senha
        ttkb.Label(
            main_frame,
            text="Nova senha (mínimo 8 caracteres):",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        new_password_var = tk.StringVar()
        new_password_entry = ttkb.Entry(
            main_frame, textvariable=new_password_var, show="*", font=("Segoe UI", 11)
        )
        new_password_entry.pack(fill="x", pady=(0, 15))

        # Confirmar senha
        ttkb.Label(
            main_frame, text="Confirmar nova senha:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        confirm_password_var = tk.StringVar()
        confirm_password_entry = ttkb.Entry(
            main_frame,
            textvariable=confirm_password_var,
            show="*",
            font=("Segoe UI", 11),
        )
        confirm_password_entry.pack(fill="x", pady=(0, 20))

        # Botões
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.pack(fill="x")

        def on_confirm():
            nonlocal result
            new_pass = new_password_var.get()
            confirm_pass = confirm_password_var.get()

            if len(new_pass) < 8:
                messagebox.showerror("Erro", "Senha deve ter pelo menos 8 caracteres!")
                return

            if not new_pass or not confirm_pass:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            result = (new_pass, confirm_pass)
            dialog.destroy()

        def on_cancel():
            nonlocal result
            result = None
            dialog.destroy()

        cancel_btn = ttkb.Button(
            btn_frame,
            text="Cancelar",
            command=on_cancel,
            bootstyle="secondary",
            width=12,
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        confirm_btn = ttkb.Button(
            btn_frame, text="Alterar", command=on_confirm, bootstyle="success", width=12
        )
        confirm_btn.pack(side="right")

        # Focar no primeiro campo
        new_password_entry.focus()

        # Enter para confirmar
        dialog.bind("<Return>", lambda e: on_confirm())

        # Aguardar resultado
        dialog.wait_window()

        return result

    def export_entries_list(self):
        """Exporta entradas para CSV"""
        try:
            # CORREÇÃO: Verificar 2FA antes de exportar
            from assets.autenticacao_2fa import verificar_apenas_2fa

            if not verificar_apenas_2fa():
                messagebox.showerror(
                    "Erro", "Verificação 2FA necessária para exportação!"
                )
                return

            export_path = filedialog.asksaveasfilename(
                title="Exportar Lista",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Todos os arquivos", "*.*")],
            )

            if export_path:
                if self.keepass_manager.export_to_csv(export_path):
                    messagebox.showinfo("Sucesso", "Lista exportada com sucesso!")
                    self.status_bar.update_status("Lista exportada")
                else:
                    messagebox.showerror("Erro", "Falha na exportação!")

        except ImportError:
            messagebox.showerror("Erro", "Módulo de autenticação 2FA não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na exportação: {e}")
