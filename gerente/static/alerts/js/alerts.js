// Sistema de Alertas de Parto Próximo
// Alerta pacientes com DPP em 20 dias ou menos

// Armazenar alertas desativados no localStorage
const ALERTAS_DESATIVADOS_KEY = 'alertas_partos_desativados';

// Função para obter alertas desativados
function getAlertasDesativados() {
    const desativados = localStorage.getItem(ALERTAS_DESATIVADOS_KEY);
    return desativados ? JSON.parse(desativados) : [];
}

// Função para salvar alertas desativados
function salvarAlertasDesativados(ids) {
    localStorage.setItem(ALERTAS_DESATIVADOS_KEY, JSON.stringify(ids));
}

// Função para desativar alerta de um paciente
function desativarAlerta(pacienteId) {
    const desativados = getAlertasDesativados();
    if (!desativados.includes(pacienteId)) {
        desativados.push(pacienteId);
        salvarAlertasDesativados(desativados);
    }
}

// Função para reativar alerta de um paciente
function reativarAlerta(pacienteId) {
    const desativados = getAlertasDesativados();
    const index = desativados.indexOf(pacienteId);
    if (index > -1) {
        desativados.splice(index, 1);
        salvarAlertasDesativados(desativados);
    }
}

// Função para verificar se alerta está desativado
function isAlertaDesativado(pacienteId) {
    const desativados = getAlertasDesativados();
    return desativados.includes(pacienteId);
}

// Função para calcular dias até o DPP
function calcularDiasAteDPP(dpp) {
    if (!dpp) return null;
    
    try {
        // Formato esperado: YYYY-MM-DD
        const dataDPP = new Date(dpp + 'T00:00:00');
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        
        const diffTime = dataDPP - hoje;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        return diffDays;
    } catch (e) {
        console.error('Erro ao calcular dias até DPP:', e);
        return null;
    }
}

// Função para buscar pacientes próximos do parto
async function buscarPacientesProximosParto() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();
        
        if (!data.success || !data.pacientes) {
            return [];
        }
        
        const alertasDesativados = getAlertasDesativados();
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        
        const pacientesProximos = data.pacientes
            .filter(paciente => {
                // Verificar se alerta está desativado
                if (isAlertaDesativado(paciente.id)) {
                    return false;
                }
                
                const dpp = paciente.avaliacao?.dpp;
                if (!dpp) return false;
                
                const diasAteDPP = calcularDiasAteDPP(dpp);
                
                // Retornar apenas pacientes com 20 dias ou menos até o parto (apenas antes da data passar)
                return diasAteDPP !== null && diasAteDPP <= 20 && diasAteDPP >= 0;
            })
            .map(paciente => {
                const diasAteDPP = calcularDiasAteDPP(paciente.avaliacao.dpp);
                return {
                    ...paciente,
                    diasAteDPP: diasAteDPP
                };
            })
            .sort((a, b) => a.diasAteDPP - b.diasAteDPP); // Ordenar por dias restantes (menor primeiro)
        
        return pacientesProximos;
    } catch (error) {
        console.error('Erro ao buscar pacientes próximos do parto:', error);
        return [];
    }
}

// Função para formatar mensagem de dias
function formatarMensagemDias(dias) {
    if (dias < 0) {
        return `Parto previsto há ${Math.abs(dias)} dia(s)`;
    } else if (dias === 0) {
        return 'Parto previsto para hoje!';
    } else if (dias === 1) {
        return 'Parto previsto para amanhã!';
    } else {
        return `Parto previsto em ${dias} dias`;
    }
}

// Variável para controlar o índice do alerta atual
let indiceAlertaAtual = 0;
let pacientesAlertas = [];
let alertaMinimizado = false;

// Nome do cookie para salvar estado de minimização
const COOKIE_ALERTA_MINIMIZADO = 'alerta_parto_minimizado';

// Funções para gerenciar cookies
function setCookie(nome, valor, dias = 365) {
    const data = new Date();
    data.setTime(data.getTime() + (dias * 24 * 60 * 60 * 1000));
    const expires = `expires=${data.toUTCString()}`;
    document.cookie = `${nome}=${valor};${expires};path=/`;
}

function getCookie(nome) {
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

function deleteCookie(nome) {
    document.cookie = `${nome}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

// Função para renderizar alertas
function renderizarAlertas(pacientes) {
    const container = document.getElementById('alertas-parto-container');
    if (!container) return;
    
    // Salvar lista de pacientes
    pacientesAlertas = pacientes;
    indiceAlertaAtual = 0;
    
    // Atualizar contador
    const contador = document.getElementById('alertas-contador');
    if (contador) {
        contador.textContent = pacientes.length;
    }
    
    if (pacientes.length === 0) {
        container.style.display = 'none';
        // Esconder botão minimizado se não houver alertas
        const btnMinimizado = document.getElementById('alerta-minimizado-btn');
        if (btnMinimizado) {
            btnMinimizado.style.display = 'none';
        }
        return;
    }
    
    // Verificar cookie para estado de minimização
    const cookieMinimizado = getCookie(COOKIE_ALERTA_MINIMIZADO);
    if (cookieMinimizado === 'true') {
        alertaMinimizado = true;
    }
    
    // Se não estiver minimizado, mostrar container
    if (!alertaMinimizado) {
        container.style.display = 'flex';
    } else {
        container.style.display = 'none';
    }
    
    // Adicionar botão de minimizar no header se não existir
    const header = container.querySelector('.alertas-header');
    if (header) {
        let btnMinimizar = header.querySelector('.btn-minimizar-alerta');
        if (!btnMinimizar) {
            btnMinimizar = document.createElement('button');
            btnMinimizar.className = 'btn-minimizar-alerta';
            btnMinimizar.innerHTML = '−';
            btnMinimizar.title = 'Minimizar alertas';
            btnMinimizar.onclick = minimizarAlerta;
            header.appendChild(btnMinimizar);
        }
    }
    
    // Criar ou atualizar botão minimizado
    criarBotaoMinimizado();
    
    const alertasList = document.getElementById('alertas-parto-list');
    if (!alertasList) return;
    
    // Renderizar todos os alertas, mas mostrar apenas um por vez
    alertasList.innerHTML = pacientes.map((paciente, index) => {
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        const dpp = paciente.avaliacao?.dpp || '';
        const diasAteDPP = paciente.diasAteDPP;
        const dataFormatada = formatarDataDPP(dpp);
        const mensagemDias = formatarMensagemDias(diasAteDPP);
        const isUrgente = diasAteDPP <= 7;
        
        return `
            <div class="alerta-item ${isUrgente ? 'alerta-urgente' : ''} ${index === 0 ? 'alerta-ativo' : ''}" 
                 data-paciente-id="${paciente.id}" 
                 data-index="${index}"
                 style="display: ${index === 0 ? 'block' : 'none'};">
                <div class="alerta-info">
                    <div class="alerta-nome">${nome}</div>
                    <div class="alerta-detalhes">
                        <span class="alerta-dias ${isUrgente ? 'dias-urgente' : ''}">${mensagemDias}</span>
                        <span class="alerta-data">DPP: ${dataFormatada}</span>
                    </div>
                </div>
                <div class="alerta-actions">
                    <button class="btn-alerta-ver" onclick="irParaPerfilPaciente('${paciente.id}')">
                        Ver Perfil
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Adicionar controles de navegação se houver mais de um alerta
    if (pacientes.length > 1) {
        const controlesHTML = `
            <div class="alerta-navegacao">
                <button class="btn-nav-alerta" onclick="navegarAlerta(-1)" id="btnAnteriorAlerta" ${indiceAlertaAtual === 0 ? 'disabled' : ''}>
                    ← Anterior
                </button>
                <span class="alerta-indicador">${indiceAlertaAtual + 1} / ${pacientes.length}</span>
                <button class="btn-nav-alerta" onclick="navegarAlerta(1)" id="btnProximoAlerta" ${indiceAlertaAtual === pacientes.length - 1 ? 'disabled' : ''}>
                    Próximo →
                </button>
            </div>
        `;
        
        // Verificar se já existe navegação, se não, adicionar
        let navegacao = alertasList.querySelector('.alerta-navegacao');
        if (!navegacao) {
            alertasList.insertAdjacentHTML('beforeend', controlesHTML);
        } else {
            navegacao.outerHTML = controlesHTML;
        }
    } else {
        // Remover navegação se houver apenas um alerta
        const navegacao = alertasList.querySelector('.alerta-navegacao');
        if (navegacao) {
            navegacao.remove();
        }
    }
}

// Função para navegar entre alertas
function navegarAlerta(direcao) {
    if (pacientesAlertas.length === 0) return;
    
    const novoIndice = indiceAlertaAtual + direcao;
    
    if (novoIndice < 0 || novoIndice >= pacientesAlertas.length) return;
    
    const alertasList = document.getElementById('alertas-parto-list');
    if (!alertasList) return;
    
    // Esconder alerta atual
    const alertaAtual = alertasList.querySelector(`.alerta-item[data-index="${indiceAlertaAtual}"]`);
    if (alertaAtual) {
        alertaAtual.style.display = 'none';
        alertaAtual.classList.remove('alerta-ativo');
    }
    
    // Atualizar índice
    indiceAlertaAtual = novoIndice;
    
    // Mostrar novo alerta
    const novoAlerta = alertasList.querySelector(`.alerta-item[data-index="${indiceAlertaAtual}"]`);
    if (novoAlerta) {
        novoAlerta.style.display = 'block';
        novoAlerta.classList.add('alerta-ativo');
        
        // Scroll suave até o alerta
        novoAlerta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Atualizar botões de navegação
    const btnAnterior = document.getElementById('btnAnteriorAlerta');
    const btnProximo = document.getElementById('btnProximoAlerta');
    const indicador = alertasList.querySelector('.alerta-indicador');
    
    if (btnAnterior) {
        btnAnterior.disabled = indiceAlertaAtual === 0;
    }
    if (btnProximo) {
        btnProximo.disabled = indiceAlertaAtual === pacientesAlertas.length - 1;
    }
    if (indicador) {
        indicador.textContent = `${indiceAlertaAtual + 1} / ${pacientesAlertas.length}`;
    }
}

// Função para formatar data DPP
function formatarDataDPP(dpp) {
    if (!dpp) return 'Não informado';
    
    try {
        const [ano, mes, dia] = dpp.split('-');
        if (ano && mes && dia) {
            return `${dia}/${mes}/${ano}`;
        }
        return dpp;
    } catch (e) {
        return dpp;
    }
}

// Função para ir ao perfil do paciente
function irParaPerfilPaciente(pacienteId) {
    // Verificar se estamos na página de pacientes
    if (window.location.pathname === '/pacientes' || window.location.pathname === '/pacientes/') {
        // Se já estamos na página de pacientes, apenas selecionar o paciente
        if (typeof window.selecionarPaciente === 'function') {
            window.selecionarPaciente(pacienteId);
            // Scroll até o perfil
            setTimeout(() => {
                const perfil = document.getElementById('pacientePerfil');
                if (perfil) {
                    perfil.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 300);
        } else {
            // Aguardar o script carregar
            setTimeout(() => {
                if (typeof window.selecionarPaciente === 'function') {
                    window.selecionarPaciente(pacienteId);
                } else {
                    window.location.href = `/pacientes?paciente=${pacienteId}`;
                }
            }, 500);
        }
    } else {
        // Navegar para a página de pacientes com o ID
        window.location.href = `/pacientes?paciente=${pacienteId}`;
    }
}

// Função para toggle do alerta (chamada do perfil)
function toggleAlertaPaciente(pacienteId, ativo) {
    if (ativo) {
        reativarAlerta(pacienteId);
    } else {
        desativarAlerta(pacienteId);
    }
    // Recarregar alertas para atualizar a lista
    carregarAlertas();
}

// Função para verificar se paciente tem alerta ativo
function pacienteTemAlertaAtivo(paciente) {
    if (!paciente || !paciente.avaliacao || !paciente.avaliacao.dpp) {
        return false;
    }
    
    // Verificar se alerta está desativado
    if (isAlertaDesativado(paciente.id)) {
        return false;
    }
    
    const diasAteDPP = calcularDiasAteDPP(paciente.avaliacao.dpp);
    
    // Retornar true se tiver 20 dias ou menos até o parto (apenas antes da data passar)
    return diasAteDPP !== null && diasAteDPP <= 20 && diasAteDPP >= 0;
}

// Função principal para carregar e exibir alertas
async function carregarAlertas() {
    const pacientes = await buscarPacientesProximosParto();
    renderizarAlertas(pacientes);
    
    // Aplicar estado minimizado se estiver salvo no cookie
    const cookieMinimizado = getCookie(COOKIE_ALERTA_MINIMIZADO);
    if (cookieMinimizado === 'true' && pacientes.length > 0) {
        alertaMinimizado = true;
        const container = document.getElementById('alertas-parto-container');
        if (container) {
            container.style.display = 'none';
        }
        criarBotaoMinimizado();
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(carregarAlertas, 500);
        // Atualizar a cada 5 minutos
        setInterval(carregarAlertas, 5 * 60 * 1000);
    });
} else {
    setTimeout(carregarAlertas, 500);
    // Atualizar a cada 5 minutos
    setInterval(carregarAlertas, 5 * 60 * 1000);
}

// Função para minimizar alerta
function minimizarAlerta() {
    alertaMinimizado = true;
    
    // Salvar estado no cookie
    setCookie(COOKIE_ALERTA_MINIMIZADO, 'true');
    
    const container = document.getElementById('alertas-parto-container');
    if (container) {
        container.style.display = 'none';
    }
    
    // Mostrar botão minimizado
    const btnMinimizado = document.getElementById('alerta-minimizado-btn');
    if (btnMinimizado) {
        btnMinimizado.style.display = 'flex';
    }
}

// Função para restaurar alerta
function restaurarAlerta() {
    alertaMinimizado = false;
    
    // Remover cookie (ou salvar como false)
    deleteCookie(COOKIE_ALERTA_MINIMIZADO);
    
    const container = document.getElementById('alertas-parto-container');
    if (container) {
        container.style.display = 'flex';
    }
    
    // Esconder botão minimizado
    const btnMinimizado = document.getElementById('alerta-minimizado-btn');
    if (btnMinimizado) {
        btnMinimizado.style.display = 'none';
    }
}

// Função para criar botão minimizado
function criarBotaoMinimizado() {
    let btnMinimizado = document.getElementById('alerta-minimizado-btn');
    
    if (!btnMinimizado) {
        btnMinimizado = document.createElement('div');
        btnMinimizado.id = 'alerta-minimizado-btn';
        btnMinimizado.className = 'alerta-minimizado-btn';
        btnMinimizado.onclick = restaurarAlerta;
        document.body.appendChild(btnMinimizado);
    }
    
    // Atualizar contador no botão minimizado
    const contador = document.getElementById('alertas-contador');
    let contadorMinimizado = btnMinimizado.querySelector('.alerta-minimizado-contador');
    
    if (contador) {
        if (!contadorMinimizado) {
            // Criar elemento de contador se não existir
            btnMinimizado.innerHTML = '🚨';
            contadorMinimizado = document.createElement('span');
            contadorMinimizado.className = 'alerta-minimizado-contador';
            btnMinimizado.appendChild(contadorMinimizado);
        }
        contadorMinimizado.textContent = contador.textContent;
    }
    
    // Mostrar ou esconder baseado no estado
    if (alertaMinimizado && pacientesAlertas.length > 0) {
        btnMinimizado.style.display = 'flex';
    } else {
        btnMinimizado.style.display = 'none';
    }
}

// Exportar funções para uso global
window.irParaPerfilPaciente = irParaPerfilPaciente;
window.toggleAlertaPaciente = toggleAlertaPaciente;
window.pacienteTemAlertaAtivo = pacienteTemAlertaAtivo;
window.isAlertaDesativado = isAlertaDesativado;
window.calcularDiasAteDPP = calcularDiasAteDPP;
window.navegarAlerta = navegarAlerta;
window.minimizarAlerta = minimizarAlerta;
window.restaurarAlerta = restaurarAlerta;