/* ============================================================
   laos-sim · main.js
   Handles: mobile nav, table sort, smooth scroll, image fallbacks
   No frameworks — vanilla JS only.
   Site is fully usable with JS disabled (progressive enhancement).
   ============================================================ */

(function () {
  'use strict';

  /* ── Mobile nav toggle ─────────────────────────────────── */
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close on nav link click (mobile)
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });

    // Close on outside click
    document.addEventListener('click', e => {
      if (!navLinks.contains(e.target) && !toggle.contains(e.target)) {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  /* ── Sticky nav: add shadow on scroll ─────────────────── */
  const nav = document.querySelector('.site-nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── Table sort ────────────────────────────────────────── */
  const table = document.querySelector('table.comp-table');
  if (table) {
    const headers = table.querySelectorAll('thead th[data-sort]');
    let sortCol = -1;
    let sortDir = 1;

    headers.forEach((th, colIdx) => {
      th.style.cursor = 'pointer';
      th.title = 'Click to sort';

      th.addEventListener('click', () => {
        const tbody = table.querySelector('tbody');
        const rows  = Array.from(tbody.querySelectorAll('tr'));

        if (sortCol === colIdx) {
          sortDir *= -1;
        } else {
          sortCol = colIdx;
          sortDir = 1;
        }

        // Update sort indicators
        headers.forEach(h => h.removeAttribute('data-sorted'));
        th.setAttribute('data-sorted', sortDir === 1 ? 'asc' : 'desc');

        rows.sort((a, b) => {
          const aText = a.cells[colIdx]?.textContent.trim() ?? '';
          const bText = b.cells[colIdx]?.textContent.trim() ?? '';

          // Try numeric sort first
          const aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
          const bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));

          if (!isNaN(aNum) && !isNaN(bNum)) {
            return (aNum - bNum) * sortDir;
          }
          return aText.localeCompare(bText) * sortDir;
        });

        rows.forEach(r => tbody.appendChild(r));
      });
    });
  }

  /* ── Image error fallback ──────────────────────────────── */
  document.querySelectorAll('img[data-fallback-bg]').forEach(img => {
    img.addEventListener('error', () => {
      const parent = img.parentElement;
      if (parent) {
        parent.style.background = img.dataset.fallbackBg;
        img.style.display = 'none';
      }
    });
  });

  /* ── Lazy-load images with IntersectionObserver ────────── */
  if ('IntersectionObserver' in window) {
    const lazyImgs = document.querySelectorAll('img[data-src]');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const img = e.target;
          img.src = img.dataset.src;
          if (img.dataset.srcset) img.srcset = img.dataset.srcset;
          obs.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });

    lazyImgs.forEach(img => observer.observe(img));
  } else {
    // Fallback: load all immediately
    document.querySelectorAll('img[data-src]').forEach(img => {
      img.src = img.dataset.src;
    });
  }

  /* ── Smooth scroll for anchor links ───────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 70; // nav height
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

})();
