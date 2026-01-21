// Módulo do calendário

// Variáveis
let dataAtualCalendario = new Date();
let agendamentosCalendario = [];
let diaExpandido = null;

// Carregar calendário completo
async function carregarCalendario() {
    try {
        const calendarioContainer = document.querySelector('.calendario-container');
        if (calendarioContainer) {
            calendarioContainer.style.opacity = '0.5';
        }

        await buscarAgendamentosPorPeriodo();
        await gerarCalendario();
        configurarControlesCalendario();

        if (calendarioContainer) {
            calendarioContainer.style.opacity = '1';
        }
    } catch (error) {
        console.error('Erro ao carregar calendário:', error);
        mostrarErro('Erro ao carregar calendário');
    }
}

// Buscar agendamentos por período
async function buscarAgendamentosPorPeriodo() {
    const ano = dataAtualCalendario.getFullYear();
    const mes = dataAtualCalendario.getMonth() + 1;

    const primeiroDia = new Date(ano, mes - 1, 1);
    const ultimoDia = new Date(ano, mes, 0);

    const dataInicio = primeiroDia.toISOString().split('T')[0];
    const dataFim = ultimoDia.toISOString().split('T')[0];

    try {
        const response = await fetch(`/api/agendamentos?data_inicio=${dataInicio}&data_fim=${dataFim}`);
        const data = await response.json();

        if (data.success && data.agendamentos) {
            agendamentosCalendario = data.agendamentos;
        } else {
            agendamentosCalendario = [];
        }
    } catch (error) {
        console.error('Erro ao buscar agendamentos:', error);
        agendamentosCalendario = [];
    }
}

// Gerar calendário mensal
async function gerarCalendario() {
    const ano = dataAtualCalendario.getFullYear();
    const mes = dataAtualCalendario.getMonth();

    const tituloMes = document.getElementById('mesAtual');
    if (tituloMes) {
        const nomeMeses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];
        tituloMes.textContent = `${nomeMeses[mes]} ${ano}`;
    }

    await renderizarDiasCalendario();
}

// Verificar se um dia tem agendamentos atrasados
function diaTemAgendamentosAtrasados(dataFormatada) {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    const dataComparar = new Date(dataFormatada + 'T00:00:00');
    
    // Qualquer data anterior a hoje está atrasada
    return dataComparar < hoje;
}

// Renderizar dias do calendário
async function renderizarDiasCalendario() {
    const containerDias = document.getElementById('diasCalendario');
    if (!containerDias) return;

    const ano = dataAtualCalendario.getFullYear();
    const mes = dataAtualCalendario.getMonth();

    const primeiroDia = new Date(ano, mes, 1);
    const diaSemanaPrimeiro = primeiroDia.getDay();

    const ultimoDia = new Date(ano, mes + 1, 0);
    const ultimoDiaMes = ultimoDia.getDate();

    const agendamentosPorDia = {};
    agendamentosCalendario.forEach(agendamento => {
        const data = agendamento.data_consulta;
        if (!agendamentosPorDia[data]) {
            agendamentosPorDia[data] = [];
        }
        agendamentosPorDia[data].push(agendamento);
    });

    let html = '';

    for (let i = 0; i < diaSemanaPrimeiro; i++) {
        html += '<div class="dia-calendario dia-vazio"></div>';
    }

    for (let dia = 1; dia <= ultimoDiaMes; dia++) {
        const dataAtual = new Date(ano, mes, dia);
        const dataFormatada = dataAtual.toISOString().split('T')[0];
        const agendamentosDia = agendamentosPorDia[dataFormatada] || [];
        const temAgendamentos = agendamentosDia.length > 0;
        
        // Verificar se o dia está atrasado (qualquer data passada)
        const temAtrasados = temAgendamentos && diaTemAgendamentosAtrasados(dataFormatada);
        
        const classes = `dia-calendario ${temAgendamentos ? 'dia-com-agendamentos' : ''} ${temAtrasados ? 'dia-com-atrasados' : ''}`;
        const badge = temAgendamentos ? `<span class="badge-agendamentos ${temAtrasados ? 'badge-atrasado-calendario' : ''}">${agendamentosDia.length}</span>` : '';

        html += `
            <div class="${classes}" data-data="${dataFormatada}" data-tem-atrasados="${temAtrasados}">
                <div class="numero-dia">${dia}</div>
                ${badge}
                ${temAtrasados ? '<span class="icone-atrasado">⚠️</span>' : ''}
            </div>
        `;
    }

    containerDias.innerHTML = html;

    // Event listeners para dias com agendamentos
    document.querySelectorAll('.dia-com-agendamentos').forEach(dia => {
        const temAtrasados = dia.dataset.temAtrasados === 'true';
        
        dia.addEventListener('click', (e) => {
            if (temAtrasados) {
                // Redirecionar para o histórico
                e.preventDefault();
                mostrarView('historico');
                
                // Mostrar mensagem
                setTimeout(() => {
                    mostrarMensagem('Dia com agendamentos atrasados selecionado. Atualize o status no histórico.', false);
                }, 300);
            } else {
                // Comportamento normal - expandir o dia
                expandirDia(dia.dataset.data);
            }
        });
    });
}

// Configurar controles do calendário
function configurarControlesCalendario() {
    const btnMesAnterior = document.getElementById('mesAnterior');
    const btnProximoMes = document.getElementById('proximoMes');

    if (btnMesAnterior) {
        btnMesAnterior.onclick = () => {
            dataAtualCalendario.setMonth(dataAtualCalendario.getMonth() - 1);
            carregarCalendario();
            colapsarDiaExpandido();
        };
    }

    if (btnProximoMes) {
        btnProximoMes.onclick = () => {
            dataAtualCalendario.setMonth(dataAtualCalendario.getMonth() + 1);
            carregarCalendario();
            colapsarDiaExpandido();
        };
    }

    configurarModalPerfil();
}

// Expandir/colapsar dia
async function expandirDia(data) {
    const expansaoContainer = document.getElementById('expansaoDia');
    const tituloDia = document.getElementById('tituloDiaExpandido');
    const agendamentosContainer = document.getElementById('agendamentosDia');

    if (!expansaoContainer || !tituloDia || !agendamentosContainer) return;

    if (diaExpandido === data) {
        colapsarDiaExpandido();
        return;
    }

    diaExpandido = data;

    const dataObj = new Date(data + 'T00:00:00');
    const nomeMeses = [
        'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ];
    const nomeDia = dataObj.toLocaleDateString('pt-BR', { weekday: 'long' });
    const dia = dataObj.getDate();
    const mes = nomeMeses[dataObj.getMonth()];
    const ano = dataObj.getFullYear();

    tituloDia.textContent = `Agendamentos de ${nomeDia}, ${dia} de ${mes} de ${ano}`;

    const agendamentosDia = agendamentosCalendario.filter(ag => ag.data_consulta === data);
    agendamentosDia.sort((a, b) => a.hora_consulta.localeCompare(b.hora_consulta));
    
    const agendamentosPassados = agendamentosDia.filter(ag => window.isAgendamentoPassado(ag));
    
    if (agendamentosPassados.length > 0) {
        setTimeout(() => {
            window.mostrarModalConfirmarAtendimento(agendamentosPassados[0]);
        }, 500);
    }

    let html = '';

    if (agendamentosDia.length === 0) {
        html = '<div class="empty-state"><div class="empty-state-icon">📅</div><div class="empty-state-text">Nenhum agendamento neste dia</div></div>';
    } else {
        for (const agendamento of agendamentosDia) {
            let paciente = null;
            try {
                paciente = await obterDadosPaciente(agendamento.paciente_id);
            } catch (error) {
                console.error('Erro ao buscar dados da paciente:', error);
            }

            const horaFormatada = formatarHora(agendamento.hora_consulta);
            const statusClass = `status-${agendamento.status}`;
            const statusLabel = formatarStatus(agendamento.status);
            const tipoLabel = formatarTipoConsulta(agendamento.tipo_consulta);
            
            const ePassado = window.isAgendamentoPassado(agendamento);
            const eRevisado = window.isAgendamentoRevisado(agendamento);
            const estiloVermelho = ePassado ? 'style="border: 2px solid #d32f2f; background: #ffebee;"' : '';
            
            let badgeStatus = '';
            if (ePassado) {
                badgeStatus = '<span style="color: #d32f2f; font-weight: bold;">⚠️ Pendente</span>';
            } else if (eRevisado) {
                const agora = new Date();
                const dataAgendamento = new Date(agendamento.data_consulta + 'T' + (agendamento.hora_consulta || '00:00:00'));
                if (dataAgendamento < agora) {
                    badgeStatus = '<span style="color: #388e3c; font-weight: bold;">✅ Revisada</span>';
                }
            }

            html += `
                <div class="agendamento-expandido" onclick="abrirPerfilCompleto('${agendamento.paciente_id}')" ${estiloVermelho}>
                    <div class="agendamento-expandido-header">
                        <div class="hora-agendamento">${horaFormatada}</div>
                        <span class="status-agendamento ${statusClass}">${statusLabel}</span>
                        ${badgeStatus}
                    </div>
                    <div class="perfil-resumido">
                        <div class="nome-paciente">${agendamento.nome_gestante || 'Nome não informado'}</div>
                        ${tipoLabel ? `<div class="tipo-consulta">${tipoLabel}</div>` : ''}
                        ${paciente ? exibirPerfilResumido(paciente) : ''}
                        ${agendamento.observacoes ? `<div class="observacoes-agendamento">${agendamento.observacoes}</div>` : ''}
                    </div>
                </div>
            `;
        }
    }

    agendamentosContainer.innerHTML = html;

    expansaoContainer.style.display = 'block';
    setTimeout(() => {
        expansaoContainer.style.opacity = '1';
        expansaoContainer.style.transform = 'translateY(0)';
    }, 10);

    setTimeout(() => {
        expansaoContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
}

// Colapsar dia expandido
function colapsarDiaExpandido() {
    const expansaoContainer = document.getElementById('expansaoDia');
    if (!expansaoContainer) return;

    diaExpandido = null;

    expansaoContainer.style.opacity = '0';
    expansaoContainer.style.transform = 'translateY(-20px)';

    setTimeout(() => {
        expansaoContainer.style.display = 'none';
    }, 300);
}

// Obter dia expandido
function obterDiaExpandido() {
    return diaExpandido;
}

// Exportar funções
window.carregarCalendario = carregarCalendario;
window.expandirDia = expandirDia;
window.colapsarDiaExpandido = colapsarDiaExpandido;
window.obterDiaExpandido = obterDiaExpandido;
