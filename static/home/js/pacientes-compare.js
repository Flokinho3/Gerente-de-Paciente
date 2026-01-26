// Módulo de comparação de pacientes

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
        }).slice(0, 10);
        
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
window.atualizarListaPacientesSelecionados = function() {
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
};

// Atualizar botão de comparar
window.atualizarBotaoComparar = function() {

    const btnComparar = document.getElementById('btn-comparar-pacientes');
    if (btnComparar) {
        btnComparar.disabled = pacientesSelecionados.length < 1;
        
        if (pacientesSelecionados.length === 0) {
            btnComparar.textContent = 'Comparar Pacientes Selecionados';
        } else if (pacientesSelecionados.length === 1) {
            btnComparar.textContent = 'Visualizar Paciente Selecionado';
        } else {
            btnComparar.textContent = `Comparar ${pacientesSelecionados.length} Pacientes`;
        }
    }
};

// Comparar pacientes selecionados
window.compararPacientesSelecionados = function() {

    if (pacientesSelecionados.length < 1) {
        alert('Selecione pelo menos 1 paciente para visualizar.');
        return;
    }
    
    comparacaoPacientesCharts.forEach(chart => chart.destroy());
    comparacaoPacientesCharts.clear();
    
    const container = document.getElementById('comparacao-pacientes-container');
    if (!container) return;
    
    container.innerHTML = '';
    
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
        
        const nomes = pacientesSelecionados.map(p => p.identificacao?.nome_gestante || 'Sem nome');
        const datasets = [];
        
        if (indicador.tipo === 'numero') {
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
};

// Limpar seleção de pacientes
window.limparSelecaoPacientes = function() {
    pacientesSelecionados = [];
    atualizarListaPacientesSelecionados();
    atualizarBotaoComparar();
    
    // Limpar todos os gráficos
    comparacaoPacientesCharts.forEach(chart => chart.destroy());
    comparacaoPacientesCharts.clear();
    
    // Limpar container de comparação
    const container = document.getElementById('comparacao-pacientes-container');
    if (container) {
        container.innerHTML = '';
    }
};

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
};

// Configurar eventos de comparação de pacientes
function configurarComparacaoPacientes() {
    const pacienteSearch = document.getElementById('paciente-search');
    if (pacienteSearch) {
        pacienteSearch.addEventListener('input', (e) => {
            buscarPacientesParaComparacao(e.target.value);
        });
        
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
}

// Exportar funções
window.carregarPacientesParaComparacao = carregarPacientesParaComparacao;
window.compararPacientesSelecionados = compararPacientesSelecionados;
window.configurarComparacaoPacientes = configurarComparacaoPacientes;
