"""
FortiCore Sentinel - Aba do Cofre KeePass - VERSÃO CORRIGIDA
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import pyperclip
from datetime import datetime

from core.keepass_manager import KeePassManager

# MUDANÇA 1: Importar a função correta para usar apenas 2FA
from assets.autenticacao_2fa import verificar_apenas_2fa, verificar_2fa_gui


class VaultTab:
    def __init__(self, notebook, status_bar):
        """Inicializa a aba do cofre"""
        self.notebook = notebook
        self.status_bar = status_bar
        self.keepass_manager = KeePassManager()
        self.current_entries = []

    def create(self):
        """Cria a aba do cofre"""
        self.tab_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="🗂️ Cofre KeePass")

        self.main_container = ttkb.Frame(self.tab_frame)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_toolbar()
        self.create_vault_list()
        self.create_context_menu()

        # Carregar dados iniciais SEM autenticação automática
        self.refresh_vault_list()

    def create_toolbar(self):
        """Cria a barra de ferramentas"""
        self.toolbar = ttkb.Frame(self.main_container)
        self.toolbar.pack(fill="x", pady=(0, 10))

        # Lado esquerdo - Busca
        search_frame = ttkb.Frame(self.toolbar)
        search_frame.pack(side="left", fill="x", expand=True)

        ttkb.Label(search_frame, text="🔍 Buscar:").pack(side="left")

        self.search_entry = ttkb.Entry(search_frame, font=("Segoe UI", 10), width=30)
        self.search_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_vault())
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        search_btn = ttkb.Button(
            search_frame,
            text="Buscar",
            command=self.search_vault,
            bootstyle="primary-outline",
            width=10,
        )
        search_btn.pack(side="left", padx=(10, 0))

        # Lado direito - Ações
        action_frame = ttkb.Frame(self.toolbar)
        action_frame.pack(side="right")

        add_btn = ttkb.Button(
            action_frame,
            text="➕ Nova Entrada",
            command=self.add_entry,
            bootstyle="success-outline",
            width=15,
        )
        add_btn.pack(side="left", padx=(0, 5))

        refresh_btn = ttkb.Button(
            action_frame,
            text="🔄 Atualizar",
            command=self.refresh_vault_list,
            bootstyle="info-outline",
            width=12,
        )
        refresh_btn.pack(side="left", padx=(0, 5))

        backup_btn = ttkb.Button(
            action_frame,
            text="📦 Backup",
            command=self.backup_vault,
            bootstyle="warning-outline",
            width=10,
        )
        backup_btn.pack(side="left", padx=(0, 5))

        import_csv_btn = ttkb.Button(
            action_frame,
            text="📥 Importar CSV",
            command=self.import_csv_entries,
            bootstyle="secondary-outline",
            width=15,
        )
        import_csv_btn.pack(side="left", padx=(0, 5))

    def create_vault_list(self):
        """Cria a lista do cofre"""
        list_frame = ttkb.Frame(self.main_container)
        list_frame.pack(fill="both", expand=True)

        # Configurar Treeview
        columns = ("title", "username", "password", "url", "created", "modified")
        self.vault_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        # Cabeçalhos
        headers = {
            "title": "Título",
            "username": "Usuário",
            "url": "URL/Website",
            "created": "Criado em",
            "modified": "Modificado em",
        }

        for col, header in headers.items():
            self.vault_tree.heading(
                col, text=header, command=lambda c=col: self.sort_by_column(c)
            )
            if col == "title":
                self.vault_tree.column(col, width=250)
            elif col == "username":
                self.vault_tree.column(col, width=150)
            elif col == "url":
                self.vault_tree.column(col, width=200)
            else:
                self.vault_tree.column(col, width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.vault_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient="horizontal", command=self.vault_tree.xview
        )

        self.vault_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Grid layout
        self.vault_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Bindings
        self.vault_tree.bind("<Double-1>", self.view_entry_details)
        self.vault_tree.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        """Cria menu de contexto"""
        self.context_menu = tk.Menu(self.tab_frame, tearoff=0)
        self.context_menu.add_command(
            label="👁️ Ver Detalhes", command=self.view_entry_details
        )
        self.context_menu.add_command(
            label="📋 Copiar Senha", command=self.copy_password
        )
        self.context_menu.add_command(
            label="📋 Copiar Usuário", command=self.copy_username
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Editar", command=self.edit_entry)
        self.context_menu.add_command(label="🗑️ Excluir", command=self.delete_entry)

    def import_csv_entries(self):
        """Importa entradas de arquivo CSV"""
        try:
            # MUDANÇA 2: Usar verificar_apenas_2fa em vez de verificar_2fa_gui
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo("Cancelado", "Operação cancelada pelo usuário.")
                return

            from tkinter import filedialog, messagebox

            # Abrir diálogo para selecionar arquivo CSV
            csv_path = filedialog.askopenfilename(
                title="Importar Entradas de CSV",
                filetypes=[("CSV files", "*.csv"), ("Todos os arquivos", "*.*")],
            )

            if not csv_path:
                return

            # Confirmar importação
            if not messagebox.askyesno(
                "Confirmar Importação",
                "Deseja importar entradas do arquivo CSV?\n\n"
                "Formato esperado:\ntitle,username,password,url,notes\n\n"
                "As entradas serão adicionadas ao seu cofre.",
            ):
                return

            # Usar o KeePassManager para importar
            if hasattr(self, "keepass_manager"):
                success = self.keepass_manager.import_from_csv(csv_path)
            else:
                # Se não tiver referência direta, criar uma instância
                from core.keepass_manager import KeePassManager

                manager = KeePassManager()
                success = manager.import_from_csv(csv_path)

            if success:
                # Atualizar a tabela de entradas
                self.refresh_entries()

                # Atualizar status bar se disponível
                if hasattr(self, "status_bar"):
                    self.status_bar.update_status("Entradas importadas do CSV")

                messagebox.showinfo("Sucesso", "Entradas importadas com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha na importação do CSV!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar CSV: {e}")

    def refresh_entries(self):
        """Atualiza a lista de entradas na tabela"""
        # CORREÇÃO: Usar self.vault_tree ao invés de self.tree
        try:
            # Limpar tabela atual
            for item in self.vault_tree.get_children():
                self.vault_tree.delete(item)

            # Recarregar entradas do banco
            if hasattr(self, "keepass_manager"):
                entries = self.keepass_manager.get_all_entries()
            else:
                from core.keepass_manager import KeePassManager

                manager = KeePassManager()
                entries = manager.get_all_entries()

            # Repopular a tabela
            for entry in entries:
                created_str = (
                    entry["created"][:16].replace("T", " ")
                    if entry["created"]
                    else "N/A"
                )
                modified_str = (
                    entry["modified"][:16].replace("T", " ")
                    if entry["modified"]
                    else "N/A"
                )

                self.vault_tree.insert(
                    "",
                    "end",
                    values=(
                        entry["title"],
                        entry["username"],
                        entry["url"],
                        created_str,
                        modified_str,
                    ),
                    tags=(str(hash(entry["title"] + entry["created"])),),
                )

            # Atualizar entradas atuais
            self.current_entries = entries

            # Atualizar status se disponível
            if hasattr(self, "status_bar"):
                count = len(entries)
                self.status_bar.update_entries_count(f"{count} entradas no cofre")

        except Exception as e:
            print(f"Erro ao atualizar entradas: {e}")

    def refresh_vault_list(self):
        """Atualiza a lista do cofre SEM autenticação"""
        try:
            # Limpar árvore
            for item in self.vault_tree.get_children():
                self.vault_tree.delete(item)

            # Obter entradas SEM autenticação (apenas listagem)
            self.current_entries = self.keepass_manager.get_all_entries()

            # Popular árvore
            for entry in self.current_entries:
                created_str = (
                    entry["created"][:16].replace("T", " ")
                    if entry["created"]
                    else "N/A"
                )
                modified_str = (
                    entry["modified"][:16].replace("T", " ")
                    if entry["modified"]
                    else "N/A"
                )

                self.vault_tree.insert(
                    "",
                    "end",
                    values=(
                        entry["title"],
                        entry["username"],
                        entry["url"],
                        created_str,
                        modified_str,
                    ),
                    tags=(str(hash(entry["title"] + entry["created"])),),
                )

            # Atualizar status
            count = len(self.current_entries)
            self.status_bar.update_entries_count(f"{count} entradas no cofre")

        except Exception as e:
            self.status_bar.update_status(f"Erro ao carregar cofre: {str(e)}")

    def on_search_change(self, event):
        """Busca em tempo real conforme digita SEM autenticação"""
        query = self.search_entry.get().strip()
        if len(query) >= 2:  # Buscar a partir de 2 caracteres
            self.filter_entries(query)
        elif len(query) == 0:  # Limpar busca
            self.refresh_vault_list()

    def filter_entries(self, query):
        """Filtra entradas na lista SEM autenticação"""
        try:
            # Limpar árvore
            for item in self.vault_tree.get_children():
                self.vault_tree.delete(item)

            # Filtrar entradas
            query_lower = query.lower()
            filtered_entries = []

            for entry in self.current_entries:
                if (
                    query_lower in entry["title"].lower()
                    or query_lower in entry["username"].lower()
                    or query_lower in entry["url"].lower()
                ):
                    filtered_entries.append(entry)

            # Popular árvore com resultados filtrados
            for entry in filtered_entries:
                created_str = (
                    entry["created"][:16].replace("T", " ")
                    if entry["created"]
                    else "N/A"
                )
                modified_str = (
                    entry["modified"][:16].replace("T", " ")
                    if entry["modified"]
                    else "N/A"
                )

                self.vault_tree.insert(
                    "",
                    "end",
                    values=(
                        entry["title"],
                        entry["username"],
                        entry["url"],
                        created_str,
                        modified_str,
                    ),
                    tags=(str(hash(entry["title"] + entry["created"])),),
                )

        except Exception as e:
            print(f"Erro ao filtrar: {e}")

    def search_vault(self):
        """Busca no cofre com 2FA APENAS se for busca avançada"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Aviso", "Digite algo para buscar!")
            return

        try:
            # MUDANÇA 3: Usar verificar_apenas_2fa para busca avançada
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo("Cancelado", "Busca cancelada pelo usuário.")
                return

            results = self.keepass_manager.search_entries(query)

            if results:
                self.show_search_results(query, results)
                self.status_bar.update_status(
                    f"Encontradas {len(results)} entradas para '{query}'"
                )
            else:
                messagebox.showinfo(
                    "Busca", f"Nenhuma entrada encontrada para '{query}'"
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar: {str(e)}")

    def show_search_results(self, query, results):
        """Mostra resultados detalhados da busca"""
        results_window = ttkb.Toplevel(self.tab_frame)
        results_window.title(f"Resultados: {query}")
        results_window.geometry("700x500")
        results_window.transient(self.tab_frame)
        results_window.grab_set()

        main_frame = ttkb.Frame(results_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text=f"🔍 Resultados para: '{query}'",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 15))

        # Lista de resultados
        results_frame = ttkb.LabelFrame(
            main_frame, text=f"{len(results)} entradas encontradas", padding=10
        )
        results_frame.pack(fill="both", expand=True)

        # Treeview para resultados
        columns = ("title", "username", "url")
        results_tree = ttk.Treeview(
            results_frame, columns=columns, show="headings", height=12
        )

        results_tree.heading("title", text="Título")
        results_tree.heading("username", text="Usuário")
        results_tree.heading("url", text="URL")

        results_tree.column("title", width=200)
        results_tree.column("username", width=150)
        results_tree.column("url", width=200)

        # Popular resultados
        for result in results:
            results_tree.insert(
                "", "end", values=(result["title"], result["username"], result["url"])
            )

        results_tree.pack(fill="both", expand=True)

        # Botões
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        def view_selected():
            selection = results_tree.selection()
            if selection:
                item = results_tree.item(selection[0])
                title = item["values"][0]
                # Encontrar entrada correspondente
                for result in results:
                    if result["title"] == title:
                        self.show_entry_details(result)
                        break

        view_btn = ttkb.Button(
            button_frame,
            text="👁️ Ver Detalhes",
            command=view_selected,
            bootstyle="primary",
            width=15,
        )
        view_btn.pack(side="left", padx=(0, 10))

        close_btn = ttkb.Button(
            button_frame,
            text="Fechar",
            command=results_window.destroy,
            bootstyle="secondary",
            width=10,
        )
        close_btn.pack(side="right")

    def get_selected_entry(self):
        """Obtém a entrada selecionada"""
        selection = self.vault_tree.selection()
        if not selection:
            return None

        item = self.vault_tree.item(selection[0])
        title = item["values"][0]
        created = item["values"][3]

        # Encontrar entrada correspondente
        for entry in self.current_entries:
            entry_created = (
                entry["created"][:16].replace("T", " ") if entry["created"] else "N/A"
            )
            if entry["title"] == title and entry_created == created:
                return entry

        return None

    def show_context_menu(self, event):
        """Mostra menu de contexto"""
        item = self.vault_tree.identify("item", event.x, event.y)
        if item:
            self.vault_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def view_entry_details(self, event=None):
        """Visualiza detalhes da entrada COM 2FA"""
        entry = self.get_selected_entry()
        if not entry:
            if event is None:  # Chamado pelo menu, não por duplo clique
                messagebox.showwarning("Aviso", "Selecione uma entrada!")
            return

        try:
            # MUDANÇA 4: Usar verificar_apenas_2fa para ver detalhes
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo("Cancelado", "Visualização cancelada pelo usuário.")
                return

            self.show_entry_details(entry)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar detalhes: {str(e)}")

    def show_entry_details(self, entry):
        """Mostra janela com detalhes da entrada"""
        details_window = ttkb.Toplevel(self.tab_frame)
        details_window.title(f"Detalhes: {entry['title']}")
        details_window.geometry("600x500")
        details_window.transient(self.tab_frame)
        details_window.grab_set()

        main_frame = ttkb.Frame(details_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text=f"🔐 {entry['title']}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 15))

        # Informações
        info_frame = ttkb.LabelFrame(main_frame, text="Informações", padding=15)
        info_frame.pack(fill="x", pady=(0, 15))

        # Campos de informação
        fields = [
            ("Título:", entry["title"]),
            ("Usuário:", entry["username"]),
            ("password", entry["password"]),
            ("URL:", entry["url"]),
            (
                "Criado em:",
                entry["created"][:16].replace("T", " ") if entry["created"] else "N/A",
            ),
            (
                "Modificado em:",
                (
                    entry["modified"][:16].replace("T", " ")
                    if entry["modified"]
                    else "N/A"
                ),
            ),
        ]

        for label_text, value in fields:
            field_frame = ttkb.Frame(info_frame)
            field_frame.pack(fill="x", pady=2)

            ttkb.Label(
                field_frame, text=label_text, font=("Segoe UI", 10, "bold"), width=15
            ).pack(side="left")
            ttkb.Label(field_frame, text=value, font=("Segoe UI", 10)).pack(
                side="left", anchor="w"
            )

        # Senha
        password_frame = ttkb.LabelFrame(main_frame, text="Senha", padding=15)
        password_frame.pack(fill="x", pady=(0, 15))

        password_display_frame = ttkb.Frame(password_frame)
        password_display_frame.pack(fill="x")

        password_var = ttkb.StringVar(value=entry["password"])
        password_entry = ttkb.Entry(
            password_display_frame,
            textvariable=password_var,
            font=("Consolas", 11),
            state="readonly",
            show="*",
        )
        password_entry.pack(side="left", fill="x", expand=True)

        def toggle_visibility():
            current = password_entry.cget("show")
            if current == "":
                password_entry.config(show="*")
                toggle_btn.config(text="👁️")
            else:
                password_entry.config(show="")
                toggle_btn.config(text="🔒")

        toggle_btn = ttkb.Button(
            password_display_frame,
            text="👁️",
            width=3,
            command=toggle_visibility,
            bootstyle="outline-secondary",
        )
        toggle_btn.pack(side="right", padx=(5, 0))

        # Notas
        if entry["notes"]:
            notes_frame = ttkb.LabelFrame(main_frame, text="Notas", padding=15)
            notes_frame.pack(fill="both", expand=True, pady=(0, 15))

            notes_text = tk.Text(
                notes_frame,
                height=6,
                font=("Segoe UI", 10),
                state="normal",
                wrap="word",
            )
            notes_text.pack(fill="both", expand=True)
            notes_text.insert("1.0", entry["notes"])
            notes_text.config(state="disabled")

            # Scrollbar para notas
            notes_scroll = ttk.Scrollbar(
                notes_frame, orient="vertical", command=notes_text.yview
            )
            notes_text.configure(yscrollcommand=notes_scroll.set)
            notes_scroll.pack(side="right", fill="y")

        # Botões
        buttons_frame = ttkb.Frame(main_frame)
        buttons_frame.pack(fill="x")

        copy_pass_btn = ttkb.Button(
            buttons_frame,
            text="📋 Copiar Senha",
            command=lambda: self.copy_to_clipboard(entry["password"], "Senha copiada!"),
            bootstyle="primary",
            width=15,
        )
        copy_pass_btn.pack(side="left", padx=(0, 5))

        copy_user_btn = ttkb.Button(
            buttons_frame,
            text="📋 Copiar Usuário",
            command=lambda: self.copy_to_clipboard(
                entry["username"], "Usuário copiado!"
            ),
            bootstyle="info",
            width=15,
        )
        copy_user_btn.pack(side="left", padx=(0, 5))

        edit_btn = ttkb.Button(
            buttons_frame,
            text="✏️ Editar",
            command=lambda: self.edit_entry_dialog(entry),
            bootstyle="warning",
            width=10,
        )
        edit_btn.pack(side="left", padx=(0, 5))

        close_btn = ttkb.Button(
            buttons_frame,
            text="Fechar",
            command=details_window.destroy,
            bootstyle="secondary",
            width=10,
        )
        close_btn.pack(side="right")

    def copy_to_clipboard(self, text, message):
        """Copia texto para área de transferência"""
        if text:
            pyperclip.copy(text)
            self.status_bar.update_status(message)
        else:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar!")

    def copy_password(self):
        """Copia senha da entrada selecionada COM 2FA"""
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Aviso", "Selecione uma entrada!")
            return

        try:
            # MUDANÇA 5: Usar verificar_apenas_2fa para copiar senha
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo(
                    "Cancelado", "Cópia de senha cancelada pelo usuário."
                )
                return

            self.copy_to_clipboard(entry["password"], "Senha copiada!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar senha: {str(e)}")

    def copy_username(self):
        """Copia usuário da entrada selecionada SEM 2FA"""
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Aviso", "Selecione uma entrada!")
            return

        # Copiar usuário não precisa de autenticação
        self.copy_to_clipboard(entry["username"], "Usuário copiado!")

    def add_entry(self):
        """Adiciona nova entrada COM 2FA"""
        try:
            # MUDANÇA 6: Usar verificar_apenas_2fa para adicionar entrada
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo(
                    "Cancelado", "Adição de entrada cancelada pelo usuário."
                )
                return

            self.show_entry_editor()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar entrada: {str(e)}")

    def edit_entry(self):
        """Edita entrada selecionada COM 2FA"""
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Aviso", "Selecione uma entrada!")
            return

        try:
            # MUDANÇA 7: Usar verificar_apenas_2fa para editar entrada
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo(
                    "Cancelado", "Edição de entrada cancelada pelo usuário."
                )
                return

            self.edit_entry_dialog(entry)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar entrada: {str(e)}")

    def edit_entry_dialog(self, entry):
        """Mostra diálogo de edição"""
        self.show_entry_editor(entry)

    def show_entry_editor(self, entry=None):
        """Mostra editor de entrada"""
        is_edit = entry is not None
        title = "Editar Entrada" if is_edit else "Nova Entrada"

        editor_window = ttkb.Toplevel(self.tab_frame)
        editor_window.title(title)
        editor_window.geometry("500x600")
        editor_window.transient(self.tab_frame)
        editor_window.grab_set()

        main_frame = ttkb.Frame(editor_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ttkb.Label(
            main_frame,
            text=f"{'✏️' if is_edit else '➕'} {title}",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 20))

        # Campos
        fields_frame = ttkb.LabelFrame(
            main_frame, text="Informações da Entrada", padding=20
        )
        fields_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Variáveis
        title_var = ttkb.StringVar(value=entry["title"] if is_edit else "")
        username_var = ttkb.StringVar(value=entry["username"] if is_edit else "")
        password_var = ttkb.StringVar(value=entry["password"] if is_edit else "")
        url_var = ttkb.StringVar(value=entry["url"] if is_edit else "")
        notes_var = ttkb.StringVar(value=entry["notes"] if is_edit else "")

        # Título
        ttkb.Label(fields_frame, text="Título*:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        title_entry = ttkb.Entry(
            fields_frame, textvariable=title_var, font=("Segoe UI", 11)
        )
        title_entry.pack(fill="x", pady=(5, 15))

        # Usuário
        ttkb.Label(fields_frame, text="Usuário:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        username_entry = ttkb.Entry(
            fields_frame, textvariable=username_var, font=("Segoe UI", 11)
        )
        username_entry.pack(fill="x", pady=(5, 15))

        # Senha
        password_frame = ttkb.Frame(fields_frame)
        password_frame.pack(fill="x", pady=(0, 15))

        ttkb.Label(password_frame, text="Senha*:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )

        password_input_frame = ttkb.Frame(password_frame)
        password_input_frame.pack(fill="x", pady=(5, 0))

        password_entry = ttkb.Entry(
            password_input_frame,
            textvariable=password_var,
            font=("Consolas", 11),
            show="*",
        )
        password_entry.pack(side="left", fill="x", expand=True)

        def toggle_password_visibility():
            current = password_entry.cget("show")
            if current == "":
                password_entry.config(show="*")
                pass_toggle_btn.config(text="👁️")
            else:
                password_entry.config(show="")
                pass_toggle_btn.config(text="🔒")

        pass_toggle_btn = ttkb.Button(
            password_input_frame,
            text="👁️",
            width=3,
            command=toggle_password_visibility,
            bootstyle="outline-secondary",
        )
        pass_toggle_btn.pack(side="right", padx=(5, 0))

        # URL
        ttkb.Label(
            fields_frame, text="URL/Website:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")
        url_entry = ttkb.Entry(
            fields_frame, textvariable=url_var, font=("Segoe UI", 11)
        )
        url_entry.pack(fill="x", pady=(5, 15))

        # Notas
        ttkb.Label(fields_frame, text="Notas:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        notes_text = tk.Text(fields_frame, height=6, font=("Segoe UI", 10), wrap="word")
        notes_text.pack(fill="both", expand=True, pady=(5, 0))
        if is_edit and entry["notes"]:
            notes_text.insert("1.0", entry["notes"])

        # Botões
        buttons_frame = ttkb.Frame(main_frame)
        buttons_frame.pack(fill="x")

        def save_entry():
            title_val = title_var.get().strip()
            password_val = password_var.get().strip()

            if not title_val:
                messagebox.showerror("Erro", "Título é obrigatório!")
                return

            if not password_val:
                messagebox.showerror("Erro", "Senha é obrigatória!")
                return

            notes_val = notes_text.get("1.0", "end-1c")

            try:
                if is_edit:
                    # Atualizar entrada existente
                    success = self.keepass_manager.update_entry(
                        entry["entry_object"],
                        title=title_val,
                        username=username_var.get().strip(),
                        password=password_val,
                        url=url_var.get().strip(),
                        notes=notes_val,
                    )
                else:
                    # Criar nova entrada
                    success = self.keepass_manager.add_entry(
                        title=title_val,
                        username=username_var.get().strip(),
                        password=password_val,
                        url=url_var.get().strip(),
                        notes=notes_val,
                    )

                if success:
                    editor_window.destroy()
                    self.refresh_vault_list()
                    action = "atualizada" if is_edit else "adicionada"
                    messagebox.showinfo("Sucesso", f"Entrada {action} com sucesso!")
                    self.status_bar.update_status(f"Entrada {action}")
                else:
                    messagebox.showerror("Erro", "Falha ao salvar entrada!")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

        save_btn = ttkb.Button(
            buttons_frame,
            text="💾 Salvar",
            command=save_entry,
            bootstyle="success",
            width=12,
        )
        save_btn.pack(side="left", padx=(0, 10))

        cancel_btn = ttkb.Button(
            buttons_frame,
            text="Cancelar",
            command=editor_window.destroy,
            bootstyle="secondary",
            width=10,
        )
        cancel_btn.pack(side="right")

        # Focar no primeiro campo
        title_entry.focus()

    def delete_entry(self):
        """Exclui entrada selecionada COM 2FA"""
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Aviso", "Selecione uma entrada!")
            return

        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a entrada:\n\n'{entry['title']}'?\n\nEsta ação não pode ser desfeita!",
        ):
            return

        try:
            # MUDANÇA 8: Usar verificar_apenas_2fa para exclusão
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo("Cancelado", "Exclusão cancelada pelo usuário.")
                return

            success = self.keepass_manager.delete_entry(entry["entry_object"])

            if success:
                self.refresh_vault_list()
                messagebox.showinfo("Sucesso", "Entrada excluída com sucesso!")
                self.status_bar.update_status("Entrada excluída")
            else:
                messagebox.showerror("Erro", "Falha ao excluir entrada!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir entrada: {str(e)}")

    def backup_vault(self):
        """Faz backup do cofre COM 2FA"""
        try:
            # MUDANÇA 9: Usar verificar_apenas_2fa para backup
            if not verificar_apenas_2fa(self.tab_frame):
                messagebox.showinfo("Cancelado", "Backup cancelado pelo usuário.")
                return

            backup_path = filedialog.asksaveasfilename(
                title="Salvar Backup do Cofre",
                defaultextension=".kdbx",
                filetypes=[("KeePass Database", "*.kdbx"), ("All files", "*.*")],
            )

            if not backup_path:
                return

            success = self.keepass_manager.backup_database(backup_path)

            if success:
                messagebox.showinfo("Backup", f"Backup salvo em:\n{backup_path}")
                self.status_bar.update_status("Backup realizado com sucesso")
            else:
                messagebox.showerror("Erro", "Falha ao criar backup!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {str(e)}")

    def lock_vault(self):
        """Trava o cofre"""
        if messagebox.askyesno(
            "Confirmar",
            "Deseja trancar o cofre?\n\nVocê precisará inserir a senha novamente para acessá-lo.",
        ):
            self.keepass_manager.close_database()

            # Limpar lista
            for item in self.vault_tree.get_children():
                self.vault_tree.delete(item)

            self.current_entries = []
            self.status_bar.update_entries_count("Cofre trancado")
            self.status_bar.update_status("Cofre trancado com segurança")

    def sort_by_column(self, column):
        """Ordena por coluna"""
        # Implementação básica de ordenação
        items = [
            (self.vault_tree.set(k, column), k)
            for k in self.vault_tree.get_children("")
        ]
        items.sort()

        for index, (val, k) in enumerate(items):
            self.vault_tree.move(k, "", index)
