document.addEventListener("DOMContentLoaded", function() {

    const editListingBtns = document.querySelectorAll('.edit-listing-btn');
    const editListingPanel = document.getElementById('edit-listing-panel');
    if (editListingBtns.length > 0 && editListingPanel) {
        editListingBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('edit-id').value = this.dataset.id;
                document.getElementById('edit-brand').value = this.dataset.brand;
                document.getElementById('edit-name').value = this.dataset.name;
                document.getElementById('edit-category').value = this.dataset.category;
                document.getElementById('edit-vendor').value = this.dataset.vendor;
                document.getElementById('edit-price').value = this.dataset.price;
                document.getElementById('edit-mpn').value = this.dataset.mpn;
                document.getElementById('edit-tags').value = this.dataset.tags;
                document.getElementById('edit-status').value = this.dataset.status;
                document.getElementById('edit-desc').value = this.dataset.desc;
                editListingPanel.classList.add('open');
            });
        });
    }

    const editVariantBtns = document.querySelectorAll('.edit-variant-btn');
    const editVariantPanel = document.getElementById('edit-variant-panel');

    if (editVariantBtns.length > 0 && editVariantPanel) {
        editVariantBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('edit-variant-id').value = this.dataset.id;
                document.getElementById('edit-variant-listing').value = this.dataset.listing;
                document.getElementById('edit-variant-name').value = this.dataset.name;
                document.getElementById('edit-variant-sku').value = this.dataset.sku;
                document.getElementById('edit-variant-price').value = this.dataset.price;
                document.getElementById('edit-variant-qty').value = this.dataset.qty;
                document.getElementById('edit-variant-status').value = this.dataset.status;

                const imageUrl = this.getAttribute('data-image');
                const imageDisplay = document.getElementById('current-variant-image-display');

                if (imageDisplay) {
                    if (imageUrl && imageUrl !== "None" && imageUrl !== "") {
                        imageDisplay.innerHTML = `<img src="${imageUrl}" style="max-width: 100%; height: 120px; object-fit: contain; border-radius: 8px;">`;
                    } else {
                        imageDisplay.innerHTML = `<span style="color: #a0aec0;">Using Parent Listing Thumbnail</span>`;
                    }
                }

                const container = document.getElementById('edit-attributes-container');
                if (container) {
                    container.innerHTML = '';
                    const row = this.closest('tr');
                    const attributes = row.querySelectorAll('.attr-tag');
                    attributes.forEach(attr => {
                        const [name, val] = attr.innerText.split(': ');
                        const div = document.createElement('div');
                        div.className = 'flex-row align-center';
                        div.style.marginBottom = '8px';
                        div.innerHTML = `
                            <input type="text" name="edit_attr_names[]" class="form-control" value="${name}" style="flex:1">
                            <input type="text" name="edit_attr_vals[]" class="form-control" value="${val || ''}" style="flex:1; margin-left:10px;">
                        `;
                        container.appendChild(div);
                    });
                }
                editVariantPanel.classList.add('open');
            });
        });
    }

    const editCategoryPanel = document.getElementById('edit-category-panel');
    const editCategoryBtns = document.querySelectorAll('.edit-category-btn');
    if (editCategoryBtns.length > 0 && editCategoryPanel) {
        editCategoryBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('edit-category-id').value = this.dataset.id;
                document.getElementById('edit-category-name').value = this.dataset.name;
                editCategoryPanel.classList.add('open');
            });
        });
    }

    const deleteListingBtn = document.getElementById('delete-listing-btn');
    if (deleteListingBtn) {
        deleteListingBtn.addEventListener('click', function() {
            const id = document.getElementById('edit-id').value;
            const name = document.getElementById('edit-name').value;
            if (id && confirm(`⚠️ Delete Product "${name}" and all its units?`)) {
                window.location.href = `/manage/inventory/listings/delete/${id}/`;
            }
        });
    }

    const deleteVariantBtn = document.getElementById('delete-variant-btn');
    if (deleteVariantBtn) {
        deleteVariantBtn.addEventListener('click', function() {
            const id = document.getElementById('edit-variant-id').value;
            const sku = document.getElementById('edit-variant-sku').value;
            if (id && confirm(`⚠️ Permanently delete unit ${sku}?`)) {
                window.location.href = `/manage/inventory/units/delete/${id}/`;
            }
        });
    }

    document.querySelectorAll('.close-btn, .btn-cancel, #close-edit-category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.side-panel').forEach(p => p.classList.remove('open'));
        });
    });
});