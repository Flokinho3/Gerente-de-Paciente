@echo off
chcp 65001 >nul
echo ========================================
echo   Criando executável Gerente.exe
echo ========================================
echo.

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Executando PyInstaller...
pyinstaller build_gerente.spec --clean --noconfirm

echo.
if exist dist\Gerente.exe (
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo.
    echo Executável criado em: dist\Gerente.exe
    echo.
    echo Tamanho aproximado: 
    dir dist\Gerente.exe | find "Gerente.exe"
    echo.
    pause
) else (
    echo ========================================
    echo   ERRO: Executável não foi criado
    echo ========================================
    echo.
    echo Verifique os erros acima.
    pause
    exit /b 1
)
