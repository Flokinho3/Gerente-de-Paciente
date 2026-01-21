@echo off
echo ========================================
echo   Gerente de Pacientes - Build .exe
echo ========================================
echo.

REM Verificar se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERRO] PyInstaller nao encontrado!
    echo Instalando PyInstaller...
    pip install pyinstaller
    echo.
)

REM Limpar builds anteriores
echo [1/4] Limpando builds anteriores...
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist
echo Concluido!
echo.

REM Criar o executável
echo [2/4] Criando executavel com PyInstaller...
echo Isso pode levar alguns minutos...
pyinstaller gerente_pacientes.spec --clean --noconfirm
echo Concluido!
echo.

REM Verificar se foi criado com sucesso
if exist "dist\Gerente_de_Pacientes.exe" (
    echo [3/4] Executavel criado com sucesso!
    echo.
    
    REM Copiar pasta data se existir
    if exist "data" (
        echo [4/4] Copiando banco de dados...
        xcopy /E /I /Y data dist\data
        echo Concluido!
    ) else (
        echo [4/4] Criando pasta data...
        mkdir dist\data
        echo Concluido!
    )
    
    echo.
    echo ========================================
    echo   BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    echo Localizacao do executavel:
    echo   %cd%\dist\Gerente_de_Pacientes.exe
    echo.
    echo Tamanho aproximado: ~25-30 MB
    echo.
    echo Para executar:
    echo   1. Va ate a pasta 'dist'
    echo   2. Execute: Gerente_de_Pacientes.exe
    echo   3. O navegador abrira automaticamente
    echo.
) else (
    echo.
    echo [ERRO] Falha ao criar o executavel!
    echo Verifique os erros acima.
    echo.
)

pause
