document.addEventListener("DOMContentLoaded", function() {
    const searchTrigger = document.getElementById('search-trigger');
    const searchOverlay = document.getElementById('search-overlay');
    const cancelBtn = document.getElementById('cancel-search-btn');
    const expandedInput = document.getElementById('expanded-search-input');

    searchTrigger.addEventListener('click', function(e) {
        searchOverlay.classList.add('active');
        
        setTimeout(() => {
            expandedInput.focus();
        }, 100);
    });

    cancelBtn.addEventListener('click', function() {
        searchOverlay.classList.remove('active');
        expandedInput.value = '';
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            searchOverlay.classList.remove('active');
        }
    });
});