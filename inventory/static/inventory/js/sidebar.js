

document.addEventListener("DOMContentLoaded", function() {
    const toggleBtn = document.getElementById('toggle-btn');
    const sidebar = document.getElementById('sidebar');

    
    toggleBtn.addEventListener('click', () => {
        
        sidebar.classList.toggle('collapsed');
    });


    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu a');

    menuLinks.forEach(link => { 
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
    });
});