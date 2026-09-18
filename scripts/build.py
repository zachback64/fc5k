#!/usr/bin/env python3
"""Build the FC5K pages.

  admin/index.html  everything: guest lists, posts, notes, all photos. Gitignored, open locally.
  history.html      public year-by-year page. No guest lists, no addresses, only photos/public/.

Sources: data/public.json (committed) + data/private/* and photos/private/* (gitignored).
Run: python3 scripts/build.py
"""
import html, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIV = ROOT / "data" / "private"
PHOTOS = ROOT / "photos"
IMG_EXT = {".jpg", ".jpeg", ".png", ".heic"}
esc = html.escape


def sections(path):
    """Split a markdown file into {heading: body} on '## ' headings."""
    out, cur = {}, None
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def year_of(heading):
    m = re.search(r"(20\d\d)", heading)
    return m.group(1) if m else None


def thumbs(src_dir, year):
    """JPEG thumbnails for every image in src_dir (HEIC won't render in Chrome)."""
    out = []
    tdir = PHOTOS / "private" / "thumbs" / year
    for f in sorted(src_dir.iterdir()) if src_dir.exists() else []:
        if f.suffix.lower() not in IMG_EXT:
            continue
        t = tdir / (f.stem + ".jpg")
        if not t.exists():
            tdir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["sips", "-Z", "1000", "-s", "format", "jpeg", str(f), "--out", str(t)],
                           capture_output=True)
        if t.exists():
            out.append((t, f))
    return out


def md_block(text):
    rows = []
    for line in text.splitlines():
        line = esc(line)
        line = re.sub(r"(https?://\S+)", r'<a href="\1">\1</a>', line)
        m = re.match(r"^(Going|Maybe|Can't|Can&#x27;t go|Can&#x27;t|Invited[^:]*|Hosts?|Description|Posts[^:]*):", line)
        if m:
            line = f"<b>{m.group(0)}</b>" + line[len(m.group(0)):]
        rows.append(f"<p>{line}</p>" if line.strip() else "")
    return "\n".join(rows)


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>{robots}
<link rel="stylesheet" href="{css}">
</head><body>
<header class="mast"><p class="mark">FC5K</p><p class="edition">{sub}</p></header>
<main class="{cls}">
{body}
</main>
<footer><p>Elmhurst, IL · a club, not a race company</p></footer>
</body></html>
"""


def build_admin(pub):
    fb = sections(PRIV / "facebook_events.md")
    pf = sections(PRIV / "partiful_guests.md")
    body = ['<p class="warn">Private. This page and everything under data/private and photos/private is gitignored. '
            'Don’t publish it.</p>',
            '<nav>' + " · ".join(f'<a href="#y{e["year"]}">{e["year"]}</a>' for e in pub["editions"]) +
            ' · <a href="#notes">Notes</a></nav>']
    # album photos grouped by capture year via filename index
    album_years = {}
    idx = PRIV / "photos_album_index.txt"
    if idx.exists():
        for line in idx.read_text().splitlines():
            m = re.match(r"(.+?) \| .*?(20\d\d)", line)
            if m:
                album_years[Path(m.group(1)).stem] = m.group(2)
    album = thumbs(PHOTOS / "private" / "album", "album")
    for e in pub["editions"]:
        y = str(e["year"])
        body.append(f'<section id="y{y}"><h2>{y} · {esc(e["edition"])} · {esc(e.get("date",""))}</h2>')
        body.append("<dl>" + "".join(f"<dt>{esc(k)}</dt><dd>{esc(str(v))}</dd>" for k, v in e.items()
                                     if k not in ("year", "edition", "date", "quotes") and v not in ("", None)) + "</dl>")
        for src, secs in (("Facebook", fb), ("Partiful", pf)):
            for h, t in secs.items():
                if year_of(h) == y:
                    body.append(f"<h3>{src}: {esc(h)}</h3>{md_block(t)}")
        pics = [(t, f) for t, f in album if album_years.get(f.stem) == y]
        pics += thumbs(PHOTOS / "private" / "raceday" / y, y)
        seen, uniq = set(), []
        for t, f in pics:
            if f.name not in seen:
                seen.add(f.name)
                uniq.append((t, f))
        if uniq:
            body.append(f"<h3>Photos ({len(uniq)})</h3><div class='grid'>" + "".join(
                f'<a href="../{f.relative_to(ROOT)}"><img loading="lazy" src="../{t.relative_to(ROOT)}" alt="{esc(f.name)}" title="{esc(f.name)}"></a>'
                for t, f in uniq) + "</div>")
        body.append("</section>")
    notes = PRIV / "notes_raw.txt"
    if notes.exists():
        body.append(f'<section id="notes"><h2>Apple Notes (raw)</h2><pre>{esc(notes.read_text())}</pre></section>')
    out = ROOT / "admin" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(PAGE.format(title="FC5K admin", robots='\n<meta name="robots" content="noindex">',
                               css="../style.css", sub="Admin · everything we have", cls="wide",
                               body="\n".join(body)))
    return out


def build_public(pub):
    body = ["<section><h1>History</h1><p>Eight runnings so far. Same neighborhood, same week, colder every time we tell it.</p></section>"]
    for e in reversed(pub["editions"]):
        y = str(e["year"])
        body.append(f'<section id="y{y}"><h2>{y} · {esc(e["edition"])}</h2><dl>')
        for k, label in (("date", "When"), ("winner", "Icicle"), ("time", "Winning time"), ("temp", "Temp"),
                         ("gun", "Gun"), ("went", "Ran / came"), ("course", "Course"), ("notes", "Notes")):
            if e.get(k) not in ("", None):
                body.append(f"<dt>{label}</dt><dd>{esc(str(e[k]))}</dd>")
        body.append("</dl>")
        for q in e.get("quotes", []):
            body.append(f"<blockquote>{esc(q)}</blockquote>")
        pdir = PHOTOS / "public" / y
        pics = sorted(p for p in pdir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}) if pdir.exists() else []
        if pics:
            body.append("<div class='grid'>" + "".join(
                f'<img loading="lazy" src="{p.relative_to(ROOT)}" alt="FC5K {y}">' for p in pics) + "</div>")
        body.append("</section>")
    out = ROOT / "history.html"
    out.write_text(PAGE.format(title="FC5K — History", robots="", css="style.css",
                               sub='<a href="index.html">Home</a> · History', cls="", body="\n".join(body)))
    return out


if __name__ == "__main__":
    pub = json.loads((ROOT / "data" / "public.json").read_text())
    print(build_public(pub))
    if PRIV.exists():
        print(build_admin(pub))
