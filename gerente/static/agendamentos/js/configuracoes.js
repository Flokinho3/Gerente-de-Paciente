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
            if (modalExcluirBD) modalExcluirBD.style.display = 'none';
            if (confirmTextExcluirBD) confirmTextExcluirBD.value = '';
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
        
        // Limpar todos os arrays em cache de forma agressiva
        // Limpar cache de agendamentos (lista principal)
        if (window.obterAgendamentos) {
            const agendamentos = window.obterAgendamentos();
            if (Array.isArray(agendamentos)) {
                agendamentos.length = 0;
            }
        }
        if (window.agendamentosArray && Array.isArray(window.agendamentosArray)) {
            window.agendamentosArray.length = 0;
        }
        
        // Limpar cache do calendário - forçar nova referência vazia
        window.agendamentosCalendario = [];
        
        // Limpar cache do histórico - forçar nova referência vazia
        window.historicoAgendamentos = [];
        
        // Limpar cache dos alertas de agendamentos - forçar nova referência vazia
        window.agendamentosAlertas = [];
        
        // Limpar expansão do dia no calendário se estiver expandido
        if (window.colapsarDiaExpandido) {
            window.colapsarDiaExpandido();
        }
        
        // Limpar HTML dos containers para garantir que não há dados visuais antigos
        const containerAgendamentos = document.getElementById('agendamentosList');
        if (containerAgendamentos) {
            containerAgendamentos.innerHTML = '';
        }
        
        const containerCalendario = document.getElementById('diasCalendario');
        if (containerCalendario) {
            containerCalendario.innerHTML = '';
        }
        
        const containerHistorico = document.getElementById('historicoList');
        if (containerHistorico) {
            containerHistorico.innerHTML = '';
        }
        
        const containerExpansao = document.getElementById('expansaoDia');
        if (containerExpansao) {
            containerExpansao.style.display = 'none';
            const agendamentosDia = document.getElementById('agendamentosDia');
            if (agendamentosDia) {
                agendamentosDia.innerHTML = '';
            }
        }
        
        // Recarregar pacientes
        await window.carregarTodosPacientes();

        // Forçar atualização de todas as views
        if (window.carregarCalendario) await window.carregarCalendario();
        if (window.carregarAgendamentos) await window.carregarAgendamentos();
        
        // Atualizar histórico
        if (window.carregarHistorico) {
            await window.carregarHistorico();
        }
        
        // Atualizar alertas de agendamentos
        if (window.carregarAlertasAgendamentos) {
            await window.carregarAlertasAgendamentos();
        }
        
        // Atualizar alertas de parto (se existir)
        if (window.carregarAlertasParto) {
            await window.carregarAlertasParto();
        }
        
        // Garantir que as referências globais estejam sincronizadas após recarregar
        // Isso é importante porque os módulos podem criar novas referências locais
        if (window.obterAgendamentos) {
            const agendamentosAtuais = window.obterAgendamentos();
            if (Array.isArray(agendamentosAtuais) && window.agendamentosArray) {
                window.agendamentosArray.length = 0;
                window.agendamentosArray.push(...agendamentosAtuais);
            }
        }
        
        mostrarMensagem('Dados atualizados com sucesso!', false);
    } catch (error) {
        console.error('Erro ao atualizar BD:', error);
        mostrarMensagem('Erro ao atualizar dados', true);
    }
}

// Exportar funções
window.configurarConfiguracoes = configurarConfiguracoes;
