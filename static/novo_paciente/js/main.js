// Configuração do Wizard
let currentStep = 1;
const totalSteps = 10;
const form = document.getElementById('formPaciente');
const messageDiv = document.getElementById('message');

// Elementos do DOM
const progressFill = document.getElementById('progressFill');
const currentStepSpan = document.getElementById('currentStep');
const totalStepsSpan = document.getElementById('totalSteps');
const btnAnterior = document.getElementById('btnAnterior');
const btnProximo = document.getElementById('btnProximo');
const btnSalvar = document.getElementById('btnSalvar');

// Marcar campos que originalmente tinham required
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

// Inicializar
totalStepsSpan.textContent = totalSteps;
showStep(currentStep); // Inicializar o primeiro step corretamente
updateProgress();

// Função para mostrar mensagem
function showMessage(text, isError = false) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${isError ? 'error' : 'success'}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Função para validar campo do step atual
function validateCurrentStep() {
    const currentStepElement = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return false;
    
    // Validar inputs de texto e number
    const textInputs = currentStepElement.querySelectorAll('input[type="text"], input[type="number"], select');
    for (let input of textInputs) {
        if (input.hasAttribute('required')) {
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

// Função para atualizar progresso
function updateProgress() {
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

// Função para gerenciar atributo required dinamicamente
function toggleRequiredAttributes(step) {
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

// Função para mostrar step
function showStep(step) {
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
        
        // Scroll suave para o topo do container
        document.querySelector('.container').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Função para ir para próximo step
function nextStep() {
    if (currentStep < totalSteps && validateCurrentStep()) {
        currentStep++;
        showStep(currentStep);
        updateProgress();
        
        // Focar no primeiro campo do próximo step
        const stepElement = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
        const firstInput = stepElement.querySelector('input, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }
}

// Função para ir para step anterior
function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
        updateProgress();
        
        // Focar no primeiro campo do step anterior
        const stepElement = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
        const firstInput = stepElement.querySelector('input, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }
}

// Event listeners para inputs (validar em tempo real)
form.addEventListener('input', function(e) {
    // Verificar se o input pertence ao step atual
    const inputStep = e.target.closest('.wizard-step');
    const currentStepElement = document.querySelector('.wizard-step.active');
    
    if (inputStep === currentStepElement) {
        updateProgress();
    }
});

// Event listeners para radio buttons
form.addEventListener('change', function(e) {
    if (e.target.type === 'radio') {
        const inputStep = e.target.closest('.wizard-step');
        const currentStepElement = document.querySelector('.wizard-step.active');
        
        if (inputStep === currentStepElement) {
            updateProgress();
        }
    }
});

// Event listeners para botões
btnProximo.addEventListener('click', nextStep);
btnAnterior.addEventListener('click', previousStep);

// Permitir avançar com Enter (apenas se válido)
form.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && currentStep < totalSteps) {
        e.preventDefault();
        if (validateCurrentStep()) {
            nextStep();
        }
    }
});

// Função para verificar se paciente já existe (busca exata por nome)
async function verificarPacienteExistente(nome) {
    try {
        const response = await fetch(`/api/pacientes?nome=${encodeURIComponent(nome)}`);
        const result = await response.json();
        
        if (result.success && result.pacientes && result.pacientes.length > 0) {
            // Buscar exatamente pelo nome (case-insensitive)
            const nomeLower = nome.toLowerCase().trim();
            for (let paciente of result.pacientes) {
                const nomePaciente = paciente.identificacao.nome_gestante.toLowerCase().trim();
                if (nomePaciente === nomeLower) {
                    return paciente;
                }
            }
        }
        return null;
    } catch (error) {
        console.error('Erro ao verificar paciente:', error);
        return null;
    }
}

// Função para mostrar diálogo de confirmação
function mostrarDialogoDuplicata(pacienteExistente, callback) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Paciente já cadastrado</h3>
            <p>Já existe um paciente cadastrado com o nome <strong>"${pacienteExistente.identificacao.nome_gestante}"</strong>.</p>
            <div class="modal-info">
                <p><strong>Unidade:</strong> ${pacienteExistente.identificacao.unidade_saude}</p>
                <p><strong>Data do cadastro:</strong> ${pacienteExistente.data_salvamento}</p>
            </div>
            <p class="modal-question">O que deseja fazer?</p>
            <div class="modal-actions">
                <button id="btnAtualizar" class="btn btn-primary">🔄 Atualizar Dados</button>
                <button id="btnDescartar" class="btn btn-secondary">❌ Descartar</button>
                <button id="btnCancelar" class="btn btn-secondary">↩️ Cancelar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    document.getElementById('btnAtualizar').addEventListener('click', () => {
        document.body.removeChild(modal);
        callback('atualizar', pacienteExistente);
    });
    
    document.getElementById('btnDescartar').addEventListener('click', () => {
        document.body.removeChild(modal);
        callback('descartar');
    });
    
    document.getElementById('btnCancelar').addEventListener('click', () => {
        document.body.removeChild(modal);
        callback('cancelar');
    });
    
    // Fechar ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
            callback('cancelar');
        }
    });
}

// Função para salvar paciente
async function salvarPaciente(data, pacienteId = null) {
    const originalText = btnSalvar.textContent;
    btnSalvar.disabled = true;
    btnSalvar.textContent = '⏳ Salvando...';
    
    try {
        const url = pacienteId ? `/api/atualizar_paciente/${pacienteId}` : '/api/salvar_paciente';
        const method = pacienteId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage(`✅ ${result.message}`, false);
            form.reset();
            // Redirecionar após 2 segundos
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showMessage(`❌ ${result.message}`, true);
            btnSalvar.disabled = false;
            btnSalvar.textContent = originalText;
        }
    } catch (error) {
        showMessage(`❌ Erro ao salvar: ${error.message}`, true);
        btnSalvar.disabled = false;
        btnSalvar.textContent = originalText;
    }
}

// Submit do formulário
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Remover required de todos os campos escondidos antes de validar
    document.querySelectorAll('.wizard-step:not(.active) input, .wizard-step:not(.active) select').forEach(input => {
        input.removeAttribute('required');
    });
    
    // Validar último step manualmente
    if (!validateCurrentStep()) {
        showMessage('❌ Por favor, preencha todos os campos obrigatórios', true);
        // Restaurar required nos campos escondidos
        restoreRequiredAttributes();
        return;
    }
    
    // Restaurar required nos campos escondidos
    restoreRequiredAttributes();
    
    // Coletar dados do formulário
    const formData = new FormData(form);
    const nomeGestante = formData.get('nome_gestante').trim();
    
    // Verificar se paciente já existe
    const pacienteExistente = await verificarPacienteExistente(nomeGestante);
    
    const data = {
        identificacao: {
            nome_gestante: nomeGestante,
            unidade_saude: formData.get('unidade_saude').trim()
        },
        avaliacao: {
            inicio_pre_natal_antes_12s: formData.get('inicio_pre_natal_antes_12s') === 'true',
            consultas_pre_natal: parseInt(formData.get('consultas_pre_natal')),
            vacinas_completas: formData.get('vacinas_completas'),
            plano_parto: formData.get('plano_parto') === 'true',
            participou_grupos: formData.get('participou_grupos') === 'true',
            avaliacao_odontologica: formData.get('avaliacao_odontologica') === 'true',
            estratificacao: formData.get('estratificacao') === 'true',
            cartao_pre_natal_completo: formData.get('cartao_pre_natal_completo') === 'true'
        }
    };
    
    if (pacienteExistente) {
        // Mostrar diálogo de duplicata
        mostrarDialogoDuplicata(pacienteExistente, (acao, paciente) => {
            if (acao === 'atualizar') {
                salvarPaciente(data, paciente.id);
            } else if (acao === 'descartar') {
                salvarPaciente(data); // Salvar mesmo assim (novo registro)
            }
            // Se cancelar, não faz nada
        });
    } else {
        // Não existe duplicata, salvar normalmente
        salvarPaciente(data);
    }
});

// Função para restaurar atributos required originais
function restoreRequiredAttributes() {
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
