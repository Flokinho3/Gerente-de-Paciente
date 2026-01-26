// Sistema de Alertas de Agendamentos Próximos
// Alerta agendamentos do dia atual

// Armazenar alertas desativados no localStorage
const ALERTAS_AGENDAMENTOS_DESATIVADOS_KEY = 'alertas_agendamentos_desativados';

// Variável para controlar o índice do alerta atual
let indiceAlertaAtualAgendamentos = 0;
let agendamentosAlertas = [];
let alertaAgendamentosMinimizado = false;

// Nome do cookie para salvar estado de minimização
const COOKIE_ALERTA_AGENDAMENTOS_MINIMIZADO = 'alerta_agendamentos_minimizado';

// Funções para gerenciar cookies
function setCookieAgendamentos(nome, valor, dias = 365) {
    const data = new Date();
    data.setTime(data.getTime() + (dias * 24 * 60 * 60 * 1000));
    const expires = `expires=${data.toUTCString()}`;
    document.cookie = `${nome}=${valor};${expires};path=/`;
}

function getCookieAgendamentos(nome) {
    const nomeCompleto = `${nome}=`;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(nomeCompleto) === 0) {
            return cookie.substring(nomeCompleto.length);
        }
    }
    return null;
}

function deleteCookieAgendamentos(nome) {
    document.cookie = `${nome}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

// Função para obter alertas desativados
function getAlertasAgendamentosDesativados() {
    const desativados = localStorage.getItem(ALERTAS_AGENDAMENTOS_DESATIVADOS_KEY);
    return desativados ? JSON.parse(desativados) : [];
}

// Função para salvar alertas desativados
function salvarAlertasAgendamentosDesativados(ids) {
    localStorage.setItem(ALERTAS_AGENDAMENTOS_DESATIVADOS_KEY, JSON.stringify(ids));
}

// Função para desativar alerta de um agendamento
function desativarAlertaAgendamento(agendamentoId) {
    const desativados = getAlertasAgendamentosDesativados();
    if (!desativados.includes(agendamentoId)) {
        desativados.push(agendamentoId);
        salvarAlertasAgendamentosDesativados(desativados);
    }
}

// Função para reativar alerta de um agendamento
function reativarAlertaAgendamento(agendamentoId) {
    const desativados = getAlertasAgendamentosDesativados();
    const index = desativados.indexOf(agendamentoId);
    if (index > -1) {
        desativados.splice(index, 1);
        salvarAlertasAgendamentosDesativados(desativados);
    }
}

// Função para verificar se alerta está desativado
function isAlertaAgendamentoDesativado(agendamentoId) {
    const desativados = getAlertasAgendamentosDesativados();
    return desativados.includes(agendamentoId);
}

// Função para calcular horas até o agendamento
function calcularHorasAteAgendamento(dataConsulta, horaConsulta) {
    if (!dataConsulta) return null;
    
    try {
        const hoje = new Date();
        hoje.setSeconds(0, 0);
        
        // Combinar data e hora
        let dataHoraAgendamento;
        if (horaConsulta) {
            const [hora, minuto] = horaConsulta.split(':');
            dataHoraAgendamento = new Date(`${dataConsulta}T${hora}:${minuto}:00`);
        } else {
            dataHoraAgendamento = new Date(`${dataConsulta}T00:00:00`);
        }
        
        const diffTime = dataHoraAgendamento - hoje;
        const diffHours = diffTime / (1000 * 60 * 60);
        
        return diffHours;
    } catch (e) {
        console.error('Erro ao calcular horas até agendamento:', e);
        return null;
    }
}

// Função para buscar agendamentos próximos
async function buscarAgendamentosProximos() {
    try {
        const response = await fetch('/api/agendamentos');
        const data = await response.json();
        
        if (!data.success || !data.agendamentos) {
            return [];
        }
        
        const alertasDesativados = getAlertasAgendamentosDesativados();
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        
        const agendamentosProximos = data.agendamentos
            .filter(agendamento => {
                // Verificar se alerta está desativado
                if (isAlertaAgendamentoDesativado(agendamento.id)) {
                    return false;
                }
                
                // Filtrar apenas agendados ou confirmados
                if (agendamento.status !== 'agendado' && agendamento.status !== 'confirmado') {
                    return false;
                }
                
                // Verificar se é do dia atual
                const hoje = new Date();
                hoje.setHours(0, 0, 0, 0);
                const dataAgendamento = new Date(agendamento.data_consulta + 'T00:00:00');
                dataAgendamento.setHours(0, 0, 0, 0);
                
                // Verificar se é do dia atual
                const mesmoDia = dataAgendamento.getTime() === hoje.getTime();
                
                if (!mesmoDia) {
                    return false;
                }
                
                const horasAteAgendamento = calcularHorasAteAgendamento(
                    agendamento.data_consulta,
                    agendamento.hora_consulta
                );
                
                // Retornar apenas agendamentos do dia atual (e não passados)
                return horasAteAgendamento !== null && horasAteAgendamento >= 0;
            })
            .map(agendamento => {
                const horasAteAgendamento = calcularHorasAteAgendamento(
                    agendamento.data_consulta,
                    agendamento.hora_consulta
                );
                return {
                    ...agendamento,
                    horasAteAgendamento: horasAteAgendamento
                };
            })
            .sort((a, b) => a.horasAteAgendamento - b.horasAteAgendamento); // Ordenar por horas restantes (menor primeiro)
        
        return agendamentosProximos;
    } catch (error) {
        console.error('Erro ao buscar agendamentos próximos:', error);
        return [];
    }
}

// Função para formatar mensagem de horas
function formatarMensagemHoras(horas) {
    if (horas < 0) {
        return `Agendamento passado há ${Math.abs(Math.floor(horas))} hora(s)`;
    } else if (horas < 1) {
        const minutos = Math.floor(horas * 60);
        return minutos <= 0 ? 'Agendamento agora!' : `Agendamento em ${minutos} minuto(s)`;
    } else if (horas === 1) {
        return 'Agendamento em 1 hora';
    } else {
        return `Agendamento em ${Math.floor(horas)} horas`;
    }
}

// Função para renderizar alertas
function renderizarAlertasAgendamentos(agendamentos) {
    const container = document.getElementById('alertas-agendamentos-container');
    if (!container) return;
    
    // Salvar lista de agendamentos
    agendamentosAlertas = agendamentos;
    indiceAlertaAtualAgendamentos = 0;
    
    // Atualizar contador
    const contador = document.getElementById('alertas-agendamentos-contador');
    if (contador) {
        contador.textContent = agendamentos.length;
    }
    
    if (agendamentos.length === 0) {
        container.style.display = 'none';
        // Esconder botão minimizado se não houver alertas
        const btnMinimizado = document.getElementById('alerta-agendamentos-minimizado-btn');
        if (btnMinimizado) {
            btnMinimizado.style.display = 'none';
        }
        return;
    }
    
    // Verificar cookie para estado de minimização
    const cookieMinimizado = getCookieAgendamentos(COOKIE_ALERTA_AGENDAMENTOS_MINIMIZADO);
    if (cookieMinimizado === 'true') {
        alertaAgendamentosMinimizado = true;
    }
    
    // Se não estiver minimizado, mostrar container
    if (!alertaAgendamentosMinimizado) {
        container.style.display = 'flex';
    } else {
        container.style.display = 'none';
    }
    
    // Adicionar botão de minimizar no header se não existir
    const header = container.querySelector('.alertas-header-agendamentos');
    if (header) {
        let btnMinimizar = header.querySelector('.btn-minimizar-alerta');
        if (!btnMinimizar) {
            btnMinimizar = document.createElement('button');
            btnMinimizar.className = 'btn-minimizar-alerta';
            btnMinimizar.innerHTML = '−';
            btnMinimizar.title = 'Minimizar alertas';
            btnMinimizar.onclick = minimizarAlertaAgendamentos;
            header.appendChild(btnMinimizar);
        }
    }
    
    // Criar ou atualizar botão minimizado
    criarBotaoMinimizadoAgendamentos();
    
    const alertasList = document.getElementById('alertas-agendamentos-list');
    if (!alertasList) return;
    
    // Renderizar todos os alertas, mas mostrar apenas um por vez
    alertasList.innerHTML = agendamentos.map((agendamento, index) => {
        const nomePaciente = agendamento.nome_gestante || agendamento.paciente_nome || 'Paciente não informado';
        const dataFormatada = formatarDataAgendamento(agendamento.data_consulta);
        const horaFormatada = agendamento.hora_consulta || 'Não informado';
        const horasAteAgendamento = agendamento.horasAteAgendamento;
        const mensagemHoras = formatarMensagemHoras(horasAteAgendamento);
        const isUrgente = horasAteAgendamento <= 2; // Urgente se for em até 2 horas
        
        return `
            <div class="alerta-item-agendamentos ${isUrgente ? 'alerta-urgente-agendamentos' : ''} ${index === 0 ? 'alerta-ativo-agendamentos' : ''}" 
                 data-agendamento-id="${agendamento.id}" 
                 data-index="${index}"
                 style="display: ${index === 0 ? 'block' : 'none'};">
                <div class="alerta-info-agendamentos">
                    <div class="alerta-nome-agendamentos">${nomePaciente}</div>
                    <div class="alerta-detalhes-agendamentos">
                        <span class="alerta-horas ${isUrgente ? 'horas-urgente-agendamentos' : ''}">${mensagemHoras}</span>
                        <span class="alerta-data-agendamentos">📅 ${dataFormatada} às ${horaFormatada}</span>
                        ${agendamento.tipo_consulta ? `<span class="alerta-tipo-agendamentos">Tipo: ${formatarTipoConsulta(agendamento.tipo_consulta)}</span>` : ''}
                    </div>
                </div>
                <div class="alerta-actions-agendamentos">
                    <button class="btn-alerta-ver-agendamentos" onclick="irParaAgendamento('${agendamento.id}')">
                        Ver Detalhes
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Adicionar controles de navegação se houver mais de um alerta
    if (agendamentos.length > 1) {
        const controlesHTML = `
            <div class="alerta-navegacao-agendamentos">
                <button class="btn-nav-alerta-agendamentos" onclick="navegarAlertaAgendamentos(-1)" id="btnAnteriorAlertaAgendamentos" ${indiceAlertaAtualAgendamentos === 0 ? 'disabled' : ''}>
                    ← Anterior
                </button>
                <span class="alerta-indicador-agendamentos">${indiceAlertaAtualAgendamentos + 1} / ${agendamentos.length}</span>
                <button class="btn-nav-alerta-agendamentos" onclick="navegarAlertaAgendamentos(1)" id="btnProximoAlertaAgendamentos" ${indiceAlertaAtualAgendamentos === agendamentos.length - 1 ? 'disabled' : ''}>
                    Próximo →
                </button>
            </div>
        `;
        
        // Verificar se já existe navegação, se não, adicionar
        let navegacao = alertasList.querySelector('.alerta-navegacao-agendamentos');
        if (!navegacao) {
            alertasList.insertAdjacentHTML('beforeend', controlesHTML);
        } else {
            navegacao.outerHTML = controlesHTML;
        }
    } else {
        // Remover navegação se houver apenas um alerta
        const navegacao = alertasList.querySelector('.alerta-navegacao-agendamentos');
        if (navegacao) {
            navegacao.remove();
        }
    }
}

// Função para navegar entre alertas
function navegarAlertaAgendamentos(direcao) {
    if (agendamentosAlertas.length === 0) return;
    
    const novoIndice = indiceAlertaAtualAgendamentos + direcao;
    
    if (novoIndice < 0 || novoIndice >= agendamentosAlertas.length) return;
    
    const alertasList = document.getElementById('alertas-agendamentos-list');
    if (!alertasList) return;
    
    // Esconder alerta atual
    const alertaAtual = alertasList.querySelector(`.alerta-item-agendamentos[data-index="${indiceAlertaAtualAgendamentos}"]`);
    if (alertaAtual) {
        alertaAtual.style.display = 'none';
        alertaAtual.classList.remove('alerta-ativo-agendamentos');
    }
    
    // Atualizar índice
    indiceAlertaAtualAgendamentos = novoIndice;
    
    // Mostrar novo alerta
    const novoAlerta = alertasList.querySelector(`.alerta-item-agendamentos[data-index="${indiceAlertaAtualAgendamentos}"]`);
    if (novoAlerta) {
        novoAlerta.style.display = 'block';
        novoAlerta.classList.add('alerta-ativo-agendamentos');
        
        // Scroll suave até o alerta
        novoAlerta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Atualizar botões de navegação
    const btnAnterior = document.getElementById('btnAnteriorAlertaAgendamentos');
    const btnProximo = document.getElementById('btnProximoAlertaAgendamentos');
    const indicador = alertasList.querySelector('.alerta-indicador-agendamentos');
    
    if (btnAnterior) {
        btnAnterior.disabled = indiceAlertaAtualAgendamentos === 0;
    }
    if (btnProximo) {
        btnProximo.disabled = indiceAlertaAtualAgendamentos === agendamentosAlertas.length - 1;
    }
    if (indicador) {
        indicador.textContent = `${indiceAlertaAtualAgendamentos + 1} / ${agendamentosAlertas.length}`;
    }
}

// Função para formatar data do agendamento
function formatarDataAgendamento(data) {
    if (!data) return 'Não informado';
    
    try {
        const [ano, mes, dia] = data.split('-');
        if (ano && mes && dia) {
            return `${dia}/${mes}/${ano}`;
        }
        return data;
    } catch (e) {
        return data;
    }
}

// Função para formatar tipo de consulta
function formatarTipoConsulta(tipo) {
    const tipos = {
        'consulta_pre_natal': 'Consulta Pré-Natal',
        'retorno': 'Retorno',
        'avaliacao': 'Avaliação',
        'exame': 'Exame',
        'outro': 'Outro'
    };
    return tipos[tipo] || tipo;
}

// Função para ir ao agendamento
async function irParaAgendamento(agendamentoId) {
    // Verificar se estamos na página de agendamentos
    if (window.location.pathname === '/agendamentos' || window.location.pathname === '/agendamentos/') {
        // Verificar se existe função mostrarView para mudar de view
        if (typeof mostrarView === 'function') {
            // Mudar para a view de agenda se não estiver nela
            const agendaView = document.getElementById('agenda');
            if (agendaView && !agendaView.classList.contains('ativa')) {
                mostrarView('agenda');
                // Aguardar a view mudar e carregar
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        }
        
        // Verificar se a lista está carregada
        const agendamentosList = document.getElementById('agendamentosList');
        const item = document.querySelector(`[data-agendamento-id="${agendamentoId}"]`);
        
        // Se a lista não existe ou o item não foi encontrado, carregar agendamentos
        if ((!agendamentosList || !item) && typeof carregarAgendamentos === 'function') {
            await carregarAgendamentos();
            await new Promise(resolve => setTimeout(resolve, 300));
        }
        
        // Função para destacar o agendamento
        const destacarAgendamento = () => {
            const item = document.querySelector(`[data-agendamento-id="${agendamentoId}"]`);
            if (item) {
                // Scroll até o item
                setTimeout(() => {
                    item.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Adicionar animação de destaque
                    item.style.transition = 'all 0.3s ease';
                    item.style.boxShadow = '0 0 20px rgba(33, 150, 243, 0.5)';
                    item.style.transform = 'scale(1.02)';
                    item.style.border = '2px solid rgba(33, 150, 243, 0.5)';
                    
                    setTimeout(() => {
                        item.style.boxShadow = '';
                        item.style.transform = '';
                        item.style.border = '';
                    }, 2000);
                }, 300);
            }
        };
        
        // Scroll até a lista de agendamentos
        const lista = document.getElementById('agendamentosList');
        if (lista) {
            lista.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Destacar o agendamento
        setTimeout(destacarAgendamento, 500);
    }
}

// Função para minimizar alerta
function minimizarAlertaAgendamentos() {
    alertaAgendamentosMinimizado = true;
    
    // Salvar estado no cookie
    setCookieAgendamentos(COOKIE_ALERTA_AGENDAMENTOS_MINIMIZADO, 'true');
    
    const container = document.getElementById('alertas-agendamentos-container');
    if (container) {
        container.style.display = 'none';
    }
    
    // Mostrar botão minimizado
    const btnMinimizado = document.getElementById('alerta-agendamentos-minimizado-btn');
    if (btnMinimizado) {
        btnMinimizado.style.display = 'flex';
    }
}

// Função para restaurar alerta
function restaurarAlertaAgendamentos() {
    alertaAgendamentosMinimizado = false;
    
    // Remover cookie
    deleteCookieAgendamentos(COOKIE_ALERTA_AGENDAMENTOS_MINIMIZADO);
    
    const container = document.getElementById('alertas-agendamentos-container');
    if (container) {
        container.style.display = 'flex';
    }
    
    // Esconder botão minimizado
    const btnMinimizado = document.getElementById('alerta-agendamentos-minimizado-btn');
    if (btnMinimizado) {
        btnMinimizado.style.display = 'none';
    }
}

// Função para criar botão minimizado
function criarBotaoMinimizadoAgendamentos() {
    let btnMinimizado = document.getElementById('alerta-agendamentos-minimizado-btn');
    
    if (!btnMinimizado) {
        btnMinimizado = document.createElement('div');
        btnMinimizado.id = 'alerta-agendamentos-minimizado-btn';
        btnMinimizado.className = 'alerta-minimizado-btn-agendamentos';
        btnMinimizado.onclick = restaurarAlertaAgendamentos;
        document.body.appendChild(btnMinimizado);
    }
    
    // Atualizar contador no botão minimizado
    const contador = document.getElementById('alertas-agendamentos-contador');
    let contadorMinimizado = btnMinimizado.querySelector('.alerta-minimizado-contador-agendamentos');
    
    if (contador) {
        if (!contadorMinimizado) {
            // Criar elemento de contador se não existir
            btnMinimizado.innerHTML = '📅';
            contadorMinimizado = document.createElement('span');
            contadorMinimizado.className = 'alerta-minimizado-contador-agendamentos';
            btnMinimizado.appendChild(contadorMinimizado);
        }
        contadorMinimizado.textContent = contador.textContent;
    }
    
    // Mostrar ou esconder baseado no estado
    if (alertaAgendamentosMinimizado && agendamentosAlertas.length > 0) {
        btnMinimizado.style.display = 'flex';
    } else {
        btnMinimizado.style.display = 'none';
    }
}

// Função principal para carregar e exibir alertas
async function carregarAlertasAgendamentos() {
    const agendamentos = await buscarAgendamentosProximos();
    renderizarAlertasAgendamentos(agendamentos);
    
    // Aplicar estado minimizado se estiver salvo no cookie
    const cookieMinimizado = getCookieAgendamentos(COOKIE_ALERTA_AGENDAMENTOS_MINIMIZADO);
    if (cookieMinimizado === 'true' && agendamentos.length > 0) {
        alertaAgendamentosMinimizado = true;
        const container = document.getElementById('alertas-agendamentos-container');
        if (container) {
            container.style.display = 'none';
        }
        criarBotaoMinimizadoAgendamentos();
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(carregarAlertasAgendamentos, 500);
        // Atualizar a cada 5 minutos
        setInterval(carregarAlertasAgendamentos, 5 * 60 * 1000);
    });
} else {
    setTimeout(carregarAlertasAgendamentos, 500);
    // Atualizar a cada 5 minutos
    setInterval(carregarAlertasAgendamentos, 5 * 60 * 1000);
}

// Exportar funções para uso global
window.irParaAgendamento = irParaAgendamento;
window.navegarAlertaAgendamentos = navegarAlertaAgendamentos;
window.minimizarAlertaAgendamentos = minimizarAlertaAgendamentos;
window.restaurarAlertaAgendamentos = restaurarAlertaAgendamentos;
window.carregarAlertasAgendamentos = carregarAlertasAgendamentos;
// Exportar variável para limpeza de cache
window.agendamentosAlertas = agendamentosAlertas;