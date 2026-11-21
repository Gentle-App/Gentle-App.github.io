"""Cleans the emulator screenshots for the website.

- The status bar strip (top 112 px) had app content scrolled under it, so it's replaced with the screen's own
  background, copied from a clean row just below. The website draws a tidy status bar over that strip.
- The Today screens start at the points card, dropping the half-hidden sample-data card above it.
- "learned" ends after the gut and food card instead of cutting the next card in half.
Writes 600-px-wide JPEGs into the website's img/app folder.
"""
import pathlib
import sys

from PIL import Image, ImageDraw

SRC = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parents[2] / "screenshots" / "raw"
DST = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1] / "img" / "app"
BAR = 112  # status bar strip in the raw 1080 x 2400 captures
WIDTH = 600


def first_gap_after_first_card(im, x=540, start=BAR):
    """For the scrolled Today screens: the first background row after the first card ends."""
    bg = im.getpixel((10, start + 20))
    in_card = False
    for y in range(start, im.height):
        p = im.getpixel((x, y))
        same = sum(abs(a - b) for a, b in zip(p, bg)) < 18
        if not same:
            in_card = True
        elif in_card:
            return y + 4
    return start


def handle(img, draw_y):
    d = ImageDraw.Draw(img)
    w = img.width
    d.rounded_rectangle([w / 2 - 142, draw_y, w / 2 + 142, draw_y + 11], radius=6, fill=(60, 64, 63))


for raw in sorted(SRC.glob("raw-*.png")):
    name = raw.stem[4:]
    im = Image.open(raw).convert("RGB")
    w, h = im.size
    if name.startswith("today-"):
        top = 310  # all four were captured at the same scroll: the card above ends at 304 and the points card starts at 327
        body = im.crop((0, top, w, h))
    elif name == "learned":
        # Keep down to just after the gut and food card, then plain background and the gesture handle.
        body_end = 2062
        body = Image.new("RGB", (w, h - BAR), im.getpixel((10, 2050)))
        body.paste(im.crop((0, BAR, w, body_end)), (0, 0))
        handle(body, h - BAR - 38)
    else:
        body = im.crop((0, BAR, w, h))
    # A clean strip for the status bar: repeat the first row of the body.
    strip_row = body.crop((0, 0, w, 1))
    out = Image.new("RGB", (w, body.height + BAR))
    for y in range(BAR):
        out.paste(strip_row, (0, y))
    out.paste(body, (0, BAR))
    small = out.resize((WIDTH, round(out.height * WIDTH / w)), Image.LANCZOS)
    dest = DST / f"{name}.jpg"
    small.save(dest, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"{name}: {small.width}x{small.height}, body from {top if name.startswith('today-') else BAR}, {dest.stat().st_size // 1024} KB")
