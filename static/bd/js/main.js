// Gerenciamento completo do banco de dados
let todosPacientes = [];
let pacientesFiltrados = [];
let paginaAtual = 1;
const pacientesPorPagina = 20;
let colunaOrdenacao = 'nome';
let ordemAscendente = true;
let termoPesquisa = '';

// Elementos de Loading
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingTitle = document.getElementById('loadingTitle');
const loadingMessage = document.getElementById('loadingMessage');
const loadingProgressFill = document.getElementById('loadingProgressFill');
const loadingProgressPercent = document.getElementById('loadingProgressPercent');

// Elementos DOM
const searchInput = document.getElementById('searchInput');
const tableBody = document.getElementById('tableBody');
const totalRecords = document.getElementById('totalRecords');
const showingRecords = document.getElementById('showingRecords');
const paginationText = document.getElementById('paginationText');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const addBtn = document.getElementById('addBtn');
const refreshBtn = document.getElementById('refreshBtn');
const editModal = document.getElementById('editModal');
const closeModal = document.getElementById('closeModal');
const cancelBtn = document.getElementById('cancelBtn');
const saveBtn = document.getElementById('saveBtn');
const patientForm = document.getElementById('patientForm');
const modalTitle = document.getElementById('modalTitle');
const statusMessage = document.getElementById('statusMessage');

// Campos do formulário
const patientId = document.getElementById('patientId');
const nomeGestante = document.getElementById('nomeGestante');
const unidadeSaude = document.getElementById('unidadeSaude');
const inicioPreNatal = document.getElementById('inicioPreNatal');
const consultasPreNatal = document.getElementById('consultasPreNatal');
const vacinasCompletas = document.getElementById('vacinasCompletas');
const planoParto = document.getElementById('planoParto');
const participouGrupos = document.getElementById('participouGrupos');
const avaliacaoOdontologica = document.getElementById('avaliacaoOdontologica');
const estratificacao = document.getElementById('estratificacao');
const cartaoPreNatalCompleto = document.getElementById('cartaoPreNatalCompleto');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarPacientes();
    configurarEventos();
});

// Configurar eventos
function configurarEventos() {
    // Pesquisa em tempo real
    let timeoutPesquisa;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeoutPesquisa);
        timeoutPesquisa = setTimeout(() => {
            termoPesquisa = e.target.value.toLowerCase().trim();
            filtrarEOrdenar();
            renderizarTabela();
        }, 300);
    });

    // Ordenação por colunas
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const novaColuna = header.dataset.column;
            if (colunaOrdenacao === novaColuna) {
                ordemAscendente = !ordemAscendente;
            } else {
                colunaOrdenacao = novaColuna;
                ordemAscendente = true;
            }
            atualizarIndicadoresOrdenacao();
            filtrarEOrdenar();
            renderizarTabela();
        });
    });

    // Paginação
    prevPageBtn.addEventListener('click', () => {
        if (paginaAtual > 1) {
            paginaAtual--;
            renderizarTabela();
        }
    });

    nextPageBtn.addEventListener('click', () => {
        const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
        if (paginaAtual < totalPaginas) {
            paginaAtual++;
            renderizarTabela();
        }
    });

    // Botões de ação
    addBtn.addEventListener('click', () => abrirModalAdicionar());
    refreshBtn.addEventListener('click', () => carregarPacientes());
    
    // Botões de backup/restore
    const backupBtn = document.getElementById('backupBtn');
    const loadBackupBtn = document.getElementById('loadBackupBtn');
    const clearDbBtn = document.getElementById('clearDbBtn');
    const confirmClearModal = document.getElementById('confirmClearModal');
    const closeConfirmModal = document.getElementById('closeConfirmModal');
    const cancelClearBtn = document.getElementById('cancelClearBtn');
    const confirmClearBtn = document.getElementById('confirmClearBtn');
    const confirmText = document.getElementById('confirmText');
    const backupFileInput = document.getElementById('backupFileInput');
    
    if (backupBtn) {
        backupBtn.addEventListener('click', criarBackupBD);
    }
    
    if (loadBackupBtn) {
        loadBackupBtn.addEventListener('click', () => backupFileInput.click());
        backupFileInput.addEventListener('change', carregarBackupBD);
    }
    
    if (clearDbBtn) {
        clearDbBtn.addEventListener('click', () => {
            confirmClearModal.classList.add('active');
            confirmText.value = '';
            confirmClearBtn.disabled = true;
        });
    }
    
    if (closeConfirmModal) {
        closeConfirmModal.addEventListener('click', () => {
            confirmClearModal.classList.remove('active');
            confirmText.value = '';
        });
    }
    
    if (cancelClearBtn) {
        cancelClearBtn.addEventListener('click', () => {
            confirmClearModal.classList.remove('active');
            confirmText.value = '';
        });
    }
    
    if (confirmText) {
        confirmText.addEventListener('input', (e) => {
            confirmClearBtn.disabled = e.target.value !== 'CONFIRMAR';
        });
    }
    
    if (confirmClearBtn) {
        confirmClearBtn.addEventListener('click', () => {
            if (confirmText.value === 'CONFIRMAR') {
                excluirTodosDadosBD();
            }
        });
    }

    // Modal
    closeModal.addEventListener('click', fecharModal);
    cancelBtn.addEventListener('click', fecharModal);
    saveBtn.addEventListener('click', salvarPaciente);

    // Fechar modal ao clicar fora
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) {
            fecharModal();
        }
    });
}

// Carregar pacientes
async function carregarPacientes() {
    try {
        mostrarLoading('Carregando Pacientes', 'Buscando dados dos pacientes no servidor...');
        atualizarProgressoLoading(20);

        tableBody.innerHTML = '<tr><td colspan="9" class="loading-row">Carregando dados...</td></tr>';

        atualizarProgressoLoading(50);
        const response = await fetch('/api/pacientes');
        atualizarProgressoLoading(80);

        const data = await response.json();

        if (data.success) {
            todosPacientes = data.pacientes || [];
            paginaAtual = 1;
            filtrarEOrdenar();
            renderizarTabela();
            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                mostrarStatus('Dados carregados com sucesso!', 'success');
            }, 300);
        } else {
            esconderLoading();
            mostrarErro('Erro ao carregar pacientes');
        }
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
        esconderLoading();
        mostrarErro('Erro ao conectar com o servidor');
    }
}

// Filtrar e ordenar
function filtrarEOrdenar() {
    // Filtrar
    if (termoPesquisa) {
        pacientesFiltrados = todosPacientes.filter(paciente => {
            const nome = (paciente.identificacao?.nome_gestante || '').toLowerCase();
            const unidade = (paciente.identificacao?.unidade_saude || '').toLowerCase();
            return nome.includes(termoPesquisa) || unidade.includes(termoPesquisa);
        });
    } else {
        pacientesFiltrados = [...todosPacientes];
    }

    // Ordenar
    pacientesFiltrados.sort((a, b) => {
        let valorA, valorB;

        switch (colunaOrdenacao) {
            case 'nome':
                valorA = (a.identificacao?.nome_gestante || '').toLowerCase();
                valorB = (b.identificacao?.nome_gestante || '').toLowerCase();
                break;
            case 'unidade':
                valorA = (a.identificacao?.unidade_saude || '').toLowerCase();
                valorB = (b.identificacao?.unidade_saude || '').toLowerCase();
                break;
            case 'data':
                valorA = new Date(a.data_salvamento || 0);
                valorB = new Date(b.data_salvamento || 0);
                break;
            default:
                return 0;
        }

        if (valorA < valorB) return ordemAscendente ? -1 : 1;
        if (valorA > valorB) return ordemAscendente ? 1 : -1;
        return 0;
    });

    atualizarEstatisticas();
}

// Atualizar indicadores de ordenação
function atualizarIndicadoresOrdenacao() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.classList.remove('asc', 'desc');
        if (header.dataset.column === colunaOrdenacao) {
            header.classList.add(ordemAscendente ? 'asc' : 'desc');
        }
    });
}

// Atualizar estatísticas
function atualizarEstatisticas() {
    totalRecords.textContent = todosPacientes.length;
    const inicio = (paginaAtual - 1) * pacientesPorPagina;
    const fim = Math.min(inicio + pacientesPorPagina, pacientesFiltrados.length);
    showingRecords.textContent = `${inicio + 1}-${fim} de ${pacientesFiltrados.length}`;

    const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina) || 1;
    paginationText.textContent = `Página ${paginaAtual} de ${totalPaginas}`;

    prevPageBtn.disabled = paginaAtual <= 1;
    nextPageBtn.disabled = paginaAtual >= totalPaginas || totalPaginas === 0;
}

// Renderizar tabela
function renderizarTabela() {
    const inicio = (paginaAtual - 1) * pacientesPorPagina;
    const fim = inicio + pacientesPorPagina;
    const pacientesPagina = pacientesFiltrados.slice(inicio, fim);

    if (pacientesPagina.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="9" class="loading-row">Nenhum paciente encontrado.</td></tr>';
        atualizarEstatisticas();
        return;
    }

    tableBody.innerHTML = pacientesPagina.map(paciente => {
        const ident = paciente.identificacao || {};
        const avaliacao = paciente.avaliacao || {};
        const data = formatarData(paciente.data_salvamento);

        return `
            <tr>
                <td>${ident.nome_gestante || 'Não informado'}</td>
                <td>${ident.unidade_saude || 'Não informado'}</td>
                <td>${data}</td>
                <td>${formatarBoolean(avaliacao.inicio_pre_natal_antes_12s)}</td>
                <td>${avaliacao.consultas_pre_natal || 0}</td>
                <td>${avaliacao.vacinas_completas || 'Não avaliado'}</td>
                <td>${formatarBoolean(avaliacao.plano_parto)}</td>
                <td>${formatarBoolean(avaliacao.participou_grupos)}</td>
                <td class="actions-column">
                    <div class="action-buttons">
                        <button class="action-btn edit" onclick="editarPaciente('${paciente.id}')">
                            ✏️ Editar
                        </button>
                        <button class="action-btn delete" onclick="confirmarExclusao('${paciente.id}')">
                            🗑️ Excluir
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    atualizarEstatisticas();
}

// Abrir modal para adicionar
function abrirModalAdicionar() {
    modalTitle.textContent = 'Adicionar Novo Paciente';
    patientForm.reset();
    patientId.value = '';
    editModal.classList.add('active');
}

// Editar paciente
async function editarPaciente(pacienteId) {
    try {
        const response = await fetch(`/api/pacientes`);
        const data = await response.json();

        if (data.success) {
            const paciente = data.pacientes.find(p => p.id === pacienteId);
            
            if (paciente) {
                preencherFormulario(paciente);
                modalTitle.textContent = 'Editar Paciente';
                editModal.classList.add('active');
            } else {
                mostrarStatus('Paciente não encontrado', 'error');
            }
        }
    } catch (error) {
        console.error('Erro ao carregar paciente:', error);
        mostrarStatus('Erro ao carregar dados do paciente', 'error');
    }
}

// Preencher formulário
function preencherFormulario(paciente) {
    const ident = paciente.identificacao || {};
    const avaliacao = paciente.avaliacao || {};

    patientId.value = paciente.id || '';
    nomeGestante.value = ident.nome_gestante || '';
    unidadeSaude.value = ident.unidade_saude || '';
    inicioPreNatal.checked = avaliacao.inicio_pre_natal_antes_12s === true;
    consultasPreNatal.value = avaliacao.consultas_pre_natal || 0;
    vacinasCompletas.value = avaliacao.vacinas_completas || '';
    planoParto.checked = avaliacao.plano_parto === true;
    participouGrupos.checked = avaliacao.participou_grupos === true;
    avaliacaoOdontologica.checked = avaliacao.avaliacao_odontologica === true;
    estratificacao.checked = avaliacao.estratificacao === true;
    cartaoPreNatalCompleto.checked = avaliacao.cartao_pre_natal_completo === true;
}

// Salvar paciente
async function salvarPaciente() {
    if (!patientForm.checkValidity()) {
        patientForm.reportValidity();
        return;
    }

    const pacienteData = {
        identificacao: {
            nome_gestante: nomeGestante.value.trim(),
            unidade_saude: unidadeSaude.value.trim()
        },
        avaliacao: {
            inicio_pre_natal_antes_12s: inicioPreNatal.checked,
            consultas_pre_natal: parseInt(consultasPreNatal.value) || 0,
            vacinas_completas: vacinasCompletas.value,
            plano_parto: planoParto.checked,
            participou_grupos: participouGrupos.checked,
            avaliacao_odontologica: avaliacaoOdontologica.checked,
            estratificacao: estratificacao.checked,
            cartao_pre_natal_completo: cartaoPreNatalCompleto.checked
        }
    };

    try {
        mostrarLoading('Salvando Paciente', 'Enviando dados para o servidor...');
        atualizarProgressoLoading(30);

        saveBtn.disabled = true;
        saveBtn.textContent = 'Salvando...';

        const pacienteIdValue = patientId.value;
        const url = pacienteIdValue
            ? `/api/atualizar_paciente/${pacienteIdValue}`
            : '/api/salvar_paciente';
        const method = pacienteIdValue ? 'PUT' : 'POST';

        atualizarProgressoLoading(60);
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pacienteData)
        });

        atualizarProgressoLoading(90);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(async () => {
                esconderLoading();
                mostrarStatus(pacienteIdValue ? 'Paciente atualizado com sucesso!' : 'Paciente adicionado com sucesso!', 'success');
                fecharModal();
                await carregarPacientes();
            }, 300);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao salvar paciente', 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar paciente:', error);
        esconderLoading();
        mostrarStatus('Erro ao salvar paciente', 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Salvar';
    }
}

// Confirmar exclusão
async function confirmarExclusao(pacienteId) {
    const paciente = todosPacientes.find(p => p.id === pacienteId);
    const nome = paciente?.identificacao?.nome_gestante || 'este paciente';

    if (confirm(`Tem certeza que deseja excluir o paciente "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        await excluirPaciente(pacienteId);
    }
}

// Excluir paciente
async function excluirPaciente(pacienteId) {
    try {
        const response = await fetch(`/api/deletar_paciente/${pacienteId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            mostrarStatus('Paciente excluído com sucesso!', 'success');
            await carregarPacientes();
        } else {
            mostrarStatus(data.message || 'Erro ao excluir paciente', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir paciente:', error);
        mostrarStatus('Erro ao excluir paciente', 'error');
    }
}

// Fechar modal
function fecharModal() {
    editModal.classList.remove('active');
    patientForm.reset();
}

// Funções auxiliares
function formatarData(dataString) {
    if (!dataString) return 'Data não disponível';
    try {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dataString;
    }
}

function formatarBoolean(valor) {
    if (valor === true) {
        return '<span class="badge badge-yes">Sim</span>';
    } else if (valor === false) {
        return '<span class="badge badge-no">Não</span>';
    } else {
        return '<span class="badge badge-unknown">Não informado</span>';
    }
}

function mostrarStatus(mensagem, tipo = 'success') {
    statusMessage.textContent = mensagem;
    statusMessage.className = `status-message status-${tipo}`;
    statusMessage.style.display = 'block';

    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 3000);
}

function mostrarErro(mensagem) {
    mostrarStatus(mensagem, 'error');
}

// Funções de Loading
function mostrarLoading(titulo = 'Processando...', mensagem = 'Por favor, aguarde enquanto processamos sua solicitação.') {
    loadingTitle.textContent = titulo;
    loadingMessage.textContent = mensagem;
    loadingOverlay.style.display = 'flex';
    atualizarProgressoLoading(0);
    // Desabilitar botões principais durante loading
    desabilitarBotoesAcao(true);
}

function esconderLoading() {
    loadingOverlay.style.display = 'none';
    // Reabilitar botões principais
    desabilitarBotoesAcao(false);
}

function atualizarProgressoLoading(percent) {
    const clampedPercent = Math.max(0, Math.min(100, percent));
    loadingProgressFill.style.width = clampedPercent + '%';
    loadingProgressPercent.textContent = clampedPercent + '%';
}

function desabilitarBotoesAcao(desabilitar) {
    const botoes = [
        document.getElementById('addBtn'),
        document.getElementById('refreshBtn'),
        document.getElementById('backupBtn'),
        document.getElementById('loadBackupBtn'),
        document.getElementById('clearDbBtn')
    ];

    botoes.forEach(botao => {
        if (botao) {
            botao.disabled = desabilitar;
            if (desabilitar) {
                botao.style.opacity = '0.6';
                botao.style.cursor = 'not-allowed';
            } else {
                botao.style.opacity = '1';
                botao.style.cursor = 'pointer';
            }
        }
    });
}

// Criar backup do banco de dados
async function criarBackupBD() {
    try {
        mostrarLoading('Criando Backup', 'Gerando cópia de segurança dos dados...');
        atualizarProgressoLoading(30);

        const response = await fetch('/api/backup/criar');
        atualizarProgressoLoading(70);

        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(90);

            // Criar link de download
            const blob = new Blob([JSON.stringify(data.backup, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            a.download = `backup_bd_${timestamp}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            atualizarProgressoLoading(100);
            setTimeout(() => {
                esconderLoading();
                mostrarStatus('Backup criado e baixado com sucesso!', 'success');
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao criar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar backup:', error);
        esconderLoading();
        mostrarStatus('Erro ao criar backup', 'error');
    }
}

// Carregar backup do banco de dados
async function carregarBackupBD(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        mostrarStatus('Por favor, selecione um arquivo JSON válido', 'error');
        return;
    }

    if (!confirm('ATENÇÃO: Carregar este backup irá substituir TODOS os dados atuais do banco de dados!\n\nTem certeza que deseja continuar?')) {
        event.target.value = '';
        return;
    }

    try {
        mostrarLoading('Carregando Backup', 'Lendo arquivo e validando estrutura...');
        atualizarProgressoLoading(20);

        const fileContent = await file.text();
        atualizarProgressoLoading(40);

        const backup = JSON.parse(fileContent);
        atualizarProgressoLoading(60);

        // Validar estrutura do backup
        let backupData = backup;

        // Verificar se é um backup antigo (com propriedade 'pacientes') ou novo (array direto)
        if (backup.pacientes && Array.isArray(backup.pacientes)) {
            backupData = backup.pacientes;
        } else if (backup.backup && Array.isArray(backup.backup)) {
            backupData = backup.backup;
        } else if (Array.isArray(backup)) {
            backupData = backup;
        } else {
            esconderLoading();
            mostrarStatus('Arquivo de backup inválido. Estrutura não reconhecida.', 'error');
            event.target.value = '';
            return;
        }

        atualizarProgressoLoading(80);
        const response = await fetch('/api/backup/restaurar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ backup: backupData })
        });

        atualizarProgressoLoading(90);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(async () => {
                esconderLoading();
                mostrarStatus('Backup restaurado com sucesso!', 'success');
                await carregarPacientes();
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao restaurar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar backup:', error);
        esconderLoading();
        if (error instanceof SyntaxError) {
            mostrarStatus('Erro: Arquivo JSON inválido', 'error');
        } else {
            mostrarStatus('Erro ao carregar backup', 'error');
        }
    } finally {
        event.target.value = '';
    }
}

// Excluir todos os dados do banco de dados
async function excluirTodosDadosBD() {
    try {
        mostrarLoading('Excluindo Dados', 'Removendo todos os registros do banco de dados...');
        atualizarProgressoLoading(50);

        const response = await fetch('/api/backup/limpar', {
            method: 'DELETE'
        });

        atualizarProgressoLoading(80);
        const data = await response.json();

        if (data.success) {
            atualizarProgressoLoading(100);
            setTimeout(async () => {
                esconderLoading();
                mostrarStatus('Todos os dados foram excluídos com sucesso!', 'success');
                document.getElementById('confirmClearModal').classList.remove('active');
                document.getElementById('confirmText').value = '';
                await carregarPacientes();
            }, 500);
        } else {
            esconderLoading();
            mostrarStatus(data.message || 'Erro ao excluir dados', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir dados:', error);
        esconderLoading();
        mostrarStatus('Erro ao excluir dados', 'error');
    }
}
