document.addEventListener("DOMContentLoaded", function() {
    // --- 1. LISTING UPDATE (Parent Products) ---
    // These IDs match your listings.html
    const saveEditBtn = document.getElementById('save-edit-btn');
    const editListingForm = document.getElementById('edit-listing-form');

    if (saveEditBtn && editListingForm) {
        saveEditBtn.addEventListener('click', function() {
            console.log("Listing update button clicked");
            if (editListingForm.checkValidity()) {
                saveEditBtn.disabled = true;
                saveEditBtn.innerText = "Updating...";
                editListingForm.submit();
            } else {
                editListingForm.reportValidity();
            }
        });
    }

    // --- 2. VARIANT UPDATE (Inventory Units) ---
    // These IDs match your units.html
    const saveEditVariantBtn = document.getElementById('save-edit-variant-btn');
    const editVariantForm = document.getElementById('edit-variant-form');

    if (saveEditVariantBtn && editVariantForm) {
        saveEditVariantBtn.addEventListener('click', function() {
            console.log("Variant update button clicked");
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