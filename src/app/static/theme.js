// Theme toggle logic with localStorage persistence

const THEME_KEY = "claude-visualizer-theme";
const DARK_THEME = "dark";
const LIGHT_THEME = "light";

function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? DARK_THEME : LIGHT_THEME;
}

function initTheme() {
    // Get stored theme or use system preference
    let theme = localStorage.getItem(THEME_KEY);
    if (!theme) {
        theme = getSystemTheme();
    }
    applyTheme(theme);
}

function applyTheme(theme, dispatchEvent = false) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);

    // Dispatch custom event only when toggling (not on initial load)
    if (dispatchEvent) {
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: theme }
        }));
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute("data-theme");
    const newTheme = current === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    applyTheme(newTheme, true); // Dispatch event on toggle
}

// Set up theme toggle button
document.addEventListener("DOMContentLoaded", function () {
    initTheme();

    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", toggleTheme);
    }
});

// Watch for system theme changes
if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem(THEME_KEY)) {
            applyTheme(e.matches ? DARK_THEME : LIGHT_THEME);
        }
    });
}

// Helper for Chart.js colors based on current theme
function getChartColors() {
    const theme = document.documentElement.getAttribute("data-theme");
    const isDark = theme === DARK_THEME;

    return {
        textColor: isDark ? "#e6edf3" : "#1f2937",
        gridColor: isDark ? "#30363d" : "#d1d5db",
        opusColor: isDark ? "#a855f7" : "#9333ea",
        sonnetColor: isDark ? "#3b82f6" : "#2563eb",
        haikuColor: isDark ? "#10b981" : "#059669",
    };
}