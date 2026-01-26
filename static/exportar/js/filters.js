// Lógica de filtros (Unidades e Campos do BD)
import { state } from './state.js';
import { dom } from './dom.js';
import { carregarTodosPacientes } from './api.js';
import { atualizarTotalFiltrado, atualizarEstadoBotaoExportar } from './ui.js';
import { atualizarResumoFiltros } from './ui.js';
import { renderizarTagsSelecionadas } from './ui.js';

let todasUpas = [];

export function separarUnidadesPorTipo() {
    if (!dom.filterUpasOptions) return;

    const unidadesGerais = [];

    // Garantir que todas as unidades do BD sejam processadas
    state.unidadesDisponiveis.forEach(unidade => {
        // Validar que a unidade não está vazia
        if (!unidade || typeof unidade !== 'string' || unidade.trim() === '') {
            return; // Pular unidades inválidas
        }

        // TODAS as unidades vão para o primeiro filtro
        // Isso inclui: UBS, UPA, Kitis, Unidades Básicas, Centros de Saúde, etc.
        unidadesGerais.push(unidade);
    });

    todasUpas = unidadesGerais;

    // Popular gaveta do primeiro filtro (TODAS as unidades não-Kitis)
    // A opção "Todas" já existe no HTML, apenas garantir que está selecionada
    if (dom.filterUpasTodas) {
        dom.filterUpasTodas.checked = true;
    }
    
    // Remover apenas as opções antigas (não a opção "Todas")
    if (dom.filterUpasOptions) {
        const opcoesAntigas = dom.filterUpasOptions.querySelectorAll('.filter-option');
        opcoesAntigas.forEach(opcao => {
            const checkbox = opcao.querySelector('.filter-checkbox');
            if (checkbox && checkbox.value !== 'TODAS') {
                opcao.remove();
            }
        });
    }

    // Popular opções com TODAS as unidades disponíveis (exceto Kitis)
    unidadesGerais.forEach(unidade => {
        const label = document.createElement('label');
        label.className = 'filter-option';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'filter-checkbox';
        checkbox.value = unidade;
        checkbox.dataset.unidade = unidade;
        
        const span = document.createElement('span');
        span.className = 'filter-option-text';
        span.textContent = unidade;
        
        label.appendChild(checkbox);
        label.appendChild(span);
        dom.filterUpasOptions.appendChild(label);
    });
}

// Popular gaveta de campos do BD
export function popularCamposDisponiveis() {
    if (!dom.filterCamposOptions) return;

    // A opção "Todos os campos" já existe no HTML, apenas garantir que está selecionada
    if (dom.filterCamposTodos) {
        dom.filterCamposTodos.checked = true;
    }
    
    // Remover apenas as opções antigas (não a opção "Todos os campos")
    const opcoesAntigas = dom.filterCamposOptions.querySelectorAll('.filter-option');
    opcoesAntigas.forEach(opcao => {
        const checkbox = opcao.querySelector('.filter-checkbox');
        if (checkbox && checkbox.value !== 'TODOS') {
            opcao.remove();
        }
    });

    // Popular opções com todos os campos disponíveis
    state.camposDisponiveis.forEach(campo => {
        const label = document.createElement('label');
        label.className = 'filter-option';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'filter-checkbox';
        checkbox.value = campo.campo;
        checkbox.dataset.campo = campo.campo;
        
        const span = document.createElement('span');
        span.className = 'filter-option-text';
        span.textContent = campo.label;
        span.title = campo.campo; // Tooltip com o nome técnico
        
        label.appendChild(checkbox);
        label.appendChild(span);
        dom.filterCamposOptions.appendChild(label);
    });
}

export function atualizarUpasSelecionadas() {
    if (!dom.filterUpasOptions) return;
    
    // Coletar todas as unidades selecionadas (exceto "Todas")
    const checkboxes = dom.filterUpasOptions.querySelectorAll('.filter-checkbox:not([value="TODAS"])');
    state.upasSelecionadas = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    // Se "Todas" estiver selecionada ou nenhuma unidade específica estiver selecionada
    if (dom.filterUpasTodas?.checked || state.upasSelecionadas.length === 0) {
        state.upasSelecionadas = [];
        if (dom.filterUpasTodas && !dom.filterUpasTodas.checked) {
            dom.filterUpasTodas.checked = true;
        }
        atualizarTextoBotaoUpas('Todas');
    } else {
        // Garantir que "Todas" não esteja marcada quando há seleções específicas
        if (dom.filterUpasTodas) {
            dom.filterUpasTodas.checked = false;
        }
        atualizarTextoBotaoUpas(state.upasSelecionadas.length === 1 
            ? state.upasSelecionadas[0] 
            : `${state.upasSelecionadas.length} unidades selecionadas`);
    }

    renderizarTagsSelecionadas(dom.selectedUpasTags, state.upasSelecionadas, 'UPA', (valor) => {
        const checkbox = dom.filterUpasOptions.querySelector(`.filter-checkbox[value="${valor}"]`);
        if (checkbox) {
            checkbox.checked = false;
        }
        // Se não houver mais nenhuma selecionada, selecionar "Todas"
        const totalSelecionadas = dom.filterUpasOptions.querySelectorAll('.filter-checkbox:checked:not([value="TODAS"])').length;
        if (totalSelecionadas === 0 && dom.filterUpasTodas) {
            dom.filterUpasTodas.checked = true;
        }
        atualizarUpasSelecionadas();
        aplicarFiltroUnidade();
        atualizarResumoFiltros();
        atualizarEstadoBotaoExportar();
    });
}

function atualizarTextoBotaoUpas(texto) {
    if (dom.filterUpasText) {
        dom.filterUpasText.textContent = texto;
    }
}

export function atualizarCamposSelecionados() {
    if (!dom.filterCamposOptions) return;
    
    // Coletar todos os campos selecionados (exceto "Todos os campos")
    const checkboxes = dom.filterCamposOptions.querySelectorAll('.filter-checkbox:not([value="TODOS"])');
    state.camposSelecionados = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    // Se "Todos os campos" estiver selecionado ou nenhum campo específico estiver selecionado
    if (dom.filterCamposTodos?.checked || state.camposSelecionados.length === 0) {
        state.camposSelecionados = [];
        if (dom.filterCamposTodos && !dom.filterCamposTodos.checked) {
            dom.filterCamposTodos.checked = true;
        }
        atualizarTextoBotaoCampos('Todos os campos');
    } else {
        // Garantir que "Todos os campos" não esteja marcado quando há seleções específicas
        if (dom.filterCamposTodos) {
            dom.filterCamposTodos.checked = false;
        }
        const labels = state.camposSelecionados.map(campo => {
            const campoInfo = state.camposDisponiveis.find(c => c.campo === campo);
            return campoInfo ? campoInfo.label : campo;
        });
        atualizarTextoBotaoCampos(state.camposSelecionados.length === 1 
            ? labels[0]
            : `${state.camposSelecionados.length} campos selecionados`);
    }

    renderizarTagsSelecionadas(dom.selectedCamposTags, state.camposSelecionados.map(campo => {
        const campoInfo = state.camposDisponiveis.find(c => c.campo === campo);
        return campoInfo ? campoInfo.label : campo;
    }), 'CAMPO', (valor) => {
        // Encontrar o campo pelo label
        const campoInfo = state.camposDisponiveis.find(c => c.label === valor);
        if (campoInfo) {
            const checkbox = dom.filterCamposOptions.querySelector(`.filter-checkbox[value="${campoInfo.campo}"]`);
            if (checkbox) {
                checkbox.checked = false;
            }
        }
        // Se não houver mais nenhum selecionado, selecionar "Todos os campos"
        const totalSelecionados = dom.filterCamposOptions.querySelectorAll('.filter-checkbox:checked:not([value="TODOS"])').length;
        if (totalSelecionados === 0 && dom.filterCamposTodos) {
            dom.filterCamposTodos.checked = true;
        }
        atualizarCamposSelecionados();
        aplicarFiltroUnidade();
        atualizarResumoFiltros();
        atualizarEstadoBotaoExportar();
    });
}

function atualizarTextoBotaoCampos(texto) {
    if (dom.filterCamposText) {
        dom.filterCamposText.textContent = texto;
    }
}

export async function aplicarFiltroUnidade() {
    // Se nenhum filtro está ativo, carregar todos os pacientes
    if (state.upasSelecionadas.length === 0 && state.camposSelecionados.length === 0) {
        const pacientes = await carregarTodosPacientes();
        state.pacientesFiltrados = pacientes;
        atualizarTotalFiltrado();
        return;
    }

    try {
        // Buscar todos os pacientes primeiro
        let pacientes = await carregarTodosPacientes();

        // Aplicar filtro de Unidades (se houver seleção)
        if (state.upasSelecionadas.length > 0) {
            pacientes = pacientes.filter(paciente => {
                const unidade = paciente.identificacao?.unidade_saude || '';
                return state.upasSelecionadas.includes(unidade);
            });
        }

        // Aplicar filtro de Campos (se houver seleção)
        // Filtrar pacientes que têm valores não-nulos nos campos selecionados
        if (state.camposSelecionados.length > 0) {
            pacientes = pacientes.filter(paciente => {
                return state.camposSelecionados.every(campo => {
                    // Buscar o valor do campo na estrutura do paciente
                    // A maioria dos campos está em avaliacao
                    let valor = null;
                    
                    // Verificar em avaliacao primeiro (maioria dos campos)
                    if (paciente.avaliacao && paciente.avaliacao[campo] !== undefined) {
                        valor = paciente.avaliacao[campo];
                    }
                    // Verificar em identificacao (caso especial)
                    else if (paciente.identificacao && paciente.identificacao[campo] !== undefined) {
                        valor = paciente.identificacao[campo];
                    }
                    // Verificar na raiz (casos especiais como id, data_salvamento)
                    else if (paciente[campo] !== undefined) {
                        valor = paciente[campo];
                    }
                    
                    // Retornar true se o campo tem um valor não-nulo e não-vazio
                    // Para booleanos, considerar false como válido também
                    if (valor === null || valor === undefined || valor === '') {
                        return false;
                    }
                    // Para números, considerar 0 como válido
                    if (typeof valor === 'number' && valor === 0) {
                        return true;
                    }
                    // Para booleanos, considerar false como válido
                    if (typeof valor === 'boolean') {
                        return true;
                    }
                    return true;
                });
            });
        }

        state.pacientesFiltrados = pacientes;
        atualizarTotalFiltrado();
        atualizarEstadoBotaoExportar();
    } catch (error) {
        console.error('Erro ao filtrar pacientes:', error);
        state.pacientesFiltrados = [];
        atualizarTotalFiltrado();
        atualizarEstadoBotaoExportar();
    }
}

// Função para filtrar UPAs na busca
export function filtrarUpasNaBusca(termo) {
    if (!dom.filterUpasOptions) return;
    
    const termoLower = termo.toLowerCase().trim();
    const opcoes = dom.filterUpasOptions.querySelectorAll('.filter-option');
    
    opcoes.forEach(opcao => {
        const texto = opcao.querySelector('.filter-option-text')?.textContent || '';
        const checkbox = opcao.querySelector('.filter-checkbox');
        
        // Sempre mostrar "Todas"
        if (checkbox?.value === 'TODAS') {
            opcao.classList.remove('filter-hidden');
            return;
        }
        
        // Filtrar outras opções
        if (texto.toLowerCase().includes(termoLower)) {
            opcao.classList.remove('filter-hidden');
        } else {
            opcao.classList.add('filter-hidden');
        }
    });
}

// Função para filtrar campos na busca
export function filtrarCamposNaBusca(termo) {
    if (!dom.filterCamposOptions) return;
    
    const termoLower = termo.toLowerCase().trim();
    const opcoes = dom.filterCamposOptions.querySelectorAll('.filter-option');
    
    opcoes.forEach(opcao => {
        const texto = opcao.querySelector('.filter-option-text')?.textContent || '';
        const checkbox = opcao.querySelector('.filter-checkbox');
        
        // Sempre mostrar "Todos os campos"
        if (checkbox?.value === 'TODOS') {
            opcao.classList.remove('filter-hidden');
            return;
        }
        
        // Filtrar outras opções
        if (texto.toLowerCase().includes(termoLower)) {
            opcao.classList.remove('filter-hidden');
        } else {
            opcao.classList.add('filter-hidden');
        }
    });
}
