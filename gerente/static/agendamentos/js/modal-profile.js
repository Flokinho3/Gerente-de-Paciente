// Módulo do modal de perfil de paciente

// Obter dados completos da paciente
async function obterDadosPaciente(pacienteId) {
    try {
        const response = await fetch(`/api/pacientes`);
        const data = await response.json();

        if (data.success && data.pacientes) {
            return data.pacientes.find(p => p.id === pacienteId);
        }
        return null;
    } catch (error) {
        console.error('Erro ao buscar dados da paciente:', error);
        return null;
    }
}

// Abrir perfil completo da paciente
async function abrirPerfilCompleto(pacienteId) {
    try {
        const paciente = await obterDadosPaciente(pacienteId);
        if (paciente) {
            renderizarModalPerfil(paciente);
            mostrarModalPerfil();
        } else {
            mostrarMensagem('Paciente não encontrado', true);
        }
    } catch (error) {
        console.error('Erro ao abrir perfil completo:', error);
        mostrarMensagem('Erro ao carregar perfil da paciente', true);
    }
}

// Renderizar modal de perfil
function renderizarModalPerfil(paciente) {
    const identificacao = paciente.identificacao || {};
    const avaliacao = paciente.avaliacao || {};

    const html = `
        <div class="perfil-section">
            <h3>📋 Identificação</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">Nome da Gestante</span>
                    <div class="perfil-value">${identificacao.nome_gestante || 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Unidade de Saúde</span>
                    <div class="perfil-value">${identificacao.unidade_saude || 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Data de Cadastro</span>
                    <div class="perfil-value">${formatarData(paciente.data_salvamento)}</div>
                </div>
            </div>
        </div>

        ${avaliacao.ja_ganhou_crianca !== undefined || avaliacao.quantidade_filhos !== undefined || avaliacao.metodo_preventivo ? `
        <div class="perfil-section">
            <h3>👶 Histórico Reprodutivo</h3>
            <div class="perfil-field-grid">
                ${avaliacao.ja_ganhou_crianca !== undefined ? `
                <div class="perfil-field">
                    <span class="perfil-label">Já ganhou a criança?</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.ja_ganhou_crianca)}</div>
                </div>
                ` : ''}
                ${avaliacao.ja_ganhou_crianca && avaliacao.data_ganhou_crianca ? `
                <div class="perfil-field">
                    <span class="perfil-label">Data (gêmeos ou mais)</span>
                    <div class="perfil-value">${formatarDataSimples(avaliacao.data_ganhou_crianca)}</div>
                </div>
                ` : ''}
                ${avaliacao.quantidade_filhos !== undefined ? `
                <div class="perfil-field">
                    <span class="perfil-label">Quantidade de Filhos</span>
                    <div class="perfil-value">${avaliacao.quantidade_filhos || 0}</div>
                </div>
                ` : ''}
                ${avaliacao.quantidade_filhos > 0 && avaliacao.generos_filhos ? `
                <div class="perfil-field" style="grid-column: 1 / -1;">
                    <span class="perfil-label">Gêneros dos Filhos</span>
                    <div class="perfil-value" style="background: #e8f5e9; padding: 12px; border-radius: 8px; border-left: 4px solid #4caf50;">
                        ${avaliacao.generos_filhos}
                    </div>
                </div>
                ` : ''}
                ${avaliacao.metodo_preventivo ? `
                <div class="perfil-field">
                    <span class="perfil-label">Método Preventivo Atual</span>
                    <div class="perfil-value">
                        <span class="badge-status">${avaliacao.metodo_preventivo}</span>
                    </div>
                </div>
                ` : ''}
                ${avaliacao.metodo_preventivo === 'Outros' && avaliacao.metodo_preventivo_outros ? `
                <div class="perfil-field" style="grid-column: 1 / -1;">
                    <span class="perfil-label">Especificação do Método Preventivo</span>
                    <div class="perfil-value" style="background: #fff3e0; padding: 12px; border-radius: 8px; border-left: 4px solid #ff9800; white-space: pre-wrap; word-wrap: break-word;">
                        ${avaliacao.metodo_preventivo_outros}
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
        ` : ''}

        <div class="perfil-section">
            <h3>📅 Datas Importantes</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">DUM (Data da Última Menstruação)</span>
                    <div class="perfil-value">${formatarDataSimples(avaliacao.dum) || 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">DPP (Data Provável do Parto)</span>
                    <div class="perfil-value">${formatarDataSimples(avaliacao.dpp) || 'Não informado'}</div>
                </div>
                ${avaliacao.proxima_avaliacao ? `
                <div class="perfil-field">
                    <span class="perfil-label">Próxima Avaliação</span>
                    <div class="perfil-value">
                        ${formatarDataSimples(avaliacao.proxima_avaliacao)}
                        ${avaliacao.proxima_avaliacao_hora ? ` às ${formatarHora(avaliacao.proxima_avaliacao_hora)}` : ''}
                    </div>
                </div>
                ` : ''}
            </div>
        </div>

        <div class="perfil-section">
            <h3>📊 Avaliação</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">Início Pré-Natal antes de 12 semanas</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.inicio_pre_natal_antes_12s)}</div>
                </div>
                ${avaliacao.inicio_pre_natal_antes_12s && avaliacao.inicio_pre_natal_semanas != null ? `
                <div class="perfil-field">
                    <span class="perfil-label">Semanas de gestação no início</span>
                    <div class="perfil-value">${avaliacao.inicio_pre_natal_semanas} semanas</div>
                </div>
                ` : ''}
                ${avaliacao.inicio_pre_natal_antes_12s && avaliacao.inicio_pre_natal_observacao ? `
                <div class="perfil-field" style="grid-column: 1 / -1;">
                    <span class="perfil-label">Observações sobre o início do pré-natal</span>
                    <div class="perfil-value" style="background: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 4px solid #2196f3; white-space: pre-wrap; word-wrap: break-word;">${avaliacao.inicio_pre_natal_observacao}</div>
                </div>
                ` : ''}
                <div class="perfil-field">
                    <span class="perfil-label">Consultas de pré-natal</span>
                    <div class="perfil-value">${avaliacao.consultas_pre_natal ?? 'Não informado'}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Vacinas completas</span>
                    <div class="perfil-value">${typeof window.getBadgeClassVacina === 'function' ? `<span class="badge-status ${window.getBadgeClassVacina(avaliacao.vacinas_completas)}">${avaliacao.vacinas_completas || 'Não avaliado'}</span>` : (avaliacao.vacinas_completas || 'Não avaliado')}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Plano de parto</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.plano_parto)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Participou de grupos</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.participou_grupos)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Avaliação odontológica</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.avaliacao_odontologica)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Estratificação</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.estratificacao)}</div>
                </div>
                ${avaliacao.estratificacao && avaliacao.estratificacao_problema ? `
                <div class="perfil-field" style="grid-column: 1 / -1;">
                    <span class="perfil-label">Problema identificado na estratificação</span>
                    <div class="perfil-value" style="background: #fff3cd; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; white-space: pre-wrap; word-wrap: break-word;">${avaliacao.estratificacao_problema}</div>
                </div>
                ` : ''}
                <div class="perfil-field">
                    <span class="perfil-label">Cartão pré-natal completo</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.cartao_pre_natal_completo)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Possui Bolsa Família</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.possui_bolsa_familia)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Tem vacina de COVID</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.tem_vacina_covid)}</div>
                </div>
                <div class="perfil-field">
                    <span class="perfil-label">Plano de parto entregue por</span>
                    <div class="perfil-value">${avaliacao.plano_parto_entregue_por_unidade || 'Nenhuma'}</div>
                </div>
            </div>
        </div>

        ${avaliacao.ganhou_kit !== undefined ? `
        <div class="perfil-section">
            <h3>🎁 KIT</h3>
            <div class="perfil-field-grid">
                <div class="perfil-field">
                    <span class="perfil-label">Ganhou o KIT?</span>
                    <div class="perfil-value">${formatarBoolean(avaliacao.ganhou_kit)}</div>
                </div>
                ${avaliacao.ganhou_kit && avaliacao.kit_tipo && typeof window.formatarKitTipo === 'function' ? `
                <div class="perfil-field">
                    <span class="perfil-label">Tipo(s) de KIT</span>
                    <div class="perfil-value">${window.formatarKitTipo(avaliacao.kit_tipo)}</div>
                </div>
                ` : ''}
            </div>
        </div>
        ` : ''}
    `;

    const conteudoPerfil = document.getElementById('conteudoPerfil');
    if (conteudoPerfil) {
        conteudoPerfil.innerHTML = html;
    }
}

// Configurar modal de perfil
function configurarModalPerfil() {
    const modal = document.getElementById('modalPerfil');
    const btnFechar = document.getElementById('fecharModalPerfil');

    if (btnFechar) {
        btnFechar.addEventListener('click', fecharModalPerfil);
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                fecharModalPerfil();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.style.display !== 'none') {
            fecharModalPerfil();
        }
    });
}

// Mostrar modal de perfil
function mostrarModalPerfil() {
    const modal = document.getElementById('modalPerfil');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.style.opacity = '1';
        }, 10);
    }
}

// Fechar modal de perfil
function fecharModalPerfil() {
    const modal = document.getElementById('modalPerfil');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Exibir perfil resumido da paciente (usado no calendário)
function exibirPerfilResumido(paciente) {
    const identificacao = paciente.identificacao || {};
    const avaliacao = paciente.avaliacao || {};

    let html = '';

    if (identificacao.unidade_saude) {
        html += `<div class="unidade-saude">🏥 ${identificacao.unidade_saude}</div>`;
    }

    if (avaliacao.dpp) {
        const dppFormatada = formatarDataSimples(avaliacao.dpp);
        html += `<div class="dpp-paciente">📅 DPP: ${dppFormatada}</div>`;
    }

    return html;
}

// Exportar funções
window.abrirPerfilCompleto = abrirPerfilCompleto;
window.obterDadosPaciente = obterDadosPaciente;
window.configurarModalPerfil = configurarModalPerfil;
window.exibirPerfilResumido = exibirPerfilResumido;
