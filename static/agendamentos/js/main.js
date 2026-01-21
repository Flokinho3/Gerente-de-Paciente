// Sistema de Gestão de Agendamentos - Orquestrador Principal

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Carregar pacientes
    if (window.carregarTodosPacientes) {
        window.carregarTodosPacientes();
    }
    
    // Configurar eventos
    if (window.configurarEventosAgendamentos) {
        window.configurarEventosAgendamentos();
    }
    configurarNavegacao();
    if (window.configurarPesquisaPaciente) {
        window.configurarPesquisaPaciente();
    }
    if (window.configurarConfiguracoes) {
        window.configurarConfiguracoes();
    }
    if (window.configurarModalConfirmarAtendimento) {
        window.configurarModalConfirmarAtendimento();
    }
    
    // Verificar qual view está ativa e carregar dados apropriados
    const viewAtiva = document.querySelector('.view.ativa');
    if (viewAtiva) {
        const viewId = viewAtiva.id;
        if (viewId === 'calendario') {
            if (window.carregarCalendario) {
                window.carregarCalendario();
            }
        } else if (viewId === 'agenda') {
            if (window.carregarAgendamentos) {
                window.carregarAgendamentos();
            }
        }
    }
});

// Configurar navegação entre views
function configurarNavegacao() {
    const links = document.querySelectorAll('[data-view]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = link.getAttribute('data-view');
            mostrarView(viewId);
        });
    });
}

// Mostrar view específica
function mostrarView(viewId) {
    // Esconder todas as views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('ativa');
    });
    
    // Mostrar view selecionada
    const view = document.getElementById(viewId);
    if (view) {
        view.classList.add('ativa');
        
        // Carregar dados específicos da view
        if (viewId === 'agenda') {
            if (window.carregarAgendamentos) {
                window.carregarAgendamentos();
            }
        } else if (viewId === 'calendario') {
            if (window.carregarCalendario) {
                window.carregarCalendario();
            }
        } else if (viewId === 'historico') {
            if (window.carregarHistorico) {
                window.carregarHistorico();
            }
        }
    }
}

// Exportar função para uso global
window.mostrarView = mostrarView;
