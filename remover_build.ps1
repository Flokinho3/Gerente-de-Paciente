# Script PowerShell para remover pasta build do histórico do Git
# Execute com cuidado! Faça backup antes!

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  REMOVER BUILD DO HISTORICO DO GIT" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Perguntar confirmação
$confirm = Read-Host "Tem certeza? Isso modificara o historico! (SIM/nao)"
if ($confirm -ne "SIM") {
    Write-Host "Operacao cancelada." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "[1/5] Criando backup..." -ForegroundColor Cyan
$backupPath = "..\backup-antes-limpeza-$(Get-Date -Format 'yyyyMMdd-HHmmss').git"
git clone --mirror . $backupPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "    Backup criado em: $backupPath" -ForegroundColor Green
} else {
    Write-Host "    AVISO: Falha ao criar backup!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/5] Verificando historico da pasta build..." -ForegroundColor Cyan
$history = git log --all --full-history --oneline -- build/
if ($history) {
    Write-Host "    Encontrado no historico:" -ForegroundColor Yellow
    Write-Host $history -ForegroundColor Gray
} else {
    Write-Host "    Pasta build nao encontrada no historico!" -ForegroundColor Green
    exit
}

Write-Host ""
Write-Host "[3/5] Removendo build do historico..." -ForegroundColor Cyan
Write-Host "    Isso pode levar alguns minutos..." -ForegroundColor Yellow

# Verificar se git-filter-repo está instalado
$hasFilterRepo = Get-Command git-filter-repo -ErrorAction SilentlyContinue
if ($hasFilterRepo) {
    Write-Host "    Usando git-filter-repo (recomendado)..." -ForegroundColor Green
    git filter-repo --path build --invert-paths --force
} else {
    Write-Host "    Usando git filter-branch..." -ForegroundColor Yellow
    git filter-branch --force --index-filter "git rm -rf --cached --ignore-unmatch build" --prune-empty --tag-name-filter cat -- --all
}

Write-Host ""
Write-Host "[4/5] Limpando referencias antigas..." -ForegroundColor Cyan
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object {
    git update-ref -d $_
}
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host ""
Write-Host "[5/5] Verificando resultado..." -ForegroundColor Cyan
$newHistory = git log --all --full-history --oneline -- build/
if (-not $newHistory) {
    Write-Host "    Sucesso! Build removido do historico!" -ForegroundColor Green
} else {
    Write-Host "    AVISO: Ainda ha referencias no historico!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Verifique se tudo esta correto: git log --oneline -5" -ForegroundColor White
Write-Host "2. Se estiver tudo OK, faca force push:" -ForegroundColor White
Write-Host "   git push origin main --force-with-lease" -ForegroundColor Yellow
Write-Host ""
Write-Host "ATENCAO: Force push reescreve o historico remoto!" -ForegroundColor Red
Write-Host "Avise colaboradores antes de fazer isso!" -ForegroundColor Red
Write-Host ""
