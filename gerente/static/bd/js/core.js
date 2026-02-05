/**
 * core.js - Funções base e utilitários do sistema
 * Inclui: Loading, formatação, utilitários gerais
 */

// Variáveis globais do sistema
let todosPacientes = [];
let pacientesFiltrados = [];
let paginaAtual = 1;
const pacientesPorPagina = 20;
let colunaOrdenacao = 'nome';
let ordemAscendente = true;
let termoPesquisa = '';

// Elementos de Loading
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingTitle = document.getElementById('loadingTitle');
const loadingMessage = document.getElementById('loadingMessage');
const loadingProgressFill = document.getElementById('loadingProgressFill');
const loadingProgressPercent = document.getElementById('loadingProgressPercent');

// Elementos DOM principais
const searchInput = document.getElementById('searchInput');
const tableBody = document.getElementById('tableBody');
const totalRecords = document.getElementById('totalRecords');
const showingRecords = document.getElementById('showingRecords');
const paginationText = document.getElementById('paginationText');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');

// ==================== FUNÇÕES DE LOADING ====================

function mostrarLoading(titulo = 'Processando...', mensagem = 'Por favor, aguarde enquanto processamos sua solicitação.') {
    if (!loadingOverlay) return;
    loadingTitle.textContent = titulo;
    loadingMessage.textContent = mensagem;
    loadingOverlay.style.display = 'flex';
    atualizarProgressoLoading(0);
    desabilitarBotoesAcao(true);
}

function esconderLoading() {
    if (!loadingOverlay) return;
    loadingOverlay.style.display = 'none';
    desabilitarBotoesAcao(false);
}

function atualizarProgressoLoading(percent) {
    if (!loadingProgressFill || !loadingProgressPercent) return;
    const clampedPercent = Math.max(0, Math.min(100, percent));
    loadingProgressFill.style.width = clampedPercent + '%';
    loadingProgressPercent.textContent = clampedPercent + '%';
}

function desabilitarBotoesAcao(desabilitar) {
    const botoes = [
        document.getElementById('addBtn'),
        document.getElementById('refreshBtn'),
        document.getElementById('backupBtn'),
        document.getElementById('loadBackupBtn'),
        document.getElementById('clearDbBtn'),
        document.getElementById('syncBtn')
    ];

    botoes.forEach(botao => {
        if (botao) {
            botao.disabled = desabilitar;
            botao.style.opacity = desabilitar ? '0.6' : '1';
            botao.style.cursor = desabilitar ? 'not-allowed' : 'pointer';
        }
    });
}

// ==================== FUNÇÕES DE FORMATAÇÃO ====================

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
        return '<span class="badge badge-yes">Sim</span>';
    } else if (valor === false) {
        return '<span class="badge badge-no">Não</span>';
    } else {
        return '<span class="badge badge-unknown">Não informado</span>';
    }
}

function calcularDPPBD(dumStr) {
    if (!dumStr) return null;
    try {
        const d = new Date(dumStr + 'T00:00:00');
        if (isNaN(d.getTime())) return null;
        d.setDate(d.getDate() + 7);
        d.setMonth(d.getMonth() - 3);
        const y = d.getFullYear(), 
              m = String(d.getMonth() + 1).padStart(2, '0'), 
              day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    } catch (e) { 
        return null; 
    }
}

// ==================== FUNÇÕES DE STATUS ====================

function mostrarStatus(mensagem, tipo = 'success') {
    const statusMessage = document.getElementById('statusMessage');
    if (!statusMessage) return;
    
    statusMessage.textContent = mensagem;
    statusMessage.className = `status-message status-${tipo}`;
    statusMessage.style.display = 'block';

    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 3000);
}

function mostrarErro(mensagem) {
    mostrarStatus(mensagem, 'error');
}

// ==================== FUNÇÕES DE PAGINAÇÃO E ORDENAÇÃO ====================

function atualizarIndicadoresOrdenacao() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.classList.remove('asc', 'desc');
        if (header.dataset.column === colunaOrdenacao) {
            header.classList.add(ordemAscendente ? 'asc' : 'desc');
        }
    });
}

function atualizarEstatisticas() {
    if (totalRecords) totalRecords.textContent = todosPacientes.length;
    
    const inicio = (paginaAtual - 1) * pacientesPorPagina;
    const fim = Math.min(inicio + pacientesPorPagina, pacientesFiltrados.length);
    
    if (showingRecords) showingRecords.textContent = `${inicio + 1}-${fim} de ${pacientesFiltrados.length}`;

    const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina) || 1;
    if (paginationText) paginationText.textContent = `Página ${paginaAtual} de ${totalPaginas}`;

    if (prevPageBtn) prevPageBtn.disabled = paginaAtual <= 1;
    if (nextPageBtn) nextPageBtn.disabled = paginaAtual >= totalPaginas || totalPaginas === 0;
}

// ==================== FUNÇÕES DE FILTRO ====================

function filtrarEOrdenar() {
    // Filtrar
    if (termoPesquisa) {
        pacientesFiltrados = todosPacientes.filter(paciente => {
            const nome = (paciente.identificacao?.nome_gestante || '').toLowerCase();
            const unidade = (paciente.identificacao?.unidade_saude || '').toLowerCase();
            return nome.includes(termoPesquisa) || unidade.includes(termoPesquisa);
        });
    } else {
        pacientesFiltrados = [...todosPacientes];
    }

    // Ordenar
    pacientesFiltrados.sort((a, b) => {
        let valorA, valorB;

        switch (colunaOrdenacao) {
            case 'nome':
                valorA = (a.identificacao?.nome_gestante || '').toLowerCase();
                valorB = (b.identificacao?.nome_gestante || '').toLowerCase();
                break;
            case 'unidade':
                valorA = (a.identificacao?.unidade_saude || '').toLowerCase();
                valorB = (b.identificacao?.unidade_saude || '').toLowerCase();
                break;
            case 'data':
                valorA = new Date(a.data_salvamento || 0);
                valorB = new Date(b.data_salvamento || 0);
                break;
            default:
                return 0;
        }

        if (valorA < valorB) return ordemAscendente ? -1 : 1;
        if (valorA > valorB) return ordemAscendente ? 1 : -1;
        return 0;
    });

    atualizarEstatisticas();
}

// ==================== FUNÇÕES DE UNIDADES ====================

async function carregarUnidadesPlanoPartoBD() {
    const sel = document.getElementById('planoPartoEntreguePorUnidade');
    if (!sel) return;
    
    try {
        const r = await fetch('/api/unidades_saude');
        const data = await r.json();
        if (!data.success || !Array.isArray(data.unidades)) return;
        
        data.unidades.filter(Boolean).forEach(u => {
            const opt = document.createElement('option');
            opt.value = u;
            opt.textContent = u;
            sel.appendChild(opt);
        });
    } catch (e) {
        console.warn('Erro ao carregar unidades para plano de parto:', e);
    }
}
