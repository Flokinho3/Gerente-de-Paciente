// Função para determinar a cor do indicador baseado na porcentagem
function getStatusIndicator(percentage) {
    if (percentage >= 70) {
        return '🟢'; // Verde: >= 70%
    } else if (percentage >= 30) {
        return '🟡'; // Amarelo: entre 30% e 70%
    } else {
        return '🔴'; // Vermelho: < 30%
    }
}

// Função para calcular porcentagem do valor positivo
function calculatePositivePercentage(sim, nao) {
    const total = sim + nao;
    if (total === 0) return 0;
    return (sim / total) * 100;
}

// Função para calcular porcentagem do valor positivo (com 3 categorias)
function calculatePositivePercentage3(positivo, negativo, neutro) {
    const total = positivo + negativo + neutro;
    if (total === 0) return 0;
    return (positivo / total) * 100;
}

// Variável global para armazenar os dados dos indicadores
let indicadoresData = null;
let comparacaoChartCounter = 0;
const comparacaoCharts = new Map();

// Função para obter os dados de um indicador específico
function getIndicadorData(filtro) {
    if (!indicadoresData) return null;
    
    const indicadores = {
        'inicio_pre_natal_antes_12s': {
            data: indicadoresData.inicio_pre_natal_antes_12s,
            labels: ['Sim', 'Não'],
            backgroundColor: ['#4CAF50', '#f44336'],
            title: 'Início do pré-natal antes de 12 semanas'
        },
        'consultas_pre_natal': {
            data: indicadoresData.consultas_pre_natal,
            labels: ['≥ 6 consultas', '< 6 consultas'],
            backgroundColor: ['#2196F3', '#FF9800'],
            title: 'Consultas de pré-natal'
        },
        'vacinas_completas': {
            data: indicadoresData.vacinas_completas,
            labels: ['Completo', 'Incompleto', 'Não avaliado'],
            backgroundColor: ['#4CAF50', '#FF9800', '#9E9E9E'],
            title: 'Vacinas completas'
        },
        'plano_parto': {
            data: indicadoresData.plano_parto,
            labels: ['Sim', 'Não'],
            backgroundColor: ['#2196F3', '#f44336'],
            title: 'Plano de parto'
        },
        'participou_grupos': {
            data: indicadoresData.participou_grupos,
            labels: ['Participou', 'Não participou'],
            backgroundColor: ['#4CAF50', '#9E9E9E'],
            title: 'Participação em grupos'
        }
    };
    
    return indicadores[filtro] || null;
}

// Função para criar um gráfico de linha com dados temporais
function criarGraficoTemporal(filtro, chartId, containerId, container) {
    // Buscar dados temporais da API
    fetch(`/api/indicadores/temporais/${filtro}`)
        .then(response => response.json())
        .then(dataTemporal => {
            if (!dataTemporal || !dataTemporal.datas || dataTemporal.datas.length === 0) {
                alert('Não há dados temporais disponíveis para este indicador.');
                return;
            }
            
            // Obter informações do indicador para título
            const indicadorInfo = getIndicadorData(filtro);
            const title = indicadorInfo ? indicadorInfo.title : filtro;
            
            // Preparar dados para gráfico de linha
            const datas = dataTemporal.datas;
            const valores = dataTemporal.valores;
            
            // Determinar as séries de dados baseado no filtro
            let datasets = [];
            
            if (filtro === 'vacinas_completas') {
                datasets = [
                    {
                        label: 'Completo',
                        data: datas.map(data => valores[data]['Completo'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Incompleto',
                        data: datas.map(data => valores[data]['Incompleto'] || 0),
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não avaliado',
                        data: datas.map(data => valores[data]['Não avaliado'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'consultas_pre_natal') {
                datasets = [
                    {
                        label: '≥ 6 consultas',
                        data: datas.map(data => valores[data]['≥ 6 consultas'] || 0),
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: '< 6 consultas',
                        data: datas.map(data => valores[data]['< 6 consultas'] || 0),
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'inicio_pre_natal_antes_12s') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'plano_parto') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'participou_grupos') {
                datasets = [
                    {
                        label: 'Participou',
                        data: datas.map(data => valores[data]['Participou'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não participou',
                        data: datas.map(data => valores[data]['Não participou'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            }
            
            // Criar o gráfico
            const chartConfig = {
                type: 'line',
                data: {
                    labels: datas.map(data => {
                        // Formatar data para exibição (DD/MM/YYYY)
                        const [ano, mes, dia] = data.split('-');
                        return `${dia}/${mes}/${ano}`;
                    }),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            };
            
            const ctx = document.getElementById(containerId);
            const chart = new Chart(ctx, chartConfig);
            
            comparacaoCharts.set(chartId, chart);
        })
        .catch(error => {
            console.error('Erro ao carregar dados temporais:', error);
            alert('Erro ao carregar dados temporais para o gráfico de linha.');
        });
}

// Função para criar um gráfico de comparação
function criarGraficoComparacao(filtro, estilo) {
    const chartId = `comparacao-chart-${comparacaoChartCounter++}`;
    const containerId = `comparacao-container-${chartId}`;
    
    // Obter informações do indicador para título
    const indicadorInfo = getIndicadorData(filtro);
    if (!indicadorInfo && estilo !== 'line') return null;
    
    const title = indicadorInfo ? indicadorInfo.title : filtro;
    
    // Criar o HTML do card do gráfico
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
    
    // Se for gráfico de linha, usar dados temporais
    if (estilo === 'line') {
        criarGraficoTemporal(filtro, chartId, containerId, container);
        return { chartId, chart: null }; // Chart será criado assincronamente
    }
    
    // Para outros estilos, usar dados agregados normais
    if (!indicadorInfo) return null;
    
    // Converter os dados para array
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
    
    // Configurar opções do gráfico
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
    
    // Adicionar escalas para gráficos de barra
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
    
    // Criar o dataset
    const dataset = {
        label: 'Pacientes',
        data: dataArray,
        backgroundColor: indicadorInfo.backgroundColor,
        borderWidth: estilo === 'pie' || estilo === 'doughnut' ? 2 : 1,
        borderColor: estilo === 'pie' || estilo === 'doughnut' ? '#fff' : undefined
    };
    
    // Criar o gráfico
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
    
    return { chartId, chart };
}

// Função para adicionar gráfico ao comparativo
function adicionarGraficoComparacao() {
    const filtro = document.getElementById('comparacao-filtro').value;
    const estilo = document.getElementById('comparacao-estilo').value;
    
    if (!indicadoresData) {
        alert('Aguarde o carregamento dos dados antes de adicionar gráficos.');
        return;
    }
    
    const resultado = criarGraficoComparacao(filtro, estilo);
    if (resultado) {
        comparacaoCharts.set(resultado.chartId, resultado.chart);
    }
}

// Função para remover gráfico do comparativo (global para uso com onclick)
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

// Buscar dados dos indicadores
fetch('/api/indicadores')
    .then(response => response.json())
    .then(data => {
        indicadoresData = data; // Armazenar dados globalmente
        // Calcular porcentagens e atualizar indicadores visuais
        
        // Indicador 1: Início pré-natal antes de 12 semanas
        const perc1 = calculatePositivePercentage(
            data.inicio_pre_natal_antes_12s.sim,
            data.inicio_pre_natal_antes_12s.nao
        );
        document.getElementById('status1').textContent = getStatusIndicator(perc1);

        // Indicador 2: Consultas de pré-natal (>= 6 consultas)
        const perc2 = calculatePositivePercentage(
            data.consultas_pre_natal.mais_6,
            data.consultas_pre_natal.ate_6
        );
        document.getElementById('status2').textContent = getStatusIndicator(perc2);

        // Indicador 3: Vacinas completas
        const perc3 = calculatePositivePercentage3(
            data.vacinas_completas.completa,
            data.vacinas_completas.incompleta,
            data.vacinas_completas.nao_avaliado
        );
        document.getElementById('status3').textContent = getStatusIndicator(perc3);

        // Indicador 4: Plano de parto
        const perc4 = calculatePositivePercentage(
            data.plano_parto.sim,
            data.plano_parto.nao
        );
        document.getElementById('status4').textContent = getStatusIndicator(perc4);

        // Indicador 5: Participação em grupos
        const perc5 = calculatePositivePercentage(
            data.participou_grupos.sim,
            data.participou_grupos.nao
        );
        document.getElementById('status5').textContent = getStatusIndicator(perc5);

        // Gráfico 1: Início pré-natal antes de 12 semanas (Pizza)
        new Chart(document.getElementById('chart1'), {
            type: 'pie',
            data: {
                labels: ['Sim', 'Não'],
                datasets: [{
                    data: [data.inicio_pre_natal_antes_12s.sim, data.inicio_pre_natal_antes_12s.nao],
                    backgroundColor: ['#4CAF50', '#f44336'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
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
            }
        });

        // Gráfico 2: Consultas de pré-natal (Barra)
        new Chart(document.getElementById('chart2'), {
            type: 'bar',
            data: {
                labels: ['≥ 6 consultas', '< 6 consultas'],
                datasets: [{
                    label: 'Pacientes',
                    data: [data.consultas_pre_natal.mais_6, data.consultas_pre_natal.ate_6],
                    backgroundColor: ['#2196F3', '#FF9800'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Gráfico 3: Vacinas completas (Pizza)
        new Chart(document.getElementById('chart3'), {
            type: 'pie',
            data: {
                labels: ['Completo', 'Incompleto', 'Não avaliado'],
                datasets: [{
                    data: [
                        data.vacinas_completas.completa,
                        data.vacinas_completas.incompleta,
                        data.vacinas_completas.nao_avaliado
                    ],
                    backgroundColor: ['#4CAF50', '#FF9800', '#9E9E9E'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
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
            }
        });

        // Gráfico 4: Plano de parto (Barra)
        new Chart(document.getElementById('chart4'), {
            type: 'bar',
            data: {
                labels: ['Sim', 'Não'],
                datasets: [{
                    label: 'Pacientes',
                    data: [data.plano_parto.sim, data.plano_parto.nao],
                    backgroundColor: ['#2196F3', '#f44336'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Gráfico 5: Participação em grupos (Barra)
        new Chart(document.getElementById('chart5'), {
            type: 'bar',
            data: {
                labels: ['Participou', 'Não participou'],
                datasets: [{
                    label: 'Pacientes',
                    data: [data.participou_grupos.sim, data.participou_grupos.nao],
                    backgroundColor: ['#4CAF50', '#9E9E9E'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Erro ao carregar indicadores:', error);
    });

// Variáveis para comparação de pacientes
let todosPacientes = [];
let pacientesSelecionados = [];
let pacienteSearchTimeout = null;
const comparacaoPacientesCharts = new Map();
let comparacaoPacienteChartCounter = 0;

// Carregar lista de pacientes
async function carregarPacientesParaComparacao() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();
        if (data.success) {
            todosPacientes = data.pacientes || [];
        }
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
    }
}

// Buscar pacientes ao digitar
function buscarPacientesParaComparacao(termo) {
    clearTimeout(pacienteSearchTimeout);
    
    const listaDropdown = document.getElementById('pacientes-lista');
    if (!listaDropdown) return;
    
    if (!termo || termo.trim() === '') {
        listaDropdown.innerHTML = '';
        listaDropdown.querySelector('.pacientes-lista-dropdown-content')?.classList.remove('show');
        return;
    }
    
    pacienteSearchTimeout = setTimeout(() => {
        const termoLower = termo.toLowerCase().trim();
        const pacientesFiltrados = todosPacientes.filter(paciente => {
            const nome = paciente.identificacao?.nome_gestante || '';
            return nome.toLowerCase().includes(termoLower);
        }).slice(0, 10); // Limitar a 10 resultados
        
        // Remover pacientes já selecionados
        const idsSelecionados = pacientesSelecionados.map(p => p.id);
        const pacientesDisponiveis = pacientesFiltrados.filter(p => !idsSelecionados.includes(p.id));
        
        let dropdownContent = listaDropdown.querySelector('.pacientes-lista-dropdown-content');
        if (!dropdownContent) {
            dropdownContent = document.createElement('div');
            dropdownContent.className = 'pacientes-lista-dropdown-content';
            listaDropdown.appendChild(dropdownContent);
        }
        
        if (pacientesDisponiveis.length === 0) {
            dropdownContent.innerHTML = '<div class="paciente-item-dropdown">Nenhum paciente encontrado</div>';
        } else {
            dropdownContent.innerHTML = pacientesDisponiveis.map(paciente => {
                const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
                const unidade = paciente.identificacao?.unidade_saude || 'Unidade não informada';
                return `
                    <div class="paciente-item-dropdown" onclick="adicionarPacienteSelecionado('${paciente.id}')">
                        <div class="paciente-item-nome">${nome}</div>
                        <div class="paciente-item-detalhes">${unidade}</div>
                    </div>
                `;
            }).join('');
        }
        
        dropdownContent.classList.add('show');
    }, 300);
}

// Adicionar paciente selecionado
window.adicionarPacienteSelecionado = function(pacienteId) {
    const paciente = todosPacientes.find(p => p.id === pacienteId);
    if (!paciente || pacientesSelecionados.find(p => p.id === pacienteId)) {
        return;
    }
    
    pacientesSelecionados.push(paciente);
    atualizarListaPacientesSelecionados();
    
    // Limpar busca
    const searchInput = document.getElementById('paciente-search');
    if (searchInput) {
        searchInput.value = '';
    }
    
    const listaDropdown = document.getElementById('pacientes-lista');
    const dropdownContent = listaDropdown?.querySelector('.pacientes-lista-dropdown-content');
    if (dropdownContent) {
        dropdownContent.classList.remove('show');
    }
    
    atualizarBotaoComparar();
}

// Remover paciente selecionado
window.removerPacienteSelecionado = function(pacienteId) {
    pacientesSelecionados = pacientesSelecionados.filter(p => p.id !== pacienteId);
    atualizarListaPacientesSelecionados();
    atualizarBotaoComparar();
}

// Atualizar lista de pacientes selecionados
function atualizarListaPacientesSelecionados() {
    const container = document.getElementById('pacientes-selecionados');
    if (!container) return;
    
    if (pacientesSelecionados.length === 0) {
        container.innerHTML = '<span style="color: #999; font-style: italic;">Nenhum paciente selecionado</span>';
        return;
    }
    
    container.innerHTML = pacientesSelecionados.map(paciente => {
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        return `
            <div class="paciente-selecionado-tag">
                <span>${nome}</span>
                <span class="remove-paciente" onclick="removerPacienteSelecionado('${paciente.id}')">✕</span>
            </div>
        `;
    }).join('');
}

// Atualizar botão de comparar
function atualizarBotaoComparar() {
    const btnComparar = document.getElementById('btn-comparar-pacientes');
    if (btnComparar) {
        // Habilitar botão se houver pelo menos 1 paciente
        btnComparar.disabled = pacientesSelecionados.length < 1;
        
        // Atualizar texto do botão baseado na quantidade
        if (pacientesSelecionados.length === 0) {
            btnComparar.textContent = 'Comparar Pacientes Selecionados';
        } else if (pacientesSelecionados.length === 1) {
            btnComparar.textContent = 'Visualizar Paciente Selecionado';
        } else {
            btnComparar.textContent = `Comparar ${pacientesSelecionados.length} Pacientes`;
        }
    }
}

// Comparar pacientes selecionados
function compararPacientesSelecionados() {
    if (pacientesSelecionados.length < 1) {
        alert('Selecione pelo menos 1 paciente para visualizar.');
        return;
    }
    
    // Limpar gráficos anteriores
    comparacaoPacientesCharts.forEach(chart => chart.destroy());
    comparacaoPacientesCharts.clear();
    
    const container = document.getElementById('comparacao-pacientes-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Criar gráficos de comparação para cada indicador
    const indicadores = [
        { nome: 'Início pré-natal antes de 12s', campo: 'inicio_pre_natal_antes_12s', labels: ['Sim', 'Não'] },
        { nome: 'Consultas de pré-natal', campo: 'consultas_pre_natal', labels: ['≥ 6 consultas', '< 6 consultas'], tipo: 'numero' },
        { nome: 'Vacinas completas', campo: 'vacinas_completas', labels: ['Completo', 'Incompleto', 'Não avaliado'] },
        { nome: 'Plano de parto', campo: 'plano_parto', labels: ['Sim', 'Não'] },
        { nome: 'Participação em grupos', campo: 'participou_grupos', labels: ['Participou', 'Não participou'] }
    ];
    
    indicadores.forEach(indicador => {
        const chartId = `paciente-chart-${comparacaoPacienteChartCounter++}`;
        const containerId = `paciente-container-${chartId}`;
        
        // Preparar dados para o gráfico
        const nomes = pacientesSelecionados.map(p => p.identificacao?.nome_gestante || 'Sem nome');
        const datasets = [];
        
        if (indicador.tipo === 'numero') {
            // Para consultas, mostrar valores numéricos
            const valores = pacientesSelecionados.map(p => {
                const avaliacao = p.avaliacao || {};
                return avaliacao[indicador.campo] || 0;
            });
            
            datasets.push({
                label: 'Número de consultas',
                data: valores,
                backgroundColor: 'rgba(33, 150, 243, 0.6)',
                borderColor: '#2196F3',
                borderWidth: 2
            });
        } else {
            // Para outros indicadores booleanos ou categóricos
            indicador.labels.forEach((label, index) => {
                const valores = pacientesSelecionados.map(p => {
                    const avaliacao = p.avaliacao || {};
                    const valor = avaliacao[indicador.campo];
                    
                    if (indicador.campo === 'vacinas_completas') {
                        if (index === 0) return valor && (valor.toLowerCase().includes('completa') || valor.toLowerCase() === 'completo') ? 1 : 0;
                        if (index === 1) return valor && (valor.toLowerCase().includes('incompleta') || valor.toLowerCase() === 'incompleto') ? 1 : 0;
                        if (index === 2) return (!valor || valor === '') ? 1 : 0;
                    } else if (indicador.campo === 'consultas_pre_natal') {
                        const numConsultas = valor || 0;
                        return index === 0 ? (numConsultas >= 6 ? 1 : 0) : (numConsultas < 6 ? 1 : 0);
                    } else {
                        // Para indicadores booleanos (inicio_pre_natal_antes_12s, plano_parto, participou_grupos)
                        // index 0 = Sim/True, index 1 = Não/False
                        if (index === 0) {
                            return valor === true ? 1 : 0;
                        } else {
                            return valor === false ? 1 : 0;
                        }
                    }
                });
                
                const cores = [
                    ['#4CAF50', 'rgba(76, 175, 80, 0.6)'],
                    ['#f44336', 'rgba(244, 67, 54, 0.6)'],
                    ['#FF9800', 'rgba(255, 152, 0, 0.6)'],
                    ['#9E9E9E', 'rgba(158, 158, 158, 0.6)']
                ];
                
                datasets.push({
                    label: label,
                    data: valores,
                    backgroundColor: cores[index]?.[1] || 'rgba(0, 0, 0, 0.6)',
                    borderColor: cores[index]?.[0] || '#000',
                    borderWidth: 2
                });
            });
        }
        
        // Criar card do gráfico
        const chartCard = document.createElement('div');
        chartCard.className = 'comparacao-chart-card';
        chartCard.id = `card-${chartId}`;
        chartCard.innerHTML = `
            <div class="comparacao-chart-header">
                <h3 class="comparacao-chart-title">${indicador.nome}</h3>
                <button class="btn-remover-chart" onclick="removerGraficoPaciente('${chartId}')">✕ Remover</button>
            </div>
            <div class="comparacao-chart-container">
                <canvas id="${containerId}"></canvas>
            </div>
        `;
        container.appendChild(chartCard);
        
        // Criar gráfico
        const chartConfig = {
            type: 'bar',
            data: {
                labels: nomes,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: indicador.tipo === 'numero' ? undefined : 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        };
        
        const ctx = document.getElementById(containerId);
        const chart = new Chart(ctx, chartConfig);
        comparacaoPacientesCharts.set(chartId, chart);
    });
}

// Função para remover gráfico de paciente
window.removerGraficoPaciente = function(chartId) {
    const chart = comparacaoPacientesCharts.get(chartId);
    if (chart) {
        chart.destroy();
        comparacaoPacientesCharts.delete(chartId);
    }
    
    const card = document.getElementById(`card-${chartId}`);
    if (card) {
        card.remove();
    }
}

// Limpar seleção de pacientes
function limparSelecaoPacientes() {
    pacientesSelecionados = [];
    atualizarListaPacientesSelecionados();
    atualizarBotaoComparar();
    
    // Limpar gráficos
    comparacaoPacientesCharts.forEach(chart => chart.destroy());
    comparacaoPacientesCharts.clear();
    
    const container = document.getElementById('comparacao-pacientes-container');
    if (container) {
        container.innerHTML = '';
    }
}

// Event listener para o botão de adicionar gráfico
document.addEventListener('DOMContentLoaded', function() {
    const btnAdicionar = document.getElementById('btn-adicionar-comparacao');
    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', adicionarGraficoComparacao);
    }
    
    // Inicializar funcionalidade de comparação de pacientes
    const pacienteSearch = document.getElementById('paciente-search');
    if (pacienteSearch) {
        pacienteSearch.addEventListener('input', (e) => {
            buscarPacientesParaComparacao(e.target.value);
        });
        
        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {
            if (!pacienteSearch.contains(e.target)) {
                const listaDropdown = document.getElementById('pacientes-lista');
                const dropdownContent = listaDropdown?.querySelector('.pacientes-lista-dropdown-content');
                if (dropdownContent) {
                    dropdownContent.classList.remove('show');
                }
            }
        });
    }
    
    const btnCompararPacientes = document.getElementById('btn-comparar-pacientes');
    if (btnCompararPacientes) {
        btnCompararPacientes.addEventListener('click', compararPacientesSelecionados);
    }
    
    const btnLimparPacientes = document.getElementById('btn-limpar-pacientes');
    if (btnLimparPacientes) {
        btnLimparPacientes.addEventListener('click', limparSelecaoPacientes);
    }
    
    // Carregar pacientes ao inicializar
    carregarPacientesParaComparacao().then(() => {
        atualizarListaPacientesSelecionados();
        atualizarBotaoComparar();
    });
});