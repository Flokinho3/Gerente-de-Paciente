// Módulo de indicadores e dados

// Variável global para armazenar os dados dos indicadores
let indicadoresData = null;

// Função para obter os dados de um indicador específico
function getIndicadorData(filtro, unidadeSaude = null) {
    // Indicadores hardcoded conhecidos
    const indicadoresHardcoded = ['inicio_pre_natal_antes_12s', 'consultas_pre_natal', 'vacinas_completas', 'plano_parto', 'participou_grupos'];
    
    // Se não especificar unidade, usar dados gerais (apenas para hardcoded)
    if (!unidadeSaude && indicadoresData && indicadoresHardcoded.includes(filtro)) {
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
    
    // Para colunas dinâmicas ou quando precisa buscar filtrado, retornar null
    // (será feito assincronamente via buscarIndicadorPorUnidade)
    return null;
}

// Função para buscar dados de indicador filtrado por unidade
async function buscarIndicadorPorUnidade(filtro, unidadeSaude) {
    // Indicadores hardcoded conhecidos
    const indicadoresHardcoded = ['inicio_pre_natal_antes_12s', 'consultas_pre_natal', 'vacinas_completas', 'plano_parto', 'participou_grupos'];
    
    // Se for um indicador hardcoded, usar a API original
    if (indicadoresHardcoded.includes(filtro)) {
        const url = unidadeSaude 
            ? `/api/indicadores?unidade_saude=${encodeURIComponent(unidadeSaude)}`
            : '/api/indicadores';
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            const indicadores = {
                'inicio_pre_natal_antes_12s': {
                    data: data.inicio_pre_natal_antes_12s,
                    labels: ['Sim', 'Não'],
                    backgroundColor: ['#4CAF50', '#f44336'],
                    title: 'Início do pré-natal antes de 12 semanas'
                },
                'consultas_pre_natal': {
                    data: data.consultas_pre_natal,
                    labels: ['≥ 6 consultas', '< 6 consultas'],
                    backgroundColor: ['#2196F3', '#FF9800'],
                    title: 'Consultas de pré-natal'
                },
                'vacinas_completas': {
                    data: data.vacinas_completas,
                    labels: ['Completo', 'Incompleto', 'Não avaliado'],
                    backgroundColor: ['#4CAF50', '#FF9800', '#9E9E9E'],
                    title: 'Vacinas completas'
                },
                'plano_parto': {
                    data: data.plano_parto,
                    labels: ['Sim', 'Não'],
                    backgroundColor: ['#2196F3', '#f44336'],
                    title: 'Plano de parto'
                },
                'participou_grupos': {
                    data: data.participou_grupos,
                    labels: ['Participou', 'Não participou'],
                    backgroundColor: ['#4CAF50', '#9E9E9E'],
                    title: 'Participação em grupos'
                }
            };
            
            return indicadores[filtro] || null;
        } catch (error) {
            console.error('Erro ao buscar indicador por unidade:', error);
            return null;
        }
    } else {
        // Para colunas dinâmicas, usar a API genérica
        try {
            const url = unidadeSaude 
                ? `/api/indicadores_coluna/${filtro}?unidade_saude=${encodeURIComponent(unidadeSaude)}`
                : `/api/indicadores_coluna/${filtro}`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success && data.data) {
                // Obter título amigável do filtro
                const filtroSelect = document.getElementById('comparacao-filtro');
                let titulo = filtro.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                if (filtroSelect) {
                    const option = filtroSelect.querySelector(`option[value="${filtro}"]`);
                    if (option) {
                        titulo = option.text;
                    }
                }
                
                return {
                    data: data.data,
                    labels: ['Sim', 'Não'],
                    backgroundColor: ['#4CAF50', '#f44336'],
                    title: titulo
                };
            } else {
                return null;
            }
        } catch (error) {
            console.error('Erro ao buscar indicador genérico por unidade:', error);
            return null;
        }
    }
}

// Carregar dados dos indicadores
async function carregarIndicadores() {
    try {
        const response = await fetch('/api/indicadores');
        const data = await response.json();
        indicadoresData = data;
        return data;
    } catch (error) {
        console.error('Erro ao carregar indicadores:', error);
        return null;
    }
}

// Obter dados dos indicadores
function obterIndicadoresData() {
    return indicadoresData;
}

// Exportar funções
window.getIndicadorData = getIndicadorData;
window.buscarIndicadorPorUnidade = buscarIndicadorPorUnidade;
window.carregarIndicadores = carregarIndicadores;
window.obterIndicadoresData = obterIndicadoresData;
