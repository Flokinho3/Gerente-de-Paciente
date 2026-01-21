// Sistema Home - Orquestrador Principal

// Inicialização
document.addEventListener('DOMContentLoaded', async function() {
    // Carregar dados dos indicadores
    const data = await window.carregarIndicadores();
    if (data) {
        // Calcular porcentagens e atualizar indicadores visuais
        
        // Indicador 1: Início pré-natal antes de 12 semanas
        const perc1 = window.calculatePositivePercentage(
            data.inicio_pre_natal_antes_12s.sim,
            data.inicio_pre_natal_antes_12s.nao
        );
        document.getElementById('status1-geral').textContent = window.getStatusIndicator(perc1);

        // Indicador 2: Consultas de pré-natal (>= 6 consultas)
        const perc2 = window.calculatePositivePercentage(
            data.consultas_pre_natal.mais_6,
            data.consultas_pre_natal.ate_6
        );
        document.getElementById('status2-geral').textContent = window.getStatusIndicator(perc2);

        // Indicador 3: Vacinas completas
        const perc3 = window.calculatePositivePercentage3(
            data.vacinas_completas.completa,
            data.vacinas_completas.incompleta,
            data.vacinas_completas.nao_avaliado
        );
        document.getElementById('status3-geral').textContent = window.getStatusIndicator(perc3);

        // Indicador 4: Plano de parto
        const perc4 = window.calculatePositivePercentage(
            data.plano_parto.sim,
            data.plano_parto.nao
        );
        document.getElementById('status4-geral').textContent = window.getStatusIndicator(perc4);

        // Indicador 5: Participação em grupos
        const perc5 = window.calculatePositivePercentage(
            data.participou_grupos.sim,
            data.participou_grupos.nao
        );
        document.getElementById('status5-geral').textContent = window.getStatusIndicator(perc5);

        // Criar gráficos
        window.criarGraficoPizza('chart1-geral', ['Sim', 'Não'], [data.inicio_pre_natal_antes_12s.sim, data.inicio_pre_natal_antes_12s.nao], ['#4CAF50', '#f44336']);
        window.criarGraficoBarra('chart2-geral', ['≥ 6 consultas', '< 6 consultas'], [data.consultas_pre_natal.mais_6, data.consultas_pre_natal.ate_6], ['#2196F3', '#FF9800']);
        window.criarGraficoPizza('chart3-geral', ['Completo', 'Incompleto', 'Não avaliado'], [data.vacinas_completas.completa, data.vacinas_completas.incompleta, data.vacinas_completas.nao_avaliado], ['#4CAF50', '#FF9800', '#9E9E9E']);
        window.criarGraficoBarra('chart4-geral', ['Sim', 'Não'], [data.plano_parto.sim, data.plano_parto.nao], ['#2196F3', '#f44336']);
        window.criarGraficoBarra('chart5-geral', ['Participou', 'Não participou'], [data.participou_grupos.sim, data.participou_grupos.nao], ['#4CAF50', '#9E9E9E']);
    }
    
    // Event listener para o botão de adicionar gráfico
    const btnAdicionar = document.getElementById('btn-adicionar-comparacao');
    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', window.adicionarGraficoComparacao);
    }
    
    // Configurar comparação de pacientes
    if (window.configurarComparacaoPacientes) {
        window.configurarComparacaoPacientes();
    }
    
    // Carregar pacientes para comparação
    if (window.carregarPacientesParaComparacao) {
        window.carregarPacientesParaComparacao().then(() => {
            if (window.atualizarListaPacientesSelecionados) {
                window.atualizarListaPacientesSelecionados();
            }
            if (window.atualizarBotaoComparar) {
                window.atualizarBotaoComparar();
            }
        });
    }
    
    // Carregar unidades de saúde e criar abas
    if (window.carregarUnidadesSaude) {
        window.carregarUnidadesSaude().then(() => {
            // Após carregar unidades, configurar seleção de unidades para comparação
            if (window.configurarSelecaoUnidades) {
                window.configurarSelecaoUnidades();
            }
        });
    }
    
    // Configurar evento de clique nas abas
    const tabGeral = document.getElementById('tab-geral');
    if (tabGeral && window.trocarAba) {
        tabGeral.addEventListener('click', () => window.trocarAba('geral'));
    }
    
    // Configurar dropdowns (gavetas) do topbar
    configurarDropdownsTopbar();
});

// Função para configurar os dropdowns do topbar
function configurarDropdownsTopbar() {
    const dropdowns = document.querySelectorAll('.topbar-dropdown');
    
    dropdowns.forEach(dropdown => {
        const btn = dropdown.querySelector('.topbar-dropdown-btn');
        const content = dropdown.querySelector('.topbar-dropdown-content');
        
        if (!btn || !content) return;
        
        // Toggle ao clicar no botão
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Fechar todos os outros dropdowns
            dropdowns.forEach(otherDropdown => {
                if (otherDropdown !== dropdown) {
                    otherDropdown.classList.remove('active');
                }
            });
            
            // Toggle o dropdown atual
            dropdown.classList.toggle('active');
        });
    });
    
    // Fechar dropdowns ao clicar fora
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.topbar-dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
    
    // Fechar dropdowns ao clicar em um item
    document.querySelectorAll('.topbar-dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        });
    });
    
    // Marcar item ativo baseado na URL atual
    marcarItemAtivoTopbar();
}

// Função para marcar o item ativo no topbar baseado na URL
function marcarItemAtivoTopbar() {
    const currentPath = window.location.pathname;
    const items = document.querySelectorAll('.topbar-dropdown-item');
    
    items.forEach(item => {
        item.classList.remove('active');
        const href = item.getAttribute('href');
        
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            item.classList.add('active');
        }
    });
}
