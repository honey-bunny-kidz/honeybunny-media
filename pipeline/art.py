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

def star_pts(cx, cy, r, ri=None, rot=-math.pi / 2):
    ri = r * 0.45 if ri is None else ri
    return [(cx + (r if k % 2 == 0 else ri) * math.cos(rot + k * math.pi / 5),
             cy + (r if k % 2 == 0 else ri) * math.sin(rot + k * math.pi / 5)) for k in range(10)]


def _suit(im, shape, fill, stripes=(), dots=None, ol=OUT):
    """Paint a costume body over the sprite: shape = ("ellipse", cx, cy, rx, ry) or ("poly", pts).
    stripes = [(y0, y1, colour)] bands clipped to the shape; dots = (colour, [(x, y, r)])."""
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    if shape[0] == "ellipse":
        _, cx, cy, rx, ry = shape
        box = [cx - rx, cy - ry, cx + rx, cy + ry]
        ld.ellipse(box, fill=fill); md.ellipse(box, fill=255)
    else:
        ld.polygon(shape[1], fill=fill); md.polygon(shape[1], fill=255)
    for (y0, y1, col) in stripes:
        ld.rectangle([0, y0, im.width, y1], fill=col)
    if dots:
        col, pts = dots
        for (x, y, r) in pts:
            ld.ellipse([x - r, y - r * 1.3, x + r, y + r * 1.3], fill=col)
    lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", im.size, 0), mask))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    if shape[0] == "ellipse":
        d.ellipse(box, outline=ol, width=7)
    else:
        d.polygon(shape[1], outline=ol, width=7)
    return d


def _strawberry_pts(cx, cy, rx, ry, n=60):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        s = math.sin(a)
        pts.append((cx + rx * math.cos(a) * (1 - 0.42 * max(0.0, s) ** 1.5), cy + ry * s * (1.08 if s > 0 else 0.85)))
    return pts


def _leaf_crown(d, cx, cy, s, col=(110, 190, 90, 255)):
    for k in range(5):
        a = math.pi + k * math.pi / 4
        tip = (cx + math.cos(a) * 70 * s, cy + math.sin(a) * 34 * s + 14 * s)
        l = (cx + math.cos(a - 0.35) * 26 * s, cy + math.sin(a - 0.35) * 14 * s)
        r = (cx + math.cos(a + 0.35) * 26 * s, cy + math.sin(a + 0.35) * 14 * s)
        d.polygon([l, tip, r], fill=col, outline=OUT, width=6)
    E(d, cx, cy, 24 * s, 14 * s, col)
    d.line([cx, cy - 8 * s, cx + 8 * s, cy - 48 * s], fill=(120, 90, 60, 255), width=int(12 * s))

def bunny(eyes="open", m=0, fur=(236, 196, 140), inner=(255, 182, 193), bow=True, h=520, costume=None):
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
    if costume == "strawberry":   # red strawberry suit with yellow seeds and a leafy collar
        seeds = [(400 + dx, 800 + dy, 11) for dy in (0, 75, 150, 220) for dx in range(-180 + (dy // 75 % 2) * 45, 200, 90)
                 if abs(dx) < 205 - dy * 0.55]
        d = _suit(im, ("poly", _strawberry_pts(400, 875, 250, 215)), (238, 62, 82, 255), dots=((255, 225, 110, 255), seeds))
        for side in (-1, 1):
            E(d, 400 + side * 246, 850, 44, 58, fur + (255,))
        for k in range(-3, 4):
            x = 400 + k * 62
            d.polygon([(x - 42, 745), (x + 42, 745), (x + k * 12, 830 - abs(k) * 8)], fill=(110, 190, 90, 255), outline=OUT, width=6)
    elif costume == "pajamas":    # soft blue star pajamas with buttons
        stars = [(400 + dx, 800 + dy, 9) for dy in (0, 90, 180) for dx in (-140, -50, 50, 140) if not (dy == 0 and abs(dx) < 60)]
        d = _suit(im, ("ellipse", 400, 880, 215, 215), (178, 205, 250, 255), dots=((255, 255, 255, 235), stars))
        for side in (-1, 1):
            E(d, 400 + side * 185, 840, 55, 82, (178, 205, 250, 255))
            E(d, 400 + side * 185, 905, 40, 18, (255, 255, 255, 255), w=4)
        for yy in (760, 840, 920):
            E(d, 400, yy, 15, 15, (255, 215, 120, 255), w=4)
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
    if costume == "strawberry":
        _leaf_crown(d, 400, 312, 2.4)
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


def kitten(eyes="open", m=0, fur=(250, 236, 222), patch=(244, 170, 110), h=420, costume=None):
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
    if costume == "star":   # big twinkly yellow star suit
        sp = [(450 + dx, 800 + dy, 9) for (dx, dy) in ((-150, -10), (140, 0), (-60, 90), (70, 110), (0, 20), (-110, 170), (120, 180))]
        d = _suit(im, ("poly", star_pts(450, 790, 300, 150, rot=-math.pi / 2)), (255, 214, 70, 255), dots=((255, 250, 210, 255), sp))
        for side in (-1, 1):
            E(d, 450 + side * 95, 950, 80, 42, F)
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
    if costume == "star":   # sparkly headband with a little star
        d.arc([215, 150, 685, 520], 205, 335, fill=(255, 170, 210, 255), width=22)
        d.polygon(star_pts(450, 150, 62), fill=(255, 214, 70, 255), outline=OUT, width=6)
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


def puppy(eyes="open", m=0, h=400, costume=None):
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
    if costume == "firefighter":  # pretend firefighter coat (yellow with shiny stripes)
        COAT = (255, 200, 60, 255)
        d = _suit(im, ("ellipse", 450, 790, 195, 182), COAT, stripes=[(850, 880, (235, 240, 245, 255)), (880, 888, (200, 205, 215, 255))])
        for side in (-1, 1):
            E(d, 450 + side * 128, 875, 54, 68, COAT)
            d.rectangle([450 + side * 128 - 52, 900, 450 + side * 128 + 52, 918], fill=(235, 240, 245, 255))
            E(d, 450 + side * 128, 940, 40, 20, FUR, w=5)
        d.line([450, 640, 450, 960], fill=(210, 150, 40, 255), width=8)
        for yy in (720, 800):
            E(d, 450 - 30, yy, 13, 13, (90, 70, 60, 255), w=0)
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
    if costume == "firefighter":  # soft red pretend helmet with a gold star badge
        RED, DARK = (236, 70, 70, 255), (196, 45, 55, 255)
        E(d, 450, 268, 300, 48, DARK)
        d.chord([255, 70, 645, 400], 180, 360, fill=RED, outline=OUT, width=7)
        d.line([450, 78, 450, 230], fill=DARK, width=14)
        d.polygon(star_pts(450, 185, 52), fill=(255, 215, 80, 255), outline=OUT, width=5)
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


def _pumpkin_body(d, cx, cy, rx, ry, col=(255, 150, 50, 255), rib=(235, 120, 35, 255)):
    """Round cartoon pumpkin made of overlapping lobes."""
    for k, f in ((-2, 0.55), (2, 0.55), (-1, 0.75), (1, 0.75), (0, 0.6)):
        E(d, cx + k * rx * 0.24, cy, rx * f, ry, col)
    for k in (-1, 1):
        d.arc([cx + k * rx * 0.24 - rx * 0.2, cy - ry * 0.95, cx + k * rx * 0.24 + rx * 0.2, cy + ry * 0.95], 100 if k < 0 else -80, 260 if k < 0 else 80, fill=rib, width=6)


def _stem(d, cx, top, s):
    d.polygon([(cx - 22 * s, top + 10 * s), (cx - 12 * s, top - 60 * s), (cx + 18 * s, top - 70 * s), (cx + 22 * s, top + 10 * s)],
              fill=(110, 150, 70, 255), outline=OUT, width=6)
    E(d, cx + 70 * s, top - 30 * s, 55 * s, 26 * s, (120, 190, 90, 255), w=6)
    d.arc([cx - 60 * s, top - 80 * s, cx + 10 * s, top - 10 * s], 180, 320, fill=(110, 170, 80, 255), width=7)


def pumpkin(eyes="open", m=0, h=150, face=None):
    W, H = 600, 520
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _pumpkin_body(d, 300, 320, 260, 185)
    _stem(d, 300, 145, 1.0)
    if face == "smile":
        dark = (120, 55, 30, 255)
        glow = (255, 220, 110, 255)
        for side in (-1, 1):
            d.polygon([(300 + side * 95, 250), (300 + side * 55, 320), (300 + side * 135, 320)], fill=glow, outline=dark, width=6)
        d.chord([180, 300, 420, 450], 15, 165, fill=glow, outline=dark, width=6)
        d.rectangle([285, 400, 315, 440], fill=(255, 150, 50, 255))
    return finish(im, (int(h * W / H), h))


PUMPKIN_COLS = {"orange": ((255, 150, 50, 255), (235, 120, 35, 255)), "yellow": ((255, 214, 80, 255), (232, 180, 50, 255)),
                "white": ((252, 244, 228, 255), (225, 212, 190, 255)), "green": ((150, 205, 110, 255), (115, 170, 85, 255)),
                "coral": ((255, 128, 100, 255), (232, 98, 78, 255))}


def painted_pumpkin(eyes="open", m=0, h=150, col="orange", face="happy"):
    """Little pumpkin with a face PAINTED on (no carving): happy, sleepy, silly, surprised, giggle."""
    W, H = 600, 520
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = PUMPKIN_COLS[col]
    _pumpkin_body(d, 300, 320, 260, 185, c, r)
    _stem(d, 300, 145, 1.0)
    P = (70, 45, 55, 255)
    ex, ey, er = 95, 290, 30
    if face in ("happy", "surprised"):
        for sd in (-1, 1):
            rr = er * (1.25 if face == "surprised" else 1.0)
            E(d, 300 + sd * ex, ey, rr, rr * 1.2, P, w=0)
            E(d, 300 + sd * ex + rr * 0.3, ey - rr * 0.4, rr * 0.33, rr * 0.33, (255, 255, 255, 255), w=0)
    elif face in ("sleepy", "giggle"):
        for sd in (-1, 1):
            if face == "sleepy":
                d.arc([300 + sd * ex - 38, ey - 25, 300 + sd * ex + 38, ey + 25], 20, 160, fill=P, width=11)
            else:
                d.arc([300 + sd * ex - 38, ey - 15, 300 + sd * ex + 38, ey + 40], 200, 340, fill=P, width=11)
    elif face == "silly":
        E(d, 300 - ex, ey, er, er * 1.2, P, w=0)
        E(d, 300 - ex + 9, ey - 12, 10, 10, (255, 255, 255, 255), w=0)
        d.line([300 + ex - 36, ey - 18, 300 + ex + 30, ey], fill=P, width=11)
        d.line([300 + ex - 36, ey + 18, 300 + ex + 30, ey], fill=P, width=11)
    # pink painted cheeks
    for sd in (-1, 1):
        E(d, 300 + sd * 165, 355, 38, 22, (255, 150, 170, 255), w=0)
    if face == "happy":
        d.arc([215, 300, 385, 420], 20, 160, fill=P, width=12)
    elif face == "sleepy":
        E(d, 300, 385, 22, 26, P, w=0)
        for k, (zx, zy, zs) in enumerate(((430, 170, 1.0), (480, 120, 0.7))):
            z = 36 * zs
            d.line([zx, zy, zx + z, zy, zx, zy + z, zx + z, zy + z], fill=(120, 110, 200, 255), width=8)
    elif face == "silly":
        d.chord([220, 320, 380, 420], 0, 180, fill=P)
        E(d, 315, 418, 34, 30, (250, 120, 150, 255), ol=P, w=6)
    elif face == "surprised":
        E(d, 300, 392, 30, 36, P, w=0)
    elif face == "giggle":
        d.chord([215, 320, 385, 440], 0, 180, fill=P)
        E(d, 300, 412, 34, 16, (250, 120, 150, 255), w=0)
    return finish(im, (int(h * W / H), h))


def pumpkin_suit(eyes="open", m=0, h=420):
    """A friend dressed up in a big pumpkin costume (Pip inside: puppy feet, waggy tail, peeking eyes)."""
    W, H = 1000, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    FUR = (238, 190, 120, 255)
    d.arc([740, 430, 950, 640], 140, 330, fill=OUT, width=52)       # waggy tail peeking out
    d.arc([740, 430, 950, 640], 140, 330, fill=FUR, width=38)
    for side in (-1, 1):
        E(d, 450 + side * 110, 950, 85, 44, FUR)
        E(d, 450 + side * 110, 958, 50, 22, (255, 243, 225, 255), w=0)
    _pumpkin_body(d, 450, 600, 340, 320)
    _stem(d, 450, 285, 1.5)
    # peek window with eyes
    E(d, 450, 520, 210, 105, (238, 190, 120, 255), ol=(150, 75, 30, 255), w=10)
    for side in (-1, 1):
        eye(d, 450 + side * 90, 515, 44, eyes)
    cheeks(im, [(320, 560), (580, 560)], 40, 22)
    d = ImageDraw.Draw(im)
    E(d, 450, 552, 26, 18, (70, 45, 50, 255), w=0)
    # costume smile (opens when talking)
    if m == 0:
        d.arc([360, 640, 540, 740], 15, 165, fill=(150, 75, 30, 255), width=12)
    else:
        hh = 30 + 18 * m
        d.chord([370, 670 - hh, 530, 690 + hh], 0, 180, fill=(150, 50, 70, 255), outline=(150, 75, 30, 255), width=8)
    return finish(im, (int(h * W / H), h))


def autumn_tree(d, W, H, x, ground, s=1.0, cols=((255, 160, 60), (245, 110, 70), (255, 205, 80)), sw=None):
    sw = sw or s
    d.rectangle([x - W * 0.03 * sw, H * (ground - 0.55 * s), x + W * 0.03 * sw, H * ground], fill=(130, 85, 60))
    for i, (dx, dy, r) in enumerate(((0, 0.62, 0.12), (-0.08, 0.52, 0.09), (0.08, 0.52, 0.09), (0, 0.45, 0.1), (-0.05, 0.7, 0.08), (0.06, 0.68, 0.08))):
        cx, cy, rr = x + dx * W * sw, H * (ground - dy * s), r * W * sw
        d.ellipse([cx - rr, cy - rr * 0.85, cx + rr, cy + rr * 0.85], fill=cols[i % len(cols)])


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


def cricket(eyes="open", m=0, h=150):
    """Tiny friendly cricket: round green body, big head, curly antennae, little legs."""
    W, H = 900, 760
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    G, LG, DG = (130, 205, 95, 255), (190, 235, 150, 255), (95, 165, 70, 255)
    # back jumping legs
    for x0 in (560, 640):
        d.line([x0, 560, x0 + 110, 420, x0 + 150, 690], fill=OUT, width=34, joint="curve")
        d.line([x0, 560, x0 + 110, 420, x0 + 150, 690], fill=DG, width=20, joint="curve")
    # little front legs
    for x0 in (330, 420):
        d.line([x0, 600, x0 - 20, 700], fill=OUT, width=24)
        d.line([x0, 600, x0 - 20, 700], fill=DG, width=12)
    E(d, 530, 540, 230, 150, G)                       # body
    E(d, 560, 470, 170, 70, DG, w=5)                  # folded wings
    d.line([440, 470, 690, 470], fill=(80, 140, 60, 255), width=5)
    # antennae
    d.arc([120, 20, 380, 300], 200, 300, fill=OUT, width=10)
    d.arc([200, -20, 470, 260], 210, 300, fill=OUT, width=10)
    E(d, 140, 115, 18, 18, (255, 220, 110, 255), w=4)
    E(d, 235, 55, 18, 18, (255, 220, 110, 255), w=4)
    E(d, 310, 430, 200, 185, G)                       # head
    E(d, 310, 500, 120, 70, LG, w=0)
    for side in (-1, 1):
        eye(d, 310 + side * 78, 400, 42, eyes)
    cheeks(im, [(200, 490), (420, 490)], 36, 20)
    d = ImageDraw.Draw(im)
    mouth(d, 310, 500, 0.7, m)
    return finish(im, (int(h * W / H), h))


def frog(eyes="open", m=0, h=200):
    """Cute little green frog with big eyes on top and a wide smile."""
    W, H = 900, 820
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    G, LG, DG = (120, 200, 110, 255), (205, 240, 170, 255), (95, 170, 90, 255)
    for side in (-1, 1):                              # back legs
        E(d, 450 + side * 270, 690, 150, 95, DG)
        E(d, 450 + side * 330, 775, 95, 34, G)
    E(d, 450, 560, 300, 230, G)                       # body
    E(d, 450, 630, 190, 150, LG, w=0)
    for side in (-1, 1):                              # front feet
        E(d, 450 + side * 120, 780, 70, 32, G)
    E(d, 450, 380, 320, 200, G)                       # head
    for side in (-1, 1):                              # eye bumps
        E(d, 450 + side * 165, 220, 115, 110, G)
        E(d, 450 + side * 165, 225, 82, 80, (255, 255, 255, 255), w=0)
        eye(d, 450 + side * 165, 230, 46, eyes)
    cheeks(im, [(250, 430), (650, 430)], 52, 30)
    d = ImageDraw.Draw(im)
    for side in (-1, 1):
        E(d, 450 + side * 30, 360, 8, 6, (70, 120, 65, 255), w=0)
    if m == 0:
        d.arc([300, 340, 600, 470], 25, 155, fill=OUT, width=10)
    else:
        hh = 30 + 26 * m
        d.chord([310, 420 - hh * 0.3, 590, 430 + hh], 0, 180, fill=(150, 50, 70, 255), outline=OUT, width=8)
        E(d, 450, 425 + hh * 0.8, 60, hh * 0.25, (245, 130, 150, 255), w=0)
    return finish(im, (int(h * W / H), h))


def ball(eyes="open", m=0, h=150):
    """Pip's red play ball: a big CIRCLE."""
    W = H = 400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    E(d, 200, 200, 180, 180, (240, 80, 80, 255), w=9)
    d.arc([40, 90, 360, 330], 200, 340, fill=(255, 255, 255, 255), width=26)
    d.arc([40, 70, 360, 310], 20, 160, fill=(255, 210, 90, 255), width=26)
    E(d, 120, 110, 34, 22, (255, 255, 255, 200), w=0)
    return finish(im, (h, h))


def block(eyes="open", m=0, h=150):
    """A blue toy block: a SQUARE with a yellow star."""
    W = H = 400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 380, 380], 26, fill=(95, 160, 240, 255), outline=OUT, width=10)
    d.rounded_rectangle([55, 55, 345, 345], 18, outline=(170, 210, 255, 255), width=10)
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = 110 if k % 2 == 0 else 46
        pts.append((200 + r * math.cos(a), 210 + r * math.sin(a)))
    d.polygon(pts, fill=(255, 215, 80, 255), outline=OUT, width=7)
    return finish(im, (h, h))


def sandwich(eyes="open", m=0, h=150):
    """A triangle jam sandwich: a TRIANGLE."""
    W, H = 460, 400
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tri = [(230, 28), (24, 376), (436, 376)]
    d.polygon(tri, fill=(225, 165, 95, 255))
    d.line(tri + [tri[0]], fill=OUT, width=12, joint="curve")
    d.polygon([(230, 82), (72, 350), (388, 350)], fill=(255, 246, 225, 255))
    for (x, y, r) in ((230, 255, 62), (180, 300, 40), (285, 300, 44), (230, 315, 40)):
        E(d, x, y, r, r * 0.8, (235, 90, 120, 255), w=0)
    E(d, 212, 238, 14, 10, (255, 170, 190, 255), w=0)
    return finish(im, (int(h * W / H), h))


def swing_set(d, W, H, x, ground, s):
    """A-frame swing set (triangle legs) with a little seat."""
    top, half = H * (ground - 0.36 * s), H * 0.17 * s
    col = (235, 120, 110)
    for cx in (x - H * 0.2 * s, x + H * 0.2 * s):
        d.line([(cx, top), (cx - half * 0.7, H * ground)], fill=col, width=int(16 * s) + 2)
        d.line([(cx, top), (cx + half * 0.7, H * ground)], fill=col, width=int(16 * s) + 2)
    d.line([(x - H * 0.22 * s, top), (x + H * 0.22 * s, top)], fill=(240, 175, 90), width=int(18 * s) + 2)
    for k in (-1, 1):
        d.line([(x + k * H * 0.06 * s, top), (x + k * H * 0.06 * s, H * (ground - 0.1 * s))], fill=(150, 120, 110), width=int(5 * s) + 2)
    d.rounded_rectangle([x - H * 0.08 * s, H * (ground - 0.11 * s), x + H * 0.08 * s, H * (ground - 0.085 * s)], 8, fill=(120, 190, 240))


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
    "pumpkin": dict(fn=pumpkin, kw=dict(), h=0.13),
    "pumpkin_smile": dict(fn=pumpkin, kw=dict(face="smile"), h=0.13),
    "p_happy": dict(fn=painted_pumpkin, kw=dict(col="orange", face="happy"), h=0.13),
    "p_sleepy": dict(fn=painted_pumpkin, kw=dict(col="yellow", face="sleepy"), h=0.13),
    "p_silly": dict(fn=painted_pumpkin, kw=dict(col="white", face="silly"), h=0.13),
    "p_surprised": dict(fn=painted_pumpkin, kw=dict(col="green", face="surprised"), h=0.13),
    "p_giggle": dict(fn=painted_pumpkin, kw=dict(col="coral", face="giggle"), h=0.13),
    "pumpkinpip": dict(fn=pumpkin_suit, kw=dict(), h=0.42),
    "honey_berry": dict(fn=bunny, kw=dict(costume="strawberry", bow=False), h=0.44),
    "honey_pj": dict(fn=bunny, kw=dict(costume="pajamas"), h=0.44),
    "pip_fire": dict(fn=puppy, kw=dict(costume="firefighter"), h=0.40),
    "mimi_star": dict(fn=kitten, kw=dict(costume="star"), h=0.40),
    "cricket": dict(fn=cricket, kw=dict(), h=0.12),
    "frog": dict(fn=frog, kw=dict(), h=0.16),
    "ball": dict(fn=ball, kw=dict(), h=0.15),
    "block": dict(fn=block, kw=dict(), h=0.15),
    "sandwich": dict(fn=sandwich, kw=dict(), h=0.13),
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
    elif kind == "pumpkin_patch":
        im = grad(W, H, (150, 205, 245), (255, 228, 185))
        d = ImageDraw.Draw(im)
        d.ellipse([W * 0.08, H * 0.07, W * 0.08 + H * 0.14, H * 0.21], fill=(255, 220, 110))
        for i in range(3):
            cloud(d, rnd.uniform(W * 0.25, W * 0.85), rnd.uniform(H * 0.05, H * 0.22), H / 1000, (255, 250, 245))
        hills(d, W, H, ground - 0.14, 0.07, (225, 195, 130), 2)
        if W > H:
            autumn_tree(d, W, H, W * 0.1, ground - 0.08, 0.9)
            autumn_tree(d, W, H, W * 0.9, ground - 0.09, 1.0, ((245, 110, 70), (255, 185, 70), (230, 140, 60)))
        else:
            autumn_tree(d, W, H, W * 0.12, ground - 0.08, 0.62, sw=1.5)
            autumn_tree(d, W, H, W * 0.88, ground - 0.09, 0.68, ((245, 110, 70), (255, 185, 70), (230, 140, 60)), sw=1.6)
        hills(d, W, H, ground - 0.04, 0.035, (170, 195, 105), 4)
        # wooden fence
        fy0, fy1 = H * (ground - 0.15), H * (ground - 0.04)
        step = W / 14
        for k in range(15):
            fx = k * step + step * 0.3
            d.rounded_rectangle([fx - 9, fy0, fx + 9, fy1], 6, fill=(205, 150, 105))
        for fy in (fy0 + (fy1 - fy0) * 0.25, fy0 + (fy1 - fy0) * 0.65):
            d.rectangle([0, fy - 7, W, fy + 7], fill=(190, 135, 95))
        # hay bale
        hx, hy, hw = W * (0.8 if W > H else 0.72), H * (ground - 0.02), min(W, H) * 0.18
        d.rounded_rectangle([hx - hw / 2, hy - hw * 0.55, hx + hw / 2, hy], 20, fill=(240, 205, 110), outline=(200, 160, 80), width=5)
        for k in range(1, 4):
            d.line([hx - hw / 2 + 10, hy - hw * 0.55 * k / 4, hx + hw / 2 - 10, hy - hw * 0.55 * k / 4], fill=(215, 175, 85), width=4)
        d.rectangle([0, H * ground, W, H], fill=(150, 175, 90))
        hills(d, W, H, ground + 0.01, 0.02, (150, 175, 90), 7)
        # pumpkins in the patch with curly vines
        s = H / 1080
        spots = [(0.05, 0.02, 0.9), (0.21, 0.07, 0.7), (0.38, 0.02, 0.55), (0.62, 0.08, 0.65), (0.95, 0.03, 1.0), (0.72, 0.0, 0.5), (0.5, 0.11, 0.8)]
        if W < H:
            spots = [(0.1, 0.05, 1.0), (0.35, 0.12, 0.8), (0.9, 0.06, 1.1), (0.65, 0.16, 0.9)]
        for (px, py, ps) in spots:
            x, y = W * px, H * (ground + py)
            d.arc([x - 120 * s, y - 40 * s, x + 30 * s, y + 30 * s], 160, 340, fill=(100, 150, 70), width=int(6 * s) + 1)
            pr = 70 * s * ps
            for k, f in ((-1, 0.62), (1, 0.62), (0, 0.7)):
                d.ellipse([x + k * pr * 0.35 - pr * f, y - pr * 0.75, x + k * pr * 0.35 + pr * f, y + pr * 0.15], fill=(250, 145, 50), outline=(205, 105, 35), width=3)
            d.rectangle([x - 6 * s * ps, y - pr * 0.95, x + 6 * s * ps, y - pr * 0.7], fill=(110, 150, 70))
        # falling leaves
        for k in range(10):
            lx, ly = rnd.uniform(0, W), rnd.uniform(H * 0.1, H * (ground - 0.2))
            c = rnd.choice([(255, 160, 60), (240, 110, 70), (255, 205, 80)])
            d.ellipse([lx - 14 * s, ly - 8 * s, lx + 14 * s, ly + 8 * s], fill=c)
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
    elif kind == "night_garden":
        # Honey's cottage porch at night: glowing window, lantern, oak tree, little pond, fireflies
        im = grad(W, H, (28, 30, 85), (120, 85, 150))
        d = ImageDraw.Draw(im)
        land = W > H
        for _ in range(int(120 * W * H / (1920 * 1080))):
            stars.append((rnd.uniform(0, W), rnd.uniform(0, H * (ground - 0.3)), rnd.uniform(1.5, 3.6), rnd.uniform(0, 6.28)))
        hills(d, W, H, ground - 0.13, 0.07, (50, 80, 120), 2)
        tree(d, W, H, W * (0.74 if land else 0.62), True)
        # cottage on the left with a warm window
        hx, hw = W * (0.1 if land else 0.12), min(W, H) * (0.42 if land else 0.36)
        top = H * (ground - (0.40 if land else 0.26))
        d.rectangle([hx - hw / 2, top, hx + hw / 2, H * ground], fill=(150, 120, 140))
        d.polygon([(hx - hw * 0.62, top + 6), (hx, top - hw * 0.45), (hx + hw * 0.62, top + 6)], fill=(150, 70, 95))
        wy = top + (H * ground - top) * 0.22
        ww = hw * 0.26
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([hx + hw * 0.18 - ww * 2, wy - ww * 1.4, hx + hw * 0.18 + ww * 2, wy + ww * 2.6], fill=(255, 210, 120, 90))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im)
        d.rectangle([hx + hw * 0.18 - ww / 2, wy, hx + hw * 0.18 + ww / 2, wy + ww * 1.1], fill=(255, 220, 140), outline=(110, 80, 90), width=6)
        d.line([hx + hw * 0.18, wy, hx + hw * 0.18, wy + ww * 1.1], fill=(110, 80, 90), width=5)
        d.rounded_rectangle([hx - hw * 0.32, H * (ground - 0.2 if land else ground - 0.13), hx - hw * 0.06, H * ground], 20, fill=(110, 75, 70))
        # porch lantern
        lx, ly = hx + hw * 0.5, top + (H * ground - top) * 0.45
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - H * 0.12, ly - H * 0.12, lx + H * 0.12, ly + H * 0.12], fill=(255, 215, 130, 110))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(35)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([lx - H * 0.018, ly - H * 0.03, lx + H * 0.018, ly + H * 0.03], 8, fill=(255, 225, 140), outline=(110, 80, 90), width=4)
        hills(d, W, H, ground - 0.02, 0.04, (45, 110, 95), 3)
        d.rectangle([0, H * ground, W, H], fill=(45, 110, 95))
        # little pond with lily pads
        px0, px1 = (W * 0.80, W * 1.02) if land else (W * 0.55, W * 1.05)
        py = H * (ground + 0.05)
        d.ellipse([px0, py - H * 0.035, px1, py + H * 0.05], fill=(70, 105, 170))
        d.ellipse([px0 + W * 0.02, py - H * 0.02, px1 - W * 0.02, py + H * 0.035], fill=(95, 135, 195))
        for k in range(3):
            lx2 = px0 + (px1 - px0) * (0.25 + k * 0.25)
            d.pieslice([lx2 - H * 0.025, py - H * 0.01, lx2 + H * 0.025, py + H * 0.02], 30, 330, fill=(80, 150, 90))
        flowers(d, W, H, ground * H, 40, 13, night=True)
        # fireflies (twinkle like stars)
        for _ in range(9):
            stars.append((rnd.uniform(W * 0.25, W * 0.95), rnd.uniform(H * (ground - 0.32), H * (ground - 0.05)), rnd.uniform(3, 5), rnd.uniform(0, 6.28)))
    elif kind == "playground":
        im = grad(W, H, (140, 210, 252), (245, 250, 235))
        d = ImageDraw.Draw(im)
        for cx, cy in ((0.30, 0.10), (0.68, 0.06), (0.86, 0.17)):
            cloud(d, W * cx, H * cy, min(W, H) / 1050, (255, 255, 255))
        sx, sy, sr = W * (0.55 if W > H else 0.62), H * (0.20 if W > H else 0.14), min(W, H) * 0.075
        d.ellipse([sx - sr * 1.35, sy - sr * 1.35, sx + sr * 1.35, sy + sr * 1.35], fill=(255, 240, 170))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 215, 90))
        hills(d, W, H, ground - 0.13, 0.07, (165, 222, 150), 8)
        land = W > H
        tree(d, W, H, W * (0.08 if land else 0.1), False)
        swing_set(d, W, H, W * (0.83 if land else 0.78), ground - 0.02, 1.0 if land else 0.75)
        hills(d, W, H, ground - 0.02, 0.035, (130, 205, 115), 9)
        # checkered picnic blanket at the front
        bx0, bx1 = W * (0.30 if land else 0.12), W * (0.62 if land else 0.75)
        by0, by1 = H * (ground + 0.03), H * (ground + 0.12)
        d.polygon([(bx0 + W * 0.03, by0), (bx1 + W * 0.03, by0), (bx1, by1), (bx0, by1)], fill=(255, 255, 255))
        n = 8
        for i in range(n):
            for j in range(3):
                if (i + j) % 2 == 0:
                    t0, t1 = j / 3, (j + 1) / 3
                    def P(u, t):
                        xl = bx0 + W * 0.03 * (1 - t)
                        xr = bx1 + W * 0.03 * (1 - t)
                        return (xl + (xr - xl) * u, by0 + (by1 - by0) * t)
                    d.polygon([P(i / n, t0), P((i + 1) / n, t0), P((i + 1) / n, t1), P(i / n, t1)], fill=(250, 140, 150))
        flowers(d, W, H, ground * H, 45, 17)
    elif kind == "autumn_porch":
        # Honey's cottage front porch on an autumn afternoon: wooden wall, door with leaf wreath,
        # window, leaf garland, a long low pumpkin shelf, potted yellow flowers, wooden floor, leaves
        land = W > H
        im = grad(W, H, (160, 210, 245), (255, 232, 200))
        d = ImageDraw.Draw(im)
        s = H / 1080
        sx = W * 0.86 if land else W * 0.74
        d.ellipse([sx, H * 0.02, sx + H * 0.1, H * 0.12], fill=(255, 222, 110))
        for cx, cy in ((0.18, 0.03), (0.55, 0.05)) if land else ((0.25, 0.06), (0.62, 0.13)):
            cloud(d, W * cx, H * cy, H / 1300, (255, 255, 255))
        wall_top = H * (ground - (0.62 if land else 0.40))
        d.rectangle([0, wall_top, W, H * ground], fill=(250, 226, 192))
        for k in range(1, 14):
            yy = wall_top + (H * ground - wall_top) * k / 14
            d.line([0, yy, W, yy], fill=(236, 206, 168), width=max(2, int(3 * s)))
        d.rectangle([0, wall_top - 18 * s, W, wall_top + 6 * s], fill=(205, 120, 105))
        # door with a leafy wreath
        dx, dw = W * (0.2 if land else 0.24), W * (0.13 if land else 0.24)
        dtop = H * (ground - (0.48 if land else 0.31))
        d.rounded_rectangle([dx - dw / 2, dtop, dx + dw / 2, H * ground], int(40 * s), fill=(160, 105, 75), outline=(125, 80, 60), width=int(6 * s) + 1)
        d.ellipse([dx + dw * 0.28 - 9 * s, H * (ground - 0.2) - 9 * s, dx + dw * 0.28 + 9 * s, H * (ground - 0.2) + 9 * s], fill=(255, 210, 90))
        wx, wy, wr = dx, dtop + (H * ground - dtop) * 0.25, dw * 0.3
        for k in range(14):
            a = k / 14 * 6.283
            cc = [(240, 110, 70), (255, 175, 60), (210, 80, 70), (250, 200, 80)][k % 4]
            lx, ly = wx + math.cos(a) * wr, wy + math.sin(a) * wr
            d.ellipse([lx - 22 * s, ly - 13 * s, lx + 22 * s, ly + 13 * s], fill=cc)
        d.polygon([(wx - 16 * s, wy + wr + 4 * s), (wx, wy + wr - 12 * s), (wx + 16 * s, wy + wr + 4 * s)], fill=(240, 120, 150))
        # window with flower box
        if land:
            for wx2 in (W * 0.80,):
                ww, wh = W * 0.12, H * 0.17
                wy2 = H * (ground - 0.47)
                d.rounded_rectangle([wx2 - ww / 2, wy2, wx2 + ww / 2, wy2 + wh], int(14 * s), fill=(170, 215, 245), outline=(255, 255, 255), width=int(9 * s))
                d.line([wx2, wy2, wx2, wy2 + wh], fill=(255, 255, 255), width=int(7 * s))
                d.line([wx2 - ww / 2, wy2 + wh / 2, wx2 + ww / 2, wy2 + wh / 2], fill=(255, 255, 255), width=int(7 * s))
        # leaf garland
        gy = wall_top + 30 * s
        for k in range(int(W / (60 * s)) + 1):
            gx = k * 60 * s + 20 * s
            sag = math.sin((k % 6) / 6 * math.pi) * 28 * s
            cc = [(240, 110, 70), (255, 175, 60), (250, 205, 80), (215, 90, 70)][k % 4]
            d.ellipse([gx - 20 * s, gy + sag - 12 * s, gx + 20 * s, gy + sag + 12 * s], fill=cc)
        # long low pumpkin shelf (pumpkins stand on y = ground - 0.055)
        sx0, sx1 = W * (0.33 if land else 0.06), W * (0.97 if land else 0.94)
        st = H * (ground - 0.055)
        d.rounded_rectangle([sx0, st, sx1, st + 22 * s], int(8 * s), fill=(185, 125, 85), outline=(140, 90, 65), width=int(4 * s) + 1)
        for lx in (sx0 + 30 * s, (sx0 + sx1) / 2, sx1 - 30 * s):
            d.rectangle([lx - 12 * s, st + 22 * s, lx + 12 * s, H * ground], fill=(165, 110, 75))
        # potted yellow flowers
        for px in ((W * 0.04, W * 0.98) if land else (W * 0.05,)):
            pw = 70 * s
            d.polygon([(px - pw, H * (ground - 0.075)), (px + pw, H * (ground - 0.075)), (px + pw * 0.75, H * ground), (px - pw * 0.75, H * ground)], fill=(205, 115, 80))
            for k in range(7):
                fx2 = px + (k - 3) * 22 * s
                fy2 = H * (ground - 0.09) - (abs(3 - k) < 2) * 26 * s
                d.ellipse([fx2 - 22 * s, fy2 - 22 * s, fx2 + 22 * s, fy2 + 22 * s], fill=(255, 205, 60))
                d.ellipse([fx2 - 8 * s, fy2 - 8 * s, fx2 + 8 * s, fy2 + 8 * s], fill=(220, 140, 60))
        # wooden porch floor
        d.rectangle([0, H * ground, W, H], fill=(205, 150, 105))
        for k in range(8):
            yy = H * ground + (H - H * ground) * (k / 8) ** 1.3
            d.line([0, yy, W, yy], fill=(185, 130, 90), width=max(2, int(4 * s)))
        for k in range(12):
            lx, ly = rnd.uniform(0, W), rnd.uniform(H * (ground + 0.02), H * 0.99)
            cc = rnd.choice([(240, 110, 70), (255, 175, 60), (250, 205, 80)])
            d.ellipse([lx - 16 * s, ly - 9 * s, lx + 16 * s, ly + 9 * s], fill=cc)
    elif kind == "playroom":
        # Honey's sunny dress-up playroom: peach polka-dot wall, window, bunting, mirror, costume trunk, rug
        L = W > H
        im = grad(W, H, (255, 222, 200), (255, 236, 214))
        d = ImageDraw.Draw(im)
        for yy in range(0, int(H * ground), int(H * 0.09)):
            for xx in range(0, W + 60, int(H * 0.09)):
                off = (H * 0.045) if (yy // int(H * 0.09)) % 2 else 0
                d.ellipse([xx + off - 7, yy + H * 0.05 - 7, xx + off + 7, yy + H * 0.05 + 7], fill=(255, 205, 190))
        # window with afternoon sky and an autumn tree
        wx0, wx1 = W * (0.36 if L else 0.22), W * (0.64 if L else 0.78)
        wy0, wy1 = H * (0.14 if L else 0.08), H * (0.52 if L else 0.27)
        d.rounded_rectangle([wx0 - 16, wy0 - 16, wx1 + 16, wy1 + 16], 18, fill=(255, 250, 240), outline=OUT, width=5)
        sky = grad(int(wx1 - wx0), int(wy1 - wy0), (140, 200, 250), (215, 238, 255))
        sd = ImageDraw.Draw(sky)
        sw_, sh_ = sky.size
        sd.ellipse([-sw_ * 0.2, sh_ * 0.72, sw_ * 1.2, sh_ * 1.6], fill=(150, 205, 120))
        sd.rectangle([sw_ * 0.72, sh_ * 0.4, sw_ * 0.77, sh_ * 0.85], fill=(140, 95, 70))
        for (cx, cy, r, col) in ((0.745, 0.33, 0.2, (255, 160, 60)), (0.66, 0.42, 0.13, (245, 110, 70)), (0.83, 0.42, 0.13, (255, 205, 80))):
            sd.ellipse([sw_ * cx - sh_ * r, sh_ * cy - sh_ * r, sw_ * cx + sh_ * r, sh_ * cy + sh_ * r], fill=col)
        sd.ellipse([sw_ * 0.12, sh_ * 0.12, sw_ * 0.12 + sh_ * 0.2, sh_ * 0.32], fill=(255, 225, 120))
        for (cx, cy) in ((0.38, 0.2), (0.5, 0.16)):
            sd.ellipse([sw_ * cx - sh_ * 0.12, sh_ * cy - sh_ * 0.05, sw_ * cx + sh_ * 0.12, sh_ * cy + sh_ * 0.05], fill=(255, 255, 255))
        im.paste(sky, (int(wx0), int(wy0)))
        d = ImageDraw.Draw(im)
        d.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=(255, 250, 240), width=12)
        d.line([wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2], fill=(255, 250, 240), width=12)
        # bunting
        cols = [(255, 120, 150), (255, 200, 80), (120, 200, 240), (150, 215, 130), (200, 160, 240)]
        n = 9 if L else 6
        d.line([0, H * 0.035, W, H * 0.035], fill=(200, 150, 120), width=4)
        for i in range(n):
            x = W * (i + 0.5) / n
            d.polygon([(x - W * 0.03, H * 0.035), (x + W * 0.03, H * 0.035), (x, H * 0.035 + H * 0.07)], fill=cols[i % 5], outline=OUT, width=3)
        # round mirror on the wall
        mx, my, mr = W * (0.86 if L else 0.84), H * (0.36 if L else 0.36), H * (0.11 if L else 0.055)
        d.ellipse([mx - mr - 14, my - mr * 1.3 - 14, mx + mr + 14, my + mr * 1.3 + 14], fill=(255, 190, 210), outline=OUT, width=5)
        d.ellipse([mx - mr, my - mr * 1.3, mx + mr, my + mr * 1.3], fill=(215, 238, 250))
        d.line([mx - mr * 0.4, my - mr * 0.7, mx + mr * 0.1, my - mr * 1.1], fill=(255, 255, 255), width=8)
        # floor + rug
        d.rectangle([0, H * ground, W, H], fill=(214, 160, 110))
        for k in range(1, 6):
            d.line([0, H * ground + k * H * 0.03, W, H * ground + k * H * 0.03], fill=(196, 142, 96), width=2)
        d.rectangle([0, H * ground - 6, W, H * ground + 4], fill=(240, 200, 160))
        d.ellipse([W * 0.2, H * (ground + 0.01), W * 0.8, H * (ground + 0.12)], fill=(180, 210, 245), outline=(150, 180, 230), width=6)
        d.ellipse([W * 0.28, H * (ground + 0.03), W * 0.72, H * (ground + 0.10)], outline=(255, 255, 255), width=5)
        # dress-up trunk with colourful clothes peeking out (left)
        tx0, tx1 = W * (0.0 if L else 0.0), W * (0.13 if L else 0.2)
        ty0 = H * (ground - (0.17 if L else 0.08))
        for (dx, col) in ((0.2, (255, 120, 150)), (0.5, (150, 215, 130)), (0.8, (255, 200, 80))):
            x = tx0 + (tx1 - tx0) * dx
            d.ellipse([x - W * 0.03, ty0 - H * 0.04, x + W * 0.03, ty0 + H * 0.03], fill=col, outline=OUT, width=4)
        d.rounded_rectangle([tx0 - 10, ty0, tx1, H * ground + 6], 14, fill=(200, 120, 80), outline=OUT, width=5)
        d.rectangle([tx0 - 10, ty0 + (H * ground - ty0) * 0.35, tx1, ty0 + (H * ground - ty0) * 0.45], fill=(240, 190, 90))
        d.ellipse([(tx0 + tx1) / 2 - 10, ty0 + (H * ground - ty0) * 0.3, (tx0 + tx1) / 2 + 10, ty0 + (H * ground - ty0) * 0.5], fill=(150, 90, 60))
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
