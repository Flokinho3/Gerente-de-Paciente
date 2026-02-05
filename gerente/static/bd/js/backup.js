/**
 * backup.js - Funções de backup e restore
 * Inclui: Criar backup, carregar backup, limpar banco
 */

// ==================== CRIAR BACKUP ====================

async function criarBackupBD() {
    try {
        mostrarLoading('Criando Backup', 'Gerando cópia de segurança dos dados...');
        atualizarProgressoLoading(30);

        const response = await fetch('/api/backup/criar');
        atualizarProgressoLoading(70);

        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(90);

            // Criar link de download
            const blob = new Blob([JSON.stringify(data.backup, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            a.download = `backup_bd_${timestamp}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                mostrarStatus('Backup criado e baixado com sucesso!', 'success');
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao criar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar backup:', error);
        esconderLoading();
        mostrarStatus('Erro ao criar backup', 'error');
    }
}

// ==================== CARREGAR BACKUP ====================

async function carregarBackupBD(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        mostrarStatus('Por favor, selecione um arquivo JSON válido', 'error');
        return;
    }

    try {
        mostrarLoading('Lendo Arquivo', 'Lendo e validando estrutura do backup...');
        atualizarProgressoLoading(30);

        const fileContent = await file.text();
        atualizarProgressoLoading(60);

        const backup = JSON.parse(fileContent);

        // Validar estrutura do backup
        let backupData = backup;

        // Verificar se é um backup antigo (com propriedade 'pacientes') ou novo (array direto)
        if (backup.pacientes && Array.isArray(backup.pacientes)) {
            backupData = backup.pacientes;
        } else if (backup.backup && Array.isArray(backup.backup)) {
            backupData = backup.backup;
        } else if (Array.isArray(backup)) {
            backupData = backup;
        } else {
            esconderLoading();
            mostrarStatus('Arquivo de backup inválido. Estrutura não reconhecida.', 'error');
            event.target.value = '';
            return;
        }

        atualizarProgressoLoading(80);
        
        // Chamar comparação em vez de importar diretamente
        await compararBackupAntesImportar(backupData);
        
        esconderLoading();
    } catch (error) {
        console.error('Erro ao carregar backup:', error);
        esconderLoading();
        if (error instanceof SyntaxError) {
            mostrarStatus('Erro: Arquivo JSON inválido', 'error');
        } else {
            mostrarStatus('Erro ao carregar backup', 'error');
        }
    } finally {
        event.target.value = '';
    }
}

// LEGACY: Carregar backup direto (sem comparação) - mantido para compatibilidade
async function carregarBackupBDDireto(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        mostrarStatus('Por favor, selecione um arquivo JSON válido', 'error');
        return;
    }

    if (!confirm('ATENÇÃO: Carregar este backup irá substituir TODOS os dados atuais do banco de dados!\n\nTem certeza que deseja continuar?')) {
        event.target.value = '';
        return;
    }

    try {
        mostrarLoading('Carregando Backup', 'Lendo arquivo e validando estrutura...');
        atualizarProgressoLoading(20);

        const fileContent = await file.text();
        atualizarProgressoLoading(40);

        const backup = JSON.parse(fileContent);
        atualizarProgressoLoading(60);

        // Validar estrutura do backup
        let backupData = backup;

        // Verificar se é um backup antigo (com propriedade 'pacientes') ou novo (array direto)
        if (backup.pacientes && Array.isArray(backup.pacientes)) {
            backupData = backup.pacientes;
        } else if (backup.backup && Array.isArray(backup.backup)) {
            backupData = backup.backup;
        } else if (Array.isArray(backup)) {
            backupData = backup;
        } else {
            esconderLoading();
            mostrarStatus('Arquivo de backup inválido. Estrutura não reconhecida.', 'error');
            event.target.value = '';
            return;
        }

        atualizarProgressoLoading(80);
        const response = await fetch('/api/backup/restaurar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup: backupData })
        });

        atualizarProgressoLoading(90);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(async () => {
                esconderLoading();
                mostrarStatus('Backup restaurado com sucesso!', 'success');
                await carregarPacientes();
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao restaurar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar backup:', error);
        esconderLoading();
        if (error instanceof SyntaxError) {
            mostrarStatus('Erro: Arquivo JSON inválido', 'error');
        } else {
            mostrarStatus('Erro ao carregar backup', 'error');
        }
    } finally {
        event.target.value = '';
    }
}

// ==================== LIMPAR BANCO ====================

async function excluirTodosDadosBD() {
    try {
        mostrarLoading('Excluindo Dados', 'Removendo todos os registros do banco de dados...');
        atualizarProgressoLoading(50);

        const response = await fetch('/api/backup/limpar', {
            method: 'DELETE'
        });

        atualizarProgressoLoading(80);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(async () => {
                esconderLoading();
                mostrarStatus('Todos os dados foram excluídos com sucesso!', 'success');
                
                const confirmClearModal = document.getElementById('confirmClearModal');
                const confirmText = document.getElementById('confirmText');
                
                if (confirmClearModal) confirmClearModal.classList.remove('active');
                if (confirmText) confirmText.value = '';
                
                await carregarPacientes();
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao excluir dados', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir dados:', error);
        esconderLoading();
        mostrarStatus('Erro ao excluir dados', 'error');
    }
}
