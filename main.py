#!/usr/bin/env python3
"""Draw the 20 Nov 2026 world-news front page (1024x1024 PNG).

Entry for make.fun news-image-20261120: "Sum up 20 November's world
news in one image". The image is drawn entirely by this program
(Python standard library + PIL, Noto fonts bundled under fonts/ so the
render is identical in any sandbox). No generated imagery, no network,
no randomness, no clocks: two runs write the same bytes.

Stories are real headlines from the 20 November 2026 news cycle,
verified against Reuters, BBC, USA Today, CNN, Le Monde, The Hindu
and NASA on the day. Layout budget (1024 tall): masthead to ~172,
lead to ~400, row 2 to ~592, row 3 to ~792, footer to ~1000.
"""
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 36  # margin

PAPER = (248, 244, 233)
INK = (25, 23, 19)
RED = (164, 31, 31)
MUTED = (96, 89, 76)
BODY = (52, 48, 42)
FAINT = (200, 192, 172)

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# Bundled fonts first (deterministic in any sandbox), then the usual
# system locations, then PIL's built-in bitmap font as a last resort.
FONT_CANDIDATES = {
    "black": ["NotoSerifDisplay-Black.ttf", "DejaVuSerif-Bold.ttf"],
    "serif_bold": ["NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"],
    "sans_bold": ["NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "sans": ["NotoSans-Regular.ttf", "DejaVuSans.ttf"],
}
FONT_DIRS = [
    HERE / "fonts",
    Path("/usr/share/fonts/truetype/noto"),
    Path("/usr/share/fonts/truetype/dejavu"),
]


def font(kind, size):
    for name in FONT_CANDIDATES[kind]:
        for d in FONT_DIRS:
            p = d / name
            if p.is_file():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size=size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines (never truncates)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill=INK):
    lines = wrap(draw, text, fnt, max_w)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, text, size=19):
    f = font("sans_bold", size)
    draw.text((x, y), text, font=f, fill=RED)
    return y + size + 7


def story(draw, x, y, w, kick, head, head_size, summary, sum_size=19):
    """One story block; returns y after it."""
    y = kicker(draw, x, y, kick)
    y = para(draw, x, y, head, font("serif_bold", head_size),
             w, head_size + 5)
    y += 5
    y = para(draw, x, y, summary, font("sans", sum_size),
             w, sum_size + 6, fill=BODY)
    return y


def globe(draw, cx, cy, r):
    """Small line-drawn globe: circle, meridians, parallels."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    for lon in (35, 70):
        rx = r * math.sin(math.radians(lon))
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=INK, width=2)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=INK, width=2)
    for k in (-0.5, 0.5):
        yy = cy + k * r
        half = (r * r - (k * r) ** 2) ** 0.5
        draw.line([(cx - half, yy), (cx + half, yy)], fill=INK, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    y = 24
    title = "THE WORLD TODAY"
    tf = font("black", 68)
    d.text(((W - d.textlength(title, font=tf)) / 2, y), title, font=tf, fill=INK)
    y += 84
    hline(d, M, W - M, y, 3)
    hline(d, M, W - M, y + 5, 1)
    y += 13
    date = "FRIDAY, 20 NOVEMBER 2026"
    df = font("sans_bold", 24)
    d.text(((W - d.textlength(date, font=df)) / 2, y), date, font=df, fill=INK)
    y += 32
    tag = "THE DAY IN SIX STORIES  \u00b7  ONE IMAGE"
    gf = font("sans", 17)
    d.text(((W - d.textlength(tag, font=gf)) / 2, y), tag, font=gf, fill=MUTED)
    y += 22
    hline(d, M, W - M, y, 1, fill=FAINT)

    # ---- Lead story: the Shenzhen trilateral ----
    y += 10
    lx, lw = M, 640
    y = kicker(d, lx, y, "LEAD STORY  \u2014  SHENZHEN", 19)
    y = para(d, lx, y, "Three powers, one table",
             font("black", 48), lw, 58)
    y += 2
    y = para(d, lx, y,
             "Trump, Xi and Putin hold first-ever three-way talks; "
             "joint vow on UN, nukes and oil",
             font("serif_bold", 25), lw, 31)
    y += 6
    y = para(d, lx, y,
             "The three leaders meet for 90 minutes at the APEC summit in "
             "Shenzhen and issue a joint declaration to reform the UN, cut "
             "nuclear risks and boost oil output \u2014 but reach no "
             "breakthrough on Ukraine or Iran.",
             font("sans", 19), lw, 25, fill=BODY)
    lead_bottom = y
    globe(d, W - M - 100, 292, 88)
    cap = "SHENZHEN, THURSDAY"
    cf = font("sans_bold", 14)
    d.text((W - M - 100 - d.textlength(cap, font=cf) / 2, 292 + 88 + 10),
           cap, font=cf, fill=MUTED)

    # ---- Row 2: the world court + the record IPO ----
    y = lead_bottom + 10
    hline(d, M, W - M, y, 1, fill=FAINT)
    y += 10
    col_w = 464
    y2 = story(d, M, y, col_w,
               "JUSTICE  \u2014  THE HAGUE",
               "World court: Myanmar committed genocide",
               31,
               "The ICJ rules Myanmar\u2019s forces committed genocide against "
               "the Rohingya in the 2017 crackdown \u2014 the first time the "
               "court has held a state responsible \u2014 and orders "
               "reparations.", 19)
    y3 = story(d, M + col_w + 24, y, col_w,
               "MARKETS  \u2014  NEW YORK",
               "Anthropic\u2019s $81bn IPO sets a record",
               31,
               "The Claude-maker prices at $83 a share and raises $81.3bn, "
               "the biggest IPO ever. Shares open 34% higher on their "
               "Nasdaq debut, then pull back.", 19)
    y = max(y2, y3)

    # ---- Row 3: three columns ----
    y += 10
    hline(d, M, W - M, y, 1, fill=FAINT)
    y += 10
    cw = 296
    gap = 30
    x1, x2, x3 = M, M + cw + gap, M + 2 * (cw + gap)
    ya = story(d, x1, y, cw,
               "WEATHER  \u2014  INDIA",
               "Cyclone Akvan hits Odisha coast",
               28,
               "The storm crosses near Gopalpur at noon; 300,000 people "
               "evacuated, 423 rescue teams deployed, 69 trains cancelled.",
               18)
    yb = story(d, x2, y, cw,
               "MIDDLE EAST  \u2014  RIYADH",
               "Houthi strike hits Riyadh\u2019s tallest tower",
               28,
               "A missile damages the PIF Tower, home of the Saudi wealth "
               "fund, blowing out windows over seven floors. No injuries.",
               18)
    yc = story(d, x3, y, cw,
               "WASHINGTON",
               "Trump: no rush on Iran",
               28,
               "The president says he will \u201csee what happens\u201d after "
               "1 January, pushing any decision on Iran into 2027.", 18)
    y = max(ya, yb, yc)

    # ---- Footer: also today + sources ----
    y += 8
    hline(d, M, W - M, y, 3)
    hline(d, M, W - M, y + 5, 1)
    y += 14
    y = kicker(d, M, y, "ALSO TODAY", 17)
    y = para(d, M, y,
             "NASA confirms Voyager 1 is one light-day from Earth, the first "
             "human-made object to reach it  \u00b7  European leaders say they "
             "are ready for talks with Russia on ending the Ukraine war",
             font("sans", 18), W - 2 * M, 24, fill=BODY)
    y += 6
    src = ("Sources: Reuters, BBC, USA Today, CNN, Le Monde, The Hindu, NASA "
           "\u2014 20 November 2026")
    sf = font("sans", 14)
    d.text((M, y), src, font=sf, fill=MUTED)
    y += 20
    assert y <= H, f"layout overflow: final y={y}"
    print("final y:", y)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "entry.png"
    img.save(out, "PNG", optimize=True)
    print("saved", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
