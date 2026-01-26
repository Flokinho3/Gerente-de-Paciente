// Módulo de comparação de indicadores

let comparacaoChartCounter = 0;
const comparacaoCharts = new Map();

// Função auxiliar para obter o título amigável de um filtro
function obterTituloAmigavel(filtro) {
    const filtroSelect = document.getElementById('comparacao-filtro');
    if (filtroSelect) {
        const option = filtroSelect.querySelector(`option[value="${filtro}"]`);
        if (option) {
            return option.text;
        }
    }
    return filtro;
}

// Variáveis para gerenciar seleção de unidades
let todasUnidades = [];
let unidadesSelecionadas = new Set();
let termoPesquisaUnidade = '';

// Tornar comparacaoCharts disponível globalmente para outras funções
window.comparacaoCharts = comparacaoCharts;

// Função para criar um gráfico de comparação
async function criarGraficoComparacao(filtro, estilo, unidadeSaude = null) {
    const chartId = `comparacao-chart-${comparacaoChartCounter++}`;
    const containerId = `comparacao-container-${chartId}`;
    
    let indicadorInfo = window.getIndicadorData(filtro, unidadeSaude);
    
    if (!indicadorInfo && unidadeSaude !== null) {
        indicadorInfo = await window.buscarIndicadorPorUnidade(filtro, unidadeSaude);
    }
    
    if (!indicadorInfo && estilo !== 'line') return null;
    
    let title = indicadorInfo ? indicadorInfo.title : obterTituloAmigavel(filtro);
    if (unidadeSaude) {
        title += ` - ${unidadeSaude}`;
    } else {
        title += ' - Geral';
    }
    
    const container = document.getElementById('comparacao-charts-container');
    const chartCard = document.createElement('div');
    chartCard.className = 'comparacao-chart-card';
    chartCard.id = `card-${chartId}`;
    chartCard.innerHTML = `
        <div class="comparacao-chart-header">
            <h3 class="comparacao-chart-title">${title}</h3>
            <button class="btn-remover-chart" onclick="removerGraficoComparacao('${chartId}')">✕ Remover</button>
        </div>
        <div class="comparacao-chart-container">
            <canvas id="${containerId}"></canvas>
        </div>
    `;
    container.appendChild(chartCard);
    
    if (estilo === 'line') {
        window.criarGraficoTemporal(filtro, chartId, containerId, container, unidadeSaude);
        return { chartId, chart: null };
    }
    
    if (!indicadorInfo) return null;
    
    let dataArray = [];
    if (filtro === 'vacinas_completas') {
        dataArray = [
            indicadorInfo.data.completa,
            indicadorInfo.data.incompleta,
            indicadorInfo.data.nao_avaliado
        ];
    } else if (filtro === 'consultas_pre_natal') {
        dataArray = [
            indicadorInfo.data.mais_6,
            indicadorInfo.data.ate_6
        ];
    } else {
        dataArray = [
            indicadorInfo.data.sim,
            indicadorInfo.data.nao
        ];
    }
    
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: estilo === 'bar' ? 'top' : 'bottom'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                        return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                    }
                }
            }
        }
    };
    
    if (estilo === 'bar') {
        chartOptions.scales = {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        };
        chartOptions.plugins.legend.display = false;
    }
    
    const dataset = {
        label: 'Pacientes',
        data: dataArray,
        backgroundColor: indicadorInfo.backgroundColor,
        borderWidth: estilo === 'pie' || estilo === 'doughnut' ? 2 : 1,
        borderColor: estilo === 'pie' || estilo === 'doughnut' ? '#fff' : undefined
    };
    
    const chartConfig = {
        type: estilo,
        data: {
            labels: indicadorInfo.labels,
            datasets: [dataset]
        },
        options: chartOptions
    };
    
    const ctx = document.getElementById(containerId);
    const chart = new Chart(ctx, chartConfig);
    
    comparacaoCharts.set(chartId, chart);
    return { chartId, chart };
}

function escapeHtmlComparacao(s) {
    if (s == null || s === '') return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

// Função para adicionar gráfico ao comparativo - Usa /api/ranking_unidades e um único mini-dashboard
async function adicionarGraficoComparacao() {
    const filtro = document.getElementById('comparacao-filtro').value;
    const container = document.getElementById('comparacao-charts-container');
    if (!container) return;

    try {
        let url = `/api/ranking_unidades?criterio=${encodeURIComponent(filtro)}&limite=0`;
        if (unidadesSelecionadas.size > 0) {
            url += '&unidades=' + encodeURIComponent([...unidadesSelecionadas].join(','));
        }
        const res = await fetch(url);
        const data = await res.json();
        if (!data.success) {
            alert(data.message || 'Erro ao carregar ranking.');
            return;
        }
        const ranking = data.ranking || [];
        let titulo = obterTituloAmigavel(filtro);
        if (titulo === filtro && data.criterio_label) {
            titulo = data.criterio_label;
        }
        const comparacaoId = `comparacao-${Date.now()}`;
        const comparacaoSection = document.createElement('div');
        comparacaoSection.className = 'comparacao-unidades-section';
        comparacaoSection.id = comparacaoId;
        const listaHtml = ranking.length === 0
            ? '<p class="comparacao-ranking-empty">Nenhuma unidade com dados para este indicador.</p>'
            : ranking.map((r, i) => {
                const rank = i + 1;
                const rankCl = rank <= 3 ? ` rank-${rank}` : '';
                const pct = Math.min(100, Math.max(0, r.percentual));
                return `<div class="mini-dashboard-item${rankCl}"><span class="mini-dashboard-item-nome">🏥 ${escapeHtmlComparacao(r.unidade)}</span><div class="mini-dashboard-item-bar"><div class="mini-dashboard-item-bar-fill" style="width:${pct}%"></div></div><span class="mini-dashboard-item-pct">${pct.toFixed(1)}%</span></div>`;
            }).join('');
        const chartId = `comparacao-chart-${comparacaoChartCounter++}`;
        const estiloSelecionado = document.getElementById('comparacao-estilo')?.value || 'bar';
        const chartCanvasId = `comparacao-ranking-canvas-${chartId}`;
        comparacaoSection.innerHTML = `
            <div class="comparacao-section-header">
                <h3 class="comparacao-section-title">🏆 ${escapeHtmlComparacao(titulo)}</h3>
                <button class="btn-remover-comparacao" onclick="removerComparacaoCompleta('${comparacaoId}')">✕ Remover Comparação</button>
            </div>
            <div class="comparacao-ranking-lista">${listaHtml}</div>
            <div class="comparacao-ranking-chart" data-comparacao-id="${comparacaoId}" data-chart-id="${chartId}">
                <div class="comparacao-ranking-chart-header">
                    <h4 class="comparacao-ranking-chart-title">📊 Comparação entre unidades</h4>
                </div>
                <div class="comparacao-ranking-chart-canvas" id="comparacao-ranking-canvas-wrap-${chartId}">
                    <canvas id="${chartCanvasId}"></canvas>
                </div>
            </div>
        `;
        container.appendChild(comparacaoSection);

        if (ranking.length === 0) {
            comparacaoSection.querySelector(`[data-chart-id="${chartId}"]`)?.remove();
            return;
        }

        const canvasWrapper = document.getElementById(`comparacao-ranking-canvas-wrap-${chartId}`);
        if (canvasWrapper) {
            const chartHeight = Math.max(260, ranking.length * 28);
            canvasWrapper.style.height = `${chartHeight}px`;
        }
        const labels = ranking.map(item => item.unidade);
        const valores = ranking.map(item => item.percentual);
        const baseColors = [
            '#2f7d6d',
            '#4f9f89',
            '#7fc8b0',
            '#f5a623',
            '#f26d6d',
            '#6c7bd1',
            '#56b3b4',
            '#d27ab2',
            '#8bc34a',
            '#ffb74d',
            '#90a4ae',
            '#ab47bc'
        ];
        const cores = labels.map((_, idx) => baseColors[idx % baseColors.length]);
        const ctx = document.getElementById(chartCanvasId);
        const tipoRanking = ['pie', 'doughnut'].includes(estiloSelecionado) ? estiloSelecionado : 'bar';
        const chart = new Chart(ctx, {
            type: tipoRanking,
            data: {
                labels,
                datasets: [{
                    label: titulo,
                    data: valores,
                    backgroundColor: tipoRanking === 'bar'
                        ? cores.map(c => `${c}cc`)
                        : cores,
                    borderColor: cores,
                    borderWidth: tipoRanking === 'bar' ? 1 : 2,
                    borderRadius: tipoRanking === 'bar' ? 6 : 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: tipoRanking === 'bar' ? 'y' : 'x',
                plugins: {
                    legend: { display: tipoRanking !== 'bar' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const pct = tipoRanking === 'bar'
                                    ? (context.parsed.x ?? 0)
                                    : (context.parsed ?? 0);
                                return `${pct.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: tipoRanking === 'bar'
                    ? {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: value => `${value}%`
                            }
                        },
                        y: {
                            ticks: {
                                autoSkip: false,
                                font: { size: 11 }
                            }
                        }
                    }
                    : {}
            }
        });
        comparacaoCharts.set(chartId, chart);
    } catch (e) {
        console.error('Erro ao carregar ranking de unidades:', e);
        alert('Erro ao carregar ranking. Tente novamente.');
    }
}

// Função auxiliar para criar gráfico dentro de um grid específico
async function criarGraficoComparacaoNoGrid(filtro, estilo, unidadeSaude, gridContainer, comparacaoId) {
    const chartId = `comparacao-chart-${comparacaoChartCounter++}`;
    const containerId = `comparacao-container-${chartId}`;
    
    let indicadorInfo = window.getIndicadorData(filtro, unidadeSaude);
    
    if (!indicadorInfo && unidadeSaude !== null) {
        indicadorInfo = await window.buscarIndicadorPorUnidade(filtro, unidadeSaude);
    }
    
    // Se não encontrou indicadorInfo e não é gráfico de linha, tentar buscar dados genéricos
    if (!indicadorInfo && estilo !== 'line' && unidadeSaude === null) {
        // Tentar buscar dados genéricos para o filtro
        indicadorInfo = await window.buscarIndicadorPorUnidade(filtro, null);
    }
    
    if (!indicadorInfo && estilo !== 'line') {
        return null;
    }
    
    let title = indicadorInfo ? indicadorInfo.title : obterTituloAmigavel(filtro);
    if (unidadeSaude) {
        title = `🏥 ${unidadeSaude}`;
    } else {
        title = '📊 Geral';
    }
    
    const chartCard = document.createElement('div');
    chartCard.className = 'comparacao-chart-card';
    chartCard.id = `card-${chartId}`;
    chartCard.setAttribute('data-comparacao-id', comparacaoId);
    chartCard.innerHTML = `
        <div class="comparacao-chart-header">
            <h4 class="comparacao-chart-title" style="margin: 0;">${title}</h4>
        </div>
        <div class="comparacao-chart-container">
            <canvas id="${containerId}"></canvas>
        </div>
    `;
    gridContainer.appendChild(chartCard);
    
    if (estilo === 'line') {
        // Para gráficos temporais, precisamos garantir que o chart seja armazenado corretamente
        window.criarGraficoTemporal(filtro, chartId, containerId, gridContainer, unidadeSaude);
        // O gráfico será armazenado pela função criarGraficoTemporal através de window.comparacaoCharts
        return { chartId, chart: null };
    }
    
    if (!indicadorInfo) return null;
    
    let dataArray = [];
    if (filtro === 'vacinas_completas') {
        dataArray = [
            indicadorInfo.data.completa,
            indicadorInfo.data.incompleta,
            indicadorInfo.data.nao_avaliado
        ];
    } else if (filtro === 'consultas_pre_natal') {
        dataArray = [
            indicadorInfo.data.mais_6,
            indicadorInfo.data.ate_6
        ];
    } else {
        dataArray = [
            indicadorInfo.data.sim,
            indicadorInfo.data.nao
        ];
    }
    
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: estilo === 'bar' ? 'top' : 'bottom'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                        return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                    }
                }
            }
        }
    };
    
    if (estilo === 'bar') {
        chartOptions.scales = {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        };
        chartOptions.plugins.legend.display = false;
    }
    
    const dataset = {
        label: 'Pacientes',
        data: dataArray,
        backgroundColor: indicadorInfo.backgroundColor,
        borderWidth: estilo === 'pie' || estilo === 'doughnut' ? 2 : 1,
        borderColor: estilo === 'pie' || estilo === 'doughnut' ? '#fff' : undefined
    };
    
    const chartConfig = {
        type: estilo,
        data: {
            labels: indicadorInfo.labels,
            datasets: [dataset]
        },
        options: chartOptions
    };
    
    const ctx = document.getElementById(containerId);
    const chart = new Chart(ctx, chartConfig);
    
    comparacaoCharts.set(chartId, chart);
    return { chartId, chart };
}

// Função para remover toda uma comparação completa
window.removerComparacaoCompleta = function(comparacaoId) {
    const cards = document.querySelectorAll(`[data-comparacao-id="${comparacaoId}"]`);
    cards.forEach(card => {
        const chartId = card.getAttribute('data-chart-id') || (card.id || '').replace('card-', '');
        if (chartId) {
            const chart = comparacaoCharts.get(chartId);
            if (chart) {
                chart.destroy();
                comparacaoCharts.delete(chartId);
            }
        }
    });
    
    const section = document.getElementById(comparacaoId);
    if (section) {
        section.remove();
    } else {
        // Fallback: procurar pela seção que contém o grid
        const grid = document.getElementById(`grid-${comparacaoId}`);
        if (grid) {
            grid.closest('.comparacao-unidades-section')?.remove();
        }
    }
}

// Função para remover gráfico do comparativo
window.removerGraficoComparacao = function(chartId) {
    const chart = comparacaoCharts.get(chartId);
    if (chart) {
        chart.destroy();
        comparacaoCharts.delete(chartId);
    }
    
    const card = document.getElementById(`card-${chartId}`);
    if (card) {
        card.remove();
    }
}

// Função para atualizar lista de todas as unidades
window.atualizarTodasUnidades = function(unidades) {
    todasUnidades = unidades || [];
    if (document.getElementById('unidades-selecionadas')) {
        atualizarListaUnidades();
    }
}

// Funções para gerenciar seleção de unidades
function configurarSelecaoUnidades() {
    const unidadeSearch = document.getElementById('unidade-search');
    const unidadesLista = document.getElementById('unidades-lista');
    const unidadesSelecionadasList = document.getElementById('unidades-selecionadas');
    
    if (!unidadeSearch || !unidadesLista || !unidadesSelecionadasList) return;
    
    // Carregar unidades quando disponíveis
    if (window.obterUnidadesSaude) {
        todasUnidades = window.obterUnidadesSaude();
        atualizarListaUnidades();
    }
    
    // Event listener para pesquisa
    unidadeSearch.addEventListener('input', function(e) {
        termoPesquisaUnidade = e.target.value.toLowerCase();
        atualizarListaUnidades();
    });
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(e) {
        if (!unidadesLista.contains(e.target) && e.target !== unidadeSearch) {
            unidadesLista.querySelector('.unidades-lista-dropdown-content')?.classList.remove('show');
        }
    });
    
    // Abrir dropdown ao focar no campo de pesquisa
    unidadeSearch.addEventListener('focus', function() {
        const dropdown = unidadesLista.querySelector('.unidades-lista-dropdown-content');
        if (dropdown) {
            dropdown.classList.add('show');
        }
    });
}

function atualizarListaUnidades() {
    const unidadesLista = document.getElementById('unidades-lista');
    if (!unidadesLista) return;
    
    let dropdown = unidadesLista.querySelector('.unidades-lista-dropdown-content');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'unidades-lista-dropdown-content';
        unidadesLista.appendChild(dropdown);
    }
    
    dropdown.innerHTML = '';
    
    // Filtrar unidades pelo termo de pesquisa
    const unidadesFiltradas = todasUnidades.filter(unidade => 
        unidade.toLowerCase().includes(termoPesquisaUnidade)
    );
    
    if (unidadesFiltradas.length === 0) {
        dropdown.innerHTML = '<div class="unidade-item-dropdown" style="text-align: center; color: var(--text-muted);">Nenhuma unidade encontrada</div>';
    } else {
        unidadesFiltradas.forEach(unidade => {
            const item = document.createElement('div');
            item.className = 'unidade-item-dropdown';
            if (unidadesSelecionadas.has(unidade)) {
                item.classList.add('selecionada');
            }
            item.innerHTML = `<div class="unidade-item-nome">🏥 ${unidade}</div>`;
            item.addEventListener('click', () => toggleUnidade(unidade));
            dropdown.appendChild(item);
        });
    }
    
    atualizarListaUnidadesSelecionadas();
}

function toggleUnidade(unidade) {
    if (unidadesSelecionadas.has(unidade)) {
        unidadesSelecionadas.delete(unidade);
    } else {
        unidadesSelecionadas.add(unidade);
    }
    atualizarListaUnidades();
}

function atualizarListaUnidadesSelecionadas() {
    const unidadesSelecionadasList = document.getElementById('unidades-selecionadas');
    if (!unidadesSelecionadasList) return;
    
    unidadesSelecionadasList.innerHTML = '';
    
    if (unidadesSelecionadas.size === 0) {
        const tag = document.createElement('div');
        tag.className = 'unidade-selecionada-tag';
        tag.style.background = 'var(--secondary)';
        tag.textContent = '📊 Todas as unidades';
        unidadesSelecionadasList.appendChild(tag);
    } else {
        unidadesSelecionadas.forEach(unidade => {
            const tag = document.createElement('div');
            tag.className = 'unidade-selecionada-tag';
            tag.innerHTML = `
                <span>🏥 ${unidade}</span>
                <span class="remove-unidade" onclick="removerUnidade('${unidade}')">✕</span>
            `;
            unidadesSelecionadasList.appendChild(tag);
        });
    }
}

window.removerUnidade = function(unidade) {
    unidadesSelecionadas.delete(unidade);
    atualizarListaUnidades();
}

// Exportar funções
window.criarGraficoComparacao = criarGraficoComparacao;
window.adicionarGraficoComparacao = adicionarGraficoComparacao;
window.configurarSelecaoUnidades = configurarSelecaoUnidades;