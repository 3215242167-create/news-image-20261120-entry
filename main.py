#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Friday, 20 November 2026.

A single-file newspaper front page, drawn entirely with Pillow: a
masthead with the date, one lead story beside a line-drawn globe, five
more stories in a ruled two-column grid, and an ALSO TODAY strip at the
foot. The picture is fully deterministic -- no randomness, no clock, no
network -- so two runs write identical bytes.

Run:  MAKEFUN_OUTPUT_DIR=<dir> python3 -P -s main.py
Writes <dir>/entry.png (1024 x 1024).
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 44
GUTTER = 28
INK = (22, 22, 22)
PAPER = (248, 244, 233)
RED = (158, 27, 27)
GREY = (96, 92, 84)

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"


def load(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


F = {
    "title": load("NotoSerifDisplay-Black.ttf", 72),
    "date": load("NotoSans-Bold.ttf", 20),
    "kick": load("NotoSans-Bold.ttf", 16),
    "head": load("NotoSerif-Bold.ttf", 42),
    "sub": load("NotoSerif-Bold.ttf", 28),
    "body": load("NotoSans-Regular.ttf", 19),
    "small": load("NotoSans-Regular.ttf", 18),
    "also_b": load("NotoSans-Bold.ttf", 17),
    "also": load("NotoSans-Regular.ttf", 17),
    "foot": load("NotoSans-Regular.ttf", 15),
}

LEAD_KICK = "APEC SUMMIT  \u2022  SHENZHEN"
LEAD_HEAD = "TRUMP, XI AND PUTIN HOLD FIRST-EVER THREE-WAY TALKS"
LEAD_BODY = (
    "Donald Trump, Xi Jinping and Vladimir Putin held 90 minutes of "
    "three-way talks on the sidelines of APEC \u2014 the first such "
    "meeting. A joint statement pledged UN reform, lower nuclear risk "
    "and higher oil output, but no breakthrough on Ukraine or Iran."
)

STORIES = [
    {
        "kick": "THE HAGUE",
        "head": "COURT FINDS MYANMAR GUILTY OF GENOCIDE",
        "body": (
            "The International Court of Justice ruled Myanmar committed "
            "genocide against the Rohingya in 2017 \u2014 the first "
            "ruling of its kind \u2014 and ordered reparations."
        ),
    },
    {
        "kick": "MARKETS",
        "head": "ANTHROPIC IPO IS THE BIGGEST EVER",
        "body": (
            "Anthropic priced its shares at $83 and raised $81.3 "
            "billion, the largest offering in history. The stock jumped "
            "34% at its Nasdaq debut before easing back."
        ),
    },
    {
        "kick": "INDIA",
        "head": "CYCLONE AKVAN STRIKES ODISHA COAST",
        "body": (
            "Cyclone Akvan came ashore near Gopalpur, Odisha, around "
            "noon. Some 300,000 people were evacuated, 423 rescue "
            "teams deployed and 69 trains cancelled."
        ),
    },
    {
        "kick": "SAUDI ARABIA",
        "head": "HOUTHI STRIKE HITS RIYADH\u2019S PIF TOWER",
        "body": (
            "A Houthi attack damaged the Public Investment Fund tower "
            "in Riyadh, shattering windows across seven floors. No one "
            "was hurt."
        ),
    },
]

STRIP = {
    "kick": "WASHINGTON",
    "head": "TRUMP IN NO RUSH ON IRAN \u2014 DECISION WAITS UNTIL 2027",
    "body": (
        "Donald Trump said there was no hurry over Iran and that he "
        "would decide after 1 January, pushing any decision into 2027."
    ),
}

ALSO = [
    (
        "VOYAGER 1",
        "NASA confirms Voyager 1 is one light-day from Earth \u2014 a "
        "first for a human-made object.",
    ),
    (
        "UKRAINE",
        "European leaders say they are ready to negotiate with Russia "
        "to end the war in Ukraine.",
    ),
]

FOOT = "Every story above was first reported on Friday, 20 November 2026."


def wrap(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit in width."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(draw, x, y, width, text, font, leading, color=INK):
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=color)
        y += leading
    return y


def rule(draw, y, weight=2):
    draw.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=weight)
    return y + weight


def globe(draw, cx, cy, r):
    """A small line-art globe: circle, meridians, latitude chords."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    for frac in (0.45, 0.85):
        w = int(r * frac)
        draw.ellipse([cx - w, cy - r, cx + w, cy + r], outline=INK, width=2)
    for dy in (-r // 2, 0, r // 2):
        half = int(math.sqrt(max(r * r - dy * dy, 0)))
        draw.line([(cx - half, cy + dy), (cx + half, cy + dy)],
                  fill=INK, width=2)
    for dx, dy in ((-r // 3, -r // 3), (r // 4, r // 5), (-r // 5, r // 2)):
        dot = 4
        draw.ellipse([cx + dx - dot, cy + dy - dot,
                      cx + dx + dot, cy + dy + dot], fill=RED)


def story(draw, x, y, width, item):
    draw.text((x, y), item["kick"], font=F["kick"], fill=RED)
    y += 21
    y = para(draw, x, y, width, item["head"], F["sub"], 33)
    y += 4
    y = para(draw, x, y, width, item["body"], F["small"], 22)
    return y


def label_para(draw, x, y, width, label, text):
    """Bold label followed by regular text, flowing across lines."""
    head = label + " \u2014 "
    head_w = draw.textlength(head, font=F["also_b"])
    words = text.split()
    first = head
    rest = []
    overflow = False
    for word in words:
        if overflow:
            rest.append(word)
            continue
        trial = first + word + " "
        trial_w = head_w + draw.textlength(trial[len(head):], font=F["also"])
        if trial_w <= width:
            first = trial
        else:
            overflow = True
            rest.append(word)
    draw.text((x, y), head, font=F["also_b"], fill=RED)
    draw.text((x + head_w, y), first[len(head):], font=F["also"],
              fill=INK)
    y += 21
    for line in wrap(draw, " ".join(rest), F["also"], width):
        draw.text((x, y), line, font=F["also"], fill=INK)
        y += 21
    return y


def build():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    y = 30

    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=2)
    y += 12
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=F["title"])
    d.text(((PAGE_W - tw) / 2, y), title, font=F["title"], fill=INK)
    y += 88
    date = "FRIDAY, 20 NOVEMBER 2026"
    dw = d.textlength(date, font=F["date"])
    d.text(((PAGE_W - dw) / 2, y), date, font=F["date"], fill=INK)
    y += 28
    y = rule(d, y, 3)
    y += 5
    y = rule(d, y, 1)
    y += 10

    # Lead story: kicker, headline, body on the left, globe on the right.
    d.text((MARGIN, y), LEAD_KICK, font=F["kick"], fill=RED)
    y += 22
    y = para(d, MARGIN, y, PAGE_W - 2 * MARGIN, LEAD_HEAD, F["head"], 47)
    y += 8
    body_top = y
    y = para(d, MARGIN, y, 600, LEAD_BODY, F["body"], 24)
    globe(d, 852, body_top + 56, 56)
    y = max(y, body_top + 112) + 8
    y = rule(d, y, 2)
    y += 10

    # Two-column grid: stories 1-2, then stories 3-4.
    col_w = (PAGE_W - 2 * MARGIN - GUTTER) // 2
    col2 = MARGIN + col_w + GUTTER
    for row in range(2):
        left = story(d, MARGIN, y, col_w, STORIES[row * 2])
        right = story(d, col2, y, col_w, STORIES[row * 2 + 1])
        y = max(left, right) + 10
        y = rule(d, y, 1)
        y += 10

    # Full-width strip: story 5.
    d.text((MARGIN, y), STRIP["kick"], font=F["kick"], fill=RED)
    y += 21
    y = para(d, MARGIN, y, PAGE_W - 2 * MARGIN, STRIP["head"], F["sub"], 33)
    y += 4
    y = para(d, MARGIN, y, PAGE_W - 2 * MARGIN, STRIP["body"], F["small"], 22)
    y += 10
    y = rule(d, y, 2)
    y += 10

    # ALSO TODAY band.
    band_top = y
    d.text((MARGIN, y), "ALSO TODAY", font=F["kick"], fill=RED)
    y += 22
    left = label_para(d, MARGIN, y, col_w, ALSO[0][0], ALSO[0][1])
    right = label_para(d, col2, y, col_w, ALSO[1][0], ALSO[1][1])
    y = max(left, right) + 8
    d.rectangle([MARGIN, band_top - 8, PAGE_W - MARGIN, y], outline=INK,
                width=1)
    y += 10

    # Footer note naming the day again.
    fw = d.textlength(FOOT, font=F["foot"])
    d.text(((PAGE_W - fw) / 2, y), FOOT, font=F["foot"], fill=GREY)
    y += 20
    return img, y


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    img, final_y = build()
    print("final y:", final_y, "of", PAGE_H)
    img.save(out_dir / "entry.png")


if __name__ == "__main__":
    main()
