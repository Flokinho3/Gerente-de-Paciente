// Funções utilitárias

// Formatação de dados
function formatarData(dataString) {
    if (!dataString) return 'Não informado';
    
    try {
        const [ano, mes, dia] = dataString.split('-');
        return `${dia}/${mes}/${ano}`;
    } catch (e) {
        return dataString;
    }
}

function formatarHora(horaString) {
    if (!horaString) return 'Não informado';
    
    try {
        const [hora, minuto] = horaString.split(':');
        return `${hora}:${minuto}`;
    } catch (e) {
        return horaString;
    }
}

function formatarDataSimples(dataString) {
    if (!dataString) return null;

    try {
        const [ano, mes, dia] = dataString.split('-');
        return `${dia}/${mes}/${ano}`;
    } catch (e) {
        return dataString;
    }
}

function formatarBoolean(valor) {
    if (valor === true) {
        return 'Sim';
    } else if (valor === false) {
        return 'Não';
    }
    return 'Não informado';
}

function formatarStatus(status) {
    const statusMap = {
        'agendado': 'Agendado',
        'confirmado': 'Confirmado',
        'realizado': 'Realizado',
        'cancelado': 'Cancelado',
        'falta': 'Falta'
    };
    return statusMap[status] || status;
}

function formatarTipoConsulta(tipo) {
    if (!tipo) return '';
    
    const tipoMap = {
        'consulta_pre_natal': 'Consulta Pré-Natal',
        'retorno': 'Retorno',
        'avaliacao': 'Avaliação',
        'exame': 'Exame',
        'outro': 'Outro'
    };
    return tipoMap[tipo] || tipo;
}

// Mensagens
function mostrarMensagem(mensagem, isError = false) {
    const mensagemDiv = document.createElement('div');
    mensagemDiv.className = `message ${isError ? 'error' : 'success'}`;
    mensagemDiv.textContent = mensagem;
    mensagemDiv.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 3000;
        animation: slideInRight 0.3s ease;
    `;
    
    if (isError) {
        mensagemDiv.style.background = '#ffebee';
        mensagemDiv.style.color = '#c62828';
        mensagemDiv.style.border = '2px solid #c62828';
    } else {
        mensagemDiv.style.background = '#e8f5e9';
        mensagemDiv.style.color = '#388e3c';
        mensagemDiv.style.border = '2px solid #388e3c';
    }
    
    document.body.appendChild(mensagemDiv);
    
    setTimeout(() => {
        mensagemDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(mensagemDiv);
        }, 300);
    }, 3000);
}

function mostrarErro(mensagem) {
    mostrarMensagem(mensagem, true);
}

// Exportar funções
window.formatarData = formatarData;
window.formatarHora = formatarHora;
window.formatarDataSimples = formatarDataSimples;
window.formatarBoolean = formatarBoolean;
window.formatarStatus = formatarStatus;
window.formatarTipoConsulta = formatarTipoConsulta;
window.mostrarMensagem = mostrarMensagem;
window.mostrarErro = mostrarErro;
