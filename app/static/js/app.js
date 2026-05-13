// === Виниловая Гавань — UI скрипты ===

// Тема (светлая/тёмная)
(function () {
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  let mode = (() => {
    try { return localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light'); }
    catch (e) { return 'light'; }
  })();
  root.setAttribute('data-theme', mode);
  setIcon();
  if (toggle) toggle.addEventListener('click', () => {
    mode = mode === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', mode);
    try { localStorage.setItem('theme', mode); } catch (e) {}
    setIcon();
  });
  function setIcon() {
    if (!toggle) return;
    toggle.innerHTML = mode === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
})();

// Режим для слабовидящих
(function () {
  const btn = document.querySelector('[data-vision-toggle]');
  let on = false;
  try { on = localStorage.getItem('vision') === '1'; } catch (e) {}
  if (on) document.body.classList.add('vision-mode');
  if (btn) btn.addEventListener('click', () => {
    on = !on;
    document.body.classList.toggle('vision-mode', on);
    try { localStorage.setItem('vision', on ? '1' : '0'); } catch (e) {}
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
})();

// Mobile menu
(function () {
  const t = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('.nav-main');
  if (t && nav) t.addEventListener('click', () => nav.classList.toggle('is-open'));
})();

// Слайдер на главной
(function () {
  const slider = document.querySelector('[data-slider]');
  if (!slider) return;
  const track = slider.querySelector('.slider-track');
  const slides = slider.querySelectorAll('.slide');
  const dots = slider.querySelectorAll('.slider-dots button');
  const prev = slider.querySelector('[data-prev]');
  const next = slider.querySelector('[data-next]');
  let i = 0;
  const total = slides.length;
  if (total === 0) return;
  function go(n) {
    i = (n + total) % total;
    track.style.transform = `translateX(-${i * 100}%)`;
    dots.forEach((d, idx) => d.classList.toggle('active', idx === i));
  }
  if (prev) prev.addEventListener('click', () => go(i - 1));
  if (next) next.addEventListener('click', () => go(i + 1));
  dots.forEach((d, idx) => d.addEventListener('click', () => go(idx)));
  let auto = setInterval(() => go(i + 1), 6000);
  slider.addEventListener('mouseenter', () => clearInterval(auto));
  slider.addEventListener('mouseleave', () => { auto = setInterval(() => go(i + 1), 6000); });
  go(0);
})();

// Поиск с подсказками
(function () {
  const input = document.querySelector('[data-search-input]');
  const box = document.querySelector('[data-suggestions]');
  if (!input || !box) return;
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) { box.classList.remove('is-open'); box.innerHTML = ''; return; }
    timer = setTimeout(async () => {
      try {
        const res = await fetch('/api/suggest?q=' + encodeURIComponent(q));
        const data = await res.json();
        let html = '';
        if (data.products && data.products.length) {
          html += '<h4>Товары / Products</h4>';
          data.products.forEach(p => {
            html += `<a href="${p.url}"><span class="price">${Math.round(p.price).toLocaleString('ru-RU')} ₽</span>${p.name}</a>`;
          });
        }
        if (data.news && data.news.length) {
          html += '<h4>Новости / News</h4>';
          data.news.forEach(n => { html += `<a href="${n.url}">${n.title}</a>`; });
        }
        if (!html) html = '<h4>Ничего не найдено</h4>';
        box.innerHTML = html;
        box.classList.add('is-open');
      } catch (e) {}
    }, 200);
  });
  document.addEventListener('click', (e) => {
    if (!box.contains(e.target) && e.target !== input) box.classList.remove('is-open');
  });
  input.addEventListener('focus', () => { if (input.value.trim().length >= 2 && box.innerHTML) box.classList.add('is-open'); });
})();

// Drop-zone аватара
(function () {
  document.querySelectorAll('.avatar-drop').forEach(zone => {
    const input = zone.querySelector('input[type=file]');
    if (!input) return;
    zone.addEventListener('click', () => input.click());
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.style.borderColor = 'var(--color-primary)'; });
    zone.addEventListener('dragleave', () => { zone.style.borderColor = 'var(--color-border)'; });
    zone.addEventListener('drop', e => {
      e.preventDefault();
      if (e.dataTransfer.files.length) input.files = e.dataTransfer.files;
      updateLabel();
    });
    input.addEventListener('change', updateLabel);
    function updateLabel() {
      const lbl = zone.querySelector('.label');
      if (input.files && input.files[0] && lbl) lbl.textContent = input.files[0].name;
    }
  });
})();

// Внешние новости (раздел в корзине)
(function () {
  const btn = document.querySelector('[data-external-news]');
  const box = document.querySelector('[data-external-news-box]');
  if (!btn || !box) return;
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.textContent = 'Загружаем…';
    try {
      const res = await fetch('/api/external-news');
      const data = await res.json();
      let html = '<div class="news-grid" style="margin-top: 1rem;">';
      data.items.forEach(n => {
        html += `<a href="${n.url}" class="news-card"><div class="card-body"><h3>${n.title_ru}</h3><div class="meta">★ ${n.rating}</div></div></a>`;
      });
      html += '</div>';
      box.innerHTML = html;
    } catch (e) {
      box.textContent = 'Не удалось загрузить.';
    } finally { btn.disabled = false; btn.textContent = 'Подобрать ещё'; }
  });
})();

// Авто-скрытие flash-сообщений
(function () {
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(f => {
      f.style.opacity = '0';
      f.style.transition = 'opacity 0.4s';
      setTimeout(() => f.remove(), 500);
    });
  }, 5000);
})();
