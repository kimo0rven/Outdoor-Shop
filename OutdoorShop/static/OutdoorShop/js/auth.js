(function () {
	function svgEye(open) {
		if (open) {
			return (
				'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
			);
		}
		return (
			'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
		);
	}

	function bindPasswordToggle(wrap) {
		var input = wrap.querySelector('input[type="password"], input[type="text"]');
		var btn = wrap.querySelector('.auth-toggle-password');
		if (!input || !btn) return;
		btn.innerHTML = svgEye(false);
		btn.addEventListener('click', function () {
			var show = input.type === 'password';
			input.type = show ? 'text' : 'password';
			btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
			btn.innerHTML = svgEye(show);
		});
	}

	document.querySelectorAll('.auth-password-wrap').forEach(bindPasswordToggle);

	
	var p1 = document.getElementById('id_password1');
	var rules = document.getElementById('auth-password-rules');
	if (p1 && rules) {
		var items = rules.querySelectorAll('li[data-rule]');
		function check() {
			var v = p1.value || '';
			items.forEach(function (li) {
				var key = li.getAttribute('data-rule');
				var ok = false;
				if (key === 'len') ok = v.length >= 8;
				else if (key === 'upper') ok = /[A-Z]/.test(v);
				else if (key === 'lower') ok = /[a-z]/.test(v);
				else if (key === 'num') ok = /[0-9]/.test(v);
				else if (key === 'special') ok = /[!@#$%^&*]/.test(v);
				li.classList.toggle('is-met', ok);
			});
		}
		p1.addEventListener('input', check);
		p1.addEventListener('change', check);
		check();
	}
})();
