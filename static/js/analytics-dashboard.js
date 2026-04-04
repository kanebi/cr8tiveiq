/**
 * Analytics Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply width to breakdown fill bars from data attributes
    const breakdownFills = document.querySelectorAll('.breakdown-fill[data-width]');
    breakdownFills.forEach(function(element) {
        const width = element.getAttribute('data-width');
        element.style.width = width + '%';
    });
});
