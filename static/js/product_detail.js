/* ============================================================
   Product Detail — التحكم بالكمية
   ============================================================ */
   (function () {
    'use strict';

    const form        = document.getElementById('addToCartForm');
    if (!form) return;

    const qtyInput    = document.getElementById('quantity');
    const decreaseBtn = form.querySelector('[data-action="decrease"]');
    const increaseBtn = form.querySelector('[data-action="increase"]');

    const min = parseInt(qtyInput.min, 10) || 1;
    const max = parseInt(qtyInput.max, 10) || 999;

    function clamp(value) {
        if (isNaN(value) || value < min) return min;
        if (value > max) return max;
        return value;
    }

    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function () {
            qtyInput.value = clamp(parseInt(qtyInput.value, 10) - 1);
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener('click', function () {
            qtyInput.value = clamp(parseInt(qtyInput.value, 10) + 1);
        });
    }

    // ضبط القيمة عند الكتابة اليدوية
    qtyInput.addEventListener('blur', function () {
        qtyInput.value = clamp(parseInt(qtyInput.value, 10));
    });

    qtyInput.addEventListener('input', function () {
        // السماح بالكتابة المؤقتة لكن مع منع الحروف
        this.value = this.value.replace(/[^0-9]/g, '');
    });

})();