import { updateProgress } from './wizard.js';

// Função para mostrar/esconder campos de detalhes do início do pré-natal
let tentativasInicioPreNatal = 0;
const MAX_TENTATIVAS_INICIO_PRE_NATAL = 10;

export function toggleCampoInicioPreNatalDetalhes() {
    const radiosInicioPreNatal = document.querySelectorAll('input[name="inicio_pre_natal_antes_12s"]');
    const detalhesGroup = document.getElementById('inicio-pre-natal-detalhes-group');
    const semanasInput = document.getElementById('inicio_pre_natal_semanas');
    const observacaoInput = document.getElementById('inicio_pre_natal_observacao');
    
    // Se os elementos não existem, tentar novamente apenas se ainda não excedemos o limite
    if (!detalhesGroup || !semanasInput) {
        tentativasInicioPreNatal++;
        if (tentativasInicioPreNatal < MAX_TENTATIVAS_INICIO_PRE_NATAL) {
            setTimeout(toggleCampoInicioPreNatalDetalhes, 100);
        } else {
            // Limite atingido, parar tentativas
            tentativasInicioPreNatal = 0;
        }
        return;
    }
    
    // Resetar contador quando encontrar os elementos
    tentativasInicioPreNatal = 0;
    
    // Verificar se estamos no step 3 antes de manipular os elementos
    const step3Element = document.querySelector('.wizard-step[data-step="3"]');
    if (!step3Element || !step3Element.classList.contains('active')) {
        // Não estamos no step 3, esconder os campos se estiverem visíveis
        if (detalhesGroup.style.display !== 'none') {
            detalhesGroup.style.display = 'none';
            semanasInput.removeAttribute('required');
        }
        return;
    }
    
    // Verificar qual radio está selecionado
    const inicioPreNatalSelecionado = Array.from(radiosInicioPreNatal).find(radio => radio.checked);
    const valorSelecionado = inicioPreNatalSelecionado ? inicioPreNatalSelecionado.value : null;
    
    if (valorSelecionado === 'true') {
        // Mostrar os campos usando múltiplas estratégias
        detalhesGroup.style.display = 'block';
        detalhesGroup.style.visibility = 'visible';
        detalhesGroup.style.opacity = '1';
        detalhesGroup.style.marginTop = '20px';
        detalhesGroup.removeAttribute('hidden');
        detalhesGroup.classList.remove('hidden');
        
        // Forçar exibição com !important via setProperty
        detalhesGroup.style.setProperty('display', 'block', 'important');
        
        semanasInput.setAttribute('required', 'required');
        semanasInput.setAttribute('data-original-required', 'true');
        semanasInput.removeAttribute('disabled');
        
        if (observacaoInput) {
            observacaoInput.removeAttribute('disabled');
        }
        
        // Focar no campo quando aparecer
        setTimeout(() => {
            if (semanasInput.offsetParent !== null) {
                semanasInput.focus();
                semanasInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            // Atualizar validação após mostrar o campo
            updateProgress();
        }, 200);
    } else {
        // Esconder os campos
        detalhesGroup.style.display = 'none';
        detalhesGroup.style.visibility = 'hidden';
        detalhesGroup.style.opacity = '0';
        semanasInput.removeAttribute('required');
        semanasInput.value = '';
        if (observacaoInput) {
            observacaoInput.value = '';
        }
        // Atualizar validação imediatamente ao esconder
        updateProgress();
    }
}

// Função para mostrar/esconder campo de problema de estratificação
export function toggleCampoEstratificacaoProblema() {
    // Buscar elementos de forma mais robusta - buscar em todo o documento
    const radiosEstratificacao = document.querySelectorAll('input[name="estratificacao"]');
    const problemaGroup = document.getElementById('estratificacao-problema-group');
    const problemaInput = document.getElementById('estratificacao_problema');
    
    if (!problemaGroup || !problemaInput) {
        console.warn('Elementos de estratificação não encontrados! Tentando novamente...');
        // Tentar novamente após um pequeno delay
        setTimeout(toggleCampoEstratificacaoProblema, 100);
        return;
    }
    
    // Verificar qual radio está selecionado
    const estratificacaoSelecionada = Array.from(radiosEstratificacao).find(radio => radio.checked);
    const valorSelecionado = estratificacaoSelecionada ? estratificacaoSelecionada.value : null;
    
    if (valorSelecionado === 'true') {
        // Mostrar o campo usando múltiplas estratégias
        problemaGroup.style.display = 'block';
        problemaGroup.style.visibility = 'visible';
        problemaGroup.style.opacity = '1';
        problemaGroup.style.marginTop = '20px';
        problemaGroup.removeAttribute('hidden');
        problemaGroup.classList.remove('hidden');
        
        // Forçar exibição com !important via setProperty
        problemaGroup.style.setProperty('display', 'block', 'important');
        
        problemaInput.removeAttribute('disabled');
        
        // Focar no campo quando aparecer
        setTimeout(() => {
            if (problemaInput.offsetParent !== null) {
                problemaInput.focus();
                problemaInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            // Atualizar validação após mostrar o campo
            updateProgress();
        }, 200);
    } else {
        // Esconder o campo
        problemaGroup.style.display = 'none';
        problemaGroup.style.visibility = 'hidden';
        problemaGroup.style.opacity = '0';
        problemaInput.removeAttribute('required');
        problemaInput.value = '';
        // Atualizar validação imediatamente ao esconder
        updateProgress();
    }
}

// Função para verificar e mostrar alerta quando ambos kits forem selecionados
export function verificarKitsSelecionados() {
    const kitTipoCheckboxes = document.querySelectorAll('input[name="kit_tipo"]:checked');
    const alerta = document.getElementById('kit-alerta');
    
    if (alerta) {
        if (kitTipoCheckboxes.length === 2) {
            // Ambos selecionados - mostrar alerta
            alerta.style.display = 'block';
        } else {
            // Menos de 2 selecionados - esconder alerta
            alerta.style.display = 'none';
        }
    }
}

// Função para mostrar/esconder campo de tipo de KIT
export function toggleCampoKitTipo() {
    const radiosKit = document.querySelectorAll('input[name="ganhou_kit"]');
    const kitTipoGroup = document.getElementById('kit-tipo-group');
    
    if (!kitTipoGroup) {
        console.warn('Elementos de KIT não encontrados! Tentando novamente...');
        setTimeout(toggleCampoKitTipo, 100);
        return;
    }
    
    // Verificar qual radio está selecionado
    const kitSelecionado = Array.from(radiosKit).find(radio => radio.checked);
    const valorSelecionado = kitSelecionado ? kitSelecionado.value : null;
    
    if (valorSelecionado === 'true') {
        // Mostrar o campo usando múltiplas estratégias
        kitTipoGroup.style.display = 'block';
        kitTipoGroup.style.visibility = 'visible';
        kitTipoGroup.style.opacity = '1';
        kitTipoGroup.style.marginTop = '20px';
        kitTipoGroup.removeAttribute('hidden');
        kitTipoGroup.classList.remove('hidden');
        
        // Forçar exibição com !important via setProperty
        kitTipoGroup.style.setProperty('display', 'block', 'important');
        
        // Remover disabled dos checkboxes
        const kitTipoCheckboxes = kitTipoGroup.querySelectorAll('input[name="kit_tipo"]');
        kitTipoCheckboxes.forEach(checkbox => {
            checkbox.removeAttribute('disabled');
        });
        
        // Configurar event listeners para verificar quando ambos são selecionados
        kitTipoCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', verificarKitsSelecionados);
        });
        
        // Verificar estado inicial
        verificarKitsSelecionados();
        
        // Atualizar validação após mostrar o campo
        setTimeout(() => {
            updateProgress();
        }, 200);
    } else {
        // Esconder o campo
        kitTipoGroup.style.display = 'none';
        kitTipoGroup.style.visibility = 'hidden';
        kitTipoGroup.style.opacity = '0';
        
        // Limpar valores e esconder alerta
        const kitTipoCheckboxes = kitTipoGroup.querySelectorAll('input[name="kit_tipo"]');
        kitTipoCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        
        const alerta = document.getElementById('kit-alerta');
        if (alerta) {
            alerta.style.display = 'none';
        }
        
        // Atualizar validação imediatamente ao esconder
        updateProgress();
    }
}

// Função para mostrar/esconder campo de data quando já ganhou a criança
export function toggleCampoDataGanhou() {
    const radiosGanhou = document.querySelectorAll('input[name="ja_ganhou_crianca"]');
    const dataGroup = document.getElementById('data-ganhou-group');
    const dataInput = document.getElementById('data_ganhou_crianca');
    
    if (!dataGroup || !dataInput) {
        setTimeout(toggleCampoDataGanhou, 100);
        return;
    }
    
    const ganhouSelecionado = Array.from(radiosGanhou).find(radio => radio.checked);
    const valorSelecionado = ganhouSelecionado ? ganhouSelecionado.value : null;
    
    if (valorSelecionado === 'true') {
        dataGroup.style.display = 'block';
        dataGroup.style.visibility = 'visible';
        dataGroup.style.opacity = '1';
        dataGroup.style.marginTop = '20px';
        dataGroup.removeAttribute('hidden');
        dataGroup.classList.remove('hidden');
        dataGroup.style.setProperty('display', 'block', 'important');
        
        dataInput.removeAttribute('disabled');
        
        setTimeout(() => {
            if (dataInput.offsetParent !== null) {
                dataInput.focus();
                dataInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            updateProgress();
        }, 200);
    } else {
        dataGroup.style.display = 'none';
        dataGroup.style.visibility = 'hidden';
        dataGroup.style.opacity = '0';
        dataInput.value = '';
        updateProgress();
    }
}

// Função para mostrar/esconder campo de gêneros quando há filhos
export function toggleCampoGenerosFilhos() {
    const quantidadeInput = document.getElementById('quantidade_filhos');
    const generosGroup = document.getElementById('generos-filhos-group');
    const generosInput = document.getElementById('generos_filhos');
    
    if (!quantidadeInput || !generosGroup || !generosInput) {
        setTimeout(toggleCampoGenerosFilhos, 100);
        return;
    }
    
    const quantidade = parseInt(quantidadeInput.value) || 0;
    
    if (quantidade > 0) {
        generosGroup.style.display = 'block';
        generosGroup.style.visibility = 'visible';
        generosGroup.style.opacity = '1';
        generosGroup.style.marginTop = '20px';
        generosGroup.removeAttribute('hidden');
        generosGroup.classList.remove('hidden');
        generosGroup.style.setProperty('display', 'block', 'important');
        
        generosInput.removeAttribute('disabled');
        
        setTimeout(() => {
            updateProgress();
        }, 200);
    } else {
        generosGroup.style.display = 'none';
        generosGroup.style.visibility = 'hidden';
        generosGroup.style.opacity = '0';
        generosInput.value = '';
        updateProgress();
    }
}

// Função para mostrar/esconder campo "outros" no método preventivo
export function toggleCampoMetodoOutros() {
    const metodoSelect = document.getElementById('metodo_preventivo');
    const outrosGroup = document.getElementById('metodo-outros-group');
    const outrosInput = document.getElementById('metodo_preventivo_outros');
    
    if (!metodoSelect || !outrosGroup || !outrosInput) {
        setTimeout(toggleCampoMetodoOutros, 100);
        return;
    }
    
    const valorSelecionado = metodoSelect.value;
    
    if (valorSelecionado === 'Outros') {
        outrosGroup.style.display = 'block';
        outrosGroup.style.visibility = 'visible';
        outrosGroup.style.opacity = '1';
        outrosGroup.style.marginTop = '20px';
        outrosGroup.removeAttribute('hidden');
        outrosGroup.classList.remove('hidden');
        outrosGroup.style.setProperty('display', 'block', 'important');
        
        outrosInput.removeAttribute('disabled');
        
        setTimeout(() => {
            if (outrosInput.offsetParent !== null) {
                outrosInput.focus();
                outrosInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            updateProgress();
        }, 200);
    } else {
        outrosGroup.style.display = 'none';
        outrosGroup.style.visibility = 'hidden';
        outrosGroup.style.opacity = '0';
        outrosInput.value = '';
        updateProgress();
    }
}