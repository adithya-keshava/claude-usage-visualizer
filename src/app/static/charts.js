/**
 * Chart.js initialization and configuration
 * Handles chart creation, theme colors, and timezone conversion
 */

// Chart.js default font
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

// Get model colors from CSS variables
function getModelColor(modelId, opacity = 0.8) {
    const opacityInt = Math.round(opacity * 255).toString(16).padStart(2, '0');
    const colors = {
        'claude-opus-4-6': `#a855f7${opacityInt}`,
        'claude-opus-4-5-20251101': `#9333ea${opacityInt}`,
        'claude-sonnet-4-5-20250929': `#3b82f6${opacityInt}`,
        'claude-haiku-4-5-20251001': `#10b981${opacityInt}`,
    };
    return colors[modelId] || `#6366f1${opacityInt}`;
}

// Get theme colors
function getChartThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        textColor: isDark ? '#e5e7eb' : '#1f2937',
        gridColor: isDark ? '#374151' : '#e5e7eb',
        backgroundColor: isDark ? '#1f2937' : '#ffffff',
    };
}

// Format chart labels based on current timezone format
function formatChartLabels(labels) {
    const timeFormat = document.documentElement.getAttribute('data-time-format') || 'UTC';

    return labels.map(label => {
        // Check if label looks like a timestamp (contains T or is ISO date)
        if (label && (label.includes('T') || label.match(/^\d{4}-\d{2}-\d{2}$/))) {
            // For ISO format timestamps, convert to selected format
            if (window.formatTimestamp) {
                return window.formatTimestamp(label, timeFormat);
            }
        }
        return label;
    });
}

// Create daily activity chart (messages + sessions over time)
function initDailyActivityChart() {
    const canvas = document.getElementById('dailyActivityChart');
    if (!canvas) return;

    // Use /api/activity endpoint which auto-selects hourly vs daily granularity
    fetch('/api/activity')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: theme.textColor,
                                padding: 15,
                            },
                        },
                        title: {
                            display: true,
                            text: data.granularity === 'hourly' ? 'Hourly Activity' : 'Daily Activity',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Messages',
                                color: theme.textColor,
                            },
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Sessions',
                                color: theme.textColor,
                            },
                            ticks: { color: theme.textColor },
                            grid: { drawOnChartArea: false },
                        },
                        x: {
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                    },
                },
            });

            // Store chart instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['dailyActivityChart'] = chart;
        })
        .catch(err => console.error('Failed to load daily activity chart:', err));
}

// Create model cost split doughnut chart
function initModelCostChart() {
    const canvas = document.getElementById('modelCostChart');
    if (!canvas) return;

    fetch('/api/model-split')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: theme.textColor,
                                padding: 15,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Model Cost Distribution',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `$${value.toFixed(2)} (${percentage}%)`;
                                }
                            }
                        }
                    },
                },
            });

            // Store chart instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['modelCostChart'] = chart;
        })
        .catch(err => console.error('Failed to load model cost chart:', err));
}

// Create hourly distribution bar chart
function initHourlyChart() {
    const canvas = document.getElementById('hourlyChart');
    if (!canvas) return;

    fetch('/api/hourly-distribution')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: theme.textColor,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Session Starts by Hour (UTC)',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Number of Sessions',
                                color: theme.textColor,
                            },
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                        x: {
                            ticks: {
                                color: theme.textColor,
                                maxRotation: 45,
                                minRotation: 0,
                            },
                            grid: { color: theme.gridColor },
                        },
                    },
                },
            });

            // Store chart instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['hourlyChart'] = chart;
        })
        .catch(err => console.error('Failed to load hourly chart:', err));
}

// Create daily cost trend stacked area chart
function initDailyCostChart() {
    const canvas = document.getElementById('dailyCostChart');
    if (!canvas) return;

    fetch('/api/daily-cost')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        filler: {
                            propagate: true,
                        },
                        legend: {
                            labels: {
                                color: theme.textColor,
                                padding: 15,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Daily Cost Trend by Model',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                    },
                    scales: {
                        y: {
                            stacked: true,
                            title: {
                                display: true,
                                text: 'Cost (USD)',
                                color: theme.textColor,
                            },
                            ticks: {
                                color: theme.textColor,
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            },
                            grid: { color: theme.gridColor },
                        },
                        x: {
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                    },
                },
            });

            // Store chart instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['dailyCostChart'] = chart;
        })
        .catch(err => console.error('Failed to load daily cost chart:', err));
}

// Create project cost horizontal bar chart
function initProjectCostChart() {
    const canvas = document.getElementById('projectCostChart');
    if (!canvas) return;

    fetch('/api/project-cost')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: theme.textColor,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Cost per Project',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Cost (USD)',
                                color: theme.textColor,
                            },
                            ticks: {
                                color: theme.textColor,
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            },
                            grid: { color: theme.gridColor },
                        },
                        y: {
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                    },
                },
            });

            // Store chart instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['projectCostChart'] = chart;
        })
        .catch(err => console.error('Failed to load project cost chart:', err));
}

// Create project-specific activity chart
function initProjectActivityChart() {
    const canvas = document.getElementById('projectActivityChart');
    if (!canvas) return;

    // Extract encoded path from URL: /projects/{encoded_path}
    const pathMatch = window.location.pathname.match(/\/projects\/([^\/]+)$/);
    if (!pathMatch) return;

    const encodedPath = pathMatch[1];

    fetch(`/api/projects/${encodedPath}/activity`)
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: theme.textColor,
                                padding: 15,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Project Activity Over Time',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Messages',
                                color: theme.textColor,
                            },
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Sessions',
                                color: theme.textColor,
                            },
                            ticks: { color: theme.textColor },
                            grid: { drawOnChartArea: false },
                        },
                        x: {
                            ticks: { color: theme.textColor },
                            grid: { color: theme.gridColor },
                        },
                    },
                },
            });
        })
        .catch(err => console.error('Failed to load project activity chart:', err));
}

// Create project-specific cost breakdown chart
function initProjectModelCostChart() {
    const canvas = document.getElementById('projectModelCostChart');
    if (!canvas) return;

    // Extract encoded path from URL
    const pathMatch = window.location.pathname.match(/\/projects\/([^\/]+)$/);
    if (!pathMatch) return;

    const encodedPath = pathMatch[1];

    fetch(`/api/projects/${encodedPath}/cost-breakdown`)
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: theme.textColor,
                                padding: 15,
                            },
                        },
                        title: {
                            display: true,
                            text: 'Model Cost Distribution',
                            color: theme.textColor,
                            padding: 20,
                            font: { size: 14, weight: 'bold' },
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `$${value.toFixed(2)} (${percentage}%)`;
                                }
                            }
                        }
                    },
                },
            });
        })
        .catch(err => console.error('Failed to load project cost chart:', err));
}

// Initialize all charts when DOM is ready
function initAllCharts() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllCharts);
        return;
    }

    initDailyActivityChart();
    initModelCostChart();
    initHourlyChart();
    initDailyCostChart();
    initProjectCostChart();
    initProjectActivityChart();
    initProjectModelCostChart();
}

// Initialize on page load
initAllCharts();

// Reinitialize charts when theme changes
document.addEventListener('themechange', () => {
    // For now, a simple page reload works best
    // In future, could update chart colors dynamically
    setTimeout(() => window.location.reload(), 200);
});

// Update timestamps when timezone format changes
document.addEventListener('timeformatchange', (event) => {
    const newFormat = event.detail.format;

    // Re-convert all timestamps on the page to new format
    if (window.convertTimestamps) {
        window.convertTimestamps(newFormat);
    }

    // Update chart labels with new timezone format
    if (window.chartInstances) {
        Object.values(window.chartInstances).forEach(chart => {
            if (chart && chart.data && chart.data.labels) {
                // Format labels based on new timezone
                const formattedLabels = formatChartLabels(chart.data.labels);
                chart.data.labels = formattedLabels;
                chart.update();
            }
        });
    }
});
