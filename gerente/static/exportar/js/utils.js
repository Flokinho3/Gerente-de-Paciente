// Funções utilitárias
import { state } from './state.js';
import { dom } from './dom.js';

export function construirFiltrosParams() {
    const params = new URLSearchParams();

    // Adicionar UPAs selecionadas
    if (state.upasSelecionadas.length > 0) {
        state.upasSelecionadas.forEach(upa => {
            params.append('upas', upa);
        });
    }

    // Adicionar campos selecionados
    if (state.camposSelecionados.length > 0) {
        state.camposSelecionados.forEach(campo => {
            params.append('campos', campo);
        });
    }

    if (dom.togglePersonalizar?.checked && state.colunasPersonalizadas.length > 0) {
        params.append('personalizado', 'true');
        state.colunasPersonalizadas.forEach(coluna => params.append('colunas', coluna));
    }

    return params;
}
