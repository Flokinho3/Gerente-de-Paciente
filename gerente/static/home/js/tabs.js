// Módulo de sistema de abas por unidade

let unidadesSaude = [];
let abasCharts = new Map();
let abaAtiva = 'geral';

// Funções para gerenciar abas
function criarAbaUnidade(unidade) {
    const tabsHeader = document.querySelector('.tabs-header');
    const tabsContent = document.querySelector('.tabs-content');
    
    const unidadeId = window.sanitizarId(unidade);
    const tabId = `tab-${unidadeId}`;
    const panelId = `panel-${unidadeId}`;
    
    // Se há muitas unidades (mais de 8), usar dropdown em vez de botões
    const maxTabsVisiveis = 8;
    
    // Criar painel sempre (necessário para os dados)
    if (!document.getElementById(panelId)) {
        const tabPanel = document.createElement('div');
        tabPanel.className = 'tab-panel';
        tabPanel.id = panelId;
        tabPanel.innerHTML = `
            <div class="indicadores-grid">
                <div class="indicador-card">
                    <div class="indicador-header">
                        <h2><span class="status-indicator" id="status1-${panelId}">🟢</span> Início do pré-natal antes de 12 semanas</h2>
                        <span class="badge">Indicador clássico do SUS</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart1-${panelId}"></canvas>
                    </div>
                </div>
                <div class="indicador-card">
                    <div class="indicador-header">
                        <h2><span class="status-indicator" id="status2-${panelId}">🟢</span> Média de consultas de pré-natal</h2>
                        <span class="badge">Qualidade do acompanhamento</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart2-${panelId}"></canvas>
                    </div>
                </div>
                <div class="indicador-card">
                    <div class="indicador-header">
                        <h2><span class="status-indicator" id="status3-${panelId}">🟢</span> Vacinas completas</h2>
                        <span class="badge">Segurança materno-infantil</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart3-${panelId}"></canvas>
                    </div>
                </div>
                <div class="indicador-card">
                    <div class="indicador-header">
                        <h2><span class="status-indicator" id="status4-${panelId}">🟢</span> Plano de parto</h2>
                        <span class="badge">Humanização do cuidado</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart4-${panelId}"></canvas>
                    </div>
                </div>
                <div class="indicador-card">
                    <div class="indicador-header">
                        <h2><span class="status-indicator" id="status5-${panelId}">🟢</span> Participação em grupos</h2>
                        <span class="badge">Educação em saúde</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart5-${panelId}"></canvas>
                    </div>
                </div>
            </div>
        `;
        tabsContent.appendChild(tabPanel);
    }
}

function trocarAba(unidade) {
    // Atualizar botões
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const tabId = unidade === 'geral' ? 'tab-geral' : `tab-${window.sanitizarId(unidade)}`;
    const tabButton = document.getElementById(tabId);
    if (tabButton) {
        tabButton.classList.add('active');
    }
    
    // Atualizar seletor dropdown
    const selector = document.getElementById('unidades-selector');
    if (selector) {
        selector.value = unidade === 'geral' ? '' : unidade;
    }
    
    // Atualizar painéis
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    const panelId = unidade === 'geral' ? 'panel-geral' : `panel-${window.sanitizarId(unidade)}`;
    const tabPanel = document.getElementById(panelId);
    if (tabPanel) {
        tabPanel.classList.add('active');
    }
    
    abaAtiva = unidade;
    
    if (unidade !== 'geral' && !abasCharts.has(unidade)) {
        carregarDadosAba(unidade);
    }
}

function carregarDadosAba(unidade) {
    const panelId = `panel-${window.sanitizarId(unidade)}`;
    const url = `/api/indicadores?unidade_saude=${encodeURIComponent(unidade)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            criarGraficosAba(panelId, data);
            abasCharts.set(unidade, true);
        })
        .catch(error => {
            console.error('Erro ao carregar dados da aba:', error);
        });
}

function criarGraficosAba(panelId, data) {
    const perc1 = window.calculatePositivePercentage(
        data.inicio_pre_natal_antes_12s.sim,
        data.inicio_pre_natal_antes_12s.nao
    );
    document.getElementById(`status1-${panelId}`).textContent = window.getStatusIndicator(perc1);

    const perc2 = window.calculatePositivePercentage(
        data.consultas_pre_natal.mais_6,
        data.consultas_pre_natal.ate_6
    );
    document.getElementById(`status2-${panelId}`).textContent = window.getStatusIndicator(perc2);

    const perc3 = window.calculatePositivePercentage3(
        data.vacinas_completas.completa,
        data.vacinas_completas.incompleta,
        data.vacinas_completas.nao_avaliado
    );
    document.getElementById(`status3-${panelId}`).textContent = window.getStatusIndicator(perc3);

    const perc4 = window.calculatePositivePercentage(
        data.plano_parto.sim,
        data.plano_parto.nao
    );
    document.getElementById(`status4-${panelId}`).textContent = window.getStatusIndicator(perc4);

    const perc5 = window.calculatePositivePercentage(
        data.participou_grupos.sim,
        data.participou_grupos.nao
    );
    document.getElementById(`status5-${panelId}`).textContent = window.getStatusIndicator(perc5);

    window.criarGraficoPizza(`chart1-${panelId}`, ['Sim', 'Não'], [data.inicio_pre_natal_antes_12s.sim, data.inicio_pre_natal_antes_12s.nao], ['#4CAF50', '#f44336']);
    window.criarGraficoBarra(`chart2-${panelId}`, ['≥ 6 consultas', '< 6 consultas'], [data.consultas_pre_natal.mais_6, data.consultas_pre_natal.ate_6], ['#2196F3', '#FF9800']);
    window.criarGraficoPizza(`chart3-${panelId}`, ['Completo', 'Incompleto', 'Não avaliado'], [data.vacinas_completas.completa, data.vacinas_completas.incompleta, data.vacinas_completas.nao_avaliado], ['#4CAF50', '#FF9800', '#9E9E9E']);
    window.criarGraficoBarra(`chart4-${panelId}`, ['Sim', 'Não'], [data.plano_parto.sim, data.plano_parto.nao], ['#2196F3', '#f44336']);
    window.criarGraficoBarra(`chart5-${panelId}`, ['Participou', 'Não participou'], [data.participou_grupos.sim, data.participou_grupos.nao], ['#4CAF50', '#9E9E9E']);
}

// Carregar unidades de saúde e criar abas/seletor
function carregarUnidadesSaude() {
    return fetch('/api/unidades_saude')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.unidades) {
                unidadesSaude = data.unidades;
                
                // Criar painéis para todas as unidades
                unidadesSaude.forEach(unidade => {
                    criarAbaUnidade(unidade);
                });
                
                // Configurar interface baseado na quantidade
                const maxTabsVisiveis = 8;
                if (unidadesSaude.length > maxTabsVisiveis) {
                    criarSeletorUnidades();
                } else {
                    criarBotoesUnidades();
                }
                
                // Atualizar lista de unidades no módulo de comparação se disponível
                if (window.atualizarTodasUnidades) {
                    window.atualizarTodasUnidades(unidadesSaude);
                }
            }
            return unidadesSaude;
        })
        .catch(error => {
            console.error('Erro ao carregar unidades de saúde:', error);
            return [];
        });
}

// Criar botões para unidades (quando há poucas)
function criarBotoesUnidades() {
    const tabsHeader = document.querySelector('.tabs-header');
    if (!tabsHeader) return;
    
    // Remover seletor se existir
    const seletorExistente = tabsHeader.querySelector('.unidades-selector');
    if (seletorExistente) {
        seletorExistente.remove();
    }
    
    // Criar botões para cada unidade
    unidadesSaude.forEach(unidade => {
        const unidadeId = window.sanitizarId(unidade);
        const tabId = `tab-${unidadeId}`;
        
        // Só criar se não existir
        if (!document.getElementById(tabId)) {
            const tabButton = document.createElement('button');
            tabButton.className = 'tab-button';
            tabButton.setAttribute('data-tab', unidade);
            tabButton.id = tabId;
            tabButton.textContent = `🏥 ${unidade}`;
            tabButton.addEventListener('click', () => trocarAba(unidade));
            tabsHeader.appendChild(tabButton);
        }
    });
}

// Criar seletor dropdown para unidades (quando há muitas)
function criarSeletorUnidades() {
    const tabsHeader = document.querySelector('.tabs-header');
    if (!tabsHeader) return;
    
    // Remover botões de unidades se existirem (manter apenas o "Geral")
    const tabGeral = document.getElementById('tab-geral');
    const todosBotoes = tabsHeader.querySelectorAll('.tab-button');
    todosBotoes.forEach(btn => {
        if (btn.id !== 'tab-geral') {
            btn.remove();
        }
    });
    
    // Remover seletor existente se houver
    const seletorExistente = tabsHeader.querySelector('.unidades-selector');
    if (seletorExistente) {
        seletorExistente.remove();
    }
    
    // Criar container do seletor
    const selectorContainer = document.createElement('div');
    selectorContainer.className = 'unidades-selector';
    
    const selectorLabel = document.createElement('label');
    selectorLabel.textContent = '🏥 Unidade:';
    selectorLabel.className = 'unidades-selector-label';
    
    const select = document.createElement('select');
    select.className = 'unidades-selector-select';
    select.id = 'unidades-selector';
    
    // Adicionar opção padrão
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Selecione uma unidade...';
    select.appendChild(defaultOption);
    
    // Adicionar unidades
    unidadesSaude.forEach(unidade => {
        const option = document.createElement('option');
        option.value = unidade;
        option.textContent = unidade;
        select.appendChild(option);
    });
    
    // Event listener para mudança de unidade
    select.addEventListener('change', (e) => {
        if (e.target.value) {
            trocarAba(e.target.value);
        }
    });
    
    selectorContainer.appendChild(selectorLabel);
    selectorContainer.appendChild(select);
    tabsHeader.appendChild(selectorContainer);
}

// Exportar funções
window.carregarUnidadesSaude = carregarUnidadesSaude;
window.trocarAba = trocarAba;
window.obterUnidadesSaude = () => unidadesSaude;
