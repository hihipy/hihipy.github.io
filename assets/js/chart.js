// Site-level override of Blowfish's themes/blowfish/assets/js/chart.js
// Adds theme-aware text + grid colors via CSS variables that swap automatically
// when the user toggles light/dark mode. Original Blowfish defaults preserved.

function css(name) {
  return "rgb(" + getComputedStyle(document.documentElement).getPropertyValue(name) + ")";
}

Chart.defaults.font.size = 14;
Chart.defaults.backgroundColor = css("--color-primary-300");
Chart.defaults.elements.point.borderColor = css("--color-primary-400");
Chart.defaults.elements.bar.borderColor = css("--color-primary-500");
Chart.defaults.elements.bar.borderWidth = 1;
Chart.defaults.elements.line.borderColor = css("--color-primary-400");
Chart.defaults.elements.arc.backgroundColor = css("--color-primary-200");
Chart.defaults.elements.arc.borderColor = css("--color-primary-500");
Chart.defaults.elements.arc.borderWidth = 1;

// Site override additions: theme-aware text and grid colors.
// --color-neutral-700 is dark gray in light mode, light gray in dark mode.
// --color-neutral-200 gives subtle gridlines in both themes.
Chart.defaults.color = css("--color-neutral-700");
Chart.defaults.borderColor = css("--color-neutral-300");
if (Chart.defaults.scale && Chart.defaults.scale.grid) {
  Chart.defaults.scale.grid.color = css("--color-neutral-200");
}
