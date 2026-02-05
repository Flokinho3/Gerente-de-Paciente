// Módulo de pesquisa e seleção de pacientes

// Variáveis
let todosPacientes = [];
let timeoutPesquisa = null;

// Elementos DOM
const pacienteSearch = document.getElementById('pacienteSearch');
const pacienteIdHidden = document.getElementById('pacienteId');
const pacienteSearchResults = document.getElementById('pacienteSearchResults');

// Carregar todos os pacientes para pesquisa
async function carregarTodosPacientes() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();
        
        if (data.success && data.pacientes) {
            todosPacientes = data.pacientes;
        }
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
        mostrarMensagem('Erro ao carregar pacientes', true);
    }
}

// Configurar pesquisa de paciente em tempo real
function configurarPesquisaPaciente() {
    if (!pacienteSearch) return;

    // Pesquisa com debounce
    pacienteSearch.addEventListener('input', (e) => {
        const termo = e.target.value.trim();

        if (timeoutPesquisa) {
            clearTimeout(timeoutPesquisa);
        }

        if (termo === '') {
            pacienteSearchResults.style.display = 'none';
            pacienteIdHidden.value = '';
            return;
        }

        timeoutPesquisa = setTimeout(() => {
            pesquisarPacientes(termo);
        }, 300);
    });

    // Fechar resultados ao clicar fora
    document.addEventListener('click', (e) => {
        if (!pacienteSearch.contains(e.target) && !pacienteSearchResults.contains(e.target)) {
            pacienteSearchResults.style.display = 'none';
        }
    });

    // Fechar resultados ao pressionar ESC
    pacienteSearch.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            pacienteSearchResults.style.display = 'none';
        }
    });
}

// Pesquisar pacientes
function pesquisarPacientes(termo) {
    if (!termo || termo.length < 2) {
        pacienteSearchResults.style.display = 'none';
        return;
    }

    const termoLower = termo.toLowerCase();
    const resultados = todosPacientes.filter(paciente => {
        const nome = paciente.identificacao?.nome_gestante || '';
        return nome.toLowerCase().includes(termoLower);
    }).slice(0, 10);

    if (resultados.length === 0) {
        pacienteSearchResults.innerHTML = '<div class="no-results">Nenhum paciente encontrado</div>';
        pacienteSearchResults.style.display = 'block';
        return;
    }

    let html = '';
    resultados.forEach(paciente => {
        const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
        const unidade = paciente.identificacao?.unidade_saude || 'Não informado';
        
        html += `
            <div class="paciente-result-item" data-paciente-id="${paciente.id}">
                <div class="paciente-result-info">
                    <div class="paciente-result-nome">${nome}</div>
                    <div class="paciente-result-unidade">${unidade}</div>
                </div>
                <button 
                    class="btn-preview-paciente" 
                    onclick="mostrarPreviewPerfil('${paciente.id}')"
                    title="Ver perfil"
                    type="button"
                >
                    👁️
                </button>
            </div>
        `;
    });

    pacienteSearchResults.innerHTML = html;
    pacienteSearchResults.style.display = 'block';

    pacienteSearchResults.querySelectorAll('.paciente-result-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-preview-paciente')) {
                return;
            }

            const pacienteId = item.dataset.pacienteId;
            const paciente = todosPacientes.find(p => p.id === pacienteId);
            
            if (paciente) {
                selecionarPaciente(paciente);
            }
        });
    });
}

// Selecionar paciente
function selecionarPaciente(paciente) {
    const nome = paciente.identificacao?.nome_gestante || 'Nome não informado';
    
    pacienteSearch.value = nome;
    pacienteIdHidden.value = paciente.id;
    pacienteSearchResults.style.display = 'none';
    
    pacienteSearch.setCustomValidity('');
    pacienteSearch.style.borderColor = 'var(--success)';
    
    setTimeout(() => {
        pacienteSearch.style.borderColor = '';
    }, 2000);
}

// Limpar seleção de paciente
function limparSelecaoPaciente() {
    if (pacienteSearch) {
        pacienteSearch.value = '';
    }
    if (pacienteIdHidden) {
        pacienteIdHidden.value = '';
    }
    if (pacienteSearchResults) {
        pacienteSearchResults.style.display = 'none';
    }
}

// Mostrar preview do perfil
async function mostrarPreviewPerfil(pacienteId) {
    try {
        const paciente = todosPacientes.find(p => p.id === pacienteId);
        
        if (!paciente) {
            const response = await fetch('/api/pacientes');
            const data = await response.json();
            
            if (data.success && data.pacientes) {
                const pacienteCompleto = data.pacientes.find(p => p.id === pacienteId);
                if (pacienteCompleto) {
                    renderizarPreviewPerfil(pacienteCompleto);
                    return;
                }
            }
            
            mostrarMensagem('Paciente não encontrado', true);
            return;
        }

        renderizarPreviewPerfil(paciente);
    } catch (error) {
        console.error('Erro ao mostrar preview do perfil:', error);
        mostrarMensagem('Erro ao carregar perfil', true);
    }
}

// Renderizar preview do perfil
function renderizarPreviewPerfil(paciente) {
    const identificacao = paciente.identificacao || {};
    const avaliacao = paciente.avaliacao || {};

    const html = `
        <div class="preview-section">
            <h4>📋 Identificação</h4>
            <div class="preview-field">
                <strong>Nome:</strong> ${identificacao.nome_gestante || 'Não informado'}
            </div>
            <div class="preview-field">
                <strong>Unidade:</strong> ${identificacao.unidade_saude || 'Não informado'}
            </div>
            <div class="preview-field">
                <strong>Cadastro:</strong> ${formatarData(paciente.data_salvamento)}
            </div>
        </div>

        <div class="preview-section">
            <h4>📅 Datas Importantes</h4>
            ${avaliacao.dum ? `
            <div class="preview-field">
                <strong>DUM:</strong> ${formatarDataSimples(avaliacao.dum)}
            </div>
            ` : ''}
            ${avaliacao.dpp ? `
            <div class="preview-field">
                <strong>DPP:</strong> ${formatarDataSimples(avaliacao.dpp)}
            </div>
            ` : ''}
            ${avaliacao.proxima_avaliacao ? `
            <div class="preview-field">
                <strong>Próxima Avaliação:</strong> ${formatarDataSimples(avaliacao.proxima_avaliacao)}
                ${avaliacao.proxima_avaliacao_hora ? ` às ${formatarHora(avaliacao.proxima_avaliacao_hora)}` : ''}
            </div>
            ` : ''}
        </div>

        <div class="preview-section">
            <h4>📊 Resumo</h4>
            ${avaliacao.quantidade_filhos !== undefined ? `
            <div class="preview-field">
                <strong>Filhos:</strong> ${avaliacao.quantidade_filhos || 0}
            </div>
            ` : ''}
            ${avaliacao.metodo_preventivo ? `
            <div class="preview-field">
                <strong>Método Preventivo:</strong> ${avaliacao.metodo_preventivo}
            </div>
            ` : ''}
            <div class="preview-field">
                <strong>Consultas:</strong> ${avaliacao.consultas_pre_natal || 0}
            </div>
            <div class="preview-field">
                <strong>Vacinas:</strong> ${avaliacao.vacinas_completas || 'Não avaliado'}
            </div>
            <div class="preview-field">
                <strong>Plano de Parto:</strong> ${formatarBoolean(avaliacao.plano_parto)}
            </div>
        </div>

        <div class="preview-actions">
            <button class="btn btn-primary" onclick="abrirPerfilCompleto('${paciente.id}'); fecharPreviewPerfil();" type="button">
                Ver Perfil Completo
            </button>
        </div>
    `;

    const conteudoPreview = document.getElementById('conteudoPreviewPerfil');
    if (conteudoPreview) {
        conteudoPreview.innerHTML = html;
    }

    const preview = document.getElementById('previewPerfil');
    if (preview) {
        preview.style.display = 'block';
        setTimeout(() => {
            preview.style.opacity = '1';
        }, 10);
    }

    const btnFechar = document.getElementById('fecharPreviewPerfil');
    if (btnFechar) {
        btnFechar.onclick = fecharPreviewPerfil;
    }

    preview.addEventListener('click', (e) => {
        if (e.target === preview) {
            fecharPreviewPerfil();
        }
    });
}

// Fechar preview do perfil
function fecharPreviewPerfil() {
    const preview = document.getElementById('previewPerfil');
    if (preview) {
        preview.style.opacity = '0';
        setTimeout(() => {
            preview.style.display = 'none';
        }, 300);
    }
}

// Exportar funções
window.carregarTodosPacientes = carregarTodosPacientes;
window.configurarPesquisaPaciente = configurarPesquisaPaciente;
window.selecionarPaciente = selecionarPaciente;
window.limparSelecaoPaciente = limparSelecaoPaciente;
window.mostrarPreviewPerfil = mostrarPreviewPerfil;
window.fecharPreviewPerfil = fecharPreviewPerfil;
window.obterTodosPacientes = () => todosPacientes;
