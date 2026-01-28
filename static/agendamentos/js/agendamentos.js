// Módulo de CRUD de agendamentos

// Variáveis
let agendamentos = [];

// Elementos DOM (apenas os específicos deste módulo)
const formAgendamento = document.getElementById('formAgendamento');

// Carregar agendamentos
async function carregarAgendamentos() {
    try {
        let container = document.getElementById('agendamentosList');
        if (!container) {
            const agendaView = document.getElementById('agenda');
            if (agendaView) {
                container = document.createElement('div');
                container.id = 'agendamentosList';
                container.className = 'agendamentos-list';
                agendaView.appendChild(container);
            } else {
                console.error('View de agenda não encontrada');
                return;
            }
        }

        container.innerHTML = '<div class="loading">Carregando agendamentos...</div>';

        const response = await fetch('/api/agendamentos');
        const data = await response.json();

        if (data.success && data.agendamentos) {
            agendamentos = data.agendamentos;
            renderizarAgendamentos();
        } else {
            mostrarErro('Erro ao carregar agendamentos');
        }
    } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
        mostrarErro('Erro ao carregar agendamentos');
    }
}

// Verificar se agendamento está atrasado
function isAgendamentoAtrasado(dataConsulta) {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    const dataAgendamento = new Date(dataConsulta + 'T00:00:00');
    
    // Se a data é anterior a hoje, está atrasado
    return dataAgendamento < hoje;
}

// Renderizar agendamentos
function renderizarAgendamentos() {
    const container = document.getElementById('agendamentosList');
    if (!container) return;
    
    if (agendamentos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <div class="empty-state-text">Nenhum agendamento encontrado</div>
                <div class="empty-state-subtext">Adicione um novo agendamento na seção "Adicionar Agendamento"</div>
            </div>
        `;
        return;
    }

    container.innerHTML = agendamentos.map(agendamento => {
        const dataFormatada = formatarData(agendamento.data_consulta);
        const horaFormatada = formatarHora(agendamento.hora_consulta);
        const statusClass = `status-${agendamento.status}`;
        const statusLabel = formatarStatus(agendamento.status);
        const tipoLabel = formatarTipoConsulta(agendamento.tipo_consulta);
        
        // Verificar se está atrasado (qualquer data passada)
        const atrasado = isAgendamentoAtrasado(agendamento.data_consulta);
        const atrasadoClass = atrasado ? 'agendamento-atrasado' : '';
        const atrasadoAttr = atrasado ? 'data-atrasado="true"' : '';

        return `
            <div class="agendamento-card ${atrasadoClass}" data-agendamento-id="${agendamento.id}" ${atrasadoAttr}>
                <div class="agendamento-info">
                    <div class="agendamento-header">
                        <h3 class="agendamento-nome">${agendamento.nome_gestante || 'Nome não informado'}</h3>
                        <span class="agendamento-status ${statusClass}">${statusLabel}</span>
                        ${atrasado ? '<span class="badge-atrasado">⚠️ Atrasado</span>' : ''}
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
                    ${atrasado ? `
                    <div class="aviso-atrasado">
                        💡 Clique no card para ir ao histórico e atualizar o status
                    </div>
                    ` : ''}
                </div>
                <div class="agendamento-actions">
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
    
    // Adicionar event listeners para agendamentos atrasados
    const cardsAtrasados = container.querySelectorAll('.agendamento-card[data-atrasado="true"]');
    cardsAtrasados.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function(e) {
            // Não redirecionar se clicou nos botões de ação
            if (e.target.closest('.agendamento-actions')) {
                return;
            }
            
            // Redirecionar para o histórico
            mostrarView('historico');
            
            // Mostrar mensagem informativa
            setTimeout(() => {
                mostrarMensagem('Agendamento atrasado selecionado. Atualize o status no histórico.', false);
            }, 300);
        });
    });
}

// Salvar agendamento
async function salvarAgendamento() {
    const agendamentoId = document.getElementById('agendamentoId').value;
    const pacienteIdHidden = document.getElementById('pacienteId');
    const pacienteId = pacienteIdHidden ? pacienteIdHidden.value : document.getElementById('pacienteSelect')?.value;
    const dataConsulta = document.getElementById('dataConsulta').value;
    const horaConsulta = document.getElementById('horaConsulta').value;
    const tipoConsulta = document.getElementById('tipoConsulta').value;
    const status = document.getElementById('statusAgendamento').value;
    const observacoes = document.getElementById('observacoes').value;

    if (!pacienteId || !dataConsulta || !horaConsulta) {
        mostrarMensagem('Preencha todos os campos obrigatórios', true);
        return;
    }

    const dados = {
        paciente_id: pacienteId,
        data_consulta: dataConsulta,
        hora_consulta: horaConsulta,
        tipo_consulta: tipoConsulta || null,
        status: status,
        observacoes: observacoes || null
    };

    try {
        let response;
        if (agendamentoId) {
            response = await fetch(`/api/agendamentos/${agendamentoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
        } else {
            response = await fetch('/api/agendamentos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });
        }

        const resultado = await response.json();
        
        if (resultado.success) {
            mostrarMensagem(resultado.message);
            if (formAgendamento) {
                formAgendamento.reset();
                document.getElementById('agendamentoId').value = '';
                limparSelecaoPaciente();
            }
            const agendaView = document.getElementById('agenda');
            if (agendaView && agendaView.classList.contains('ativa')) {
                carregarAgendamentos();
            }
        } else {
            mostrarMensagem(resultado.message, true);
        }
    } catch (error) {
        console.error('Erro ao salvar agendamento:', error);
        mostrarMensagem('Erro ao salvar agendamento', true);
    }
}

// Confirmar exclusão
function confirmarExclusao(agendamentoId) {
    if (confirm('Tem certeza que deseja excluir este agendamento?')) {
        excluirAgendamento(agendamentoId);
    }
}

// Excluir agendamento
async function excluirAgendamento(agendamentoId) {
    try {
        const response = await fetch(`/api/agendamentos/${agendamentoId}`, { method: 'DELETE' });
        const resultado = await response.json();
        if (resultado.success) {
            mostrarMensagem(resultado.message);
            carregarAgendamentos();
            if (window.carregarCalendario) window.carregarCalendario();
        } else {
            mostrarMensagem(resultado.message, true);
        }
    } catch (error) {
        console.error('Erro ao excluir agendamento:', error);
        mostrarMensagem('Erro ao excluir agendamento', true);
    }
}

// Editar agendamento
async function editarAgendamento(agendamentoId) {
    try {
        const response = await fetch(`/api/agendamentos/${agendamentoId}`);
        const data = await response.json();

        if (!data.success || !data.agendamento) {
            mostrarMensagem('Erro ao carregar agendamento', true);
            return;
        }

        const agendamento = data.agendamento;
        const todosPacientes = window.obterTodosPacientes();

        document.getElementById('agendamentoId').value = agendamento.id;
        
        if (agendamento.paciente_id) {
            const paciente = todosPacientes.find(p => p.id === agendamento.paciente_id);
            if (paciente) {
                selecionarPaciente(paciente);
            } else {
                const pacientesResponse = await fetch('/api/pacientes');
                const pacientesData = await pacientesResponse.json();
                if (pacientesData.success && pacientesData.pacientes) {
                    const pacienteCompleto = pacientesData.pacientes.find(p => p.id === agendamento.paciente_id);
                    if (pacienteCompleto) {
                        selecionarPaciente(pacienteCompleto);
                    }
                }
            }
        }

        document.getElementById('dataConsulta').value = agendamento.data_consulta || '';
        document.getElementById('horaConsulta').value = agendamento.hora_consulta || '';
        
        if (agendamento.tipo_consulta) {
            document.getElementById('tipoConsulta').value = agendamento.tipo_consulta;
        }
        
        if (agendamento.status) {
            document.getElementById('statusAgendamento').value = agendamento.status;
        }
        
        if (agendamento.observacoes) {
            document.getElementById('observacoes').value = agendamento.observacoes;
        }

        mostrarView('novo');

        setTimeout(() => {
            const formSection = document.getElementById('novo');
            if (formSection) {
                formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);

        mostrarMensagem('Agendamento carregado para edição');
    } catch (error) {
        console.error('Erro ao editar agendamento:', error);
        mostrarMensagem('Erro ao carregar agendamento', true);
    }
}

// Aplicar filtros
function aplicarFiltros() {
    const dataInicio = document.getElementById('filterDataInicio').value;
    const dataFim = document.getElementById('filterDataFim').value;
    const status = document.getElementById('filterStatus').value;

    let url = '/api/agendamentos?';
    const params = [];

    if (dataInicio) {
        params.push(`data_inicio=${dataInicio}`);
    }
    if (dataFim) {
        params.push(`data_fim=${dataFim}`);
    }
    if (status) {
        params.push(`status=${status}`);
    }

    url += params.join('&');

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.agendamentos) {
                agendamentos = data.agendamentos;
                renderizarAgendamentos();
            }
        })
        .catch(error => {
            console.error('Erro ao filtrar agendamentos:', error);
            mostrarMensagem('Erro ao filtrar agendamentos', true);
        });
}

// Limpar filtros
function limparFiltros() {
    document.getElementById('filterDataInicio').value = '';
    document.getElementById('filterDataFim').value = '';
    document.getElementById('filterStatus').value = '';
    carregarAgendamentos();
}

// Toggle de filtros
function toggleFiltros() {
    const filtrosContent = document.getElementById('filtrosContent');
    const btnToggle = document.querySelector('.btn-toggle-filtros');
    
    if (filtrosContent && btnToggle) {
        filtrosContent.classList.toggle('collapsed');
        btnToggle.classList.toggle('ativo');
    }
}

// Configurar eventos do formulário
function configurarEventosAgendamentos() {
    if (formAgendamento) {
        formAgendamento.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const pacienteIdHidden = document.getElementById('pacienteId');
            const pacienteSearch = document.getElementById('pacienteSearch');
            
            if (pacienteIdHidden && !pacienteIdHidden.value) {
                if (pacienteSearch) {
                    pacienteSearch.setCustomValidity('Por favor, selecione um paciente da lista');
                    pacienteSearch.reportValidity();
                }
                return;
            }
            
            salvarAgendamento();
        });

        formAgendamento.addEventListener('reset', () => {
            if (window.limparSelecaoPaciente) {
                window.limparSelecaoPaciente();
            }
        });
    }

    const pacienteSearch = document.getElementById('pacienteSearch');
    if (pacienteSearch) {
        pacienteSearch.addEventListener('blur', () => {
            const pacienteIdHidden = document.getElementById('pacienteId');
            if (!pacienteIdHidden || !pacienteIdHidden.value) {
                if (pacienteSearch.value.trim() !== '') {
                    pacienteSearch.setCustomValidity('Por favor, selecione um paciente da lista de resultados');
                }
            } else {
                pacienteSearch.setCustomValidity('');
            }
        });
    }
}

// Exportar funções
window.carregarAgendamentos = carregarAgendamentos;
window.salvarAgendamento = salvarAgendamento;
window.editarAgendamento = editarAgendamento;
window.confirmarExclusao = confirmarExclusao;
window.aplicarFiltros = aplicarFiltros;
window.limparFiltros = limparFiltros;
window.toggleFiltros = toggleFiltros;
window.configurarEventosAgendamentos = configurarEventosAgendamentos;
window.obterAgendamentos = () => agendamentos;
// Exportar variável para limpeza de cache
window.agendamentosArray = agendamentos;