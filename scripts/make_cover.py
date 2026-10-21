import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PUB = Path(r"C:\Users\bizoi\roman\publish")
W, H = 1600, 2560
SILVER = (216, 216, 232)
WHITE = (242, 242, 242)
DIM = (170, 160, 190)
GB = r"C:\Windows\Fonts\georgiab.ttf"   # Georgia Bold
GR = r"C:\Windows\Fonts\georgia.ttf"    # Georgia

def cover_fit(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h)).convert("RGB")

def spaced(draw, cx, y, text, font, fill, tracking):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines

def center_block(draw, cx, y, lines, font, fill, lh):
    for ln in lines:
        draw.text((cx - draw.textlength(ln, font=font) / 2, y), ln, font=font, fill=fill)
        y += lh
    return y

# ---------- FRONT ----------
front = cover_fit(Image.open(PUB / "cover_front.png"), W, H)
d = ImageDraw.Draw(front)
f_title = ImageFont.truetype(GB, 132)
f_auth = ImageFont.truetype(GR, 62)
spaced(d, W / 2, 300, "THE GLASS", f_title, SILVER, 14)
spaced(d, W / 2, 460, "CROWN", f_title, SILVER, 30)
spaced(d, W / 2, 2360, "L. T.", f_auth, DIM, 18)
front.save(PUB / "cover_front_final.png")
print("front ok")

# ---------- BACK ----------
back = cover_fit(Image.open(PUB / "cover_back.png"), W, H)
black = Image.new("RGB", (W, H), (5, 2, 10))
back = Image.blend(back, black, 0.20)
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([180, 560, W - 180, 2100], radius=40, fill=110)
panel = Image.new("RGB", (W, H), (8, 4, 14))
# darken panel zone: composite panel color through mask
back = Image.composite(Image.blend(back, panel, 0.55), back, mask)
d = ImageDraw.Draw(back)
f_head = ImageFont.truetype(GB, 56)
f_body = ImageFont.truetype(GR, 42)
f_small = ImageFont.truetype(GR, 34)
y = 640
spaced(d, W / 2, y, "THE GLASS CROWN", f_head, SILVER, 8)
y += 110
blurb = ("Leah Estia, twenty and heiress of Valdris, fled a forced marriage into the Red Velvet Inn \u2014 where her body became hers for the first time. Then Lara walked in: Queen of the Vestalian Empire, with a million soldiers on the road and proof of every murder. A throne for vassalage. And something no one ever gave her: attention. Between rescue and rule, Leah must decide whether Lara's discipline is care or better-packaged abuse. Dark political fantasy. Open ending.")
y = center_block(d, W / 2, y, wrap(d, blurb, f_body, W - 480), f_body, WHITE, 60)
y += 50
warn = "18+ ONLY: consensual adult content incl. light BDSM, sex-work setting, political violence. No minors in sexual contexts \u2014 ever."
y = center_block(d, W / 2, y, wrap(d, warn, f_small, W - 480), f_small, DIM, 50)
back.save(PUB / "cover_back_final.png")
print("back ok")

# ---------- WRAP (back + spine + front) ----------
SP = 120
wrap_img = Image.new("RGB", (W + SP + W, H), (12, 6, 20))
wrap_img.paste(Image.open(PUB / "cover_back_final.png"), (0, 0))
wrap_img.paste(Image.open(PUB / "cover_front_final.png"), (W + SP, 0))
d = ImageDraw.Draw(wrap_img)
f_sp = ImageFont.truetype(GB, 54)
txt = "THE GLASS CROWN \u00b7 L. T."
tmp = Image.new("RGB", (1200, 100), (12, 6, 20))
td = ImageDraw.Draw(tmp)
spaced(td, 600, 10, txt, f_sp, SILVER, 8)
tmp = tmp.rotate(90, expand=True)
wrap_img.paste(tmp, (W + SP // 2 - tmp.width // 2, H // 2 - tmp.height // 2))
wrap_img.save(PUB / "cover_wrap.png")
print("wrap ok")
