/**
 * HTMX configuration and helpers
 * Handles loading indicators and HTMX behavior
 */

// Configure HTMX defaults
document.addEventListener('htmx:configRequest', (detail) => {
    // Add any custom headers if needed
});

// Show loading indicator
document.addEventListener('htmx:xhr:loadstart', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.add('htmx-loading');
    }
});

// Hide loading indicator
document.addEventListener('htmx:xhr:loadend', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.remove('htmx-loading');
    }
});

// Handle HTMX errors
document.addEventListener('htmx:responseError', (event) => {
    console.error('HTMX request failed:', event.detail);
    // Could show user-facing error message here
});
