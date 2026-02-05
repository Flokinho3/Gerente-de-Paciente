document.addEventListener('DOMContentLoaded', () => {
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/common/css/subprocessos.css';
    document.head.appendChild(link);

    // Create Container
    const container = document.createElement('div');
    container.id = 'subprocessos-container';
    document.body.appendChild(container);

    let lastEventId = 0;
    // Initial fetch to get latest ID but maybe not show old events, or show last 2?
    // Let's start with 0 to show recent history on page load

    // Icon mapping
    const icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'working': '🔄'
    };

    function createToast(event) {
        const item = document.createElement('div');
        item.className = `subprocesso-item type-${event.type}`;

        const icon = icons[event.type] || 'ℹ️';

        item.innerHTML = `
            <span class="subprocesso-icon">${icon}</span>
            <span class="subprocesso-message">${event.message}</span>
        `;

        // Add to container
        container.appendChild(item);

        // Auto remove after 5 seconds, unless it's an error
        const duration = event.type === 'error' ? 8000 : 5000;

        setTimeout(() => {
            item.classList.add('removing');
            setTimeout(() => item.remove(), 300);
        }, duration);
    }

    async function pollEvents() {
        try {
            const response = await fetch(`/api/events/poll?since=${lastEventId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.events.length > 0) {
                    data.events.forEach(event => {
                        // Only show if we haven't seen it (though API filters by ID)
                        if (event.id > lastEventId) {
                            createToast(event);
                            lastEventId = event.id;
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error polling background events:', error);
        }
    }

    // Poll every 2 seconds
    setInterval(pollEvents, 2000);

    // Initial poll
    pollEvents();
});
