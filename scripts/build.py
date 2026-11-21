"""
Builds the Gentle website from src/pages/*.html into the site root.

Each page in src/pages starts with a small header of "key: value" lines between --- markers, then its content.
This script wraps every page in the shared layout (head, search tags, schema, nav, theme picker, footer),
turns each page's FAQ block into FAQ schema, and writes sitemap.xml. It also flags any word or phrase the
house writing rules ban, so the copy stays readable.

Run from anywhere:  python website/scripts/build.py
Change SITE below once the site has its real address; everything else follows.
"""
import datetime
import html
import json
import pathlib
import re
import sys

SITE = "https://gentle-app.github.io/"  # The live address (the Gentle-App organisation's GitHub Pages site). One change here updates every page, the sitemap and robots.txt.
EMAIL = "gentleappdev@gmail.com"
NAME = "Gentle"
# Paste analytics tags (GA4, Clarity) here when they're set up; they go in every page's <head>.
HEAD_EXTRA = ""

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"

# The top bar. A (label, [pages]) entry is a dropdown; a (page, label) entry is a plain link.
NAV = [
    ("How it works", [
        ("energy-pacing-app.html", "How the points work"),
        ("heart-rate-pacing.html", "Heart-rate pacing"),
        ("crash-pem-tracker.html", "Crashes and PEM"),
        ("bowel-movement-tracker.html", "Gut and food"),
        ("works-with-your-watch.html", "Watches"),
        ("themes.html", "Themes"),
    ]),
    ("Who it's for", [
        ("me-cfs-long-covid.html", "ME/CFS and Long COVID"),
        ("crohns-ibd-fatigue.html", "Crohn's and IBD"),
        ("index.html#who", "Any energy-limiting condition"),
    ]),
    ("free-no-subscription.html", "Free for good"),
    ("privacy.html", "Privacy"),
]


def nav_html(current):
    """The top bar's links. Dropdowns are a button and a list; site.js opens them, and the phone menu shows them open."""
    out = []
    for n, (a, b) in enumerate(NAV):
        if isinstance(b, list):
            here = " current" if any(f == current for f, _ in b) else ""
            links = "\n".join(
                f'          <li><a href="{f}"{" aria-current=" + chr(34) + "page" + chr(34) if f == current else ""}>{html.escape(label)}</a></li>'
                for f, label in b
            )
            out.append(
                f'      <li class="has-sub{here}">\n'
                f'        <button type="button" class="sub-toggle" aria-expanded="false" aria-controls="sub-{n}">{html.escape(a)}</button>\n'
                f'        <ul class="sub" id="sub-{n}" hidden>\n{links}\n        </ul>\n      </li>'
            )
        else:
            cur = " aria-current=" + chr(34) + "page" + chr(34) if a == current else ""
            out.append(f'      <li><a href="{a}"{cur}>{html.escape(b)}</a></li>')
    return "\n".join(out)

THEMES = [
    ("calm", "Calm"), ("dark", "Dark"), ("pink", "Pink"), ("y2k", "Y2K sparkle"), ("aero", "Frutiger Aero"),
]

# The house rules for public copy: words and phrases that read as filler or as machine-written. Most come from the
# user's own writing rules and Wikipedia's "Signs of AI writing" list (checked November 2026).
BANNED = [
    "delve", "intricate", "tapestry", "pivotal", "underscore", "landscape", "foster", "enhance", "crucial", "breathtaking",
    "captivate", "profound", "steadfast", "robust", "testament", "watershed", "deeply rooted", "stands as", "solidifies",
    "lasting legacy", "plays a significant role", "moreover", "furthermore", "in addition", "on the other hand", "in conclusion",
    "in summary", "overall,", "it's important to note", "it is important to note", "it's worth noting", "it is worth noting",
    "it's worth mentioning", "showcase", "vibrant", "groundbreaking", "game-changer", "game changer", "seamless", "leverage",
    "unlock", "empower", "journey", "elevate", "revolutionise", "revolutionize", "cutting-edge", "state-of-the-art",
    "experts say", "many experts", "studies show", "in this article", "vital", "additionally", "navigate the",
    "not only", "—",
    # From Wikipedia's list: vocabulary, copula-avoidance and "not just X" patterns.
    "boasts", "bolster", "garner", "interplay", "meticulous", "valuable", "align with", "highlighting", "emphasising",
    "emphasizing", "serves as", "not just", "it's not about", "quietly", "dependable", "multifaceted", "prioritise",
    "prioritize", "universal", "practical", "the short version", "here's the thing", "the best part", "let's be honest",
    "honestly", "simply put", "in today's", "plainly",
]


def read_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing the --- header")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["body"] = m.group(2)
    meta["file"] = path.stem + ".html"
    return meta


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def faqs(body):
    """The page's FAQ block: <details class="faq-item"><summary>Q</summary> answer </details>."""
    out = []
    for q, a in re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>(.*?)</details>', body, re.S):
        out.append({"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}})
    return out


def url(file):
    return SITE if file == "index.html" else SITE + file


def schema(p):
    blocks = []
    if p["file"] == "index.html":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "MobileApplication",
            "@id": SITE + "#app",
            "name": NAME,
            "url": SITE,
            "description": p["description"],
            "operatingSystem": "Android 8.0 or later; Wear OS 3 or later for the optional watch app",
            "applicationCategory": "HealthApplication",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "GBP"},
            "author": {"@type": "Person", "name": "The developer of Gentle", "email": EMAIL},
            "screenshot": [SITE + "img/app/today-light.jpg", SITE + "img/app/allowance.jpg", SITE + "img/app/history.jpg"],
            "featureList": [
                "Daily energy allowance in points, from your own ordinary day",
                "Morning, evening and any-time check-ins, by tap or by voice",
                "Heart-rate pace line with alerts from your watch",
                "Crash and PEM log with early warning",
                "Bowel movement tracker with the Bristol stool chart",
                "List of foods you can't eat",
                "Report for your doctor (PDF and spreadsheets)",
                "Works with Health Connect: Pixel Watch, Fitbit, Samsung, Garmin and more",
            ],
        })
    else:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": NAME, "item": SITE},
                {"@type": "ListItem", "position": 2, "name": p.get("crumb", p["title"]), "item": url(p["file"])},
            ],
        })
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": p["title"],
            "description": p["description"],
            "url": url(p["file"]),
            "about": {"@id": SITE + "#app"},
            "dateModified": TODAY,
        })
    qs = faqs(p["body"])
    if qs:
        blocks.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qs})
    return "\n".join(f'  <script type="application/ld+json">\n{json.dumps(b, indent=2, ensure_ascii=False)}\n  </script>' for b in blocks)


ICON = """<svg viewBox="0 0 108 108" aria-hidden="true"><use href="#heart"></use></svg>"""

# The status bar drawn over each screenshot: the time, then mobile signal, wifi and battery, like Android's.
STATUS_ICONS = (
    '<svg viewBox="0 0 12 12"><path d="M12 0V12H0Z"/></svg>'
    '<svg viewBox="0 0 16 12"><path d="M8 11.6 0.4 3.7a10.8 10.8 0 0 1 15.2 0Z"/></svg>'
    '<svg viewBox="0 0 8 13"><rect x="2.5" width="3" height="2" rx=".6"/><rect y="1.4" width="8" height="11.6" rx="1.7"/></svg>'
)


def jpeg_size(path):
    """Width and height of a JPEG, read from its header (so the page reserves the right space before it loads)."""
    data = path.read_bytes()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + length
    return None


def file_version(*paths):
    """A short fingerprint of some files, added to their address so browsers fetch a new copy when they change."""
    h = __import__("hashlib").sha1()
    for path in paths:
        h.update(path.read_bytes())
    return h.hexdigest()[:8]


def phones(body):
    """Turns <div class="phone"><img ...></div> into a phone with a screen, a status bar and a camera."""
    def frame(m):
        cls, img = m.group(1), m.group(2)
        src = re.search(r'src="([^"]+)"', img).group(1)
        size = jpeg_size(ROOT / src)
        if size:
            img = re.sub(r'width="\d+" height="\d+"', f'width="{size[0]}" height="{size[1]}"', img)
        if 'data-shot="today"' in img:
            # The home page's screenshot swaps with the theme, so it carries one fingerprint for all the Today screenshots.
            v = file_version(*sorted((ROOT / "img" / "app").glob("today-*.jpg")))
            img = img.replace(f'src="{src}"', f'src="{src}?v={v}" data-v="{v}"')
        else:
            img = img.replace(f'src="{src}"', f'src="{src}?v={file_version(ROOT / src)}"')
        ink = "light" if "today-dark" in src else "dark"
        return (f'<div class="{cls}" data-ink="{ink}"><div class="phone-screen">{img}'
                f'<div class="phone-status" aria-hidden="true"><span>2:50</span><span class="phone-icons">{STATUS_ICONS}</span></div>'
                f'<span class="phone-camera" aria-hidden="true"></span></div></div>')
    return re.sub(r'<div class="(phone(?: phone-sm)?)">(<img [^>]*>)</div>', frame, body)

SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="hg" x1="40" y1="30" x2="66" y2="77" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FF8ACB"/><stop offset=".45" stop-color="#FF2E93"/><stop offset="1" stop-color="#C2006B"/>
    </linearGradient>
    <linearGradient id="hs" x1="38" y1="34" x2="44" y2="45" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity=".2"/>
    </linearGradient>
    <symbol id="heart" viewBox="0 0 108 108">
      <g transform="translate(0 4)">
        <path d="M54,77 C33,62 28,51 28,43 C28,35.5 34,30 41,30 C46.5,30 51,33 54,38 C57,33 61.5,30 67,30 C74,30 80,35.5 80,43 C80,51 75,62 54,77 Z" fill="url(#hg)"/>
        <path d="M54,77 C33,62 28,51 28,43 C28,35.5 34,30 41,30 C46.5,30 51,33 54,38 C57,33 61.5,30 67,30 C74,30 80,35.5 80,43 C80,51 75,62 54,77 Z" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.6"/>
        <path d="M35,41 C35,36 39,33.5 43,33.5 C46.5,33.5 49,35.5 50.5,38.5 C46,38 40,40 37,45 C35.8,44.2 35,42.8 35,41 Z" fill="url(#hs)"/>
        <circle cx="70.5" cy="38" r="2.2" fill="#fff" fill-opacity=".8"/>
      </g>
      <path d="M81,25 L82.4,29.6 L87,31 L82.4,32.4 L81,37 L79.6,32.4 L75,31 L79.6,29.6 Z" fill="#fff"/>
      <path d="M28,62 L29,65 L32,66 L29,67 L28,70 L27,67 L24,66 L27,65 Z" fill="#FFE48A"/>
    </symbol>
  </defs>
</svg>"""


def full_title(p):
    """The page title, with "| Gentle" added when it doesn't already say Gentle and there's room (search results cut off at about 60)."""
    t = p["title"]
    return t if NAME in t or len(t) + len(NAME) + 3 > 62 else f"{t} | {NAME}"


def layout(p, pages):
    title = full_title(p)
    desc = html.escape(p["description"], quote=True)
    canonical = url(p["file"])
    og_image = SITE + "og-image.png"
    nav = nav_html(p["file"])
    theme_buttons = "\n".join(f'            <button type="button" data-set-theme="{k}" role="radio" aria-checked="false"><span class="swatch swatch-{k}"></span><span>{label}</span></button>' for k, label in THEMES)
    crumbs = "" if p["file"] == "index.html" else f"""
<div class="container breadcrumb">
  <nav aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">{html.escape(p.get("crumb", p["title"]))}</li></ol></nav>
</div>"""
    related = ""
    if p.get("related"):
        items = []
        for f in [r.strip() for r in p["related"].split(",") if r.strip()]:
            other = pages.get(f)
            if other:
                items.append(f'      <li><a href="{f}"><strong>{html.escape(other.get("crumb", other["title"]))}</strong><span>{html.escape(other.get("blurb", other["description"]))}</span></a></li>')
        related = f"""
<section class="related">
  <div class="container">
    <h2>Related pages</h2>
    <ul class="related-list">
{chr(10).join(items)}
    </ul>
  </div>
</section>"""
    footer_links = "\n".join(f'        <li><a href="{f}">{html.escape(pages[f].get("crumb", pages[f]["title"]))}</a></li>' for f in ORDER if f in pages and f != "index.html")
    return f"""<!DOCTYPE html>
<html lang="en-GB" data-theme="aero">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title, quote=False)}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canonical}">{chr(10) + '  <meta name="robots" content="noindex">' if p.get("noindex") else ""}
  <meta name="theme-color" content="#8FD3FF">

  <meta property="og:site_name" content="{NAME}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="en_GB">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Gentle, a free energy pacing app, showing today's energy points">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title, quote=True)}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_image}">

  <script>
    // Set the theme and low-stimulus mode before anything draws, so there's no flash of the wrong look.
    (function () {{
      var d = document.documentElement, t = null, low = null;
      try {{
        t = localStorage.getItem('gentle-theme');
        low = localStorage.getItem('gentle-low');
        // Low stimulus used to be one of the themes; it's a separate switch now.
        if (t === 'low') {{ t = 'dark'; low = 'on'; localStorage.setItem('gentle-theme', t); localStorage.setItem('gentle-low', low); }}
      }} catch (e) {{}}
      if (!t) t = 'aero'; // Frutiger Aero is the default look, as in the app
      d.setAttribute('data-theme', t);
      if (low === 'on') d.setAttribute('data-low', 'on');
    }})();
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Silkscreen&family=Sniglet:wght@800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v={VERSION}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
{schema(p)}
{HEAD_EXTRA}</head>
<body>
{SPRITE}
<a class="skip-link" href="#main">Skip to content</a>

<header class="site-nav">
  <div class="nav-inner">
    <a href="index.html" class="brand">{ICON}<span>Gentle</span></a>
    <ul class="nav-links" id="nav-links">
{nav}
    </ul>
    <div class="nav-actions">
      <div class="theme-picker">
        <button type="button" class="theme-toggle" id="theme-toggle" aria-expanded="false" aria-controls="theme-menu">
          <svg class="palette" viewBox="0 0 24 24" aria-hidden="true"><path class="rim" d="M12 2.8c-5.1 0-9.2 3.9-9.2 8.9 0 5 4 9.5 9 9.5 1.2 0 1.9-.8 1.9-1.8 0-.5-.2-.9-.5-1.3-.3-.3-.5-.8-.5-1.3 0-1 .8-1.8 1.8-1.8h2.1c2.7 0 4.9-2.2 4.9-4.9 0-4.3-4.2-7.3-9.5-7.3Z"/><circle class="d1" cx="7.4" cy="11.8" r="1.7"/><circle class="d2" cx="10.3" cy="7.4" r="1.7"/><circle class="d3" cx="15.1" cy="7.7" r="1.7"/></svg><span class="theme-label">Theme</span>
        </button>
        <div class="theme-menu" id="theme-menu" hidden>
          <p class="theme-menu-title" id="theme-menu-title">The app's themes</p>
          <div role="radiogroup" aria-labelledby="theme-menu-title">
{theme_buttons}
          </div>
          <div class="theme-menu-divider"></div>
          <button type="button" class="low-toggle" id="low-toggle" role="switch" aria-checked="false">
            <span class="low-text"><span>Low stimulus</span><span class="low-hint">Dim, muted and still, on any theme</span></span><span class="switch" aria-hidden="true"></span>
          </button>
        </div>
      </div>
      <button type="button" class="menu-toggle" id="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav-links"><span class="burger" aria-hidden="true"></span></button>
    </div>
  </div>
</header>
{crumbs}
<main id="main">
{phones(p["body"].strip())}
</main>
{related}

<section class="promise-band" aria-label="The promise">
  <div class="container promise-inner">
    <p class="promise-head">Free, and it'll stay free</p>
    <p>There will never be a subscription or a premium version. The app has small banner ads, which a one-off 99p (99 cents in the US) gets rid of, and that's the only thing you can buy. Your data stays on your phone, and nobody else gets it, me included.</p>
    <p class="promise-links"><a href="free-no-subscription.html">Why it's free</a> &middot; <a href="privacy.html">Privacy</a></p>
  </div>
</section>

<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <a href="index.html" class="brand brand-footer">{ICON}<span>Gentle</span></a>
      <p>A pacing app for anyone who has to manage limited energy, made by one person.</p>
      <p>Found a bug, even a tiny one, or have an idea for a new feature? Please tell me: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div>
      <h2 class="footer-head">Pages</h2>
      <ul class="footer-links">
{footer_links}
      </ul>
    </div>
  </div>
  <div class="container footer-small">
    <p>Gentle is not a medical device and does not diagnose, treat, cure or prevent any medical condition. Talk to your doctor or care team before changing how you manage your health.</p>
    <p>Android, Google Play, Wear OS, Pixel and Fitbit are trademarks of Google LLC. Other product names belong to their owners.</p>
  </div>
</footer>

<script src="site.js?v={VERSION}" defer></script>
</body>
</html>
"""


ORDER = [
    "index.html", "energy-pacing-app.html", "heart-rate-pacing.html", "me-cfs-long-covid.html", "crash-pem-tracker.html",
    "crohns-ibd-fatigue.html", "bowel-movement-tracker.html", "works-with-your-watch.html", "themes.html",
    "free-no-subscription.html", "privacy.html",
]
TODAY = datetime.date.today().isoformat()
# Changes whenever styles.css or site.js do, so browsers fetch the new ones instead of using an old copy.
VERSION = __import__("hashlib").sha1((ROOT / "styles.css").read_bytes() + (ROOT / "site.js").read_bytes()).hexdigest()[:8]


def lint(p):
    # A dash on its own in a table cell (class "none") is a placeholder for "not mentioned", not an em dash in a sentence.
    body = re.sub(r'<td class="none">.*?</td>', "", p["body"])
    text = strip_tags(body).lower() + " " + p["title"].lower() + " " + p["description"].lower()
    found = [w for w in BANNED if w in text]
    return found


def main():
    pages = {}
    for path in sorted(PAGES.glob("*.html")):
        p = read_page(path)
        pages[p["file"]] = p
    problems = 0
    for f, p in pages.items():
        out = layout(p, pages)
        (ROOT / f).write_text(out, encoding="utf-8", newline="\n")
        bad = lint(p)
        if bad:
            problems += 1
            print(f"  {f}: check the wording: {', '.join(bad)}")
        if len(full_title(p)) > 62 or len(p["description"]) > 160:
            print(f"  {f}: title {len(full_title(p))} chars, description {len(p['description'])} chars (aim for 60 and 155)")
    listed = [f for f in ORDER if f in pages] + [f for f in pages if f not in ORDER and f != "404.html"]
    urls = "\n".join(
        f"  <url><loc>{url(f)}</loc><lastmod>{TODAY}</lastmod><priority>{'1.0' if f == 'index.html' else '0.7'}</priority></url>"
        for f in listed
    )
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8", newline="\n")
    # robots.txt and llms.txt are kept in src/ with {{SITE}} where the address goes.
    for name in ("robots.txt", "llms.txt"):
        src = ROOT / "src" / name
        if src.exists():
            (ROOT / name).write_text(src.read_text(encoding="utf-8").replace("{{SITE}}", SITE), encoding="utf-8", newline="\n")
    print(f"Built {len(pages)} pages and sitemap.xml" + (f"; {problems} page(s) to check" if problems else "; wording check passed"))


if __name__ == "__main__":
    main()
