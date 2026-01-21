# Gerente de Pacientes - Executável

## Como usar o executável

O executável `Gerente_de_Pacientes` foi criado usando PyInstaller e contém toda a aplicação web de gerenciamento de pacientes em um único arquivo.

### Instruções de uso:

1. **Localização**: O executável está localizado em `dist/Gerente_de_Pacientes`

2. **Execução**:
   ```bash
   cd dist
   ./Gerente_de_Pacientes
   ```

3. **Acesso à aplicação**:
   - Abra seu navegador web
   - Acesse: `http://localhost:5000`
   - A aplicação iniciará automaticamente no navegador

### Funcionalidades incluídas:

- ✅ Gerenciamento completo de pacientes
- ✅ Interface web responsiva
- ✅ Banco de dados SQLite integrado
- ✅ Exportação para Excel (.xlsx)
- ✅ Exportação para Word (.docx)
- ✅ Exportação para texto (.txt)
- ✅ Estatísticas e indicadores
- ✅ Backup e restauração de dados

### Requisitos do sistema:

- Sistema operacional Linux (64-bit)
- Não requer instalação de Python ou dependências adicionais
- O executável é totalmente autocontido

### Arquivos criados:

- `Gerente_de_Pacientes` - Executável principal (20MB)
- `gerente_pacientes.spec` - Arquivo de configuração do PyInstaller
- `requirements.txt` - Lista de dependências

### Notas importantes:

- O executável cria uma pasta `data/` automaticamente para armazenar o banco de dados
- Todos os arquivos de template e static são incluídos no executável
- A aplicação roda em modo debug para desenvolvimento
- Pressione Ctrl+C no terminal para parar a aplicação

### Solução de problemas:

Se o executável não iniciar:
1. Verifique se tem permissões de execução: `chmod +x Gerente_de_Pacientes`
2. Certifique-se de que a porta 5000 não está em uso
3. Execute em um terminal com suporte a interface gráfica (para o Tkinter)

---

**Desenvolvido para transformar aplicações Python em executáveis totalmente portáteis!**