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

/**
 * Calcula a idade gestacional com base na DUM
 * @param {string} dum - Data da Última Menstruação (formato YYYY-MM-DD)
 * @returns {Object|null} Objeto com semanas, dias e texto formatado, ou null se data inválida
 */
export function calcularIdadeGestacional(dum) {
    if (!dum) return null;
    
    // Criar objeto Date a partir da string DUM (formato YYYY-MM-DD)
    const dataDUM = new Date(dum + 'T00:00:00');
    const dataAtual = new Date();
    
    // Verificar se a data é válida
    if (isNaN(dataDUM.getTime())) {
        return null;
    }
    
    // Calcular diferença em dias
    const diffTime = dataAtual - dataDUM;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    // Verificar se a DUM é no futuro
    if (diffDays < 0) {
        return {
            semanas: 0,
            dias: 0,
            totalDias: 0,
            texto: "Data no futuro - verifique a DUM informada",
            valido: false
        };
    }
    
    // Calcular semanas e dias restantes
    const semanas = Math.floor(diffDays / 7);
    const dias = diffDays % 7;
    
    // Criar texto formatado
    let texto = "";
    if (semanas === 0 && dias === 0) {
        texto = "Gestação iniciada hoje";
    } else if (semanas === 0) {
        texto = `${dias} ${dias === 1 ? 'dia' : 'dias'} de gestação`;
    } else if (dias === 0) {
        texto = `${semanas} ${semanas === 1 ? 'semana' : 'semanas'} de gestação`;
    } else {
        texto = `${semanas} ${semanas === 1 ? 'semana' : 'semanas'} e ${dias} ${dias === 1 ? 'dia' : 'dias'} de gestação`;
    }
    
    return {
        semanas: semanas,
        dias: dias,
        totalDias: diffDays,
        texto: texto,
        valido: true
    };
}

/**
 * Atualiza a exibição da idade gestacional na interface
 * @param {string} dum - Data da Última Menstruação (formato YYYY-MM-DD)
 */
export function atualizarIdadeGestacional(dum) {
    const resultadoDiv = document.getElementById('resultadoIdadeGestacional');
    const textoDiv = document.getElementById('textoIdadeGestacional');
    
    if (!resultadoDiv || !textoDiv) return;
    
    const idadeGestacional = calcularIdadeGestacional(dum);
    
    if (!idadeGestacional) {
        resultadoDiv.style.display = 'none';
        return;
    }
    
    textoDiv.textContent = idadeGestacional.texto;
    
    // Ajustar cor baseado na validade
    if (idadeGestacional.valido) {
        resultadoDiv.style.background = 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)';
        resultadoDiv.style.borderLeft = '4px solid #4caf50';
        textoDiv.style.color = '#1b5e20';
    } else {
        resultadoDiv.style.background = 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)';
        resultadoDiv.style.borderLeft = '4px solid #ff9800';
        textoDiv.style.color = '#e65100';
    }
    
    resultadoDiv.style.display = 'block';
}
