#!/usr/bin/env python3
"""
The Scriptorium — Static Page Generator
========================================
Reads competitions.json and resources.json, outputs fully pre-rendered
HTML landing pages. No client-side data fetching required — every card
is in the source HTML for instant Google indexing.

Usage:
  python3 generate.py

Output: writes directly to the current directory (repo root).
Run from: /Users/craigscutt/Documents/GitHub/thescriptorium/
"""

import json, html, os, re
from datetime import date

# ── config ────────────────────────────────────────────────────────────────────
BASE_URL   = 'https://www.thescriptorium.com.au'
GA_ID      = 'G-978827DY1C'
WORKER_URL = 'https://scriptorium.scutt-rmit.workers.dev/'
NL_GROUP   = '181263296197821532'
TODAY      = date.today().isoformat()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ── helpers ───────────────────────────────────────────────────────────────────
FLAGS = {
    'Australia': '🇦🇺', 'UK': '🇬🇧', 'USA': '🇺🇸',
    'Canada': '🇨🇦', 'Ireland': '🇮🇪', 'New Zealand': '🇳🇿',
    'International': '🌐',
}
TYPE_LABELS = {
    'short-story':   'Short Story',
    'novel':         'Complete Novel',
    'novel-extract': 'Novel Extract',
    'flash':         'Flash Fiction',
    'poetry':        'Poetry',
    'screenplay':    'Screenplay',
}
PRESTIGE_LABELS = {'high': 'High Prestige', 'mid': 'Mid Prestige', 'low': 'Emerging'}
RES_TYPE_LABELS = {
    'writers-centre': 'Writers Centre',
    'association':    'Association',
    'training':       'Training',
    'festival':       'Festival & Event',
}

def esc(s):
    """HTML-escape a string safely."""
    return html.escape(str(s or ''), quote=True)

def safe(s, maxlen=165):
    """Truncate and escape for card body."""
    s = str(s or '')
    if len(s) > maxlen:
        s = s[:maxlen].rstrip() + '…'
    return html.escape(s)

def is_upcoming(c):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
              'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12,
              'January':1,'February':2,'March':3,'April':4,'June':6,'July':7,
              'August':8,'September':9,'October':10,'November':11,'December':12}
    dl = (c.get('deadline') or '').strip()
    if not dl or dl.lower() in ('rolling', 'varies annually', 'see website'):
        return True
    m = re.search(r'([A-Za-z]+)\s+(\d{4})', dl)
    if m and m.group(1) in months:
        import datetime
        try:
            return datetime.date(int(m.group(2)), months[m.group(1)], 28) >= date.today()
        except:
            pass
    try:
        import datetime
        return datetime.date.fromisoformat(dl) >= date.today()
    except:
        return True  # unknown — include it


# ── competition card HTML ─────────────────────────────────────────────────────
def comp_card(c):
    p     = c.get('prestige', 'low')
    intl  = c.get('international', False)
    types = c.get('types', [])
    flag  = FLAGS.get(c.get('country', ''), '')

    intl_badge = (
        '<span class="badge badge-intl">✓ Intl.</span>'
        if intl else
        '<span class="badge badge-no-intl">Domestic</span>'
    )
    type_chips = ''.join(
        f'<span class="type-chip">{esc(TYPE_LABELS.get(t, t))}</span>'
        for t in types
    )
    fee = (
        '<span class="meta-val free">Free</span>'
        if c.get('entryFeeSort', 1) == 0
        else f'<span class="meta-val">{esc(c.get("entryFeeNote", "See website"))}</span>'
    )
    link = (
        f'<a class="card-link" href="{esc(c["url"])}" target="_blank" rel="noopener">Visit site →</a>'
        if c.get('url') else ''
    )
    return f'''<div class="card prestige-{esc(p)}" data-types="{esc(",".join(types))}" data-country="{esc(c.get("country",""))}" data-prestige="{esc(p)}">
  <div class="card-badges">
    <span class="badge badge-country">{flag} {esc(c.get("country",""))}</span>
    {intl_badge}
    <span class="badge badge-prestige-{esc(p)}">{esc(PRESTIGE_LABELS.get(p,"Emerging"))}</span>
  </div>
  <div class="card-title">{esc(c.get("name",""))}</div>
  <div class="card-org">{esc(c.get("org",""))}</div>
  <div class="card-types">{type_chips}</div>
  <p class="card-desc">{safe(c.get("description",""))}</p>
  <div class="card-meta">
    <div class="meta-item"><span class="meta-label">Entry Fee</span>{fee}</div>
    <div class="meta-item"><span class="meta-label">Prize</span><span class="meta-val prize">{esc(c.get("prize","—"))}</span></div>
  </div>
  <div class="card-footer">
    <span class="deadline-chip">Closes: {esc(c.get("deadline","See website"))}</span>
    {link}
  </div>
</div>'''


# ── resource card HTML ────────────────────────────────────────────────────────
def res_card(r):
    is_fest = r.get('type') == 'festival'
    flag    = FLAGS.get(r.get('country', ''), '')
    card_cls = 'card resource-festival' if is_fest else 'card'
    link_cls = 'card-link res-link' if is_fest else 'card-link'

    badge_style = (
        'background:#e8f7f5;color:#1a7a6e;border:1px solid rgba(26,122,110,.2);'
        if is_fest else
        'background:var(--primary-light);color:var(--primary);'
    )
    type_label = esc(RES_TYPE_LABELS.get(r.get('type', ''), r.get('type', '')))

    city = r.get('city') or ''
    when = r.get('when') or ''
    if is_fest:
        meta = f'<div class="card-org">{esc(city)}{"&nbsp;·&nbsp;" + esc(when) if city and when else esc(when) if when else ""}</div>' if city or when else ''
    else:
        meta = f'<div class="card-org">{esc(city)}</div>' if city else ''

    if r.get('membershipFrom'):
        fee_note = f'<span class="deadline-chip">{esc(r["membershipFrom"])}</span>'
    elif r.get('free'):
        fee_note = '<span class="deadline-chip free-note">Free to attend</span>'
    else:
        fee_note = '<span class="deadline-chip">See website</span>'

    link = f'<a class="{link_cls}" href="{esc(r["url"])}" target="_blank" rel="noopener">Visit site →</a>' if r.get('url') else ''

    return f'''<div class="{card_cls}" data-type="{esc(r.get("type",""))}" data-country="{esc(r.get("country",""))}">
  <div class="card-badges">
    <span class="badge badge-country">{flag} {esc(r.get("country",""))}</span>
    <span class="badge" style="{badge_style}">{type_label}</span>
  </div>
  <div class="card-title">{esc(r.get("name",""))}</div>
  {meta}
  <p class="card-desc" style="flex:1;">{safe(r.get("description",""))}</p>
  <div class="card-footer">{fee_note}{link}</div>
</div>'''


# ── shared CSS ────────────────────────────────────────────────────────────────
def shared_css():
    return '''
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#ec4913;--primary-hover:#c93c0f;--primary-light:#fef3ef;
  --bg:#f8f6f6;--bg-dark:#221510;
  --surface:#fff;--surface2:#f4f0ef;
  --border:#ebe4e2;--border-strong:#d5c8c5;
  --text:#1a1210;--text-2:#5c4843;--text-3:#9c837e;
  --green:#2d7a4f;--green-light:#edf7f2;
  --teal:#1a7a6e;--teal-light:#e8f7f5;
  --radius:12px;--radius-sm:8px;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 4px 16px rgba(0,0,0,.05);
  --shadow-hover:0 8px 24px rgba(0,0,0,.1),0 2px 6px rgba(0,0,0,.06);
  --shadow-primary:0 4px 14px rgba(236,73,19,.25);
}
html{scroll-behavior:smooth}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}

/* NAV */
.site-nav{background:rgba(248,246,246,.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:500}
.nav-inner{max-width:1200px;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;height:60px;gap:.25rem}
.nav-brand{display:flex;align-items:center;gap:.5rem;text-decoration:none;flex-shrink:0;margin-right:.5rem}
.nav-brand-icon{background:var(--primary);color:white;width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:transform .2s}
.nav-brand:hover .nav-brand-icon{transform:rotate(6deg)}
.nav-brand-name{font-size:1rem;font-weight:900;color:var(--text);letter-spacing:-.02em;white-space:nowrap}
.nav-links{display:flex;align-items:center;overflow-x:auto;scrollbar-width:none;flex:1}
.nav-links::-webkit-scrollbar{display:none}
.nav-link{font-size:.8rem;font-weight:600;color:var(--text-2);text-decoration:none;padding:.4rem .6rem;border-radius:7px;white-space:nowrap;transition:all .15s;flex-shrink:0}
.nav-link:hover{color:var(--text);background:var(--surface2)}
.nav-link.active{color:var(--primary);background:var(--primary-light)}
.nav-cta{flex-shrink:0;background:var(--primary);color:white;font-size:.8rem;font-weight:700;text-decoration:none;padding:.45rem 1rem;border-radius:8px;margin-left:.5rem;white-space:nowrap;transition:background .15s}
.nav-cta:hover{background:var(--primary-hover)}
.nav-hamburger{display:none;flex-direction:column;gap:4px;background:none;border:none;cursor:pointer;padding:6px;margin-left:auto;border-radius:6px}
.nav-hamburger span{display:block;width:20px;height:2px;background:var(--text-2);border-radius:2px;transition:all .2s}

/* HERO */
.hero{background:var(--primary);padding:3.25rem 2rem 2.75rem;text-align:center;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:600px;height:600px;background:radial-gradient(circle,rgba(255,255,255,.07) 0%,transparent 70%);pointer-events:none}
.hero-eyebrow{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.65);margin-bottom:.875rem}
.hero h1{font-size:clamp(1.75rem,4.5vw,2.75rem);font-weight:900;letter-spacing:-.03em;color:#fff;margin-bottom:.875rem;line-height:1.1}
.hero-intro{font-size:.9375rem;color:rgba(255,255,255,.85);max-width:560px;margin:0 auto .75rem;line-height:1.65}
.hero-sub{font-size:.8rem;color:rgba(255,255,255,.55);margin-top:.25rem}
.hero-sub strong{color:rgba(255,255,255,.8)}
.hero-stats{display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-top:1.75rem;padding-top:1.75rem;border-top:1px solid rgba(255,255,255,.15)}
.hero-stat{text-align:center}
.hero-stat-num{font-size:2rem;font-weight:900;color:#fff;letter-spacing:-.03em;line-height:1}
.hero-stat-label{font-size:.67rem;font-weight:600;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:.08em;margin-top:.25rem}

/* PAGE TABS */
.page-tabs{background:var(--surface);border-bottom:1px solid var(--border)}
.page-tabs-inner{max-width:1200px;margin:0 auto;padding:0 1.5rem;display:flex}
.page-tab{font-family:'Inter',sans-serif;font-size:.875rem;font-weight:700;color:var(--text-3);background:none;border:none;border-bottom:3px solid transparent;padding:.875rem 1.25rem .75rem;cursor:pointer;transition:all .15s;white-space:nowrap}
.page-tab:hover{color:var(--text-2)}
.page-tab.active{color:var(--primary);border-bottom-color:var(--primary)}

/* FILTER BARS */
.filter-bar{background:var(--surface2);border-bottom:1px solid var(--border);padding:.625rem 1.5rem;position:sticky;top:60px;z-index:100}
.filter-bar-inner{max-width:1200px;margin:0 auto;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}
.filter-label{font-size:.7rem;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:.07em;margin-right:.25rem;white-space:nowrap;flex-shrink:0}
.filter-btn{font-family:'Inter',sans-serif;font-size:.78rem;font-weight:600;padding:.35rem .9rem;border:1px solid var(--border);border-radius:99px;background:var(--surface);color:var(--text-2);cursor:pointer;transition:all .15s;white-space:nowrap}
.filter-btn:hover{border-color:var(--border-strong);background:var(--surface)}
.filter-btn.active{background:var(--primary);color:#fff;border-color:var(--primary);box-shadow:var(--shadow-primary)}
.filter-btn.fest-btn{border-color:rgba(26,122,110,.3);color:var(--teal)}
.filter-btn.fest-btn.active{background:var(--teal);border-color:var(--teal);color:#fff}
.search-box{font-family:'Inter',sans-serif;font-size:.85rem;padding:.38rem .9rem;border:1px solid var(--border);border-radius:99px;background:var(--bg);color:var(--text);outline:none;width:200px;transition:border-color .2s;margin-left:auto}
.search-box:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(236,73,19,.1);background:var(--surface)}

/* MAIN */
.main{max-width:1200px;margin:0 auto;padding:2.25rem 1.5rem 5rem}
.section{display:none}.section.active{display:block}
.results-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem;flex-wrap:wrap;gap:.75rem}
.results-count{font-size:.9rem;font-weight:700;color:var(--text)}
.results-count strong{color:var(--primary)}

/* CARD GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.375rem;display:flex;flex-direction:column;transition:box-shadow .2s,transform .2s,border-color .2s;position:relative;overflow:hidden}
.card:hover{box-shadow:var(--shadow-hover);transform:translateY(-2px);border-color:rgba(236,73,19,.2)}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:var(--radius) var(--radius) 0 0}
.prestige-high::before{background:var(--text)}
.prestige-mid::before{background:var(--primary)}
.prestige-low::before{background:var(--border-strong)}
.resource-festival::before{background:var(--teal)}
.resource-festival:hover{border-color:rgba(26,122,110,.25)}
.resource-festival:hover .card-title{color:var(--teal)}
.card.hidden{display:none}

/* BADGES */
.card-badges{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.75rem}
.badge{font-size:.67rem;font-weight:700;padding:.18rem .5rem;border-radius:4px;letter-spacing:.02em}
.badge-country{background:var(--surface2);color:var(--text-2);border:1px solid var(--border)}
.badge-intl{background:var(--green-light);color:var(--green)}
.badge-no-intl{background:var(--surface2);color:var(--text-3);border:1px solid var(--border)}
.badge-prestige-high{background:var(--text);color:white}
.badge-prestige-mid{background:var(--primary-light);color:var(--primary)}
.badge-prestige-low{background:var(--surface2);color:var(--text-3);border:1px solid var(--border)}

/* CARD BODY */
.card-title{font-size:1.0625rem;font-weight:800;line-height:1.3;color:var(--text);margin-bottom:.2rem;letter-spacing:-.01em;transition:color .15s}
.card:hover .card-title{color:var(--primary)}
.card-org{font-size:.75rem;color:var(--text-3);margin-bottom:.75rem}
.card-types{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.875rem}
.type-chip{font-size:.7rem;font-weight:500;padding:.18rem .6rem;background:var(--surface2);border:1px solid var(--border);border-radius:99px;color:var(--text-2)}
.card-desc{font-size:.8125rem;line-height:1.65;color:var(--text-2);flex:1;margin-bottom:1rem}
.card-meta{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;border-top:1px solid var(--border);padding-top:.875rem;margin-bottom:.875rem}
.meta-item{display:flex;flex-direction:column;gap:.2rem}
.meta-label{font-size:.64rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text-3)}
.meta-val{font-size:.8125rem;font-weight:600;color:var(--text)}
.meta-val.prize,.meta-val.free,.free-note{color:var(--green)}
.card-footer{display:flex;align-items:center;justify-content:space-between;padding-top:.875rem;border-top:1px solid var(--border);gap:.5rem}
.deadline-chip{font-size:.75rem;color:var(--text-3)}
.card-link{display:flex;align-items:center;gap:.3rem;font-size:.8rem;font-weight:700;color:var(--primary);text-decoration:none;padding:.35rem .875rem;border-radius:var(--radius-sm);background:var(--primary-light);transition:all .15s;white-space:nowrap}
.card-link:hover{background:var(--primary);color:white}
.res-link{color:var(--teal);background:var(--teal-light)}
.res-link:hover{background:var(--teal);color:white}

/* NO RESULTS */
.no-results{grid-column:1/-1;text-align:center;padding:3rem 2rem;color:var(--text-3);font-size:.9rem;display:none}
.no-results a{color:var(--primary);font-weight:700;text-decoration:none}

/* INFO SECTION */
.info-section{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:2rem;margin-top:3rem}
.info-section h2{font-size:1.375rem;font-weight:900;letter-spacing:-.02em;color:var(--text);margin-bottom:.875rem}
.info-section p{font-size:.875rem;color:var(--text-2);line-height:1.75;margin-bottom:.875rem}
.info-section p:last-child{margin-bottom:0}
.info-section a{color:var(--primary);font-weight:700;text-decoration:none}

/* NEWSLETTER */
.nl-band{background:var(--bg-dark);border-radius:var(--radius);padding:2.25rem;text-align:center;margin-top:1.5rem}
.nl-band h3{font-size:1.25rem;font-weight:900;color:white;margin-bottom:.375rem;letter-spacing:-.02em}
.nl-band p{font-size:.875rem;color:rgba(255,255,255,.45);margin-bottom:1.25rem}
.nl-form{display:flex;gap:.5rem;max-width:440px;margin:0 auto .5rem}
.nl-form input{flex:1;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:var(--radius-sm);padding:.6rem 1rem;font-family:'Inter',sans-serif;font-size:.875rem;color:white;outline:none;min-width:0}
.nl-form input::placeholder{color:rgba(255,255,255,.3)}
.nl-form input:focus{border-color:var(--primary)}
.nl-form button{background:var(--primary);color:white;border:none;padding:.6rem 1.25rem;border-radius:var(--radius-sm);font-family:'Inter',sans-serif;font-size:.875rem;font-weight:700;cursor:pointer;transition:background .15s;white-space:nowrap}
.nl-form button:hover{background:var(--primary-hover)}
.nl-country{display:block;width:100%;max-width:440px;margin:.5rem auto 0;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:var(--radius-sm);padding:.45rem .75rem;font-family:'Inter',sans-serif;font-size:.8rem;color:rgba(255,255,255,.6);outline:none;cursor:pointer}
.nl-country option{background:#221510;color:white}
.nl-country:focus{border-color:var(--primary)}
.nl-hint{font-size:.72rem;color:rgba(255,255,255,.25);margin-top:.5rem}
.nl-success{display:none;color:rgba(255,255,255,.7);font-size:.9rem;margin-top:.75rem}

/* CTA */
.cta-band{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:2rem;text-align:center;margin-top:1.5rem}
.cta-band h2{font-size:1.25rem;font-weight:900;letter-spacing:-.02em;color:var(--text);margin-bottom:.5rem}
.cta-band p{font-size:.875rem;color:var(--text-2);margin-bottom:1.25rem}
.btn{display:inline-block;background:var(--primary);color:#fff;font-family:'Inter',sans-serif;font-size:.875rem;font-weight:700;padding:.75rem 1.75rem;border-radius:var(--radius-sm);text-decoration:none;transition:all .15s;box-shadow:var(--shadow-primary)}
.btn:hover{background:var(--primary-hover);transform:translateY(-1px)}
.suggest-note{text-align:center;padding:1.25rem 0 .25rem;border-top:1px solid var(--border);margin-top:.5rem;font-size:.8125rem;color:var(--text-3)}
.suggest-note a{color:var(--primary);font-weight:700;text-decoration:none}

/* FOOTER */
.site-footer{background:var(--bg-dark);color:rgba(255,255,255,.45);padding:3.5rem 1.5rem 2.5rem}
.footer-inner{max-width:1200px;margin:0 auto}
.footer-top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:2.5rem;padding-bottom:2.5rem;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:2rem}
.footer-logo{display:flex;align-items:center;gap:.5rem;margin-bottom:.875rem}
.footer-logo-icon{background:var(--primary);color:white;width:30px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center}
.footer-logo-name{font-size:1rem;font-weight:900;color:white}
.footer-desc{font-size:.8rem;line-height:1.7;color:rgba(255,255,255,.32);max-width:230px;margin-bottom:1.5rem}
.footer-nl-label{font-size:.67rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.32);margin-bottom:.5rem}
.footer-nl-form{display:flex;gap:.375rem;max-width:260px;margin-bottom:.5rem}
.footer-nl-form input{flex:1;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:7px;padding:.5rem .75rem;font-family:'Inter',sans-serif;font-size:.8rem;color:white;outline:none;min-width:0}
.footer-nl-form input::placeholder{color:rgba(255,255,255,.25)}
.footer-nl-form input:focus{border-color:var(--primary)}
.footer-nl-form button{background:var(--primary);color:white;border:none;padding:.5rem .875rem;border-radius:7px;font-family:'Inter',sans-serif;font-size:.8rem;font-weight:700;cursor:pointer;transition:background .15s;white-space:nowrap}
.footer-nl-form button:hover{background:var(--primary-hover)}
.footer-nl-success{display:none;font-size:.8rem;color:rgba(255,255,255,.55);margin-top:.375rem}
.footer-col h4{font-size:.67rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:1rem}
.footer-col ul{list-style:none;display:flex;flex-direction:column;gap:.5rem}
.footer-col a{font-size:.8125rem;color:rgba(255,255,255,.4);text-decoration:none;transition:color .15s}
.footer-col a:hover{color:white}
.footer-bottom{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.footer-bottom p{font-size:.72rem;color:rgba(255,255,255,.22);line-height:1.6}
.footer-legal{display:flex;gap:1.25rem}
.footer-legal a{font-size:.72rem;color:rgba(255,255,255,.28);text-decoration:none}
.footer-legal a:hover{color:rgba(255,255,255,.6)}

/* RESPONSIVE */
@media(max-width:900px){.footer-top{grid-template-columns:1fr 1fr}}
@media(max-width:640px){
  .nav-hamburger{display:flex}
  .nav-links{display:none;position:absolute;top:60px;left:0;right:0;background:white;border-bottom:1px solid var(--border);padding:.75rem 1rem;flex-direction:column;gap:.25rem;box-shadow:0 8px 24px rgba(0,0,0,.08)}
  .nav-links.open{display:flex}
  .nav-cta{display:none}
  .hero{padding:2.5rem 1rem 2rem}
  .filter-bar{padding:.5rem 1rem}
  .search-box{width:100%;margin-left:0}
  .main{padding:1.5rem 1rem 3rem}
  .grid{grid-template-columns:1fr}
  .nl-form{flex-direction:column}
  .footer-top{grid-template-columns:1fr;gap:2rem}
  .footer-bottom{flex-direction:column;text-align:center}
}
'''


# ── shared nav HTML ───────────────────────────────────────────────────────────
NAV_LINKS = [
    ('home',       '/',                                       'Home'),
    ('australia',  '/writing-competitions-australia.html',    '🇦🇺 Australia'),
    ('uk',         '/writing-competitions-uk.html',           '🇬🇧 United Kingdom'),
    ('usa',        '/writing-competitions-usa.html',          '🇺🇸 United States'),
    ('canada',     '/writing-competitions-canada.html',       '🇨🇦 Canada'),
    ('ireland',    '/writing-competitions-ireland.html',      '🇮🇪 Ireland'),
    ('nz',         '/writing-competitions-new-zealand.html',  '🇳🇿 New Zealand'),
    ('2026',       '/writing-competitions-2026.html',         '📅 2026'),
    ('submit',     '/submit-competition.html',                '+ Submit'),
]

def nav_html(active_slug):
    links = ''.join(
        f'<a href="{href}" class="nav-link{"  active" if slug == active_slug else ""}">{label}</a>'
        for slug, href, label in NAV_LINKS
    )
    return f'''<nav class="site-nav">
  <div class="nav-inner">
    <a href="/" class="nav-brand">
      <div class="nav-brand-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="white" aria-hidden="true">
          <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 2v7l-2.5-1.5L12 11V4h5zm-5 16H6V4h4v9l3.5-2.1L17 13V4h1v16h-6z"/>
        </svg>
      </div>
      <span class="nav-brand-name">The Scriptorium</span>
    </a>
    <button class="nav-hamburger" id="nav-hamburger" aria-label="Toggle menu">
      <span></span><span></span><span></span>
    </button>
    <div class="nav-links" id="nav-links">{links}</div>
    <a href="#newsletter" class="nav-cta">Subscribe free →</a>
  </div>
</nav>'''


# ── shared footer HTML ────────────────────────────────────────────────────────
def footer_html():
    return f'''<footer class="site-footer" id="newsletter">
  <div class="footer-inner">
    <div class="footer-top">
      <div>
        <div class="footer-logo">
          <div class="footer-logo-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white" aria-hidden="true">
              <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 2v7l-2.5-1.5L12 11V4h5zm-5 16H6V4h4v9l3.5-2.1L17 13V4h1v16h-6z"/>
            </svg>
          </div>
          <span class="footer-logo-name">The Scriptorium</span>
        </div>
        <p class="footer-desc">The world's most curated directory of writing competitions, festivals, and opportunities for serious writers.</p>
        <div class="footer-nl-label">Weekly digest — free</div>
        <form class="footer-nl-form" id="footer-nl-form" onsubmit="handleNL(event,'footer')">
          <input type="email" id="footer-nl-email" placeholder="your@email.com" required autocomplete="email">
          <button type="submit">Join</button>
        </form>
        <select class="footer-nl-form" id="footer-nl-country" style="margin-top:.375rem;max-width:260px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:7px;padding:.45rem .75rem;font-family:inherit;font-size:.8rem;color:rgba(255,255,255,.6);outline:none;">
          <option value="">Country (optional)</option>
          <option value="Australia">🇦🇺 Australia</option>
          <option value="New Zealand">🇳🇿 New Zealand</option>
          <option value="UK">🇬🇧 United Kingdom</option>
          <option value="Ireland">🇮🇪 Ireland</option>
          <option value="USA">🇺🇸 United States</option>
          <option value="Canada">🇨🇦 Canada</option>
          <option value="other">✏ Other…</option>
        </select>
        <div class="footer-nl-success" id="footer-nl-success">✓ You're subscribed!</div>
      </div>
      <div class="footer-col">
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
      <div class="footer-col">
        <h4>Resources</h4>
        <ul>
          <li><a href="/writing-courses-melbourne.html">Writing Courses Melbourne</a></li>
          <li><a href="/">Writers Centres</a></li>
          <li><a href="/">Associations</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>The Scriptorium</h4>
        <ul>
          <li><a href="/submit-competition.html">Submit a Competition</a></li>
          <li><a href="/">Broadcast to Writers</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© {date.today().year} The Scriptorium · Generated {TODAY} · Always verify details on official websites before submitting.</p>
      <div class="footer-legal"><a href="/">Privacy</a><a href="/">Terms</a></div>
    </div>
  </div>
</footer>'''


# ── shared JS ─────────────────────────────────────────────────────────────────
def shared_js():
    return f'''
// ── NAV HAMBURGER ─────────────────────────────────────────────────────────────
document.getElementById('nav-hamburger').addEventListener('click', function() {{
  const links = document.getElementById('nav-links');
  const open  = links.classList.toggle('open');
  this.setAttribute('aria-expanded', open);
}});

// ── COMPETITION FILTER ────────────────────────────────────────────────────────
let activeType = 'all', searchTerm = '';

function applyCompFilters() {{
  const cards   = document.querySelectorAll('#comp-grid .card');
  const noRes   = document.getElementById('no-comps');
  let visible   = 0;
  cards.forEach(card => {{
    const types   = (card.dataset.types || '').split(',');
    const typeOk  = activeType === 'all' || types.includes(activeType);
    const text    = (card.textContent || '').toLowerCase();
    const searchOk = !searchTerm || text.includes(searchTerm);
    const show    = typeOk && searchOk;
    card.classList.toggle('hidden', !show);
    if (show) visible++;
  }});
  document.getElementById('comp-count').innerHTML =
    visible === 0
      ? 'No results'
      : 'Showing <strong>' + visible + '</strong> competition' + (visible !== 1 ? 's' : '');
  if (noRes) noRes.style.display = visible === 0 ? 'block' : 'none';
}}

document.querySelectorAll('.comp-filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.comp-filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeType = btn.dataset.type;
    applyCompFilters();
  }});
}});
const searchBox = document.getElementById('search-box');
if (searchBox) {{
  searchBox.addEventListener('input', e => {{
    searchTerm = e.target.value.toLowerCase().trim();
    applyCompFilters();
  }});
}}

// ── RESOURCE FILTER ───────────────────────────────────────────────────────────
let activeResType = 'all';

function applyResFilters() {{
  const cards = document.querySelectorAll('#res-grid .card');
  let visible = 0;
  cards.forEach(card => {{
    const show = activeResType === 'all' || card.dataset.type === activeResType;
    card.classList.toggle('hidden', !show);
    if (show) visible++;
  }});
  document.getElementById('res-count').innerHTML =
    'Showing <strong>' + visible + '</strong> resource' + (visible !== 1 ? 's' : '');
}}

document.querySelectorAll('.res-filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.res-filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeResType = btn.dataset.type;
    applyResFilters();
  }});
}});

// ── PAGE TABS ─────────────────────────────────────────────────────────────────
function showTab(tab) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + tab).classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  document.getElementById('filter-bar-comps').style.display = tab === 'comps' ? '' : 'none';
  document.getElementById('filter-bar-res').style.display   = tab === 'res'   ? '' : 'none';
}}

// ── NEWSLETTER ────────────────────────────────────────────────────────────────
async function handleNL(e, source) {{
  e.preventDefault();
  const emailId   = source === 'footer' ? 'footer-nl-email' : 'nl-email';
  const countryId = source === 'footer' ? 'footer-nl-country' : 'nl-country';
  const email   = document.getElementById(emailId)?.value;
  const country = document.getElementById(countryId)?.value || '';
  const btn = e.target.querySelector('button');
  if (btn) {{ btn.textContent = '…'; btn.disabled = true; }}
  const payload = {{ email, groups: ['{NL_GROUP}'] }};
  if (country && country !== 'other') payload.fields = {{ country }};
  try {{
    await fetch('{WORKER_URL}', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(payload)
    }});
  }} catch(err) {{ console.warn(err); }}
  if (source === 'footer') {{
    document.getElementById('footer-nl-success').style.display = 'block';
    document.getElementById('footer-nl-form').style.display = 'none';
  }} else {{
    document.getElementById('nl-success').style.display = 'block';
    e.target.style.display = 'none';
  }}
  if (typeof gtag !== 'undefined') gtag('event', 'generate_lead', {{ method: 'newsletter_' + source }});
}}
'''


# ── page template ─────────────────────────────────────────────────────────────
def make_page(cfg, comp_cards_html, res_cards_html, stats):
    slug       = cfg['slug']
    canonical  = f"{BASE_URL}/{cfg['file']}"
    info_paras = '\n'.join(f'<p>{p}</p>' for p in cfg['info'])

    n_comps    = stats['comps']
    n_free     = stats['free']
    n_open     = stats['open']
    n_fests    = stats['fests']

    comp_filter_btns = '\n'.join(
        f'<button class="filter-btn comp-filter-btn{"  active" if t == "all" else ""}" data-type="{t}">{label}</button>'
        for t, label in [('all','All')] + list(TYPE_LABELS.items())
    )

    schema = f'''{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{cfg['schema_name']}",
  "description": "{cfg['meta_desc']}",
  "url": "{canonical}",
  "dateModified": "{TODAY}",
  "publisher": {{
    "@type": "Organization",
    "name": "The Scriptorium",
    "url": "{BASE_URL}"
  }}
}}'''

    hero_sub = (
        f'Competitions &amp; prizes for writers in <strong>{cfg["country_label"]}</strong> and open internationally.'
        if cfg.get('country_label')
        else 'All countries · All types · Sorted by deadline.'
    )

    return f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cfg['title']}</title>
<meta name="description" content="{cfg['meta_desc']}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{cfg['title']}">
<meta property="og:description" content="{cfg['meta_desc']}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:image" content="{BASE_URL}/Favicon.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/Favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
<script type="application/ld+json">
{schema}
</script>
<style>{shared_css()}</style>
</head>
<body>

{nav_html(slug)}

<section class="hero">
  <p class="hero-eyebrow">The Scriptorium &middot; Free Directory</p>
  <h1>{cfg['h1']}</h1>
  <p class="hero-intro">{cfg['intro']}</p>
  <p class="hero-sub">{hero_sub}</p>
  <div class="hero-stats">
    <div class="hero-stat"><div class="hero-stat-num">{n_comps}</div><div class="hero-stat-label">Competitions</div></div>
    <div class="hero-stat"><div class="hero-stat-num">{n_free}</div><div class="hero-stat-label">Free to Enter</div></div>
    <div class="hero-stat"><div class="hero-stat-num">{n_open}</div><div class="hero-stat-label">Open Now</div></div>
    <div class="hero-stat"><div class="hero-stat-num">{n_fests}</div><div class="hero-stat-label">Festivals</div></div>
  </div>
</section>

<div class="page-tabs">
  <div class="page-tabs-inner">
    <button class="page-tab active" id="tab-comps" onclick="showTab('comps')">Competitions &amp; Prizes</button>
    <button class="page-tab" id="tab-res" onclick="showTab('res')">Resources &amp; Festivals</button>
  </div>
</div>

<div class="filter-bar" id="filter-bar-comps">
  <div class="filter-bar-inner">
    <span class="filter-label">Type:</span>
    {comp_filter_btns}
    <input type="search" id="search-box" class="search-box" placeholder="Search&hellip;" aria-label="Search competitions">
  </div>
</div>

<div class="filter-bar" id="filter-bar-res" style="display:none">
  <div class="filter-bar-inner">
    <span class="filter-label">Filter:</span>
    <button class="filter-btn res-filter-btn active" data-type="all">All</button>
    <button class="filter-btn res-filter-btn" data-type="writers-centre">Writers Centres</button>
    <button class="filter-btn res-filter-btn" data-type="association">Associations</button>
    <button class="filter-btn res-filter-btn" data-type="training">Training</button>
    <button class="filter-btn res-filter-btn fest-btn" data-type="festival">🎪 Festivals &amp; Events</button>
  </div>
</div>

<main class="main">

  <div class="section active" id="section-comps">
    <div class="results-bar">
      <p class="results-count" id="comp-count">Showing <strong>{n_comps}</strong> competitions</p>
    </div>
    <div class="grid" id="comp-grid">
      {comp_cards_html}
      <div class="no-results" id="no-comps">No competitions match your filters. <a href="/">Browse the full directory &rarr;</a></div>
    </div>
    <div class="info-section">
      <h2>{cfg['info_h2']}</h2>
      {info_paras}
      <p>Can&rsquo;t find what you&rsquo;re looking for? <a href="/">Browse the full Scriptorium directory</a> or <a href="/submit-competition.html">submit a competition</a> for review.</p>
    </div>
    <div class="cta-band">
      <h2>Browse the full directory</h2>
      <p>Search all competitions across Australia, NZ, UK, Ireland, USA and Canada in one place.</p>
      <a href="/" class="btn">Open full directory &rarr;</a>
    </div>
  </div>

  <div class="section" id="section-res">
    <div class="results-bar">
      <p class="results-count" id="res-count">Showing <strong>{stats["res_total"]}</strong> resources</p>
    </div>
    <div class="grid" id="res-grid">
      {res_cards_html}
    </div>
    <p class="suggest-note">Know a resource or festival we&rsquo;ve missed? <a href="/submit-competition.html">Let us know &rarr;</a></p>
  </div>

  <section class="nl-band" id="nl-band">
    <h3>Never miss a deadline</h3>
    <p>Join writers across 6 countries getting curated competition deadlines and literary news every week.</p>
    <form class="nl-form" onsubmit="handleNL(event,'inline')">
      <input type="email" id="nl-email" placeholder="your@email.com" required autocomplete="email">
      <button type="submit">Subscribe free &rarr;</button>
    </form>
    <select class="nl-country" id="nl-country">
      <option value="">Country (optional)</option>
      <option value="Australia">🇦🇺 Australia</option>
      <option value="New Zealand">🇳🇿 New Zealand</option>
      <option value="UK">🇬🇧 United Kingdom</option>
      <option value="Ireland">🇮🇪 Ireland</option>
      <option value="USA">🇺🇸 United States</option>
      <option value="Canada">🇨🇦 Canada</option>
      <option value="other">✏ Other…</option>
    </select>
    <p class="nl-hint">Free. No spam. Unsubscribe anytime.</p>
    <div class="nl-success" id="nl-success">&#10003; You&rsquo;re subscribed! Check your inbox.</div>
  </section>

</main>

{footer_html()}

<script>{shared_js()}</script>
</body>
</html>'''


# ── page definitions ──────────────────────────────────────────────────────────
PAGES = [
  dict(
    file='writing-competitions-australia.html', slug='australia',
    title='Writing Competitions Australia 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of Australian writing competitions and literary prizes for 2026. Short story, poetry, novel, flash fiction and screenplay competitions. Free to search, updated regularly.',
    h1='Writing Competitions Australia 2026',
    intro='The most comprehensive free directory of Australian writing competitions and literary prizes — updated regularly, searchable by type.',
    country_label='Australia',
    schema_name='Writing Competitions Australia 2026',
    info_h2='Australian Writing Competitions in 2026',
    info=[
      'Australia has one of the most vibrant literary competition scenes in the world, with prizes run by state writers centres, universities, literary journals, and cultural organisations across every state and territory. From the Victorian Premier\'s Literary Awards to the Vogel Literary Award, there are opportunities for writers of all levels.',
      'Many Australian competitions are free to enter and open to writers worldwide, while others are specifically for Australian citizens or residents. Filter by type to find short story competitions, poetry prizes, novel awards, flash fiction contests, and screenwriting opportunities.',
      'The Resources &amp; Festivals tab lists Australian writers centres, associations, training providers — and major literary festivals including the Melbourne Writers Festival, Sydney Writers\' Festival, Adelaide Writers\' Week (entirely free to attend), and the Emerging Writers\' Festival.',
    ],
    comp_filter=lambda c: c.get('country') == 'Australia' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'Australia',
  ),
  dict(
    file='writing-competitions-uk.html', slug='uk',
    title='Writing Competitions UK 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of UK writing competitions and literary prizes for 2026. Short story, poetry, novel, flash fiction and screenplay competitions. Free to search, updated regularly.',
    h1='Writing Competitions UK 2026',
    intro='Curated directory of UK writing competitions and literary prizes — updated regularly, searchable by type.',
    country_label='United Kingdom',
    schema_name='Writing Competitions UK 2026',
    info_h2='UK Writing Competitions in 2026',
    info=[
      'The United Kingdom has one of the world\'s richest literary competition landscapes, with prestigious prizes including the Bridport Prize, the Bath Novel Award, the Costa Book Awards, and the Rathbones Folio Prize.',
      'Many UK competitions are open to international writers, including writers from Australia, New Zealand, Ireland, and Canada. Use the filters above to find competitions by type — from short fiction and poetry to novel awards and screenwriting.',
      'See the Resources &amp; Festivals tab for UK writers\' organisations, training providers — and major literary festivals including the Hay Festival, Edinburgh International Book Festival, and Cheltenham Literature Festival.',
    ],
    comp_filter=lambda c: c.get('country') == 'UK' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'UK',
  ),
  dict(
    file='writing-competitions-usa.html', slug='usa',
    title='Writing Competitions USA 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of US writing competitions, screenwriting contests and literary prizes for 2026. Short story, poetry, novel, screenplay and flash fiction competitions. Free to search.',
    h1='Writing Competitions USA 2026',
    intro='Curated directory of US writing competitions, literary prizes, and screenwriting contests — searchable by type.',
    country_label='United States',
    schema_name='Writing Competitions USA 2026',
    info_h2='US Writing Competitions in 2026',
    info=[
      'The United States has the world\'s largest and most varied literary competition ecosystem, with prizes across every genre — from the Pulitzer Prize to genre-specific screenplay contests like the PAGE Awards and Final Draft Big Break.',
      'Most US competitions are open internationally. Use the filters to find competitions by type — fiction, poetry, novel, flash, or screenplay.',
      'See the Resources &amp; Festivals tab for US writers\' organisations — and major literary events including the AWP Conference, Tin House Summer Workshop, Bread Loaf Writers\' Conference, and Austin Film Festival.',
    ],
    comp_filter=lambda c: c.get('country') == 'USA' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'USA',
  ),
  dict(
    file='writing-competitions-canada.html', slug='canada',
    title='Writing Competitions Canada 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of Canadian writing competitions and literary prizes for 2026. Short story, poetry, novel and flash fiction competitions. Free to search, updated regularly.',
    h1='Writing Competitions Canada 2026',
    intro='Curated directory of Canadian writing competitions and literary prizes — updated regularly, searchable by type.',
    country_label='Canada',
    schema_name='Writing Competitions Canada 2026',
    info_h2='Canadian Writing Competitions in 2026',
    info=[
      'Canada has a rich literary competition landscape, with prizes from major institutions including the Scotiabank Giller Prize, the Griffin Poetry Prize, and the Canada Reads competition.',
      'Many Canadian competitions welcome international entries. Use the filters above to find competitions by type.',
      'See the Resources &amp; Festivals tab for Canadian writers\' organisations — and literary festivals including the Vancouver Writers Fest and Eden Mills Writers\' Festival.',
    ],
    comp_filter=lambda c: c.get('country') == 'Canada' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'Canada',
  ),
  dict(
    file='writing-competitions-ireland.html', slug='ireland',
    title='Writing Competitions Ireland 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of Irish writing competitions and literary prizes for 2026. Short story, poetry and novel competitions. Free to search, updated regularly.',
    h1='Writing Competitions Ireland 2026',
    intro='Curated directory of Irish writing competitions and literary prizes — updated regularly, searchable by type.',
    country_label='Ireland',
    schema_name='Writing Competitions Ireland 2026',
    info_h2='Irish Writing Competitions in 2026',
    info=[
      'Ireland has a vibrant literary competition and festival scene — from the Fish Publishing competitions to some of Europe\'s most celebrated literary events.',
      'Irish competitions are often open to writers worldwide. Use the filters above to find competitions by type.',
      'See the Resources &amp; Festivals tab for Irish writers\' organisations — and major festivals including Cúirt International Festival of Literature in Galway and Mountains to Sea in Dún Laoghaire.',
    ],
    comp_filter=lambda c: c.get('country') == 'Ireland' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'Ireland',
  ),
  dict(
    file='writing-competitions-new-zealand.html', slug='nz',
    title='Writing Competitions New Zealand 2026 — Free Directory | The Scriptorium',
    meta_desc='Curated directory of New Zealand writing competitions and literary prizes for 2026. Short story, poetry and novel competitions. Free to search, updated regularly.',
    h1='Writing Competitions New Zealand 2026',
    intro='Curated directory of New Zealand writing competitions and literary prizes — updated regularly, searchable by type.',
    country_label='New Zealand',
    schema_name='Writing Competitions New Zealand 2026',
    info_h2='NZ Writing Competitions in 2026',
    info=[
      'New Zealand has a distinctive literary competition culture, with prizes including the Ockham New Zealand Book Awards and competitions run by the New Zealand Society of Authors.',
      'Many New Zealand competitions are open internationally. Use the filters above to find competitions by type.',
      'See the Resources &amp; Festivals tab for NZ writers\' organisations — and the Auckland Writers Festival, one of the Southern Hemisphere\'s most significant literary events.',
    ],
    comp_filter=lambda c: c.get('country') == 'New Zealand' or c.get('international'),
    res_filter=lambda r: r.get('country') == 'New Zealand',
  ),
  dict(
    file='writing-competitions-2026.html', slug='2026',
    title='Writing Competition Deadlines 2026 — Full Calendar | The Scriptorium',
    meta_desc='Complete calendar of writing competition deadlines for 2026. Short story, poetry, novel, flash fiction and screenplay competition dates across Australia, UK, USA, Canada, Ireland and New Zealand.',
    h1='Writing Competition Deadlines 2026',
    intro='Every major writing competition deadline for 2026, in one place — sorted by closing date.',
    country_label=None,
    schema_name='Writing Competition Deadlines 2026',
    info_h2='Plan Your 2026 Submissions',
    info=[
      '2026 is a strong year for writing competitions, with major prizes open across short fiction, poetry, novel, flash fiction, and screenwriting. This page lists every deadline in the Scriptorium directory.',
      'Notable deadlines include the Bath Novel Award (31 May), the Bridport Prize (May), the PAGE International Screenwriting Awards (June), and the Script Pipeline Screenwriting Contest (August).',
      'Use the filters above to narrow by type, or search by name to find a specific competition. Literary festivals and events are listed in the Resources &amp; Festivals tab.',
    ],
    comp_filter=lambda c: True,
    res_filter=lambda r: True,
  ),
]


# ── build all pages ───────────────────────────────────────────────────────────
def build_all(output_dir=None):
    comps     = load('competitions.json')
    resources = load('resources.json')
    out_dir   = output_dir or SCRIPT_DIR

    for cfg in PAGES:
        page_comps = [c for c in comps if cfg['comp_filter'](c)]
        page_res   = [r for r in resources if cfg['res_filter'](r)]

        # Sort competitions by deadline month then name
        def sort_key(c):
            dm = c.get('deadlineMonth', 0) or 0
            return (dm if dm > 0 else 13, c.get('name', ''))
        page_comps.sort(key=sort_key)
        page_res.sort(key=lambda r: (r.get('type',''), r.get('name','')))

        comp_cards = '\n'.join(comp_card(c) for c in page_comps)
        res_cards  = '\n'.join(res_card(r)  for r in page_res)

        stats = {
            'comps':     len(page_comps),
            'free':      sum(1 for c in page_comps if c.get('entryFeeSort', 1) == 0),
            'open':      sum(1 for c in page_comps if is_upcoming(c)),
            'fests':     sum(1 for r in page_res   if r.get('type') == 'festival'),
            'res_total': len(page_res),
        }

        output = make_page(cfg, comp_cards, res_cards, stats)

        out_path = os.path.join(out_dir, cfg['file'])
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"  ✓ {cfg['file']:50s} comps={stats['comps']:3d}  res={stats['res_total']:2d}  ({len(output):,} chars)")

    print(f"\nAll {len(PAGES)} pages written to {out_dir}")
    print(f"Generated: {TODAY}")


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else None
    print("The Scriptorium — Static Page Generator")
    print("=" * 50)
    build_all(out)
