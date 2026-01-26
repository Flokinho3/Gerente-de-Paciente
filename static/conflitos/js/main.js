let conflitos = {
    pacientes: [],
    agendamentos: []
};

async function carregarConflitos() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    
    loadingOverlay.style.display = 'flex';
    loadingMessage.textContent = 'Carregando conflitos...';
    
    try {
        const response = await fetch('/api/sync/conflitos');
        const data = await response.json();
        
        if (data.success) {
            conflitos = {
                pacientes: data.pacientes || [],
                agendamentos: data.agendamentos || []
            };
            
            atualizarEstatisticas();
            renderizarConflitos();
        } else {
            mostrarMensagem('Erro ao carregar conflitos: ' + data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao carregar conflitos: ' + error.message, 'error');
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function atualizarEstatisticas() {
    const total = conflitos.pacientes.length + conflitos.agendamentos.length;
    
    document.getElementById('totalConflitos').textContent = total;
    document.getElementById('pacientesConflito').textContent = conflitos.pacientes.length;
    document.getElementById('agendamentosConflito').textContent = conflitos.agendamentos.length;
    
    const semConflitos = document.getElementById('semConflitos');
    if (total === 0) {
        semConflitos.style.display = 'block';
    } else {
        semConflitos.style.display = 'none';
    }
}

function renderizarConflitos() {
    renderizarPacientes();
    renderizarAgendamentos();
}

function renderizarPacientes() {
    const container = document.getElementById('pacientesConflitoList');
    container.innerHTML = '';
    
    if (conflitos.pacientes.length === 0) {
        container.innerHTML = '<p style="color: #666; padding: 20px; text-align: center;">Nenhum paciente com conflito.</p>';
        return;
    }
    
    conflitos.pacientes.forEach(paciente => {
        const item = criarItemConflitoPaciente(paciente);
        container.appendChild(item);
    });
}

function renderizarAgendamentos() {
    const container = document.getElementById('agendamentosConflitoList');
    container.innerHTML = '';
    
    if (conflitos.agendamentos.length === 0) {
        container.innerHTML = '<p style="color: #666; padding: 20px; text-align: center;">Nenhum agendamento com conflito.</p>';
        return;
    }
    
    conflitos.agendamentos.forEach(agendamento => {
        const item = criarItemConflitoAgendamento(agendamento);
        container.appendChild(item);
    });
}

function criarItemConflitoPaciente(paciente) {
    const div = document.createElement('div');
    div.className = 'conflito-item';
    
    const nome = paciente.identificacao?.nome_gestante || paciente.nome_gestante || 'Sem nome';
    const unidade = paciente.identificacao?.unidade_saude || paciente.unidade_saude || 'Não informado';
    
    div.innerHTML = `
        <div class="conflito-header">
            <div class="conflito-title">👤 ${nome}</div>
            <div class="conflito-actions">
                <button class="btn-resolver btn-comparar" onclick="compararConflito('paciente', '${paciente.id}')">
                    🔍 Comparar
                </button>
                <button class="btn-resolver btn-manter-local" onclick="resolverConflito('paciente', '${paciente.id}', 'manter_local')">
                    ✓ Manter Local
                </button>
            </div>
        </div>
        <div class="conflito-info">
            <div><strong>Unidade:</strong> ${unidade}</div>
            <div><strong>Última Modificação:</strong> ${formatarData(paciente.ultima_modificacao || paciente.data_salvamento)}</div>
            <div><strong>Versão:</strong> ${paciente.versao || 1}</div>
            <div><strong>PC ID:</strong> ${paciente.pc_id || 'N/A'}</div>
        </div>
    `;
    
    return div;
}

function criarItemConflitoAgendamento(agendamento) {
    const div = document.createElement('div');
    div.className = 'conflito-item';
    
    div.innerHTML = `
        <div class="conflito-header">
            <div class="conflito-title">📅 Agendamento - ${formatarData(agendamento.data_consulta)} ${agendamento.hora_consulta || ''}</div>
            <div class="conflito-actions">
                <button class="btn-resolver btn-comparar" onclick="compararConflito('agendamento', '${agendamento.id}')">
                    🔍 Comparar
                </button>
                <button class="btn-resolver btn-manter-local" onclick="resolverConflito('agendamento', '${agendamento.id}', 'manter_local')">
                    ✓ Manter Local
                </button>
            </div>
        </div>
        <div class="conflito-info">
            <div><strong>Paciente ID:</strong> ${agendamento.paciente_id}</div>
            <div><strong>Status:</strong> ${agendamento.status || 'agendado'}</div>
            <div><strong>Última Modificação:</strong> ${formatarData(agendamento.ultima_modificacao || agendamento.data_atualizacao)}</div>
            <div><strong>Versão:</strong> ${agendamento.versao || 1}</div>
        </div>
    `;
    
    return div;
}

async function resolverConflito(tipo, registroId, acao) {
    const acaoTexto = acao === 'manter_local' ? 'manter a versão local' : 'aceitar a versão remota';
    if (!confirm(`Tem certeza que deseja ${acaoTexto}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/sync/conflitos/resolver', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                registro_id: registroId,
                tipo: tipo,
                acao: acao
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Conflito resolvido com sucesso!', 'success');
            setTimeout(() => {
                carregarConflitos(); // Recarregar lista após um momento
            }, 500);
        } else {
            mostrarMensagem('Erro ao resolver conflito: ' + data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao resolver conflito: ' + error.message, 'error');
    }
}

async function compararConflito(tipo, registroId) {
    // Por enquanto, apenas mostra informação básica
    // Em uma versão futura, poderia buscar dados remotos para comparação side-by-side
    alert('Funcionalidade de comparação detalhada será implementada em breve.\n\nPor enquanto, você pode resolver o conflito escolhendo manter a versão local ou aceitar a versão remota.');
}

function fecharModalComparacao() {
    document.getElementById('comparacaoModal').style.display = 'none';
}

function formatarData(dataStr) {
    if (!dataStr) return 'N/A';
    try {
        const data = new Date(dataStr);
        return data.toLocaleString('pt-BR');
    } catch {
        return dataStr;
    }
}

function mostrarMensagem(mensagem, tipo) {
    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = mensagem;
    statusMessage.className = `status-message ${tipo}`;
    statusMessage.style.display = 'block';
    
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

// Carregar conflitos ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    carregarConflitos();
});
