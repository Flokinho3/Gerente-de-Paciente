// Módulo de criação de gráficos

function criarGraficoPizza(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

function criarGraficoBarra(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pacientes',
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Função para criar um gráfico de linha com dados temporais
function criarGraficoTemporal(filtro, chartId, containerId, container, unidadeSaude = null) {
    fetch(`/api/indicadores/temporais/${filtro}`)
        .then(response => response.json())
        .then(dataTemporal => {
            if (!dataTemporal || !dataTemporal.datas || dataTemporal.datas.length === 0) {
                alert('Não há dados temporais disponíveis para este indicador.');
                return;
            }
            
            const indicadorInfo = window.getIndicadorData(filtro);
            const title = indicadorInfo ? indicadorInfo.title : filtro;
            
            const datas = dataTemporal.datas;
            const valores = dataTemporal.valores;
            
            let datasets = [];
            
            if (filtro === 'vacinas_completas') {
                datasets = [
                    {
                        label: 'Completo',
                        data: datas.map(data => valores[data]['Completo'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Incompleto',
                        data: datas.map(data => valores[data]['Incompleto'] || 0),
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não avaliado',
                        data: datas.map(data => valores[data]['Não avaliado'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'consultas_pre_natal') {
                datasets = [
                    {
                        label: '≥ 6 consultas',
                        data: datas.map(data => valores[data]['≥ 6 consultas'] || 0),
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: '< 6 consultas',
                        data: datas.map(data => valores[data]['< 6 consultas'] || 0),
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'inicio_pre_natal_antes_12s') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'plano_parto') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'participou_grupos') {
                datasets = [
                    {
                        label: 'Participou',
                        data: datas.map(data => valores[data]['Participou'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não participou',
                        data: datas.map(data => valores[data]['Não participou'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'possui_bolsa_familia') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            } else if (filtro === 'tem_vacina_covid') {
                datasets = [
                    {
                        label: 'Sim',
                        data: datas.map(data => valores[data]['Sim'] || 0),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Não',
                        data: datas.map(data => valores[data]['Não'] || 0),
                        borderColor: '#9E9E9E',
                        backgroundColor: 'rgba(158, 158, 158, 0.1)',
                        tension: 0.4
                    }
                ];
            }
            
            const chartConfig = {
                type: 'line',
                data: {
                    labels: datas.map(data => {
                        const [ano, mes, dia] = data.split('-');
                        return `${dia}/${mes}/${ano}`;
                    }),
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            };
            
            const ctx = document.getElementById(containerId);
            const chart = new Chart(ctx, chartConfig);
            
            window.comparacaoCharts?.set(chartId, chart);
        })
        .catch(error => {
            console.error('Erro ao carregar dados temporais:', error);
            alert('Erro ao carregar dados temporais para o gráfico de linha.');
        });
}

// Exportar funções
window.criarGraficoPizza = criarGraficoPizza;
window.criarGraficoBarra = criarGraficoBarra;
window.criarGraficoTemporal = criarGraficoTemporal;
