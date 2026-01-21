# ✅ Correção: Erro de Thread no Flask

## 🐛 Problema Encontrado

Quando executava o `.exe`, aparecia o erro:

```
ValueError: signal only works in main thread of the main interpreter
```

### Causa do Problema:

O Flask estava configurado para rodar com:
- `debug=True` 
- Em uma **thread separada** (via `threading.Thread`)

O problema é que o **reloader do Werkzeug** (usado no modo debug) precisa rodar na **thread principal**, não em uma thread separada. Isso causa o erro de `signal`.

---

## ✅ Solução Implementada

### Mudança no código:

**Antes:**
```python
def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=True)  # ❌ Sempre debug=True

# Em thread separada
threading.Thread(target=run_flask, daemon=True).start()  # ❌ Thread + debug = erro
```

**Depois:**
```python
def run_flask(debug=False, use_reloader=False):
    """Inicia o servidor Flask"""
    app.run(host='127.0.0.1', port=5000, debug=debug, use_reloader=use_reloader)

# Modo executável: SEM debug (seguro para thread)
if is_executable:
    threading.Thread(target=run_flask, args=(False, False), daemon=True).start()  # ✅ OK

# Modo desenvolvimento: COM debug (thread principal)
else:
    run_flask(debug=True, use_reloader=True)  # ✅ Thread principal = OK
```

---

## 📋 Explicação da Solução

### Modo Executável:
- ✅ `debug=False` - Desabilita modo debug
- ✅ `use_reloader=False` - Desabilita reloader automático
- ✅ Pode rodar em thread separada sem problemas
- ✅ Performance melhor (sem overhead do debug)

### Modo Desenvolvimento:
- ✅ `debug=True` - Mantém modo debug
- ✅ `use_reloader=True` - Mantém reloader automático
- ✅ Roda na thread principal (seguro)
- ✅ Hot-reload funciona (atualiza código automaticamente)

---

## 🧪 Como Testar

### 1. Teste o executável:
```batch
cd dist
Gerente_de_Pacientes.exe
```

**Resultado esperado:**
- ✅ Janela informativa aparece
- ✅ Clique OK
- ✅ Navegador abre automaticamente
- ✅ Sistema funciona normalmente
- ✅ **SEM erros no console**

### 2. Teste em modo desenvolvimento:
```batch
python main.py
```

**Resultado esperado:**
- ✅ Flask inicia com debug
- ✅ Hot-reload funciona
- ✅ Mensagens de debug aparecem
- ✅ Modificação nos arquivos recarrega automaticamente

---

## 🎯 Vantagens da Correção

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Executável** | ❌ Erro de thread | ✅ Funciona perfeitamente |
| **Desenvolvimento** | ✅ Funcionava | ✅ Continua funcionando |
| **Debug no .exe** | ⚠️ Tentava usar (erro) | ✅ Desabilitado (correto) |
| **Performance** | ⚠️ Tentava debug | ✅ Sem overhead |

---

## 📝 Notas Importantes

### Por que não usar debug no executável?

1. **Performance:** Modo debug é mais lento
2. **Segurança:** Não é necessário em produção
3. **Threading:** Reloader não funciona em threads
4. **Estabilidade:** Melhor para usuários finais

### Modo Debug vs Produção:

- **Desenvolvimento:** Use `python main.py` (com debug)
- **Distribuição:** Use `.exe` (sem debug, mais rápido)

---

## 🔄 Se Precisar Habilitar Debug no .exe

Se por algum motivo você precisar de debug no executável (não recomendado):

1. Edite `main.py`
2. Mude para rodar Flask na thread principal:

```python
if is_executable:
    # AVISO: Não use isso em produção!
    run_flask(debug=True, use_reloader=False)  # Thread principal
```

**⚠️ Não recomendado:** Debug torna o app mais lento e menos estável.

---

## ✅ Status

- ✅ Problema identificado
- ✅ Correção implementada
- ✅ Executável recriado
- ✅ Pronto para testar

---

**Data da correção:** Janeiro 2026  
**Versão:** 1.0.1 (correção de threading)
