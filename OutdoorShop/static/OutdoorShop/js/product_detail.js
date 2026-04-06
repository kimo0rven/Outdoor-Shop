document.addEventListener('DOMContentLoaded', function () {
  const mainImg = document.getElementById('mainProductImg');
  const galleryThumbs = document.querySelectorAll('.gallery-thumb');

  const formEl = document.querySelector('.add-to-cart-form');
  const selectedVariantIdInput = document.getElementById('selectedVariantId');
  const addToCartBtn = document.getElementById('addToCartBtn');

  const availabilityWarning = document.getElementById('availabilityWarning');
  const displayStock = document.getElementById('displayStock');
  const displayPrice = document.getElementById('displayPrice');

  const qtyInput = document.getElementById('qtyInput');
  const defaultAddToCartText = addToCartBtn ? (addToCartBtn.dataset.defaultText || addToCartBtn.textContent || 'Add to Cart') : 'Add to Cart';

  const variantMapping = window.variantMapping || {};
  const attributeGroups = Array.from(document.querySelectorAll('.attribute-group'));
  const attributeNames = attributeGroups
    .map((el) => el.dataset.groupName)
    .filter((v) => v && v.trim().length > 0);
  const sortedAttributeNames = attributeNames.slice().sort();

  const selectedAttributes = {};

  function showWarning(message) {
    if (!availabilityWarning) return;
    availabilityWarning.textContent = message;
    availabilityWarning.style.display = 'block';
  }

  function setAvailabilityUI({ available, stock }) {
    if (availabilityWarning) {
      if (available) {
        availabilityWarning.style.display = 'none';
      } else {
        showWarning('Currently unavailable or out of stock.');
      }
    }

    if (displayStock) {
      if (!available) {
        displayStock.textContent = 'Out of stock';
      } else {
        const n = Number(stock);
        if (Number.isFinite(n) && n > 0 && n < 5) {
          displayStock.textContent = `Low stock: ${n} left`;
        } else {
          displayStock.textContent = 'In stock';
        }
      }
    }

    if (addToCartBtn) {
      addToCartBtn.disabled = !available;
      addToCartBtn.classList.toggle('is-disabled', addToCartBtn.disabled);
      addToCartBtn.textContent = available ? defaultAddToCartText : 'Currently Unavailable';
    }
  }

  function resetSelectionUI() {
    if (selectedVariantIdInput) selectedVariantIdInput.value = '';
    if (availabilityWarning) availabilityWarning.style.display = 'none';
    if (displayStock) displayStock.textContent = 'Select options to see stock';
    if (addToCartBtn) {
      addToCartBtn.disabled = true;
      addToCartBtn.classList.add('is-disabled');
      addToCartBtn.textContent = defaultAddToCartText;
    }
  }

  function buildComboKey() {
    return sortedAttributeNames.map((k) => `${k}:${selectedAttributes[k]}`).join('|');
  }

  function allAttributesSelected() {
    if (!sortedAttributeNames.length) return false;
    return sortedAttributeNames.every((k) => selectedAttributes[k] && String(selectedAttributes[k]).trim().length > 0);
  }

  function applyVariantSelection() {
    if (!selectedVariantIdInput || !addToCartBtn) {
      return;
    }

    if (!allAttributesSelected()) {
      resetSelectionUI();
      return;
    }

    const comboKey = buildComboKey();
    const variantInfo = variantMapping[comboKey];

    if (!variantInfo) {
      resetSelectionUI();
      showWarning('This combination is currently unavailable or out of stock.');
      return;
    }

    const stock = Number(variantInfo.stock ?? 0);
    const available = stock > 0;

    if (selectedVariantIdInput) selectedVariantIdInput.value = available ? String(variantInfo.id) : '';

    if (displayPrice && variantInfo.price !== undefined && variantInfo.price !== null && variantInfo.price !== '') {
      const priceNum = Number(variantInfo.price);
      if (Number.isFinite(priceNum)) {
        displayPrice.textContent = `₱${priceNum.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      } else {
        displayPrice.textContent = `₱${variantInfo.price}`;
      }
    }

    setAvailabilityUI({ available, stock });

    const targetMainImage = variantInfo.main_image || variantInfo.thumbnail;
    if (available && mainImg && targetMainImage) {
      mainImg.src = targetMainImage;
      galleryThumbs.forEach((t) => t.classList.remove('active'));
      galleryThumbs.forEach((t) => {
        if (t.getAttribute('src') === targetMainImage) t.classList.add('active');
      });
    }
  }

  window.swapImage = function (imgEl) {
    if (!imgEl || !mainImg) return;
    const src = imgEl.getAttribute('src');
    if (!src) return;

    mainImg.src = src;

    galleryThumbs.forEach((t) => t.classList.remove('active'));
    imgEl.classList.add('active');
  };

  window.selectAttribute = function (btn) {
    if (!btn) return;

    const groupEl = btn.closest('.attribute-group');
    if (!groupEl) return;

    const groupName = groupEl.dataset.groupName;
    const value = btn.dataset.value;
    if (!groupName || !value) return;

    selectedAttributes[groupName] = String(value).trim();

    groupEl.querySelectorAll('.attr-btn').forEach((b) => {
      b.classList.toggle('selected', b === btn);
    });

    applyVariantSelection();
  };

  window.updateQty = function (delta) {
    if (!qtyInput) return;
    const current = parseInt(qtyInput.value || '1', 10);
    const next = Math.min(99, Math.max(1, current + Number(delta)));
    qtyInput.value = String(next);
  };

  if (formEl && selectedVariantIdInput) {
    formEl.addEventListener('submit', function (e) {
      if (!selectedVariantIdInput.value) {
        e.preventDefault();
        if (availabilityWarning) {
          availabilityWarning.textContent = 'Please select product variation first.';
          availabilityWarning.style.display = 'block';
        }
        resetSelectionUI();
      }
    });
  }

  if (selectedVariantIdInput && addToCartBtn) {
    resetSelectionUI();
  }
});