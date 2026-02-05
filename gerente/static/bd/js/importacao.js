/**
 * importacao.js - Importação com comparação e ações individuais
 * Inclui: Comparar backup, ações (confirmar/editar/ignorar), importação seletiva
 */

// Variáveis globais para importação
let dadosComparacao = null;
let pacientesSelecionados = { novos: [], modificados: [], removidos: [] };
let acoesImportacao = { novos: {}, modificados: {} };
let nomeArquivoBackup = '';

// ==================== COMPARAR BACKUP ====================

async function compararBackupAntesImportar(backupData) {
    try {
        mostrarLoading('Comparando Dados', 'Analisando diferenças entre o backup e os dados atuais...');
        atualizarProgressoLoading(30);

        const response = await fetch('/api/backup/comparar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup: backupData })
        });

        atualizarProgressoLoading(70);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                dadosComparacao = data.comparison;
                mostrarModalComparacao(dadosComparacao);
            }, 300);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao comparar dados', 'error');
            return false;
        }
    } catch (error) {
        console.error('Erro ao comparar backup:', error);
        esconderLoading();
        mostrarStatus('Erro ao comparar dados do backup', 'error');
        return false;
    }
}

// ==================== MODAL DE COMPARAÇÃO ====================

function mostrarModalComparacao(data) {
    const modal = document.getElementById('importComparisonModal');
    if (!modal) {
        console.error('Modal de comparação não encontrado');
        return;
    }

    const resumo = data.resumo || {};
    const comparison = data.comparison || data;

    // Atualizar resumo
    const resumoContainer = document.getElementById('comparisonSummary');
    if (resumoContainer) {
        resumoContainer.innerHTML = `
            <div class="comparison-summary-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px;">
                <div class="summary-item summary-new" style="text-align: center; padding: 15px; background: #d4edda; border-radius: 8px;">
                    <span class="summary-number" style="font-size: 2em; font-weight: bold; color: #155724; display: block;">${resumo.novos || comparison.novos?.length || 0}</span>
                    <span class="summary-label" style="color: #155724;">Novos</span>
                </div>
                <div class="summary-item summary-modified" style="text-align: center; padding: 15px; background: #fff3cd; border-radius: 8px;">
                    <span class="summary-number" style="font-size: 2em; font-weight: bold; color: #856404; display: block;">${resumo.modificados || comparison.modificados?.length || 0}</span>
                    <span class="summary-label" style="color: #856404;">Modificados</span>
                </div>
                <div class="summary-item summary-identical" style="text-align: center; padding: 15px; background: #d1ecf1; border-radius: 8px;">
                    <span class="summary-number" style="font-size: 2em; font-weight: bold; color: #0c5460; display: block;">${resumo.identicos || comparison.identicos?.length || 0}</span>
                    <span class="summary-label" style="color: #0c5460;">Identicos</span>
                </div>
                <div class="summary-item summary-removed" style="text-align: center; padding: 15px; background: #f8d7da; border-radius: 8px;">
                    <span class="summary-number" style="font-size: 2em; font-weight: bold; color: #721c24; display: block;">${resumo.removidos || comparison.removidos?.length || 0}</span>
                    <span class="summary-label" style="color: #721c24;">Removidos</span>
                </div>
            </div>
        `;
    }

    // Mostrar/ocultar seções
    const novosSection = document.getElementById('comparisonNovos');
    const modificadosSection = document.getElementById('comparisonModificados');
    const removidosSection = document.getElementById('comparisonRemovidos');
    
    if (novosSection) {
        const novos = comparison.novos || [];
        novosSection.style.display = novos.length > 0 ? 'block' : 'none';
        const titulo = novosSection.querySelector('h3');
        if (titulo) titulo.innerHTML = `➕ Novos Pacientes (${novos.length})`;
    }
    if (modificadosSection) {
        const modificados = comparison.modificados || [];
        modificadosSection.style.display = modificados.length > 0 ? 'block' : 'none';
        const titulo = modificadosSection.querySelector('h3');
        if (titulo) titulo.innerHTML = `✏️ Pacientes Modificados (${modificados.length})`;
    }
    if (removidosSection) {
        const removidos = comparison.removidos || [];
        removidosSection.style.display = removidos.length > 0 ? 'block' : 'none';
        const titulo = removidosSection.querySelector('h3');
        if (titulo) titulo.innerHTML = `🗑️ Pacientes Removidos (${removidos.length})`;
    }

    // Renderizar listas
    renderizarListaComparacao('novosList', comparison.novos || [], 'novos');
    renderizarListaComparacao('modificadosList', comparison.modificados || [], 'modificados');
    renderizarListaComparacao('removidosList', comparison.removidos || [], 'removidos');

    // Inicializar seleções
    pacientesSelecionados = {
        novos: (comparison.novos || []).map(p => p.id),
        modificados: (comparison.modificados || []).map(p => p.paciente?.id || p.id),
        removidos: []
    };

    modal.classList.add('active');
    modal.style.display = 'flex';
}

// ==================== RENDERIZAR LISTA COM CHECKBOXES ====================

function renderizarListaComparacao(containerId, items, tipo) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (items.length === 0) {
        container.innerHTML = `<p class="empty-list" style="padding: 20px; text-align: center; color: #666;">Nenhum paciente ${tipo === 'novos' ? 'novo' : tipo === 'modificados' ? 'modificado' : 'removido'}.</p>`;
        return;
    }

    container.innerHTML = items.map((item, index) => {
        const paciente = item.paciente || item;
        const id = paciente.id || `temp-${index}`;
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        const unidade = paciente.identificacao?.unidade_saude || 'Unidade não informada';
        const data = paciente.data_salvamento ? formatarData(paciente.data_salvamento) : '';

        let detalhesHtml = '';
        if (tipo === 'modificados' && item.diferencas && item.diferencas.length > 0) {
            const campos = item.diferencas.map(d => d.campo).join(', ');
            detalhesHtml = `<small class="modified-fields" style="display: block; margin-top: 5px; color: #856404; font-style: italic;">Campos alterados: ${campos}</small>`;
        }

        const checkboxChecked = tipo !== 'removidos' ? 'checked' : '';

        return `
            <div class="comparison-item ${tipo}" data-id="${id}" data-tipo="${tipo}" style="padding: 12px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 12px;">
                <input type="checkbox" class="comparison-checkbox" 
                       data-id="${id}" data-tipo="${tipo}" ${checkboxChecked} style="width: 18px; height: 18px; cursor: pointer;">
                <div class="comparison-item-info" style="flex: 1;">
                    <strong>${nome}</strong>
                    <small style="display: block; color: #666;">${unidade}${data ? ` - ${data}` : ''}</small>
                    ${detalhesHtml}
                </div>
                ${tipo === 'modificados' ? `
                    <button class="btn btn-sm btn-secondary" onclick='mostrarDetalhesModificacao(${JSON.stringify(item)})' style="padding: 5px 10px; font-size: 0.85em;">
                        Ver Detalhes
                    </button>
                ` : ''}
            </div>
        `;
    }).join('');

    // Adicionar event listeners
    container.querySelectorAll('.comparison-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const id = e.target.dataset.id;
            const tipo = e.target.dataset.tipo;
            
            if (e.target.checked) {
                if (!pacientesSelecionados[tipo].includes(id)) {
                    pacientesSelecionados[tipo].push(id);
                }
            } else {
                pacientesSelecionados[tipo] = pacientesSelecionados[tipo].filter(pid => pid !== id);
            }
        });
    });
}

// ==================== DETALHES DE MODIFICAÇÃO ====================

function mostrarDetalhesModificacao(paciente) {
    const modal = document.getElementById('modificationDetailsModal');
    if (!modal) return;

    const pacienteData = paciente.paciente || paciente;
    const diferencas = paciente.diferencas || [];

    const bodyContainer = document.getElementById('modificationDetailsBody');
    if (bodyContainer) {
        const nome = pacienteData.identificacao?.nome_gestante || 'Nome não informado';
        const unidade = pacienteData.identificacao?.unidade_saude || 'Unidade não informada';
        
        let diferencasHtml = '';
        if (diferencas.length === 0) {
            diferencasHtml = '<p style="padding: 20px; text-align: center; color: #666;">Nenhuma diferença detalhada disponível.</p>';
        } else {
            diferencasHtml = diferencas.map(diff => {
                let valorAntigo = diff.valor_antigo;
                let valorNovo = diff.valor_novo;

                if (typeof valorAntigo === 'boolean') valorAntigo = valorAntigo ? 'Sim' : 'Não';
                if (typeof valorNovo === 'boolean') valorNovo = valorNovo ? 'Sim' : 'Não';
                if (valorAntigo === null || valorAntigo === undefined) valorAntigo = '(vazio)';
                if (valorNovo === null || valorNovo === undefined) valorNovo = '(vazio)';

                return `
                    <div class="difference-row" style="margin-bottom: 15px; padding: 12px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #ffc107;">
                        <div class="difference-field" style="font-weight: bold; margin-bottom: 8px; color: #856404;">${diff.campo}</div>
                        <div class="difference-values" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div class="difference-old" style="padding: 8px; background: #f8d7da; border-radius: 4px;">
                                <span class="diff-label" style="font-size: 0.85em; color: #721c24; display: block; margin-bottom: 4px;">Valor Atual:</span>
                                <span class="diff-value" style="color: #721c24; word-break: break-word;">${valorAntigo}</span>
                            </div>
                            <div class="difference-new" style="padding: 8px; background: #d4edda; border-radius: 4px;">
                                <span class="diff-label" style="font-size: 0.85em; color: #155724; display: block; margin-bottom: 4px;">Novo Valor:</span>
                                <span class="diff-value" style="color: #155724; word-break: break-word;">${valorNovo}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        bodyContainer.innerHTML = `
            <div id="modificationPatientInfo" style="margin-bottom: 20px; padding: 15px; background: #e9ecef; border-radius: 8px;">
                <h4 style="margin-top: 0; margin-bottom: 10px;">${nome}</h4>
                <p style="margin: 5px 0;"><strong>Unidade:</strong> ${unidade}</p>
                <p style="margin: 5px 0;"><strong>ID:</strong> ${pacienteData.id}</p>
            </div>
            <div id="modificationDifferences">
                ${diferencasHtml}
            </div>
        `;
    }

    modal.classList.add('active');
    modal.style.display = 'flex';
}

// ==================== CONFIRMAR IMPORTAÇÃO ====================

async function confirmarImportacaoSelecionada() {
    const modal = document.getElementById('importComparisonModal');
    if (!modal || !dadosComparacao) return;

    const novosSelecionados = (dadosComparacao.novos || []).filter(p => 
        pacientesSelecionados.novos.includes(p.id)
    );
    const modificadosSelecionados = (dadosComparacao.modificados || []).filter(p => 
        pacientesSelecionados.modificados.includes(p.paciente?.id || p.id)
    ).map(p => p.paciente || p);

    const totalSelecionados = novosSelecionados.length + modificadosSelecionados.length;

    if (totalSelecionados === 0) {
        mostrarStatus('Nenhum paciente selecionado para importação', 'error');
        return;
    }

    if (!confirm('Deseja importar ' + totalSelecionados + ' paciente(s) selecionado(s)?')) {
        return;
    }

    try {
        mostrarLoading('Importando Pacientes', 'Importando ' + totalSelecionados + ' paciente(s)...');
        atualizarProgressoLoading(30);

        const pacientesParaImportar = [...novosSelecionados, ...modificadosSelecionados];

        const response = await fetch('/api/backup/importar_selecionados', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pacientes: pacientesParaImportar })
        });

        atualizarProgressoLoading(70);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                modal.classList.remove('active');
                modal.style.display = 'none';
                mostrarStatus('Importação concluída! ' + (data.importados || totalSelecionados) + ' paciente(s) importado(s).', 'success');
                carregarPacientes();
            }, 500);
        } else {
            throw new Error(data.message || 'Erro ao importar pacientes');
        }
    } catch (error) {
        console.error('Erro na importação:', error);
        esconderLoading();
        mostrarStatus('Erro ao importar: ' + error.message, 'error');
    }
}

// ==================== IMPORTAÇÃO FORÇADA ====================

async function importacaoForcadaCompleta() {
    const modal = document.getElementById('importComparisonModal');
    if (!modal || !dadosComparacao) return;

    const totalNovos = (dadosComparacao.novos || []).length;
    const totalModificados = (dadosComparacao.modificados || []).length;
    const total = totalNovos + totalModificados;

    if (!confirm('ATENÇÃO: Esta ação irá substituir TODOS os dados atuais pelos dados do backup.\n\nTotal de pacientes a serem importados: ' + total + '\n\nDeseja continuar?')) {
        return;
    }

    try {
        mostrarLoading('Importação Completa', 'Substituindo todos os dados...');
        atualizarProgressoLoading(30);

        const pacientesParaImportar = [
            ...(dadosComparacao.novos || []),
            ...(dadosComparacao.modificados || []).map(p => p.paciente || p)
        ];

        const response = await fetch('/api/backup/importar_selecionados', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                pacientes: pacientesParaImportar,
                substituir_todos: true
            })
        });

        atualizarProgressoLoading(70);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                modal.classList.remove('active');
                modal.style.display = 'none';
                mostrarStatus('Importação completa realizada com sucesso!', 'success');
                carregarPacientes();
            }, 500);
        } else {
            throw new Error(data.message || 'Erro na importação');
        }
    } catch (error) {
        console.error('Erro na importação forçada:', error);
        esconderLoading();
        mostrarStatus('Erro: ' + error.message, 'error');
    }
}

// ==================== FECHAR MODAIS ====================

function fecharModalComparacao() {
    const modal = document.getElementById('importComparisonModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
    dadosComparacao = null;
    pacientesSelecionados = { novos: [], modificados: [], removidos: [] };
}

function fecharModalDetalhesModificacao() {
    const modal = document.getElementById('modificationDetailsModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}
