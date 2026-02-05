// Módulo para popular dinamicamente o filtro comparacao-filtro com colunas do BD

// Função para carregar colunas do BD e popular o filtro
async function carregarColunasParaFiltro() {
    try {
        const response = await fetch('/api/campos_disponiveis');
        const data = await response.json();
        
        if (data.success && data.campos && data.campos.length > 0) {
            const filtroSelect = document.getElementById('comparacao-filtro');
            if (!filtroSelect) return;
            
            // Limpar opções existentes (exceto os indicadores hardcoded principais)
            // Manter os optgroups principais e substituir os outros
            const indicadoresPrincipaisOptgroup = filtroSelect.querySelector('optgroup[label="Indicadores Principais"]');
            const optgroupsParaRemover = filtroSelect.querySelectorAll('optgroup:not([label="Indicadores Principais"])');
            optgroupsParaRemover.forEach(optgroup => optgroup.remove());
            
            // Mapear campos do BD para grupos
            const grupos = {};
            
            // Mapeamento de campos para grupos
            const gruposMap = {
                'Avaliação Pré-Natal': ['inicio_pre_natal_semanas', 'inicio_pre_natal_observacao', 'avaliacao_odontologica', 'estratificacao', 'estratificacao_problema', 'cartao_pre_natal_completo', 'possui_bolsa_familia', 'tem_vacina_covid', 'plano_parto_entregue_por_unidade'],
                'Datas e Gestação': ['dum', 'dpp', 'data_salvamento'],
                'Kit': ['ganhou_kit', 'kit_tipo'],
                'Próxima Avaliação': ['proxima_avaliacao', 'proxima_avaliacao_hora'],
                'Histórico Reprodutivo': ['ja_ganhou_crianca', 'data_ganhou_crianca', 'quantidade_filhos', 'generos_filhos', 'metodo_preventivo', 'metodo_preventivo_outros']
            };
            
            // Campos que já estão nos indicadores principais (não adicionar novamente)
            const camposJaIncluidos = ['inicio_pre_natal_antes_12s', 'consultas_pre_natal', 'vacinas_completas', 'plano_parto', 'participou_grupos'];
            
            // Agrupar campos
            data.campos.forEach(campo => {
                if (camposJaIncluidos.includes(campo.campo)) {
                    return; // Pular campos já incluídos nos indicadores principais
                }
                
                // Encontrar grupo do campo
                let grupoEncontrado = null;
                for (const [grupoNome, campos] of Object.entries(gruposMap)) {
                    if (campos.includes(campo.campo)) {
                        grupoEncontrado = grupoNome;
                        break;
                    }
                }
                
                if (!grupoEncontrado) {
                    grupoEncontrado = 'Outros';
                }
                
                if (!grupos[grupoEncontrado]) {
                    grupos[grupoEncontrado] = [];
                }
                
                grupos[grupoEncontrado].push(campo);
            });
            
            // Adicionar optgroups dinamicamente
            const ordemGrupos = ['Avaliação Pré-Natal', 'Datas e Gestação', 'Kit', 'Próxima Avaliação', 'Histórico Reprodutivo', 'Outros'];
            
            ordemGrupos.forEach(nomeGrupo => {
                if (grupos[nomeGrupo] && grupos[nomeGrupo].length > 0) {
                    const optgroup = document.createElement('optgroup');
                    optgroup.label = nomeGrupo;
                    
                    grupos[nomeGrupo].forEach(campo => {
                        const option = document.createElement('option');
                        option.value = campo.campo;
                        option.textContent = campo.label;
                        optgroup.appendChild(option);
                    });
                    
                    filtroSelect.appendChild(optgroup);
                }
            });
        }
    } catch (error) {
        console.error('Erro ao carregar colunas para filtro:', error);
    }
}

// Exportar função
window.carregarColunasParaFiltro = carregarColunasParaFiltro;
