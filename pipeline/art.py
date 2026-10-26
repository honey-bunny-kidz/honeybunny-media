"""Cartoon art for Honey Bunny Kidz: characters (sprites) and backgrounds, drawn with PIL."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = (95, 62, 72, 255)      # soft cartoon outline
SS = 2                        # supersampling


def E(d, cx, cy, rx, ry, fill, ol=OUT, w=7):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=ol if w else None, width=w)


def finish(img, size):
    return img.resize(size, Image.LANCZOS)


def eye(d, x, y, r, state, mood=0):
    if state == "closed":
        d.arc([x - r, y - r * 0.6, x + r, y + r * 0.9], 200, 340, fill=OUT, width=9)
        d.arc([x - r, y - r * 0.9, x + r, y + r * 0.6], 20, 160, fill=OUT, width=9)
        return
    E(d, x, y, r, r * 1.22, (45, 32, 40, 255), w=0)
    E(d, x + r * 0.3, y - r * 0.42, r * 0.34, r * 0.34, (255, 255, 255, 255), w=0)
    E(d, x - r * 0.28, y + r * 0.42, r * 0.16, r * 0.16, (255, 255, 255, 230), w=0)


def mouth(d, x, y, s, m):
    if m == 0:
        d.arc([x - 40 * s, y - 24 * s, x, y + 14 * s], 20, 160, fill=OUT, width=8)
        d.arc([x, y - 24 * s, x + 40 * s, y + 14 * s], 20, 160, fill=OUT, width=8)
    else:
        h = (14 + 13 * m) * s
        E(d, x, y + h * 0.6, 26 * s, h, (150, 50, 70, 255), w=7)
        E(d, x, y + h * 1.15, 15 * s, h * 0.38, (245, 130, 150, 255), w=0)


def cheeks(layer, pts, rx, ry):
    c = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    for (x, y) in pts:
        cd.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(255, 140, 160, 120))
    c = c.filter(ImageFilter.GaussianBlur(6))
    layer.alpha_composite(c)


# ---------------------------------------------------------------- characters
def bunny(eyes="open", m=0, fur=(236, 196, 140), inner=(255, 182, 193), bow=True, h=520):
    W, H = 800, 1160
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for side in (-1, 1):  # ears on their own layer so they can tilt
        ear = Image.new("RGBA", (260, 460), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ear)
        E(ed, 130, 230, 62, 200, fur + (255,))
        E(ed, 130, 250, 30, 150, inner + (255,), w=0)
        ear = ear.rotate(-side * 12, resample=Image.BICUBIC, expand=False)
        im.alpha_composite(ear, (int(400 + side * 95 - 130), 0))
    d = ImageDraw.Draw(im)
    for side in (-1, 1):
        E(d, 400 + side * 115, 1080, 95, 48, fur + (255,))
    E(d, 400, 880, 215, 215, fur + (255,))
    E(d, 400, 915, 130, 150, (255, 244, 225, 255), w=0)
    for side in (-1, 1):
        E(d, 400 + side * 185, 840, 55, 82, fur + (255,))
    E(d, 400, 545, 268, 238, fur + (255,))
    for side in (-1, 1):
        eye(d, 400 + side * 98, 525, 44, eyes)
    cheeks(im, [(262, 615), (538, 615)], 50, 30)
    d = ImageDraw.Draw(im)
    E(d, 400, 592, 24, 17, (240, 120, 140, 255), w=5)
    mouth(d, 400, 625, 1, m)
    if bow:
        bx, by = 290, 330
        d.polygon([(bx, by), (bx - 85, by - 55), (bx - 85, by + 55)], fill=(255, 105, 160, 255), outline=OUT, width=7)
        d.polygon([(bx, by), (bx + 85, by - 55), (bx + 85, by + 55)], fill=(255, 105, 160, 255), outline=OUT, width=7)
        E(d, bx, by, 26, 26, (255, 150, 195, 255))
    return finish(im, (int(h * W / H), h))


def duckling(eyes="open", m=0, h=330):
    W, H = 800, 860
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    Y = (255, 214, 80, 255)
    for side in (-1, 1):
        E(d, 400 + side * 80, 820, 75, 32, (255, 150, 60, 255))
    E(d, 420, 620, 270, 200, Y)
    E(d, 560, 610, 110, 80, (250, 196, 60, 255))
    E(d, 380, 330, 210, 200, Y)
    d.polygon([(350, 140), (390, 70), (410, 145)], fill=Y, outline=OUT, width=7)
    d.polygon([(390, 140), (450, 85), (440, 150)], fill=Y, outline=OUT, width=7)
    for side in (-1, 1):
        eye(d, 380 + side * 80, 300, 34, eyes)
    cheeks(im, [(270, 380), (490, 380)], 40, 24)
    d = ImageDraw.Draw(im)
    op = 10 + 18 * m
    E(d, 380, 405 - op * 0.2, 80, 32, (255, 150, 60, 255))
    E(d, 380, 440 + op * 0.6, 62, 18 + op * 0.7, (255, 135, 50, 255))
    return finish(im, (int(h * W / H), h))


def owl(eyes="open", m=0, h=420):
    W, H = 800, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    B, L = (150, 104, 78, 255), (232, 205, 170, 255)
    d.polygon([(190, 260), (230, 90), (320, 200)], fill=B, outline=OUT, width=7)
    d.polygon([(610, 260), (570, 90), (480, 200)], fill=B, outline=OUT, width=7)
    E(d, 400, 560, 290, 390, B)
    E(d, 400, 690, 190, 230, L, w=0)
    for row in range(4):
        for k in range(-2, 3):
            x, y = 400 + k * 70 + (35 if row % 2 else 0), 560 + row * 70
            if abs(x - 400) < 170:
                d.arc([x - 28, y - 18, x + 28, y + 22], 20, 160, fill=(190, 150, 115, 255), width=6)
    for side in (-1, 1):
        E(d, 400 + side * 300, 600, 70, 210, (125, 85, 62, 255))
    for side in (-1, 1):
        E(d, 400 + side * 120, 360, 118, 118, (255, 245, 225, 255))
        eye(d, 400 + side * 120, 360, 52, eyes)
    cheeks(im, [(240, 470), (560, 470)], 40, 22)
    d = ImageDraw.Draw(im)
    op = 12 * m
    d.polygon([(370, 440), (430, 440), (400, 500 + op)], fill=(250, 170, 60, 255), outline=OUT, width=6)
    for side in (-1, 1):
        for t in (-1, 0, 1):
            E(d, 400 + side * 90 + t * 28, 950, 16, 30, (250, 170, 60, 255), w=5)
    return finish(im, (int(h * W / H), h))


def moon(eyes="closed", m=0, h=300):
    W = H = 900
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([60, 60, 840, 840], fill=(255, 245, 200, 110))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(im)
    E(d, 450, 450, 300, 300, (255, 240, 180, 255), ol=(200, 170, 110, 255))
    for (x, y, r) in ((330, 330, 40), (560, 300, 28), (590, 560, 35), (300, 580, 22)):
        E(d, x, y, r, r, (245, 225, 160, 255), w=0)
    for side in (-1, 1):
        eye(d, 450 + side * 100, 440, 40, eyes)
    cheeks(im, [(320, 520), (580, 520)], 45, 26)
    d = ImageDraw.Draw(im)
    mouth(d, 450, 540, 1.1, m)
    return finish(im, (int(h * W / H), h))


def kitten(eyes="open", m=0, fur=(250, 236, 222), patch=(244, 170, 110), h=420):
    W, H = 900, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    F, P = fur + (255,), patch + (255,)
    # curly tail
    d.arc([560, 560, 820, 860], 200, 470, fill=OUT, width=52)
    d.arc([560, 560, 820, 860], 200, 470, fill=P, width=38)
    # feet + body
    for side in (-1, 1):
        E(d, 450 + side * 95, 950, 80, 42, F)
    E(d, 450, 790, 185, 175, F)
    E(d, 450, 820, 110, 120, (255, 250, 244, 255), w=0)
    for side in (-1, 1):
        E(d, 450 + side * 120, 880, 48, 62, F)
        for t in (-1, 0, 1):
            d.line([450 + side * 120 + t * 16, 920, 450 + side * 120 + t * 16, 940], fill=OUT, width=5)
    # ears
    for side in (-1, 1):
        bx = 450 + side * 175
        d.polygon([(bx - side * 95, 250), (bx + side * 70, 70), (bx + side * 90, 310)], fill=P if side < 0 else F, outline=OUT, width=7)
        d.polygon([(bx - side * 55, 245), (bx + side * 60, 125), (bx + side * 68, 285)], fill=(255, 180, 195, 255))
    # head
    E(d, 450, 420, 285, 235, F)
    d.ellipse([205, 250, 425, 480], fill=P)                   # round orange patch over left eye
    d.ellipse([165, 185, 735, 655], outline=OUT, width=7)
    for k in (-1, 0, 1):  # forehead stripes
        d.line([450 + k * 40, 195, 450 + k * 30, 250], fill=(240, 160, 100, 255), width=12)
    for side in (-1, 1):
        eye(d, 450 + side * 110, 410, 50, eyes)
    cheeks(im, [(300, 500), (600, 500)], 52, 30)
    d = ImageDraw.Draw(im)
    d.polygon([(425, 470), (475, 470), (450, 498)], fill=(245, 125, 150, 255), outline=OUT, width=4)
    for side in (-1, 1):  # whiskers
        for k in (-1, 0, 1):
            d.line([450 + side * 130, 505 + k * 22, 450 + side * 250, 490 + k * 40], fill=OUT, width=5)
    mouth(d, 450, 520, 0.85, m)
    # pink collar with bell
    d.arc([300, 560, 600, 680], 20, 160, fill=(255, 105, 160, 255), width=26)
    E(d, 450, 690, 26, 26, (255, 215, 80, 255), w=5)
    return finish(im, (int(h * W / H), h))


def lamb(eyes="open", m=0, h=400):
    W, H = 900, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    WOOL, FACE, LEG = (253, 251, 246, 255), (255, 232, 214, 255), (150, 118, 120, 255)

    def puff(circles):
        for (x, y, r) in circles:
            E(d, x, y, r, r, WOOL, w=7)
        for (x, y, r) in circles:
            E(d, x, y, r - 7, r - 7, WOOL, w=0)
    # little legs
    for side in (-1, 1):
        d.rounded_rectangle([450 + side * 95 - 34, 820, 450 + side * 95 + 34, 985], 30, fill=LEG, outline=OUT, width=7)
    # fluffy body
    body = [(450, 715, 140)] + [(450 + 195 * math.cos(a), 720 + 118 * math.sin(a), 78)
                                 for a in [k * math.pi * 2 / 11 for k in range(11)]]
    puff(body)
    # floppy ears
    for side in (-1, 1):
        ear = Image.new("RGBA", (300, 160), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ear)
        E(ed, 150, 80, 120, 52, FACE)
        E(ed, 150 + side * 15, 80, 78, 28, (255, 180, 195, 255), w=0)
        ear = ear.rotate(side * -22, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(ear, (int(450 + side * 265 - ear.width / 2), int(350 - ear.height / 2)))
    d = ImageDraw.Draw(im)
    # face
    E(d, 450, 430, 230, 215, FACE)
    # wool tuft on top
    puff([(450 + dx, 215 + dy, r) for dx, dy, r in ((-95, 40, 70), (0, 0, 85), (95, 40, 70), (-50, 70, 60), (50, 70, 60))])
    # lavender bow
    bx, by = 585, 225
    d.polygon([(bx, by), (bx - 70, by - 48), (bx - 70, by + 48)], fill=(185, 150, 245, 255), outline=OUT, width=7)
    d.polygon([(bx, by), (bx + 70, by - 48), (bx + 70, by + 48)], fill=(185, 150, 245, 255), outline=OUT, width=7)
    E(d, bx, by, 22, 22, (215, 190, 255, 255))
    for side in (-1, 1):
        eye(d, 450 + side * 95, 420, 44, eyes)
    cheeks(im, [(315, 505), (585, 505)], 48, 28)
    d = ImageDraw.Draw(im)
    E(d, 450, 492, 22, 15, (240, 120, 140, 255), w=5)
    mouth(d, 450, 525, 0.85, m)
    return finish(im, (int(h * W / H), h))


def puppy(eyes="open", m=0, h=400):
    W, H = 900, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    FUR, LIGHT, EAR = (238, 190, 120, 255), (255, 243, 225, 255), (176, 116, 78, 255)
    # happy wagging tail
    d.arc([590, 560, 830, 800], 175, 335, fill=OUT, width=52)
    d.arc([590, 560, 830, 800], 175, 335, fill=FUR, width=38)
    # feet + body
    for side in (-1, 1):
        E(d, 450 + side * 100, 950, 85, 44, FUR)
        E(d, 450 + side * 100, 958, 50, 22, LIGHT, w=0)
    E(d, 450, 790, 190, 178, FUR)
    E(d, 450, 820, 112, 125, LIGHT, w=0)
    for side in (-1, 1):
        E(d, 450 + side * 125, 880, 50, 64, FUR)
    # head
    E(d, 450, 420, 280, 240, FUR)
    E(d, 340, 330, 70, 60, (225, 170, 100, 255), w=0)          # little patch above eye
    # floppy ears hanging down
    for side in (-1, 1):
        ear = Image.new("RGBA", (220, 380), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ear)
        E(ed, 110, 190, 88, 170, EAR)
        ear = ear.rotate(side * 14, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(ear, (int(450 + side * 265 - ear.width / 2), int(410 - ear.height / 2)))
    d = ImageDraw.Draw(im)
    # muzzle
    E(d, 450, 520, 140, 100, LIGHT, w=6)
    for side in (-1, 1):
        eye(d, 450 + side * 105, 400, 46, eyes)
    cheeks(im, [(295, 510), (605, 510)], 50, 28)
    d = ImageDraw.Draw(im)
    E(d, 450, 478, 40, 28, (70, 45, 50, 255), w=0)               # nose
    E(d, 462, 470, 12, 8, (255, 255, 255, 200), w=0)
    mouth(d, 450, 535, 0.85, m)
    # blue collar with gold star tag
    d.arc([290, 560, 610, 690], 20, 160, fill=(90, 160, 240, 255), width=28)
    cx, cy, r = 450, 700, 30
    pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + k * math.pi / 5),
            cy + (r if k % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
    d.polygon(pts, fill=(255, 215, 80, 255), outline=OUT, width=4)
    return finish(im, (int(h * W / H), h))


def yarn(eyes="open", m=0, h=150):
    W = H = 400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    E(d, 200, 200, 170, 170, (255, 130, 180, 255))
    for k in range(-3, 4):
        d.arc([60 + k * 10, 60 - k * 25, 340 + k * 10, 340 + k * 25], 200, 340, fill=(230, 90, 150, 255), width=8)
    d.arc([40, 150, 360, 520], 250, 300, fill=(230, 90, 150, 255), width=8)
    d.line([300, 330, 390, 390], fill=(230, 90, 150, 255), width=9)
    return finish(im, (h, h))


def sunflower(d, x, ground, H, s=1.0):
    d.line([x, ground, x, ground - H * 0.42 * s], fill=(90, 160, 80), width=int(14 * s))
    d.ellipse([x - 70 * s, ground - H * 0.27 * s, x - 5, ground - H * 0.23 * s], fill=(110, 185, 95))
    cy = ground - H * 0.45 * s
    for k in range(14):
        a = k * math.pi * 2 / 14
        px, py = x + math.cos(a) * 62 * s, cy + math.sin(a) * 62 * s
        d.ellipse([px - 30 * s, py - 30 * s, px + 30 * s, py + 30 * s], fill=(255, 205, 40))
    d.ellipse([x - 45 * s, cy - 45 * s, x + 45 * s, cy + 45 * s], fill=(150, 95, 50))


def rose_bush(d, x, ground, H, s=1.0):
    for dx, dy, r in ((0, 0.10, 0.11), (-0.09, 0.06, 0.08), (0.09, 0.06, 0.08)):
        cx, cy, rr = x + dx * H, ground - dy * H * s, r * H * s
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr * 0.7], fill=(80, 160, 90))
    rnd = random.Random(int(x))
    for _ in range(9):
        fx, fy = x + rnd.uniform(-0.15, 0.15) * H * s, ground - rnd.uniform(0.04, 0.19) * H * s
        r = 0.022 * H * s
        d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=(235, 60, 80))
        d.ellipse([fx - r * 0.45, fy - r * 0.45, fx + r * 0.45, fy + r * 0.45], fill=(200, 35, 60))


CHARS = {
    "honey": dict(fn=bunny, kw=dict(), h=0.44),
    "mama": dict(fn=bunny, kw=dict(fur=(246, 228, 205), bow=False), h=0.54),
    "dotty": dict(fn=duckling, kw=dict(), h=0.28),
    "ollie": dict(fn=owl, kw=dict(), h=0.36),
    "moon": dict(fn=moon, kw=dict(), h=0.30),
    "mimi": dict(fn=kitten, kw=dict(), h=0.40),
    "yarn": dict(fn=yarn, kw=dict(), h=0.12),
    "lulu": dict(fn=lamb, kw=dict(), h=0.40),
    "pip": dict(fn=puppy, kw=dict(), h=0.40),
}


def sprites(cid, H, scale=1.0):
    c = CHARS[cid]
    hh = int(H * c["h"] * scale)
    return {(e, m): c["fn"](eyes=e, m=m, h=hh, **c["kw"]) for e in ("open", "closed") for m in (0, 1, 2)}


# ---------------------------------------------------------------- backgrounds
def grad(W, H, top, bot):
    t = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(top)[None, None] * (1 - t) + np.array(bot)[None, None] * t)
    return Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8), "RGB").convert("RGBA")


def hills(d, W, H, base, amp, col, seed, ol=None):
    pts = [(0, H)]
    for x in range(0, W + 20, 20):
        y = base * H - amp * H * (0.5 + 0.5 * math.sin(x / W * math.pi * 2.2 + seed)) \
            - amp * H * 0.3 * math.sin(x / W * math.pi * 5 + seed * 2)
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=col)


def cloud(d, x, y, s, col):
    for dx, dy, r in ((0, 0, 60), (60, -25, 70), (125, 0, 58), (60, 20, 60)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=col)


def flowers(d, W, H, y0, n, seed, night=False):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(y0, H)
        r = H * 0.009 * (0.7 + (y - y0) / (H - y0))
        c = rnd.choice([(255, 170, 200), (255, 230, 120), (200, 180, 255), (255, 255, 255)])
        if night:
            c = tuple(int(v * 0.45) + 20 for v in c)
        for k in range(5):
            a = k * math.pi * 2 / 5
            d.ellipse([x + math.cos(a) * r - r, y + math.sin(a) * r - r, x + math.cos(a) * r + r, y + math.sin(a) * r + r], fill=c)
        d.ellipse([x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7], fill=(255, 200, 80) if not night else (120, 100, 60))


def tree(d, W, H, x, night):
    trunk = (110, 78, 60) if not night else (62, 48, 58)
    leaf = (110, 190, 110) if not night else (40, 80, 85)
    d.rectangle([x - W * 0.045, H * 0.25, x + W * 0.045, H * 0.92], fill=trunk)
    d.polygon([(x, H * 0.48), (x - W * 0.2, H * 0.40), (x - W * 0.2, H * 0.44), (x, H * 0.55)], fill=trunk)
    for dx, dy, r in ((0, 0.12, 0.17), (-0.12, 0.2, 0.13), (0.12, 0.2, 0.13), (-0.2, 0.32, 0.1), (0.07, 0.03, 0.12)):
        cx, cy, rr = x + dx * W, dy * H, r * W
        d.ellipse([cx - rr, cy - rr * 0.8, cx + rr, cy + rr * 0.8], fill=leaf)


def background(kind, W, H):
    """Returns (bg RGBA, fg RGBA or None, stars list)."""
    stars, fg = [], None
    rnd = random.Random(7)
    ground = 0.86 if W > H else 0.74
    if kind == "day":
        im = grad(W, H, (150, 210, 250), (235, 245, 255))
        d = ImageDraw.Draw(im)
        d.ellipse([W * 0.8, H * 0.06, W * 0.8 + H * 0.16, H * 0.22], fill=(255, 230, 120))
        for i in range(4):
            cloud(d, rnd.uniform(0, W * 0.8), rnd.uniform(H * 0.06, H * 0.3), H / 900, (255, 255, 255))
        hills(d, W, H, ground - 0.12, 0.08, (150, 215, 140), 1)
        hills(d, W, H, ground - 0.02, 0.05, (120, 200, 115), 3)
        flowers(d, W, H, ground * H, 60, 2)
    elif kind in ("night", "oak"):
        im = grad(W, H, (20, 24, 70), (95, 70, 140))
        d = ImageDraw.Draw(im)
        for _ in range(int(140 * W * H / (1920 * 1080))):
            stars.append((rnd.uniform(0, W), rnd.uniform(0, H * (ground - 0.25)), rnd.uniform(1.5, 4), rnd.uniform(0, 6.28)))
        hills(d, W, H, ground - 0.12, 0.08, (45, 85, 110), 1)
        if kind == "oak":
            tree(d, W, H, W * 0.74 if W > H else W * 0.62, True)
        hills(d, W, H, ground - 0.02, 0.05, (40, 105, 100), 3)
        if kind == "night":
            d.ellipse([W * 0.55, H * (ground - 0.03), W * 0.95, H * (ground + 0.07)], fill=(70, 110, 170))
            d.ellipse([W * 0.6, H * (ground - 0.01), W * 0.9, H * (ground + 0.05)], fill=(90, 135, 190))
        flowers(d, W, H, ground * H, 40, 2, night=True)
    elif kind in ("garden", "garden_pond", "porch"):
        im = grad(W, H, (165, 220, 252), (240, 248, 255))
        d = ImageDraw.Draw(im)
        d.ellipse([W * 0.06, H * 0.06, W * 0.06 + H * 0.15, H * 0.21], fill=(255, 232, 120))
        for i in range(3):
            cloud(d, rnd.uniform(W * 0.25, W * 0.85), rnd.uniform(H * 0.05, H * 0.25), H / 1000, (255, 255, 255))
        hills(d, W, H, ground - 0.12, 0.07, (160, 220, 150), 2)
        if kind == "porch":  # little cottage
            hx, hw = W * (0.66 if W > H else 0.5), min(W, H) * 0.55
            d.rectangle([hx - hw / 2, H * (ground - 0.42), hx + hw / 2, H * ground], fill=(255, 225, 190))
            d.polygon([(hx - hw * 0.62, H * (ground - 0.40)), (hx, H * (ground - 0.66)), (hx + hw * 0.62, H * (ground - 0.40))], fill=(220, 100, 110))
            d.rounded_rectangle([hx - hw * 0.12, H * (ground - 0.26), hx + hw * 0.12, H * ground], 30, fill=(150, 100, 70))
            for wx in (hx - hw * 0.33, hx + hw * 0.33):
                d.rectangle([wx - hw * 0.1, H * (ground - 0.32), wx + hw * 0.1, H * (ground - 0.18)], fill=(150, 205, 245), outline=(255, 255, 255), width=6)
        hills(d, W, H, ground - 0.02, 0.04, (125, 200, 115), 4)
        if kind == "garden":
            rose_bush(d, W * (0.62 if W > H else 0.75), H * ground, H)
            sunflower(d, W * (0.88 if W > H else 0.2), H * ground, H)
        if kind == "garden_pond":
            d.ellipse([W * 0.5, H * (ground - 0.03), W * 0.97, H * (ground + 0.08)], fill=(80, 150, 230))
            d.ellipse([W * 0.55, H * (ground - 0.01), W * 0.92, H * (ground + 0.06)], fill=(110, 180, 245))
        flowers(d, W, H, ground * H, 55, 5)
    elif kind == "meadow":
        im = grad(W, H, (130, 205, 250), (250, 245, 225))
        d = ImageDraw.Draw(im)
        # soft rainbow arc
        rx, ry, rr = W * 0.5, H * (ground - 0.05), min(W, H) * (0.62 if W > H else 0.55)
        bands = [(255, 150, 150), (255, 200, 130), (255, 240, 140), (160, 225, 150), (150, 200, 255), (200, 170, 245)]
        rain = Image.new("RGBA", (W, H), (200, 200, 230, 0))
        rd = ImageDraw.Draw(rain)
        bw = rr * 0.07
        for i, c in enumerate(bands):
            r = rr - i * bw
            rd.ellipse([rx - r, ry - r, rx + r, ry + r], outline=c + (200,), width=int(bw) + 2)
        im.alpha_composite(rain.filter(ImageFilter.GaussianBlur(3)))
        d = ImageDraw.Draw(im)
        d.ellipse([W * 0.84, H * 0.05, W * 0.84 + H * 0.14, H * 0.19], fill=(255, 225, 110))
        for i in range(3):
            cloud(d, rnd.uniform(0, W * 0.75), rnd.uniform(H * 0.05, H * 0.22), H / 1000, (255, 255, 255))
        hills(d, W, H, ground - 0.10, 0.07, (170, 225, 140), 5)
        hills(d, W, H, ground - 0.01, 0.04, (130, 205, 110), 6)
        # tulips along the back
        for k in range(9):
            tx = W * (0.04 + k * 0.118) + rnd.uniform(-20, 20)
            ty = H * (ground - 0.03) + rnd.uniform(-10, 10)
            s = H / 1080
            d.line([tx, ty, tx, ty - 70 * s], fill=(90, 160, 80), width=int(8 * s) + 1)
            c = rnd.choice([(255, 120, 150), (255, 200, 80), (200, 140, 240), (255, 160, 90)])
            d.pieslice([tx - 24 * s, ty - 112 * s, tx + 24 * s, ty - 64 * s], 0, 180, fill=c)
            d.polygon([(tx - 24 * s, ty - 88 * s), (tx - 12 * s, ty - 118 * s), (tx, ty - 92 * s), (tx + 12 * s, ty - 118 * s), (tx + 24 * s, ty - 88 * s)], fill=c)
        # butterflies
        for k in range(4):
            bx, by, s = rnd.uniform(W * 0.05, W * 0.95), rnd.uniform(H * 0.25, H * 0.5), H / 1080
            c = rnd.choice([(255, 170, 210), (170, 210, 255), (255, 220, 120)])
            for side in (-1, 1):
                d.ellipse([bx + side * 22 * s - 18 * s, by - 20 * s, bx + side * 22 * s + 18 * s, by + 6 * s], fill=c)
                d.ellipse([bx + side * 16 * s - 11 * s, by + 2 * s, bx + side * 16 * s + 11 * s, by + 20 * s], fill=c)
            d.line([bx, by - 16 * s, bx, by + 16 * s], fill=(95, 62, 72), width=int(5 * s) + 1)
        flowers(d, W, H, ground * H, 55, 11)
    elif kind == "sunset":
        im = grad(W, H, (125, 115, 200), (255, 190, 150))
        d = ImageDraw.Draw(im)
        sx, sy, sr = W * (0.3 if W > H else 0.5), H * (ground - 0.13), min(W, H) * 0.16
        glow = Image.new("RGBA", (W, H), (255, 220, 150, 0))
        ImageDraw.Draw(glow).ellipse([sx - sr * 2.2, sy - sr * 2.2, sx + sr * 2.2, sy + sr * 2.2], fill=(255, 220, 150, 120))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
        d = ImageDraw.Draw(im)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 175, 95))
        for i in range(4):
            cloud(d, rnd.uniform(0, W * 0.85), rnd.uniform(H * 0.06, H * 0.3), H / 950, (255, 200, 210))
        for _ in range(int(25 * W * H / (1920 * 1080))):
            stars.append((rnd.uniform(0, W), rnd.uniform(0, H * 0.18), rnd.uniform(1.2, 2.6), rnd.uniform(0, 6.28)))
        hills(d, W, H, ground - 0.12, 0.08, (200, 160, 175), 1)
        tree(d, W, H, W * (0.82 if W > H else 0.8), False)
        hills(d, W, H, ground - 0.02, 0.05, (125, 175, 120), 3)
        flowers(d, W, H, ground * H, 55, 9)
    elif kind == "bedroom":
        im = grad(W, H, (120, 82, 92), (160, 112, 98))
        d = ImageDraw.Draw(im)
        d.rectangle([0, H * ground, W, H], fill=(115, 80, 66))
        # round window with night sky
        wx, wy, wr = W * (0.78 if W > H else 0.7), H * 0.28, min(W, H) * 0.17
        d.ellipse([wx - wr - 18, wy - wr - 18, wx + wr + 18, wy + wr + 18], fill=(150, 100, 70))
        win = grad(int(2 * wr), int(2 * wr), (25, 30, 80), (80, 60, 130))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, win.size[0], win.size[1]], fill=255)
        im.paste(win, (int(wx - wr), int(wy - wr)), mask)
        for _ in range(14):
            a, r = rnd.uniform(0, 6.28), rnd.uniform(0, wr * 0.85)
            stars.append((wx + math.cos(a) * r, wy + math.sin(a) * r, rnd.uniform(1.5, 3.5), rnd.uniform(0, 6.28)))
        d.line([wx - wr, wy, wx + wr, wy], fill=(150, 100, 70), width=10)
        d.line([wx, wy - wr, wx, wy + wr], fill=(150, 100, 70), width=10)
        # night light glow
        lx, ly = W * (0.1 if W > H else 0.15), H * (ground - 0.08)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - H * 0.2, ly - H * 0.2, lx + H * 0.2, ly + H * 0.2], fill=(255, 220, 140, 90))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        d = ImageDraw.Draw(im)
        d.ellipse([lx - H * 0.035, ly - H * 0.05, lx + H * 0.035, ly + H * 0.02], fill=(255, 225, 150))
        d.rectangle([lx - H * 0.01, ly + H * 0.02, lx + H * 0.01, ly + H * 0.08], fill=(150, 100, 70))
        # bed
        bx0, bx1 = W * (0.22 if W > H else 0.08), W * (0.62 if W > H else 0.92)
        by = H * (ground - 0.06)
        d.rounded_rectangle([bx0 - 20, H * (ground - 0.36), bx0 + 30, H * ground], 15, fill=(170, 110, 75))
        d.rounded_rectangle([bx0, by - H * 0.05, bx1, by + H * 0.08], 20, fill=(185, 125, 85))
        d.rounded_rectangle([bx0 + 20, by - H * 0.2, bx0 + W * 0.15, by - H * 0.06], 60, fill=(255, 250, 240), outline=OUT, width=4)
        for i in range(5):
            sx = W * (0.08 + i * 0.2) if W > H else W * (0.1 + i * 0.2)
            d.polygon([(sx, H * 0.06), (sx + 22, H * 0.06), (sx + 11, H * 0.1)], fill=(255, 210, 120))
        d.line([0, H * 0.06, W, H * 0.06], fill=(200, 160, 120), width=3)
        fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fg)
        fd.rounded_rectangle([bx0 + W * 0.035, by - H * 0.035, bx1 + 10, by + H * 0.07], 40, fill=(140, 180, 240), outline=OUT, width=5)
        for i in range(6):
            x = bx0 + W * 0.08 + i * (bx1 - bx0 - W * 0.08) / 6
            fd.ellipse([x + 20, by + H * 0.005, x + 45, by + H * 0.03], fill=(255, 220, 120))
        fd.rounded_rectangle([bx1 - 10, H * (ground - 0.25), bx1 + 40, H * ground], 15, fill=(170, 110, 75))
    else:
        raise ValueError(kind)
    return im, fg, stars


def bed_pos(W, H):
    """Where a character lies in bed (head on pillow): x center, feet-y."""
    ground = 0.86 if W > H else 0.74
    bx0 = W * (0.22 if W > H else 0.08)
    return (bx0 + (20 + W * 0.15) / 2) / W, ground - 0.06 + 0.103 + 0.0
