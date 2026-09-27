/* ============================================================
   Product List — الترتيب
   ============================================================ */
   (function () {
    'use strict';

    const sortSelect = document.getElementById('sortSelect');
    if (!sortSelect) return;

    sortSelect.addEventListener('change', function () {
        const baseUrl = this.dataset.baseUrl || window.location.pathname;
        const sortValue = this.value;
        const url = new URL(baseUrl, window.location.origin);

        // الحفاظ على بقية الـ query params إن وُجدت (غير sort)
        const params = new URLSearchParams(window.location.search);
        params.set('sort', sortValue);

        window.location.href = `${url.pathname}?${params.toString()}`;
    });

})();