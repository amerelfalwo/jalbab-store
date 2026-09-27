/* ============================================================
   Cart Page — التفاعلات
   ============================================================ */
   (function () {
    'use strict';

    const cartSection = document.querySelector('.cart-section');
    if (!cartSection) return;

    // ----------------------------------------------------
    // 1) التحكم بالكمية (+ / −) مع تحديث تلقائي
    // ----------------------------------------------------
    cartSection.querySelectorAll('.cart-row').forEach(function (row) {
        const form      = row.querySelector('.cart-qty-form');
        const input     = row.querySelector('.cart-qty-input');
        const decBtn    = row.querySelector('[data-action="decrease"]');
        const incBtn    = row.querySelector('[data-action="increase"]');
        const subtotalEl = row.querySelector('.cart-subtotal');

        if (!form || !input) return;

        const min   = 0;
        const max   = parseInt(input.max, 10) || 999;

        function submitUpdate(newValue) {
            const value = Math.max(min, Math.min(max, parseInt(newValue, 10) || 0));
            input.value = value;

            const formData = new FormData(form);
            formData.set('quantity', value);

            fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData,
            })
            .then(r => r.json())
            .then(data => {
                if (!data.success) return;

                // إذا صارت الكمية 0 → حذف الصف مع أنيميشن
                if (parseInt(data.quantity, 10) === 0) {
                    row.style.transition = 'opacity .25s, transform .25s';
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(20px)';
                    setTimeout(() => {
                        row.remove();
                        updateCartBadge(data.cart_count);
                        updateCartTotal(data.cart_total);
                        if (!document.querySelector('.cart-row')) {
                            window.location.reload();
                        }
                    }, 250);
                    return;
                }

                // تحديث الإجمالي الفرعي
                if (subtotalEl) {
                    subtotalEl.textContent = `${parseInt(data.subtotal, 10)} جنيه`;
                }

                updateCartBadge(data.cart_count);
                updateCartTotal(data.cart_total);
            })
            .catch(err => console.error('Cart update failed:', err));
        }

        if (decBtn) {
            decBtn.addEventListener('click', () => submitUpdate(parseInt(input.value, 10) - 1));
        }

        if (incBtn) {
            incBtn.addEventListener('click', () => submitUpdate(parseInt(input.value, 10) + 1));
        }

        // عند الكتابة اليدوية ثم الخروج من الحقل
        input.addEventListener('change', () => submitUpdate(input.value));

        // تنظيف المدخلات (أرقام فقط)
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });

    // ----------------------------------------------------
    // 2) دوال مساعدة
    // ----------------------------------------------------
    function updateCartBadge(count) {
        const badge = document.querySelector('.cart-badge');
        const cartIcon = document.querySelector('.navbar-cart');

        if (count > 0) {
            if (badge) {
                badge.textContent = count;
            } else if (cartIcon) {
                const span = document.createElement('span');
                span.className = 'cart-badge';
                span.textContent = count;
                cartIcon.appendChild(span);
            }
        } else if (badge) {
            badge.remove();
        }
    }

    function updateCartTotal(total) {
        const totalEl = document.querySelector('.cart-total-amount');
        if (totalEl) {
            totalEl.textContent = `${parseInt(total, 10)} جنيه`;
        }
        // تحديث المجموع الفرعي في الملخص (أول عنصر في القائمة)
        const subtotalSummary = document.querySelector('.cart-summary-list li:nth-child(2) span:last-child');
        if (subtotalSummary) {
            subtotalSummary.textContent = `${parseInt(total, 10)} جنيه`;
        }
    }

})();