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

// === Патч 1 ===========================================================

// Язык кнопок (для ариа-лейблов). Берём из <html lang>.
const LANG = (document.documentElement.lang || 'ru').toLowerCase().startsWith('en') ? 'en' : 'ru';
const L = {
  ru: { show: 'Показать пароль', hide: 'Скрыть пароль' },
  en: { show: 'Show password', hide: 'Hide password' },
}[LANG];

// === Кнопка «показать пароль» — оборачиваем любой input[type=password] ===
(function () {
  const EYE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
  const EYE_OFF = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 3l18 18M10.5 6.2A10 10 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-3.3 4M6.6 6.6A17 17 0 0 0 2 12s3.5 6 10 6c1.6 0 3-.3 4.3-.8"/><path d="M14.1 14.1A3 3 0 0 1 9.9 9.9"/></svg>';
  document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.dataset.pwReady) return;
    input.dataset.pwReady = '1';
    const wrap = document.createElement('div');
    wrap.className = 'pw-wrap';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pw-toggle';
    btn.setAttribute('aria-label', L.show);
    btn.title = L.show;
    btn.innerHTML = EYE;
    btn.addEventListener('click', () => {
      const shown = input.type === 'text';
      input.type = shown ? 'password' : 'text';
      btn.innerHTML = shown ? EYE : EYE_OFF;
      btn.setAttribute('aria-label', shown ? L.show : L.hide);
      btn.title = shown ? L.show : L.hide;
      btn.setAttribute('aria-pressed', shown ? 'false' : 'true');
    });
    wrap.appendChild(btn);
  });
})();

// === Маска телефона +7 (___) ___-__-__ ===
(function () {
  function format(digits) {
    // нормализуем: любая ведущая “8” → “7”, обрезаем по 11
    let d = digits.replace(/\D/g, '');
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (d.length && !d.startsWith('7')) d = '7' + d;
    d = d.slice(0, 11);
    let out = '+7';
    if (d.length > 1) out += ' (' + d.slice(1, 4);
    if (d.length >= 4) out += ')';
    if (d.length >= 5) out += ' ' + d.slice(4, 7);
    if (d.length >= 8) out += '-' + d.slice(7, 9);
    if (d.length >= 10) out += '-' + d.slice(9, 11);
    return out;
  }
  function apply(input) {
    if (input.dataset.maskReady) return;
    input.dataset.maskReady = '1';
    input.setAttribute('inputmode', 'tel');
    input.setAttribute('placeholder', '+7 (___) ___-__-__');
    const reformat = () => {
      const v = input.value;
      if (!v) return;
      input.value = format(v);
    };
    input.addEventListener('input', reformat);
    input.addEventListener('focus', () => { if (!input.value) input.value = '+7 ('; });
    input.addEventListener('blur', () => { if (input.value.replace(/\D/g, '').length <= 1) input.value = ''; });
    if (input.value) reformat();
  }
  document.querySelectorAll('input[type="tel"], input[name="phone"], [data-phone]').forEach(apply);
})();

// === Модалка «Скоро откроем» для data-soon ссылок (ВК / МАКС) ===
(function () {
  const overlay = document.querySelector('[data-soon-modal]');
  if (!overlay) return;
  const closeBtn = overlay.querySelector('[data-soon-close]');
  const iconBox = overlay.querySelector('[data-soon-icon]');
  const ICONS = {
    vk: '<svg width="36" height="36" viewBox="0 0 32 32" fill="currentColor"><text x="16" y="22" text-anchor="middle" font-family="Inter, sans-serif" font-weight="800" font-size="15">VK</text></svg>',
    max: '<svg width="36" height="36" viewBox="0 0 32 32" fill="currentColor"><text x="16" y="22" text-anchor="middle" font-family="Inter, sans-serif" font-weight="800" font-size="13">MAX</text></svg>',
    default: '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  };
  function open(kind) {
    if (iconBox) iconBox.innerHTML = ICONS[kind] || ICONS.default;
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.classList.add('is-open'));
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    setTimeout(() => { overlay.hidden = true; }, 220);
  }
  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-soon]');
    if (!a) return;
    e.preventDefault();
    open(a.dataset.soon);
  });
  if (closeBtn) closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !overlay.hidden) close(); });
})();
