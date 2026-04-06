document.addEventListener("DOMContentLoaded", function() {

    const saveEditBtn = document.getElementById('save-edit-btn');
    const editListingForm = document.getElementById('edit-listing-form');

    if (saveEditBtn && editListingForm) {
        saveEditBtn.addEventListener('click', function() {
            if (editListingForm.checkValidity()) {
                saveEditBtn.disabled = true;
                saveEditBtn.innerText = "Updating...";
                editListingForm.submit();
            } else {
                editListingForm.reportValidity();
            }
        });
    }

    const saveEditVariantBtn = document.getElementById('save-edit-variant-btn');
    const editVariantForm = document.getElementById('edit-variant-form');

    if (saveEditVariantBtn && editVariantForm) {
        saveEditVariantBtn.addEventListener('click', function() {
            if (editVariantForm.checkValidity()) {
                saveEditVariantBtn.disabled = true;
                saveEditVariantBtn.innerText = "Updating...";
                editVariantForm.submit();
            } else {
                editVariantForm.reportValidity();
            }
        });
    }
});