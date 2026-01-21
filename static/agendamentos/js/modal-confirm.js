// Módulo do modal de confirmação de atendimento

// Variável
let agendamentoAtualModal = null;

// Verificar se um agendamento foi revisado (confirmado)
function isAgendamentoRevisado(agendamento) {
    const statusRevisado = agendamento.status === 'realizado' || agendamento.status === 'falta';
    const temMotivo = agendamento.observacoes && 
        agendamento.observacoes.includes('Motivo de não realização');
    
    return statusRevisado || temMotivo;
}

// Verificar se um agendamento é passado (data e hora já passaram)
function isAgendamentoPassado(agendamento) {
    try {
        const agora = new Date();
        agora.setSeconds(0, 0);
        
        let dataHoraAgendamento;
        if (agendamento.hora_consulta) {
            const [hora, minuto] = agendamento.hora_consulta.split(':');
            dataHoraAgendamento = new Date(`${agendamento.data_consulta}T${hora}:${minuto}:00`);
        } else {
            dataHoraAgendamento = new Date(`${agendamento.data_consulta}T23:59:59`);
        }
        
        const jaPassou = dataHoraAgendamento < agora;
        const naoFinalizado = agendamento.status !== 'realizado' && 
                             agendamento.status !== 'falta' && 
                             agendamento.status !== 'cancelado';
        const naoRevisado = !isAgendamentoRevisado(agendamento);
        
        return jaPassou && naoFinalizado && naoRevisado;
    } catch (error) {
        console.error('Erro ao verificar se agendamento é passado:', error);
        return false;
    }
}

// Mostrar modal de confirmação de atendimento
function mostrarModalConfirmarAtendimento(agendamento) {
    agendamentoAtualModal = agendamento;
    
    const modal = document.getElementById('modalConfirmarAtendimento');
    const infoDiv = document.getElementById('infoAgendamentoConfirmar');
    const divMotivo = document.getElementById('divMotivoNaoRealizado');
    const motivoTextarea = document.getElementById('motivoNaoRealizado');
    
    if (!modal || !infoDiv) return;
    
    if (motivoTextarea) {
        motivoTextarea.value = '';
    }
    if (divMotivo) {
        divMotivo.style.display = 'none';
    }
    
    const dataFormatada = formatarData(agendamento.data_consulta);
    const horaFormatada = formatarHora(agendamento.hora_consulta);
    const tipoLabel = formatarTipoConsulta(agendamento.tipo_consulta);
    
    infoDiv.innerHTML = `
        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            👤 ${agendamento.nome_gestante || 'Nome não informado'}
        </div>
        <div style="margin-bottom: 5px;">
            <strong>📅 Data:</strong> ${dataFormatada}
        </div>
        <div style="margin-bottom: 5px;">
            <strong>🕐 Hora:</strong> ${horaFormatada}
        </div>
        ${tipoLabel ? `<div style="margin-bottom: 5px;"><strong>🏥 Tipo:</strong> ${tipoLabel}</div>` : ''}
        ${agendamento.unidade_saude ? `<div><strong>🏢 Unidade:</strong> ${agendamento.unidade_saude}</div>` : ''}
    `;
    
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);
}

// Fechar modal de confirmação
function fecharModalConfirmarAtendimento() {
    const modal = document.getElementById('modalConfirmarAtendimento');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
            agendamentoAtualModal = null;
        }, 300);
    }
}

// Marcar atendimento como realizado
async function marcarComoRealizado() {
    if (!agendamentoAtualModal) return;
    
    try {
        const dados = {
            status: 'realizado'
        };
        
        const response = await fetch(`/api/agendamentos/${agendamentoAtualModal.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            mostrarMensagem('Atendimento marcado como realizado!');
            fecharModalConfirmarAtendimento();
            
            await window.carregarCalendario();
            
            const diaExpandido = window.obterDiaExpandido();
            if (diaExpandido) {
                window.expandirDia?.(diaExpandido);
            }
            
            const viewHistorico = document.getElementById('historico');
            if (viewHistorico && viewHistorico.classList.contains('ativa')) {
                await window.carregarHistorico?.();
            }
        } else {
            mostrarMensagem(resultado.message || 'Erro ao atualizar agendamento', true);
        }
    } catch (error) {
        console.error('Erro ao marcar como realizado:', error);
        mostrarMensagem('Erro ao atualizar agendamento', true);
    }
}

// Salvar motivo de não realizado
async function salvarMotivoNaoRealizado() {
    if (!agendamentoAtualModal) return;
    
    const motivoTextarea = document.getElementById('motivoNaoRealizado');
    const motivo = motivoTextarea ? motivoTextarea.value.trim() : '';
    
    if (!motivo) {
        mostrarMensagem('Por favor, informe o motivo pelo qual o atendimento não foi realizado', true);
        return;
    }
    
    try {
        const observacoesAtuais = agendamentoAtualModal.observacoes || '';
        const novaObservacao = observacoesAtuais 
            ? `${observacoesAtuais}\n\n❌ Motivo de não realização: ${motivo}`
            : `❌ Motivo de não realização: ${motivo}`;
        
        const dados = {
            status: 'falta',
            observacoes: novaObservacao
        };
        
        const response = await fetch(`/api/agendamentos/${agendamentoAtualModal.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            mostrarMensagem('Status atualizado: Agendamento não realizado');
            fecharModalConfirmarAtendimento();
            
            await window.carregarCalendario();
            
            const diaExpandido = window.obterDiaExpandido();
            if (diaExpandido) {
                window.expandirDia?.(diaExpandido);
            }
            
            const viewHistorico = document.getElementById('historico');
            if (viewHistorico && viewHistorico.classList.contains('ativa')) {
                await window.carregarHistorico?.();
            }
        } else {
            mostrarMensagem(resultado.message || 'Erro ao atualizar agendamento', true);
        }
    } catch (error) {
        console.error('Erro ao salvar motivo:', error);
        mostrarMensagem('Erro ao atualizar agendamento', true);
    }
}

// Configurar eventos do modal de confirmação
function configurarModalConfirmarAtendimento() {
    const modal = document.getElementById('modalConfirmarAtendimento');
    const btnFechar = document.getElementById('fecharModalConfirmarAtendimento');
    const btnSim = document.getElementById('btnAtendimentoSim');
    const btnNao = document.getElementById('btnAtendimentoNao');
    const btnSalvarMotivo = document.getElementById('btnSalvarMotivo');
    const btnCancelarMotivo = document.getElementById('btnCancelarMotivo');
    const divMotivo = document.getElementById('divMotivoNaoRealizado');
    
    if (btnFechar) {
        btnFechar.addEventListener('click', fecharModalConfirmarAtendimento);
    }
    
    if (btnSim) {
        btnSim.addEventListener('click', marcarComoRealizado);
    }
    
    if (btnNao) {
        btnNao.addEventListener('click', () => {
            if (divMotivo) {
                divMotivo.style.display = 'block';
            }
        });
    }
    
    if (btnSalvarMotivo) {
        btnSalvarMotivo.addEventListener('click', salvarMotivoNaoRealizado);
    }
    
    if (btnCancelarMotivo) {
        btnCancelarMotivo.addEventListener('click', () => {
            if (divMotivo) {
                divMotivo.style.display = 'none';
            }
            const motivoTextarea = document.getElementById('motivoNaoRealizado');
            if (motivoTextarea) {
                motivoTextarea.value = '';
            }
        });
    }
    
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                fecharModalConfirmarAtendimento();
            }
        });
    }
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.style.display !== 'none') {
            fecharModalConfirmarAtendimento();
        }
    });
}

// Exportar funções
window.isAgendamentoRevisado = isAgendamentoRevisado;
window.isAgendamentoPassado = isAgendamentoPassado;
window.mostrarModalConfirmarAtendimento = mostrarModalConfirmarAtendimento;
window.configurarModalConfirmarAtendimento = configurarModalConfirmarAtendimento;
