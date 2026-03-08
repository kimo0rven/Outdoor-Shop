document.addEventListener("DOMContentLoaded", function() {

    const btnAddListing = document.getElementById('btn-add-listing');
    const listingPanel = document.getElementById('add-listing-panel');
    const closeListingBtn = document.getElementById('close-listing-btn');
    const cancelListingBtn = document.getElementById('cancel-listing-btn');

    const saveListingBtn = document.getElementById('save-listing-btn');
    const createListingForm = document.getElementById('create-listing-form');

    if (btnAddListing && listingPanel) {
        btnAddListing.addEventListener('click', () => listingPanel.classList.add('open'));
    }
    
    [closeListingBtn, cancelListingBtn].forEach(btn => {
        if (btn) btn.addEventListener('click', () => listingPanel.classList.remove('open'));
    });

    const btnAddVariant = document.getElementById('btn-add-variant');
    const variantPanel = document.getElementById('add-variant-panel');
    const closeVariantBtn = document.getElementById('close-variant-btn');

    if (btnAddVariant && variantPanel) {
        btnAddVariant.addEventListener('click', () => variantPanel.classList.add('open'));
    }
    if (closeVariantBtn) {
        closeVariantBtn.addEventListener('click', () => variantPanel.classList.remove('open'));
    }

    if (saveListingBtn && createListingForm) {
        saveListingBtn.addEventListener('click', () => {
            console.log("New Listing save clicked");
            createListingForm.submit();
        });
    }

    const closeEditBtn = document.getElementById('close-edit-btn');
    const closeEditVariantBtn = document.getElementById('close-edit-variant-btn');

    if (closeEditBtn) {
        closeEditBtn.addEventListener('click', () => {
            document.getElementById('edit-listing-panel').classList.remove('open');
        });
    }
    if (closeEditVariantBtn) {
        closeEditVariantBtn.addEventListener('click', () => {
            document.getElementById('edit-variant-panel').classList.remove('open');
        });
    }


    const messageContainer = document.querySelector('.messages-container');
    
    if (messageContainer) {
        setTimeout(() => {
            messageContainer.style.transition = "opacity 0.5s ease";
            messageContainer.style.opacity = "0";
            setTimeout(() => {
                messageContainer.remove();
            }, 500); 
        }, 3000);
    }


});