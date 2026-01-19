# 🖥️ Tray Icon - Inicialização Automática

O **tray icon** é iniciado **automaticamente** junto com o `main.py` sempre que possível.

## 🚀 Comportamento Padrão

### ✅ **Inicia Automaticamente** quando:
- Executável (.exe) é executado
- Modo silencioso (`--silent` ou `SILENT_MODE=1`)
- Scripts `iniciar_silencioso.sh` ou `iniciar_background.sh`
- Variável `USE_TRAY=1` está definida
- Argumento `--tray` é passado

### ❌ **Não Inicia** quando:
- Argumento `--no-tray` é passado
- `pystray` não está instalado (fallback para modo normal)

## 📋 Modos de Execução

### 1. **Execução Normal** (com tray icon automático)
```bash
python3 main.py
```
- ✅ Tenta iniciar tray icon automaticamente
- ✅ Se não disponível, roda em modo desenvolvimento normal

### 2. **Forçar Tray Icon**
```bash
python3 main.py --tray
```
- ✅ Força uso do tray icon

### 3. **Desabilitar Tray Icon**
```bash
python3 main.py --no-tray
```
- ❌ Desabilita tray icon completamente

### 4. **Modo Silencioso** (sempre com tray)
```bash
python3 main.py --silent
# ou
./iniciar_silencioso.sh
```
- ✅ Sempre usa tray icon

## 🔧 Instalação

Para garantir que o tray icon funcione:

```bash
# Instalar dependências
pip3 install pystray pillow

# Ou usar o script
./instalar_dependencias.sh
```

## 📝 Logs de Inicialização

Quando iniciado, você verá:
```
Iniciando servidor Flask na porta 5000...
✓ Servidor Flask iniciado na porta 5000
Iniciando tray icon...
```

Se o tray icon não estiver disponível:
```
⚠ pystray não instalado: ...
Instale com: pip install pystray pillow
Continuando sem tray icon...
```

## ✅ Verificação

Para verificar se o tray icon está ativo:
1. Procure o ícone na bandeja do sistema (área de notificação)
2. Clique com botão direito no ícone
3. Você verá o menu com status, porta e ações

## 🎯 Resumo

- **Padrão**: Tray icon inicia automaticamente quando possível
- **Fallback**: Se não disponível, aplicação funciona normalmente
- **Controle**: Use `--tray` para forçar ou `--no-tray` para desabilitar
