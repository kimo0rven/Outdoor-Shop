document.addEventListener("DOMContentLoaded", function () {
	const saveVariantBtn = document.getElementById("save-variant-btn");
	const createVariantForm = document.getElementById("create-variant-form");
	const addAttrBtn = document.getElementById("add-attribute-row");
	const attrContainer = document.getElementById("attributes-container");
	const addImageInput = document.getElementById("add-variant-image");

	if (addImageInput) {
		addImageInput.addEventListener("change", function () {
			if (this.files && this.files[0]) {
				console.log("File selected:", this.files[0].name);
			}
		});
	}

	if (addAttrBtn) {
		addAttrBtn.addEventListener("click", function () {
			const row = document.createElement("div");
			row.className = "flex-row align-center attribute-row";
			row.style.gap = "10px";
			row.style.marginBottom = "10px";

			row.innerHTML = `
                <input type="text" name="attr_name[]" class="form-control" style="flex: 2;" placeholder="e.g. Size">
                <input type="text" name="attr_val[]" class="form-control" style="flex: 2;" placeholder="e.g. Large">
                <button type="button" class="remove-attr" style="background: none; border: none; color: #ff5c5c; cursor: pointer; font-size: 1.2rem;">✕</button>
            `;
			attrContainer.appendChild(row);
			row.querySelector(".remove-attr").addEventListener("click", () => row.remove());
		});
	}

	if (saveVariantBtn) {
		saveVariantBtn.addEventListener("click", () => {
			if (createVariantForm.checkValidity()) {
				saveVariantBtn.disabled = true;
				saveVariantBtn.innerText = "Saving...";
				createVariantForm.submit();
			} else {
				createVariantForm.reportValidity();
			}
		});
	}
});
