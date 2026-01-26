// Lógica de colunas personalizadas
import { COLUNAS_DISPONIVEIS } from './constants.js';
import { state } from './state.js';
import { dom } from './dom.js';
import { atualizarResumoFiltros, atualizarEstadoBotaoExportar } from './ui.js';

export function popularOpcoesPersonalizadas() {
    if (!dom.customColumnSelect) return;
    dom.customColumnSelect.innerHTML = '';
    COLUNAS_DISPONIVEIS.forEach(coluna => {
        const option = document.createElement('option');
        option.value = coluna.value;
        option.textContent = coluna.label;
        dom.customColumnSelect.appendChild(option);
    });
}

export function adicionarColunaPersonalizada() {
    if (!dom.togglePersonalizar?.checked) return;
    const value = dom.customColumnSelect?.value;
    if (!value) return;
    if (state.colunasPersonalizadas.includes(value)) return;
    state.colunasPersonalizadas.push(value);
    renderizarColunasPersonalizadas();
    atualizarResumoFiltros();
    atualizarEstadoBotaoExportar();
}

export function renderizarColunasPersonalizadas() {
    if (!dom.customList) return;
    dom.customList.innerHTML = '';

    if (state.colunasPersonalizadas.length === 0) {
        const placeholder = document.createElement('span');
        placeholder.className = 'custom-placeholder';
        placeholder.textContent = 'Nenhuma coluna selecionada.';
        dom.customList.appendChild(placeholder);
        return;
    }

    state.colunasPersonalizadas.forEach(coluna => {
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
            state.colunasPersonalizadas = state.colunasPersonalizadas.filter(v => v !== coluna);
            renderizarColunasPersonalizadas();
            atualizarResumoFiltros();
            atualizarEstadoBotaoExportar();
        });

        chip.appendChild(button);
        dom.customList.appendChild(chip);
    });
}

export function obterLabelColuna(valor) {
    return COLUNAS_DISPONIVEIS.find(col => col.value === valor)?.label || valor;
}
