# 🛡️ FortiCore Sentinel v2.0

**Gerador de Senhas Seguras & Cofre KeePass com 2FA**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![KeePass](https://img.shields.io/badge/Format-KeePass_KDBX-orange.svg)](https://keepass.info)

## 📋 Sobre o Projeto

FortiCore Sentinel é uma aplicação de segurança que combina geração criptográfica de senhas com um cofre seguro baseado no formato KeePass (.kdbx). A versão 2.0 representa uma completa reformulação com foco em segurança, usabilidade e compatibilidade com padrões da indústria.

### ✨ Principais Características

- 🔐 **Banco KeePass (.kdbx)**: Formato padrão da indústria
- 🛡️ **Criptografia AES-256**: Com Argon2 KDF para derivação de chaves
- ✅ **Verificação HMAC**: Integridade dos dados garantida
- 🔒 **2FA Obrigatório**: Autenticação de dois fatores com TOTP
- 🎨 **Interface Moderna**: Design intuitivo com ttkbootstrap
- 🔄 **Compatibilidade**: Funciona com KeePass, KeePassXC e apps móveis

## 🏗️ Estrutura do Projeto

```
FortiCore-Sentinel/
├── main.py                          # Arquivo principal
├── requirements.txt                 # Dependências
├── README.md                       # Este arquivo
│
├── assets/                         # Módulos de funcionalidade
│   ├── __init__.py
│   ├── autenticacao_2fa.py        # Sistema 2FA existente
│   ├── cripto_cofre.py            # Sistema antigo (para migração)
│   └── gerador_de_senha.py        # Gerador de senhas existente
│
├── core/                          # Núcleo do sistema
│   ├── __init__.py
│   └── keepass_manager.py         # Gerenciador KeePass com HMAC
│
├── ui/                            # Interface gráfica
│   ├── __init__.py
│   ├── main_window.py             # Janela principal
│   │
│   ├── components/                # Componentes reutilizáveis
│   │   ├── __init__.py
│   │   ├── header.py              # Cabeçalho da aplicação
│   │   └── status_bar.py          # Barra de status
│   │
│   └── tabs/                      # Abas da aplicação
│       ├── __init__.py
│       ├── password_generator_tab.py  # Gerador de senhas
│       ├── vault_tab.py               # Cofre KeePass
│       ├── security_tab.py            # Configurações de segurança
│       └── about_tab.py               # Sobre o projeto
│
├── utils/                         # Utilitários
│   ├── __init__.py
│   └── caminhos.py               # Gerenciamento de caminhos (existente)
│
├── img/                          # Imagens e ícones
│   └── logo.ico                  # Ícone da aplicação
│
└── cofre/                        # Pasta de dados (criada automaticamente)
    ├── forticore.kdbx            # Banco KeePass
    ├── forticore.kdbx.hmac       # Verificação de integridade
    ├── .hmac_key                 # Chave HMAC (oculta)
    ├── chave_2fa.txt             # Chave 2FA
    └── qrcode_ja_mostrado.flag   # Flag de configuração
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/forticore-sentinel.git
cd forticore-sentinel
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a Aplicação

```bash
python main.py
```

### 4. Primeira Configuração

1. **Configurar 2FA**: Na primeira execução, será exibido um QR Code para configurar o Google Authenticator
2. **Criar Senha Mestra**: Defina uma senha forte para proteger seu cofre
3. **Começar a Usar**: Gere senhas e salve no cofre seguro!

## 🔧 Migração do Sistema Anterior

Se você já usava o FortiCore Sentinel v1.x, pode importar seus dados:

1. Abra a aba **"🔒 Segurança"**
2. Clique em **"📥 Importar Sistema Antigo"**
3. Selecione os arquivos `._dados.sjson` e `.chave_aes`
4. Seus dados serão importados para o novo formato KeePass

## 🛡️ Segurança

### Criptografia e Padrões

- **AES-256-CBC**: Criptografia de nível militar
- **Argon2 KDF**: Derivação de chave resistente a ataques
- **HMAC-SHA256**: Verificação de integridade
- **TOTP 2FA**: Autenticação de dois fatores padrão RFC 6238

### Boas Práticas Implementadas

- ✅ Dados armazenados apenas localmente
- ✅ Senhas nunca armazenadas em texto plano
- ✅ Verificação de integridade automática
- ✅ 2FA obrigatório para operações sensíveis
- ✅ Geração criptográfica segura de senhas

## 📱 Compatibilidade

### Desktop

- **KeePass 2.x** (Windows)
- **KeePassXC** (Windows, Linux, macOS)
- **MacPass** (macOS)

### Mobile

- **KeePass2Android** (Android)
- **Strongbox** (iOS)
- **KeePassium** (iOS)

## 🔄 Funcionalidades Principais

### Gerador de Senhas

- Comprimento configurável (6-50 caracteres)
- Tipos de caracteres personalizáveis
- Remoção de caracteres duplicados
- Indicador de força em tempo real

### Cofre KeePass

- Adicionar/editar/excluir entradas
- Busca avançada em tempo real
- Organização por grupos
- Notas e metadados completos

### Segurança e Backup

- Backup com verificação de integridade
- Alteração de senha mestra
- Verificação manual de integridade
- Exportação segura (sem senhas)

## 🐛 Solução de Problemas

### Erro ao Abrir Banco

- Verifique se a senha mestra está correta
- Execute verificação de integridade na aba Segurança

### 2FA Não Funciona

- Verifique se o horário do sistema está correto
- Reconfigure o 2FA se necessário

### Banco Corrompido

- Restaure do último backup
- Use a verificação HMAC para validar integridade

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/forticore-sentinel/issues)
- 📧 **Email**: seu-email@exemplo.com
- 📖 **Wiki**: [Documentação Completa](https://github.com/seu-usuario/forticore-sentinel/wiki)

## 🙏 Agradecimentos

- **KeePass**: Pela criação do formato padrão .kdbx
- **PyKeePass**: Biblioteca essencial para manipulação de bancos
- **ttkbootstrap**: Interface moderna e elegante
- **Comunidade Python**: Pelo ecossistema incrível

---

**⚠️ Aviso**: Este software é fornecido "como está". Mantenha sempre backups de seus dados e lembre-se de suas senhas mestras. Sem elas, os dados são irrecuperáveis por design de segurança.
