/**
 * Modal de Edição de Aparência - Editor de Paleta de Cores
 * Permite ao usuário personalizar as cores do sistema com preview em tempo real
 */

class AparenciaModal {
    constructor() {
        this.modalId = 'aparencia-modal';
        this.isOpen = false;
        this.currentTheme = null;
        this.originalTheme = null;
        this.colorInputs = {};
        this.init();
    }

    /**
     * Inicializa o modal
     */
    init() {
        this.createModalHTML();
        this.setupEventListeners();
        this.loadCurrentTheme();
    }

    /**
     * Cria o HTML do modal dinamicamente
     */
    createModalHTML() {
        if (document.getElementById(this.modalId)) {
            return; // Modal já existe
        }

        const modalHTML = `
            <div id="${this.modalId}" class="aparencia-modal-overlay" style="display: none;">
                <div class="aparencia-modal">
                    <div class="aparencia-modal-header">
                        <h2>🎨 Personalizar Aparência</h2>
                        <button class="aparencia-modal-close" onclick="aparenciaModal.close()">
                            <span>&times;</span>
                        </button>
                    </div>

                    <div class="aparencia-modal-body">
                        <div class="aparencia-theme-info">
                            <div class="aparencia-theme-name">
                                <label for="theme-name">Nome do Tema:</label>
                                <input type="text" id="theme-name" placeholder="Meu Tema Personalizado" maxlength="50">
                            </div>
                            <div class="aparencia-theme-status">
                                <span id="theme-status">Tema atual: Padrão</span>
                            </div>
                        </div>

                        <div class="aparencia-color-groups">
                            ${this.createColorGroupHTML('Cores Principais', 'primary', [
                                {key: '--bg', label: 'Fundo Geral', default: '#f2f5f4'},
                                {key: '--card', label: 'Cartões', default: '#ffffff'},
                                {key: '--primary', label: 'Cor Primária', default: '#2f7d6d'},
                                {key: '--primary-hover', label: 'Primária (Hover)', default: '#266758'},
                                {key: '--secondary', label: 'Cor Secundária', default: '#4a90a4'},
                                {key: '--secondary-hover', label: 'Secundária (Hover)', default: '#3d7a8a'},
                                {key: '--accent', label: 'Destaque', default: '#e6f2ef'},
                                {key: '--text', label: 'Texto Principal', default: '#263238'},
                                {key: '--text-muted', label: 'Texto Secundário', default: '#607d8b'}
                            ])}

                            ${this.createColorGroupHTML('Estados e Feedback', 'states', [
                                {key: '--success', label: 'Sucesso', default: '#2e7d32'},
                                {key: '--success-light', label: 'Sucesso (Claro)', default: '#c8e6c9'},
                                {key: '--warning', label: 'Aviso', default: '#f57c00'},
                                {key: '--warning-light', label: 'Aviso (Claro)', default: '#ffe0b2'},
                                {key: '--danger', label: 'Erro', default: '#c62828'},
                                {key: '--danger-light', label: 'Erro (Claro)', default: '#ffcdd2'},
                                {key: '--info', label: 'Informação', default: '#0277bd'},
                                {key: '--info-light', label: 'Informação (Claro)', default: '#b3e5fc'}
                            ])}

                            ${this.createColorGroupHTML('Bordas e Elementos', 'borders', [
                                {key: '--border', label: 'Borda', default: '#d0d7d5'},
                                {key: '--border-light', label: 'Borda (Clara)', default: '#e8edec'}
                            ])}
                        </div>

                        <div class="aparencia-preview">
                            <h3>Preview do Tema</h3>
                            <div class="aparencia-preview-content">
                                <div class="preview-card">
                                    <h4>Exemplo de Cartão</h4>
                                    <p>Este é um exemplo de como ficará a aparência com as cores selecionadas.</p>
                                    <button class="preview-btn-primary">Botão Primário</button>
                                    <button class="preview-btn-secondary">Botão Secundário</button>
                                </div>
                                <div class="preview-alerts">
                                    <div class="preview-alert preview-alert-success">Mensagem de sucesso</div>
                                    <div class="preview-alert preview-alert-warning">Mensagem de aviso</div>
                                    <div class="preview-alert preview-alert-danger">Mensagem de erro</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="aparencia-modal-footer">
                        <button class="aparencia-btn aparencia-btn-secondary" onclick="aparenciaModal.resetToDefault()">
                            🔄 Resetar para Padrão
                        </button>
                        <div class="aparencia-footer-actions">
                            <button class="aparencia-btn aparencia-btn-cancel" onclick="aparenciaModal.close()">
                                Cancelar
                            </button>
                            <button class="aparencia-btn aparencia-btn-primary" onclick="aparenciaModal.saveTheme()">
                                💾 Salvar Tema
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    /**
     * Cria HTML para um grupo de cores
     */
    createColorGroupHTML(title, groupId, colors) {
        return `
            <div class="aparencia-color-group">
                <h3>${title}</h3>
                <div class="aparencia-color-grid" id="${groupId}-colors">
                    ${colors.map(color => `
                        <div class="aparencia-color-item">
                            <label for="${color.key.replace('--', '')}">${color.label}</label>
                            <div class="aparencia-color-input-wrapper">
                                <input type="color"
                                       id="${color.key.replace('--', '')}"
                                       name="${color.key}"
                                       value="${color.default}"
                                       class="aparencia-color-input"
                                       data-variable="${color.key}">
                                <span class="aparencia-color-value">${color.default}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Configura os event listeners
     */
    setupEventListeners() {
        // Event listeners serão configurados quando o modal for criado
        // Os eventos dos inputs são configurados em loadCurrentTheme()
    }

    /**
     * Carrega o tema atual nos inputs
     */
    loadCurrentTheme() {
        try {
            this.currentTheme = themeManager.getCurrentTheme();
            this.originalTheme = JSON.parse(JSON.stringify(this.currentTheme)); // Deep copy

            // Preencher nome do tema
            const nameInput = document.getElementById('theme-name');
            if (nameInput) {
                nameInput.value = this.currentTheme.nome;
            }

            // Atualizar status
            this.updateThemeStatus();

            // Preencher inputs de cor
            for (const [variable, color] of Object.entries(this.currentTheme.cores)) {
                const inputId = variable.replace('--', '');
                const input = document.getElementById(inputId);
                if (input) {
                    input.value = color;
                    this.colorInputs[variable] = input;

                    // Atualizar valor exibido
                    const valueSpan = input.nextElementSibling;
                    if (valueSpan && valueSpan.classList.contains('aparencia-color-value')) {
                        valueSpan.textContent = color;
                    }
                }
            }

            // Configurar event listeners para preview em tempo real
            this.setupColorInputListeners();

        } catch (error) {
            console.error('Erro ao carregar tema atual:', error);
        }
    }

    /**
     * Configura listeners para inputs de cor (preview em tempo real)
     */
    setupColorInputListeners() {
        for (const [variable, input] of Object.entries(this.colorInputs)) {
            input.addEventListener('input', (e) => {
                const newColor = e.target.value;
                this.updateColorPreview(variable, newColor);
                this.updateColorValueDisplay(e.target, newColor);
            });

            input.addEventListener('change', (e) => {
                const newColor = e.target.value;
                this.currentTheme.cores[variable] = newColor;
            });
        }

        // Listener para nome do tema
        const nameInput = document.getElementById('theme-name');
        if (nameInput) {
            nameInput.addEventListener('input', (e) => {
                this.currentTheme.nome = e.target.value.trim() || 'Tema Personalizado';
                this.updateThemeStatus();
            });
        }
    }

    /**
     * Atualiza o preview de uma cor específica
     */
    updateColorPreview(variable, color) {
        const previewTheme = JSON.parse(JSON.stringify(this.currentTheme));
        previewTheme.cores[variable] = color;
        themeManager.applyTheme(previewTheme);
    }

    /**
     * Atualiza a exibição do valor da cor
     */
    updateColorValueDisplay(input, color) {
        const valueSpan = input.nextElementSibling;
        if (valueSpan && valueSpan.classList.contains('aparencia-color-value')) {
            valueSpan.textContent = color;
        }
    }

    /**
     * Atualiza o status do tema
     */
    updateThemeStatus() {
        const statusElement = document.getElementById('theme-status');
        if (statusElement) {
            const isCustom = themeManager.hasCustomTheme();
            const themeName = this.currentTheme ? this.currentTheme.nome : 'Padrão';
            statusElement.textContent = isCustom ? `Tema atual: ${themeName}` : 'Tema atual: Padrão';
            statusElement.className = isCustom ? 'theme-status-custom' : 'theme-status-default';
        }
    }

    /**
     * Abre o modal
     */
    open() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'flex';
            this.isOpen = true;
            this.loadCurrentTheme();

            // Focar no primeiro input
            setTimeout(() => {
                const firstInput = document.querySelector('.aparencia-color-input');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 100);
        }
    }

    /**
     * Fecha o modal
     */
    close() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'none';
            this.isOpen = false;

            // Restaurar tema original se não foi salvo
            if (this.originalTheme) {
                themeManager.applyTheme(this.originalTheme);
            }
        }
    }

    /**
     * Salva o tema atual
     */
    saveTheme() {
        try {
            if (!this.currentTheme) {
                alert('Erro: Tema não carregado corretamente.');
                return;
            }

            // Validar nome do tema
            const themeName = this.currentTheme.nome.trim();
            if (!themeName) {
                this.currentTheme.nome = 'Tema Personalizado';
            }

            // Tentar salvar
            const success = themeManager.saveTheme(this.currentTheme);

            if (success) {
                alert(`Tema "${this.currentTheme.nome}" salvo com sucesso!`);
                this.updateThemeStatus();
                this.close();
            } else {
                alert('Erro ao salvar o tema. Tente novamente.');
            }

        } catch (error) {
            console.error('Erro ao salvar tema:', error);
            alert('Erro inesperado ao salvar o tema.');
        }
    }

    /**
     * Reseta para o tema padrão
     */
    resetToDefault() {
        if (confirm('Tem certeza que deseja resetar para o tema padrão? Todas as personalizações serão perdidas.')) {
            try {
                const success = themeManager.resetToDefault();
                if (success) {
                    alert('Tema resetado para o padrão com sucesso!');
                    this.loadCurrentTheme();
                } else {
                    alert('Erro ao resetar tema. Tente novamente.');
                }
            } catch (error) {
                console.error('Erro ao resetar tema:', error);
                alert('Erro inesperado ao resetar tema.');
            }
        }
    }

    /**
     * Verifica se o modal está aberto
     */
    isModalOpen() {
        return this.isOpen;
    }
}

// ========== INSTÂNCIA GLOBAL ==========
const aparenciaModal = new AparenciaModal();

// ========== FUNÇÕES GLOBAIS ==========
window.AparenciaModal = AparenciaModal;
window.aparenciaModal = aparenciaModal;

// ========== FUNÇÃO PARA ABRIR MODAL (usada no HTML) ==========
function abrirAparenciaModal() {
    aparenciaModal.open();
}

window.abrirAparenciaModal = abrirAparenciaModal;