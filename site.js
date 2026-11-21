/* Gentle website: theme picker, low-stimulus switch, mobile menu, and screenshots that follow the theme. */
(function () {
  var root = document.documentElement;

  // The Today screen in each theme.
  var shots = {
    calm: ['img/app/today-light.jpg', 'Light', 'dark'],
    dark: ['img/app/today-dark.jpg', 'Dark', 'light'],
    pink: ['img/app/today-pink.jpg', 'Pink', 'dark'],
    y2k: ['img/app/today-y2k.jpg', 'Y2K sparkle', 'dark'],
    aero: ['img/app/today-aero.jpg', 'Frutiger Aero', 'dark']
  };
  var themeColours = { calm: '#F4F1EA', dark: '#121614', pink: '#FFE6F3', y2k: '#FFE6F2', aero: '#8FD3FF' };
  var lowColours = { light: '#E7E5E0', dark: '#0B0C0C' };

  // Gentle moving decorations for Y2K sparkle and Frutiger Aero, like the app's own but fewer and slower.
  // The CSS hides them in low-stimulus mode and stills them for anyone whose device asks for reduced motion.
  var PASTELS = ['#FFB8DA', '#FFD3B5', '#FFF1A8', '#BDF2D5', '#B9DCFF', '#DCC6FF'];
  var SPARK = '<svg viewBox="-10 -10 20 20"><path d="M0-10C.8-3 3-.8 10 0 3 .8.8 3 0 10-.8 3-3 .8-10 0-3-.8-.8-3 0-10Z"/></svg>';
  var STAR = '<svg viewBox="-12 -12 24 24"><path d="M0-10.5 3-3.6 10.4-3.2 4.6 1.5 6.5 8.6 0 4.6-6.5 8.6-4.6 1.5-10.4-3.2-3-3.6Z"/></svg>';
  var HEART = '<svg viewBox="-12 -12 24 24"><path d="M0 9C-7 4-10 0-10-4c0-3.3 2.6-5.6 5.4-5.6 2.1 0 3.6 1.2 4.6 2.9 1-1.7 2.5-2.9 4.6-2.9C7.4-9.6 10-7.3 10-4c0 4-3 8-10 13Z"/></svg>';
  var FLY = '<svg viewBox="-20 -16 40 32"><path class="w1" d="M-1-1C-8-15-19-12-17-4-16 1-8 1-1-1Z"/><path class="w2" d="M-1 1C-7 2-14 6-12 11-9 15-3 9-1 1Z"/>' +
    '<path class="w1" d="M1-1C8-15 19-12 17-4 16 1 8 1 1-1Z"/><path class="w2" d="M1 1C7 2 14 6 12 11 9 15 3 9 1 1Z"/></svg>';
  var decorFor = null;
  // A puffy cumulus cloud: overlapping puffs in one shape, white on top shading to pale blue underneath, softened at
  // the edge, with a faint glossy sheen on the biggest puff. Each one needs its own gradient and filter ids.
  function cloudSvg(i) {
    return '<svg viewBox="0 0 220 110"><defs>' +
      '<linearGradient id="cg' + i + '" x1="0" y1="14" x2="0" y2="96" gradientUnits="userSpaceOnUse">' +
      '<stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#D4EBFF"/></linearGradient>' +
      '<filter id="cs' + i + '" x="-10%" y="-15%" width="120%" height="135%"><feGaussianBlur stdDeviation="1.3"/></filter></defs>' +
      '<g fill="url(#cg' + i + ')" filter="url(#cs' + i + ')"><circle cx="58" cy="66" r="28"/><circle cx="95" cy="48" r="36"/>' +
      '<circle cx="138" cy="54" r="31"/><circle cx="172" cy="70" r="22"/><rect x="34" y="62" width="160" height="32" rx="16"/></g>' +
      '<ellipse cx="86" cy="30" rx="17" ry="6" fill="#fff" opacity=".7"/></svg>';
  }

  function seeded(seed) { return function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }
  function piece(layer, cls, inner, style) {
    var el = document.createElement('span');
    el.className = cls;
    el.innerHTML = inner;
    el.setAttribute('style', style);
    layer.appendChild(el);
  }

  function decor(t, low) {
    var want = !low && (t === 'y2k' || t === 'aero') ? t : null;
    if (want === decorFor) return;
    var old = document.querySelector('.decor');
    if (old) old.parentNode.removeChild(old);
    decorFor = want;
    if (!want) return;
    var layer = document.createElement('div');
    layer.className = 'decor decor-' + want;
    layer.setAttribute('aria-hidden', 'true');
    var r = seeded(want === 'y2k' ? 2003 : 2009);
    var edge = function () { return r() < 0.5 ? 1 + r() * 9 : 90 + r() * 8; };
    var i;
    if (want === 'y2k') {
      piece(layer, 'sheen', '', '');
      for (i = 0; i < 16; i++) piece(layer, 'glint', '', 'left:' + r() * 100 + '%;top:' + r() * 100 + '%;--d:' + (3 + r() * 4) + 's;--delay:-' + r() * 7 + 's');
      for (i = 0; i < 9; i++) piece(layer, 'spark', SPARK, 'left:' + r() * 100 + '%;top:' + r() * 100 + '%;--s:' + (10 + r() * 14) + 'px;--d:' + (6 + r() * 5) + 's;--delay:-' + r() * 11 + 's');
      for (i = 0; i < 6; i++) piece(layer, 'sticker', i % 2 ? HEART : STAR, 'left:' + edge() + '%;top:' + (10 + r() * 80) + '%;--s:' + (24 + r() * 18) + 'px;--c:' + PASTELS[i % 6] + ';--d:' + (7 + r() * 5) + 's;--delay:-' + r() * 10 + 's');
      for (i = 0; i < 2; i++) piece(layer, 'fly', '<span class="fly-bob">' + FLY + '</span>', 'top:' + (18 + r() * 60) + '%;--d:' + (80 + r() * 30) + 's;--delay:-' + r() * 90 + 's;--a:' + PASTELS[i * 2] + ';--b:' + PASTELS[i * 2 + 1]);
    } else {
      for (i = 0; i < 3; i++) piece(layer, 'cloud', cloudSvg(i), 'top:' + (6 + i * 9 + r() * 6) + '%;--s:' + (170 + r() * 110) + 'px;--d:' + (150 + r() * 80) + 's;--delay:-' + (i * 70 + r() * 40) + 's');
      for (i = 0; i < 7; i++) piece(layer, 'bokeh', '', 'left:' + r() * 100 + '%;top:' + (12 + r() * 70) + '%;--s:' + (40 + r() * 90) + 'px;--d:' + (9 + r() * 6) + 's;--delay:-' + r() * 12 + 's');
      for (i = 0; i < 11; i++) piece(layer, 'bubble', '<span></span>', 'left:' + r() * 100 + '%;--s:' + (14 + r() * 44) + 'px;--d:' + (50 + r() * 40) + 's;--delay:-' + r() * 90 + 's;--sway:' + (5 + r() * 4) + 's');
    }
    document.body.insertBefore(layer, document.body.firstChild);
  }

  function save(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* it just won't be remembered */ }
  }

  function paint() {
    var t = root.getAttribute('data-theme');
    var low = root.getAttribute('data-low') === 'on';
    document.querySelectorAll('[data-set-theme]').forEach(function (b) {
      b.setAttribute('aria-checked', b.getAttribute('data-set-theme') === t ? 'true' : 'false');
    });
    var lowToggle = document.getElementById('low-toggle');
    if (lowToggle) lowToggle.setAttribute('aria-checked', low ? 'true' : 'false');
    document.querySelectorAll('img[data-shot="today"]').forEach(function (img) {
      var v = img.getAttribute('data-v');
      var want = shots[t][0] + (v ? '?v=' + v : '');
      if (img.getAttribute('src') !== want) img.setAttribute('src', want);
      var phone = img.closest('.phone');
      if (phone) phone.setAttribute('data-ink', shots[t][2]);
    });
    document.querySelectorAll('[data-shot-caption]').forEach(function (el) {
      el.textContent = "Gentle's Today screen in its " + shots[t][1] + ' theme, with sample data.';
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', low ? lowColours[t === 'dark' ? 'dark' : 'light'] : themeColours[t]);
    decor(t, low);
  }

  function applyTheme(t) {
    if (!shots[t]) t = 'aero';
    root.setAttribute('data-theme', t);
    save('gentle-theme', t);
    paint();
  }

  function applyLow(on) {
    if (on) root.setAttribute('data-low', 'on'); else root.removeAttribute('data-low');
    save('gentle-low', on ? 'on' : 'off');
    paint();
  }

  if (!shots[root.getAttribute('data-theme')]) root.setAttribute('data-theme', 'aero');
  paint();

  // Theme picker
  var toggle = document.getElementById('theme-toggle');
  var menu = document.getElementById('theme-menu');
  function closeMenu() { if (menu && !menu.hidden) { menu.hidden = true; toggle.setAttribute('aria-expanded', 'false'); } }
  if (toggle && menu) {
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      closeSubs();
      var open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) { var cur = menu.querySelector('[aria-checked="true"]'); if (cur) cur.focus(); }
    });
    menu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-set-theme]');
      if (b) { applyTheme(b.getAttribute('data-set-theme')); closeMenu(); toggle.focus(); return; }
      if (e.target.closest('#low-toggle')) applyLow(root.getAttribute('data-low') !== 'on');
    });
    document.addEventListener('click', function (e) { if (!menu.contains(e.target)) closeMenu(); });
  }

  // Dropdowns in the top bar ("How it works", "Who it's for"). In the phone menu they're shown open, as plain lists.
  function closeSubs(except) {
    document.querySelectorAll('.sub-toggle[aria-expanded="true"]').forEach(function (b) {
      if (b === except) return;
      b.setAttribute('aria-expanded', 'false');
      document.getElementById(b.getAttribute('aria-controls')).hidden = true;
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var sub = document.getElementById(b.getAttribute('aria-controls'));
      var open = b.getAttribute('aria-expanded') !== 'true';
      closeSubs(b);
      closeMenu();
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      sub.hidden = !open;
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.has-sub')) closeSubs(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeMenu(); closeNav(); closeSubs(); } });

  // Mobile menu
  var menuToggle = document.getElementById('menu-toggle');
  var navLinks = document.getElementById('nav-links');
  function closeNav() { root.classList.remove('nav-open'); closeSubs(); if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false'); }
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      closeMenu();
      var open = !root.classList.contains('nav-open');
      root.classList.toggle('nav-open', open);
      menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      // Open the group holding the page you're on, so it's one tap away.
      var here = open && document.querySelector('.has-sub.current > .sub-toggle');
      if (here) { here.setAttribute('aria-expanded', 'true'); document.getElementById(here.getAttribute('aria-controls')).hidden = false; }
      if (!open) closeSubs();
    });
    navLinks.addEventListener('click', function (e) { if (e.target.closest('a')) closeNav(); });
    // Tapping the dimmed page outside the top bar closes the menu.
    document.addEventListener('click', function (e) { if (root.classList.contains('nav-open') && !e.target.closest('.site-nav')) closeNav(); });
  }
  // Cookies for the website's analytics: Google Analytics (through Google Tag Manager) and Microsoft Clarity.
  // UK and EU law needs a yes before these load, so nothing loads until the visitor accepts. The choice is kept in
  // this browser and can be changed from "Cookie settings" in the footer. The Gentle app itself has no analytics.
  var CONSENT_KEY = 'gentle-cookies';
  var body = document.body;
  var gtmId = body.getAttribute('data-gtm');
  var clarityId = body.getAttribute('data-clarity');
  var loaded = false;

  function getConsent() { try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; } }

  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    if (gtmId) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
      var g = document.createElement('script');
      g.async = true;
      g.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(gtmId);
      document.head.appendChild(g);
    }
    if (clarityId) {
      window.clarity = window.clarity || function () { (window.clarity.q = window.clarity.q || []).push(arguments); };
      var c = document.createElement('script');
      c.async = true;
      c.src = 'https://www.clarity.ms/tag/' + encodeURIComponent(clarityId);
      document.head.appendChild(c);
      window.clarity('consentv2', { ad_Storage: 'denied', analytics_Storage: 'granted' });
    }
  }

  function clearAnalyticsCookies() {
    document.cookie.split(';').forEach(function (part) {
      var name = part.split('=')[0].trim();
      if (/^(_ga|_gid|_gat|_clck|_clsk|CLID|MUID)/.test(name)) {
        var gone = '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
        document.cookie = name + gone;
        document.cookie = name + gone + '; domain=' + location.hostname;
        document.cookie = name + gone + '; domain=.' + location.hostname;
      }
    });
  }

  function choose(value) {
    var before = getConsent();
    try { localStorage.setItem(CONSENT_KEY, value); } catch (e) { /* asked again next visit */ }
    hideBanner();
    if (value === 'granted') {
      loadAnalytics();
    } else if (before === 'granted' || loaded) {
      // Changed their mind: tell both services, remove their cookies, and reload so nothing keeps running.
      if (window.gtag) window.gtag('consent', 'update', { analytics_storage: 'denied' });
      if (window.clarity) window.clarity('consentv2', { ad_Storage: 'denied', analytics_Storage: 'denied' });
      clearAnalyticsCookies();
      location.reload();
    }
  }

  var banner = null;
  function hideBanner() { if (banner) { banner.parentNode.removeChild(banner); banner = null; } }
  function showBanner() {
    if (banner || !(gtmId || clarityId)) return;
    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookies');
    banner.innerHTML =
      '<p><strong>Help me improve Gentle?</strong> It\'s free and made by one person, so seeing which pages people use, ' +
      'and where they get stuck, is how I know what to fix next. This uses cookies from Google Analytics and Microsoft Clarity, ' +
      'and only if you say yes. <a href="privacy.html#website">More about this</a></p>' +
      '<div class="cookie-actions">' +
      '<button type="button" class="btn btn-quiet" data-consent="denied">No thanks</button>' +
      '<button type="button" class="btn btn-quiet" data-consent="granted">Yes, happy to help</button>' +
      '</div>';
    banner.addEventListener('click', function (e) {
      var b = e.target.closest('[data-consent]');
      if (b) choose(b.getAttribute('data-consent'));
    });
    body.appendChild(banner);
  }

  var choice = getConsent();
  if (choice === 'granted') loadAnalytics();
  else if (choice !== 'denied') showBanner();
  var settings = document.getElementById('cookie-settings');
  if (settings) settings.addEventListener('click', function () { showBanner(); var first = banner && banner.querySelector('button'); if (first) first.focus(); });
})();
