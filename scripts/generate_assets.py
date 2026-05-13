"""Генерирует все SVG-плейсхолдеры в app/static/img/."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "app" / "static" / "img"
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = {}

# Favicon
ASSETS["favicon.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="15" fill="#1a120a"/>
  <circle cx="16" cy="16" r="14" fill="none" stroke="#b8862d" stroke-width="0.5"/>
  <circle cx="16" cy="16" r="10" fill="none" stroke="#b8862d" stroke-width="0.5"/>
  <circle cx="16" cy="16" r="5" fill="#7a1f1f"/>
  <circle cx="16" cy="16" r="1.5" fill="#fbf3df"/>
</svg>'''

# Default avatar
ASSETS["default-avatar.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
  <rect width="120" height="120" fill="#efe2cb"/>
  <circle cx="60" cy="48" r="20" fill="#b89c70"/>
  <path d="M22 110c0-22 17-32 38-32s38 10 38 32" fill="#b89c70"/>
</svg>'''

# Placeholder for products
ASSETS["placeholder.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <circle cx="200" cy="150" r="80" fill="#1a120a"/>
  <circle cx="200" cy="150" r="78" fill="none" stroke="#b8862d" stroke-width="0.5"/>
  <circle cx="200" cy="150" r="55" fill="none" stroke="#b8862d" stroke-width="0.3"/>
  <circle cx="200" cy="150" r="30" fill="#7a1f1f"/>
  <circle cx="200" cy="150" r="6" fill="#fbf3df"/>
</svg>'''

# Vinyl record (PF)
def vinyl(label_color, label_text):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <g transform="translate(200,150)">
    <circle r="120" fill="#0a0807"/>
    <circle r="118" fill="none" stroke="#3a2a18" stroke-width="0.3"/>
    <circle r="105" fill="none" stroke="#5a4a30" stroke-width="0.3"/>
    <circle r="92" fill="none" stroke="#3a2a18" stroke-width="0.3"/>
    <circle r="78" fill="none" stroke="#5a4a30" stroke-width="0.3"/>
    <circle r="65" fill="none" stroke="#3a2a18" stroke-width="0.3"/>
    <circle r="52" fill="none" stroke="#5a4a30" stroke-width="0.3"/>
    <circle r="42" fill="{label_color}"/>
    <circle r="40" fill="none" stroke="#fbf3df" stroke-width="0.5" opacity="0.3"/>
    <text y="5" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="11" fill="#fbf3df" font-weight="700">{label_text}</text>
    <circle r="6" fill="#0a0807"/>
    <circle r="2" fill="#fbf3df"/>
  </g>
</svg>'''

ASSETS["product-vinyl-pf.svg"] = vinyl("#1a3a4a", "PINK FLOYD")
ASSETS["product-vinyl-miles.svg"] = vinyl("#2a4a8a", "KIND OF BLUE")
ASSETS["product-vinyl-beatles.svg"] = vinyl("#5a3a1a", "ABBEY ROAD")

# Guitar
ASSETS["product-guitar.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <g transform="translate(200,150)">
    <ellipse cx="-50" cy="40" rx="80" ry="55" fill="#7a1f1f"/>
    <ellipse cx="-50" cy="40" rx="78" ry="53" fill="none" stroke="#3a0d0d" stroke-width="0.5"/>
    <circle cx="-50" cy="40" r="14" fill="#1a0a05"/>
    <circle cx="-50" cy="40" r="13" fill="#0a0807"/>
    <rect x="-40" y="-50" width="14" height="92" fill="#1a0d05"/>
    <rect x="50" y="-90" width="36" height="50" rx="3" fill="#1a0d05"/>
    <line x1="-37" y1="-50" x2="62" y2="-90" stroke="#b8862d" stroke-width="0.5"/>
    <line x1="-31" y1="-50" x2="68" y2="-90" stroke="#b8862d" stroke-width="0.5"/>
    <line x1="-37" y1="40" x2="-37" y2="-50" stroke="#b8862d" stroke-width="0.5"/>
    <line x1="-31" y1="40" x2="-31" y2="-50" stroke="#b8862d" stroke-width="0.5"/>
    <circle cx="65" cy="-65" r="2" fill="#b8862d"/>
    <circle cx="80" cy="-55" r="2" fill="#b8862d"/>
    <circle cx="65" cy="-78" r="2" fill="#b8862d"/>
    <circle cx="80" cy="-72" r="2" fill="#b8862d"/>
  </g>
</svg>'''

# Piano
ASSETS["product-piano.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <g transform="translate(80,40)">
    <rect width="240" height="180" fill="#1a0d05" rx="4"/>
    <rect x="10" y="10" width="220" height="50" fill="#2a160a" rx="2"/>
    <text x="120" y="42" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="20" fill="#b8862d">YAMAHA</text>
    <rect x="10" y="80" width="220" height="60" fill="#fbf3df"/>
    <g fill="none" stroke="#1a0d05" stroke-width="1">
      <line x1="32" y1="80" x2="32" y2="140"/>
      <line x1="54" y1="80" x2="54" y2="140"/>
      <line x1="76" y1="80" x2="76" y2="140"/>
      <line x1="98" y1="80" x2="98" y2="140"/>
      <line x1="120" y1="80" x2="120" y2="140"/>
      <line x1="142" y1="80" x2="142" y2="140"/>
      <line x1="164" y1="80" x2="164" y2="140"/>
      <line x1="186" y1="80" x2="186" y2="140"/>
      <line x1="208" y1="80" x2="208" y2="140"/>
    </g>
    <g fill="#1a0d05">
      <rect x="22" y="80" width="14" height="36"/>
      <rect x="44" y="80" width="14" height="36"/>
      <rect x="88" y="80" width="14" height="36"/>
      <rect x="110" y="80" width="14" height="36"/>
      <rect x="132" y="80" width="14" height="36"/>
      <rect x="176" y="80" width="14" height="36"/>
      <rect x="198" y="80" width="14" height="36"/>
    </g>
    <rect x="10" y="150" width="220" height="20" fill="#0a0807"/>
  </g>
</svg>'''

# Saxophone
ASSETS["product-sax.svg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <g transform="translate(200,150)" stroke="#5a3a18" fill="#b8862d">
    <path d="M-30 -90 L-25 -50 Q-10 -20 0 30 Q5 70 50 80 Q90 88 95 50 Q97 30 80 25 Q60 22 60 45 Q60 60 75 60" stroke-width="14" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
    <ellipse cx="-32" cy="-90" rx="6" ry="3" fill="#1a0d05"/>
    <circle cx="-15" cy="-30" r="3" fill="#fbf3df" stroke="#5a3a18"/>
    <circle cx="-5" cy="0" r="3" fill="#fbf3df" stroke="#5a3a18"/>
    <circle cx="5" cy="30" r="3" fill="#fbf3df" stroke="#5a3a18"/>
    <circle cx="20" cy="60" r="3" fill="#fbf3df" stroke="#5a3a18"/>
  </g>
</svg>'''

# Turntable Technics
def turntable(plate_color="#0a0807", plinth_color="#1a0d05"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#efe2cb"/>
  <g transform="translate(200,170)">
    <rect x="-150" y="-60" width="300" height="100" rx="6" fill="{plinth_color}"/>
    <rect x="-148" y="-58" width="296" height="3" fill="#3a2a18" opacity="0.4"/>
    <circle cx="-30" cy="-10" r="60" fill="{plate_color}"/>
    <circle cx="-30" cy="-10" r="58" fill="none" stroke="#3a2a18" stroke-width="0.4"/>
    <circle cx="-30" cy="-10" r="42" fill="none" stroke="#5a4a30" stroke-width="0.3"/>
    <circle cx="-30" cy="-10" r="28" fill="#7a1f1f"/>
    <circle cx="-30" cy="-10" r="3" fill="#fbf3df"/>
    <line x1="80" y1="-40" x2="20" y2="-5" stroke="#b8862d" stroke-width="3" stroke-linecap="round"/>
    <circle cx="80" cy="-40" r="6" fill="#fbf3df" stroke="#5a3a18"/>
    <circle cx="20" cy="-5" r="3" fill="#1a0d05"/>
    <rect x="60" y="20" width="60" height="14" fill="#3a2a18" rx="2"/>
    <text x="90" y="30" text-anchor="middle" font-family="monospace" font-size="8" fill="#b8862d">33⅓ · 45</text>
  </g>
</svg>'''

ASSETS["product-player-technics.svg"] = turntable()
ASSETS["product-player-projekt.svg"] = turntable("#0f0c08", "#2a1a08")
ASSETS["product-player-rega.svg"] = turntable("#1a0d05", "#5a3a18")

# News images
def news_card(title, color, accent):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 225">
  <rect width="400" height="225" fill="{color}"/>
  <g transform="translate(200,112)">
    <circle r="60" fill="#0a0807" opacity="0.85"/>
    <circle r="58" fill="none" stroke="{accent}" stroke-width="0.5"/>
    <circle r="42" fill="none" stroke="{accent}" stroke-width="0.4"/>
    <circle r="22" fill="{accent}"/>
    <circle r="3" fill="#fbf3df"/>
  </g>
  <text x="200" y="200" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="14" fill="#fbf3df" opacity="0.7">{title}</text>
</svg>'''

ASSETS["news-japan.svg"] = news_card("JAPANESE PRESSINGS", "#7a1f1f", "#e8c8b8")
ASSETS["news-workshop.svg"] = news_card("RESTORATION", "#3a2a18", "#b8862d")
ASSETS["news-jazz.svg"] = news_card("JAZZ GUIDE", "#1a3a4a", "#e9d39c")
ASSETS["news-guitars.svg"] = news_card("VINTAGE GUITARS", "#5a3a18", "#b8862d")
ASSETS["news-default.svg"] = news_card("VINYL HARBOUR", "#7a1f1f", "#b8862d")

# Promo
def promo(text, color):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 225">
  <rect width="400" height="225" fill="{color}"/>
  <text x="50%" y="55%" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="900" font-size="44" fill="#fbf3df">{text}</text>
</svg>'''

ASSETS["promo-jazz.svg"] = promo("-15% JAZZ", "#7a1f1f")
ASSETS["promo-needle.svg"] = promo("FREE NEEDLE", "#3a2a18")
ASSETS["promo-default.svg"] = promo("PROMO", "#7a1f1f")


def main():
    for name, content in ASSETS.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"  ✓ {name}")
    print(f"\nGenerated {len(ASSETS)} SVG assets in {OUT}")


if __name__ == "__main__":
    main()
