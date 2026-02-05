document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('syncRateChart').getContext('2d');
    const uploadVal = document.getElementById('upload-val');
    const downloadVal = document.getElementById('download-val');

    const initialData = {
        labels: Array(20).fill(''),
        datasets: [
            {
                label: 'Upload (itens/s)',
                data: Array(20).fill(0),
                borderColor: '#2ecc71',
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            },
            {
                label: 'Download (itens/s)',
                data: Array(20).fill(0),
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }
        ]
    };

    const chart = new Chart(ctx, {
        type: 'line',
        data: initialData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0 // Desativa animação para performance em real-time
            },
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 10
                },
                x: {
                    display: false
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    function updateChart() {
        fetch('/api/firebase/sync/stats')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const upRate = data.upload_rate || 0;
                    const downRate = data.download_rate || 0;

                    // Update datasets
                    chart.data.datasets[0].data.push(upRate);
                    chart.data.datasets[0].data.shift();

                    chart.data.datasets[1].data.push(downRate);
                    chart.data.datasets[1].data.shift();

                    chart.update();

                    // Update text badges
                    if (uploadVal) uploadVal.textContent = upRate.toFixed(1);
                    if (downloadVal) downloadVal.textContent = downRate.toFixed(1);
                }
            })
            .catch(e => console.error("Erro chart", e));
    }

    // Update every 1 second
    setInterval(updateChart, 1000);
});
