# 🚀 Execução Silenciosa - Sem Terminal Visível

Este documento explica como executar o **Gerente de Pacientes** sem abrir terminal/console visível.

## 📋 Opções de Execução

### 1. **Execução Silenciosa com Feedback** (Recomendado)
```bash
./iniciar_silencioso.sh
```
- ✅ Inicia sem terminal visível
- ✅ Mostra mensagens de status
- ✅ Abre navegador automaticamente
- ✅ Logs salvos em `logs/app.log`

### 2. **Execução Totalmente em Background**
```bash
./iniciar_background.sh
```
- ✅ Executa completamente em background
- ✅ Sem nenhuma janela visível
- ✅ Ideal para iniciar automaticamente
- ✅ Logs em `logs/app.log` e `logs/error.log`

### 3. **Parar Aplicação**
```bash
./parar.sh
```
- ✅ Encerra a aplicação em background
- ✅ Limpa arquivos PID

### 4. **Atalho Desktop** (Linux)
1. Copie `iniciar.desktop` para `~/.local/share/applications/`
2. Ou clique duas vezes no arquivo para executar
3. A aplicação iniciará sem terminal visível

## 🔧 Configuração para Windows (.exe)

O arquivo `gerente_pacientes.spec` já está configurado com `console=False`:
- ✅ Executável não mostra console
- ✅ Execução silenciosa
- ✅ Apenas janela informativa do Tkinter

Para gerar o executável:
```bash
# Windows
build_exe.bat

# Ou manualmente
pyinstaller gerente_pacientes.spec --clean --noconfirm
```

## 📁 Estrutura de Logs

```
logs/
├── app.log      # Log geral da aplicação
├── error.log    # Log de erros (apenas background)
└── app.pid      # Arquivo PID (apenas background)
```

## 🎯 Modo Desenvolvimento vs Produção

### Desenvolvimento
```bash
python3 main.py
```
- Mostra output no terminal
- Debug ativado
- Recarregamento automático

### Produção (Silencioso)
```bash
./iniciar_silencioso.sh    # Com feedback
./iniciar_background.sh    # Totalmente silencioso
```
- Sem terminal visível
- Logs em arquivo
- Execução estável

## 🔍 Verificar se Está Rodando

```bash
# Verificar processo
ps aux | grep "python3 main.py"

# Verificar porta
netstat -tuln | grep 5000

# Ver logs
tail -f logs/app.log
```

## ⚙️ Configuração Automática no Boot (Linux)

Para iniciar automaticamente ao ligar o sistema:

1. **Usando systemd** (Recomendado):
```bash
sudo nano /etc/systemd/system/gerente-pacientes.service
```

Conteúdo:
```ini
[Unit]
Description=Gerente de Pacientes
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/Gerente de Paciente
ExecStart=/caminho/para/Gerente de Paciente/iniciar_background.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl enable gerente-pacientes.service
sudo systemctl start gerente-pacientes.service
```

2. **Usando crontab**:
```bash
crontab -e
```
Adicionar:
```
@reboot /caminho/para/Gerente\ de\ Paciente/iniciar_background.sh
```

## 🛠️ Troubleshooting

### Problema: Script não executa
```bash
chmod +x iniciar_silencioso.sh iniciar_background.sh parar.sh
```

### Problema: Porta 5000 já em uso
```bash
# Encontrar processo
lsof -i :5000

# Parar processo
kill <PID>
```

### Problema: Navegador não abre
- Acesse manualmente: http://localhost:5000
- Verifique se o servidor iniciou: `tail -f logs/app.log`

## 📝 Notas Importantes

- ✅ Todos os scripts são executáveis e prontos para uso
- ✅ Logs são salvos automaticamente
- ✅ Aplicação roda em `http://localhost:5000`
- ✅ Executável Windows já configurado sem console
- ✅ Scripts Linux funcionam em qualquer distribuição
