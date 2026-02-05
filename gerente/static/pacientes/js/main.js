// Gerenciamento da página de pacientes
let todosPacientes = [], pacientesFiltrados = [], paginaAtual = 1, pacienteSelecionado = null, timeoutPesquisa = null;
const pacientesPorPagina = 3;

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
    carregarMiniDashboardUnidades();
    configurarEventos();
    const criterioSelect = document.getElementById('mini-dashboard-criterio');
    if (criterioSelect) {
        criterioSelect.addEventListener('change', () => carregarMiniDashboardUnidades());
    }
    const pacienteId = new URLSearchParams(window.location.search).get('paciente');
    if (pacienteId) {
        setTimeout(() => {
            selecionarPaciente(pacienteId);
            window.history.replaceState({}, document.title, '/pacientes');
        }, 1000);
    }
});

// Configurar eventos
function configurarEventos() {
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeoutPesquisa);
        timeoutPesquisa = setTimeout(() => filtrarPacientes(e.target.value), 300);
    });
    prevBtn.addEventListener('click', () => { if (paginaAtual > 1) { paginaAtual--; renderizarPacientes(); } });
    nextBtn.addEventListener('click', () => {
        const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
        if (paginaAtual < totalPaginas) { paginaAtual++; renderizarPacientes(); }
    });
    closePerfilBtn.addEventListener('click', fecharPerfil);
}

// Mini-dashboard: ranking das melhores unidades
async function carregarMiniDashboardUnidades() {
    const lista = document.getElementById('mini-dashboard-lista');
    if (!lista) return;
    const criterio = (document.getElementById('mini-dashboard-criterio') || {}).value || 'inicio_pre_natal_antes_12s';
    lista.innerHTML = '<span class="mini-dashboard-loading">Carregando...</span>';
    try {
        const res = await fetch(`/api/ranking_unidades?criterio=${encodeURIComponent(criterio)}&limite=5`);
        const data = await res.json();
        if (!data.success || !data.ranking || data.ranking.length === 0) {
            lista.innerHTML = '<span class="mini-dashboard-empty">Nenhuma unidade com dados para o critério selecionado.</span>';
            return;
        }
        lista.innerHTML = data.ranking.map((r, i) => {
            const rank = i + 1;
            const rankClass = rank <= 3 ? ` rank-${rank}` : '';
            const pct = Math.min(100, Math.max(0, r.percentual));
            return `<div class="mini-dashboard-item${rankClass}">
                <span class="mini-dashboard-item-nome">🏥 ${escapeHtml(r.unidade)}</span>
                <div class="mini-dashboard-item-bar"><div class="mini-dashboard-item-bar-fill" style="width: ${pct}%"></div></div>
                <span class="mini-dashboard-item-pct">${pct.toFixed(1)}%</span>
            </div>`;
        }).join('');
    } catch (e) {
        console.error('Erro ao carregar ranking de unidades:', e);
        lista.innerHTML = '<span class="mini-dashboard-empty">Não foi possível carregar o ranking.</span>';
    }
}

function escapeHtml(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
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
    pacientesFiltrados = termoLower ? todosPacientes.filter(p => (p.identificacao?.nome_gestante || '').toLowerCase().includes(termoLower)) : [...todosPacientes];
    paginaAtual = 1;
    renderizarPacientes();
}

// Renderizar lista de pacientes
function renderizarPacientes() {
    if (pacientesFiltrados.length === 0) {
        pacientesList.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🔍</div><div class="empty-state-text">${searchInput.value.trim() ? 'Nenhum paciente encontrado com esse nome' : 'Nenhum paciente cadastrado'}</div></div>`;
        atualizarInfoPaginacao();
        atualizarBotoesPaginacao();
        return;
    }
    const inicio = (paginaAtual - 1) * pacientesPorPagina;
    const pacientesPagina = pacientesFiltrados.slice(inicio, inicio + pacientesPorPagina);
    pacientesList.innerHTML = pacientesPagina.map(p => {
        const nome = p.identificacao?.nome_gestante || 'Nome não informado';
        const isSelected = pacienteSelecionado?.id === p.id;
        return `<div class="paciente-item ${isSelected ? 'selected' : ''}" data-id="${p.id}" onclick="selecionarPaciente('${p.id}')"><div class="paciente-info"><div class="paciente-nome">${nome}</div><div class="paciente-detalhes">${p.identificacao?.unidade_saude || 'Unidade não informada'}</div><div class="paciente-data">Cadastrado em: ${formatarData(p.data_salvamento)}</div></div></div>`;
    }).join('');
    atualizarInfoPaginacao();
    atualizarBotoesPaginacao();
}

// Selecionar paciente
window.selecionarPaciente = function selecionarPaciente(pacienteId) {
    pacienteSelecionado = pacientesFiltrados.find(p => p.id === pacienteId);
    if (pacienteSelecionado) {
        document.querySelectorAll('.paciente-item').forEach(item => item.classList.remove('selected'));
        document.querySelector(`[data-id="${pacienteId}"]`)?.classList.add('selected');
        exibirPerfil(pacienteSelecionado);
        setTimeout(() => pacientePerfil.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
    }
}

// Exibir perfil do paciente
function exibirPerfil(paciente) {
    const id = paciente.identificacao || {};
    const av = paciente.avaliacao || {};
    
    const campo = (label, valor, cond = true) => cond ? `<div class="perfil-field"><span class="perfil-label">${label}</span><div class="perfil-value">${valor || 'Não informado'}</div></div>` : '';
    const campoTexto = (label, valor, cond = true, estilo = '') => cond && valor ? `<div class="perfil-field" ${estilo ? `style="${estilo}"` : ''}><span class="perfil-label">${label}</span><div class="perfil-value" ${estilo ? `style="${estilo}"` : ''}>${valor}</div></div>` : '';
    
    const html = `
        <div class="perfil-section"><h3>📋 Identificação</h3><div class="perfil-field-grid">
            ${campo('Nome da Gestante', id.nome_gestante)}${campo('Unidade de Saúde', id.unidade_saude)}${campo('Data de Cadastro', formatarData(paciente.data_salvamento))}
        </div></div>
        ${av.ja_ganhou_crianca !== undefined || av.quantidade_filhos !== undefined || av.metodo_preventivo ? `
        <div class="perfil-section"><h3>👶 Histórico Reprodutivo</h3><div class="perfil-field-grid">
            ${campo('Já ganhou a criança?', formatarBoolean(av.ja_ganhou_crianca), av.ja_ganhou_crianca !== undefined)}
            ${campo('Data (gêmeos ou mais)', formatarDataSimples(av.data_ganhou_crianca), av.ja_ganhou_crianca && av.data_ganhou_crianca)}
            ${campo('Quantidade de Filhos', av.quantidade_filhos || 0, av.quantidade_filhos !== undefined)}
            ${campoTexto('Gêneros dos Filhos', av.generos_filhos, av.quantidade_filhos > 0 && av.generos_filhos, 'grid-column: 1 / -1; background: #e8f5e9; padding: 12px; border-radius: 8px; border-left: 4px solid #4caf50; white-space: pre-wrap; word-wrap: break-word;')}
            ${av.metodo_preventivo ? campo('Método Preventivo Atual', `<span class="badge-status">${av.metodo_preventivo}</span>`) : ''}
            ${campoTexto('Especificação do Método Preventivo', av.metodo_preventivo_outros, av.metodo_preventivo === 'Outros' && av.metodo_preventivo_outros, 'grid-column: 1 / -1; background: #fff3e0; padding: 12px; border-radius: 8px; border-left: 4px solid #ff9800; white-space: pre-wrap; word-wrap: break-word;')}
        </div></div>` : ''}
        <div class="perfil-section"><h3>📅 Datas Importantes</h3><div class="perfil-field-grid">
            ${campo('DUM (Data da Última Menstruação)', formatarDataSimples(av.dum))}${campo('DPP (Data Provável do Parto)', formatarDataSimples(av.dpp))}
            ${verificarAlertaAtivo(paciente) ? `
            <div class="perfil-field" style="grid-column: 1 / -1; background: #fff5f5; padding: 16px; border-radius: 8px; border: 2px solid #ffcccc;">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px;">
                    <label class="switch-alerta-perfil"><input type="checkbox" ${isAlertaDesativadoPerfil(paciente.id) ? '' : 'checked'} onchange="toggleAlertaPacientePerfil('${paciente.id}', this.checked)"><span class="slider"></span></label>
                    <div style="flex: 1;"><span class="perfil-label" style="color: #ff6b6b; font-weight: 600;">🚨 Alerta de Parto Próximo</span><div style="margin-top: 8px; font-size: 0.9rem; color: #666;">${formatarMensagemAlerta(paciente)}</div></div>
                </div>
            </div>` : ''}
            ${campo('Próxima Avaliação', av.proxima_avaliacao ? `${formatarDataSimples(av.proxima_avaliacao)}${av.proxima_avaliacao_hora ? ` às ${formatarHora(av.proxima_avaliacao_hora)}` : ''}` : null, !!av.proxima_avaliacao)}
        </div></div>
        <div class="perfil-section"><h3>📊 Avaliação</h3><div class="perfil-field-grid">
            ${campo('Início Pré-Natal antes de 12 semanas', formatarBoolean(av.inicio_pre_natal_antes_12s))}
            ${campo('Semanas de Gestação no Início', `${av.inicio_pre_natal_semanas} semanas`, av.inicio_pre_natal_antes_12s && av.inicio_pre_natal_semanas)}
            ${campoTexto('Observações sobre o Início do Pré-Natal', av.inicio_pre_natal_observacao, av.inicio_pre_natal_antes_12s && av.inicio_pre_natal_observacao, 'grid-column: 1 / -1; background: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 4px solid #2196f3; white-space: pre-wrap; word-wrap: break-word;')}
            ${campo('Consultas de Pré-Natal', av.consultas_pre_natal || 0)}
            ${campo('Vacinas Completas', `<span class="badge-status ${getBadgeClassVacina(av.vacinas_completas)}">${av.vacinas_completas || 'Não avaliado'}</span>`)}
            ${campo('Plano de Parto', formatarBoolean(av.plano_parto))}${campo('Participou de Grupos', formatarBoolean(av.participou_grupos))}
            ${campo('Avaliação Odontológica', formatarBoolean(av.avaliacao_odontologica))}${campo('Estratificação', formatarBoolean(av.estratificacao))}
            ${campoTexto('Problema Identificado na Estratificação', av.estratificacao_problema, av.estratificacao && av.estratificacao_problema, 'grid-column: 1 / -1; background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; white-space: pre-wrap; word-wrap: break-word;')}
            ${campo('Cartão Pré-Natal Completo', formatarBoolean(av.cartao_pre_natal_completo))}
            ${campo('Possui Bolsa Família', formatarBoolean(av.possui_bolsa_familia))}
            ${campo('Tem vacina de COVID', formatarBoolean(av.tem_vacina_covid))}
            ${campo('Plano de parto entregue por', av.plano_parto_entregue_por_unidade || 'Nenhuma')}
        </div></div>
        ${av.ganhou_kit !== undefined ? `<div class="perfil-section"><h3>🎁 KIT</h3><div class="perfil-field-grid">
            ${campo('Ganhou o KIT?', formatarBoolean(av.ganhou_kit))}${campo('Tipo(s) de KIT', formatarKitTipo(av.kit_tipo), av.ganhou_kit && av.kit_tipo)}
        </div></div>` : ''}
        <div class="perfil-actions"><button class="btn btn-danger" onclick="confirmarExclusaoPaciente('${paciente.id}')">🗑️ Excluir Paciente</button></div>
    `;
    perfilContent.innerHTML = html;
    pacientePerfil.style.display = 'block';
}

// Fechar perfil
function fecharPerfil() {
    pacienteSelecionado = null;
    pacientePerfil.style.display = 'none';
    document.querySelectorAll('.paciente-item').forEach(item => item.classList.remove('selected'));
}

// Atualizar informações de paginação
function atualizarInfoPaginacao() {
    const total = pacientesFiltrados.length;
    const inicio = total === 0 ? 0 : (paginaAtual - 1) * pacientesPorPagina + 1;
    const fim = Math.min(paginaAtual * pacientesPorPagina, total);
    paginationInfo.textContent = total === 0 ? 'Nenhum paciente encontrado' : `Mostrando ${inicio} a ${fim} de ${total} paciente(s)`;
}

// Atualizar botões de paginação
function atualizarBotoesPaginacao() {
    const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
    prevBtn.disabled = paginaAtual <= 1;
    nextBtn.disabled = paginaAtual >= totalPaginas || totalPaginas === 0;
    pageInfo.textContent = totalPaginas > 0 ? `Página ${paginaAtual} de ${totalPaginas}` : 'Página 1';
}

// Funções auxiliares
function formatarData(dataString) {
    if (!dataString) return 'Data não disponível';
    const d = new Date(dataString);
    if (isNaN(d.getTime())) return 'Data não disponível';
    return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatarBoolean(valor) {
    if (valor === true) return '<span class="badge-status badge-success">Sim</span>';
    if (valor === false) return '<span class="badge-status badge-danger">Não</span>';
    return '<span class="badge-status badge-warning">Não informado</span>';
}

function getBadgeClassVacina(valor) {
    if (!valor) return 'badge-warning';
    const v = valor.toLowerCase();
    if (v.includes('completa') || v === 'completo') return 'badge-success';
    if (v.includes('incompleta') || v === 'incompleto') return 'badge-danger';
    return 'badge-warning';
}

function formatarDataSimples(dataString) {
    if (!dataString) return null;
    try {
        const [ano, mes, dia] = dataString.split('-');
        return (ano && mes && dia) ? `${dia}/${mes}/${ano}` : dataString;
    } catch (e) {
        return dataString;
    }
}

function formatarHora(horaString) {
    if (!horaString) return null;
    try {
        const [hora, minuto] = horaString.split(':');
        return (hora && minuto) ? `${hora}:${minuto}` : horaString;
    } catch (e) {
        return horaString;
    }
}

function formatarKitTipo(kitTipo) {
    if (!kitTipo) return 'Não informado';
    const tipos = kitTipo.split(',').map(t => t.trim());
    const labels = { MP: 'MP (Mae piraporence)', FM: 'FM (Filhos de Minas)' };
    return tipos.map(tipo => `<span class="badge-status badge-info" style="margin-right: 5px;">${labels[tipo] || tipo}</span>`).join('');
}

function verificarAlertaAtivo(paciente) {
    return typeof window.pacienteTemAlertaAtivo === 'function' ? window.pacienteTemAlertaAtivo(paciente) : false;
}

function isAlertaDesativadoPerfil(pacienteId) {
    return typeof window.isAlertaDesativado === 'function' ? window.isAlertaDesativado(pacienteId) : false;
}

function formatarMensagemAlerta(paciente) {
    if (!paciente?.avaliacao?.dpp || typeof window.calcularDiasAteDPP !== 'function') return '';
    const dias = window.calcularDiasAteDPP(paciente.avaliacao.dpp);
    if (dias === null) return '';
    if (dias < 0) return `Parto previsto há ${Math.abs(dias)} dia(s)`;
    if (dias === 0) return 'Parto previsto para hoje!';
    if (dias === 1) return 'Parto previsto para amanhã!';
    return `Parto previsto em ${dias} dias`;
}

window.toggleAlertaPacientePerfil = function toggleAlertaPacientePerfil(pacienteId, ativo) {
    if (typeof window.toggleAlertaPaciente === 'function') {
        window.toggleAlertaPaciente(pacienteId, ativo);
        if (pacienteSelecionado?.id === pacienteId) {
            setTimeout(() => exibirPerfil(pacienteSelecionado), 100);
        }
    }
}

function mostrarErro(mensagem) {
    pacientesList.innerHTML = `<div class="empty-state"><div class="empty-state-icon">⚠️</div><div class="empty-state-text">${mensagem}</div></div>`;
}

async function confirmarExclusaoPaciente(pacienteId) {
    const paciente = todosPacientes.find(p => p.id === pacienteId);
    const nome = paciente?.identificacao?.nome_gestante || 'este paciente';
    if (confirm(`Tem certeza que deseja excluir o paciente "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        await excluirPaciente(pacienteId);
    }
}

async function excluirPaciente(pacienteId) {
    try {
        const response = await fetch(`/api/deletar_paciente/${pacienteId}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            fecharPerfil();
            await carregarPacientes();
            alert('Paciente excluído com sucesso!');
        } else {
            alert(data.message || 'Erro ao excluir paciente');
        }
    } catch (error) {
        console.error('Erro ao excluir paciente:', error);
        alert('Erro ao excluir paciente. Por favor, tente novamente.');
    }
}
