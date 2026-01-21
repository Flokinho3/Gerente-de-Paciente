// Elementos do DOM
export const form = document.getElementById('formPaciente');
export const messageDiv = document.getElementById('message');
export const progressFill = document.getElementById('progressFill');
export const currentStepSpan = document.getElementById('currentStep');
export const totalStepsSpan = document.getElementById('totalSteps');
export const btnAnterior = document.getElementById('btnAnterior');
export const btnProximo = document.getElementById('btnProximo');
export const btnSalvar = document.getElementById('btnSalvar');

// Estado do wizard
export let currentStep = 1;

export function setCurrentStep(step) {
    currentStep = step;
}

export function getCurrentStep() {
    return currentStep;
}

// Marcar campos que originalmente tinham required
export function initializeRequiredFields() {
    document.querySelectorAll('input[required], select[required]').forEach(input => {
        if (input.type === 'radio') {
            // Para radio buttons, marcar todos do grupo
            const radioName = input.name;
            document.querySelectorAll(`input[type="radio"][name="${radioName}"]`).forEach(radio => {
                radio.setAttribute('data-original-required', 'true');
            });
        } else {
            input.setAttribute('data-original-required', 'true');
        }
    });
}
