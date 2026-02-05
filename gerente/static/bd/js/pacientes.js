/**
 * pacientes.js - Gerenciamento de pacientes (CRUD)
 * Inclui: Carregar, adicionar, editar, excluir pacientes
 */

// Elementos do formulário
const patientForm = document.getElementById('patientForm');
const patientId = document.getElementById('patientId');
const nomeGestante = document.getElementById('nomeGestante');
const unidadeSaude = document.getElementById('unidadeSaude');
const jaGanhouCrianca = document.getElementById('jaGanhouCrianca');
const dataGanhouCrianca = document.getElementById('dataGanhouCrianca');
const dataGanhouGroup = document.getElementById('data-ganhou-group');
const quantidadeFilhos = document.getElementById('quantidadeFilhos');
const generosFilhos = document.getElementById('generosFilhos');
const metodoPreventivo = document.getElementById('metodoPreventivo');
const metodoPreventivoOutros = document.getElementById('metodoPreventivoOutros');
const metodoPreventivoOutrosGroup = document.getElementById('metodo-preventivo-outros-group');
const dum = document.getElementById('dum');
const dpp = document.getElementById('dpp');
const proximaAvaliacao = document.getElementById('proximaAvaliacao');
const proximaAvaliacaoHora = document.getElementById('proximaAvaliacaoHora');
const inicioPreNatal = document.getElementById('inicioPreNatal');
const inicioPreNatalSemanas = document.getElementById('inicioPreNatalSemanas');
const inicioPreNatalObservacao = document.getElementById('inicioPreNatalObservacao');
const inicioPreNatalDetalhesGroup = document.getElementById('inicio-pre-natal-detalhes-group');
const consultasPreNatal = document.getElementById('consultasPreNatal');
const vacinasCompletas = document.getElementById('vacinasCompletas');
const planoParto = document.getElementById('planoParto');
const participouGrupos = document.getElementById('participouGrupos');
const avaliacaoOdontologica = document.getElementById('avaliacaoOdontologica');
const estratificacao = document.getElementById('estratificacao');
const estratificacaoProblema = document.getElementById('estratificacaoProblema');
const estratificacaoProblemaGroup = document.getElementById('estratificacao-problema-group');
const cartaoPreNatalCompleto = document.getElementById('cartaoPreNatalCompleto');
const possuiBolsaFamilia = document.getElementById('possuiBolsaFamilia');
const temVacinaCovid = document.getElementById('temVacinaCovid');
const planoPartoEntreguePorUnidade = document.getElementById('planoPartoEntreguePorUnidade');
const ganhouKit = document.getElementById('ganhouKit');
const kitTipoGroup = document.getElementById('kit-tipo-group');

// Elementos do modal
const editModal = document.getElementById('editModal');
const modalTitle = document.getElementById('modalTitle');
const saveBtn = document.getElementById('saveBtn');

// ==================== CARREGAR PACIENTES ====================

async function carregarPacientes() {
    try {
        mostrarLoading('Carregando Pacientes', 'Buscando dados dos pacientes no servidor...');
        atualizarProgressoLoading(20);

        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="9" class="loading-row">Carregando dados...</td></tr>';
        }

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

// ==================== RENDERIZAR TABELA ====================

function renderizarTabela() {
    if (!tableBody) return;
    
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

// ==================== MODAL E FORMULÁRIO ====================

function abrirModalAdicionar() {
    if (!editModal || !patientForm) return;
    
    modalTitle.textContent = 'Adicionar Novo Paciente';
    patientForm.reset();
    if (patientId) patientId.value = '';
    if (proximaAvaliacaoHora) proximaAvaliacaoHora.value = '08:00';
    
    [estratificacaoProblemaGroup, dataGanhouGroup, metodoPreventivoOutrosGroup, kitTipoGroup, inicioPreNatalDetalhesGroup].forEach(el => {
        if (el) el.style.display = 'none';
    });
    
    document.querySelectorAll('input[name="kitTipo"]').forEach(cb => { cb.checked = false; });
    editModal.classList.add('active');
}

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

function preencherFormulario(paciente) {
    const ident = paciente.identificacao || {};
    const av = paciente.avaliacao || {};

    if (patientId) patientId.value = paciente.id || '';
    if (nomeGestante) nomeGestante.value = ident.nome_gestante || '';
    if (unidadeSaude) unidadeSaude.value = ident.unidade_saude || '';

    if (jaGanhouCrianca) jaGanhouCrianca.checked = av.ja_ganhou_crianca === true;
    if (dataGanhouCrianca) dataGanhouCrianca.value = (av.data_ganhou_crianca || '').toString().slice(0, 10);
    if (dataGanhouGroup) dataGanhouGroup.style.display = av.ja_ganhou_crianca ? 'block' : 'none';
    if (quantidadeFilhos) quantidadeFilhos.value = av.quantidade_filhos ?? 0;
    if (generosFilhos) generosFilhos.value = av.generos_filhos || '';
    if (metodoPreventivo) metodoPreventivo.value = av.metodo_preventivo || '';
    if (metodoPreventivoOutros) metodoPreventivoOutros.value = av.metodo_preventivo_outros || '';
    if (metodoPreventivoOutrosGroup) metodoPreventivoOutrosGroup.style.display = av.metodo_preventivo === 'Outros' ? 'block' : 'none';

    if (dum) dum.value = (av.dum || '').toString().slice(0, 10);
    if (dpp) dpp.value = (av.dpp || '').toString().slice(0, 10);
    if (proximaAvaliacao) proximaAvaliacao.value = (av.proxima_avaliacao || '').toString().slice(0, 10);
    if (proximaAvaliacaoHora) proximaAvaliacaoHora.value = (av.proxima_avaliacao_hora || '08:00').toString().slice(0, 5);

    if (inicioPreNatal) inicioPreNatal.checked = av.inicio_pre_natal_antes_12s === true;
    if (inicioPreNatalSemanas) inicioPreNatalSemanas.value = av.inicio_pre_natal_semanas ?? '';
    if (inicioPreNatalObservacao) inicioPreNatalObservacao.value = av.inicio_pre_natal_observacao || '';
    if (inicioPreNatalDetalhesGroup) inicioPreNatalDetalhesGroup.style.display = av.inicio_pre_natal_antes_12s ? 'block' : 'none';

    if (consultasPreNatal) consultasPreNatal.value = av.consultas_pre_natal ?? 0;
    if (vacinasCompletas) vacinasCompletas.value = av.vacinas_completas || '';
    if (planoParto) planoParto.checked = av.plano_parto === true;
    if (participouGrupos) participouGrupos.checked = av.participou_grupos === true;
    if (avaliacaoOdontologica) avaliacaoOdontologica.checked = av.avaliacao_odontologica === true;
    if (estratificacao) estratificacao.checked = av.estratificacao === true;
    
    if (estratificacaoProblema) {
        estratificacaoProblema.value = av.estratificacao_problema || '';
        if (estratificacaoProblemaGroup) estratificacaoProblemaGroup.style.display = av.estratificacao ? 'block' : 'none';
    }
    
    if (cartaoPreNatalCompleto) cartaoPreNatalCompleto.checked = av.cartao_pre_natal_completo === true;
    if (possuiBolsaFamilia) possuiBolsaFamilia.checked = av.possui_bolsa_familia === true;
    if (temVacinaCovid) temVacinaCovid.checked = av.tem_vacina_covid === true;
    
    if (planoPartoEntreguePorUnidade) {
        const v = av.plano_parto_entregue_por_unidade || 'Nenhuma';
        planoPartoEntreguePorUnidade.value = v;
        if (![].slice.call(planoPartoEntreguePorUnidade.options).some(o => o.value === v)) {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            planoPartoEntreguePorUnidade.appendChild(opt);
            planoPartoEntreguePorUnidade.value = v;
        }
    }

    if (ganhouKit) ganhouKit.checked = av.ganhou_kit === true;
    if (kitTipoGroup) kitTipoGroup.style.display = av.ganhou_kit ? 'block' : 'none';
    
    document.querySelectorAll('input[name="kitTipo"]').forEach(cb => {
        cb.checked = (av.kit_tipo || '').split(',').map(s => s.trim()).includes(cb.value);
    });
}

function fecharModal() {
    if (editModal) editModal.classList.remove('active');
    if (patientForm) patientForm.reset();
}

// ==================== SALVAR PACIENTE ====================

async function salvarPaciente() {
    if (!patientForm || !patientForm.checkValidity()) {
        if (patientForm) patientForm.reportValidity();
        return;
    }

    const kitTipoVals = [];
    document.querySelectorAll('input[name="kitTipo"]:checked').forEach(cb => { kitTipoVals.push(cb.value); });
    const kitTipoStr = ganhouKit && ganhouKit.checked && kitTipoVals.length ? kitTipoVals.join(',') : null;

    const pacienteData = {
        identificacao: {
            nome_gestante: nomeGestante ? nomeGestante.value.trim() : '',
            unidade_saude: unidadeSaude ? unidadeSaude.value.trim() : ''
        },
        avaliacao: {
            ja_ganhou_crianca: jaGanhouCrianca ? jaGanhouCrianca.checked : false,
            data_ganhou_crianca: dataGanhouCrianca && jaGanhouCrianca && jaGanhouCrianca.checked && dataGanhouCrianca.value ? dataGanhouCrianca.value : null,
            quantidade_filhos: quantidadeFilhos ? (parseInt(quantidadeFilhos.value) || 0) : null,
            generos_filhos: generosFilhos ? (generosFilhos.value.trim() || null) : null,
            metodo_preventivo: metodoPreventivo ? (metodoPreventivo.value || null) : null,
            metodo_preventivo_outros: metodoPreventivo && metodoPreventivo.value === 'Outros' && metodoPreventivoOutros ? (metodoPreventivoOutros.value.trim() || null) : null,
            dum: dum && dum.value ? dum.value : null,
            dpp: dpp && dpp.value ? dpp.value : null,
            proxima_avaliacao: proximaAvaliacao && proximaAvaliacao.value ? proximaAvaliacao.value : null,
            proxima_avaliacao_hora: proximaAvaliacaoHora && proximaAvaliacao && proximaAvaliacao.value ? (proximaAvaliacaoHora.value || '08:00') : null,
            inicio_pre_natal_antes_12s: inicioPreNatal ? inicioPreNatal.checked : false,
            inicio_pre_natal_semanas: inicioPreNatal && inicioPreNatal.checked && inicioPreNatalSemanas && inicioPreNatalSemanas.value ? parseInt(inicioPreNatalSemanas.value) : null,
            inicio_pre_natal_observacao: inicioPreNatal && inicioPreNatal.checked && inicioPreNatalObservacao ? (inicioPreNatalObservacao.value.trim() || null) : null,
            consultas_pre_natal: consultasPreNatal ? (parseInt(consultasPreNatal.value) || 0) : 0,
            vacinas_completas: vacinasCompletas ? (vacinasCompletas.value || null) : null,
            plano_parto: planoParto ? planoParto.checked : false,
            participou_grupos: participouGrupos ? participouGrupos.checked : false,
            avaliacao_odontologica: avaliacaoOdontologica ? avaliacaoOdontologica.checked : false,
            estratificacao: estratificacao ? estratificacao.checked : false,
            estratificacao_problema: estratificacao && estratificacao.checked && estratificacaoProblema ? (estratificacaoProblema.value.trim() || null) : null,
            cartao_pre_natal_completo: cartaoPreNatalCompleto ? cartaoPreNatalCompleto.checked : false,
            possui_bolsa_familia: possuiBolsaFamilia ? possuiBolsaFamilia.checked : false,
            tem_vacina_covid: temVacinaCovid ? temVacinaCovid.checked : false,
            plano_parto_entregue_por_unidade: planoPartoEntreguePorUnidade ? (planoPartoEntreguePorUnidade.value || 'Nenhuma') : 'Nenhuma',
            ganhou_kit: ganhouKit ? ganhouKit.checked : false,
            kit_tipo: kitTipoStr
        }
    };

    try {
        mostrarLoading('Salvando Paciente', 'Enviando dados para o servidor...');
        atualizarProgressoLoading(30);

        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Salvando...';
        }

        const pacienteIdValue = patientId ? patientId.value : '';
        const url = pacienteIdValue
            ? `/api/atualizar_paciente/${pacienteIdValue}`
            : '/api/salvar_paciente';
        const method = pacienteIdValue ? 'PUT' : 'POST';

        atualizarProgressoLoading(60);
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
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
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Salvar';
        }
    }
}

// ==================== EXCLUIR PACIENTE ====================

async function confirmarExclusao(pacienteId) {
    const paciente = todosPacientes.find(p => p.id === pacienteId);
    const nome = paciente?.identificacao?.nome_gestante || 'este paciente';

    if (confirm(`Tem certeza que deseja excluir o paciente "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        await excluirPaciente(pacienteId);
    }
}

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
