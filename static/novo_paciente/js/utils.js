import { messageDiv } from './dom.js';

// Função para mostrar mensagem
export function showMessage(text, isError = false) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${isError ? 'error' : 'success'}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Função para calcular DPP a partir do DUM usando a Regra de Naegele
// Regra de Naegele: DPP = DUM + 7 dias - 3 meses
export function calcularDPP(dum) {
    if (!dum) return null;
    
    // Criar objeto Date a partir da string DUM (formato YYYY-MM-DD)
    const dataDUM = new Date(dum + 'T00:00:00');
    
    // Verificar se a data é válida
    if (isNaN(dataDUM.getTime())) {
        return null;
    }
    
    // Aplicar Regra de Naegele: +7 dias, -3 meses
    const dataDPP = new Date(dataDUM);
    
    // Adicionar 7 dias
    dataDPP.setDate(dataDPP.getDate() + 7);
    
    // Subtrair 3 meses
    dataDPP.setMonth(dataDPP.getMonth() - 3);
    
    // Formatar para YYYY-MM-DD (formato esperado pelo input type="date")
    const ano = dataDPP.getFullYear();
    const mes = String(dataDPP.getMonth() + 1).padStart(2, '0');
    const dia = String(dataDPP.getDate()).padStart(2, '0');
    
    return `${ano}-${mes}-${dia}`;
}
