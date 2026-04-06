let cart = [];
let currentProductImage = 'none';
let posVariantPickById = {};

const posData = document.getElementById('pos-data');
const checkoutUrl = posData.dataset.checkoutUrl;
const templateVariantUrl = posData.dataset.variantsUrl;
const searchUrl = posData.dataset.searchUrl;
const csrfToken = document.getElementById('csrf-token').value;

function escapeHtml(text) {
    if (text == null || text === '') return '';
    const el = document.createElement('div');
    el.textContent = text;
    return el.innerHTML;
}

function buildVariantAttributesHtml(v) {
    if (v.attribute_list && v.attribute_list.length) {
        const pills = v.attribute_list
            .map((a) => `<span class="v-attr-pill">${escapeHtml(`${a.name}: ${a.value}`)}</span>`)
            .join('');
        return `<div class="v-attributes">${pills}</div>`;
    }
    if (v.attributes) {
        return `<div class="v-attributes v-attributes-plain">${escapeHtml(v.attributes)}</div>`;
    }
    return '';
}

function buildCartItemAttributesHtml(item) {
    if (item.attribute_list && item.attribute_list.length) {
        const pills = item.attribute_list
            .map((a) => `<span class="v-attr-pill">${escapeHtml(`${a.name}: ${a.value}`)}</span>`)
            .join('');
        return `<div class="v-attributes cart-item-attributes">${pills}</div>`;
    }
    if (item.attributes) {
        return `<div class="v-attributes v-attributes-plain cart-item-attributes">${escapeHtml(item.attributes)}</div>`;
    }
    return '';
}

function addToCart(id, listingName, variantName, price, stock, image, attributeList, attributesString) {
    if (stock <= 0) {
        alert("This item is out of stock!");
        return;
    }

    const attrs = Array.isArray(attributeList) ? attributeList : [];
    const attrStr = attributesString || '';

    let existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        if (existingItem.qty < stock) {
            existingItem.qty += 1;
        } else {
            alert("Cannot add more than available stock.");
        }
    } else {
        cart.push({
            id: id,
            listingName: listingName,
            variantName: variantName,
            price: price,
            qty: 1,
            maxStock: stock,
            image: image,
            attribute_list: attrs,
            attributes: attrStr,
        });
    }

    updateCartUI();
}

function updateCartUI() {
    const cartList = document.getElementById('cart-list');
    const checkoutBtn = document.getElementById('checkout-btn');
    
    const subTotalNode = document.getElementById('summary-subtotal');
    const totalNode = document.getElementById('cart-total');
    
    if (cart.length === 0) {
        cartList.innerHTML = `
            <div id="empty-msg" class="cart-list-empty-msg">
              <div style="font-size: 30px; margin-bottom: 10px;">🛒</div>
              Cart is empty. Tap items to add.
            </div>`;
        
        if (subTotalNode) subTotalNode.innerText = "₱0.00";
        if (totalNode) totalNode.innerText = "₱0.00";
        checkoutBtn.disabled = true;
        return;
    }

    cartList.innerHTML = ""; 
    let subTotal = 0;

    cart.forEach((item, index) => {
        let itemTotal = item.price * item.qty;
        subTotal += itemTotal;

        let imgSrc = (item.image && item.image !== 'none') ? `<img src="${item.image}" alt="img">` : `<span style="font-size:24px">📦</span>`;
        
        let displayQty = item.qty < 10 ? `0${item.qty}` : item.qty;

        const cartAttrsHtml = buildCartItemAttributesHtml(item);

        cartList.innerHTML += `
            <div class="cart-item-card">
                <div class="cart-item-img-box">
                    ${imgSrc}
                </div>
                
                <div class="cart-item-details">
                    <div class="cart-item-title">${escapeHtml(item.listingName)}</div>
            
                    ${cartAttrsHtml}

                    <div class="cart-item-bottom">
                        <div class="qty-controls">
                            <button class="btn-qty-minus" onclick="changeQty(${index}, -1)">−</button>
                            <span class="qty-val">${displayQty}</span>
                            <button class="btn-qty-plus" onclick="changeQty(${index}, 1)">+</button>
                        </div>
                        <div class="cart-item-price-wrap">
                            Total <span class="cart-item-price">₱${itemTotal.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                        </div>
                    </div>
                </div>

                <button class="btn-delete-item" onclick="removeItem(${index})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
            </div>
        `;
    });

    let taxRate = 0.00;
    let taxAmount = subTotal * taxRate;
    let grandTotal = subTotal + taxAmount;

    if (subTotalNode) subTotalNode.innerText = `₱${subTotal.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    if (totalNode) totalNode.innerText = `₱${grandTotal.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    checkoutBtn.disabled = false;
}

function changeQty(index, delta) {
    let item = cart[index];
    item.qty += delta;

    if (item.qty <= 0) {
        cart.splice(index, 1); 
    } else if (item.qty > item.maxStock) {
        item.qty = item.maxStock; 
        alert("Maximum stock reached.");
    }
    
    updateCartUI();
}

function removeItem(index) {
    cart.splice(index, 1);
    updateCartUI();
}

function clearCart() {
    if (confirm("Are you sure you want to clear the current order?")) {
        cart = [];
        updateCartUI();
    }
}

function openVariantModal(listingId, listingName, imgUrl) {
    const modal = document.getElementById('variant-modal');
    const title = document.getElementById('modal-product-name');
    const listContainer = document.getElementById('modal-variants-list');

    currentProductImage = imgUrl;

    title.innerText = listingName;
    listContainer.innerHTML = '<div style="text-align:center; padding: 20px; color:#718096;">Loading options...</div>';
    modal.style.display = 'flex';

    const fetchUrl = templateVariantUrl.replace('0', listingId);

    fetch(fetchUrl)
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            listContainer.innerHTML = ''; 
            
            if (data.variants.length === 0) {
                listContainer.innerHTML = '<div style="text-align:center; color:#e53e3e;">No stock available for this item.</div>';
                return;
            }

            posVariantPickById = {};
            data.variants.forEach(v => {
                posVariantPickById[v.id] = {
                    listingName,
                    variantName: v.variant_name,
                    price: v.price,
                    stock: v.stock,
                    attribute_list: v.attribute_list || [],
                    attributes: v.attributes || '',
                };
            });

            data.variants.forEach(v => {
                const attributesBlock = buildVariantAttributesHtml(v);

                listContainer.innerHTML += `
                    <div class="variant-row" onclick="selectVariantAndClose(${v.id})">
                        <div class="variant-info">
                            <span class="v-name">${escapeHtml(v.variant_name)}</span>
                            ${attributesBlock}
                            <span class="v-sku">SKU: ${escapeHtml(v.sku)}</span>
                        </div>
                        <div class="variant-price-block">
                            <span class="v-price">₱${v.price.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                            <span class="v-stock">Stock: ${v.stock}</span>
                        </div>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Error fetching variants:', error);
            listContainer.innerHTML = '<div style="text-align:center; color:#e53e3e;">Failed to load options. Check browser console.</div>';
        });
}

function closeVariantModal() {
    document.getElementById('variant-modal').style.display = 'none';
}

function selectVariantAndClose(id) {
    const pick = posVariantPickById[id];
    if (!pick) {
        console.error('Missing variant pick for id', id);
        return;
    }
    addToCart(
        id,
        pick.listingName,
        pick.variantName,
        pick.price,
        pick.stock,
        currentProductImage,
        pick.attribute_list,
        pick.attributes
    );
    closeVariantModal();
}

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById('pos-search-input');
    const filterTabs = document.querySelectorAll('.filter-tab');
    const itemsGrid = document.getElementById('quick-items-grid');
    
    if (!itemsGrid) return; 

    const searchUrl = document.getElementById('pos-data').dataset.searchUrl;
    const originalGridHTML = itemsGrid.innerHTML;
    let searchTimeout;

    let activeFilters = {
        category: 'all',
        activity: 'all',
        gender: 'all'
    };

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                itemsGrid.innerHTML = originalGridHTML;
                return;
            }

            searchTimeout = setTimeout(() => {
                itemsGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #718096;">Searching for "${query}"...</div>`;

                fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            itemsGrid.innerHTML = ""; 
                            
                            data.results.forEach(item => {
                                const imgUrl = item.image ? item.image : 'none';
                                const imgHtml = item.image 
                                    ? `<img src="${item.image}" alt="${item.name}">`
                                    : `<span class="no-img">No Img</span>`;

                                itemsGrid.innerHTML += `
                                    <div class="pos-item-card" onclick="openVariantModal(${item.id}, '${item.name.replace(/'/g, "\\'")}', '${imgUrl}')">
                                      <div class="pos-item-img">${imgHtml}</div>
                                      <div class="pos-item-details">
                                        <div class="pos-item-name">${item.name}</div>
                                        <div class="pos-item-bottom">
                                          <span class="pos-item-stock">Select Options ➔</span>
                                        </div>
                                      </div>
                                    </div>
                                `;
                            });
                        } else {
                            itemsGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #e53e3e; font-weight: 600;">No items found matching "${query}".</div>`;
                        }
                    })
                    .catch(error => {
                        console.error("Search error:", error);
                        itemsGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 40px; text-align: center; color: #e53e3e;">Error communicating with server.</div>`;
                    });
            }, 300); 

            document.querySelectorAll('.filter-row').forEach(row => {
                row.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                row.querySelector('[data-val="all"]').classList.add('active');
            });
            activeFilters = { category: 'all', activity: 'all', gender: 'all' };
        });
    }

    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            if (searchInput && searchInput.value.length > 0) {
                searchInput.value = '';
                itemsGrid.innerHTML = originalGridHTML;
            }

            const parentRow = this.closest('.filter-row');
            parentRow.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const filterType = this.dataset.type;
            const filterVal = this.dataset.val;
            activeFilters[filterType] = filterVal;

            const itemCards = itemsGrid.querySelectorAll('.pos-item-card');
            
            itemCards.forEach(card => {
                const matchCategory = (activeFilters.category === 'all' || card.dataset.category === activeFilters.category);
                const matchActivity = (activeFilters.activity === 'all' || card.dataset.activity === activeFilters.activity);
                const matchGender   = (activeFilters.gender === 'all'   || card.dataset.gender === activeFilters.gender);

                if (matchCategory && matchActivity && matchGender) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});

function processCheckout() {
    if (cart.length === 0) return;

    const checkoutBtn = document.getElementById('checkout-btn');
    checkoutBtn.disabled = true;
    checkoutBtn.innerText = "Processing...";

    const payload = {
        cart: cart.map(item => ({
            id: item.id,
            qty: item.qty,
        })),
        source: 'POS',
    };

    fetch(checkoutUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const idMsg = data.order_id ? ` Order #${data.order_id}.` : '';
            alert(`Order created successfully!${idMsg}`);
            cart = [];
            updateCartUI();
            checkoutBtn.disabled = false;
            checkoutBtn.innerText = "Continue";
        } else {
            alert("Error: " + data.message);
            checkoutBtn.disabled = false;
            checkoutBtn.innerText = "Continue";
        }
    })
    .catch(error => {
        console.error('Checkout error:', error);
        alert("A system error occurred while processing the order.");
        checkoutBtn.disabled = false;
        checkoutBtn.innerText = "Continue";
    });
}