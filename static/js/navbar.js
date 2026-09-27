/* ============================================================
   Navbar — التفاعلات
   ============================================================ */
   (function () {
    'use strict';

    const navbar     = document.getElementById('navbar');
    const toggle     = document.getElementById('navbarToggle');
    const menu       = document.getElementById('navbarMenu');
    const dropdowns  = document.querySelectorAll('.navbar-dropdown');
    const isMobile   = () => window.matchMedia('(max-width: 768px)').matches;

    /* ---------- 1) فتح/إغلاق القائمة على الجوال ---------- */
    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            const isOpen = menu.classList.toggle('active');
            toggle.classList.toggle('active', isOpen);
            toggle.setAttribute('aria-expanded', isOpen);
            // منع تمرير الصفحة عند فتح القائمة على الجوال
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });
    }

    /* ---------- 2) فتح/إغلاق الـ Dropdown ---------- */
    dropdowns.forEach(function (dropdown) {
        const toggleBtn = dropdown.querySelector('.dropdown-toggle');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                // على الجوال: فتح/إغلاق
                if (isMobile()) {
                    // إغلاق باقي القوائم
                    dropdowns.forEach(d => {
                        if (d !== dropdown) d.classList.remove('open');
                    });
                    dropdown.classList.toggle('open');
                    const isOpen = dropdown.classList.contains('open');
                    toggleBtn.setAttribute('aria-expanded', isOpen);
                }
            });
        }
    });

    /* ---------- 3) إغلاق القوائم عند الضغط خارجها ---------- */
    document.addEventListener('click', function (e) {
        dropdowns.forEach(function (dropdown) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    });

    /* ---------- 4) إغلاق القائمة عند تغيير حجم الشاشة ---------- */
    window.addEventListener('resize', function () {
        if (!isMobile() && menu && menu.classList.contains('active')) {
            menu.classList.remove('active');
            toggle.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            dropdowns.forEach(d => d.classList.remove('open'));
        }
    });

    /* ---------- 5) إضافة ظل عند التمرير ---------- */
    if (navbar) {
        const onScroll = function () {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    /* ---------- 6) إغلاق التنبيهات تلقائيًا بعد 5 ثوانٍ ---------- */
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        const closeBtn = alert.querySelector('.alert-close');
        const remove   = () => {
            alert.style.transition = 'opacity .3s, transform .3s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        };
        if (closeBtn) closeBtn.addEventListener('click', remove);
        setTimeout(remove, 5000);
    });

})();