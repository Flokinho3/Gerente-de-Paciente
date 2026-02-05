/**
 * Funções auxiliares para página de Conflitos
 * As principais funcionalidades do Firebase estão no HTML inline
 * Este arquivo mantém compatibilidade com funções legadas
 */

// Função auxiliar para mostrar mensagens de status
function mostrarMensagem(mensagem, tipo = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    if (statusDiv) {
        statusDiv.textContent = mensagem;
        statusDiv.className = `status-message status-${tipo}`;
        statusDiv.style.display = 'block';

        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// Função para fechar modal de comparação
function fecharModalComparacao() {
    const modal = document.getElementById('comparacaoModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Formatar data para exibição
function formatarData(dataStr) {
    if (!dataStr) return 'N/A';
    try {
        const data = new Date(dataStr);
        if (isNaN(data.getTime())) return 'N/A';
        return data.toLocaleString('pt-BR');
    } catch {
        return 'N/A';
    }
}

// Formatar hora
function formatarHora(horaStr) {
    if (!horaStr) return '';
    return horaStr;
}

// Formatar data e hora juntos
function formatarDataHora(dataHoraStr) {
    if (!dataHoraStr) return 'N/A';
    try {
        const data = new Date(dataHoraStr);
        if (isNaN(data.getTime())) return 'N/A';
        return data.toLocaleString('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return 'N/A';
    }
}

// Exportar funções para uso global
window.mostrarMensagem = mostrarMensagem;
window.fecharModalComparacao = fecharModalComparacao;
window.formatarData = formatarData;
window.formatarHora = formatarHora;
window.formatarDataHora = formatarDataHora;
