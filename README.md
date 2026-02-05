# Gerente de Pacientes (v0.0.6)

Sistema completo de gestão de pacientes com sincronização automática com VPS, interface web e desktop, e recursos avançados de backup e exportação.

## 🚀 Visão Geral

O Gerente de Pacientes é uma aplicação robusta desenvolvida para clínicas e consultórios médicos. O sistema foi projetado para operar de forma híbrida (Online/Offline), mantendo os dados locais sincronizados com um servidor central (VPS) e garantindo a integridade das informações mesmo em caso de falha de conexão.

### Diferenciais desta Versão (v0.0.6):
- **Projeto Limpo**: Estrutura otimizada que mantém a raiz do projeto organizada, movendo arquivos de dados e logs para a pasta `data/`.
- **Launcher Inteligente**: O inicializador gerencia atualizações automaticamente, limpando arquivos temporários e ZIPs após a instalação.
- **Resiliência de Dados**: Tratamento avançado de erros em APIs e camadas de banco de dados (Data Hardening) para evitar falhas por payloads malformados.
- **Sincronização VPS**: Sincronização em tempo real de pacientes e agendamentos com tratamento de conflitos.

---

## 📋 Funcionalidades Principais

### 👥 Gerenciamento de Pacientes
- Cadastro completo com informações pessoais, identificação e avaliações.
- Busca inteligente e filtragem avançada.
- Histórico clínico detalhado.
- Exportação para relatórios profissionais (Excel, Word).

### 📅 Agendamentos
- Gestão de consultas com visualização clara.
- Sincronização automática de horários entre diferentes unidades através da VPS.
- Gestão de disponibilidade e lembretes.

### 🔄 Sincronização Inteligente
- Sincronização agendada (padrão 10 min) ou manual.
- Verificação de itens pendentes antes de subir para a nuvem.
- Logs detalhados de cada operação de sincronia em `data/updates/launcher.log`.

### 💾 Backup e Segurança
- Sistema de backup local e restauração simplificada.
- Integridade de banco de dados SQLite com modo WAL habilitado para melhor performance.
- Identificador único de instalação (PC_ID) para rastreabilidade de alterações.

---

## 🏗️ Arquitetura e Estrutura

### Organização do Projeto
```text
Gerente-de-Paciente/
├── data/                       # PASTA ESSENCIAL (Manter backup desta pasta!)
│   ├── pacientes.db            # Banco de dados SQLite local
│   ├── version.json            # Metadados de versão da aplicação
│   ├── .pc_id                  # Identificador único da instalação
│   └── updates/                # Logs e históricos de atualização
├── gerente/                    # Core da aplicação
│   ├── flask_app/              # Rotas API e lógica do servidor Web
│   ├── database/               # Camada de persistência modular
│   ├── inicio/                 # Utilitários de inicialização (Rede, Tray, etc)
│   ├── static/                 # CSS, JS e Imagens da interface
│   ├── templates/              # HTML estrutural (Jinja2)
│   ├── launcher.py             # Lógica de atualização e inicialização
│   └── config.py               # Centralizador de caminhos e configurações
├── main.py                     # Ponto de entrada (Boot do sistema)
├── .env                        # Variáveis de ambiente sensíveis
└── requirements.txt            # Dependências do projeto
```

### Stack Tecnológica
- **Backend**: Python 3.10+ / Flask
- **Servidor de Produção**: Waitress
- **Banco de Dados**: SQLite (Local) / Sincronia via REST API
- **Empacotamento**: PyInstaller
- **Interface Desktop**: PyStray (System Tray) / Tkinter (Alertas)

---

## 🌐 API Endpoints (Principais)

### Pacientes
- `GET /api/pacientes` - Lista pacientes com filtros (nome, unidade)
- `POST /api/salvar_paciente` - Cria novo paciente e inicia sync em background
- `PUT /api/atualizar_paciente/<id>` - Atualiza dados do paciente
- `DELETE /api/deletar_paciente/<id>` - Remove o paciente localmente

### Sincronização (VPS)
- `POST /api/vps/sync/executar` - Executa sincronização manual imediata
- `GET /api/vps/sync/status` - Retorna o estado atual da sincronia e itens pendentes

---

## 🛠️ Configuração e Instalação

### Requisitos de Ambiente
1. **Python 3.10**: Recomendado para garantir compatibilidade com as bibliotecas de sistema.
2. **Ambiente Virtual**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Variáveis de Ambiente (.env)
O arquivo `.env` deve estar na **raiz do projeto**:
```env
PORT=5000                    # Porta principal
FLASK_DEBUG=false            # Ativa logs estendidos e console
USE_TRAY=1                   # 1 para ícone na barra de tarefas, 0 para apenas terminal
VPS_URL=https://api.vps.com  # URL do servidor central
VPS_PASSWORD=****            # Senha de autenticação da sincronia
```

---

## 🚀 Execução e Build

### Modo Desenvolvedor
Para rodar a aplicação via código fonte:
```bash
python main.py
```

### Geração de Executáveis (Build)
O projeto agora utiliza um sistema de build centralizado na pasta `Scripts/`:
1. Execute `python Scripts/build_all.py` na raiz do projeto.
2. O script irá limpar builds anteriores e compilar `Gerente.exe` e `Launcher.exe` usando os arquivos `.spec` da raiz.
3. Após o build, um arquivo ZIP `GerenteApp_{versao}.zip` será gerado automaticamente na raiz.
4. O hash de integridade será salvo em `sha256.txt`.

---

## 📞 Suporte e Manutenção

- **Caminho dos Logs**: Confira sempre `data/updates/launcher.log` em caso de erros na inicialização.
- **Banco de Dados**: O arquivo `data/pacientes.db` é o coração do sistema. Nunca o exclua sem ter um backup.
- **Atualizações**: O Launcher verifica automaticamente novos releases no GitHub conforme configurado no template de versão.

---
**Status atual**: Operacional (v0.0.6)
**Última atualização**: Fevereiro 2026