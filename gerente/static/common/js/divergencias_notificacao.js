/**
 * Sistema de Notificações Automáticas de Divergências VPS
 * Verifica periodicamente e exibe modal quando divergências são detectadas
 */

let divergenciasAtivas = null;
let modalAberto = false;
let intervaloVerificacao = null;

// Iniciar verificação automática
function iniciarVerificacaoDivergencias() {
    // Verificar imediatamente
    verificarDivergencias();

    // Verificar a cada 30 segundos
    intervaloVerificacao = setInterval(verificarDivergencias, 30000);
}

// Parar verificação
function pararVerificacaoDivergencias() {
    if (intervaloVerificacao) {
        clearInterval(intervaloVerificacao);
        intervaloVerificacao = null;
    }
}

// Verificar se há divergências pendentes (apenas novas, não notificadas)
async function verificarDivergencias() {
    try {
        const response = await fetch('/api/vps/divergencias/pendentes');
        const data = await response.json();

        if (data.success && data.divergencias) {
            const total = data.divergencias.total || 0;

            // Atualizar badge de notificação (mostra total de pendentes)
            atualizarBadgeNotificacao(total);
            
            // Só mostrar modal se há divergências NOVAS (ainda não notificadas)
            // O backend verifica se há divergências que ainda não foram notificadas
            if (total > 0 && !modalAberto) {
                // Verificar se alguma dessas divergências é nova
                const temNovas = await verificarSeHaDivergenciasNovas();
                if (temNovas) {
                    divergenciasAtivas = data.divergencias;
                    mostrarModalDivergencias();
                    // Marcar como notificadas após mostrar
                    await marcarDivergenciasComoNotificadas();
                }
            }
        }
    } catch (error) {
        console.error('Erro ao verificar divergências:', error);
    }
}

// Verificar se há divergências novas no backend
async function verificarSeHaDivergenciasNovas() {
    try {
        const response = await fetch('/api/vps/divergencias/novas');
        const data = await response.json();
        return data.success && data.tem_novas;
    } catch (error) {
        console.error('Erro ao verificar novas divergências:', error);
        return false;
    }
}

// Marcar divergências como notificadas
async function marcarDivergenciasComoNotificadas() {
    try {
        await fetch('/api/vps/divergencias/marcar-notificadas', { method: 'POST' });
    } catch (error) {
        console.error('Erro ao marcar como notificadas:', error);
    }
}

// Atualizar badge de notificação na topbar
function atualizarBadgeNotificacao(total) {
    let badge = document.getElementById('divergenciasBadge');

    if (total > 0) {
        if (!badge) {
            // Criar badge se não existir
            const conflitosLink = document.querySelector('a[href="/conflitos"]');
            if (conflitosLink) {
                badge = document.createElement('span');
                badge.id = 'divergenciasBadge';
                badge.className = 'notification-badge';
                badge.textContent = total;
                conflitosLink.appendChild(badge);
            }
        } else {
            badge.textContent = total;
        }
    } else if (badge) {
        badge.remove();
    }
}

// Mostrar modal de divergências
function mostrarModalDivergencias() {
    if (modalAberto || !divergenciasAtivas) return;

    modalAberto = true;

    // Criar modal
    const modal = document.createElement('div');
    modal.id = 'modalDivergencias';
    modal.className = 'modal-divergencias';
    modal.innerHTML = `
        <div class="modal-divergencias-content">
            <div class="modal-divergencias-header">
                <h2>⚠️ Divergências Detectadas</h2>
                <button class="btn-fechar-modal" onclick="fecharModalDivergencias()">✕</button>
            </div>
            <div class="modal-divergencias-body">
                <p class="modal-divergencias-info">
                    Foram detectadas <strong>${divergenciasAtivas.total}</strong> divergência(s) entre o VPS e seu banco de dados local.
                </p>
                <div id="listaDivergencias"></div>
            </div>
            <div class="modal-divergencias-footer">
                <button class="btn-modal" onclick="abrirPaginaConflitos()">Ver Todas as Divergências</button>
                <button class="btn-modal btn-secondary" onclick="fecharModalDivergencias()">Fechar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    renderizarDivergenciasModal();

    // Adicionar CSS se não existir
    if (!document.getElementById('divergenciasModalCSS')) {
        const style = document.createElement('style');
        style.id = 'divergenciasModalCSS';
        style.textContent = `
            .modal-divergencias {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s;
            }
            
            .modal-divergencias-content {
                background: white;
                border-radius: 12px;
                max-width: 700px;
                width: 90%;
                max-height: 80vh;
                display: flex;
                flex-direction: column;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                animation: slideIn 0.3s;
            }
            
            @keyframes slideIn {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .modal-divergencias-header {
                padding: 20px;
                border-bottom: 2px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-divergencias-header h2 {
                margin: 0;
                color: #ff9800;
                font-size: 1.5em;
            }
            
            .btn-fechar-modal {
                background: none;
                border: none;
                font-size: 1.5em;
                cursor: pointer;
                color: #666;
                padding: 0;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                transition: all 0.2s;
            }
            
            .btn-fechar-modal:hover {
                background: #f0f0f0;
                color: #333;
            }
            
            .modal-divergencias-body {
                padding: 20px;
                overflow-y: auto;
                flex: 1;
            }
            
            .modal-divergencias-info {
                background: #fff3e0;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #ff9800;
                margin-bottom: 20px;
            }
            
            .divergencia-item-modal {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                border-left: 4px solid #2196f3;
            }
            
            .divergencia-item-modal.novo {
                border-left-color: #4caf50;
            }
            
            .divergencia-item-modal.atualizado {
                border-left-color: #ff9800;
            }
            
            .divergencia-item-modal h4 {
                margin: 0 0 10px 0;
                color: #333;
            }
            
            .divergencia-item-modal p {
                margin: 5px 0;
                color: #666;
                font-size: 0.9em;
            }
            
            .divergencia-acoes {
                margin-top: 10px;
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .btn-divergencia {
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.85em;
                transition: all 0.2s;
                font-weight: 500;
            }
            
            .btn-divergencia.aplicar {
                background: #4caf50;
                color: white;
            }
            
            .btn-divergencia.aplicar:hover {
                background: #45a049;
            }
            
            .btn-divergencia.ignorar {
                background: #ff9800;
                color: white;
            }
            
            .btn-divergencia.ignorar:hover {
                background: #f57c00;
            }
            
            .btn-divergencia.remover {
                background: #f44336;
                color: white;
            }
            
            .btn-divergencia.remover:hover {
                background: #da190b;
            }
            
            .btn-divergencia.baixar {
                background: #2196f3;
                color: white;
            }
            
            .btn-divergencia.baixar:hover {
                background: #0b7dda;
            }
            
            .btn-divergencia.enviar {
                background: #9c27b0;
                color: white;
            }
            
            .btn-divergencia.enviar:hover {
                background: #7b1fa2;
            }
            
            .modal-divergencias-footer {
                padding: 15px 20px;
                border-top: 2px solid #e0e0e0;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            
            .btn-modal {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                background: #2196f3;
                color: white;
                transition: all 0.2s;
            }
            
            .btn-modal:hover {
                background: #0b7dda;
            }
            
            .btn-modal.btn-secondary {
                background: #9e9e9e;
            }
            
            .btn-modal.btn-secondary:hover {
                background: #757575;
            }
            
            .notification-badge {
                background: #f44336;
                color: white;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 0.75em;
                margin-left: 8px;
                font-weight: bold;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Renderizar lista de divergências no modal
function renderizarDivergenciasModal() {
    const container = document.getElementById('listaDivergencias');
    if (!container || !divergenciasAtivas) return;

    let html = '';

    // Novos no VPS
    if (divergenciasAtivas.novos_vps && divergenciasAtivas.novos_vps.length > 0) {
        divergenciasAtivas.novos_vps.slice(0, 5).forEach(item => {
            html += renderizarItemDivergencia(item, 'novo');
        });
    }

    // Atualizados no VPS
    if (divergenciasAtivas.atualizados_vps && divergenciasAtivas.atualizados_vps.length > 0) {
        divergenciasAtivas.atualizados_vps.slice(0, 5).forEach(item => {
            html += renderizarItemDivergencia(item, 'atualizado');
        });
    }

    if (divergenciasAtivas.total > 5) {
        html += `<p style="text-align: center; color: #666; margin-top: 15px;">
            ... e mais ${divergenciasAtivas.total - 5} divergência(s). <a href="/conflitos">Ver todas</a>
        </p>`;
    }

    container.innerHTML = html;
}

// Renderizar item individual de divergência
function renderizarItemDivergencia(item, categoria) {
    const tipo = item.tipo || 'paciente';
    const id = item.id;
    const nome = item.nome || item.data || 'N/A';

    let html = `<div class="divergencia-item-modal ${categoria}">`;

    if (categoria === 'novo') {
        html += `
            <h4>📥 Novo ${tipo} no VPS</h4>
            <p><strong>${nome}</strong></p>
            ${item.unidade ? `<p>Unidade: ${item.unidade}</p>` : ''}
            <div class="divergencia-acoes">
                <button class="btn-divergencia aplicar" onclick="aplicarDivergencia('${id}', '${tipo}', ${JSON.stringify(item.dados).replace(/"/g, '&quot;')})">
                    ✓ Aplicar
                </button>
                <button class="btn-divergencia ignorar" onclick="ignorarDivergencia('${id}')">
                    ⏸ Ignorar
                </button>
                <button class="btn-divergencia remover" onclick="removerDivergencia('${id}')">
                    ✕ Remover
                </button>
            </div>
        `;
    } else if (categoria === 'atualizado') {
        html += `
            <h4>🔄 ${tipo.charAt(0).toUpperCase() + tipo.slice(1)} atualizado no VPS</h4>
            <p><strong>${nome}</strong></p>
            <p style="font-size: 0.85em; color: #999;">Versão do VPS é mais recente</p>
            <div class="divergencia-acoes">
                <button class="btn-divergencia baixar" onclick="atualizarDivergencia('${id}', '${tipo}', 'baixar')">
                    ⬇ Baixar do VPS
                </button>
                <button class="btn-divergencia enviar" onclick="atualizarDivergencia('${id}', '${tipo}', 'enviar')">
                    ⬆ Enviar para VPS
                </button>
                <button class="btn-divergencia ignorar" onclick="ignorarDivergencia('${id}')">
                    ⏸ Ignorar
                </button>
            </div>
        `;
    }

    html += `</div>`;
    return html;
}

// Aplicar divergência (baixar do VPS)
async function aplicarDivergencia(itemId, tipo, dados) {
    try {
        const response = await fetch('/api/vps/divergencias/aplicar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, tipo: tipo, dados: dados })
        });

        const result = await response.json();

        if (result.success) {
            alert('✓ ' + result.message);
            await verificarDivergencias();
            fecharModalDivergencias();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao aplicar divergência:', error);
        alert('Erro ao aplicar divergência');
    }
}

// Ignorar divergência temporariamente
async function ignorarDivergencia(itemId) {
    try {
        const response = await fetch('/api/vps/divergencias/ignorar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });

        const result = await response.json();

        if (result.success) {
            await verificarDivergencias();
            fecharModalDivergencias();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao ignorar divergência:', error);
    }
}

// Remover divergência permanentemente
async function removerDivergencia(itemId) {
    if (!confirm('Tem certeza que deseja remover esta divergência permanentemente?')) {
        return;
    }

    try {
        const response = await fetch('/api/vps/divergencias/remover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });

        const result = await response.json();

        if (result.success) {
            await verificarDivergencias();
            fecharModalDivergencias();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao remover divergência:', error);
    }
}

// Atualizar divergência (baixar ou enviar)
async function atualizarDivergencia(itemId, tipo, acao) {
    try {
        const response = await fetch('/api/vps/divergencias/atualizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, tipo: tipo, acao: acao })
        });

        const result = await response.json();

        if (result.success) {
            alert('✓ ' + result.message);
            await verificarDivergencias();
            fecharModalDivergencias();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao atualizar divergência:', error);
        alert('Erro ao processar ação');
    }
}

// Fechar modal
function fecharModalDivergencias() {
    const modal = document.getElementById('modalDivergencias');
    if (modal) {
        modal.remove();
    }
    modalAberto = false;
}

// Abrir página de conflitos
async function abrirPaginaConflitos() {
    // Marcar divergências como vistas antes de navegar
    try {
        await fetch('/api/vps/divergencias/marcar-visto', { method: 'POST' });
    } catch (error) {
        console.error('Erro ao marcar divergências como vistas:', error);
    }
    window.location.href = '/conflitos';
}

// Exportar funções globais
window.iniciarVerificacaoDivergencias = iniciarVerificacaoDivergencias;
window.pararVerificacaoDivergencias = pararVerificacaoDivergencias;
window.verificarDivergencias = verificarDivergencias;
window.fecharModalDivergencias = fecharModalDivergencias;
window.aplicarDivergencia = aplicarDivergencia;
window.ignorarDivergencia = ignorarDivergencia;
window.removerDivergencia = removerDivergencia;
window.atualizarDivergencia = atualizarDivergencia;
window.abrirPaginaConflitos = abrirPaginaConflitos;
window.verificarSeHaDivergenciasNovas = verificarSeHaDivergenciasNovas;
window.marcarDivergenciasComoNotificadas = marcarDivergenciasComoNotificadas;
