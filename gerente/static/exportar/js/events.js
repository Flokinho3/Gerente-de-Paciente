// Configuração de eventos
import { state } from './state.js';
import { dom } from './dom.js';
import { exportarDados } from './export.js';
import { ocultarStatus, mostrarTooltipExportar, ocultarTooltipExportar, verificarRequisitosExportacao, atualizarEstadoBotaoExportar } from './ui.js';
import { atualizarUpasSelecionadas, atualizarCamposSelecionados, aplicarFiltroUnidade, filtrarUpasNaBusca, filtrarCamposNaBusca } from './filters.js';
import { atualizarResumoFiltros } from './ui.js';
import { adicionarColunaPersonalizada } from './customColumns.js';

export function configurarEventos() {
    // Eventos dos cards de formato
    dom.formatCards.forEach(card => {
        card.addEventListener('click', () => {
            dom.formatCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.formatoSelecionado = card.dataset.format;
            
            // Atualizar estado do botão
            atualizarEstadoBotaoExportar();
            
            ocultarStatus();
            ocultarTooltipExportar();
        });
    });

    // Evento do botão de exportar
    dom.exportBtn.addEventListener('click', () => {
        if (state.formatoSelecionado) {
            exportarDados(state.formatoSelecionado);
        }
    });
    
    // Tooltip dinâmico no botão de exportar
    if (dom.exportBtn) {
        dom.exportBtn.addEventListener('mouseenter', () => {
            if (dom.exportBtn.disabled) {
                mostrarTooltipExportar();
            }
        });
        
        dom.exportBtn.addEventListener('mouseleave', () => {
            ocultarTooltipExportar();
        });
        
        // Atualizar tooltip quando o mouse se move sobre o botão
        dom.exportBtn.addEventListener('mousemove', () => {
            if (dom.exportBtn.disabled) {
                mostrarTooltipExportar();
            }
        });
    }

    // Eventos da Gaveta de UPAs
    if (dom.filtroUpasBtn && dom.filterUpasDropdown) {
        // Toggle da gaveta ao clicar no botão
        dom.filtroUpasBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dom.filtroUpasBtn.classList.toggle('active');
            dom.filterUpasDropdown.classList.toggle('active');
            
            // Focar no campo de busca quando abrir
            if (dom.filterUpasDropdown.classList.contains('active') && dom.filterUpasSearch) {
                setTimeout(() => dom.filterUpasSearch.focus(), 100);
            }
        });

        // Fechar gavetas ao clicar fora (será configurado uma vez para ambas as gavetas)

        // Evento de busca nas UPAs
        dom.filterUpasSearch?.addEventListener('input', (e) => {
            filtrarUpasNaBusca(e.target.value);
        });

        // Evento de mudança nos checkboxes de UPAs
        dom.filterUpasOptions?.addEventListener('change', (e) => {
            if (e.target.classList.contains('filter-checkbox')) {
                // Se "Todas" foi clicada
                if (e.target.value === 'TODAS') {
                    if (e.target.checked) {
                        // Desmarcar todas as outras UPAs
                        const outrasCheckboxes = dom.filterUpasOptions.querySelectorAll('.filter-checkbox:not([value="TODAS"])');
                        outrasCheckboxes.forEach(cb => cb.checked = false);
                    }
                } else {
                    // Se uma UPA específica foi selecionada, desmarcar "Todas"
                    if (e.target.checked && dom.filterUpasTodas) {
                        dom.filterUpasTodas.checked = false;
                    }
                }
                
                atualizarUpasSelecionadas();
                aplicarFiltroUnidade();
                atualizarResumoFiltros();
            }
        });

        // Prevenir fechamento da gaveta ao clicar dentro dela
        dom.filterUpasDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Eventos da Gaveta de Campos
    if (dom.filtroCamposBtn && dom.filterCamposDropdown) {
        // Toggle da gaveta ao clicar no botão
        dom.filtroCamposBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dom.filtroCamposBtn.classList.toggle('active');
            dom.filterCamposDropdown.classList.toggle('active');
            
            // Focar no campo de busca quando abrir
            if (dom.filterCamposDropdown.classList.contains('active') && dom.filterCamposSearch) {
                setTimeout(() => dom.filterCamposSearch.focus(), 100);
            }
        });

        // Evento de busca nos campos
        dom.filterCamposSearch?.addEventListener('input', (e) => {
            filtrarCamposNaBusca(e.target.value);
        });

        // Evento de mudança nos checkboxes de campos
        dom.filterCamposOptions?.addEventListener('change', (e) => {
            if (e.target.classList.contains('filter-checkbox')) {
                // Se "Todos os campos" foi clicado
                if (e.target.value === 'TODOS') {
                    if (e.target.checked) {
                        // Desmarcar todos os outros campos
                        const outrosCheckboxes = dom.filterCamposOptions.querySelectorAll('.filter-checkbox:not([value="TODOS"])');
                        outrosCheckboxes.forEach(cb => cb.checked = false);
                    }
                } else {
                    // Se um campo específico foi selecionado, desmarcar "Todos os campos"
                    if (e.target.checked && dom.filterCamposTodos) {
                        dom.filterCamposTodos.checked = false;
                    }
                }
                
                atualizarCamposSelecionados();
                aplicarFiltroUnidade();
                atualizarResumoFiltros();
            }
        });

        // Prevenir fechamento da gaveta ao clicar dentro dela
        dom.filterCamposDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Configurar listener único para fechar ambas as gavetas ao clicar fora
    document.addEventListener('click', (e) => {
        const clicouForaUpas = dom.filtroUpasBtn && !dom.filtroUpasBtn.contains(e.target) && !dom.filterUpasDropdown?.contains(e.target);
        const clicouForaCampos = dom.filtroCamposBtn && !dom.filtroCamposBtn.contains(e.target) && !dom.filterCamposDropdown?.contains(e.target);
        
        if (clicouForaUpas) {
            dom.filtroUpasBtn.classList.remove('active');
            dom.filterUpasDropdown?.classList.remove('active');
        }
        if (clicouForaCampos) {
            dom.filtroCamposBtn.classList.remove('active');
            dom.filterCamposDropdown?.classList.remove('active');
        }
    });

    // Evento do toggle de personalização
    dom.togglePersonalizar?.addEventListener('change', () => {
        dom.customPanel?.classList.toggle('active', dom.togglePersonalizar.checked);
        atualizarResumoFiltros();
        atualizarEstadoBotaoExportar();
    });

    // Evento do botão de adicionar coluna personalizada
    dom.customAddBtn?.addEventListener('click', () => {
        adicionarColunaPersonalizada();
    });
}
