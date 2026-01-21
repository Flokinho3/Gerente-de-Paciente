import { getCurrentStep } from './dom.js';

// Função para validar campo do step atual
export function validateCurrentStep() {
    const currentStep = getCurrentStep();
    const currentStepElement = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return false;
    
    // Validar campos de início do pré-natal se necessário (verificação especial)
    if (currentStep === 3) {
        const inicioPreNatalRadio = currentStepElement.querySelector('input[name="inicio_pre_natal_antes_12s"]:checked');
        const semanasInput = document.getElementById('inicio_pre_natal_semanas');
        const detalhesGroup = document.getElementById('inicio-pre-natal-detalhes-group');
        
        if (inicioPreNatalRadio && inicioPreNatalRadio.value === 'true' && semanasInput && detalhesGroup) {
            // Verificar se o grupo está visível
            const isGroupVisible = detalhesGroup.style.display !== 'none' && 
                                  !detalhesGroup.style.display.includes('none') &&
                                  detalhesGroup.offsetParent !== null;
            
            if (isGroupVisible && semanasInput.hasAttribute('required')) {
                if (!semanasInput.value || semanasInput.value.trim() === '') {
                    return false;
                }
            }
        }
    }
    
    // Validar campo de tipo de KIT se necessário (verificação especial)
    if (currentStep === 13) {
        const ganhouKitRadio = currentStepElement.querySelector('input[name="ganhou_kit"]:checked');
        const kitTipoGroup = document.getElementById('kit-tipo-group');
        
        if (ganhouKitRadio && ganhouKitRadio.value === 'true' && kitTipoGroup) {
            // Verificar se o grupo está visível
            const isGroupVisible = kitTipoGroup.style.display !== 'none' && 
                                  !kitTipoGroup.style.display.includes('none') &&
                                  kitTipoGroup.offsetParent !== null;
            
            if (isGroupVisible) {
                const kitTipoChecked = kitTipoGroup.querySelectorAll('input[name="kit_tipo"]:checked');
                if (kitTipoChecked.length === 0) {
                    return false;
                }
            }
        }
    }
    
    // Validar inputs de texto e number
    const textInputs = currentStepElement.querySelectorAll('input[type="text"], input[type="number"], select, textarea');
    for (let input of textInputs) {
        // Pular validação dos campos condicionais (já validados acima)
        if (input.id === 'estratificacao_problema' || input.id === 'inicio_pre_natal_semanas') continue;
        
        // Verificar se o campo está visível antes de validar
        const isVisible = input.offsetParent !== null && 
                         !input.closest('[style*="display: none"]') &&
                         !input.closest('[style*="display:none"]');
        
        if (input.hasAttribute('required') && isVisible) {
            if (!input.value || input.value.trim() === '') {
                return false;
            }
        }
    }
    
    // Validar radio buttons
    const radioGroups = new Set();
    currentStepElement.querySelectorAll('input[type="radio"]').forEach(radio => {
        radioGroups.add(radio.name);
    });
    
    for (let radioName of radioGroups) {
        const radioGroup = currentStepElement.querySelectorAll(`input[type="radio"][name="${radioName}"]`);
        const hasRequired = Array.from(radioGroup).some(r => r.hasAttribute('required'));
        if (hasRequired) {
            const checked = currentStepElement.querySelector(`input[type="radio"][name="${radioName}"]:checked`);
            if (!checked) {
                return false;
            }
        }
    }
    
    return true;
}

// Função para gerenciar atributo required dinamicamente
export function toggleRequiredAttributes(step) {
    // Remover required de TODOS os campos
    document.querySelectorAll('input[required], select[required]').forEach(input => {
        input.removeAttribute('required');
    });
    
    // Adicionar required apenas aos campos do step atual que originalmente tinham
    const currentStepElement = document.querySelector(`.wizard-step[data-step="${step}"]`);
    if (currentStepElement) {
        // Adicionar required em campos que originalmente tinham
        currentStepElement.querySelectorAll('input[data-original-required], select[data-original-required]').forEach(input => {
            if (!input.disabled) {
                if (input.type === 'radio') {
                    // Para radio, adicionar ao primeiro do grupo
                    const radioName = input.name;
                    const firstRadio = currentStepElement.querySelector(`input[type="radio"][name="${radioName}"]`);
                    if (firstRadio && firstRadio.hasAttribute('data-original-required')) {
                        firstRadio.setAttribute('required', 'required');
                    }
                } else {
                    input.setAttribute('required', 'required');
                }
            }
        });
    }
}

// Função para restaurar atributos required originais
export function restoreRequiredAttributes() {
    // Restaurar required em todos os campos que originalmente tinham
    document.querySelectorAll('.wizard-step input, .wizard-step select').forEach(input => {
        // Verificar se o campo originalmente tinha required (verificar no HTML)
        const stepElement = input.closest('.wizard-step');
        const allInputs = stepElement.querySelectorAll(`input[name="${input.name}"], select[name="${input.name}"]`);
        if (allInputs.length > 0) {
            // Se é radio, adicionar required ao primeiro
            if (input.type === 'radio') {
                if (allInputs[0].hasAttribute('data-original-required')) {
                    allInputs[0].setAttribute('required', 'required');
                }
            } else {
                // Para outros campos, restaurar se tinha originalmente
                if (input.hasAttribute('data-original-required')) {
                    input.setAttribute('required', 'required');
                }
            }
        }
    });
}
