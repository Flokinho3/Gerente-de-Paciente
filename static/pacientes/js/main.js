// Gerenciamento da página de pacientes
let todosPacientes = [];
let pacientesFiltrados = [];
let paginaAtual = 1;
const pacientesPorPagina = 3;
let pacienteSelecionado = null;
let timeoutPesquisa = null;

// Elementos DOM
const searchInput = document.getElementById('searchInput');
const pacientesList = document.getElementById('pacientesList');
const paginationInfo = document.getElementById('paginationInfo');
const pageInfo = document.getElementById('pageInfo');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const pacientePerfil = document.getElementById('pacientePerfil');
const perfilContent = document.getElementById('perfilContent');
const closePerfilBtn = document.getElementById('closePerfil');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarPacientes();
    configurarEventos();
});

// Configurar eventos
function configurarEventos() {
    // Pesquisa em tempo real
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeoutPesquisa);
        timeoutPesquisa = setTimeout(() => {
            filtrarPacientes(e.target.value);
        }, 300); // Debounce de 300ms
    });

    // Controles de paginação
    prevBtn.addEventListener('click', () => {
        if (paginaAtual > 1) {
            paginaAtual--;
            renderizarPacientes();
        }
    });

    nextBtn.addEventListener('click', () => {
        const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
        if (paginaAtual < totalPaginas) {
            paginaAtual++;
            renderizarPacientes();
        }
    });

    // Fechar perfil
    closePerfilBtn.addEventListener('click', () => {
        fecharPerfil();
    });
}

// Carregar pacientes da API
async function carregarPacientes() {
    try {
        pacientesList.innerHTML = '<div class="loading">Carregando pacientes</div>';
        
        const response = await fetch('/api/pacientes');
        const data = await response.json();

        if (data.success) {
            todosPacientes = data.pacientes || [];
            pacientesFiltrados = [...todosPacientes];
            paginaAtual = 1;
            renderizarPacientes();
        } else {
            mostrarErro('Erro ao carregar pacientes');
        }
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
        mostrarErro('Erro ao conectar com o servidor');
    }
}

// Filtrar pacientes por nome
function filtrarPacientes(termo) {
    const termoLower = termo.toLowerCase().trim();
    
    if (!termoLower) {
        pacientesFiltrados = [...todosPacientes];
    } else {
        pacientesFiltrados = todosPacientes.filter(paciente => {
            const nome = paciente.identificacao?.nome_gestante || '';
            return nome.toLowerCase().includes(termoLower);
        });
    }
    
    paginaAtual = 1;
    renderizarPacientes();
}

// Renderizar lista de pacientes
function renderizarPacientes() {
    if (pacientesFiltrados.length === 0) {
        pacientesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">
                    ${searchInput.value.trim() ? 'Nenhum paciente encontrado com esse nome' : 'Nenhum paciente cadastrado'}
                </div>
            </div>
        `;
        atualizarInfoPaginacao();
        atualizarBotoesPaginacao();
        return;
    }

    // Calcular índices para paginação
    const inicio = (paginaAtual - 1) * pacientesPorPagina;
    const fim = inicio + pacientesPorPagina;
    const pacientesPagina = pacientesFiltrados.slice(inicio, fim);

    // Renderizar pacientes
    pacientesList.innerHTML = pacientesPagina.map(paciente => {
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        const unidade = paciente.identificacao?.unidade_saude || 'Unidade não informada';
        const data = formatarData(paciente.data_salvamento);
        const isSelected = pacienteSelecionado && pacienteSelecionado.id === paciente.id;
        
        return `
            <div class="paciente-item ${isSelected ? 'selected' : ''}" 
                 data-id="${paciente.id}"
                 onclick="selecionarPaciente('${paciente.id}')">
                <div class="paciente-info">
                    <div class="paciente-nome">${nome}</div>
                    <div class="paciente-detalhes">${unidade}</div>
                    <div class="paciente-data">Cadastrado em: ${data}</div>
                </div>
            </div>
        `;
    }).join('');

    atualizarInfoPaginacao();
    atualizarBotoesPaginacao();
}

// Selecionar paciente
function selecionarPaciente(pacienteId) {
    pacienteSelecionado = pacientesFiltrados.find(p => p.id === pacienteId);
    
    if (pacienteSelecionado) {
        // Atualizar visual da lista
        document.querySelectorAll('.paciente-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-id="${pacienteId}"]`)?.classList.add('selected');
        
        // Exibir perfil
        exibirPerfil(pacienteSelecionado);
        
        // Scroll suave até o perfil
        setTimeout(() => {
            pacientePerfil.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
}

// Exibir perfil do paciente
function exibirPerfil(paciente) {
    const identificacao = paciente.identificacao || {};
    const avaliacao = paciente.avaliacao || {};
    
    const html = `
        <div class="perfil-section">
            <h3>📋 Identificação</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">Nome da Gestante</span>
                    <div class="perfil-value">${identificacao.nome_gestante || 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Unidade de Saúde</span>
                    <div class="perfil-value">${identificacao.unidade_saude || 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Data de Cadastro</span>
                    <div class="perfil-value">${formatarData(paciente.data_salvamento)}</div>
                </div>
            </div>
        </div>

        <div class="perfil-section">
            <h3>📊 Avaliação</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">Início Pré-Natal antes de 12 semanas</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.inicio_pre_natal_antes_12s)}
                    </div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Consultas de Pré-Natal</span>
                    <div class="perfil-value">${avaliacao.consultas_pre_natal || 0}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Vacinas Completas</span>
                    <div class="perfil-value">
                        <span class="badge-status ${getBadgeClassVacina(avaliacao.vacinas_completas)}">
                            ${avaliacao.vacinas_completas || 'Não avaliado'}
                        </span>
                    </div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Plano de Parto</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.plano_parto)}
                    </div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Participou de Grupos</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.participou_grupos)}
                    </div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Avaliação Odontológica</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.avaliacao_odontologica)}
                    </div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Estratificação</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.estratificacao)}
                    </div>
                </div>
                ${avaliacao.estratificacao && avaliacao.estratificacao_problema ? `
                <div class="perfil-field" style="grid-column: 1 / -1;">
                    <span class="perfil-label">Problema Identificado na Estratificação</span>
                    <div class="perfil-value" style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; white-space: pre-wrap; word-wrap: break-word;">
                        ${avaliacao.estratificacao_problema}
                    </div>
                </div>
                ` : ''}
                <div class="perfil-field">
                    <span class="perfil-label">Cartão Pré-Natal Completo</span>
                    <div class="perfil-value">
                        ${formatarBoolean(avaliacao.cartao_pre_natal_completo)}
                    </div>
                </div>
            </div>
        </div>

        <div class="perfil-actions">
            <button class="btn btn-danger" onclick="confirmarExclusaoPaciente('${paciente.id}')">
                🗑️ Excluir Paciente
            </button>
        </div>
    `;
    
    perfilContent.innerHTML = html;
    pacientePerfil.style.display = 'block';
}

// Fechar perfil
function fecharPerfil() {
    pacienteSelecionado = null;
    pacientePerfil.style.display = 'none';
    
    // Remover seleção da lista
    document.querySelectorAll('.paciente-item').forEach(item => {
        item.classList.remove('selected');
    });
}

// Atualizar informações de paginação
function atualizarInfoPaginacao() {
    const total = pacientesFiltrados.length;
    const inicio = total === 0 ? 0 : (paginaAtual - 1) * pacientesPorPagina + 1;
    const fim = Math.min(paginaAtual * pacientesPorPagina, total);
    
    if (total === 0) {
        paginationInfo.textContent = 'Nenhum paciente encontrado';
    } else {
        paginationInfo.textContent = `Mostrando ${inicio} a ${fim} de ${total} paciente(s)`;
    }
}

// Atualizar botões de paginação
function atualizarBotoesPaginacao() {
    const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
    
    prevBtn.disabled = paginaAtual <= 1;
    nextBtn.disabled = paginaAtual >= totalPaginas || totalPaginas === 0;
    
    pageInfo.textContent = totalPaginas > 0 
        ? `Página ${paginaAtual} de ${totalPaginas}`
        : 'Página 1';
}

// Funções auxiliares
function formatarData(dataString) {
    if (!dataString) return 'Data não disponível';
    
    try {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dataString;
    }
}

function formatarBoolean(valor) {
    if (valor === true) {
        return '<span class="badge-status badge-success">Sim</span>';
    } else if (valor === false) {
        return '<span class="badge-status badge-danger">Não</span>';
    } else {
        return '<span class="badge-status badge-warning">Não informado</span>';
    }
}

function getBadgeClassVacina(valor) {
    if (!valor) return 'badge-warning';
    
    const valorLower = valor.toLowerCase();
    if (valorLower.includes('completa') || valorLower === 'completo') {
        return 'badge-success';
    } else if (valorLower.includes('incompleta') || valorLower === 'incompleto') {
        return 'badge-danger';
    } else {
        return 'badge-warning';
    }
}

function mostrarErro(mensagem) {
    pacientesList.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <div class="empty-state-text">${mensagem}</div>
        </div>
    `;
}

// Confirmar exclusão de paciente
async function confirmarExclusaoPaciente(pacienteId) {
    const paciente = todosPacientes.find(p => p.id === pacienteId);
    const nome = paciente?.identificacao?.nome_gestante || 'este paciente';
    
    if (confirm(`Tem certeza que deseja excluir o paciente "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        await excluirPaciente(pacienteId);
    }
}

// Excluir paciente
async function excluirPaciente(pacienteId) {
    try {
        const response = await fetch(`/api/deletar_paciente/${pacienteId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Fechar perfil
            fecharPerfil();
            
            // Recarregar lista de pacientes
            await carregarPacientes();
            
            // Mostrar mensagem de sucesso
            alert('Paciente excluído com sucesso!');
        } else {
            alert(data.message || 'Erro ao excluir paciente');
        }
    } catch (error) {
        console.error('Erro ao excluir paciente:', error);
        alert('Erro ao excluir paciente. Por favor, tente novamente.');
    }
}
