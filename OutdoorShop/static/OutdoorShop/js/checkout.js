document.addEventListener('DOMContentLoaded', function () {
  const addressForm = document.getElementById('address-form-container');
  const addressSummary = document.getElementById('address-summary-container');
  const editShippingBtn = document.getElementById('edit-shipping-btn');
  const continuePaymentBtn = document.getElementById('continue-payment-btn');

  const paymentSection = document.getElementById('payment-section');
  const paymentContainer = document.getElementById('payment-container');
  const shippingSection = document.getElementById('shipping-section');

  const termsCheckbox = document.getElementById('terms-checkbox');
  const paypalContainer = document.getElementById('paypal-button-container');

  const sidebar = document.getElementById('address-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const closeSidebarBtn = document.getElementById('close-sidebar-btn');
  const useNewAddressBtn = document.getElementById('use-new-address-btn');
  const saveAddressBtn = document.getElementById('save-address-btn');

  if (editShippingBtn) {
    editShippingBtn.addEventListener('click', function () {
      sidebar.classList.add('active');
      overlay.classList.add('active');
    });
  }

  function closeSidebar() {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
  }

  if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  if (useNewAddressBtn) {
    useNewAddressBtn.addEventListener('click', function () {
      closeSidebar();
      addressSummary.style.display = 'none';
      editShippingBtn.style.display = 'none';

      document.getElementById('shipping-form').reset();
      addressForm.style.display = 'block';

      paymentSection.classList.add('disabled-step');
      paymentContainer.style.display = 'none';
      shippingSection.classList.remove('completed-step');
    });
  }

  const addressRadios = document.querySelectorAll('input[name="selected_address"]');
  addressRadios.forEach(radio => {
    radio.addEventListener('change', function() {

      document.querySelectorAll('.address-card').forEach(c => c.classList.remove('selected'));
      this.closest('.address-card').classList.add('selected');

      document.getElementById('summary-name').innerText = this.dataset.firstname + " " + this.dataset.lastname;
      document.getElementById('summary-address1').innerText = this.dataset.address1;
      document.getElementById('summary-address2').innerText = this.dataset.address2 ? ", " + this.dataset.address2 : "";
      document.getElementById('summary-city').innerText = this.dataset.city;
      document.getElementById('summary-state').innerText = this.dataset.state;
      document.getElementById('summary-zip').innerText = this.dataset.zip;
      document.getElementById('summary-phone').innerText = this.dataset.phone;

      closeSidebar();
      addressForm.style.display = 'none';
      addressSummary.style.display = 'block';
      editShippingBtn.style.display = 'block';
    });
  });

  if (saveAddressBtn) {
    saveAddressBtn.addEventListener('click', function () {
      const form = document.getElementById('shipping-form');

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      saveAddressBtn.innerText = "Saving...";
      saveAddressBtn.disabled = true;

      const addressData = {
        first_name: document.getElementById('checkout-firstname').value,
        last_name: document.getElementById('checkout-lastname').value,
        phone_number: document.getElementById('checkout-phone').value,
        address_line_1: document.getElementById('checkout-address1').value,
        address_line_2: document.getElementById('checkout-address2').value,
        city: document.getElementById('checkout-city').value,
        state: document.getElementById('checkout-state').value,
        postal_code: document.getElementById('checkout-zip').value
      };

      fetch(window.checkoutConfig.saveAddressUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': window.checkoutConfig.csrfToken
        },
        body: JSON.stringify(addressData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          window.location.reload();
        } else {
          alert("Error saving address.");
          saveAddressBtn.innerText = "Save address";
          saveAddressBtn.disabled = false;
        }
      })
      .catch(error => {
        console.error("Error:", error);
        saveAddressBtn.innerText = "Save address";
        saveAddressBtn.disabled = false;
      });
    });
  }

  if (continuePaymentBtn) {
    continuePaymentBtn.addEventListener('click', function() {
      document.getElementById('delivery-options').style.display = 'none';

      shippingSection.classList.add('completed-step');

      paymentSection.classList.remove('disabled-step');
      paymentContainer.style.display = 'block';

      paymentSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  if (termsCheckbox) {
    termsCheckbox.addEventListener('change', function() {
      if (this.checked) {
        paypalContainer.style.opacity = '1';
        paypalContainer.style.pointerEvents = 'auto';
      } else {
        paypalContainer.style.opacity = '0.5';
        paypalContainer.style.pointerEvents = 'none';
      }
    });
  }

  if (typeof paypal !== 'undefined') {
    paypal.Buttons({
      createOrder: function(data, actions) {
        return actions.order.create({
          purchase_units: [{
            amount: { value: window.checkoutConfig.totalAmount }
          }]
        });
      },

      onApprove: function(data, actions) {
        return actions.order.capture().then(function(orderData) {
          paymentContainer.innerHTML = '<h3>Processing your order... Please wait.</h3>';

          const fullName = document.getElementById('summary-name').innerText.trim().split(" ");
          const firstName = fullName[0];
          const lastName = fullName.slice(1).join(" ");

          const shippingData = {
            first_name: firstName,
            last_name: lastName,
            phone: document.getElementById('summary-phone').innerText.trim(),
            address_1: document.getElementById('summary-address1').innerText.trim(),
            address_2: document.getElementById('summary-address2').innerText.replace(',', '').trim(),
            city: document.getElementById('summary-city').innerText.trim(),
            state: document.getElementById('summary-state').innerText.trim(),
            zipcode: document.getElementById('summary-zip').innerText.trim(),
          };

          const payload = {
            shipping: shippingData,
            paypal_transaction_id: orderData.id,
            payment_method: 'card'
          };

          fetch(window.checkoutConfig.processOrderUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': window.checkoutConfig.csrfToken,
            },
            body: JSON.stringify(payload)
          })
          .then(response => response.json())
          .then(data => {
            if(data.status === 'success') {
               window.location.href = window.checkoutConfig.orderSuccessUrl;
            } else {
               alert("Error saving the order: " + data.message);
            }
          });
        });
      }
    }).render('#paypal-button-container');
  }
});