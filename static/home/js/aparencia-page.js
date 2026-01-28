/**
 * Página de Aparência - Editor de Paleta de Cores (Página Dedicada)
 * Versão expandida para página completa com mais espaço e funcionalidades
 */

class AparenciaPage {
    constructor() {
        this.currentTheme = null;
        this.originalTheme = null;
        this.colorInputs = {};
    }

    /**
     * Inicializa a página (chamado após DOMContentLoaded, após tema aplicado)
     */
    init() {
        this.loadCurrentTheme();
        this.setupEventListeners();
        this.updateThemeStatus();
        this.initializePrompt();
        this.setupImportListeners();
        this.loadSavedThemes();
    }

    /**
     * Carrega o tema atual nos inputs a partir do themeManager
     */
    loadCurrentTheme() {
        try {
            this.currentTheme = themeManager.getCurrentTheme();
            this.originalTheme = JSON.parse(JSON.stringify(this.currentTheme));
            this.fillFormFromTheme(this.currentTheme);
        } catch (error) {
            console.error('Erro ao carregar tema atual:', error);
        }
    }

    /**
     * Preenche o formulário a partir de um objeto tema (sem ler do themeManager)
     */
    fillFormFromTheme(theme) {
        if (!theme || !theme.cores) return;
        const nameInput = document.getElementById('theme-name');
        if (nameInput) nameInput.value = theme.nome || '';
        this.colorInputs = {};
        for (const [variable, color] of Object.entries(theme.cores)) {
            const inputId = variable.replace('--', '');
            const input = document.getElementById(inputId);
            if (input) {
                input.value = color;
                this.colorInputs[variable] = input;
                const valueSpan = input.nextElementSibling;
                if (valueSpan && valueSpan.classList.contains('aparencia-color-value')) {
                    valueSpan.textContent = color;
                }
            }
        }
    }

    /**
     * Configura os event listeners
     */
    setupEventListeners() {
        // Configurar event listeners para inputs de cor (preview em tempo real)
        this.setupColorInputListeners();

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
            statusElement.className = isCustom ? 'aparencia-theme-status-custom' : 'aparencia-theme-status-default';
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
            
            // Salvar também na lista de temas salvos
            this.saveThemeToList(this.currentTheme);

            if (success) {
                alert(`Tema "${this.currentTheme.nome}" salvo com sucesso! 🎨`);
                this.updateThemeStatus();
                this.loadSavedThemes(); // Recarregar lista de temas

                // Mostrar confirmação visual
                this.showSaveConfirmation();
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
            this._aplicarPadrao();
        }
    }

    /** Aplica o tema padrão sem pedir confirmação (usado pelo botão "Aplicar" do Padrão na lista). */
    aplicarPadrao() {
        this._aplicarPadrao();
    }

    _aplicarPadrao() {
        try {
            themeManager.deleteCookie('custom_css_filename');
            const link = document.getElementById('custom-css-link');
            if (link) link.remove();
            const success = themeManager.resetToDefault();
            if (success) {
                this.loadCurrentTheme();
                this.updateThemeStatus();
                this.loadSavedThemes();
                alert('Tema resetado para o padrão com sucesso! 🔄');
            } else {
                alert('Erro ao resetar tema. Tente novamente.');
            }
        } catch (error) {
            console.error('Erro ao resetar tema:', error);
            alert('Erro inesperado ao resetar tema.');
        }
    }

    /**
     * Mostra confirmação visual de salvamento
     */
    showSaveConfirmation() {
        // Criar elemento de confirmação temporário
        const confirmation = document.createElement('div');
        confirmation.className = 'aparencia-save-confirmation';
        confirmation.innerHTML = '✅ Tema salvo com sucesso!';
        confirmation.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 15px 20px;
            border-radius: var(--radius-md);
            box-shadow: 0 4px 16px var(--shadow-strong);
            z-index: 1000;
            font-weight: 600;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(confirmation);

        // Remover após 3 segundos
        setTimeout(() => {
            confirmation.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (confirmation.parentNode) {
                    confirmation.parentNode.removeChild(confirmation);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Exporta o tema atual como JSON
     */
    exportTheme() {
        try {
            const themeData = JSON.stringify(this.currentTheme, null, 2);
            const blob = new Blob([themeData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `tema-${this.currentTheme.nome.toLowerCase().replace(/\s+/g, '-')}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Erro ao exportar tema:', error);
            alert('Erro ao exportar tema.');
        }
    }

    /**
     * Importa tema de arquivo JSON
     */
    importTheme(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const themeData = JSON.parse(e.target.result);
                const sanitizedTheme = themeManager.sanitizeTheme(themeData);

                this.currentTheme = sanitizedTheme;
                this.loadCurrentTheme();
                themeManager.applyTheme(this.currentTheme);

                alert(`Tema "${sanitizedTheme.nome}" importado com sucesso!`);
            } catch (error) {
                console.error('Erro ao importar tema:', error);
                alert('Erro ao importar tema. Verifique se o arquivo é válido.');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Inicializa o prompt para IA
     */
    initializePrompt() {
        const promptTextarea = document.getElementById('ai-prompt-text');
        if (promptTextarea) {
            promptTextarea.value = this.generatePrompt();
        }
    }

    /**
     * Gera o texto do prompt para IA
     */
    generatePrompt() {
        return `Você é um especialista em design de interfaces para sistemas hospitalares. Estou criando um tema de cores personalizado para um sistema de gestão de pacientes.

Por favor, faça perguntas sobre minhas preferências de cores e estilo visual. Baseie-se no seguinte esqueleto de variáveis CSS:

\`\`\`css
:root {
  /* ========== CORES PRINCIPAIS ========== */
  --bg: #f2f5f4;              /* Fundo geral */
  --card: #ffffff;            /* Cartões */
  --primary: #2f7d6d;         /* Cor primária */
  --primary-hover: #266758;   /* Primária (hover) */
  --secondary: #4a90a4;       /* Cor secundária */
  --secondary-hover: #3d7a8a; /* Secundária (hover) */
  --accent: #e6f2ef;          /* Destaque */
  --text: #263238;            /* Texto principal */
  --text-muted: #607d8b;      /* Texto secundário */
  
  /* ========== ESTADOS E FEEDBACK ========== */
  --success: #2e7d32;         /* Sucesso */
  --success-light: #c8e6c9;   /* Sucesso (claro) */
  --warning: #f57c00;         /* Aviso */
  --warning-light: #ffe0b2;   /* Aviso (claro) */
  --danger: #c62828;          /* Erro */
  --danger-light: #ffcdd2;    /* Erro (claro) */
  --info: #0277bd;            /* Informação */
  --info-light: #b3e5fc;      /* Informação (claro) */
  
  /* ========== TONS NEUTROS ========== */
  --border: #d0d7d5;          /* Bordas */
  --border-light: #e8edec;    /* Bordas claras */
}
\`\`\`

INSTRUÇÕES:
1. Faça perguntas sobre minhas preferências de cores (ex: cores favoritas, estilo profissional ou descontraído, preferência por cores claras ou escuras)
2. Após entender minhas preferências, retorne APENAS o bloco CSS com as variáveis :root atualizadas
3. Use apenas cores hexadecimais válidas (formato #RRGGBB)
4. Mantenha a estrutura e comentários do esqueleto acima
5. Retorne o CSS completo e válido, pronto para ser importado

Responda agora com perguntas sobre minhas preferências de cores:`;
    }

    /**
     * Copia o prompt para a área de transferência
     */
    copyPrompt() {
        const promptTextarea = document.getElementById('ai-prompt-text');
        if (promptTextarea) {
            promptTextarea.select();
            promptTextarea.setSelectionRange(0, 99999); // Para mobile
            
            try {
                document.execCommand('copy');
                this.showCopyConfirmation();
            } catch (err) {
                // Fallback para API moderna
                navigator.clipboard.writeText(promptTextarea.value).then(() => {
                    this.showCopyConfirmation();
                }).catch(() => {
                    alert('Erro ao copiar. Selecione o texto manualmente e pressione Ctrl+C');
                });
            }
        }
    }

    /**
     * Mostra confirmação de cópia
     */
    showCopyConfirmation() {
        const confirmation = document.createElement('div');
        confirmation.className = 'aparencia-copy-confirmation';
        confirmation.innerHTML = '✅ Prompt copiado para a área de transferência!';
        confirmation.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 15px 20px;
            border-radius: var(--radius-md);
            box-shadow: 0 4px 16px var(--shadow-strong);
            z-index: 1000;
            font-weight: 600;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(confirmation);

        setTimeout(() => {
            confirmation.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (confirmation.parentNode) {
                    confirmation.parentNode.removeChild(confirmation);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Configura listeners para importação
     */
    setupImportListeners() {
        const fileInput = document.getElementById('css-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileImport(file);
                }
            });
        }
    }

    /**
     * Alterna entre tabs de importação
     */
    switchImportTab(tab) {
        const fileTab = document.getElementById('import-file-tab');
        const textTab = document.getElementById('import-text-tab');
        const fileBtn = document.querySelector('.aparencia-tab-btn[onclick*="file"]');
        const textBtn = document.querySelector('.aparencia-tab-btn[onclick*="text"]');

        if (tab === 'file') {
            fileTab.classList.add('active');
            textTab.classList.remove('active');
            fileBtn.classList.add('active');
            textBtn.classList.remove('active');
        } else {
            textTab.classList.add('active');
            fileTab.classList.remove('active');
            textBtn.classList.add('active');
            fileBtn.classList.remove('active');
        }

        // Limpar mensagens de erro
        this.hideErrorMessages();
    }

    /**
     * Processa importação de arquivo
     */
    handleFileImport(file) {
        // Validar extensão
        if (!file.name.toLowerCase().endsWith('.css')) {
            this.showErrorMessage('file', 'Erro: Apenas arquivos .css são aceitos. Arquivo rejeitado: ' + file.name);
            return;
        }

        // Validar tipo MIME (se disponível)
        if (file.type && !file.type.includes('css') && !file.type.includes('text')) {
            this.showErrorMessage('file', 'Erro: Tipo de arquivo inválido. Apenas arquivos CSS são aceitos.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const cssText = e.target.result;
            this.processCSSImport(cssText);
        };
        reader.onerror = () => {
            this.showErrorMessage('file', 'Erro ao ler o arquivo. Tente novamente.');
        };
        reader.readAsText(file);
    }

    /**
     * Importa CSS e aplica ao tema
     */
    importCSS() {
        const fileInput = document.getElementById('css-file-input');
        const textInput = document.getElementById('css-text-input');
        
        let cssText = '';

        // Verificar qual tab está ativa
        const fileTab = document.getElementById('import-file-tab');
        if (fileTab.classList.contains('active')) {
            if (fileInput.files.length === 0) {
                this.showErrorMessage('file', 'Por favor, selecione um arquivo CSS.');
                return;
            }
            this.handleFileImport(fileInput.files[0]);
            return;
        } else {
            cssText = textInput.value.trim();
            if (!cssText) {
                this.showErrorMessage('text', 'Por favor, cole o CSS no campo de texto.');
                return;
            }
            this.processCSSImport(cssText);
        }
    }

    /**
     * Processa e valida CSS importado
     */
    async processCSSImport(cssText) {
        try {
            const validation = this.validateCSS(cssText);
            if (!validation.valid) {
                this.showErrorMessage('text', validation.error);
                return;
            }

            const variables = this.parseCSSVariables(cssText);
            if (Object.keys(variables).length === 0) {
                this.showErrorMessage('text', 'Erro: Nenhuma variável CSS válida encontrada no arquivo.');
                return;
            }

            let cssFilename = null;
            try {
                const response = await fetch('/api/tema/salvar_css', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ css: cssText })
                });

                const result = await response.json();
                if (result.success && result.filename) {
                    cssFilename = result.filename;
                    themeManager.setCookie('custom_css_filename', cssFilename, 365);
                } else {
                    console.warn('Aviso: Não foi possível salvar CSS no servidor:', result.message);
                }
            } catch (error) {
                console.warn('Aviso: Erro ao salvar CSS no servidor:', error);
                // Continuar mesmo se não conseguir salvar no servidor
            }

            // Aplicar ao tema atual
            const newTheme = {
                nome: this.currentTheme.nome || 'Tema Importado',
                cores: {}
            };

            // Manter variáveis existentes e atualizar com as importadas
            for (const [key, value] of Object.entries(this.currentTheme.cores)) {
                newTheme.cores[key] = variables[key] || value;
            }

            this.currentTheme = newTheme;
            this.originalTheme = JSON.parse(JSON.stringify(newTheme));
            themeManager.saveTheme(newTheme);
            themeManager.applyTheme(newTheme);
            this.fillFormFromTheme(newTheme);
            this.updateThemeStatus();

            if (cssFilename) {
                themeManager.loadCustomCSSFile(cssFilename);
            }

            this.showSuccessMessage('Tema importado e aplicado com sucesso! 🎨');

            const fileInput = document.getElementById('css-file-input');
            const textInput = document.getElementById('css-text-input');
            if (fileInput) fileInput.value = '';
            if (textInput) textInput.value = '';

        } catch (error) {
            console.error('Erro ao processar CSS:', error);
            this.showErrorMessage('text', 'Erro ao processar CSS: ' + error.message);
        }
    }


    /**
     * Valida estrutura CSS
     */
    validateCSS(cssText) {
        if (!cssText || typeof cssText !== 'string') {
            return { valid: false, error: 'CSS inválido: texto vazio ou formato incorreto.' };
        }

        // Verificar se contém :root
        if (!cssText.includes(':root')) {
            return { valid: false, error: 'Erro: O CSS deve conter um bloco :root { ... }' };
        }

        // Verificar se contém variáveis CSS
        if (!cssText.match(/--[\w-]+\s*:/)) {
            return { valid: false, error: 'Erro: Nenhuma variável CSS (--nome: valor) encontrada.' };
        }

        // Verificar se não é JavaScript
        if (cssText.includes('function') || cssText.includes('const ') || cssText.includes('let ') || cssText.includes('var ')) {
            return { valid: false, error: 'Erro: Arquivo JavaScript detectado. Apenas arquivos CSS são aceitos.' };
        }

        // Verificar se não é JSON
        if (cssText.trim().startsWith('{') && cssText.trim().endsWith('}') && !cssText.includes(':root')) {
            return { valid: false, error: 'Erro: Arquivo JSON detectado. Apenas arquivos CSS são aceitos.' };
        }

        return { valid: true };
    }

    /**
     * Extrai variáveis CSS do texto
     */
    parseCSSVariables(cssText) {
        const variables = {};
        
        // Extrair bloco :root
        const rootMatch = cssText.match(/:root\s*\{([^}]+)\}/);
        if (!rootMatch) {
            return variables;
        }

        const rootContent = rootMatch[1];
        
        // Extrair todas as variáveis CSS (--nome: valor;)
        const variableRegex = /--([\w-]+)\s*:\s*([^;]+);/g;
        let match;

        while ((match = variableRegex.exec(rootContent)) !== null) {
            const varName = `--${match[1]}`;
            let varValue = match[2].trim();

            // Remover comentários inline
            varValue = varValue.split('/*')[0].trim();

            // Validar se é cor hexadecimal
            if (/^#[0-9A-Fa-f]{6}$/.test(varValue)) {
                variables[varName] = varValue;
            }
        }

        return variables;
    }

    /**
     * Mostra mensagem de erro
     */
    showErrorMessage(type, message) {
        const errorElement = document.getElementById(`${type}-error-message`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    /**
     * Esconde mensagens de erro
     */
    hideErrorMessages() {
        const fileError = document.getElementById('file-error-message');
        const textError = document.getElementById('text-error-message');
        if (fileError) fileError.style.display = 'none';
        if (textError) textError.style.display = 'none';
    }

    /**
     * Mostra mensagem de sucesso
     */
    showSuccessMessage(message) {
        const confirmation = document.createElement('div');
        confirmation.className = 'aparencia-success-message';
        confirmation.innerHTML = `✅ ${message}`;
        confirmation.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 15px 20px;
            border-radius: var(--radius-md);
            box-shadow: 0 4px 16px var(--shadow-strong);
            z-index: 1000;
            font-weight: 600;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(confirmation);

        setTimeout(() => {
            confirmation.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (confirmation.parentNode) {
                    confirmation.parentNode.removeChild(confirmation);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Salva um tema na lista de temas salvos (localStorage)
     */
    saveThemeToList(theme) {
        try {
            const savedThemes = this.getSavedThemes();
            
            // Verificar se já existe um tema com o mesmo nome
            const existingIndex = savedThemes.findIndex(t => t.nome === theme.nome);
            
            const themeToSave = {
                ...theme,
                dataSalvamento: new Date().toISOString()
            };
            
            if (existingIndex >= 0) {
                // Atualizar tema existente
                savedThemes[existingIndex] = themeToSave;
            } else {
                // Adicionar novo tema
                savedThemes.push(themeToSave);
            }
            
            // Salvar no localStorage
            localStorage.setItem('temas_salvos', JSON.stringify(savedThemes));
            return true;
        } catch (error) {
            console.error('Erro ao salvar tema na lista:', error);
            return false;
        }
    }

    /**
     * Obtém todos os temas salvos do localStorage
     */
    getSavedThemes() {
        try {
            const saved = localStorage.getItem('temas_salvos');
            if (saved) {
                return JSON.parse(saved);
            }
            return [];
        } catch (error) {
            console.error('Erro ao obter temas salvos:', error);
            return [];
        }
    }

    /**
     * Carrega e exibe a lista de temas salvos
     */
    loadSavedThemes() {
        try {
            const temasSalvos = this.getSavedThemes();
            const listaContainer = document.getElementById('temas-salvos-lista');
            if (!listaContainer) return;

            const padraoHtml = `
                <div class="tema-salvo-item tema-salvo-padrao">
                    <div class="tema-salvo-info">
                        <span class="tema-salvo-nome">Padrão</span>
                        <span class="tema-salvo-data">Tema padrão do sistema (sempre disponível)</span>
                    </div>
                    <div class="tema-salvo-acoes">
                        <button class="btn-aplicar-tema" onclick="aparenciaPage.aplicarPadrao()">Aplicar</button>
                    </div>
                </div>`;

            if (temasSalvos.length === 0) {
                listaContainer.innerHTML = padraoHtml + '<div class="temas-salvos-vazio">Nenhum tema salvo ainda. Salve um tema para vê-lo aqui.</div>';
                return;
            }

            temasSalvos.sort((a, b) => {
                const dateA = new Date(a.dataSalvamento || 0);
                const dateB = new Date(b.dataSalvamento || 0);
                return dateB - dateA;
            });

            const listHtml = temasSalvos.map((tema, index) => {
                const dataFormatada = tema.dataSalvamento
                    ? new Date(tema.dataSalvamento).toLocaleDateString('pt-BR', {
                        day: '2-digit', month: '2-digit', year: 'numeric',
                        hour: '2-digit', minute: '2-digit'
                    })
                    : 'Data não disponível';
                return `
                    <div class="tema-salvo-item">
                        <div class="tema-salvo-info">
                            <span class="tema-salvo-nome">${(tema.nome || 'Tema sem nome').replace(/</g, '&lt;')}</span>
                            <span class="tema-salvo-data">Salvo em: ${dataFormatada}</span>
                        </div>
                        <div class="tema-salvo-acoes">
                            <button class="btn-aplicar-tema" onclick="aparenciaPage.aplicarTemaSalvo(${index})">Aplicar</button>
                        </div>
                    </div>`;
            }).join('');

            listaContainer.innerHTML = padraoHtml + listHtml;
        } catch (error) {
            console.error('Erro ao carregar temas salvos:', error);
        }
    }

    /**
     * Aplica um tema salvo
     */
    aplicarTemaSalvo(index) {
        try {
            let temasSalvos = this.getSavedThemes();
            
            // Ordenar da mesma forma que na listagem (mais recente primeiro),
            // para que o index passado corresponda ao item correto exibido na tela
            temasSalvos = [...temasSalvos].sort((a, b) => {
                const dateA = new Date(a.dataSalvamento || 0);
                const dateB = new Date(b.dataSalvamento || 0);
                return dateB - dateA;
            });
            
            if (index < 0 || index >= temasSalvos.length) {
                alert('Tema não encontrado.');
                return;
            }
            
            const tema = temasSalvos[index];
            
            // Aplicar o tema
            this.currentTheme = JSON.parse(JSON.stringify(tema));
            themeManager.applyTheme(this.currentTheme);
            themeManager.saveTheme(this.currentTheme);
            
            // Atualizar inputs (loadCurrentTheme usa getCurrentTheme, que devolve o tema sanitizado)
            this.loadCurrentTheme();
            this.updateThemeStatus();
            
            // Atualizar nome do tema no input
            const nameInput = document.getElementById('theme-name');
            if (nameInput) {
                nameInput.value = tema.nome;
            }
            
            alert(`Tema "${tema.nome}" aplicado com sucesso! 🎨`);
            
        } catch (error) {
            console.error('Erro ao aplicar tema salvo:', error);
            alert('Erro ao aplicar tema.');
        }
    }
}

// ========== CSS ADICIONAL PARA A PÁGINA ==========
const pageStyles = `
<style>
.aparencia-editor-section {
    background: var(--card);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    box-shadow: 0 8px 24px var(--shadow-strong);
    border: 2px solid var(--border-light);
}

.aparencia-theme-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-xxl);
    padding: var(--spacing-lg);
    background: var(--accent);
    border-radius: var(--radius-lg);
    border: 2px solid var(--border-light);
}

.aparencia-theme-name {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.aparencia-theme-name label {
    font-weight: 600;
    color: var(--text);
    font-size: 0.95rem;
}

.aparencia-theme-name input {
    padding: var(--spacing-md);
    border: 2px solid var(--border-light);
    border-radius: var(--radius-md);
    font-size: 1rem;
    color: var(--text);
    background: var(--card);
    transition: border-color var(--transition-fast);
    max-width: 300px;
}

.aparencia-theme-name input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--accent);
}

.aparencia-theme-status {
    text-align: right;
}

.aparencia-theme-status #theme-status {
    font-size: 0.95rem;
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    display: inline-block;
}

.aparencia-theme-status-custom {
    background: var(--success-light);
    color: var(--success);
    border: 1px solid var(--success);
}

.aparencia-theme-status-default {
    background: var(--info-light);
    color: var(--info);
    border: 1px solid var(--info);
}

.aparencia-editor-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-xxl);
}

.aparencia-color-panel {
    background: var(--card);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    border: 2px solid var(--border-light);
    box-shadow: 0 4px 16px var(--shadow);
}

.aparencia-color-panel h2 {
    color: var(--text);
    font-size: var(--font-size-h2);
    margin-bottom: var(--spacing-xl);
    text-align: center;
}

.aparencia-color-groups {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.aparencia-color-group h3 {
    color: var(--text);
    font-size: var(--font-size-h3);
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-sm);
    border-bottom: 2px solid var(--border-light);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.aparencia-color-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
}

.aparencia-color-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.aparencia-color-item label {
    font-weight: 500;
    color: var(--text);
    font-size: 0.9rem;
}

.aparencia-color-input-wrapper {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--card);
    border: 2px solid var(--border-light);
    border-radius: var(--radius-md);
    transition: border-color var(--transition-fast);
}

.aparencia-color-input-wrapper:focus-within {
    border-color: var(--primary);
}

.aparencia-color-input {
    width: 60px;
    height: 40px;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    background: none;
}

.aparencia-color-input::-webkit-color-swatch-wrapper {
    padding: 0;
}

.aparencia-color-input::-webkit-color-swatch {
    border: none;
    border-radius: var(--radius-sm);
}

.aparencia-color-value {
    font-family: monospace;
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 500;
    user-select: all;
}

.aparencia-actions {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-xl);
    border-top: 2px solid var(--border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.aparencia-actions-main {
    display: flex;
    gap: var(--spacing-md);
}

.aparencia-btn {
    padding: var(--spacing-md) var(--spacing-xl);
    border: none;
    border-radius: var(--radius-md);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.aparencia-btn-primary {
    background: var(--primary);
    color: white;
}

.aparencia-btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow-medium);
}

.aparencia-btn-secondary {
    background: var(--secondary);
    color: white;
}

.aparencia-btn-secondary:hover {
    background: var(--secondary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow-medium);
}

.aparencia-btn-cancel {
    background: var(--border);
    color: var(--text);
}

.aparencia-btn-cancel:hover {
    background: var(--border-light);
    transform: translateY(-1px);
}

.aparencia-preview-panel {
    background: var(--card);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    border: 2px solid var(--border-light);
    box-shadow: 0 4px 16px var(--shadow);
    position: sticky;
    top: 100px;
    height: fit-content;
}

.aparencia-preview-panel h2 {
    color: var(--text);
    font-size: var(--font-size-h3);
    margin-bottom: var(--spacing-lg);
    text-align: center;
}

.aparencia-preview-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.preview-card {
    background: var(--card);
    border: 2px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    box-shadow: 0 4px 16px var(--shadow);
}

.preview-card h4 {
    color: var(--text);
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: var(--spacing-md);
}

.preview-card p {
    color: var(--text-muted);
    margin-bottom: var(--spacing-lg);
    line-height: 1.5;
}

.preview-btn-primary,
.preview-btn-secondary {
    padding: var(--spacing-md) var(--spacing-lg);
    border: none;
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    margin-right: var(--spacing-md);
}

.preview-btn-primary {
    background: var(--primary);
    color: white;
}

.preview-btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
}

.preview-btn-secondary {
    background: var(--secondary);
    color: white;
}

.preview-btn-secondary:hover {
    background: var(--secondary-hover);
    transform: translateY(-1px);
}

.preview-alerts {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.preview-alert {
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    font-weight: 500;
}

.preview-alert-success {
    background: var(--success-light);
    color: var(--success);
    border: 1px solid var(--success);
}

.preview-alert-warning {
    background: var(--warning-light);
    color: var(--warning);
    border: 1px solid var(--warning);
}

.preview-alert-danger {
    background: var(--danger-light);
    color: var(--danger);
    border: 1px solid var(--danger);
}

.preview-topbar {
    background: var(--primary);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin-top: var(--spacing-lg);
}

.preview-topbar-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.preview-topbar-logo {
    display: flex;
    gap: var(--spacing-md);
    font-size: 0.9rem;
    color: white;
}

.preview-topbar-logo span {
    background: rgba(255, 255, 255, 0.1);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-sm);
}

/* Confirmação de salvamento */
.aparencia-save-confirmation {
    position: fixed;
    top: 100px;
    right: 20px;
    background: var(--success);
    color: white;
    padding: 15px 20px;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 16px var(--shadow-strong);
    z-index: 1000;
    font-weight: 600;
    animation: slideInRight 0.3s ease-out;
}

/* Animações */
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

/* Responsividade */
@media (max-width: 1200px) {
    .aparencia-editor-grid {
        grid-template-columns: 1fr;
    }

    .aparencia-preview-panel {
        position: static;
    }
}

@media (max-width: 768px) {
    .aparencia-editor-section {
        padding: var(--spacing-lg);
    }

    .aparencia-color-grid {
        grid-template-columns: 1fr;
    }

    .aparencia-actions {
        flex-direction: column;
        gap: var(--spacing-md);
    }

    .aparencia-actions-main {
        width: 100%;
        justify-content: space-between;
    }

    .aparencia-btn {
        flex: 1;
        justify-content: center;
    }

    .aparencia-theme-info {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: stretch;
    }

    .aparencia-theme-name input {
        max-width: none;
    }
}

/* ========== SEÇÕES PROMPT E IMPORT ========== */

.aparencia-ai-section,
.aparencia-import-section {
    background: var(--card);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    margin-top: var(--spacing-xxl);
    box-shadow: 0 8px 24px var(--shadow-strong);
    border: 2px solid var(--border-light);
}

.aparencia-section-header {
    margin-bottom: var(--spacing-xl);
    text-align: center;
}

.aparencia-section-header h2 {
    color: var(--text);
    font-size: var(--font-size-h2);
    margin-bottom: var(--spacing-md);
    font-weight: 600;
}

.aparencia-section-header p {
    color: var(--text-muted);
    font-size: var(--font-size-large);
}

.aparencia-prompt-container {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.aparencia-prompt-instructions {
    background: var(--accent);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    border: 2px solid var(--border-light);
}

.aparencia-prompt-instructions h3 {
    color: var(--text);
    font-size: var(--font-size-h3);
    margin-bottom: var(--spacing-lg);
    font-weight: 600;
}

.aparencia-prompt-instructions ol {
    color: var(--text);
    line-height: 1.8;
    padding-left: var(--spacing-xl);
}

.aparencia-prompt-instructions li {
    margin-bottom: var(--spacing-sm);
}

.aparencia-prompt-instructions strong {
    color: var(--primary);
    font-weight: 600;
}

.aparencia-prompt-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.aparencia-prompt-textarea {
    width: 100%;
    min-height: 300px;
    padding: var(--spacing-lg);
    border: 2px solid var(--border-light);
    border-radius: var(--radius-md);
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--text);
    background: var(--card);
    resize: vertical;
    transition: border-color var(--transition-fast);
}

.aparencia-prompt-textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--accent);
}

.aparencia-import-container {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.aparencia-import-tabs {
    display: flex;
    gap: var(--spacing-sm);
    border-bottom: 2px solid var(--border-light);
}

.aparencia-tab-btn {
    padding: var(--spacing-md) var(--spacing-xl);
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all var(--transition-fast);
    position: relative;
    top: 2px;
}

.aparencia-tab-btn:hover {
    color: var(--text);
    background: var(--accent);
}

.aparencia-tab-btn.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
    font-weight: 600;
}

.aparencia-import-tab-content {
    display: none;
    padding: var(--spacing-lg);
    background: var(--accent);
    border-radius: var(--radius-md);
    border: 2px solid var(--border-light);
}

.aparencia-import-tab-content.active {
    display: block;
}

.aparencia-file-input-wrapper {
    position: relative;
}

.aparencia-file-input {
    position: absolute;
    width: 0.1px;
    height: 0.1px;
    opacity: 0;
    overflow: hidden;
    z-index: -1;
}

.aparencia-file-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xxl);
    border: 3px dashed var(--border);
    border-radius: var(--radius-md);
    background: var(--card);
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: center;
    gap: var(--spacing-sm);
}

.aparencia-file-label:hover {
    border-color: var(--primary);
    background: var(--accent);
}

.aparencia-file-label span {
    color: var(--text);
    font-size: 1.1rem;
    font-weight: 600;
}

.aparencia-file-label small {
    color: var(--text-muted);
    font-size: 0.9rem;
}

.aparencia-css-textarea {
    width: 100%;
    min-height: 250px;
    padding: var(--spacing-lg);
    border: 2px solid var(--border-light);
    border-radius: var(--radius-md);
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--text);
    background: var(--card);
    resize: vertical;
    transition: border-color var(--transition-fast);
}

.aparencia-css-textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--accent);
}

.aparencia-css-textarea::placeholder {
    color: var(--text-muted);
}

.aparencia-error-message {
    margin-top: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--danger-light);
    color: var(--danger);
    border: 1px solid var(--danger);
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    font-weight: 500;
}

.aparencia-import-actions {
    display: flex;
    justify-content: center;
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-light);
}

.aparencia-copy-confirmation,
.aparencia-success-message {
    position: fixed;
    top: 100px;
    right: 20px;
    background: var(--success);
    color: white;
    padding: 15px 20px;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 16px var(--shadow-strong);
    z-index: 1000;
    font-weight: 600;
    animation: slideInRight 0.3s ease-out;
}

@media (max-width: 768px) {
    .aparencia-ai-section,
    .aparencia-import-section {
        padding: var(--spacing-lg);
    }

    .aparencia-prompt-instructions {
        padding: var(--spacing-lg);
    }

    .aparencia-prompt-textarea,
    .aparencia-css-textarea {
        min-height: 200px;
        font-size: 0.85rem;
    }

    .aparencia-import-tabs {
        flex-direction: column;
    }

    .aparencia-tab-btn {
        width: 100%;
        text-align: center;
    }
}
</style>
`;

// Inserir estilos na página
document.head.insertAdjacentHTML('beforeend', pageStyles);

// ========== INSTÂNCIA GLOBAL ==========
const aparenciaPage = new AparenciaPage();
window.AparenciaPage = AparenciaPage;
window.aparenciaPage = aparenciaPage;

// Inicializar após DOM e tema (loadAndApplyTheme, loadCustomCSSFromCookie) estarem prontos
function runAparenciaInit() {
    aparenciaPage.init();
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAparenciaInit);
} else {
    runAparenciaInit();
}