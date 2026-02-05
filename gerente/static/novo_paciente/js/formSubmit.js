import { form, btnSalvar, getCurrentStep, setCurrentStep } from './dom.js';
import { showMessage } from './utils.js';
import { validateCurrentStep, restoreRequiredAttributes } from './validation.js';
import { showStep, updateProgress } from './wizard.js';

// Função para verificar se paciente já existe (busca exata por nome)
export async function verificarPacienteExistente(nome) {
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
export function mostrarDialogoDuplicata(pacienteExistente, callback) {
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
export async function salvarPaciente(data, pacienteId = null) {
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

// Função para inicializar o submit do formulário
export function initializeFormSubmit() {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Remover required de todos os campos escondidos antes de validar
        document.querySelectorAll('.wizard-step:not(.active) input, .wizard-step:not(.active) select').forEach(input => {
            input.removeAttribute('required');
        });
        
        // Coletar dados do formulário primeiro (antes de validar)
        const formData = new FormData(form);
        // Definir `proximaAvaliacao` a partir do FormData para evitar ReferenceError
        const proximaAvaliacao = formData.get('proxima_avaliacao');
        
        // Validar último step manualmente
        if (!validateCurrentStep()) {
            showMessage('❌ Por favor, preencha todos os campos obrigatórios', true);
            // Restaurar required nos campos escondidos
            restoreRequiredAttributes();
            return;
        }
        
        // Validar campos de início do pré-natal apenas se inicio_pre_natal_antes_12s for true
        const inicioPreNatalValue = formData.get('inicio_pre_natal_antes_12s');
        const inicioPreNatalSemanasValue = formData.get('inicio_pre_natal_semanas');
        if (inicioPreNatalValue === 'true' && (!inicioPreNatalSemanasValue || inicioPreNatalSemanasValue.trim() === '')) {
            showMessage('❌ Por favor, informe a quantidade de semanas de gestação no início do pré-natal', true);
            // Ir para o step 3 para mostrar o campo
            setCurrentStep(3);
            showStep(3);
            updateProgress();
            return;
        }
        
        // Validar campo de tipo de KIT apenas se ganhou_kit for true
        const ganhouKitValue = formData.get('ganhou_kit');
        const kitTipoValues = formData.getAll('kit_tipo'); // getAll para pegar todos os checkboxes selecionados
        if (ganhouKitValue === 'true' && kitTipoValues.length === 0) {
            showMessage('❌ Por favor, selecione pelo menos um tipo de KIT recebido', true);
            // Ir para o step 16 para mostrar o campo
            setCurrentStep(16);
            showStep(16);
            updateProgress();
            return;
        }

        // Validar data da próxima avaliação apenas se o step estiver visível (deve ser futura)
        const stepAgendamento = document.getElementById('step-proxima-avaliacao');
        const isAgendamentoVisible = stepAgendamento && stepAgendamento.style.display !== 'none' && !stepAgendamento.classList.contains('hidden-step');
        
        if (isAgendamentoVisible && proximaAvaliacao) {
            const dataAvaliacao = new Date(proximaAvaliacao);
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0); // Resetar horas para comparar apenas datas

            if (dataAvaliacao < hoje) {
                showMessage('❌ A data da próxima avaliação deve ser hoje ou uma data futura', true);
                // Ir para o step 18 para mostrar o campo
                setCurrentStep(18);
                showStep(18);
                updateProgress();
                return;
            }
        }
        
        // Restaurar required nos campos escondidos
        restoreRequiredAttributes();
        const nomeGestante = formData.get('nome_gestante').trim();
        
        // Verificar se paciente já existe
        const pacienteExistente = await verificarPacienteExistente(nomeGestante);
        
        const data = {
            identificacao: {
                nome_gestante: nomeGestante,
                unidade_saude: formData.get('unidade_saude').trim()
            },
            avaliacao: {
                ja_ganhou_crianca: formData.get('ja_ganhou_crianca') === 'true',
                data_ganhou_crianca: formData.get('data_ganhou_crianca') || null,
                quantidade_filhos: formData.get('quantidade_filhos') ? parseInt(formData.get('quantidade_filhos')) : null,
                generos_filhos: formData.get('generos_filhos') || null,
                metodo_preventivo: formData.get('metodo_preventivo') || null,
                metodo_preventivo_outros: formData.get('metodo_preventivo_outros') || null,
                dum: formData.get('dum') || null,
                dpp: formData.get('dpp') || null,
                inicio_pre_natal_antes_12s: formData.get('inicio_pre_natal_antes_12s') === 'true',
                inicio_pre_natal_semanas: inicioPreNatalValue === 'true' ? parseInt(formData.get('inicio_pre_natal_semanas')) : null,
                inicio_pre_natal_observacao: formData.get('inicio_pre_natal_observacao') || '',
                consultas_pre_natal: parseInt(formData.get('consultas_pre_natal')),
                vacinas_completas: formData.get('vacinas_completas'),
                plano_parto: formData.get('plano_parto') === 'true',
                participou_grupos: formData.get('participou_grupos') === 'true',
                avaliacao_odontologica: formData.get('avaliacao_odontologica') === 'true',
                estratificacao: formData.get('estratificacao') === 'true',
                estratificacao_problema: formData.get('estratificacao_problema') || '',
                cartao_pre_natal_completo: formData.get('cartao_pre_natal_completo') === 'true',
                possui_bolsa_familia: formData.get('possui_bolsa_familia') === 'true',
                tem_vacina_covid: formData.get('tem_vacina_covid') === 'true',
                ganhou_kit: formData.get('ganhou_kit') === 'true',
                kit_tipo: ganhouKitValue === 'true' ? (kitTipoValues.length > 0 ? kitTipoValues.join(',') : null) : null,
                proxima_avaliacao: formData.get('proxima_avaliacao') || null,
                proxima_avaliacao_hora: formData.get('proxima_avaliacao_hora') || null,
                plano_parto_entregue_por_unidade: formData.get('plano_parto_entregue_por_unidade') || 'Nenhuma'
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

        // Log para debug
        const proximaAvaliacaoHora = formData.get('proxima_avaliacao_hora');
        console.log('Próxima avaliação:', proximaAvaliacao, proximaAvaliacaoHora);
    });
}
