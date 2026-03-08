let cart = [];

document.addEventListener("DOMContentLoaded", function () {
	const searchInput = document.getElementById("pos-search-input");
	const resultsContainer = document.getElementById("search-results-container");
	const cartList = document.getElementById("cart-list");
	const totalEl = document.getElementById("cart-total");
	const checkoutBtn = document.getElementById("checkout-btn");
	const paymentModal = document.getElementById("payment-modal");
	const amountTenderedInput = document.getElementById("amount-tendered");
	const changeDisplay = document.getElementById("change-display");
	const confirmBtn = document.getElementById("confirm-checkout");
	const variantModal = document.getElementById("variant-modal");

	const posData = document.getElementById("pos-data");
	const checkoutUrl = posData ? posData.dataset.checkoutUrl : "/pos/checkout/";

	// Search Logic
	searchInput.addEventListener("input", async (e) => {
		const q = e.target.value.trim();
		if (q.length < 2) {
			resultsContainer.style.display = "none";
			return;
		}
		try {
			const response = await fetch(`/pos/search/?q=${q}`);
			const data = await response.json();

			resultsContainer.innerHTML = "";
			if (data.results && data.results.length > 0) {
				data.results.forEach((item) => {
					const div = document.createElement("div");
					div.className = "result-item";
					div.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 12px; padding: 5px; cursor: pointer;">
                            <img src="${item.image || ""}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #edf2f7;">
                            <div style="flex-grow: 1;">
                                <div style="font-weight: bold; font-size: 0.9rem;">${item.name}</div>
                                <small style="color: #718096;">SKU: ${item.sku} | Stock: ${item.stock}</small>
                            </div>
                            <div style="font-weight: bold; color: #2ab6d4;">₱${parseFloat(item.price).toFixed(2)}</div>
                        </div>
                    `;
					div.onclick = () => addToCart(item);
					resultsContainer.appendChild(div);
				});
				resultsContainer.style.display = "block";
			} else {
				resultsContainer.style.display = "none";
			}
		} catch (err) {
			console.error("Search Error:", err);
		}
	});

	// Close search results when clicking outside
	document.addEventListener("click", (e) => {
		if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
			resultsContainer.style.display = "none";
		}
	});

	// Variant Modal Logic
	window.openVariantModal = function (listingId, listingName) {
		document.getElementById("variant-modal-title").innerText = listingName + " - Select Variant";
		const variantsHtml = document.getElementById("variants-" + listingId).innerHTML;
		const modalBody = document.getElementById("variant-modal-body");

		if (variantsHtml.trim() === "") {
			modalBody.innerHTML =
				'<p style="text-align: center; color: #a0aec0; padding: 20px;">No available variants for this item.</p>';
		} else {
			modalBody.innerHTML = variantsHtml;
		}

		variantModal.style.display = "flex";
	};

	window.closeVariantModal = function () {
		if (variantModal) variantModal.style.display = "none";
	};

	// Close variant modal if clicked outside
	if (variantModal) {
		variantModal.addEventListener("click", function (e) {
			if (e.target === this) {
				closeVariantModal();
			}
		});
	}

	// Cart Logic
	window.addToCart = function (item) {
		const existing = cart.find((i) => i.id === item.id);
		if (existing) {
			if (existing.qty < item.stock) {
				existing.qty += 1;
			} else {
				alert("Limit reached based on current stock.");
			}
		} else {
			cart.push({ ...item, qty: 1 });
		}
		searchInput.value = "";
		resultsContainer.style.display = "none";
		renderCart();
	};

	window.renderCart = function () {
		if (!cartList || !totalEl) return;

		cartList.innerHTML = "";
		let total = 0;

		if (cart.length === 0) {
			cartList.innerHTML =
				'<p id="empty-msg" style="color: #a0aec0; text-align: center; margin-top: 50px;">Cart is empty</p>';
			totalEl.innerText = "₱0.00";
			checkoutBtn.disabled = true;
			return;
		}

		cart.forEach((item, index) => {
			const itemTotal = item.price * item.qty;
			total += itemTotal;
			const div = document.createElement("div");
			div.className = "cart-item";
			div.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px; padding: 10px; border-bottom: 1px solid #f7fafc;">
                    <img src="${item.image || ""}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">
                    <div style="flex-grow: 1;">
                        <div style="font-weight: bold; font-size: 0.85rem;">${item.name}</div>
                        <small>₱${parseFloat(item.price).toFixed(2)} x ${item.qty}</small>
                    </div>
                    <button onclick="removeFromCart(${index})" style="background:none; border:none; color:red; cursor:pointer; font-size:1.2rem;">✕</button>
                </div>
            `;
			cartList.appendChild(div);
		});
		totalEl.innerText = `₱${total.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
		checkoutBtn.disabled = false;
	};

	window.removeFromCart = function (index) {
		cart.splice(index, 1);
		renderCart();
	};

	// Category Filtering
	window.filterCategory = function (slug) {
		document.querySelectorAll(".cat-tab").forEach((tab) => {
			tab.classList.remove("active");
			if (tab.getAttribute("onclick").includes(`'${slug}'`)) {
				tab.classList.add("active");
			}
		});
		const items = document.querySelectorAll(".quick-item-card");
		items.forEach((item) => {
			if (slug === "all" || item.classList.contains(slug)) {
				item.style.display = "flex";
			} else {
				item.style.display = "none";
			}
		});
	};

	// Checkout Modal Logic
	checkoutBtn.addEventListener("click", () => {
		if (cart.length === 0) return;
		const totalText = totalEl.innerText;
		document.getElementById("modal-total-due").innerText = totalText;
		paymentModal.style.display = "flex";
		amountTenderedInput.value = "";
		changeDisplay.style.display = "none";
		confirmBtn.disabled = true;
		confirmBtn.style.opacity = "0.5";
		setTimeout(() => amountTenderedInput.focus(), 100);
	});

	amountTenderedInput.addEventListener("input", () => {
		const total = parseFloat(document.getElementById("modal-total-due").innerText.replace(/[₱,]/g, ""));
		const tendered = parseFloat(amountTenderedInput.value) || 0;
		if (tendered >= total) {
			const change = tendered - total;
			document.getElementById("modal-change-amount").innerText =
				`₱${change.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
			changeDisplay.style.display = "block";
			confirmBtn.disabled = false;
			confirmBtn.style.opacity = "1";
		} else {
			changeDisplay.style.display = "none";
			confirmBtn.disabled = true;
			confirmBtn.style.opacity = "0.5";
		}
	});

	confirmBtn.addEventListener("click", async () => {
		const total = parseFloat(document.getElementById("modal-total-due").innerText.replace(/[₱,]/g, ""));
		const checkoutData = {
			cart: cart,
			total: total,
			payment_method: "Cash",
			source: "POS",
		};
		try {
			const response = await fetch(checkoutUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
				},
				body: JSON.stringify(checkoutData),
			});
			const result = await response.json();
			if (result.success) {
				alert("Transaction Successful! Order #" + result.order_id);
				cart = [];
				renderCart();
				paymentModal.style.display = "none";
				window.location.reload();
			} else {
				alert("Error: " + result.message);
			}
		} catch (error) {
			console.error("Checkout Error:", error);
			alert("Server error during checkout.");
		}
	});

	document.getElementById("cancel-modal").addEventListener("click", () => {
		paymentModal.style.display = "none";
	});
});
