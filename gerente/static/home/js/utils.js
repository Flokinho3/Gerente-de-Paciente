// Funções utilitárias do Home

// Função para determinar a cor do indicador baseado na porcentagem
function getStatusIndicator(percentage) {
    if (percentage >= 70) {
        return '🟢'; // Verde: >= 70%
    } else if (percentage >= 30) {
        return '🟡'; // Amarelo: entre 30% e 70%
    } else {
        return '🔴'; // Vermelho: < 30%
    }
}

// Função para calcular porcentagem do valor positivo
function calculatePositivePercentage(sim, nao) {
    const total = sim + nao;
    if (total === 0) return 0;
    return (sim / total) * 100;
}

// Função para calcular porcentagem do valor positivo (com 3 categorias)
function calculatePositivePercentage3(positivo, negativo, neutro) {
    const total = positivo + negativo + neutro;
    if (total === 0) return 0;
    return (positivo / total) * 100;
}

// Função para sanitizar nome da unidade para ID
function sanitizarId(texto) {
    return texto
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}

// Exportar funções
window.getStatusIndicator = getStatusIndicator;
window.calculatePositivePercentage = calculatePositivePercentage;
window.calculatePositivePercentage3 = calculatePositivePercentage3;
window.sanitizarId = sanitizarId;
