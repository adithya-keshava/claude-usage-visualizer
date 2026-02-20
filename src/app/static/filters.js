/**
 * Date range and project filtering for charts
 * Pattern: Similar to timezone.js with localStorage persistence
 */

// Debounce helper (prevent excessive API calls)
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Initialize filters on page load
async function initFilters() {
  // Fetch metadata (date range, projects)
  let metadata;
  try {
    metadata = await fetch('/api/metadata').then((r) => r.json());
  } catch (error) {
    console.error('Failed to fetch metadata:', error);
    return;
  }

  // Set date input min/max
  const startInput = document.getElementById('start-date');
  const endInput = document.getElementById('end-date');

  if (startInput && endInput) {
    startInput.min = metadata.oldest_date || '';
    startInput.max = metadata.newest_date || '';
    endInput.min = metadata.oldest_date || '';
    endInput.max = metadata.newest_date || '';

    // Load saved filters from localStorage
    const savedFilters = JSON.parse(
      localStorage.getItem('chartFilters') || '{}'
    );
    if (savedFilters.start_date) startInput.value = savedFilters.start_date;
    if (savedFilters.end_date) endInput.value = savedFilters.end_date;

    // Populate project dropdown
    const projectSelect = document.getElementById('project-filter');
    if (projectSelect && metadata.projects) {
      metadata.projects.forEach((project) => {
        const option = document.createElement('option');
        option.value = project.encoded_path;
        option.textContent = `${project.display_name} (${project.session_count} sessions)`;
        projectSelect.appendChild(option);
      });

      if (savedFilters.project) {
        projectSelect.value = savedFilters.project;
      }
    }

    // Add event listeners with debouncing
    const debouncedApply = debounce(applyFilters, 300);
    startInput.addEventListener('change', debouncedApply);
    endInput.addEventListener('change', debouncedApply);
    if (projectSelect) {
      projectSelect.addEventListener('change', debouncedApply);
    }

    // Reset button
    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn) {
      resetBtn.addEventListener('click', resetFilters);
    }

    // Apply saved filters on load
    if (savedFilters.start_date || savedFilters.end_date || savedFilters.project) {
      applyFilters();
    }
  }
}

// Apply current filter state to all charts
async function applyFilters() {
  const startDate = document.getElementById('start-date')?.value;
  const endDate = document.getElementById('end-date')?.value;
  const project = document.getElementById('project-filter')?.value;

  // Save to localStorage
  localStorage.setItem(
    'chartFilters',
    JSON.stringify({
      start_date: startDate,
      end_date: endDate,
      project: project,
    })
  );

  // Build query params
  const params = new URLSearchParams();
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  if (project) params.set('project', project);

  // Update all charts
  await Promise.all([
    updateChart('dailyActivityChart', `/api/activity?${params}`),
    updateChart('dailyCostChart', `/api/daily-cost?${params}`),
    updateChart('modelCostChart', `/api/model-split?${params}`),
    updateChart('hourlyChart', `/api/hourly-distribution?${params}`),
    updateChart('projectCostChart', `/api/project-cost?${params}`),
  ]);

  // Check if hourly granularity is active
  try {
    const activityData = await fetch(`/api/activity?${params}`).then((r) =>
      r.json()
    );
    const indicator = document.getElementById('granularity-indicator');
    if (indicator) {
      if (activityData.granularity === 'hourly') {
        indicator.style.display = 'block';
        indicator.querySelector('.badge').textContent = '📊 Showing Hourly Data';
      } else {
        indicator.style.display = 'none';
      }
    }
  } catch (error) {
    console.error('Failed to check granularity:', error);
  }
}

// Update a specific chart with new data
async function updateChart(chartId, apiUrl) {
  const canvas = document.getElementById(chartId);
  if (!canvas) return;

  try {
    const data = await fetch(apiUrl).then((r) => r.json());

    // Get existing chart instance
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
      // Update existing chart data
      existingChart.data.labels = data.labels;
      existingChart.data.datasets = data.datasets;
      existingChart.update('active'); // Smooth animation
    }
  } catch (error) {
    console.error(`Failed to update ${chartId}:`, error);
  }
}

// Reset all filters to default (all time, all projects)
function resetFilters() {
  const startInput = document.getElementById('start-date');
  const endInput = document.getElementById('end-date');
  const projectSelect = document.getElementById('project-filter');

  if (startInput) startInput.value = '';
  if (endInput) endInput.value = '';
  if (projectSelect) projectSelect.value = '';

  localStorage.removeItem('chartFilters');

  // Reload page to reset charts
  window.location.reload();
}

// Handle timezone format changes
document.addEventListener('timeformatchange', (event) => {
  const newFormat = event.detail.format;

  // Get current filters
  const startDate = document.getElementById('start-date')?.value;
  const endDate = document.getElementById('end-date')?.value;
  const project = document.getElementById('project-filter')?.value;

  // Refresh charts with new timezone format
  // The API will return the same data, but the display format will change
  // through the data-timestamp attributes on elements
  applyFilters();
});

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFilters);
} else {
  initFilters();
}
