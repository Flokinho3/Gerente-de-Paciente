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
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:118',message:'initializeCalculatorDPP chamada',data:{readyState:document.readyState},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const calculatorIcon = document.getElementById('dum-calculator-icon');
    const tooltip = document.getElementById('dum-calculator-tooltip');
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:121',message:'Elementos encontrados',data:{iconFound:!!calculatorIcon,tooltipFound:!!tooltip,iconId:calculatorIcon?.id,tooltipId:tooltip?.id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    
    if (calculatorIcon && tooltip) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:125',message:'Anexando event listener ao ícone',data:{iconDisplay:tooltip.style.display},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
        calculatorIcon.addEventListener('click', function(e) {
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:127',message:'Clique no ícone capturado',data:{targetId:e.target.id,currentDisplay:tooltip.style.display},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            e.stopPropagation();
            const isVisible = tooltip.style.display === 'block';
            tooltip.style.display = isVisible ? 'none' : 'block';
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:130',message:'Tooltip display alterado',data:{isVisible,newDisplay:tooltip.style.display,computedDisplay:window.getComputedStyle(tooltip).display},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
            // #endregion
        });
        
        // Fechar tooltip ao clicar fora
        document.addEventListener('click', function(e) {
            // Buscar elementos dinamicamente para garantir referências atualizadas
            const currentIcon = document.getElementById('dum-calculator-icon');
            const currentTooltip = document.getElementById('dum-calculator-tooltip');
            
            if (!currentIcon || !currentTooltip) return;
            
            const isOutside = !currentIcon.contains(e.target) && !currentTooltip.contains(e.target);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:135',message:'Listener clicar fora executado',data:{isOutside,targetId:e.target.id,tooltipDisplay:currentTooltip.style.display,iconContains:currentIcon.contains(e.target),tooltipContains:currentTooltip.contains(e.target)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
            // #endregion
            if (isOutside) {
                currentTooltip.style.display = 'none';
                // #region agent log
                fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:138',message:'Tooltip fechado por clique fora',data:{finalDisplay:currentTooltip.style.display},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
                // #endregion
            }
        });
    } else {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:142',message:'Elementos não encontrados - listener não anexado',data:{iconFound:!!calculatorIcon,tooltipFound:!!tooltip},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
    }
}

// Inicializar calculadora quando o DOM estiver pronto
if (document.readyState === 'loading') {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:148',message:'DOM ainda carregando - aguardando DOMContentLoaded',data:{readyState:document.readyState},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    document.addEventListener('DOMContentLoaded', initializeCalculatorDPP);
} else {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/606c4a8c-c1a2-4ff2-a7bc-5c4d58af8b63',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:152',message:'DOM já pronto - usando setTimeout',data:{readyState:document.readyState},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    // DOM já está pronto
    setTimeout(initializeCalculatorDPP, 100);
}

// Inicializar submit do formulário
initializeFormSubmit();
