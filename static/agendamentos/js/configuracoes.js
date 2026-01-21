// Módulo de configurações e gerenciamento de BD

// Configurar eventos de configurações
function configurarConfiguracoes() {
    const btnExcluirBD = document.getElementById('btnExcluirBD');
    const btnExportarBD = document.getElementById('btnExportarBD');
    const btnAtualizarBD = document.getElementById('btnAtualizarBD');
    const modalExcluirBD = document.getElementById('modalExcluirBD');
    const fecharModalExcluirBD = document.getElementById('fecharModalExcluirBD');
    const cancelarExcluirBD = document.getElementById('cancelarExcluirBD');
    const confirmarExcluirBD = document.getElementById('confirmarExcluirBD');
    const confirmTextExcluirBD = document.getElementById('confirmTextExcluirBD');

    if (btnExcluirBD) {
        btnExcluirBD.addEventListener('click', () => {
            if (modalExcluirBD) {
                modalExcluirBD.style.display = 'flex';
                if (confirmTextExcluirBD) {
                    confirmTextExcluirBD.value = '';
                }
                if (confirmarExcluirBD) {
                    confirmarExcluirBD.disabled = true;
                }
            }
        });
    }

    if (btnExportarBD) {
        btnExportarBD.addEventListener('click', exportarBD);
    }

    if (btnAtualizarBD) {
        btnAtualizarBD.addEventListener('click', atualizarBD);
    }

    if (fecharModalExcluirBD) {
        fecharModalExcluirBD.addEventListener('click', () => {
            if (modalExcluirBD) {
                modalExcluirBD.style.display = 'none';
            }
        });
    }

    if (cancelarExcluirBD) {
        cancelarExcluirBD.addEventListener('click', () => {
            if (modalExcluirBD) {
                modalExcluirBD.style.display = 'none';
            }
        });
    }

    if (confirmTextExcluirBD && confirmarExcluirBD) {
        confirmTextExcluirBD.addEventListener('input', (e) => {
            confirmarExcluirBD.disabled = e.target.value !== 'CONFIRMAR';
        });
    }

    if (confirmarExcluirBD) {
        confirmarExcluirBD.addEventListener('click', excluirBD);
    }

    if (modalExcluirBD) {
        modalExcluirBD.addEventListener('click', (e) => {
            if (e.target === modalExcluirBD) {
                modalExcluirBD.style.display = 'none';
            }
        });
    }
}

// Exportar BD
async function exportarBD() {
    try {
        mostrarMensagem('Gerando backup do banco de dados...', false);
        
        const response = await fetch('/api/backup/download');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `backup_pacientes_${new Date().toISOString().slice(0, 10)}.json`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            mostrarMensagem('Backup exportado com sucesso!', false);
        } else {
            const error = await response.json();
            mostrarMensagem(error.message || 'Erro ao exportar backup', true);
        }
    } catch (error) {
        console.error('Erro ao exportar BD:', error);
        mostrarMensagem('Erro ao exportar banco de dados', true);
    }
}

// Excluir BD
async function excluirBD() {
    const modalExcluirBD = document.getElementById('modalExcluirBD');
    const confirmTextExcluirBD = document.getElementById('confirmTextExcluirBD');
    
    if (confirmTextExcluirBD && confirmTextExcluirBD.value !== 'CONFIRMAR') {
        mostrarMensagem('Por favor, digite CONFIRMAR para continuar', true);
        return;
    }

    try {
        mostrarMensagem('Excluindo dados do banco de dados...', false);
        
        const response = await fetch('/api/backup/limpar', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Banco de dados excluído com sucesso!', false);
            
            if (modalExcluirBD) {
                modalExcluirBD.style.display = 'none';
            }
            if (confirmTextExcluirBD) {
                confirmTextExcluirBD.value = '';
            }
            
            await atualizarBD();
        } else {
            mostrarMensagem(data.message || 'Erro ao excluir banco de dados', true);
        }
    } catch (error) {
        console.error('Erro ao excluir BD:', error);
        mostrarMensagem('Erro ao excluir banco de dados', true);
    }
}

// Atualizar BD (recarregar dados)
async function atualizarBD() {
    try {
        mostrarMensagem('Atualizando dados do sistema...', false);
        
        await window.carregarTodosPacientes();
        
        const viewAgenda = document.getElementById('agenda');
        if (viewAgenda && viewAgenda.classList.contains('ativa')) {
            await window.carregarAgendamentos();
        }
        
        const viewCalendario = document.getElementById('calendario');
        if (viewCalendario && viewCalendario.classList.contains('ativa')) {
            await window.carregarCalendario();
        }
        
        mostrarMensagem('Dados atualizados com sucesso!', false);
    } catch (error) {
        console.error('Erro ao atualizar BD:', error);
        mostrarMensagem('Erro ao atualizar dados', true);
    }
}

// Exportar funções
window.configurarConfiguracoes = configurarConfiguracoes;
