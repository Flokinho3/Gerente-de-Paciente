// Funções de API
import { state } from './state.js';
import { dom } from './dom.js';

export async function carregarTotalPacientes() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();

        if (data.success) {
            state.totalPacientes = data.total || 0;
            dom.totalPacientesSpan.textContent = state.totalPacientes;
        } else {
            dom.totalPacientesSpan.textContent = 'Erro ao carregar';
        }
    } catch (error) {
        console.error('Erro ao carregar total de pacientes:', error);
        dom.totalPacientesSpan.textContent = 'Erro';
    }
}

export async function carregarUnidades() {
    try {
        const response = await fetch('/api/unidades_saude');
        const data = await response.json();

        if (data.success && data.unidades) {
            state.unidadesDisponiveis = data.unidades;
        }
    } catch (error) {
        console.error('Erro ao carregar unidades:', error);
    }
    return Promise.resolve();
}

export async function carregarCamposDisponiveis() {
    try {
        const response = await fetch('/api/campos_disponiveis');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();

        if (data.success && data.campos) {
            state.camposDisponiveis = data.campos;
        }
    } catch (error) {
        console.error('Erro ao carregar campos disponíveis:', error);
    }
    return Promise.resolve();
}

export async function carregarTodosPacientes() {
    try {
        const response = await fetch('/api/pacientes');
        const data = await response.json();
        
        if (data.success && data.pacientes) {
            return data.pacientes;
        }
        return [];
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
        return [];
    }
}
