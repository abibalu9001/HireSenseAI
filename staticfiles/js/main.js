/* ── HireSense AI — Main JS ── */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss alerts ─────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // ── Mobile Sidebar Toggle ───────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Drag & Drop Upload ──────────────────────────
  const dropzone = document.getElementById('dropzone');
  if (dropzone) {
    const fileInput = dropzone.querySelector('input[type="file"]');
    const fileNameEl = document.getElementById('fileName');

    ['dragenter', 'dragover'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0 && fileInput) {
        // Use DataTransfer to assign files
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        fileInput.files = dt.files;
        updateFileName(files[0].name);
      }
    });

    if (fileInput) {
      fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
          updateFileName(fileInput.files[0].name);
        }
      });
    }

    function updateFileName(name) {
      if (fileNameEl) {
        fileNameEl.textContent = `📎 ${name}`;
        fileNameEl.style.color = 'var(--accent)';
        fileNameEl.style.fontWeight = '600';
      }
    }
  }

  // ── Score Bar Animations ────────────────────────
  const scoreBars = document.querySelectorAll('.score-bar-fill[data-width]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        bar.style.width = bar.dataset.width + '%';
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });

  scoreBars.forEach(bar => {
    bar.style.width = '0%';
    observer.observe(bar);
  });

  // ── Score Ring Animation ───────────────────────
  const scoreRings = document.querySelectorAll('.score-ring-circle[data-score]');
  scoreRings.forEach(ring => {
    const score = parseFloat(ring.dataset.score) || 0;
    const radius = parseFloat(ring.getAttribute('r'));
    const circumference = 2 * Math.PI * radius;
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = circumference;

    setTimeout(() => {
      const offset = circumference - (score / 100) * circumference;
      ring.style.transition = 'stroke-dashoffset 1.2s ease';
      ring.style.strokeDashoffset = offset;

      // Color based on score
      if (score >= 80)      ring.style.stroke = '#10b981';
      else if (score >= 65) ring.style.stroke = '#4f9cf9';
      else if (score >= 50) ring.style.stroke = '#f59e0b';
      else                  ring.style.stroke = '#ef4444';
    }, 300);
  });

  // ── Search input debounce ──────────────────────
  const searchInputs = document.querySelectorAll('.search-input');
  searchInputs.forEach(input => {
    let timer;
    input.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        input.closest('form')?.submit();
      }, 500);
    });
  });

  // ── Confirm delete modals ──────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm(btn.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Tooltip on hover ──────────────────────────
  document.querySelectorAll('[data-tooltip]').forEach(el => {
    el.addEventListener('mouseenter', () => {
      const tip = document.createElement('div');
      tip.className = 'tooltip-popup';
      tip.textContent = el.dataset.tooltip;
      tip.style.cssText = `
        position: fixed; background: #1a2540; color: #f0f4ff;
        padding: 5px 10px; border-radius: 6px; font-size: 12px;
        pointer-events: none; z-index: 9999; white-space: nowrap;
        border: 1px solid rgba(79,156,249,0.3);
      `;
      document.body.appendChild(tip);
      const rect = el.getBoundingClientRect();
      tip.style.left = rect.left + 'px';
      tip.style.top = (rect.bottom + 6) + 'px';
      el._tooltip = tip;
    });
    el.addEventListener('mouseleave', () => {
      el._tooltip?.remove();
    });
  });

  // ── Copy to clipboard ─────────────────────────
  document.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', () => {
      navigator.clipboard.writeText(btn.dataset.copy).then(() => {
        const orig = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 2000);
      });
    });
  });

  // ── Animate numbers (KPI counters) ────────────
  function animateCounter(el, target, duration = 1200) {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start = Math.min(start + step, target);
      el.textContent = Math.round(start) + (el.dataset.suffix || '');
      if (start >= target) clearInterval(timer);
    }, 16);
  }

  const kpiObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseFloat(el.dataset.count);
        if (!isNaN(target)) animateCounter(el, target);
        kpiObserver.unobserve(el);
      }
    });
  });

  document.querySelectorAll('[data-count]').forEach(el => kpiObserver.observe(el));

});
