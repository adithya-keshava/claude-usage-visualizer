/**
 * Chart Maximize Functionality
 * Allows users to view charts in fullscreen mode for better readability
 */

(function() {
    'use strict';

    // Create modal overlay on page load
    function createModal() {
        const modal = document.createElement('div');
        modal.id = 'chart-modal';
        modal.className = 'chart-modal';
        modal.innerHTML = `
            <div class="chart-modal-content">
                <div class="chart-modal-header">
                    <h3 id="chart-modal-title">Chart View</h3>
                    <button class="chart-modal-close" aria-label="Close fullscreen view">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="chart-modal-body">
                    <canvas id="chart-modal-canvas"></canvas>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Close on click outside or close button
        modal.addEventListener('click', function(e) {
            if (e.target === modal || e.target.closest('.chart-modal-close')) {
                closeModal();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    // Add maximize buttons to all charts
    function addMaximizeButtons() {
        const chartWrappers = document.querySelectorAll('.chart-wrapper');

        chartWrappers.forEach(wrapper => {
            const canvas = wrapper.querySelector('canvas');
            if (!canvas) return;

            // Check if button already exists
            if (wrapper.querySelector('.chart-maximize-btn')) return;

            const button = document.createElement('button');
            button.className = 'chart-maximize-btn';
            button.setAttribute('aria-label', 'Maximize chart');
            button.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                </svg>
            `;

            button.addEventListener('click', function() {
                maximizeChart(canvas);
            });

            wrapper.appendChild(button);
        });
    }

    // Maximize a chart
    function maximizeChart(originalCanvas) {
        const modal = document.getElementById('chart-modal');
        const modalCanvas = document.getElementById('chart-modal-canvas');
        const modalTitle = document.getElementById('chart-modal-title');

        if (!modal || !modalCanvas) return;

        // Get the chart instance from the original canvas
        const chartId = originalCanvas.id;
        const chartInstance = window.chartInstances?.[chartId];

        if (!chartInstance) {
            console.warn('No chart instance found for:', chartId);
            return;
        }

        // Set modal title from chart title
        const chartTitle = chartInstance.options?.plugins?.title?.text || 'Chart View';
        modalTitle.textContent = chartTitle;

        // Clone the chart configuration
        const config = {
            type: chartInstance.config.type,
            data: JSON.parse(JSON.stringify(chartInstance.config.data)),
            options: JSON.parse(JSON.stringify(chartInstance.config.options))
        };

        // Adjust options for fullscreen
        if (config.options) {
            config.options.maintainAspectRatio = false;
            config.options.responsive = true;
        }

        // Destroy existing modal chart if any
        if (window.modalChartInstance) {
            window.modalChartInstance.destroy();
        }

        // Create new chart in modal
        const ctx = modalCanvas.getContext('2d');
        window.modalChartInstance = new Chart(ctx, config);

        // Show modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Close modal
    function closeModal() {
        const modal = document.getElementById('chart-modal');
        if (!modal) return;

        modal.classList.remove('active');
        document.body.style.overflow = '';

        // Destroy modal chart
        if (window.modalChartInstance) {
            window.modalChartInstance.destroy();
            window.modalChartInstance = null;
        }
    }

    // Initialize on page load
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                createModal();
                // Delay button addition to ensure charts are rendered
                // Try multiple times to catch charts that load asynchronously
                setTimeout(addMaximizeButtons, 500);
                setTimeout(addMaximizeButtons, 1500);
                setTimeout(addMaximizeButtons, 3000);
            });
        } else {
            createModal();
            // Delay button addition to ensure charts are rendered
            setTimeout(addMaximizeButtons, 500);
            setTimeout(addMaximizeButtons, 1500);
            setTimeout(addMaximizeButtons, 3000);
        }
    }

    // Expose close function globally for external use
    window.closeChartModal = closeModal;

    // Initialize
    init();
})();