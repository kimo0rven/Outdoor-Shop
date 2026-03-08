document.addEventListener('DOMContentLoaded', function() {

    const searchInput = document.getElementById('variant-search') || document.getElementById('table-search');
    

    const tableBody = document.querySelector('.inventory-table tbody');

    if (searchInput && tableBody) {
        searchInput.addEventListener('input', function() {
            const filter = searchInput.value.toLowerCase();
            const rows = tableBody.querySelectorAll('tr');

            rows.forEach(row => {
                if (row.id === 'no-results-row' || row.cells.length < 2) return;

                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(filter) ? "" : "none";
            });


            const visibleRows = Array.from(rows).filter(r => r.style.display !== "none" && r.id !== 'no-results-row');
            let existingMsg = document.getElementById('no-results-row');

            if (visibleRows.length === 0 && filter !== "") {
                if (!existingMsg) {
                    const msg = document.createElement('tr');
                    msg.id = 'no-results-row';
                    msg.innerHTML = `<td colspan="7" class="no-result">No results for "${filter}"</td>`;
                    tableBody.appendChild(msg);
                }
            } else if (existingMsg) {
                existingMsg.remove();
            }
        });
    } else {
        console.error("Search input or Table body not found for Units page.");
    }
});