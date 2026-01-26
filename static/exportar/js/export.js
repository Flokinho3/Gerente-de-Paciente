// Lógica de exportação
import { state } from './state.js';
import { dom } from './dom.js';
import { mostrarStatus } from './ui.js';
import { construirFiltrosParams } from './utils.js';

export async function exportarDados(formato) {
    try {
        mostrarStatus('Preparando arquivo para download...', 'loading');
        dom.exportBtn.disabled = true;

        const params = construirFiltrosParams();
        const query = params.toString();
        const endpoint = `/api/exportar/${formato}${query ? `?${query}` : ''}`;

        const response = await fetch(endpoint, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Erro ao exportar dados');
        }

        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `pacientes_${new Date().toISOString().split('T')[0]}.${formato === 'excel' ? 'xlsx' : formato === 'word' ? 'docx' : 'txt'}`;
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?([^";]+)"?/);
            if (match) {
                filename = match[1];
            }
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        mostrarStatus(`✅ Arquivo exportado com sucesso! (${filename})`, 'success');
        setTimeout(() => {
            dom.exportBtn.disabled = false;
        }, 2000);
    } catch (error) {
        console.error('Erro ao exportar:', error);
        mostrarStatus(`❌ Erro ao exportar dados: ${error.message}`, 'error');
        dom.exportBtn.disabled = false;
    }
}
