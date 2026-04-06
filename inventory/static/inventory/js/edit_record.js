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
                document.getElementById('edit-activity').value = this.dataset.activity;
                document.getElementById('edit-vendor').value = this.dataset.vendor;
                document.getElementById('edit-price').value = this.dataset.price;
                document.getElementById('edit-mpn').value = this.dataset.mpn;
                document.getElementById('edit-tags').value = this.dataset.tags;
                document.getElementById('edit-status').value = this.dataset.status;
                document.getElementById('edit-desc').value = this.dataset.desc;

                const genderValue = this.dataset.gender;
                const genderSelect = document.getElementById('edit-gender');
                
                if (genderSelect && genderValue) {
                    genderSelect.value = genderValue;
                } else {
                    console.error("Gender element not found or value is missing:", genderValue);
                }
                
                const imageUrl = this.getAttribute('data-image');
                const imageDisplay = document.getElementById('current-listing-image-display');
                console.log(imageDisplay)

                if (imageDisplay) {
                    if (imageUrl && imageUrl !== "") {
                        imageDisplay.innerHTML = `<img src="${imageUrl}" style="max-width: 100%; height: 130px; object-fit: contain; border-radius: 4px;">`;
                    } else {
                        imageDisplay.innerHTML = `<span style="color: #a0aec0;">No Image Uploaded</span>`;
                    }
                }

                editListingPanel.classList.add('open');
            });
        });
    }

    const editVariantBtns = document.querySelectorAll('.edit-variant-btn');
    const editVariantPanel = document.getElementById('edit-variant-panel');
    const galleryContainer = document.getElementById('edit-gallery-images-container');

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

                const galleryData = this.getAttribute('data-gallery');
                
                if (galleryContainer) {
                    galleryContainer.innerHTML = ''; 
                    
                    galleryContainer.style.display = 'grid';
                    galleryContainer.style.gridTemplateColumns = 'repeat(auto-fill, minmax(80px, 1fr))';
                    galleryContainer.style.gap = '10px';

                    if (galleryData && galleryData.trim() !== "") {
                        const images = galleryData.split(',');
                        let addedImagesCount = 0;
                        
                        images.forEach(item => {
                            const [id, url] = item.split('|');
                            
                            if (id && url && url !== imageUrl) {
                                galleryContainer.innerHTML += `
                                    <label class="gallery-other-images" style="position: relative; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; cursor: pointer; display: block;">
                                        <img src="${url}" alt="Gallery Image" style="width: 100%; height: 80px; object-fit: cover; display: block;">
                                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(220, 53, 69, 0.9); color: white; font-size: 11px; padding: 6px 0; text-align: center;">
                                            <input type="checkbox" name="delete_images[]" value="${id}" style="margin: 0; cursor: pointer;"> Delete
                                        </div>
                                    </label>
                                `;
                                addedImagesCount++;
                            }
                        });

                        if (addedImagesCount === 0) {
                            galleryContainer.innerHTML = '<span class="small-text" style="color:#888;">No additional gallery images to delete.</span>';
                        }
                    } else {
                        galleryContainer.innerHTML = '<span class="small-text" style="color:#888;">No additional gallery images to delete.</span>';
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
    const saveEditCategoryBtn = document.getElementById('save-edit-category-btn');
    const editCategoryForm = document.getElementById('edit-category-form');

    if (editCategoryBtns.length > 0 && editCategoryPanel) {
        editCategoryBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('edit-category-id').value = this.dataset.id;
                document.getElementById('edit-category-name').value = this.dataset.name;
                editCategoryPanel.classList.add('open');
            });
        });
    }

    if (saveEditCategoryBtn && editCategoryForm) {
        saveEditCategoryBtn.addEventListener('click', () => {
            editCategoryForm.submit();
        });
    }

    const editActivityPanel = document.getElementById('edit-activity-panel');
    const editActivityBtns = document.querySelectorAll('.edit-activity-btn');
    const saveEditActivityBtn = document.getElementById('save-edit-activity-btn');
    const editActivityForm = document.getElementById('edit-activity-form');

    if (editActivityBtns.length > 0 && editActivityPanel) {
        editActivityBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                document.getElementById('edit-activity-id').value = this.dataset.id;
                document.getElementById('edit-activity-name').value = this.dataset.name;
                editActivityPanel.classList.add('open');
            });
        });
    }

    if (saveEditActivityBtn && editActivityForm) {
        saveEditActivityBtn.addEventListener('click', () => {
            editActivityForm.submit();
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

    const deleteCategoryBtn = document.getElementById('delete-category-btn');
    if (deleteCategoryBtn) {
        deleteCategoryBtn.addEventListener('click', function() {
            const id = document.getElementById('edit-category-id').value;
            const name = document.getElementById('edit-category-name').value;
            if (id && confirm(`⚠️ Permanently delete Category "${name}"?`)) {
                window.location.href = `/manage/inventory/category/delete/${id}/`;
            }
        });
    }


    const deleteActivityBtn = document.getElementById('delete-activity-btn');
    if (deleteActivityBtn) {
        deleteActivityBtn.addEventListener('click', function() {
            const id = document.getElementById('edit-activity-id').value;
            const name = document.getElementById('edit-activity-name').value;
            if (id && confirm(`⚠️ Permanently delete Activity "${name}"?`)) {
                window.location.href = `/manage/inventory/activity/delete/${id}/`;
            }
        });
    }

    document.querySelectorAll('.close-btn, .btn-cancel, #close-edit-category-btn, #close-edit-activity-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.side-panel').forEach(p => p.classList.remove('open'));
        });
    });
});