/**
 * main.js - Coordenador principal do módulo de banco de dados
 * Apenas inicializa a aplicação e configura event listeners globais.
 * A lógica está dividida em módulos:
 * - core.js: Utilitários, loading, formatação
 * - pacientes.js: CRUD de pacientes
 * - backup.js: Backup e restore
 * - importacao.js: Comparação e importação seletiva
 * - importacao-acoes.js: Ações individuais de importação
 * - sync.js: Sincronização entre servidores
 */

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    inicializarApp();
});

function inicializarApp() {
    // Carregar dados iniciais
    carregarPacientes();
    carregarUnidadesPlanoPartoBD();
    
    // Configurar todos os event listeners
    configurarEventosGlobais();
    configurarEventosModal();
    configurarEventosImportacao();
}

// ==================== EVENTOS GLOBAIS ====================

function configurarEventosGlobais() {
    // Pesquisa em tempo real
    let timeoutPesquisa;
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeoutPesquisa);
            timeoutPesquisa = setTimeout(() => {
                termoPesquisa = e.target.value.toLowerCase().trim();
                filtrarEOrdenar();
                renderizarTabela();
            }, 300);
        });
    }

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
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (paginaAtual > 1) {
                paginaAtual--;
                renderizarTabela();
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            const totalPaginas = Math.ceil(pacientesFiltrados.length / pacientesPorPagina);
            if (paginaAtual < totalPaginas) {
                paginaAtual++;
                renderizarTabela();
            }
        });
    }

    // Botões principais
    const addBtn = document.getElementById('addBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    if (addBtn) addBtn.addEventListener('click', abrirModalAdicionar);
    if (refreshBtn) refreshBtn.addEventListener('click', carregarPacientes);

    // Botões de backup
    const backupBtn = document.getElementById('backupBtn');
    const loadBackupBtn = document.getElementById('loadBackupBtn');
    const backupFileInput = document.getElementById('backupFileInput');
    
    if (backupBtn) backupBtn.addEventListener('click', criarBackupBD);
    if (loadBackupBtn && backupFileInput) {
        loadBackupBtn.addEventListener('click', () => backupFileInput.click());
        backupFileInput.addEventListener('change', carregarBackupBDComAcoes);
    }

    // Botões de sincronização
    const syncBtn = document.getElementById('syncBtn');
    if (syncBtn) {
        syncBtn.addEventListener('click', () => {
            const syncModal = document.getElementById('syncModal');
            if (syncModal) {
                syncModal.classList.add('active');
                resetSyncModal();
            }
        });
    }

    // Limpar banco de dados
    const clearDbBtn = document.getElementById('clearDbBtn');
    const confirmClearModal = document.getElementById('confirmClearModal');
    const confirmClearBtn = document.getElementById('confirmClearBtn');
    const confirmText = document.getElementById('confirmText');
    
    if (clearDbBtn && confirmClearModal) {
        clearDbBtn.addEventListener('click', () => {
            confirmClearModal.classList.add('active');
            if (confirmText) confirmText.value = '';
            if (confirmClearBtn) confirmClearBtn.disabled = true;
        });
    }
    
    if (confirmText && confirmClearBtn) {
        confirmText.addEventListener('input', (e) => {
            confirmClearBtn.disabled = e.target.value !== 'CONFIRMAR';
        });
        confirmClearBtn.addEventListener('click', () => {
            if (confirmText.value === 'CONFIRMAR') excluirTodosDadosBD();
        });
    }

    // Fechar modais ao clicar fora
    if (editModal) {
        editModal.addEventListener('click', (e) => {
            if (e.target === editModal) fecharModal();
        });
    }

    const syncModal = document.getElementById('syncModal');
    if (syncModal) {
        syncModal.addEventListener('click', (e) => {
            if (e.target === syncModal) syncModal.classList.remove('active');
        });
    }
}

// ==================== EVENTOS DO MODAL DE PACIENTE ====================

function configurarEventosModal() {
    const closeModalBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const saveBtn = document.getElementById('saveBtn');

    if (closeModalBtn) closeModalBtn.addEventListener('click', fecharModal);
    if (cancelBtn) cancelBtn.addEventListener('click', fecharModal);
    if (saveBtn) saveBtn.addEventListener('click', salvarPaciente);

    // Campos condicionais
    if (estratificacao && estratificacaoProblemaGroup) {
        estratificacao.addEventListener('change', () => {
            estratificacaoProblemaGroup.style.display = estratificacao.checked ? 'block' : 'none';
            if (!estratificacao.checked && estratificacaoProblema) {
                estratificacaoProblema.value = '';
            }
        });
    }

    if (jaGanhouCrianca && dataGanhouGroup) {
        jaGanhouCrianca.addEventListener('change', () => {
            dataGanhouGroup.style.display = jaGanhouCrianca.checked ? 'block' : 'none';
            if (!jaGanhouCrianca.checked && dataGanhouCrianca) {
                dataGanhouCrianca.value = '';
            }
        });
    }

    if (metodoPreventivo && metodoPreventivoOutrosGroup) {
        metodoPreventivo.addEventListener('change', () => {
            metodoPreventivoOutrosGroup.style.display = metodoPreventivo.value === 'Outros' ? 'block' : 'none';
            if (metodoPreventivo.value !== 'Outros' && metodoPreventivoOutros) {
                metodoPreventivoOutros.value = '';
            }
        });
    }

    if (ganhouKit && kitTipoGroup) {
        ganhouKit.addEventListener('change', () => {
            kitTipoGroup.style.display = ganhouKit.checked ? 'block' : 'none';
            if (!ganhouKit.checked) {
                document.querySelectorAll('input[name="kitTipo"]').forEach(cb => cb.checked = false);
            }
        });
    }

    if (inicioPreNatal && inicioPreNatalDetalhesGroup) {
        inicioPreNatal.addEventListener('change', () => {
            inicioPreNatalDetalhesGroup.style.display = inicioPreNatal.checked ? 'block' : 'none';
            if (!inicioPreNatal.checked) {
                if (inicioPreNatalSemanas) inicioPreNatalSemanas.value = '';
                if (inicioPreNatalObservacao) inicioPreNatalObservacao.value = '';
            }
        });
    }

    if (dum && dpp) {
        dum.addEventListener('change', () => {
            const dppVal = calcularDPPBD(dum.value);
            if (dppVal) dpp.value = dppVal;
        });
    }
}

// ==================== EVENTOS DE IMPORTAÇÃO ====================

function configurarEventosImportacao() {
    const closeBtn = document.getElementById('closeImportBackupModal');
    const cancelBtn = document.getElementById('cancelarImportacao');
    const executarBtn = document.getElementById('executarImportacaoBtn');
    const ignorarTodosBtn = document.getElementById('selecionarTodosIgnorar');
    const confirmarTodosBtn = document.getElementById('selecionarTodosConfirmar');
    const importModal = document.getElementById('importBackupModal');

    if (closeBtn && importModal) {
        closeBtn.addEventListener('click', () => {
            importModal.classList.remove('active');
            limparAcoesImportacao();
        });
    }

    if (cancelBtn && importModal) {
        cancelBtn.addEventListener('click', () => {
            importModal.classList.remove('active');
            limparAcoesImportacao();
        });
    }

    if (executarBtn) {
        executarBtn.addEventListener('click', confirmarImportacaoComAcoes);
    }

    if (ignorarTodosBtn) {
        ignorarTodosBtn.addEventListener('click', () => selecionarTodosAcao('ignorar'));
    }

    if (confirmarTodosBtn) {
        confirmarTodosBtn.addEventListener('click', () => selecionarTodosAcao('confirmar'));
    }
}

// ==================== EXPORTAR FUNÇÕES GLOBAIS ====================

// Funções necessárias para onclick inline no HTML
window.editarPaciente = editarPaciente;
window.confirmarExclusao = confirmarExclusao;
window.fecharModal = fecharModal;
