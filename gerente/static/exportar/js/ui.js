// Funções de UI (status, tags, resumo)
import { state } from './state.js';
import { dom } from './dom.js';
import { obterLabelColuna } from './customColumns.js';

export function mostrarStatus(mensagem, tipo = 'success') {
    dom.statusMessage.textContent = mensagem;
    dom.statusMessage.className = `status-message status-${tipo}`;
    dom.statusMessage.style.display = 'block';
}

export function ocultarStatus() {
    dom.statusMessage.style.display = 'none';
}

export function atualizarTotalFiltrado() {
    const total = state.pacientesFiltrados.length;
    dom.totalPacientesSpan.textContent = `${total} ${total === 1 ? 'paciente encontrado' : 'pacientes encontrados'}`;
    
    // Atualizar preview de contagem na planilha
    if (dom.previewContagem) {
        dom.previewContagem.textContent = `${total} ${total === 1 ? 'pessoa' : 'pessoas'}`;
    }
}

export function renderizarTagsSelecionadas(container, selecionados, tipo, onRemove) {
    if (!container) return;
    
    container.innerHTML = '';
    
    if (selecionados.length === 0) {
        return;
    }
    
    selecionados.forEach(valor => {
        const tag = document.createElement('span');
        tag.className = 'selected-tag';
        tag.textContent = valor;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'selected-tag-remove';
        removeBtn.textContent = '×';
        removeBtn.type = 'button';
        removeBtn.addEventListener('click', () => {
            if (onRemove) {
                onRemove(valor);
            }
        });
        
        tag.appendChild(removeBtn);
        container.appendChild(tag);
    });
}

export function atualizarResumoFiltros() {
    const partes = [];
    
    if (state.upasSelecionadas.length > 0) {
        if (state.upasSelecionadas.length === 1) {
            partes.push(`1ª Filtro (Unidade): ${state.upasSelecionadas[0]}`);
        } else {
            partes.push(`1ª Filtro (Unidades): ${state.upasSelecionadas.length} selecionadas`);
        }
    }
    
    if (state.camposSelecionados.length > 0) {
        if (state.camposSelecionados.length === 1) {
            const campoInfo = state.camposDisponiveis.find(c => c.campo === state.camposSelecionados[0]);
            const nomeCampo = campoInfo ? campoInfo.label : state.camposSelecionados[0];
            partes.push(`2ª Filtro (Campo): ${nomeCampo}`);
        } else {
            partes.push(`2ª Filtro (Campos): ${state.camposSelecionados.length} selecionados`);
        }
    }

    let texto = partes.length ? `Filtros ativos: ${partes.join(' · ')}` : 'Nenhum filtro ativo.';

    if (dom.togglePersonalizar?.checked) {
        if (state.colunasPersonalizadas.length > 0) {
            texto += ` · Personalizado: ${state.colunasPersonalizadas.map(obterLabelColuna).join(', ')}`;
        } else {
            texto += ' · Personalizado ativo (nenhuma coluna selecionada).';
        }
    }

    if (dom.filtrosResumo) {
        dom.filtrosResumo.textContent = texto;
    }
}

// Verificar requisitos para exportar
export function verificarRequisitosExportacao() {
    const faltando = [];
    
    // Verificar se há formato selecionado
    if (!state.formatoSelecionado) {
        faltando.push('Selecione um formato de exportação (Excel, Word ou Texto)');
    }
    
    // Verificar se o modo personalizado está ativo e se há colunas selecionadas
    if (dom.togglePersonalizar?.checked && state.colunasPersonalizadas.length === 0) {
        faltando.push('Adicione pelo menos uma coluna na planilha personalizada');
    }
    
    // Verificar se há pacientes para exportar
    if (state.pacientesFiltrados.length === 0) {
        faltando.push('Não há pacientes para exportar com os filtros aplicados');
    }
    
    return faltando;
}

// Mostrar tooltip dinâmico no botão de exportar
export function mostrarTooltipExportar() {
    if (!dom.exportBtn) return;
    
    const faltando = verificarRequisitosExportacao();
    
    // Se não há nada faltando, não mostrar tooltip
    if (faltando.length === 0) {
        ocultarTooltipExportar();
        return;
    }
    
    // Criar ou atualizar tooltip
    let tooltip = document.getElementById('exportTooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'exportTooltip';
        tooltip.className = 'export-tooltip';
        document.body.appendChild(tooltip);
    }
    
    // Criar conteúdo do tooltip
    tooltip.innerHTML = `
        <div class="tooltip-header">
            <span class="tooltip-icon">⚠️</span>
            <strong>Requisitos não atendidos:</strong>
        </div>
        <ul class="tooltip-list">
            ${faltando.map(item => `<li>${item}</li>`).join('')}
        </ul>
    `;
    
    // Posicionar tooltip acima do botão
    tooltip.style.display = 'block';
    
    // Forçar cálculo de dimensões
    const tooltipRect = tooltip.getBoundingClientRect();
    const btnRect = dom.exportBtn.getBoundingClientRect();
    
    // Posicionar acima do botão, centralizado
    let top = btnRect.top - tooltipRect.height - 15;
    let left = btnRect.left + (btnRect.width / 2) - (tooltipRect.width / 2);
    
    // Ajustar se sair da tela horizontalmente
    if (left < 10) {
        left = 10;
    }
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    // Se não couber acima, colocar abaixo
    if (top < 10) {
        top = btnRect.bottom + 15;
        tooltip.classList.add('tooltip-below');
    } else {
        tooltip.classList.remove('tooltip-below');
    }
    
    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
}

// Ocultar tooltip
export function ocultarTooltipExportar() {
    const tooltip = document.getElementById('exportTooltip');
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

// Atualizar estado do botão de exportar baseado nos requisitos
export function atualizarEstadoBotaoExportar() {
    if (!dom.exportBtn) return;
    
    const faltando = verificarRequisitosExportacao();
    const estavaDesabilitado = dom.exportBtn.disabled;
    dom.exportBtn.disabled = faltando.length > 0;
    
    // Se o botão estava desabilitado e o mouse está sobre ele, atualizar tooltip
    if (estavaDesabilitado && dom.exportBtn.matches(':hover')) {
        if (dom.exportBtn.disabled) {
            mostrarTooltipExportar();
        } else {
            ocultarTooltipExportar();
        }
    }
}
