/**
 * Gerenciador de Temas - Sistema de Paleta de Cores Personalizável
 * Permite salvar e carregar temas personalizados via cookie
 */

class ThemeManager {
    constructor() {
        this.COOKIE_NAME = 'tema_personalizado';
        this.CUSTOM_STYLE_ID = 'custom-theme';
        this.defaultTheme = this.getDefaultTheme();
        this.init();
    }

    /**
     * Inicializa o gerenciador de temas
     */
    init() {
        // Criar tag <style> para CSS customizado se não existir
        if (!document.getElementById(this.CUSTOM_STYLE_ID)) {
            const style = document.createElement('style');
            style.id = this.CUSTOM_STYLE_ID;
            style.type = 'text/css';
            document.head.appendChild(style);
        }
    }

    /**
     * Retorna os valores padrão de cores do variables.css
     */
    getDefaultTheme() {
        return {
            nome: "Padrão Hospitalar",
            cores: {
                "--bg": "#f2f5f4",
                "--card": "#ffffff",
                "--primary": "#2f7d6d",
                "--primary-hover": "#266758",
                "--secondary": "#4a90a4",
                "--secondary-hover": "#3d7a8a",
                "--accent": "#e6f2ef",
                "--text": "#263238",
                "--text-muted": "#607d8b",
                "--success": "#2e7d32",
                "--success-light": "#c8e6c9",
                "--warning": "#f57c00",
                "--warning-light": "#ffe0b2",
                "--danger": "#c62828",
                "--danger-light": "#ffcdd2",
                "--info": "#0277bd",
                "--info-light": "#b3e5fc",
                "--border": "#d0d7d5",
                "--border-light": "#e8edec"
            }
        };
    }

    /**
     * Valida se uma cor é um hexadecimal válido
     */
    isValidHexColor(color) {
        return /^#[0-9A-Fa-f]{6}$/.test(color);
    }

    /**
     * Sanitiza e valida um tema completo
     */
    sanitizeTheme(theme) {
        if (!theme || typeof theme !== 'object') {
            return this.defaultTheme;
        }

        const sanitized = {
            nome: (typeof theme.nome === 'string' && theme.nome.length > 0) ? theme.nome : "Tema Personalizado",
            cores: {}
        };

        // Validar cada cor do tema
        for (const [key, value] of Object.entries(this.defaultTheme.cores)) {
            if (theme.cores && theme.cores[key] && this.isValidHexColor(theme.cores[key])) {
                sanitized.cores[key] = theme.cores[key];
            } else {
                sanitized.cores[key] = value; // Usar valor padrão se inválido
            }
        }

        return sanitized;
    }

    /**
     * Aplica um tema CSS dinamicamente
     */
    applyTheme(theme) {
        try {
            const sanitizedTheme = this.sanitizeTheme(theme);
            const styleElement = document.getElementById(this.CUSTOM_STYLE_ID);

            if (!styleElement) {
                console.error('Elemento de estilo customizado não encontrado');
                return false;
            }

            // Criar CSS customizado
            let css = ':root {\n';
            for (const [variable, color] of Object.entries(sanitizedTheme.cores)) {
                css += `  ${variable}: ${color};\n`;
            }
            css += '}';

            styleElement.textContent = css;
            return true;
        } catch (error) {
            console.error('Erro ao aplicar tema:', error);
            return false;
        }
    }

    /**
     * Salva tema no cookie
     */
    saveTheme(theme) {
        try {
            const sanitizedTheme = this.sanitizeTheme(theme);
            const themeJson = JSON.stringify(sanitizedTheme);

            // Verificar tamanho do cookie (limite aproximado de 4KB)
            if (themeJson.length > 4000) {
                console.error('Tema muito grande para salvar no cookie');
                return false;
            }

            this.setCookie(this.COOKIE_NAME, themeJson, 365); // Salvar por 1 ano
            return true;
        } catch (error) {
            console.error('Erro ao salvar tema:', error);
            return false;
        }
    }

    /**
     * Carrega tema do cookie
     */
    loadTheme() {
        try {
            const themeJson = this.getCookie(this.COOKIE_NAME);
            if (!themeJson) {
                return null; // Nenhum tema salvo
            }

            const theme = JSON.parse(themeJson);
            return this.sanitizeTheme(theme);
        } catch (error) {
            console.error('Erro ao carregar tema:', error);
            return null; // Retornar null para usar padrão
        }
    }

    /**
     * Remove tema personalizado e volta ao padrão
     */
    resetToDefault() {
        try {
            this.deleteCookie(this.COOKIE_NAME);
            this.applyTheme(this.defaultTheme);
            return true;
        } catch (error) {
            console.error('Erro ao resetar tema:', error);
            return false;
        }
    }

    /**
     * Carrega e aplica tema salvo, ou usa padrão se erro
     */
    loadAndApplyTheme() {
        try {
            const savedTheme = this.loadTheme();
            if (savedTheme) {
                return this.applyTheme(savedTheme);
            } else {
                // Aplicar tema padrão se nenhum tema salvo
                return this.applyTheme(this.defaultTheme);
            }
        } catch (error) {
            console.error('Erro ao carregar e aplicar tema:', error);
            // Aplicar tema padrão em caso de erro
            return this.applyTheme(this.defaultTheme);
        }
    }

    // ========== FUNÇÕES UTILITÁRIAS DE COOKIE ==========

    /**
     * Define um cookie
     */
    setCookie(nome, valor, dias = 365) {
        try {
            const data = new Date();
            data.setTime(data.getTime() + (dias * 24 * 60 * 60 * 1000));
            const expires = `expires=${data.toUTCString()}`;
            document.cookie = `${nome}=${encodeURIComponent(valor)};${expires};path=/;SameSite=Strict`;
        } catch (error) {
            console.error('Erro ao definir cookie:', error);
        }
    }

    /**
     * Obtém um cookie
     */
    getCookie(nome) {
        try {
            const nomeCompleto = `${nome}=`;
            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.indexOf(nomeCompleto) === 0) {
                    return decodeURIComponent(cookie.substring(nomeCompleto.length));
                }
            }
            return null;
        } catch (error) {
            console.error('Erro ao obter cookie:', error);
            return null;
        }
    }

    /**
     * Remove um cookie
     */
    deleteCookie(nome) {
        try {
            document.cookie = `${nome}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;SameSite=Strict`;
        } catch (error) {
            console.error('Erro ao remover cookie:', error);
        }
    }

    // ========== MÉTODOS PÚBLICOS ==========

    /**
     * Obtém o tema atual (salvo ou padrão)
     */
    getCurrentTheme() {
        return this.loadTheme() || this.defaultTheme;
    }

    /**
     * Verifica se há um tema personalizado salvo
     */
    hasCustomTheme() {
        return this.getCookie(this.COOKIE_NAME) !== null;
    }

    /**
     * Obtém informações sobre o tema atual
     */
    getThemeInfo() {
        const theme = this.getCurrentTheme();
        return {
            nome: theme.nome,
            isCustom: this.hasCustomTheme(),
            coresCount: Object.keys(theme.cores).length
        };
    }

    /**
     * Carrega CSS customizado do cookie ao iniciar
     */
    loadCustomCSSFromCookie() {
        try {
            const cssFilename = this.getCookie('custom_css_filename');
            if (cssFilename) {
                this.loadCustomCSSFile(cssFilename);
            }
        } catch (error) {
            console.error('Erro ao carregar CSS customizado do cookie:', error);
        }
    }

    /**
     * Carrega arquivo CSS customizado do servidor
     */
    loadCustomCSSFile(filename) {
        try {
            // Verificar se já existe um link para CSS customizado
            let customLink = document.getElementById('custom-css-link');
            
            if (!customLink) {
                // Criar novo link
                customLink = document.createElement('link');
                customLink.id = 'custom-css-link';
                customLink.rel = 'stylesheet';
                customLink.type = 'text/css';
                document.head.appendChild(customLink);
            }
            
            // Atualizar href com timestamp para evitar cache
            customLink.href = `/static/css/${filename}?t=${Date.now()}`;
        } catch (error) {
            console.error('Erro ao carregar arquivo CSS customizado:', error);
        }
    }
}

// ========== INSTÂNCIA GLOBAL ==========
const themeManager = new ThemeManager();

// ========== FUNÇÕES GLOBAIS PARA BACKWARD COMPATIBILITY ==========
window.ThemeManager = ThemeManager;
window.themeManager = themeManager;

// ========== CARREGAR CSS CUSTOMIZADO AO INICIAR ==========
// Carregar CSS customizado quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        themeManager.loadCustomCSSFromCookie();
    });
} else {
    // DOM já está pronto
    themeManager.loadCustomCSSFromCookie();
}