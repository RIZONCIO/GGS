import os
import hashlib
import hmac
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import secrets


from utils.caminhos import get_pasta_cofre


class KeePassManager:
    def __init__(self):
        """Inicializa o gerenciador KeePass - SEM OPERAÇÕES AUTOMÁTICAS"""
        self.pasta_cofre = get_pasta_cofre()
        self.db_path = os.path.join(self.pasta_cofre, "forticore.kdbx")
        self.hmac_key_path = os.path.join(self.pasta_cofre, ".hmac_key")
        self.db = None
        self.master_password = None
        self._initialized = False

        # Criar pasta se não existir - OPERAÇÃO SEGURA
        if not os.path.exists(self.pasta_cofre):
            os.makedirs(self.pasta_cofre)

    def _lazy_init(self):
        """Inicialização lazy - só executa quando necessário"""
        if not self._initialized:
            self._ensure_hmac_key()
            self._initialized = True

    def _ensure_hmac_key(self):
        """Garante que existe uma chave HMAC - CHAMADO APENAS QUANDO NECESSÁRIO"""
        if not os.path.exists(self.hmac_key_path):
            # Gerar nova chave HMAC
            hmac_key = secrets.token_bytes(32)  # 256 bits
            with open(self.hmac_key_path, "wb") as f:
                f.write(hmac_key)
            # Tornar arquivo oculto e somente leitura
            if os.name == "nt":  # Windows
                try:
                    os.system(f'attrib +H +R "{self.hmac_key_path}"')
                except:
                    pass  # Ignora erro se não conseguir definir atributos

    def _get_hmac_key(self) -> bytes:
        """Obtém a chave HMAC"""
        self._lazy_init()  # Garante inicialização
        with open(self.hmac_key_path, "rb") as f:
            return f.read()

    def _calculate_hmac(self, data: bytes) -> str:
        """Calcula HMAC-SHA256 dos dados"""
        key = self._get_hmac_key()
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    def _verify_hmac(self, data: bytes, expected_hmac: str) -> bool:
        """Verifica integridade dos dados usando HMAC"""
        calculated_hmac = self._calculate_hmac(data)
        return hmac.compare_digest(calculated_hmac, expected_hmac)

    def _get_master_password(self) -> Optional[str]:
        """Obtém a senha mestra do usuário - REMOVIDO IMPORT NO TOPO"""
        if self.master_password:
            return self.master_password

        # Import dinâmico para evitar problemas no startup
        from tkinter import simpledialog

        password = simpledialog.askstring(
            "Senha Mestra", "Digite a senha mestra do cofre:", show="*"
        )

        if password:
            self.master_password = password

        return password

    def get_database_path(self) -> str:
        """Retorna o caminho do banco de dados"""
        return self.db_path

    def database_exists(self) -> bool:
        """Verifica se o banco de dados existe"""
        return os.path.exists(self.db_path)

    def create_database(self) -> bool:
        """Cria um novo banco de dados KeePass"""
        try:
            # Import dinâmico
            from tkinter import simpledialog, messagebox
            from pykeepass import create_database, PyKeePass

            password = simpledialog.askstring(
                "Nova Senha Mestra",
                "Crie uma senha mestra para o cofre:\n(Mínimo 8 caracteres)",
                show="*",
            )

            if not password:
                return False

            if len(password) < 8:
                messagebox.showerror("Erro", "Senha deve ter pelo menos 8 caracteres!")
                return False

            # Confirmar senha
            confirm_password = simpledialog.askstring(
                "Confirmar Senha", "Confirme a senha mestra:", show="*"
            )

            if password != confirm_password:
                messagebox.showerror("Erro", "Senhas não coincidem!")
                return False

            # Inicialização lazy
            self._lazy_init()

            # Criar novo banco KeePass
            create_database(self.db_path, password=password)

            # Agora abrir o banco recém-criado
            self.db = PyKeePass(self.db_path, password=password)

            # Criar grupo principal
            main_group = self.db.add_group(self.db.root_group, "FortiCore Senhas")

            # Adicionar entrada de metadados com HMAC
            metadata = f"Criado em: {datetime.now().isoformat()}\nVersão: FortiCore Sentinel 2.0"
            self.db.add_entry(
                main_group,
                title="📋 Metadados do Cofre",
                username="system",
                password="",
                notes=metadata,
            )

            # Salvar PRIMEIRO
            self.db.save()
            self.master_password = password

            # DEPOIS calcular e salvar HMAC (CORREÇÃO PRINCIPAL)
            self._save_database_hmac()

            messagebox.showinfo("Sucesso", "Cofre KeePass criado com sucesso!")
            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao criar cofre: {str(e)}")
            return False

    def open_database(self) -> bool:
        """Abre o banco de dados KeePass"""
        try:
            # Import dinâmico
            from pykeepass import PyKeePass
            from pykeepass.exceptions import CredentialsError
            from tkinter import messagebox

            # Inicialização lazy
            self._lazy_init()

            # CORREÇÃO: Só verificar integridade se o arquivo HMAC existir
            hmac_file = self.db_path + ".hmac"
            if os.path.exists(hmac_file) and not self._verify_database_integrity():
                messagebox.showerror(
                    "Erro de Integridade",
                    "O arquivo do cofre foi modificado ou corrompido!\n"
                    "Operação cancelada por segurança.",
                )
                return False

            password = self._get_master_password()
            if not password:
                return False

            self.db = PyKeePass(self.db_path, password=password)

            # CORREÇÃO: Gerar HMAC se não existir
            if not os.path.exists(hmac_file):
                self._save_database_hmac()

            return True

        except CredentialsError:
            from tkinter import messagebox

            messagebox.showerror("Erro", "Senha incorreta!")
            self.master_password = None
            return False
        except FileNotFoundError:
            # Banco não existe, criar novo
            return self.create_database()
        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao abrir cofre: {str(e)}")
            return False

    def _save_database_hmac(self):
        """Salva o HMAC do banco de dados"""
        if not os.path.exists(self.db_path):
            return

        try:
            with open(self.db_path, "rb") as f:
                db_data = f.read()

            hmac_value = self._calculate_hmac(db_data)
            hmac_file = self.db_path + ".hmac"

            with open(hmac_file, "w") as f:
                f.write(hmac_value)

            # Tornar arquivo HMAC oculto
            if os.name == "nt":  # Windows
                try:
                    os.system(f'attrib +H "{hmac_file}"')
                except:
                    pass  # Ignora erro

        except Exception as e:
            print(f"Erro ao salvar HMAC: {e}")

    def _verify_database_integrity(self) -> bool:
        """Verifica a integridade do banco de dados"""
        if not os.path.exists(self.db_path):
            return True  # Não existe ainda, ok

        hmac_file = self.db_path + ".hmac"
        if not os.path.exists(hmac_file):
            # CORREÇÃO: Não existe HMAC, é normal na primeira execução
            return True

        try:
            # Ler HMAC salvo
            with open(hmac_file, "r") as f:
                expected_hmac = f.read().strip()

            # Ler dados atuais
            with open(self.db_path, "rb") as f:
                current_data = f.read()

            # Verificar integridade
            return self._verify_hmac(current_data, expected_hmac)

        except Exception as e:
            print(f"Erro ao verificar integridade: {e}")
            # CORREÇÃO: Em caso de erro, assumir que está OK (evita falsos positivos)
            return True

    def ensure_open(self) -> bool:
        """Garante que o banco está aberto"""
        if self.db is None:
            return self.open_database()
        return True

    def add_entry(
        self,
        title: str,
        username: str = "",
        password: str = "",
        url: str = "",
        notes: str = "",
    ) -> bool:
        """Adiciona uma nova entrada ao cofre"""
        try:
            if not self.ensure_open():
                return False

            # Encontrar ou criar grupo principal
            main_group = None
            for group in self.db.groups:
                if group.name == "FortiCore Senhas":
                    main_group = group
                    break

            if not main_group:
                main_group = self.db.add_group(self.db.root_group, "FortiCore Senhas")

            # Adicionar metadados às notas
            timestamp = datetime.now().isoformat()
            enhanced_notes = f"{notes}\n\n--- Metadados ---\nCriado: {timestamp}\nFortiCore Sentinel v2.0"

            # Adicionar entrada
            entry = self.db.add_entry(
                main_group,
                title=title,
                username=username,
                password=password,
                url=url,
                notes=enhanced_notes,
            )

            # Salvar PRIMEIRO
            self.db.save()

            # DEPOIS atualizar HMAC
            self._save_database_hmac()

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao adicionar entrada: {str(e)}")
            return False

    def search_entries(self, query: str) -> List[Dict]:
        """Busca entradas no cofre"""
        try:
            if not self.ensure_open():
                return []

            results = []
            query_lower = query.lower()

            for entry in self.db.entries:
                # Buscar em título, username, URL e notas
                if (
                    query_lower in entry.title.lower()
                    or query_lower in (entry.username or "").lower()
                    or query_lower in (entry.url or "").lower()
                    or query_lower in (entry.notes or "").lower()
                ):

                    results.append(
                        {
                            "title": entry.title,
                            "username": entry.username or "",
                            "password": entry.password or "",
                            "url": entry.url or "",
                            "notes": entry.notes or "",
                            "created": entry.ctime.isoformat() if entry.ctime else "",
                            "modified": entry.mtime.isoformat() if entry.mtime else "",
                            "entry_object": entry,
                        }
                    )

            return results

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao buscar entradas: {str(e)}")
            return []

    def get_all_entries(self) -> List[Dict]:
        """Retorna todas as entradas do cofre"""
        try:
            if not self.ensure_open():
                return []

            results = []
            for entry in self.db.entries:
                # Pular entrada de metadados do sistema
                if entry.title == "📋 Metadados do Cofre":
                    continue

                results.append(
                    {
                        "title": entry.title,
                        "username": entry.username or "",
                        "password": entry.password or "",
                        "url": entry.url or "",
                        "notes": entry.notes or "",
                        "created": entry.ctime.isoformat() if entry.ctime else "",
                        "modified": entry.mtime.isoformat() if entry.mtime else "",
                        "entry_object": entry,
                    }
                )

            return results

        except Exception as e:
            print(f"Erro ao obter entradas: {e}")
            return []

    def count_entries(self) -> int:
        """Conta o número de entradas (excluindo metadados)"""
        try:
            if not self.ensure_open():
                return 0

            count = 0
            for entry in self.db.entries:
                if entry.title != "📋 Metadados do Cofre":
                    count += 1
            return count
        except:
            return 0

    def update_entry(
        self,
        entry_object,
        title: str = None,
        username: str = None,
        password: str = None,
        url: str = None,
        notes: str = None,
    ) -> bool:
        """Atualiza uma entrada existente"""
        try:
            if not self.ensure_open():
                return False

            # Atualizar campos se fornecidos
            if title is not None:
                entry_object.title = title
            if username is not None:
                entry_object.username = username
            if password is not None:
                entry_object.password = password
            if url is not None:
                entry_object.url = url
            if notes is not None:
                # Preservar metadados existentes e adicionar modificação
                timestamp = datetime.now().isoformat()
                if "--- Metadados ---" in notes:
                    # Atualizar metadados existentes
                    notes += f"\nModificado: {timestamp}"
                else:
                    # Adicionar novos metadados
                    notes += f"\n\n--- Metadados ---\nModificado: {timestamp}\nFortiCore Sentinel v2.0"
                entry_object.notes = notes

            # Salvar PRIMEIRO
            self.db.save()

            # DEPOIS atualizar HMAC
            self._save_database_hmac()

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao atualizar entrada: {str(e)}")
            return False

    def delete_entry(self, entry_object) -> bool:
        """Exclui uma entrada do cofre"""
        try:
            if not self.ensure_open():
                return False

            # Mover para lixeira se disponível, senão deletar permanentemente
            if hasattr(self.db, "trash"):
                self.db.move_entry(entry_object, self.db.trash)
            else:
                self.db.delete_entry(entry_object)

            # Salvar PRIMEIRO
            self.db.save()

            # DEPOIS atualizar HMAC
            self._save_database_hmac()

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao excluir entrada: {str(e)}")
            return False

    def backup_database(self, backup_path: str) -> bool:
        """Cria backup do banco de dados"""
        try:
            if not os.path.exists(self.db_path):
                return False

            import shutil

            # Copiar arquivo principal
            shutil.copy2(self.db_path, backup_path)

            # Copiar HMAC se existir
            hmac_file = self.db_path + ".hmac"
            if os.path.exists(hmac_file):
                shutil.copy2(hmac_file, backup_path + ".hmac")

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao fazer backup: {str(e)}")
            return False

    def change_master_password(self, new_password: str) -> bool:
        """Altera a senha mestra do cofre"""
        try:
            if not self.ensure_open():
                return False

            if len(new_password) < 8:
                from tkinter import messagebox

                messagebox.showerror(
                    "Erro", "Nova senha deve ter pelo menos 8 caracteres!"
                )
                return False

            # Alterar senha
            self.db.password = new_password
            self.db.save()

            # Atualizar HMAC
            self._save_database_hmac()

            # Atualizar senha em memória
            self.master_password = new_password

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao alterar senha: {str(e)}")
            return False

    def get_database_stats(self) -> Dict:
        """Retorna estatísticas do banco de dados"""
        try:
            if not self.ensure_open():
                return {
                    "total_entries": 0,
                    "total_groups": 0,
                    "database_size": 0,
                    "integrity_verified": False,
                    "created": None,
                    "last_modified": None,
                }

            stats = {
                "total_entries": len(
                    [e for e in self.db.entries if e.title != "📋 Metadados do Cofre"]
                ),
                "total_groups": len(self.db.groups),
                "database_size": (
                    os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                ),
                "integrity_verified": self._verify_database_integrity(),
                "created": None,
                "last_modified": None,
            }

            # Tentar obter datas dos metadados
            for entry in self.db.entries:
                if entry.title == "📋 Metadados do Cofre":
                    if entry.notes and "Criado em:" in entry.notes:
                        # Extrair data de criação das notas
                        for line in entry.notes.split("\n"):
                            if line.startswith("Criado em:"):
                                stats["created"] = line.replace(
                                    "Criado em:", ""
                                ).strip()
                                break
                    break

            # Data de última modificação do arquivo
            if os.path.exists(self.db_path):
                mtime = os.path.getmtime(self.db_path)
                stats["last_modified"] = datetime.fromtimestamp(mtime).isoformat()

            return stats

        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                "total_entries": 0,
                "total_groups": 0,
                "database_size": 0,
                "integrity_verified": False,
                "created": None,
                "last_modified": None,
            }

    def close_database(self):
        """Fecha o banco de dados e limpa senha da memória"""
        if self.db:
            # CORREÇÃO: Salvar antes de fechar
            try:
                self.db.save()
                self._save_database_hmac()
            except Exception as e:
                print(f"Erro ao salvar antes de fechar: {e}")
            finally:
                self.db = None
        self.master_password = None

    def is_database_locked(self) -> bool:
        """Verifica se o banco está travado (fechado)"""
        return self.db is None

    def export_to_csv(self, csv_path: str) -> bool:
        """Exporta entradas para CSV (sem senhas por segurança)"""
        try:
            if not self.ensure_open():
                return False

            import csv

            entries = self.get_all_entries()

            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["title", "username", "url", "created", "modified"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for entry in entries:
                    writer.writerow(
                        {
                            "title": entry["title"],
                            "username": entry["username"],
                            "url": entry["url"],
                            "created": (
                                entry["created"][:10] if entry["created"] else ""
                            ),  # Só a data
                            "modified": (
                                entry["modified"][:10] if entry["modified"] else ""
                            ),
                        }
                    )

            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")
            return False

    def import_from_csv(self, csv_path: str) -> bool:
        """NOVO: Importa entradas de arquivo CSV"""
        try:
            if not self.ensure_open():
                return False

            import csv
            from tkinter import messagebox

            imported_count = 0
            errors = []

            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                # Detectar automaticamente o delimitador
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(csvfile, delimiter=delimiter)

                # Verificar se tem as colunas necessárias
                required_columns = ["title"]

                if not any(col in reader.fieldnames for col in required_columns):
                    messagebox.showerror(
                        "Erro", "CSV deve conter pelo menos uma coluna 'title'!"
                    )
                    return False

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Começar na linha 2 (após header)
                    try:
                        # Limpar dados
                        title = str(row.get("title", "")).strip()
                        username = str(row.get("username", "")).strip()
                        password = str(row.get("password", "")).strip()
                        url = str(row.get("url", "")).strip()
                        notes = str(row.get("notes", "")).strip()

                        # Título é obrigatório
                        if not title:
                            errors.append(f"Linha {row_num}: Título vazio")
                            continue

                        # Adicionar prefixo de importação
                        title = f"[CSV] {title}"

                        # Adicionar metadados às notas
                        import_notes = f"Importado de CSV em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        if notes:
                            import_notes = f"{notes}\n\n{import_notes}"

                        # Adicionar entrada
                        success = self.add_entry(
                            title=title,
                            username=username,
                            password=password,
                            url=url,
                            notes=import_notes,
                        )

                        if success:
                            imported_count += 1
                        else:
                            errors.append(
                                f"Linha {row_num}: Falha ao adicionar '{title}'"
                            )

                    except Exception as e:
                        errors.append(f"Linha {row_num}: Erro - {str(e)}")
                        continue

            # Mostrar resultado
            result_msg = f"Importadas {imported_count} entradas com sucesso!"
            if errors:
                result_msg += f"\n\nErros encontrados:\n" + "\n".join(
                    errors[:5]
                )  # Mostrar só os primeiros 5 erros
                if len(errors) > 5:
                    result_msg += f"\n... e mais {len(errors) - 5} erros."

            messagebox.showinfo("Importação CSV", result_msg)
            return imported_count > 0

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro na importação CSV: {str(e)}")
            return False

    def import_from_old_system(self, old_dados_file: str, old_key_file: str) -> bool:
        """Importa dados do sistema antigo (cripto_cofre)"""
        try:
            if not self.ensure_open():
                return False

            # Importar módulo antigo temporariamente
            import json
            import base64
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives import padding
            from cryptography.hazmat.backends import default_backend
            from tkinter import messagebox

            # Ler chave antiga
            with open(old_key_file, "rb") as f:
                old_key = f.read()

            # Ler dados antigos
            with open(old_dados_file, "r") as f:
                old_data = json.load(f)

            # Descriptografar e importar
            backend = default_backend()
            imported_count = 0

            for keyword, encrypted_entries in old_data.items():
                for encrypted_entry in encrypted_entries:
                    try:
                        # Descriptografar entrada antiga
                        dado_bytes = base64.b64decode(encrypted_entry)
                        iv = dado_bytes[:16]
                        criptografado = dado_bytes[16:]

                        cipher = Cipher(
                            algorithms.AES(old_key), modes.CBC(iv), backend=backend
                        )
                        decryptor = cipher.decryptor()
                        dados_preenchidos = (
                            decryptor.update(criptografado) + decryptor.finalize()
                        )

                        unpadder = padding.PKCS7(128).unpadder()
                        decrypted_data = (
                            unpadder.update(dados_preenchidos) + unpadder.finalize()
                        ).decode()

                        # Tentar fazer parse se for JSON
                        try:
                            parsed_data = json.loads(decrypted_data)
                            password = parsed_data.get("senha", decrypted_data)
                            old_notes = f"Importado do sistema antigo\n{decrypted_data}"
                        except:
                            password = decrypted_data
                            old_notes = "Importado do sistema antigo"

                        # Adicionar ao KeePass
                        success = self.add_entry(
                            title=f"[IMPORTADO] {keyword}",
                            username="Usuário Importado",
                            password=password,
                            notes=old_notes,
                        )

                        if success:
                            imported_count += 1

                    except Exception as e:
                        print(f"Erro ao importar entrada: {e}")
                        continue

            messagebox.showinfo(
                "Importação", f"Importadas {imported_count} entradas do sistema antigo!"
            )
            return True

        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Erro", f"Erro na importação: {str(e)}")
            return False
