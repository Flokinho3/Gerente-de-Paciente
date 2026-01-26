// Arquivo principal - orquestração da aplicação
import { carregarTotalPacientes, carregarUnidades, carregarCamposDisponiveis } from './api.js';
import { atualizarUpasSelecionadas, atualizarCamposSelecionados, separarUnidadesPorTipo, popularCamposDisponiveis, aplicarFiltroUnidade } from './filters.js';
import { configurarEventos } from './events.js';
import { popularOpcoesPersonalizadas } from './customColumns.js';
import { atualizarResumoFiltros, atualizarEstadoBotaoExportar } from './ui.js';

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    carregarTotalPacientes();
    await carregarUnidades();
    await carregarCamposDisponiveis();
    // Aguardar unidades e campos serem carregados antes de inicializar filtros
    separarUnidadesPorTipo();
    popularCamposDisponiveis();
    atualizarUpasSelecionadas();
    atualizarCamposSelecionados();
    configurarEventos();
    popularOpcoesPersonalizadas();
    atualizarResumoFiltros();
    // Aplicar filtros iniciais para atualizar o preview
    await aplicarFiltroUnidade();
    // Atualizar estado inicial do botão de exportar
    atualizarEstadoBotaoExportar();
});
