document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('table-search');
    const tableBody = document.querySelector('.inventory-table tbody');
    const rows = tableBody.querySelectorAll('tr');

    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const query = searchInput.value.toLowerCase();

            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                
                if (text.includes(query)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });


            const visibleRows = Array.from(rows).filter(r => r.style.display !== "none");
        });
    }

    searchInput.addEventListener('keyup', function() {
        const filter = searchInput.value.toLowerCase();
        let resultsFound = false;

        for (let i = 0; i < rows.length; i++) {
            if (rows[i].cells.length < 2) continue;

            const textContent = rows[i].textContent.toLowerCase();
            
            if (textContent.includes(filter)) {
                rows[i].style.display = "";
                resultsFound = true;
            } else {
                rows[i].style.display = "none";
            }
        }

        const existingNoResults = document.getElementById('no-results-row');
        if (!resultsFound && filter !== "") {
            if (!existingNoResults) {
                const noResultRow = document.createElement('tr');
                noResultRow.id = 'no-results-row';
                noResultRow.innerHTML = `<td colspan="7" class="no-result">No matches found for "${filter}"</td>`;
                tableBody.appendChild(noResultRow);
            }
        } else if (existingNoResults) {
            existingNoResults.remove();
        }
    });
});