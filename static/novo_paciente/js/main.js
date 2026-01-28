// Importar módulos
import { totalSteps } from './config.js';
import { totalStepsSpan, initializeRequiredFields, form, btnProximo, btnAnterior, setCurrentStep, getCurrentStep } from './dom.js';
import { showStep, updateProgress, nextStep, previousStep } from './wizard.js';
import { toggleCampoInicioPreNatalDetalhes, toggleCampoEstratificacaoProblema, toggleCampoKitTipo, verificarKitsSelecionados, toggleCampoDataGanhou, toggleCampoGenerosFilhos, toggleCampoMetodoOutros } from './conditionalFields.js';
import { validateCurrentStep } from './validation.js';
import { initializeFormSubmit } from './formSubmit.js';
import { calcularDPP } from './utils.js';

// Inicializar
totalStepsSpan.textContent = totalSteps;
initializeRequiredFields();
setCurrentStep(1);
showStep(1);
updateProgress();

// Event listeners para inputs (validar em tempo real)
form.addEventListener('input', function(e) {
    // Verificar se o input pertence ao step atual
    const inputStep = e.target.closest('.wizard-step');
    const currentStepElement = document.querySelector('.wizard-step.active');
    
    // Calcular DPP automaticamente quando DUM for preenchido
    if (e.target.id === 'dum' && e.target.value) {
        const dppCalculado = calcularDPP(e.target.value);
        const dppInput = document.getElementById('dpp');
        if (dppInput && dppCalculado) {
            dppInput.value = dppCalculado;
            // Mostrar badge "Data Provável"
            mostrarBadgeDPP();
            // Disparar evento change para atualizar validação
            dppInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    
    // Mostrar/esconder campo de gêneros quando quantidade de filhos mudar
    if (e.target.id === 'quantidade_filhos') {
        setTimeout(() => {
            toggleCampoGenerosFilhos();
        }, 50);
    }
    
    // Mostrar/esconder campo "outros" quando método preventivo mudar
    if (e.target.id === 'metodo_preventivo') {
        setTimeout(() => {
            toggleCampoMetodoOutros();
        }, 50);
    }
    
    // Também considerar os campos condicionais que podem estar fora do step mas visíveis
    if (inputStep === currentStepElement || 
        e.target.id === 'estratificacao_problema' || 
        e.target.id === 'inicio_pre_natal_semanas' || 
        e.target.id === 'inicio_pre_natal_observacao' ||
        e.target.id === 'dum' ||
        e.target.id === 'dpp' ||
        e.target.id === 'data_ganhou_crianca' ||
        e.target.id === 'generos_filhos' ||
        e.target.id === 'metodo_preventivo_outros') {
        updateProgress();
    }
});

// Event listeners para radio buttons
form.addEventListener('change', function(e) {
    if (e.target.type === 'radio') {
        const inputStep = e.target.closest('.wizard-step');
        const currentStepElement = document.querySelector('.wizard-step.active');
        
        // Mostrar/esconder campos de início do pré-natal (sempre verificar, independente do step ativo)
        if (e.target.name === 'inicio_pre_natal_antes_12s') {
            // Usar setTimeout para garantir que o DOM esteja atualizado
            setTimeout(() => {
                toggleCampoInicioPreNatalDetalhes();
            }, 50);
        }
        
        // Mostrar/esconder campo de problema de estratificação (sempre verificar, independente do step ativo)
        if (e.target.name === 'estratificacao') {
            // Usar setTimeout para garantir que o DOM esteja atualizado
            setTimeout(() => {
                toggleCampoEstratificacaoProblema();
            }, 50);
        }
        
        // Mostrar/esconder campo de tipo de KIT (sempre verificar, independente do step ativo)
        if (e.target.name === 'ganhou_kit') {
            // Usar setTimeout para garantir que o DOM esteja atualizado
            setTimeout(() => {
                toggleCampoKitTipo();
            }, 50);
        }
        
        // Mostrar/esconder campo de data quando já ganhou a criança
        if (e.target.name === 'ja_ganhou_crianca') {
            setTimeout(() => {
                toggleCampoDataGanhou();
            }, 50);
        }
        
        // Verificar kits selecionados quando checkboxes de kit_tipo forem alterados
        if (e.target.name === 'kit_tipo' && e.target.type === 'checkbox') {
            setTimeout(() => {
                verificarKitsSelecionados();
                updateProgress();
            }, 50);
        }
        
        if (inputStep === currentStepElement) {
            updateProgress();
        }
    }
}, true); // Usar capture phase para garantir que seja capturado

// Event listeners para botões
btnProximo.addEventListener('click', nextStep);
btnAnterior.addEventListener('click', previousStep);

// Permitir avançar com Enter (apenas se válido)
form.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && getCurrentStep() < totalSteps) {
        e.preventDefault();
        if (validateCurrentStep()) {
            nextStep();
        }
    }
});

// Função para mostrar badge "Data Provável"
function mostrarBadgeDPP() {
    const badge = document.getElementById('dpp-badge');
    if (badge) {
        badge.style.display = 'block';
        // Remover após 3 segundos
        setTimeout(() => {
            badge.style.display = 'none';
        }, 3000);
    }
}

// Função para inicializar calculadora DPP
function initializeCalculatorDPP() {
    const calculatorIcon = document.getElementById('dum-calculator-icon');
    const tooltip = document.getElementById('dum-calculator-tooltip');

    if (calculatorIcon && tooltip) {
        calculatorIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = tooltip.style.display === 'block';
            tooltip.style.display = isVisible ? 'none' : 'block';
        });

        // Fechar tooltip ao clicar fora
        document.addEventListener('click', function(e) {
            const currentIcon = document.getElementById('dum-calculator-icon');
            const currentTooltip = document.getElementById('dum-calculator-tooltip');
            if (!currentIcon || !currentTooltip) return;
            const isOutside = !currentIcon.contains(e.target) && !currentTooltip.contains(e.target);
            if (isOutside) currentTooltip.style.display = 'none';
        });
    }
}

// Inicializar calculadora quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCalculatorDPP);
} else {
    setTimeout(initializeCalculatorDPP, 100);
}

// Inicializar submit do formulário
initializeFormSubmit();

// Carregar unidades para "Plano de parto entregue por qual unidade"
async function carregarUnidadesPlanoParto() {
    const sel = document.getElementById('plano_parto_entregue_por_unidade');
    if (!sel) return;
    try {
        const r = await fetch('/api/unidades_saude');
        const data = await r.json();
        if (!data.success || !Array.isArray(data.unidades)) return;
        const unidades = data.unidades.filter(Boolean);
        unidades.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u;
            opt.textContent = u;
            sel.appendChild(opt);
        });
    } catch (e) {
        console.warn('Erro ao carregar unidades para plano de parto:', e);
    }
}
carregarUnidadesPlanoParto();
