/**
 * Timezone & Time Format Toggle
 * Cycles through: UTC 24h → Local 24h → UTC 12h → Local 12h
 * Stores preference in localStorage
 * Updates all timestamp displays on the page
 */

// Time format modes in order
const TIME_FORMATS = ['UTC', 'Local', 'UTC-12h', 'Local-12h'];

// Initialize timezone on page load
function initializeTimeFormat() {
  const savedFormat = localStorage.getItem('timeFormat') || 'UTC';
  document.documentElement.setAttribute('data-time-format', savedFormat);
  updateTimeFormatDropdown(savedFormat);
  convertTimestamps(savedFormat);
}

// Update dropdown to show current format
function updateTimeFormatDropdown(format) {
  const dropdown = document.getElementById('timezone-select');
  if (dropdown) {
    dropdown.value = format;
  }
}

// Convert all timestamps on the page
function convertTimestamps(format) {
  const timestamps = document.querySelectorAll('[data-timestamp]');
  timestamps.forEach((element) => {
    const isoString = element.getAttribute('data-timestamp');
    if (isoString) {
      const formatted = formatTimestamp(isoString, format);
      element.textContent = formatted;
    }
  });
}

// Format timestamp based on time format preference
function formatTimestamp(isoString, format) {
  try {
    const date = new Date(isoString);
    const isLocal = format.includes('Local');
    const is12h = format.includes('12h');

    // Get date components
    let year, month, day, hours, minutes, seconds;

    if (isLocal) {
      // Local timezone
      year = date.getFullYear();
      month = String(date.getMonth() + 1).padStart(2, '0');
      day = String(date.getDate()).padStart(2, '0');
      hours = date.getHours();
      minutes = String(date.getMinutes()).padStart(2, '0');
      seconds = String(date.getSeconds()).padStart(2, '0');
    } else {
      // UTC timezone
      year = date.getUTCFullYear();
      month = String(date.getUTCMonth() + 1).padStart(2, '0');
      day = String(date.getUTCDate()).padStart(2, '0');
      hours = date.getUTCHours();
      minutes = String(date.getUTCMinutes()).padStart(2, '0');
      seconds = String(date.getUTCSeconds()).padStart(2, '0');
    }

    // Format hours based on 12h or 24h preference
    let timeStr;
    if (is12h) {
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const hours12 = hours % 12 || 12;
      const hours12Str = String(hours12).padStart(2, '0');
      timeStr = `${hours12Str}:${minutes}:${seconds} ${ampm}`;
    } else {
      const hours24Str = String(hours).padStart(2, '0');
      timeStr = `${hours24Str}:${minutes}:${seconds}`;
    }

    return `${year}-${month}-${day} ${timeStr}`;
  } catch (e) {
    return isoString;
  }
}

// Format date only (for date ranges and tables)
function formatDate(isoString, format) {
  try {
    const date = new Date(isoString);
    const isLocal = format.includes('Local');

    let year, month, day;

    if (isLocal) {
      year = date.getFullYear();
      month = String(date.getMonth() + 1).padStart(2, '0');
      day = String(date.getDate()).padStart(2, '0');
    } else {
      year = date.getUTCFullYear();
      month = String(date.getUTCMonth() + 1).padStart(2, '0');
      day = String(date.getUTCDate()).padStart(2, '0');
    }

    return `${year}-${month}-${day}`;
  } catch (e) {
    return isoString.substring(0, 10);
  }
}

// Change time format when dropdown selection changes
function changeTimeFormat(newFormat) {
  // Save preference
  localStorage.setItem('timeFormat', newFormat);

  // Update attribute and dropdown
  document.documentElement.setAttribute('data-time-format', newFormat);
  updateTimeFormatDropdown(newFormat);

  // Convert all timestamps
  convertTimestamps(newFormat);

  // Dispatch event so other components (like charts) can react
  const event = new CustomEvent('timeformatchange', { detail: { format: newFormat } });
  document.dispatchEvent(event);
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Initialize on page load
  initializeTimeFormat();

  // Set up change handler for dropdown
  const dropdown = document.getElementById('timezone-select');
  if (dropdown) {
    dropdown.addEventListener('change', (e) => {
      changeTimeFormat(e.target.value);
    });
  }
});

// Export functions for use in templates (if needed)
window.formatTimestamp = formatTimestamp;
window.formatDate = formatDate;
window.getTimeFormat = () =>
  document.documentElement.getAttribute('data-time-format') || 'UTC';
