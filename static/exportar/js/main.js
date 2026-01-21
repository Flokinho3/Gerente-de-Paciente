// Gerenciamento da página de exportação
const COLUNAS_DISPONIVEIS = [
    { value: 'identificacao.nome_gestante', label: 'Nome da Gestante' },
    { value: 'identificacao.unidade_saude', label: 'Unidade de Saúde' },
    { value: 'data_salvamento', label: 'Data de Cadastro' },
    { value: 'avaliacao.inicio_pre_natal_antes_12s', label: 'Início pré-natal antes de 12 semanas' },
    { value: 'avaliacao.consultas_pre_natal', label: 'Consultas de pré-natal' },
    { value: 'avaliacao.vacinas_completas', label: 'Vacinas completas' },
    { value: 'avaliacao.plano_parto', label: 'Plano de parto' },
    { value: 'avaliacao.participou_grupos', label: 'Participou de grupos' },
    { value: 'avaliacao.avaliacao_odontologica', label: 'Avaliação odontológica' },
    { value: 'avaliacao.estratificacao', label: 'Estratificação' },
    { value: 'avaliacao.cartao_pre_natal_completo', label: 'Cartão pré-natal completo' }
];

let formatoSelecionado = null;
let totalPacientes = 0;
let colunasPersonalizadas = [];
let unidadesDisponiveis = [];
let pacientesFiltrados = [];

// Elementos DOM
const formatCards = document.querySelectorAll('.format-card');
const exportBtn = document.getElementById('exportBtn');
const totalPacientesSpan = document.getElementById('totalPacientes');
const statusMessage = document.getElementById('statusMessage');
const filtroUpas = document.getElementById('filterUpas');
const filtroKitis = document.getElementById('filterKitis');
const filtrosResumo = document.getElementById('filtrosResumo');
const togglePersonalizar = document.getElementById('togglePersonalizar');
const customPanel = document.getElementById('customPanel');
const customColumnSelect = document.getElementById('customColumnSelect');
const customAddBtn = document.getElementById('customAddBtn');
const customList = document.getElementById('customList');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarTotalPacientes();
    carregarUnidades();
    configurarEventos();
    popularOpcoesPersonalizadas();
    atualizarResumoFiltros();
});

// Configurar eventos
function configurarEventos() {
    formatCards.forEach(card => {
        card.addEventListener('click', () => {
            formatCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            formatoSelecionado = card.dataset.format;
            exportBtn.disabled = false;
            ocultarStatus();
        });
    });

    exportBtn.addEventListener('click', () => {
        if (formatoSelecionado) {
            exportarDados(formatoSelecionado);
        }
    });

    filtroUpas?.addEventListener('change', () => {
        if (filtroUpas.value) {
            filtroKitis.value = '';
        }
        aplicarFiltroUnidade();
        atualizarResumoFiltros();
    });

    filtroKitis?.addEventListener('change', () => {
        if (filtroKitis.value) {
            filtroUpas.value = '';
        }
        aplicarFiltroUnidade();
        atualizarResumoFiltros();
    });

    togglePersonalizar?.addEventListener('change', () => {
        customPanel?.classList.toggle('active', togglePersonalizar.checked);
        atualizarResumoFiltros();
    });

    customAddBtn?.addEventListener('click', () => {
        adicionarColunaPersonalizada();
    });
}

// Carregar total de pacientes
async function carregarTotalPacientes() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();

        if (data.success) {
            totalPacientes = data.total || 0;
            totalPacientesSpan.textContent = totalPacientes;
        } else {
            totalPacientesSpan.textContent = 'Erro ao carregar';
        }
    } catch (error) {
        console.error('Erro ao carregar total de pacientes:', error);
        totalPacientesSpan.textContent = 'Erro';
    }
}

// Carregar unidades de saúde disponíveis
async function carregarUnidades() {
    try {
        const response = await fetch('/api/unidades_saude');
        const data = await response.json();

        if (data.success && data.unidades) {
            unidadesDisponiveis = data.unidades;
            separarUnidadesPorTipo();
        }
    } catch (error) {
        console.error('Erro ao carregar unidades:', error);
    }
}

// Separar unidades por tipo (UPAs e Kitis)
function separarUnidadesPorTipo() {
    if (!filtroUpas || !filtroKitis) return;

    const upas = [];
    const kitis = [];

    unidadesDisponiveis.forEach(unidade => {
        const unidadeUpper = unidade.toUpperCase();
        if (unidadeUpper.includes('UPA')) {
            upas.push(unidade);
        } else if (unidadeUpper.includes('KITIS') || unidadeUpper.includes('KITI')) {
            kitis.push(unidade);
        }
    });

    // Popular select de UPAs
    upas.forEach(upa => {
        const option = document.createElement('option');
        option.value = upa;
        option.textContent = upa;
        filtroUpas.appendChild(option);
    });

    // Popular select de Kitis
    kitis.forEach(kitis => {
        const option = document.createElement('option');
        option.value = kitis;
        option.textContent = kitis;
        filtroKitis.appendChild(option);
    });
}

// Aplicar filtro por unidade
async function aplicarFiltroUnidade() {
    const unidadeSelecionada = filtroUpas?.value || filtroKitis?.value;
    
    if (!unidadeSelecionada) {
        pacientesFiltrados = [];
        atualizarTotalFiltrado();
        return;
    }

    try {
        const response = await fetch(`/api/pacientes?unidade_saude=${encodeURIComponent(unidadeSelecionada)}`);
        const data = await response.json();

        if (data.success && data.pacientes) {
            pacientesFiltrados = data.pacientes;
            atualizarTotalFiltrado();
        }
    } catch (error) {
        console.error('Erro ao filtrar pacientes:', error);
        pacientesFiltrados = [];
        atualizarTotalFiltrado();
    }
}

// Atualizar contador de pacientes filtrados
function atualizarTotalFiltrado() {
    const total = pacientesFiltrados.length;
    totalPacientesSpan.textContent = `${total} ${total === 1 ? 'paciente encontrado' : 'pacientes encontrados'}`;
}

// Exportar dados
async function exportarDados(formato) {
    try {
        mostrarStatus('Preparando arquivo para download...', 'loading');
        exportBtn.disabled = true;

        const params = construirFiltrosParams();
        const query = params.toString();
        const endpoint = `/api/exportar/${formato}${query ? `?${query}` : ''}`;

        const response = await fetch(endpoint, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Erro ao exportar dados');
        }

        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `pacientes_${new Date().toISOString().split('T')[0]}.${formato === 'excel' ? 'xlsx' : formato === 'word' ? 'docx' : 'txt'}`;
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^";]+)"?/);
            if (match) {
                filename = match[1];
            }
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        mostrarStatus(`✅ Arquivo exportado com sucesso! (${filename})`, 'success');
        setTimeout(() => {
            exportBtn.disabled = false;
        }, 2000);
    } catch (error) {
        console.error('Erro ao exportar:', error);
        mostrarStatus(`❌ Erro ao exportar dados: ${error.message}`, 'error');
        exportBtn.disabled = false;
    }
}

// Mostrar mensagem de status
function mostrarStatus(mensagem, tipo = 'success') {
    statusMessage.textContent = mensagem;
    statusMessage.className = `status-message status-${tipo}`;
    statusMessage.style.display = 'block';
}

// Ocultar mensagem de status
function ocultarStatus() {
    statusMessage.style.display = 'none';
}

// Popular select com colunas disponíveis
function popularOpcoesPersonalizadas() {
    if (!customColumnSelect) return;
    customColumnSelect.innerHTML = '';
    COLUNAS_DISPONIVEIS.forEach(coluna => {
        const option = document.createElement('option');
        option.value = coluna.value;
        option.textContent = coluna.label;
        customColumnSelect.appendChild(option);
    });
}

// Adicionar coluna personalizada
function adicionarColunaPersonalizada() {
    if (!togglePersonalizar?.checked) return;
    const value = customColumnSelect?.value;
    if (!value) return;
    if (colunasPersonalizadas.includes(value)) return;
    colunasPersonalizadas.push(value);
    renderizarColunasPersonalizadas();
    atualizarResumoFiltros();
}

// Renderizar chips das colunas selecionadas
function renderizarColunasPersonalizadas() {
    if (!customList) return;
    customList.innerHTML = '';

    if (colunasPersonalizadas.length === 0) {
        const placeholder = document.createElement('span');
        placeholder.className = 'custom-placeholder';
        placeholder.textContent = 'Nenhuma coluna selecionada.';
        customList.appendChild(placeholder);
        return;
    }

    colunasPersonalizadas.forEach(coluna => {
        const chip = document.createElement('span');
        chip.className = 'custom-chip';
        const label = obterLabelColuna(coluna);

        const labelSpan = document.createElement('span');
        labelSpan.textContent = label;
        chip.appendChild(labelSpan);

        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = '×';
        button.addEventListener('click', () => {
            colunasPersonalizadas = colunasPersonalizadas.filter(v => v !== coluna);
            renderizarColunasPersonalizadas();
            atualizarResumoFiltros();
        });

        chip.appendChild(button);
        customList.appendChild(chip);
    });
}

function obterLabelColuna(valor) {
    return COLUNAS_DISPONIVEIS.find(col => col.value === valor)?.label || valor;
}

// Atualiza resumo dos filtros ativos
function atualizarResumoFiltros() {
    const partes = [];
    
    if (filtroUpas?.value) {
        partes.push(`UPA: ${filtroUpas.options[filtroUpas.selectedIndex].text}`);
    }
    
    if (filtroKitis?.value) {
        partes.push(`Kitis: ${filtroKitis.options[filtroKitis.selectedIndex].text}`);
    }

    let texto = partes.length ? `Filtros ativos: ${partes.join(' · ')}` : 'Nenhum filtro ativo.';

    if (togglePersonalizar?.checked) {
        if (colunasPersonalizadas.length > 0) {
            texto += ` · Personalizado: ${colunasPersonalizadas.map(obterLabelColuna).join(', ')}`;
        } else {
            texto += ' · Personalizado ativo (nenhuma coluna selecionada).';
        }
    }

    if (filtrosResumo) {
        filtrosResumo.textContent = texto;
    }
}

// Construir parâmetros query string
function construirFiltrosParams() {
    const params = new URLSearchParams();

    const unidadeSelecionada = filtroUpas?.value || filtroKitis?.value;
    if (unidadeSelecionada) {
        params.append('unidade_saude', unidadeSelecionada);
    }

    if (togglePersonalizar?.checked && colunasPersonalizadas.length > 0) {
        params.append('personalizado', 'true');
        colunasPersonalizadas.forEach(coluna => params.append('colunas', coluna));
    }

    return params;
}
