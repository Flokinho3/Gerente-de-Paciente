import { totalSteps } from './config.js';
import { progressFill, currentStepSpan, btnAnterior, btnProximo, btnSalvar, getCurrentStep, setCurrentStep } from './dom.js';
import { validateCurrentStep, toggleRequiredAttributes } from './validation.js';
import { toggleCampoInicioPreNatalDetalhes, toggleCampoEstratificacaoProblema, toggleCampoKitTipo, verificarKitsSelecionados } from './conditionalFields.js';

// Função para atualizar progresso
export function updateProgress() {
    const currentStep = getCurrentStep();
    const percentage = (currentStep / totalSteps) * 100;
    progressFill.style.width = `${percentage}%`;
    currentStepSpan.textContent = currentStep;
    
    // Mostrar/esconder botões
    btnAnterior.style.display = currentStep > 1 ? 'inline-block' : 'none';
    btnProximo.style.display = currentStep < totalSteps ? 'inline-block' : 'none';
    btnSalvar.style.display = currentStep === totalSteps ? 'inline-block' : 'none';
    
    // Validar e habilitar botão próximo
    if (currentStep < totalSteps) {
        const isValid = validateCurrentStep();
        btnProximo.disabled = !isValid;
    }
}

// Função para mostrar step
export function showStep(step) {
    // Esconder todos os steps
    document.querySelectorAll('.wizard-step').forEach(s => {
        s.classList.remove('active');
    });
    
    // Mostrar step atual
    const stepElement = document.querySelector(`.wizard-step[data-step="${step}"]`);
    if (stepElement) {
        stepElement.classList.add('active');
        
        // Gerenciar atributos required
        toggleRequiredAttributes(step);
        
        // Verificar estado dos campos de início do pré-natal se estiver no step 3
        if (step === 3) {
            // Configurar event listeners diretamente nos radio buttons do step 3
            setTimeout(() => {
                const radiosInicioPreNatal = stepElement.querySelectorAll('input[name="inicio_pre_natal_antes_12s"]');
                
                // Criar uma função wrapper para garantir que funcione
                const handleInicioPreNatalChange = function() {
                    setTimeout(() => {
                        toggleCampoInicioPreNatalDetalhes();
                    }, 50);
                };
                
                radiosInicioPreNatal.forEach(radio => {
                    // Remover listeners anteriores usando a função wrapper
                    radio.removeEventListener('change', handleInicioPreNatalChange);
                    // Adicionar novo listener
                    radio.addEventListener('change', handleInicioPreNatalChange, true);
                    
                    // Também adicionar listener de click como fallback
                    radio.addEventListener('click', function() {
                        setTimeout(() => {
                            toggleCampoInicioPreNatalDetalhes();
                        }, 100);
                    }, true);
                });
                
                // Verificar estado atual e mostrar/esconder campos conforme necessário
                toggleCampoInicioPreNatalDetalhes();
            }, 300);
        }
        
        // Verificar estado do campo de estratificação se estiver no step 9
        if (step === 9) {
            // Configurar event listeners diretamente nos radio buttons do step 9
            setTimeout(() => {
                const radiosEstratificacao = stepElement.querySelectorAll('input[name="estratificacao"]');
                
                // Criar uma função wrapper para garantir que funcione
                const handleEstratificacaoChange = function() {
                    setTimeout(() => {
                        toggleCampoEstratificacaoProblema();
                    }, 50);
                };
                
                radiosEstratificacao.forEach(radio => {
                    // Remover listeners anteriores usando a função wrapper
                    radio.removeEventListener('change', handleEstratificacaoChange);
                    // Adicionar novo listener
                    radio.addEventListener('change', handleEstratificacaoChange, true);
                    
                    // Também adicionar listener de click como fallback
                    radio.addEventListener('click', function() {
                        setTimeout(() => {
                            toggleCampoEstratificacaoProblema();
                        }, 100);
                    }, true);
                });
                
                // Verificar estado atual e mostrar/esconder campo conforme necessário
                toggleCampoEstratificacaoProblema();
            }, 300);
        }
        
        // Verificar estado do campo de KIT se estiver no step 13
        if (step === 13) {
            // Configurar event listeners diretamente nos radio buttons do step 13
            setTimeout(() => {
                const radiosKit = stepElement.querySelectorAll('input[name="ganhou_kit"]');
                
                // Criar uma função wrapper para garantir que funcione
                const handleKitChange = function() {
                    setTimeout(() => {
                        toggleCampoKitTipo();
                    }, 50);
                };
                
                radiosKit.forEach(radio => {
                    // Remover listeners anteriores usando a função wrapper
                    radio.removeEventListener('change', handleKitChange);
                    // Adicionar novo listener
                    radio.addEventListener('change', handleKitChange, true);
                    
                    // Também adicionar listener de click como fallback
                    radio.addEventListener('click', function() {
                        setTimeout(() => {
                            toggleCampoKitTipo();
                        }, 100);
                    }, true);
                });
                
                // Verificar estado atual e mostrar/esconder campo conforme necessário
                toggleCampoKitTipo();
                
                // Adicionar event listeners nos checkboxes de tipo de KIT
                const kitTipoCheckboxes = stepElement.querySelectorAll('input[name="kit_tipo"]');
                kitTipoCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', function() {
                        setTimeout(() => {
                            verificarKitsSelecionados();
                            updateProgress();
                        }, 50);
                    });
                });
            }, 300);
        }
        
        // Inicializar calculadora DPP se estiver no step 11
        if (step === 11) {
            setTimeout(() => {
                const calculatorIcon = stepElement.querySelector('#dum-calculator-icon');
                const tooltip = stepElement.querySelector('#dum-calculator-tooltip');
                if (calculatorIcon && tooltip) {
                    const handleCalculatorClick = function(e) {
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        const isVisible = tooltip.style.display === 'block' || window.getComputedStyle(tooltip).display === 'block';
                        tooltip.style.display = isVisible ? 'none' : 'block';
                    };
                    calculatorIcon.addEventListener('click', handleCalculatorClick, true);
                }
            }, 300);
        }
        
        // Scroll suave para o topo do container
        document.querySelector('.container').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Função para ir para próximo step
export function nextStep() {
    const currentStep = getCurrentStep();
    if (currentStep < totalSteps && validateCurrentStep()) {
        setCurrentStep(currentStep + 1);
        showStep(getCurrentStep());
        updateProgress();
        
        // Focar no primeiro campo do próximo step
        const stepElement = document.querySelector(`.wizard-step[data-step="${getCurrentStep()}"]`);
        const firstInput = stepElement.querySelector('input, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }
}

// Função para ir para step anterior
export function previousStep() {
    const currentStep = getCurrentStep();
    if (currentStep > 1) {
        setCurrentStep(currentStep - 1);
        showStep(getCurrentStep());
        updateProgress();
        
        // Focar no primeiro campo do step anterior
        const stepElement = document.querySelector(`.wizard-step[data-step="${getCurrentStep()}"]`);
        const firstInput = stepElement.querySelector('input, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }
}
