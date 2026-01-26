// Módulo de histórico de agendamentos

// Variáveis
let historicoAgendamentos = [];
let filtrosHistorico = {
    status: '',
    dataInicio: '',
    dataFim: ''
};

// Carregar histórico de agendamentos
async function carregarHistorico() {
    try {
        const container = document.getElementById('historicoList');
        if (!container) return;
        
        container.innerHTML = '<div class="loading">Carregando histórico...</div>';
        
        const response = await fetch('/api/agendamentos');
        const data = await response.json();
        
        if (data.success && data.agendamentos) {
            const agora = new Date();
            agora.setHours(0, 0, 0, 0);
            
            let agendamentosPassados = data.agendamentos.filter(ag => {
                const dataAgendamento = new Date(ag.data_consulta + 'T00:00:00');
                dataAgendamento.setHours(0, 0, 0, 0);
                return dataAgendamento < agora;
            });
            
            historicoAgendamentos = aplicarFiltrosAoHistorico(agendamentosPassados);
            
            renderizarHistorico();
        } else {
            mostrarErro('Erro ao carregar histórico');
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        mostrarErro('Erro ao carregar histórico');
    }
}

// Aplicar filtros ao histórico
function aplicarFiltrosAoHistorico(agendamentos) {
    let agendamentosFiltrados = [...agendamentos];
    
    if (filtrosHistorico.status) {
        if (filtrosHistorico.status === 'pendente') {
            agendamentosFiltrados = agendamentosFiltrados.filter(ag => 
                window.isAgendamentoPassado(ag)
            );
        } else {
            agendamentosFiltrados = agendamentosFiltrados.filter(ag => 
                ag.status === filtrosHistorico.status
            );
        }
    }
    
    if (filtrosHistorico.dataInicio) {
        agendamentosFiltrados = agendamentosFiltrados.filter(ag => 
            ag.data_consulta >= filtrosHistorico.dataInicio
        );
    }
    
    if (filtrosHistorico.dataFim) {
        agendamentosFiltrados = agendamentosFiltrados.filter(ag => 
            ag.data_consulta <= filtrosHistorico.dataFim
        );
    }
    
    agendamentosFiltrados.sort((a, b) => {
        const dataA = new Date(a.data_consulta + 'T' + (a.hora_consulta || '00:00:00'));
        const dataB = new Date(b.data_consulta + 'T' + (b.hora_consulta || '00:00:00'));
        return dataB - dataA;
    });
    
    return agendamentosFiltrados;
}

// Renderizar histórico
function renderizarHistorico() {
    const container = document.getElementById('historicoList');
    if (!container) return;
    
    if (historicoAgendamentos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <div class="empty-state-text">Nenhum agendamento encontrado no histórico</div>
                <div class="empty-state-subtext">Não há agendamentos passados com os filtros selecionados</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = historicoAgendamentos.map(agendamento => {
        const dataFormatada = formatarData(agendamento.data_consulta);
        const horaFormatada = formatarHora(agendamento.hora_consulta);
        const statusClass = `status-${agendamento.status}`;
        const statusLabel = formatarStatus(agendamento.status);
        const tipoLabel = formatarTipoConsulta(agendamento.tipo_consulta);
        
        const ePassado = window.isAgendamentoPassado(agendamento);
        const eRevisado = window.isAgendamentoRevisado(agendamento);
        const estiloVermelho = ePassado 
            ? 'style="border: 2px solid #d32f2f; background: #ffebee;"' 
            : '';
        
        let badgeStatus = '';
        if (ePassado) {
            badgeStatus = '<span style="color: #d32f2f; font-weight: bold; margin-left: 10px;">⚠️ Pendente de Confirmação</span>';
        } else if (eRevisado) {
            const agora = new Date();
            const dataAgendamento = new Date(agendamento.data_consulta + 'T' + (agendamento.hora_consulta || '00:00:00'));
            if (dataAgendamento < agora) {
                badgeStatus = '<span style="color: #388e3c; font-weight: bold; margin-left: 10px;">✅ Revisada</span>';
            }
        }
        
        return `
            <div class="agendamento-card" data-agendamento-id="${agendamento.id}" ${estiloVermelho}>
                <div class="agendamento-info">
                    <div class="agendamento-header">
                        <h3 class="agendamento-nome">${agendamento.nome_gestante || 'Nome não informado'}</h3>
                        <span class="agendamento-status ${statusClass}">${statusLabel}</span>
                        ${badgeStatus}
                    </div>
                    <div class="agendamento-detalhes">
                        <div class="agendamento-detalhe">
                            <strong>📅 Data:</strong> ${dataFormatada}
                        </div>
                        <div class="agendamento-detalhe">
                            <strong>🕐 Hora:</strong> ${horaFormatada}
                        </div>
                        ${tipoLabel ? `
                        <div class="agendamento-detalhe">
                            <strong>🏥 Tipo:</strong> ${tipoLabel}
                        </div>
                        ` : ''}
                        ${agendamento.unidade_saude ? `
                        <div class="agendamento-detalhe">
                            <strong>🏢 Unidade:</strong> ${agendamento.unidade_saude}
                        </div>
                        ` : ''}
                    </div>
                    ${agendamento.observacoes ? `
                    <div style="margin-top: 12px; padding: 12px; background: var(--accent); border-radius: 8px; font-size: 0.9rem; color: var(--text-muted);">
                        <strong>📝 Observações:</strong> ${agendamento.observacoes}
                    </div>
                    ` : ''}
                </div>
                <div class="agendamento-actions">
                    ${ePassado ? `
                    <button class="btn-icon btn-primary" onclick="questionarSituacaoAtendimento('${agendamento.id}')" title="Confirmar Situação">
                        ✅ Confirmar
                    </button>
                    ` : ''}
                    <button class="btn-icon btn-edit" onclick="editarAgendamento('${agendamento.id}')" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon btn-delete" onclick="confirmarExclusao('${agendamento.id}')" title="Excluir">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Questionar situação do atendimento
function questionarSituacaoAtendimento(agendamentoId) {
    const agendamento = historicoAgendamentos.find(ag => ag.id === agendamentoId);
    if (!agendamento) {
        const todosAgendamentos = window.obterAgendamentos?.() || [];
        const ag = todosAgendamentos.find(a => a.id === agendamentoId);
        if (ag) {
            window.mostrarModalConfirmarAtendimento(ag);
        } else {
            mostrarMensagem('Agendamento não encontrado', true);
        }
    } else {
        window.mostrarModalConfirmarAtendimento(agendamento);
    }
}

// Aplicar filtros do histórico
function aplicarFiltrosHistorico() {
    filtrosHistorico.status = document.getElementById('filterHistoricoStatus')?.value || '';
    filtrosHistorico.dataInicio = document.getElementById('filterHistoricoDataInicio')?.value || '';
    filtrosHistorico.dataFim = document.getElementById('filterHistoricoDataFim')?.value || '';
    
    carregarHistorico();
}

// Limpar filtros do histórico
function limparFiltrosHistorico() {
    filtrosHistorico = {
        status: '',
        dataInicio: '',
        dataFim: ''
    };
    
    document.getElementById('filterHistoricoStatus').value = '';
    document.getElementById('filterHistoricoDataInicio').value = '';
    document.getElementById('filterHistoricoDataFim').value = '';
    
    carregarHistorico();
}

// Toggle de filtros do histórico
function toggleFiltrosHistorico() {
    const filtrosContent = document.getElementById('filtrosContentHistorico');
    const btnToggle = document.querySelector('[onclick="toggleFiltrosHistorico()"]');
    
    if (filtrosContent && btnToggle) {
        filtrosContent.classList.toggle('collapsed');
        btnToggle.classList.toggle('ativo');
    }
}

// Exportar funções
window.carregarHistorico = carregarHistorico;
window.questionarSituacaoAtendimento = questionarSituacaoAtendimento;
window.aplicarFiltrosHistorico = aplicarFiltrosHistorico;
window.limparFiltrosHistorico = limparFiltrosHistorico;
window.toggleFiltrosHistorico = toggleFiltrosHistorico;
// Exportar variável para limpeza de cache
window.historicoAgendamentos = historicoAgendamentos;