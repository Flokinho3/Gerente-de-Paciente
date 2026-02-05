/**
 * importacao-acoes.js - Sistema de ações individuais de importação
 * Inclui: Botões de ação (confirmar/editar/ignorar) para cada paciente
 */

// ==================== RENDERIZAR LISTA COM BOTÕES DE AÇÃO ====================

/**
 * Renderiza uma lista de pacientes com botões de ação (confirmar/editar/ignorar)
 * @param {string} containerId - ID do container onde renderizar
 * @param {Array} items - Lista de pacientes
 * @param {string} tipo - Tipo da lista ('novos' ou 'modificados')
 */
function renderizarListaComAcoes(containerId, items, tipo) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (items.length === 0) {
        container.innerHTML = `<p class="empty-list" style="padding: 20px; text-align: center; color: #666;">Nenhum paciente encontrado.</p>`;
        return;
    }

    // Inicializar ações padrão
    if (!acoesImportacao[tipo]) {
        acoesImportacao[tipo] = {};
    }

    container.innerHTML = items.map((item, index) => {
        const paciente = item.paciente || item;
        const id = paciente.id || `temp-${index}`;
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        const unidade = paciente.identificacao?.unidade_saude || 'Unidade não informada';
        const data = paciente.data_salvamento ? formatarData(paciente.data_salvamento) : '';

        // Inicializar ação padrão como ignorar
        if (!acoesImportacao[tipo][id]) {
            acoesImportacao[tipo][id] = { acao: 'ignorar', motivo: '' };
        }

        let detalhesHtml = '';
        if (tipo === 'modificados' && item.diferencas && item.diferencas.length > 0) {
            const campos = item.diferencas.map(d => d.campo).join(', ');
            detalhesHtml = `<small class="modified-fields" style="display: block; margin-top: 5px; color: #856404; font-style: italic;">Campos alterados: ${campos}</small>`;
        }

        return `
            <div class="comparison-item ${tipo}" data-id="${id}" data-tipo="${tipo}" id="item-${tipo}-${id}"
                 style="padding: 15px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa;">
                
                <div class="item-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div class="item-info" style="flex: 1;">
                        <strong style="font-size: 1.1em;">${nome}</strong>
                        <small style="display: block; color: #666; margin-top: 3px;">${unidade}${data ? ` - ${data}` : ''}</small>
                        ${detalhesHtml}
                    </div>
                    <div class="item-status" id="status-${tipo}-${id}" 
                         style="padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight: bold; background: #f5f5f5; color: #666;">
                        Ignorar
                    </div>
                </div>

                <div class="acoes-container" style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                    <button type="button" class="btn-acao btn-confirmar" 
                            onclick="definirAcao('${id}', 'confirmar', '${tipo}')"
                            id="btn-confirmar-${tipo}-${id}"
                            title="Confirmar importação deste paciente"
                            style="padding: 8px 16px; border: 2px solid transparent; border-radius: 6px; cursor: pointer; font-size: 0.9em; background: #e8f5e9; color: #2e7d32; transition: all 0.2s; display: flex; align-items: center; gap: 5px;">
                        <span style="font-size: 1.1em;">✓</span> Confirmar
                    </button>
                    <button type="button" class="btn-acao btn-editar" 
                            onclick="definirAcao('${id}', 'editar', '${tipo}')"
                            id="btn-editar-${tipo}-${id}"
                            title="Importar e abrir para edição"
                            style="padding: 8px 16px; border: 2px solid transparent; border-radius: 6px; cursor: pointer; font-size: 0.9em; background: #fff3e0; color: #f57c00; transition: all 0.2s; display: flex; align-items: center; gap: 5px;">
                        <span style="font-size: 1.1em;">✏️</span> Editar
                    </button>
                    <button type="button" class="btn-acao btn-ignorar" 
                            onclick="definirAcao('${id}', 'ignorar', '${tipo}')"
                            id="btn-ignorar-${tipo}-${id}"
                            title="Não importar este paciente"
                            style="padding: 8px 16px; border: 2px solid transparent; border-radius: 6px; cursor: pointer; font-size: 0.9em; background: #ffebee; color: #c62828; transition: all 0.2s; display: flex; align-items: center; gap: 5px;">
                        <span style="font-size: 1.1em;">✕</span> Ignorar
                    </button>
                    
                    <input type="text" 
                           class="input-motivo" 
                           placeholder="Motivo (opcional)..."
                           id="motivo-${tipo}-${id}"
                           onchange="atualizarMotivo('${id}', '${tipo}', this.value)"
                           style="flex: 1; min-width: 150px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em;">
                </div>

                ${tipo === 'modificados' ? `
                    <div class="detalhes-btn" style="margin-top: 10px;">
                        <button type="button" class="btn btn-sm btn-secondary" 
                                onclick='mostrarDetalhesModificacao(${JSON.stringify(item)})'
                                style="padding: 5px 12px; font-size: 0.85em; background: #e3f2fd; color: #1565c0; border: none; border-radius: 4px; cursor: pointer;">
                            Ver Detalhes das Alterações
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');

    // Aplicar estilos iniciais
    items.forEach((item, index) => {
        const paciente = item.paciente || item;
        const id = paciente.id || `temp-${index}`;
        atualizarVisualBotoes(id, tipo, 'ignorar');
    });
}

// ==================== DEFINIR AÇÃO ====================

/**
 * Define a ação para um paciente específico
 * @param {string} itemId - ID do paciente
 * @param {string} acao - Ação ('confirmar', 'editar' ou 'ignorar')
 * @param {string} tipo - Tipo ('novos' ou 'modificados')
 */
function definirAcao(itemId, acao, tipo) {
    if (!acoesImportacao[tipo]) {
        acoesImportacao[tipo] = {};
    }
    if (!acoesImportacao[tipo][itemId]) {
        acoesImportacao[tipo][itemId] = { acao: 'ignorar', motivo: '' };
    }

    acoesImportacao[tipo][itemId].acao = acao;
    atualizarVisualBotoes(itemId, tipo, acao);
    
    console.log(`Ação definida: ${tipo}[${itemId}] = ${acao}`);
}

/**
 * Atualiza o motivo para um paciente
 * @param {string} itemId - ID do paciente
 * @param {string} tipo - Tipo ('novos' ou 'modificados')
 * @param {string} valor - Texto do motivo
 */
function atualizarMotivo(itemId, tipo, valor) {
    if (!acoesImportacao[tipo]) {
        acoesImportacao[tipo] = {};
    }
    if (!acoesImportacao[tipo][itemId]) {
        acoesImportacao[tipo][itemId] = { acao: 'ignorar', motivo: '' };
    }
    acoesImportacao[tipo][itemId].motivo = valor.trim();
}

// ==================== VISUALIZAÇÃO DOS BOTÕES ====================

/**
 * Atualiza a aparência visual dos botões baseado na ação selecionada
 */
function atualizarVisualBotoes(itemId, tipo, acaoAtiva) {
    const statusEl = document.getElementById(`status-${tipo}-${itemId}`);
    const btnConfirmar = document.getElementById(`btn-confirmar-${tipo}-${itemId}`);
    const btnEditar = document.getElementById(`btn-editar-${tipo}-${itemId}`);
    const btnIgnorar = document.getElementById(`btn-ignorar-${tipo}-${itemId}`);
    const itemEl = document.getElementById(`item-${tipo}-${itemId}`);

    if (!btnConfirmar || !btnEditar || !btnIgnorar) return;

    // Resetar todos os botões
    const resetarBtn = (btn) => {
        btn.style.transform = 'scale(1)';
        btn.style.boxShadow = 'none';
        btn.style.opacity = '0.6';
        btn.style.fontWeight = 'normal';
        btn.style.borderColor = 'transparent';
    };

    resetarBtn(btnConfirmar);
    resetarBtn(btnEditar);
    resetarBtn(btnIgnorar);

    // Resetar item
    if (itemEl) {
        itemEl.style.borderColor = '#ddd';
        itemEl.style.borderWidth = '1px';
        itemEl.style.background = '#fafafa';
    }

    // Destacar botão ativo
    const destacarBtn = (btn, cor, corBorda) => {
        btn.style.transform = 'scale(1.05)';
        btn.style.boxShadow = `0 2px 8px ${cor}`;
        btn.style.opacity = '1';
        btn.style.fontWeight = 'bold';
        btn.style.borderColor = corBorda;
    };

    // Atualizar status
    if (statusEl) {
        switch (acaoAtiva) {
            case 'confirmar':
                statusEl.textContent = '✓ Confirmado';
                statusEl.style.background = '#c8e6c9';
                statusEl.style.color = '#2e7d32';
                destacarBtn(btnConfirmar, 'rgba(46, 125, 50, 0.3)', '#4caf50');
                if (itemEl) {
                    itemEl.style.borderColor = '#4caf50';
                    itemEl.style.borderWidth = '2px';
                    itemEl.style.background = '#f1f8e9';
                }
                break;
            case 'editar':
                statusEl.textContent = '✏️ Editar';
                statusEl.style.background = '#ffe0b2';
                statusEl.style.color = '#e65100';
                destacarBtn(btnEditar, 'rgba(245, 124, 0, 0.3)', '#ff9800');
                if (itemEl) {
                    itemEl.style.borderColor = '#ff9800';
                    itemEl.style.borderWidth = '2px';
                    itemEl.style.background = '#fff8e1';
                }
                break;
            case 'ignorar':
                statusEl.textContent = '✕ Ignorado';
                statusEl.style.background = '#ffcdd2';
                statusEl.style.color = '#c62828';
                destacarBtn(btnIgnorar, 'rgba(198, 40, 40, 0.3)', '#ef5350');
                break;
        }
    }
}

// ==================== COLETAR AÇÕES ====================

/**
 * Coleta todas as ações definidas para importação
 * @returns {Object} Objeto com arrays de novos e modificados com suas ações
 */
function coletarAcoesParaImportacao() {
    const resultado = { novos: [], modificados: [] };

    // Coletar pacientes novos
    if (dadosComparacao?.novos) {
        dadosComparacao.novos.forEach(item => {
            const paciente = item.paciente || item;
            const id = paciente.id;
            
            if (acoesImportacao.novos?.[id]) {
                const acaoData = acoesImportacao.novos[id];
                if (acaoData.acao !== 'ignorar') {
                    resultado.novos.push({
                        paciente: paciente,
                        acao: acaoData.acao,
                        motivo: acaoData.motivo || ''
                    });
                }
            }
        });
    }

    // Coletar pacientes modificados
    if (dadosComparacao?.modificados) {
        dadosComparacao.modificados.forEach(item => {
            const paciente = item.paciente || item;
            const id = paciente.id;
            
            if (acoesImportacao.modificados?.[id]) {
                const acaoData = acoesImportacao.modificados[id];
                if (acaoData.acao !== 'ignorar') {
                    resultado.modificados.push({
                        paciente: paciente,
                        acao: acaoData.acao,
                        motivo: acaoData.motivo || ''
                    });
                }
            }
        });
    }

    return resultado;
}

// ==================== CONFIRMAR IMPORTAÇÃO COM AÇÕES ====================

/**
 * Confirma a importação com ações individuais definidas
 */
async function confirmarImportacaoComAcoes() {
    const modal = document.getElementById('importComparisonModal');
    if (!modal || !dadosComparacao) return;

    const dadosParaImportar = coletarAcoesParaImportacao();
    const totalSelecionados = dadosParaImportar.novos.length + dadosParaImportar.modificados.length;

    if (totalSelecionados === 0) {
        mostrarStatus('Nenhum paciente selecionado. Marque pelo menos um paciente como "Confirmar" ou "Editar".', 'error');
        return;
    }

    // Contar por ação
    const contagemConfirmar = [...dadosParaImportar.novos, ...dadosParaImportar.modificados]
        .filter(p => p.acao === 'confirmar').length;
    const contagemEditar = [...dadosParaImportar.novos, ...dadosParaImportar.modificados]
        .filter(p => p.acao === 'editar').length;

    let mensagemConfirmacao = `Deseja importar ${totalSelecionados} paciente(s)?\n\n`;
    if (contagemConfirmar > 0) mensagemConfirmacao += `• ${contagemConfirmar} para CONFIRMAR\n`;
    if (contagemEditar > 0) mensagemConfirmacao += `• ${contagemEditar} para EDITAR\n`;
    mensagemConfirmacao += '\nDeseja continuar?';

    if (!confirm(mensagemConfirmacao)) return;

    try {
        mostrarLoading('Importando Pacientes', `Processando ${totalSelecionados} paciente(s)...`);
        atualizarProgressoLoading(30);

        const payload = {
            novos: dadosParaImportar.novos,
            modificados: dadosParaImportar.modificados,
            origem_backup: nomeArquivoBackup || 'backup_importado'
        };

        atualizarProgressoLoading(50);

        const response = await fetch('/api/backup/importar_com_acoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        atualizarProgressoLoading(80);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                modal.classList.remove('active');
                modal.style.display = 'none';
                
                const stats = data.stats || {};
                const msg = `Importação concluída! Confirmados: ${stats.confirmados || 0}, Editar: ${stats.editar || 0}, Ignorados: ${stats.ignorados || 0}`;
                mostrarStatus(msg, 'success');
                
                // Abrir pacientes marcados para edição
                if (data.pacientes_para_editar?.length > 0) {
                    setTimeout(() => {
                        const nomes = data.pacientes_para_editar
                            .map(p => p.identificacao?.nome_gestante || 'Paciente')
                            .join(', ');
                        
                        if (confirm(`Pacientes para edição:\n\n${nomes}\n\nDeseja editá-los agora?`)) {
                            editarPaciente(data.pacientes_para_editar[0].id);
                        }
                    }, 500);
                }
                
                carregarPacientes();
                limparAcoesImportacao();
            }, 500);
        } else {
            throw new Error(data.message || 'Erro ao importar');
        }
    } catch (error) {
        console.error('Erro:', error);
        esconderLoading();
        mostrarStatus('Erro: ' + error.message, 'error');
    }
}

// ==================== FUNÇÕES AUXILIARES ====================

function limparAcoesImportacao() {
    acoesImportacao = { novos: {}, modificados: {} };
    nomeArquivoBackup = '';
}

// ==================== MODAL COM AÇÕES ====================

function mostrarModalComparacaoComAcoes(data, nomeArquivo = '') {
    const modal = document.getElementById('importComparisonModal');
    if (!modal) {
        console.error('Modal não encontrado');
        return;
    }

    nomeArquivoBackup = nomeArquivo;
    limparAcoesImportacao();

    const comparison = data.comparison || data;

    // Atualizar resumo
    const resumoContainer = document.getElementById('comparisonSummary');
    if (resumoContainer) {
        const totalNovos = comparison.novos?.length || 0;
        const totalModificados = comparison.modificados?.length || 0;

        resumoContainer.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px;">
                <div style="text-align: center; padding: 15px; background: #d4edda; border-radius: 8px;">
                    <span style="font-size: 2em; font-weight: bold; color: #155724; display: block;">${totalNovos}</span>
                    <span style="color: #155724;">Novos</span>
                </div>
                <div style="text-align: center; padding: 15px; background: #fff3cd; border-radius: 8px;">
                    <span style="font-size: 2em; font-weight: bold; color: #856404; display: block;">${totalModificados}</span>
                    <span style="color: #856404;">Modificados</span>
                </div>
                <div style="text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px;">
                    <span style="font-size: 2em; font-weight: bold; color: #1565c0; display: block;">${totalNovos + totalModificados}</span>
                    <span style="color: #1565c0;">Total</span>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 6px; text-align: center;">
                <small style="color: #666;">
                    <strong>Instruções:</strong> Escolha uma ação: 
                    <span style="color: #2e7d32;">✓ Confirmar</span>, 
                    <span style="color: #f57c00;">✏️ Editar</span>, ou 
                    <span style="color: #c62828;">✕ Ignorar</span> (padrão)
                </small>
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
        if (titulo) titulo.innerHTML = `🆕 Novos Pacientes (${novos.length})`;
    }
    if (modificadosSection) {
        const modificados = comparison.modificados || [];
        modificadosSection.style.display = modificados.length > 0 ? 'block' : 'none';
        const titulo = modificadosSection.querySelector('h3');
        if (titulo) titulo.innerHTML = `📝 Pacientes Modificados (${modificados.length})`;
    }
    if (removidosSection) removidosSection.style.display = 'none';

    // Renderizar listas com ações
    renderizarListaComAcoes('novosList', comparison.novos || [], 'novos');
    renderizarListaComAcoes('modificadosList', comparison.modificados || [], 'modificados');

    // Atualizar botão de confirmação
    const confirmBtn = document.getElementById('confirmImportComparison');
    if (confirmBtn) {
        confirmBtn.textContent = '✓ Confirmar Importação com Ações';
        confirmBtn.onclick = confirmarImportacaoComAcoes;
    }

    modal.classList.add('active');
    modal.style.display = 'flex';
}

// ==================== CARREGAR BACKUP COM AÇÕES ====================

async function carregarBackupBDComAcoes(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        mostrarStatus('Por favor, selecione um arquivo JSON válido', 'error');
        return;
    }

    try {
        mostrarLoading('Lendo Arquivo', 'Validando estrutura do backup...');
        atualizarProgressoLoading(30);

        const fileContent = await file.text();
        atualizarProgressoLoading(60);

        const backup = JSON.parse(fileContent);

        // Validar estrutura
        let backupData = backup;
        if (backup.pacientes && Array.isArray(backup.pacientes)) {
            backupData = backup.pacientes;
        } else if (backup.backup && Array.isArray(backup.backup)) {
            backupData = backup.backup;
        } else if (Array.isArray(backup)) {
            backupData = backup;
        } else {
            esconderLoading();
            mostrarStatus('Arquivo de backup inválido', 'error');
            event.target.value = '';
            return;
        }

        atualizarProgressoLoading(80);
        
        const response = await fetch('/api/backup/comparar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup: backupData })
        });

        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                dadosComparacao = data.comparison;
                mostrarModalComparacaoComAcoes(dadosComparacao, file.name);
            }, 300);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao comparar dados', 'error');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        esconderLoading();
        mostrarStatus(error instanceof SyntaxError ? 'Erro: Arquivo JSON inválido' : 'Erro ao carregar backup', 'error');
    } finally {
        event.target.value = '';
    }
}
