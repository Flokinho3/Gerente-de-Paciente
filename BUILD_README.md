# Como criar o executável Gerente.exe

## Método 1: Usando o arquivo .bat (Windows)

1. Clique duas vezes em `build_gerente.bat`
2. Aguarde o processo terminar
3. O executável estará em: `dist\Gerente.exe`

## Método 2: Usando o script Python

Execute no terminal:
```bash
python build_gerente.py
```

## Método 3: Usando PyInstaller diretamente

Execute no terminal:
```bash
pyinstaller build_gerente.spec --clean --noconfirm
```

## O que está incluído no executável

- Todos os templates HTML
- Todos os arquivos estáticos (CSS, JS, imagens)
- Pasta `data` (para o banco de dados)
- Todas as dependências Python necessárias

## Requisitos

- Python instalado
- PyInstaller instalado (`pip install pyinstaller`)
- Todas as dependências do `requirements.txt` instaladas

## Após criar o executável

O arquivo `Gerente.exe` estará na pasta `dist`. Você pode:
- Copiar apenas o `.exe` (tudo está incluído)
- Executar diretamente (abrirá o navegador automaticamente)

## Tamanho aproximado

O executável terá aproximadamente 25-30 MB, dependendo das dependências.
