/**
 * sync.js - Sincronização entre servidores
 * Inclui: Descobrir servidores, sincronizar, remover pacientes
 */

let servidoresEncontrados = [];
let pacientesRemovidos = [];

// Elementos do modal de sync
const syncProgress = document.getElementById('syncProgress');
const syncProgressFill = document.getElementById('syncProgressFill');
const syncProgressPercent = document.getElementById('syncProgressPercent');
const syncStatusMessage = document.getElementById('syncStatusMessage');
const syncResults = document.getElementById('syncResults');
const syncStats = document.getElementById('syncStats');
const removedPatientsSection = document.getElementById('removedPatientsSection');
const removedPatientsList = document.getElementById('removedPatientsList');
const serversList = document.getElementById('serversList');
const serversContainer = document.getElementById('serversContainer');

// ==================== GERENCIAMENTO DO MODAL ====================

function resetSyncModal() {
    if (serversList) serversList.style.display = 'none';
    if (syncProgress) syncProgress.style.display = 'none';
    if (syncResults) syncResults.style.display = 'none';
    if (removedPatientsSection) removedPatientsSection.style.display = 'none';
    if (serversContainer) serversContainer.innerHTML = '';
    if (syncStats) syncStats.innerHTML = '';
    if (removedPatientsList) removedPatientsList.innerHTML = '';
    servidoresEncontrados = [];
    pacientesRemovidos = [];
}

// ==================== DESCOBRIR SERVIDORES ====================

async function descobrirServidores() {
    try {
        const discoverBtn = document.getElementById('discoverBtn');
        if (discoverBtn) {
            discoverBtn.disabled = true;
            discoverBtn.innerHTML = '<span>⏳</span> Descobrindo...';
        }
        
        const response = await fetch('/api/sync/discover');
        const data = await response.json();
        
        if (discoverBtn) {
            discoverBtn.disabled = false;
            discoverBtn.innerHTML = '<span>🔍</span> Descobrir Servidores';
        }

        const hwEl = document.getElementById('syncHostWarning');
        if (hwEl) {
            if (data.host_warning) {
                hwEl.textContent = '⚠️ ' + data.host_warning;
                hwEl.style.display = 'block';
            } else {
                hwEl.style.display = 'none';
                hwEl.textContent = '';
            }
        }

        if (data.success) {
            servidoresEncontrados = data.servers || [];

            if (servidoresEncontrados.length === 0) {
                mostrarStatus('Nenhum servidor encontrado na rede', 'info');
                return;
            }
            
            // Mostrar lista de servidores
            if (serversContainer) {
                serversContainer.innerHTML = '';
                servidoresEncontrados.forEach((server, index) => {
                    const serverDiv = document.createElement('div');
                    serverDiv.className = 'server-item';
                    serverDiv.style.cssText = `
                        padding: 15px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        background: #f9f9f9;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    `;
                    
                    serverDiv.innerHTML = `
                        <div>
                            <strong>${server.hostname || server.ip}</strong><br>
                            <small style="color: #666;">IP: ${server.ip}:${server.port}</small>
                        </div>
                        <button class="btn btn-primary sync-server-btn" data-index="${index}">
                            🔄 Sincronizar
                        </button>
                    `;
                    
                    serversContainer.appendChild(serverDiv);
                });
                
                // Adicionar event listeners aos botões de sincronizar
                document.querySelectorAll('.sync-server-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const index = parseInt(e.target.dataset.index);
                        sincronizarComServidor(servidoresEncontrados[index]);
                    });
                });
            }
            
            if (serversList) serversList.style.display = 'block';
        } else {
            mostrarStatus(data.message || 'Erro ao descobrir servidores', 'error');
        }
    } catch (error) {
        console.error('Erro ao descobrir servidores:', error);
        mostrarStatus('Erro ao descobrir servidores na rede', 'error');
        
        const discoverBtn = document.getElementById('discoverBtn');
        if (discoverBtn) {
            discoverBtn.disabled = false;
            discoverBtn.innerHTML = '<span>🔍</span> Descobrir Servidores';
        }
    }
}

// ==================== SINCRONIZAR COM SERVIDOR ====================

async function sincronizarComServidor(server) {
    try {
        if (syncProgress) syncProgress.style.display = 'block';
        if (syncStatusMessage) syncStatusMessage.textContent = 'Conectando ao servidor...';
        atualizarProgressoSync(10);
        
        const remoteUrl = `http://${server.ip}:${server.port}`;
        if (syncStatusMessage) syncStatusMessage.textContent = 'Obtendo dados do servidor remoto...';
        atualizarProgressoSync(30);
        
        const remoteResponse = await fetch(`${remoteUrl}/api/sync/data`);
        if (!remoteResponse.ok) {
            throw new Error('Não foi possível conectar ao servidor remoto');
        }
        
        const remoteData = await remoteResponse.json();
        if (!remoteData.success) {
            throw new Error(remoteData.message || 'Erro ao obter dados do servidor remoto');
        }
        
        if (syncStatusMessage) syncStatusMessage.textContent = 'Sincronizando dados...';
        atualizarProgressoSync(50);
        
        const pacientesRemotos = remoteData.pacientes || [];
        const agendamentosRemotos = remoteData.agendamentos || [];
        
        const mergeResponse = await fetch('/api/sync/merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pacientes: pacientesRemotos,
                agendamentos: agendamentosRemotos
            })
        });
        
        atualizarProgressoSync(90);
        const mergeData = await mergeResponse.json();
        
        if (!mergeData.success) {
            throw new Error(mergeData.message || 'Erro ao sincronizar dados');
        }
        
        atualizarProgressoSync(100);
        if (syncStatusMessage) syncStatusMessage.textContent = 'Sincronização concluída!';
        
        const pacientesRemovidos = mergeData.pacientes_removidos || [];
        mostrarResultadosSync(mergeData.stats, pacientesRemovidos);
        
    } catch (error) {
        console.error('Erro ao sincronizar:', error);
        if (syncStatusMessage) syncStatusMessage.textContent = `Erro: ${error.message}`;
        mostrarStatus(`Erro ao sincronizar: ${error.message}`, 'error');
    }
}

function atualizarProgressoSync(percent) {
    if (!syncProgressFill || !syncProgressPercent) return;
    const clampedPercent = Math.max(0, Math.min(100, percent));
    syncProgressFill.style.width = clampedPercent + '%';
    syncProgressPercent.textContent = clampedPercent + '%';
}

function mostrarResultadosSync(stats, pacientesRemovidos) {
    if (syncResults) syncResults.style.display = 'block';
    
    if (syncStats) {
        syncStats.innerHTML = `
            <div style="padding: 15px; background: #e8f5e9; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="margin-top: 0;">✅ Sincronização Concluída</h4>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 5px 0;">📥 <strong>Pacientes adicionados:</strong> ${stats.pacientes_adicionados || 0}</li>
                    <li style="padding: 5px 0;">🔄 <strong>Pacientes atualizados:</strong> ${stats.pacientes_atualizados || 0}</li>
                    <li style="padding: 5px 0;">📥 <strong>Agendamentos adicionados:</strong> ${stats.agendamentos_adicionados || 0}</li>
                    <li style="padding: 5px 0;">🔄 <strong>Agendamentos atualizados:</strong> ${stats.agendamentos_atualizados || 0}</li>
                </ul>
            </div>
        `;
    }
    
    // Se houver pacientes removidos, mostrar seção para decidir
    if (pacientesRemovidos && pacientesRemovidos.length > 0 && removedPatientsList) {
        removedPatientsList.innerHTML = '';
        pacientesRemovidos.forEach(paciente => {
            const pacienteDiv = document.createElement('div');
            pacienteDiv.style.cssText = `
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                display: flex;
                align-items: center;
            `;
            
            const nome = paciente.nome_gestante || paciente.identificacao?.nome_gestante || 'Sem nome';
            const unidade = paciente.unidade_saude || paciente.identificacao?.unidade_saude || '';
            const data = paciente.data_salvamento || '';
            
            pacienteDiv.innerHTML = `
                <input type="checkbox" class="paciente-removido-checkbox" 
                       data-paciente-id="${paciente.id}" 
                       style="margin-right: 10px; cursor: pointer;">
                <div style="flex: 1;">
                    <strong>${nome}</strong>
                    ${unidade ? `<br><small style="color: #666;">Unidade: ${unidade}</small>` : ''}
                    ${data ? `<br><small style="color: #999;">Cadastrado em: ${data}</small>` : ''}
                    <br><small style="color: #999; font-family: monospace;">ID: ${paciente.id}</small>
                </div>
            `;
            
            removedPatientsList.appendChild(pacienteDiv);
        });
        
        // Adicionar checkbox "Selecionar todos"
        const selectAllDiv = document.createElement('div');
        selectAllDiv.style.cssText = `
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            background: #f1f8e9;
            display: flex;
            align-items: center;
        `;
        selectAllDiv.innerHTML = `
            <input type="checkbox" id="selectAllRemoved" 
                   style="margin-right: 10px; cursor: pointer;">
            <label for="selectAllRemoved" style="cursor: pointer; font-weight: bold;">
                Selecionar Todos (${pacientesRemovidos.length} pacientes)
            </label>
        `;
        removedPatientsList.insertBefore(selectAllDiv, removedPatientsList.firstChild);
        
        // Adicionar listener para "Selecionar Todos"
        const selectAllCheckbox = document.getElementById('selectAllRemoved');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                document.querySelectorAll('.paciente-removido-checkbox').forEach(cb => {
                    cb.checked = e.target.checked;
                });
            });
        }
        
        if (removedPatientsSection) removedPatientsSection.style.display = 'block';
    }
}

// ==================== REMOVER PACIENTES SELECIONADOS ====================

async function removerPacientesSelecionados() {
    const checkboxes = document.querySelectorAll('.paciente-removido-checkbox:checked');
    
    if (checkboxes.length === 0) {
        mostrarStatus('Nenhum paciente selecionado para remover', 'info');
        return;
    }
    
    const nomesPacientes = Array.from(checkboxes).map(cb => {
        const pacienteDiv = cb.closest('div[style*="padding: 10px"]');
        const nomeElement = pacienteDiv?.querySelector('strong');
        return nomeElement?.textContent || 'paciente';
    });
    
    const mensagem = `Tem certeza que deseja remover ${checkboxes.length} paciente(s) selecionado(s)?\n\n${nomesPacientes.join('\n')}`;
    
    if (!confirm(mensagem)) return;
    
    try {
        mostrarLoading('Removendo Pacientes', 'Excluindo pacientes selecionados...');
        atualizarProgressoLoading(30);
        
        const pacientesParaRemover = Array.from(checkboxes).map(cb => cb.dataset.pacienteId);
        
        const response = await fetch('/api/sync/remover_pacientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ paciente_ids: pacientesParaRemover })
        });
        
        atualizarProgressoLoading(70);
        
        const data = await response.json();
        
        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                mostrarStatus(data.message || `${data.removidos || checkboxes.length} paciente(s) removido(s) com sucesso!`, 'success');
                if (removedPatientsSection) removedPatientsSection.style.display = 'none';
                carregarPacientes();
            }, 500);
        } else {
            throw new Error(data.message || 'Erro ao remover pacientes');
        }
        
    } catch (error) {
        console.error('Erro ao remover pacientes:', error);
        esconderLoading();
        mostrarStatus(`Erro ao remover pacientes: ${error.message}`, 'error');
    }
}
