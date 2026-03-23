/* =============================================================
   THE SCRIPTORIUM — shared.js
   Injects consistent nav, footer, newsletter + GA helpers
   on every landing page.
   Usage: <script src="shared.js"></script>  just before </body>
   Pass  data-page="australia"  on the <body> to highlight the
   correct nav link.
   ============================================================= */

(function () {
  'use strict';

  // ── helpers ────────────────────────────────────────────────
  const GA_ID = 'G-978827DY1C';
  const WORKER = 'https://scriptorium.scutt-rmit.workers.dev/';
  const GROUP  = '181263296197821532';

  // Current page slug (set via <body data-page="australia">)
  const PAGE = document.body.dataset.page || '';

  // ── inject GA if not already present ──────────────────────
  if (!document.querySelector('script[src*="googletagmanager"]')) {
    const s1 = document.createElement('script');
    s1.async = true;
    s1.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
    document.head.appendChild(s1);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ window.dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', GA_ID);
  }

  // ── nav links config ───────────────────────────────────────
  const NAV_LINKS = [
    { slug: 'home',        href: '/',                                        label: 'Home' },
    { slug: 'australia',   href: '/writing-competitions-australia.html',     label: '🇦🇺 Australia' },
    { slug: 'uk',          href: '/writing-competitions-uk.html',            label: '🇬🇧 United Kingdom' },
    { slug: 'usa',         href: '/writing-competitions-usa.html',           label: '🇺🇸 United States' },
    { slug: 'canada',      href: '/writing-competitions-canada.html',        label: '🇨🇦 Canada' },
    { slug: 'ireland',     href: '/writing-competitions-ireland.html',       label: '🇮🇪 Ireland' },
    { slug: 'nz',          href: '/writing-competitions-new-zealand.html',   label: '🇳🇿 New Zealand' },
    { slug: '2026',        href: '/writing-competitions-2026.html',          label: '📅 2026 Deadlines' },
    { slug: 'submit',      href: '/submit-competition.html',                 label: '+ Submit' },
  ];

  // ── NAV HTML ───────────────────────────────────────────────
  function buildNav() {
    const links = NAV_LINKS.map(l =>
      `<a href="${l.href}" class="s-nav-link${l.slug === PAGE ? ' s-active' : ''}">${l.label}</a>`
    ).join('');

    return `
<nav class="s-nav" id="s-nav">
  <div class="s-nav-inner">
    <a href="/" class="s-brand">
      <div class="s-brand-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="white" aria-hidden="true">
          <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 2v7l-2.5-1.5L12 11V4h5zm-5 16H6V4h4v9l3.5-2.1L17 13V4h1v16h-6z"/>
        </svg>
      </div>
      <span class="s-brand-name">The Scriptorium</span>
    </a>
    <button class="s-hamburger" id="s-hamburger" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <div class="s-nav-links" id="s-nav-links">
      ${links}
    </div>
    <a href="#s-newsletter" class="s-nav-cta">Subscribe free →</a>
  </div>
</nav>`;
  }

  // ── FOOTER HTML ────────────────────────────────────────────
  function buildFooter() {
    return `
<footer class="s-footer" id="s-newsletter">
  <div class="s-footer-inner">

    <div class="s-footer-top">

      <!-- Brand + newsletter -->
      <div class="s-footer-brand-col">
        <div class="s-footer-logo">
          <div class="s-brand-icon" style="width:30px;height:30px;border-radius:7px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white" aria-hidden="true">
              <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 2v7l-2.5-1.5L12 11V4h5zm-5 16H6V4h4v9l3.5-2.1L17 13V4h1v16h-6z"/>
            </svg>
          </div>
          <span class="s-footer-logo-name">The Scriptorium</span>
        </div>
        <p class="s-footer-desc">The world's most curated directory of writing competitions, festivals, and opportunities for serious writers.</p>

        <div class="s-nl-wrap" id="s-nl-wrap">
          <p class="s-nl-label">Weekly digest — free</p>
          <form class="s-nl-form" id="s-nl-form" onsubmit="window.sNLSubmit(event,'footer')">
            <input type="email" id="s-nl-email" placeholder="your@email.com" required autocomplete="email">
            <button type="submit" id="s-nl-btn">Join</button>
          </form>
          <select class="s-nl-country" id="s-nl-country">
            <option value="">Country (optional)</option>
            <option value="Australia">🇦🇺 Australia</option>
            <option value="New Zealand">🇳🇿 New Zealand</option>
            <option value="UK">🇬🇧 United Kingdom</option>
            <option value="Ireland">🇮🇪 Ireland</option>
            <option value="USA">🇺🇸 United States</option>
            <option value="Canada">🇨🇦 Canada</option>
            <option value="other">✏ Other…</option>
          </select>
          <input type="text" class="s-nl-other" id="s-nl-other" placeholder="Your country" style="display:none">
        </div>
        <div class="s-nl-success" id="s-nl-success" style="display:none">✓ You're subscribed! Check your inbox.</div>
      </div>

      <!-- Directory links -->
      <div class="s-footer-col">
        <h4>Directory</h4>
        <ul>
          <li><a href="/writing-competitions-australia.html">Australia</a></li>
          <li><a href="/writing-competitions-uk.html">United Kingdom</a></li>
          <li><a href="/writing-competitions-usa.html">United States</a></li>
          <li><a href="/writing-competitions-canada.html">Canada</a></li>
          <li><a href="/writing-competitions-ireland.html">Ireland</a></li>
          <li><a href="/writing-competitions-new-zealand.html">New Zealand</a></li>
          <li><a href="/writing-competitions-2026.html">2026 Deadlines</a></li>
        </ul>
      </div>

      <!-- Resources -->
      <div class="s-footer-col">
        <h4>Resources</h4>
        <ul>
          <li><a href="/writing-courses-melbourne.html">Writing Courses Melbourne</a></li>
          <li><a href="/">Writers Centres</a></li>
          <li><a href="/">Associations</a></li>
        </ul>
      </div>

      <!-- Site links -->
      <div class="s-footer-col">
        <h4>The Scriptorium</h4>
        <ul>
          <li><a href="/submit-competition.html">Submit a Competition</a></li>
          <li><a href="/">Broadcast to Writers</a></li>
          <li><a href="/">About</a></li>
        </ul>
      </div>

    </div><!-- /footer-top -->

    <div class="s-footer-bottom">
      <p>© 2026 The Scriptorium · Always verify details on official websites before submitting.</p>
      <div class="s-footer-legal">
        <a href="/">Privacy</a>
        <a href="/">Terms</a>
      </div>
    </div>

  </div>
</footer>`;
  }

  // ── STYLES ─────────────────────────────────────────────────
  const CSS = `
/* ── SHARED NAV ─────────────────────────────────────── */
.s-nav {
  background: rgba(248,246,246,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #ebe4e2;
  position: sticky;
  top: 0;
  z-index: 500;
  box-shadow: 0 1px 0 rgba(0,0,0,0.04);
}
.s-nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  height: 60px;
  gap: 0.25rem;
}
.s-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
  margin-right: 0.5rem;
}
.s-brand-icon {
  background: #ec4913;
  color: white;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.s-brand:hover .s-brand-icon { transform: rotate(6deg); }
.s-brand-name {
  font-size: 1rem;
  font-weight: 900;
  color: #1a1210;
  letter-spacing: -0.02em;
  white-space: nowrap;
}
.s-nav-links {
  display: flex;
  align-items: center;
  gap: 0;
  overflow-x: auto;
  scrollbar-width: none;
  flex: 1;
}
.s-nav-links::-webkit-scrollbar { display: none; }
.s-nav-link {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #5c4843;
  text-decoration: none;
  padding: 0.4rem 0.7rem;
  border-radius: 7px;
  white-space: nowrap;
  transition: all 0.15s;
  flex-shrink: 0;
}
.s-nav-link:hover { color: #1a1210; background: #f4f0ef; }
.s-nav-link.s-active { color: #ec4913; background: #fef3ef; }
.s-nav-cta {
  flex-shrink: 0;
  background: #ec4913;
  color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  text-decoration: none;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  margin-left: 0.5rem;
  white-space: nowrap;
  transition: background 0.15s;
}
.s-nav-cta:hover { background: #c93c0f; }
.s-hamburger {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  margin-left: auto;
  border-radius: 6px;
}
.s-hamburger span {
  display: block;
  width: 20px;
  height: 2px;
  background: #5c4843;
  border-radius: 2px;
  transition: all 0.2s;
}

/* ── SHARED FOOTER ───────────────────────────────────── */
.s-footer {
  background: #221510;
  color: rgba(255,255,255,0.45);
  padding: 3.5rem 1.5rem 2.5rem;
  margin-top: 0;
}
.s-footer-inner { max-width: 1280px; margin: 0 auto; }
.s-footer-top {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 2.5rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  margin-bottom: 2rem;
}
.s-footer-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.875rem;
}
.s-footer-logo-name { font-size: 1rem; font-weight: 900; color: white; }
.s-footer-desc {
  font-size: 0.8rem;
  line-height: 1.7;
  color: rgba(255,255,255,0.32);
  max-width: 230px;
  margin-bottom: 1.5rem;
}
.s-nl-label {
  font-size: 0.67rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.32);
  margin-bottom: 0.5rem;
}
.s-nl-form {
  display: flex;
  gap: 0.375rem;
  max-width: 260px;
  margin-bottom: 0.5rem;
}
.s-nl-form input {
  flex: 1;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 7px;
  padding: 0.5rem 0.75rem;
  font-family: inherit;
  font-size: 0.8rem;
  color: white;
  outline: none;
  min-width: 0;
}
.s-nl-form input::placeholder { color: rgba(255,255,255,0.25); }
.s-nl-form input:focus { border-color: #ec4913; }
.s-nl-form button {
  background: #ec4913;
  color: white;
  border: none;
  padding: 0.5rem 0.875rem;
  border-radius: 7px;
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.s-nl-form button:hover { background: #c93c0f; }
.s-nl-country {
  display: block;
  width: 100%;
  max-width: 260px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 7px;
  padding: 0.45rem 0.75rem;
  font-family: inherit;
  font-size: 0.8rem;
  color: rgba(255,255,255,0.6);
  outline: none;
  cursor: pointer;
  margin-top: 0.375rem;
}
.s-nl-country option { background: #221510; color: white; }
.s-nl-country:focus { border-color: #ec4913; }
.s-nl-other {
  display: none;
  width: 100%;
  max-width: 260px;
  margin-top: 0.375rem;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 7px;
  padding: 0.45rem 0.75rem;
  font-family: inherit;
  font-size: 0.8rem;
  color: white;
  outline: none;
}
.s-nl-other:focus { border-color: #ec4913; }
.s-nl-success { font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 0.625rem; }
.s-footer-col h4 {
  font-size: 0.67rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
  margin-bottom: 1rem;
}
.s-footer-col ul { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
.s-footer-col a {
  font-size: 0.8125rem;
  color: rgba(255,255,255,0.4);
  text-decoration: none;
  transition: color 0.15s;
}
.s-footer-col a:hover { color: white; }
.s-footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.s-footer-bottom p { font-size: 0.72rem; color: rgba(255,255,255,0.22); line-height: 1.6; }
.s-footer-legal { display: flex; gap: 1.25rem; }
.s-footer-legal a { font-size: 0.72rem; color: rgba(255,255,255,0.28); text-decoration: none; }
.s-footer-legal a:hover { color: rgba(255,255,255,0.6); }

/* ── RESPONSIVE ──────────────────────────────────────── */
@media (max-width: 900px) {
  .s-footer-top { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .s-hamburger { display: flex; }
  .s-nav-links {
    display: none;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background: white;
    border-bottom: 1px solid #ebe4e2;
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 0.25rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  }
  .s-nav-links.s-open { display: flex; }
  .s-nav-link { padding: 0.6rem 0.75rem; }
  .s-nav-cta { display: none; }
  .s-footer-top { grid-template-columns: 1fr; gap: 2rem; }
  .s-footer-bottom { flex-direction: column; text-align: center; }
}
`;

  // ── INJECT STYLES ─────────────────────────────────────────
  const styleTag = document.createElement('style');
  styleTag.textContent = CSS;
  document.head.appendChild(styleTag);

  // ── INJECT NAV (before first child of body) ───────────────
  const existingNav = document.querySelector('.site-nav');
  if (!existingNav) {
    document.body.insertAdjacentHTML('afterbegin', buildNav());
  }

  // ── INJECT FOOTER (before </body>) ────────────────────────
  const existingFooter = document.querySelector('.site-footer, .s-footer');
  if (!existingFooter) {
    document.body.insertAdjacentHTML('beforeend', buildFooter());
  }

  // ── HAMBURGER TOGGLE ──────────────────────────────────────
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('#s-hamburger');
    if (btn) {
      const links = document.getElementById('s-nav-links');
      const isOpen = links.classList.toggle('s-open');
      btn.setAttribute('aria-expanded', isOpen);
    }
  });

  // ── COUNTRY "OTHER" TOGGLE ────────────────────────────────
  const countrySelect = document.getElementById('s-nl-country');
  if (countrySelect) {
    countrySelect.addEventListener('change', function() {
      const other = document.getElementById('s-nl-other');
      if (other) other.style.display = this.value === 'other' ? 'block' : 'none';
    });
  }

  // ── NEWSLETTER SUBSCRIBE ──────────────────────────────────
  async function subscribeEmail(email, country) {
    const payload = { email, groups: [GROUP] };
    if (country && country !== 'other') payload.fields = { country };
    try {
      await fetch(WORKER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch(err) { console.warn('Subscribe error', err); }
  }

  window.sNLSubmit = async function(e, source) {
    e.preventDefault();
    const emailEl = document.getElementById('s-nl-email');
    const countryEl = document.getElementById('s-nl-country');
    const otherEl = document.getElementById('s-nl-other');
    const btn = document.getElementById('s-nl-btn');
    const wrap = document.getElementById('s-nl-wrap');
    const success = document.getElementById('s-nl-success');
    if (btn) { btn.textContent = '…'; btn.disabled = true; }
    const country = countryEl?.value === 'other'
      ? (otherEl?.value.trim() || '')
      : (countryEl?.value || '');
    await subscribeEmail(emailEl.value, country);
    if (wrap) wrap.style.display = 'none';
    if (success) success.style.display = 'block';
    if (typeof gtag !== 'undefined') {
      gtag('event', 'generate_lead', { method: 'newsletter_' + (source || 'page') });
    }
  };

})();
