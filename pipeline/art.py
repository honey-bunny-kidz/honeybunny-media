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
        if costume == "raincoat":   # shiny red rain boots
            d.rounded_rectangle([400 + side * 115 - 82, 985, 400 + side * 115 + 82, 1132], 34, fill=(232, 74, 88, 255), outline=OUT, width=7)
            d.rounded_rectangle([400 + side * 115 - 82, 985, 400 + side * 115 + 82, 1018], 14, fill=(250, 120, 130, 255), outline=OUT, width=6)
            E(d, 400 + side * 115 - 40, 1070, 12, 30, (255, 255, 255, 150), w=0)
        else:
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
    elif costume == "raincoat":   # sunny yellow raincoat with big buttons and a pocket
        COAT = (255, 212, 70, 255)
        d = _suit(im, ("ellipse", 400, 885, 222, 222), COAT, stripes=[(1040, 1060, (240, 185, 50, 255))])
        for side in (-1, 1):
            E(d, 400 + side * 188, 845, 58, 86, COAT)
            E(d, 400 + side * 188, 920, 36, 20, fur + (255,), w=5)
        d.line([400, 690, 400, 1100], fill=(225, 170, 40, 255), width=8)
        for yy in (770, 860, 950):
            E(d, 430, yy, 16, 16, (90, 160, 230, 255), w=4)
        d.rounded_rectangle([250, 930, 340, 1000], 14, fill=(250, 196, 55, 255), outline=OUT, width=5)
        d.polygon([(330, 680), (400, 760), (470, 680)], fill=(240, 185, 50, 255), outline=OUT, width=6)
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
    if costume == "cosy":  # chilly-day outfit (ep023): pink fluffy earmuffs + green striped scarf
        GR, GL = (110, 195, 125, 255), (170, 230, 175, 255)
        d.rounded_rectangle([200, 745, 600, 830], 40, fill=GR, outline=OUT, width=8)
        for xx in (270, 360, 450, 540):
            d.line([(xx, 752), (xx, 823)], fill=GL, width=16)
        d.polygon([(470, 800), (545, 800), (560, 1010), (480, 1010)], fill=GR, outline=OUT, width=7)
        for yy in (870, 940):
            d.line([(474, yy), (552, yy)], fill=(255, 255, 255, 255), width=12)
        d.arc([150, 300, 650, 760], 200, 340, fill=OUT, width=30)
        d.arc([150, 300, 650, 760], 200, 340, fill=(255, 150, 190, 255), width=18)
        for side in (-1, 1):
            E(d, 400 + side * 262, 500, 66, 72, (255, 170, 205, 255), w=8)
            E(d, 400 + side * 262 - 14, 482, 22, 18, (255, 225, 238, 255), w=0)
    if costume == "strawberry":
        _leaf_crown(d, 400, 312, 2.4)
    return finish(im, (int(h * W / H), h))


def _drops(d, pts, col=(120, 190, 250, 255)):
    """Shiny water drops (teardrop shapes) at (x, y, r)."""
    for (x, y, r) in pts:
        d.polygon([(x, y - r * 2.1), (x - r * 0.85, y - r * 0.3), (x + r * 0.85, y - r * 0.3)], fill=col)
        E(d, x, y, r, r, col, w=4)
        E(d, x - r * 0.35, y - r * 0.3, r * 0.28, r * 0.28, (255, 255, 255, 230), w=0)


def duckling(eyes="open", m=0, h=330, beads=False):
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
    if beads:   # raindrops sitting on top of waterproof feathers, ready to roll off
        _drops(d, [(560, 460, 34), (660, 520, 30), (455, 445, 26), (290, 150, 26), (480, 170, 24), (610, 600, 26)])
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


def kitten(eyes="open", m=0, fur=(250, 236, 222), patch=(244, 170, 110), h=420, costume=None, bell=True):
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
    if bell:
        E(d, 450, 690, 26, 26, (255, 215, 80, 255), w=5)
    else:  # empty little ring where the bell should be
        d.ellipse([440, 668, 460, 690], outline=(255, 105, 160, 255), width=6)
    if costume == "star":   # sparkly headband with a little star
        d.arc([215, 150, 685, 520], 205, 335, fill=(255, 170, 210, 255), width=22)
        d.polygon(star_pts(450, 150, 62), fill=(255, 214, 70, 255), outline=OUT, width=6)
    return finish(im, (int(h * W / H), h))


def lamb(eyes="open", m=0, h=400, foam=False):
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
    if foam:
        _foam(im)
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
    if costume == "pajamas":  # mint-green sleepover pajamas with little yellow moons (ep022)
        PJ = (170, 225, 200, 255)
        d = _suit(im, ("ellipse", 450, 790, 195, 182), PJ)
        for side in (-1, 1):
            E(d, 450 + side * 128, 875, 54, 68, PJ)
            E(d, 450 + side * 128, 940, 40, 20, FUR, w=5)
        for (x, y) in ((360, 720), (540, 740), (420, 850), (560, 870), (330, 900)):
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(255, 225, 110, 255))
            d.ellipse([x - 8, y - 26, x + 28, y + 10], fill=PJ)
        for yy in (700, 790, 880):
            E(d, 450, yy, 12, 12, (255, 255, 255, 255), w=4)
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
    if costume == "drippy":  # rain-soaked fur: little drops flying off for a big shake
        _drops(d, [(120, 330, 36), (80, 540, 30), (780, 330, 36), (830, 540, 30), (200, 150, 30), (700, 150, 30), (450, 100, 32)])
        for (x, y) in ((260, 300), (640, 300), (450, 230)):
            d.arc([x - 40, y - 40, x + 40, y + 40], 200, 340, fill=(120, 190, 250, 255), width=8)
    if costume == "firefighter":  # soft red pretend helmet with a gold star badge
        RED, DARK = (236, 70, 70, 255), (196, 45, 55, 255)
        E(d, 450, 268, 300, 48, DARK)
        d.chord([255, 70, 645, 400], 180, 360, fill=RED, outline=OUT, width=7)
        d.line([450, 78, 450, 230], fill=DARK, width=14)
        d.polygon(star_pts(450, 185, 52), fill=(255, 215, 80, 255), outline=OUT, width=5)
    if costume == "leafy":  # popped out of the leaf pile: a few leaves stuck on head and ears
        for (x, y, L, c, r) in ((330, 190, 150, "red", -0.5), (470, 165, 170, "yellow", 0.3), (590, 215, 140, "orange", 0.9),
                                (190, 520, 120, "orange", -0.2), (710, 540, 120, "red", 0.4)):
            _leaf(d, x, y, L, c, r)
    if costume == "captain":  # folded paper captain hat (pretend ship game) with a gold star
        d.polygon([(250, 250), (650, 250), (450, 28)], fill=(255, 255, 255, 255), outline=OUT, width=8)
        d.line([(300, 222), (450, 70), (600, 222)], fill=(225, 230, 240, 255), width=6)
        d.rounded_rectangle([238, 222, 662, 272], 14, fill=(90, 160, 240, 255), outline=OUT, width=7)
        d.polygon(star_pts(450, 165, 40), fill=(255, 215, 80, 255), outline=OUT, width=5)
    if costume == "muddy":  # muddy paws, ears, nose-tip and tail after playing outside
        MUD = (150, 105, 70, 235)
        for (x, y, rx, ry) in ((360, 945, 60, 30), (560, 950, 55, 28), (330, 880, 34, 30), (575, 885, 32, 28),
                               (180, 560, 40, 52), (725, 575, 38, 48), (560, 300, 46, 34), (395, 600, 34, 22),
                               (760, 640, 36, 30), (520, 760, 40, 34)):
            E(d, x, y, rx, ry, MUD, w=0)
            E(d, x + rx * 0.5, y + ry * 0.7, rx * 0.35, ry * 0.3, MUD, w=0)
    if costume == "bubbly":  # bubble-bath foam crown on the head + a few bubbles on the ears
        for (x, y, r) in ((300, 215, 70), (380, 165, 82), (470, 145, 90), (560, 170, 80), (630, 220, 66),
                          (420, 95, 52), (520, 85, 48), (470, 40, 38), (175, 470, 46), (735, 480, 44)):
            E(d, x, y, r, r * 0.92, (255, 255, 255, 255), ol=(170, 200, 230, 255), w=6)
            E(d, x - r * 0.35, y - r * 0.38, r * 0.2, r * 0.15, (215, 240, 255, 255), w=0)
    if costume == "towel":  # snug in a soft aqua towel wrapped like a cape, after the bath
        TW, TL = (130, 210, 215, 255), (170, 228, 230, 255)
        cape = [(300, 640), (600, 640), (700, 760), (720, 960), (180, 960), (200, 760)]
        d = _suit(im, ("poly", cape), TW, stripes=[(880, 902, (255, 255, 255, 255)), (912, 922, (255, 255, 255, 255))])
        d.polygon([(450, 650), (520, 650), (470, 960), (440, 960)], fill=TL)
        d.line([(450, 650), (450, 960)], fill=OUT, width=6)
        d.rounded_rectangle([280, 615, 620, 672], 26, fill=TL, outline=OUT, width=7)   # rolled collar
        for x in (190, 710):
            d.arc([x - 40, 920, x + 40, 990], 200, 340, fill=OUT, width=6)
        _drops(d, [(250, 210, 22), (650, 215, 22)])
    if costume in ("cosy", "elbow"):  # chilly-day outfit (ep023): blue striped scarf + yellow mittens
        BLUE, BL2 = (95, 155, 235, 255), (150, 195, 250, 255)
        d.polygon([(372, 640), (452, 640), (440, 860), (360, 860)], fill=BLUE, outline=OUT, width=7)
        for yy in (700, 770):
            d.line([(368, yy), (446, yy)], fill=(255, 255, 255, 255), width=12)
        for k in range(4):
            d.line([(370 + k * 22, 860), (366 + k * 22, 900)], fill=BLUE, width=10)
        d.rounded_rectangle([270, 585, 630, 680], 44, fill=BLUE, outline=OUT, width=8)
        for xx in (340, 450, 560):
            d.line([(xx, 592), (xx, 673)], fill=BL2, width=16)
        if costume == "cosy":
            for side in (-1, 1):
                E(d, 450 + side * 128, 892, 58, 66, (255, 210, 70, 255))
                E(d, 450 + side * 128 + side * 50, 868, 22, 30, (255, 210, 70, 255), w=6)
                d.rounded_rectangle([450 + side * 128 - 56, 830, 450 + side * 128 + 56, 856], 12, fill=(255, 255, 255, 255), outline=OUT, width=5)
    if costume in ("cosy", "elbow"):  # red knit hat with a fluffy pompom
        RED, RL = (236, 78, 82, 255), (250, 130, 130, 255)
        d.chord([238, 70, 662, 440], 180, 360, fill=RED, outline=OUT, width=8)
        for xx in (320, 385, 450, 515, 580):
            d.line([(xx, 110 + abs(xx - 450) * 0.35), (xx, 250)], fill=RL, width=10)
        d.rounded_rectangle([220, 222, 680, 292], 30, fill=(255, 245, 240, 255), outline=OUT, width=8)
        for xx in range(250, 660, 34):
            d.line([(xx, 232), (xx, 282)], fill=(240, 215, 215, 255), width=6)
        E(d, 450, 72, 62, 58, (255, 255, 255, 255), w=7)
        E(d, 432, 56, 18, 14, (235, 240, 250, 255), w=0)
    if costume == "elbow":  # sneezing INTO his elbow: arm (with yellow mitten) across the muzzle
        arm = Image.new("RGBA", (900, 1000), (0, 0, 0, 0))
        ad = ImageDraw.Draw(arm)
        E(ad, 620, 700, 62, 120, FUR)                              # upper arm from the shoulder
        E(ad, 470, 548, 205, 64, FUR)                              # forearm across the muzzle
        E(ad, 600, 600, 70, 70, FUR, w=0)                          # the elbow bend
        E(ad, 268, 520, 66, 58, (255, 210, 70, 255))               # mitten at the far side
        ad.rounded_rectangle([318, 488, 352, 556], 10, fill=(255, 255, 255, 255), outline=OUT, width=5)
        im.alpha_composite(arm)
        d = ImageDraw.Draw(im)
        for (x, y, r) in ((700, 470, 16), (735, 520, 12), (690, 560, 10)):   # little sneeze puffs
            E(d, x, y, r, r, (255, 255, 255, 230), ol=(200, 215, 235, 255), w=4)
    if costume == "bighat":  # Mama's big purple hat, slipped down over Pip's eyes (funny moment)
        PUR, PL = (170, 120, 215, 255), (200, 160, 240, 255)
        d.chord([150, 30, 750, 900], 180, 360, fill=PUR, outline=OUT, width=9)
        d.rounded_rectangle([110, 380, 790, 470], 40, fill=PL, outline=OUT, width=9)
        for (x, y) in ((300, 300), (420, 210), (560, 280)):
            for a in range(5):
                ang = a * 2 * math.pi / 5
                E(d, x + 26 * math.cos(ang), y + 26 * math.sin(ang), 20, 20, (255, 200, 220, 255), w=4)
            E(d, x, y, 14, 14, (255, 225, 110, 255), w=4)
        E(d, 450, 46, 46, 40, (255, 255, 255, 255), w=7)
    if costume == "soapy":  # washing paws: soap foam on both paws + a few bubbles
        for side in (-1, 1):
            for (dx, dy, r) in ((0, 0, 58), (-40, -30, 40), (40, -36, 42), (-20, 45, 38), (35, 40, 36), (0, -70, 30)):
                E(d, 450 + side * 128 + dx, 880 + dy, r, r * 0.92, (255, 255, 255, 255), ol=(170, 200, 230, 255), w=5)
        for (x, y, r) in ((200, 760, 26), (720, 740, 22), (170, 660, 16), (760, 650, 18)):
            E(d, x, y, r, r, (235, 248, 255, 200), ol=(170, 200, 230, 255), w=4)
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


def pillow(eyes="open", m=0, h=150, col=(255, 150, 180)):
    """A soft square cushion with corner tufts and a button (prop)."""
    W, H = 460, 380
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark = tuple(max(0, int(c * 0.82)) for c in col)
    for (x, y) in ((40, 40), (420, 40), (40, 340), (420, 340)):
        E(d, x, y, 34, 34, col + (255,), w=7)
    d.rounded_rectangle([30, 30, 430, 350], 90, fill=col + (255,), outline=OUT, width=9)
    d.rounded_rectangle([80, 75, 380, 305], 70, outline=dark + (255,), width=6)
    E(d, 230, 190, 20, 20, dark + (255,), w=5)
    E(d, 150, 110, 40, 18, (255, 255, 255, 110), w=0)
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


def snail(eyes="open", m=0, h=150):
    """Tiny friendly snail: pastel swirl shell, two eye stalks, little smile (prop, slow)."""
    W, H = 760, 560
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    BODY, SH, SH2 = (200, 230, 150, 255), (255, 185, 140, 255), (245, 140, 120, 255)
    d.rounded_rectangle([60, 400, 700, 520], 60, fill=BODY, outline=OUT, width=8)
    for side in (0, 1):  # eye stalks
        sx = 560 + side * 90
        d.line([sx, 410, sx + 20 * (side * 2 - 1) + 10, 150], fill=OUT, width=26)
        d.line([sx, 410, sx + 20 * (side * 2 - 1) + 10, 150], fill=BODY, width=14)
        E(d, sx + 20 * (side * 2 - 1) + 10, 140, 52, 52, (255, 255, 255, 255))
        eye(d, sx + 20 * (side * 2 - 1) + 10, 145, 28, eyes)
    E(d, 300, 290, 210, 200, SH, w=9)
    pts = []
    for k in range(120):
        a = k / 120 * math.pi * 4.2
        r = 175 * (1 - k / 135)
        pts.append((300 + r * math.cos(a), 300 + r * math.sin(a)))
    d.line(pts, fill=SH2, width=22, joint="curve")
    E(d, 220, 190, 40, 24, (255, 235, 220, 200), w=0)
    cheeks(im, [(660, 470)], 26, 16)
    d = ImageDraw.Draw(im)
    if m == 0:
        d.arc([580, 430, 680, 495], 20, 160, fill=OUT, width=8)
    else:
        d.chord([590, 445, 680, 470 + 14 * m], 0, 180, fill=(150, 50, 70, 255), outline=OUT, width=6)
    return finish(im, (int(h * W / H), h))


def basket(eyes="open", m=0, h=150):
    """Wicker picnic basket with a red-checked cloth and a handle (prop)."""
    W, H = 560, 460
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc([110, 20, 450, 330], 180, 360, fill=OUT, width=34)
    d.arc([110, 20, 450, 330], 180, 360, fill=(205, 150, 90, 255), width=20)
    d.polygon([(40, 180), (520, 180), (470, 440), (90, 440)], fill=(225, 170, 105, 255))
    for k in range(1, 5):
        y = 180 + k * 52
        d.line([(40 + k * 10, y), (520 - k * 10, y)], fill=(190, 130, 75, 255), width=6)
    d.line([(40, 180), (520, 180), (470, 440), (90, 440), (40, 180)], fill=OUT, width=9, joint="curve")
    for i in range(6):  # checked cloth peeking out
        c = (240, 90, 100, 255) if i % 2 == 0 else (255, 255, 255, 255)
        d.polygon([(70 + i * 70, 180), (140 + i * 70, 180), (130 + i * 70, 140), (80 + i * 70, 140)], fill=c, outline=OUT)
    E(d, 380, 135, 40, 38, (230, 60, 70, 255), w=6)  # apple
    d.line([380, 98, 388, 78], fill=(110, 78, 60, 255), width=7)
    return finish(im, (int(h * W / H), h))


def bell(eyes="open", m=0, h=150):
    """Mimi's little golden collar bell with a pink bow (prop, no voice)."""
    W, H = 420, 440
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for s in (-1, 1):  # pink bow on top
        d.polygon([(210, 70), (210 + s * 120, 15), (210 + s * 120, 125)], fill=(255, 120, 170, 255), outline=OUT, width=7)
    E(d, 210, 70, 30, 28, (255, 150, 190, 255), w=6)
    E(d, 210, 270, 165, 155, (255, 210, 70, 255), w=8)          # round bell
    d.arc([70, 140, 350, 400], 200, 250, fill=(255, 245, 190, 255), width=18)  # shine
    d.line([60, 285, 360, 285], fill=(220, 160, 40, 255), width=10)
    d.ellipse([175, 320, 245, 380], fill=OUT)                    # slot
    d.rectangle([200, 260, 220, 330], fill=OUT)
    E(d, 120, 230, 18, 18, (255, 255, 240, 255), w=0)            # sparkle dot
    return finish(im, (int(h * W / H), h))




def slide(d, W, H, x, ground, s):
    """Little playground slide: ladder on the right, platform, wavy yellow chute down to the left.
    Platform top (where a friend can stand) is at y = ground - 0.26*s (fraction of H), centre x."""
    top = H * (ground - 0.26 * s)
    pw = H * 0.075 * s
    leg = (120, 170, 235)
    for lx in (x - pw, x + pw):  # posts
        d.rectangle([lx - 8 * s, top, lx + 8 * s, H * ground], fill=leg)
    for k in range(1, 6):  # ladder rungs
        yy = top + k * (H * ground - top) / 6
        d.line([x - pw, yy, x + pw, yy], fill=(250, 250, 255), width=int(9 * s) + 2)
    d.rounded_rectangle([x - pw - 14 * s, top - 14 * s, x + pw + 14 * s, top + 10 * s], 8, fill=(240, 120, 130))
    for lx in (x - pw - 6 * s, x + pw + 6 * s):  # little rails
        d.line([lx, top - 70 * s, lx, top], fill=(240, 120, 130), width=int(10 * s) + 2)
    d.line([x - pw - 6 * s, top - 70 * s, x + pw + 6 * s, top - 70 * s], fill=(240, 120, 130), width=int(10 * s) + 2)
    sx0, sx1 = x - pw, x - pw - H * 0.3 * s
    pts_top, pts_bot = [], []
    for t in np.linspace(0, 1, 30):
        xx = sx0 + (sx1 - sx0) * t
        yy = top + (H * ground - 10 - top) * (t * t * (3 - 2 * t))
        pts_top.append((xx, yy - 16 * s)); pts_bot.append((xx, yy + 16 * s))
    d.polygon(pts_top + pts_bot[::-1], fill=(255, 210, 80))
    d.line(pts_top, fill=(240, 170, 50), width=int(8 * s) + 2)


LEAF_COLS = {"red": ((235, 80, 70, 255), (190, 50, 50, 255)), "orange": ((255, 150, 50, 255), (220, 110, 30, 255)),
             "yellow": ((255, 210, 70, 255), (220, 170, 40, 255)), "brown": ((185, 120, 75, 255), (140, 85, 50, 255))}


def _leaf_pts(cx, cy, L, wdt, rot):
    """Maple-ish rounded leaf outline (5 soft lobes) centred at cx, cy, length L, rotated rot rad."""
    pts = []
    for k in range(80):
        a = k / 80 * 2 * math.pi
        r = 1 + 0.22 * math.cos(5 * a) ** 2 * (1 if math.sin(a) < 0.6 else 0.3)
        px, py = math.cos(a) * wdt * r, math.sin(a) * L * 0.5 * r
        pts.append((cx + px * math.cos(rot) - py * math.sin(rot), cy + px * math.sin(rot) + py * math.cos(rot)))
    return pts


def _leaf(d, cx, cy, L, col, rot=0.0, ol=True):
    fill, vein = LEAF_COLS[col]
    d.polygon(_leaf_pts(cx, cy, L, L * 0.42, rot), fill=fill, outline=OUT if ol else None, width=max(2, int(L / 30)) if ol else 1)
    ex, ey = math.sin(-rot) * L * 0.5, math.cos(rot) * L * 0.5
    d.line([cx - ex * 0.8, cy - ey * 0.8, cx + ex * 1.15, cy + ey * 1.15], fill=vein, width=max(2, int(L / 22)))


def leaf(eyes="open", m=0, h=150, col="red"):
    """One big autumn leaf (prop, no voice) in red / orange / yellow / brown."""
    W, H = 420, 520
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([210, 430, 225, 505], fill=OUT, width=16)
    d.line([210, 430, 225, 505], fill=LEAF_COLS[col][1], width=8)
    _leaf(d, 210, 240, 380, col, 0.0)
    E(d, 150, 170, 26, 16, (255, 255, 255, 120), w=0)  # soft shine
    return finish(im, (int(h * W / H), h))


def leafpile(eyes="open", m=0, h=150):
    """Big soft mound of colourful autumn leaves. Draw it AFTER a character in the cast list to put
    that friend IN the pile (only the head peeks out)."""
    W, H = 1100, 560
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([20, 60, 1080, 1060], 180, 360, fill=(230, 140, 60, 255), outline=OUT, width=9)
    d.rectangle([28, 545, 1072, 560], fill=(230, 140, 60, 255))
    rnd = random.Random(11)
    cols = ["red", "orange", "yellow", "brown", "orange", "yellow"]
    for i in range(70):
        a = rnd.uniform(math.pi * 1.04, math.pi * 1.96)
        rr = rnd.uniform(0.25, 0.97)
        cx, cy = 550 + math.cos(a) * 520 * rr, 560 + math.sin(a) * 490 * rr
        _leaf(d, cx, cy, rnd.uniform(70, 110), cols[i % 6], rnd.uniform(0, 6.28))
    return finish(im, (int(h * W / H), h))


def rake(eyes="open", m=0, h=150):
    """Grown-up's wooden leaf rake, standing up (prop). Mama does the raking."""
    W, H = 300, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([135, 20, 165, 820], 14, fill=(200, 145, 95, 255), outline=OUT, width=6)
    d.polygon([(150, 800), (20, 900), (280, 900)], fill=(120, 190, 120, 255), outline=OUT, width=6)
    for k in range(7):
        x = 30 + k * 40
        d.rounded_rectangle([x - 7, 890, x + 7, 985], 6, fill=(120, 190, 120, 255), outline=OUT, width=4)
    return finish(im, (int(h * W / H), h))



TB_COLS = {"lavender": ((190, 155, 245), "cloud"), "pink": ((255, 140, 180), "heart"),
           "blue": ((100, 170, 245), "star"), "yellow": ((255, 205, 70), "dot")}


def toothbrush(eyes="open", m=0, h=150, col="lavender", paste=False):
    """A child's toothbrush standing up: coloured handle with a little sticker, soft white bristles.
    lavender+cloud = Lulu, pink+heart = Honey, blue+star = Pip, yellow+dot = Dotty."""
    W, H = 200, 620
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, deco = TB_COLS[col]
    dark = tuple(int(v * 0.8) for v in c)
    if paste:  # a tiny pea-sized dab of toothpaste
        E(d, 100, 40, 34, 28, (235, 250, 248, 255), w=6)
        E(d, 100, 34, 20, 9, (150, 225, 210, 255), w=0)
    # bristles: one soft tuft block with bumpy top and blue stripes
    d.rounded_rectangle([36, 78, 164, 172], 16, fill=(255, 255, 255, 255), outline=OUT, width=6)
    for i in range(5):
        E(d, 49 + i * 25.5, 80, 15, 13, (255, 255, 255, 255), w=0)
    d.arc([34, 64, 166, 100], 180, 360, fill=None, width=0)
    for x in (68, 100, 132):
        d.line([x, 92, x, 160], fill=(170, 220, 245, 255), width=9)
    d.rounded_rectangle([34, 160, 166, 230], 26, fill=c + (255,), outline=OUT, width=8)       # head
    d.rounded_rectangle([70, 215, 130, 600], 30, fill=c + (255,), outline=OUT, width=8)       # handle
    d.rounded_rectangle([82, 470, 118, 585], 18, fill=dark + (255,))                         # grip
    cx, cy = 100, 340
    if deco == "cloud":
        for dx, dy, r in ((-16, 6, 18), (0, -8, 22), (17, 6, 18)):
            E(d, cx + dx, cy + dy, r, r, (255, 255, 255, 255), w=0)
    elif deco == "heart":
        E(d, cx - 11, cy - 6, 15, 15, (255, 255, 255, 255), w=0); E(d, cx + 11, cy - 6, 15, 15, (255, 255, 255, 255), w=0)
        d.polygon([(cx - 25, cy - 1), (cx + 25, cy - 1), (cx, cy + 26)], fill=(255, 255, 255, 255))
    elif deco == "star":
        d.polygon(star_pts(cx, cy, 26), fill=(255, 235, 120, 255))
    else:
        E(d, cx, cy, 16, 16, (255, 255, 255, 255), w=0)
    d.line([88, 250, 88, 300], fill=(255, 255, 255, 150), width=6)
    return finish(im, (int(h * W / H), h))


def toothpaste(eyes="open", m=0, h=150):
    """A plain kids' toothpaste tube (no brand): white tube, mint stripe, star, round cap."""
    W, H = 480, 260
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(40, 40), (380, 70), (380, 190), (40, 220)], fill=(255, 255, 255, 255), outline=OUT, width=8)
    d.rectangle([22, 32, 52, 228], fill=(200, 235, 230, 255), outline=OUT, width=7)
    d.polygon([(120, 110), (380, 112), (380, 148), (120, 150)], fill=(140, 220, 200, 255))
    d.polygon(star_pts(215, 130, 34), fill=(255, 200, 90, 255), outline=OUT, width=4)
    d.rounded_rectangle([380, 92, 456, 168], 18, fill=(150, 210, 245, 255), outline=OUT, width=7)
    return finish(im, (int(h * W / H), h))


def _foam(im):
    """Soft white toothpaste-foam bubbles around a mouth area of a character image (in-place)."""
    d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for (x, y, r) in ((372, 548, 36), (412, 592, 30), (500, 592, 32), (538, 552, 34), (330, 512, 22),
                      (456, 612, 26), (578, 512, 22), (300, 560, 18), (612, 562, 16)):
        E(d, x, y, r, r, (255, 255, 255, 245), ol=(170, 200, 215, 255), w=4)
        E(d, x - r * 0.35, y - r * 0.35, r * 0.25, r * 0.25, (210, 240, 255, 255), w=0)


def cloudy(eyes="open", m=0, h=300, full=True):
    """Cloudy: a small, sleepy, fluffy cloud friend (ep018). full=True: tummy heavy with raindrops."""
    W, H = 1000, 800
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    WHITE = (250, 250, 255, 255) if not full else (236, 240, 252, 255)
    puffs = [(500, 430, 250), (280, 470, 160), (720, 470, 160), (370, 300, 150), (630, 300, 150),
             (500, 230, 140), (160, 560, 105), (840, 560, 105), (500, 580, 210)]
    for (x, y, r) in puffs:
        E(d, x, y, r, r * 0.92, WHITE, w=8)
    for (x, y, r) in puffs:
        E(d, x, y, r - 8, r * 0.92 - 8, WHITE, w=0)
    if full:  # soft blue-grey tummy full of raindrops
        tum = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(tum).ellipse([220, 520, 780, 760], fill=(170, 190, 230, 150))
        tum = tum.filter(ImageFilter.GaussianBlur(28))
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        for (x, y, r) in puffs:
            md.ellipse([x - r + 8, y - r * 0.92 + 8, x + r - 8, y + r * 0.92 - 8], fill=255)
        clear = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        clear.paste(tum, (0, 0), mask)
        im.alpha_composite(clear)
        d = ImageDraw.Draw(im)
        _drops(d, [(340, 660, 30), (470, 700, 27), (600, 675, 31), (720, 625, 24), (240, 600, 22)])
    else:  # light and happy: little sparkles
        for (x, y, r) in ((110, 300, 34), (900, 260, 30), (860, 120, 20), (150, 140, 22)):
            d.polygon(star_pts(x, y, r), fill=(255, 225, 110, 255), outline=OUT, width=5)
    for side in (-1, 1):
        eye(d, 500 + side * 105, 410, 40, eyes)
    cheeks(im, [(345, 485), (655, 485)], 50, 28)
    d = ImageDraw.Draw(im)
    mouth(d, 500, 480, 0.85, m)
    return finish(im, (int(h * W / H), h))


def flowerbed(eyes="open", m=0, h=150, thirsty=False):
    """Three garden flowers (red, yellow, blue) in a little soil bed; thirsty = drooping and sleepy."""
    W, H = 1200, 800
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = [((240, 80, 85, 255), (255, 150, 150, 255)), ((255, 205, 60, 255), (255, 235, 150, 255)),
            ((90, 150, 245, 255), (165, 200, 255, 255))]
    for i, (pet, light) in enumerate(cols):
        x0 = 260 + i * 340
        if thirsty:
            hx, hy = x0 + 120, 470
            pts = [(x0, 700), (x0, 560), (x0 + 15, 450), (x0 + 55, 390), (x0 + 100, 385), (hx, hy - 60)]
            for a, b in zip(pts, pts[1:]):
                d.line([a, b], fill=(90, 160, 80, 255), width=22)
                E(d, b[0], b[1], 11, 11, (90, 160, 80, 255), w=0)
            pet = tuple(int(v * 0.82) for v in pet[:3]) + (255,)
        else:
            hx, hy = x0, 250
            d.line([(x0, 700), (x0, hy)], fill=(90, 170, 80, 255), width=22)
        for side in (-1, 1):  # leaves
            lx = x0 + side * 55
            E(d, lx, 560, 60, 26, (110, 190, 95, 255), w=6)
        r = 78
        for k in range(6):
            a = k * math.pi / 3
            E(d, hx + math.cos(a) * r, hy + math.sin(a) * r, 58, 58, pet, w=6)
        E(d, hx, hy, 70, 70, (255, 240, 200, 255), w=6)
        ey = "closed" if thirsty else eyes
        for side in (-1, 1):
            eye(d, hx + side * 26, hy - 6, 13, ey)
        if thirsty:
            d.arc([hx - 20, hy + 22, hx + 20, hy + 40], 200, 340, fill=OUT, width=6)
        else:
            d.arc([hx - 22, hy + 6, hx + 22, hy + 36], 20, 160, fill=OUT, width=7)
    # soil bed
    d.rounded_rectangle([90, 660, 1110, 790], 60, fill=(150, 100, 70, 255), outline=OUT, width=7)
    for k in range(9):
        E(d, 160 + k * 110, 715, 16, 9, (120, 80, 55, 255), w=0)
    return finish(im, (int(h * W / H), h))


def on_swing(eyes="open", m=0, h=520, who=None, kw=None):
    """A friend sitting on a swing: two ropes from the top edge (the pivot on the beam) down to a wooden seat.
    The sprite's top-centre is the pivot, so render.py can rock it like a pendulum ("swing": degrees)."""
    W, H = 600, 1000
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    seat_y = 930
    ROPE = (150, 115, 100, 255)
    for rx in (95, 505):
        d.line([(rx, 0), (rx, seat_y)], fill=OUT, width=16)
        d.line([(rx, 0), (rx, seat_y)], fill=ROPE, width=9)
    if who:
        fn, ckw, frac = who
        ch = fn(eyes=eyes, m=m, h=int(H * frac), **(kw or ckw))
        im.alpha_composite(ch, (int(W / 2 - ch.width / 2), int(seat_y + 25 - ch.height)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, seat_y - 18, 540, seat_y + 30], 16, fill=(120, 190, 240, 255), outline=OUT, width=8)
    d.line([(80, seat_y - 2), (520, seat_y - 2)], fill=(175, 220, 250, 255), width=6)
    return finish(im, (int(h * W / H), h))


# ---------------------------------------------------------------- ep020: where animals sleep
def birdie(eyes="open", m=0, h=150, col=(120, 180, 245), belly=(255, 240, 215)):
    """Little round baby bird (no voice; sfx tweet). Colours: blue / pink / yellow."""
    W, H = 600, 560
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark = tuple(max(0, int(v * 0.8)) for v in col)
    # tail + feet
    d.polygon([(110, 330), (20, 260), (40, 360)], fill=dark + (255,), outline=OUT, width=7)
    for fx in (250, 350):
        d.line([fx, 480, fx, 540], fill=(245, 160, 60, 255), width=12)
        d.line([fx - 25, 545, fx + 25, 545], fill=(245, 160, 60, 255), width=12)
    E(d, 300, 300, 215, 200, col + (255,))
    E(d, 310, 360, 130, 115, belly + (255,), w=0)
    # head tuft
    for k, (dx, a) in enumerate(((-18, -0.4), (0, 0), (18, 0.4))):
        x0, y0 = 300 + dx, 112
        d.line([x0, y0, x0 + math.sin(a) * 50, y0 - 60], fill=col + (255,), width=16)
    # wing
    E(d, 140, 330, 70, 105, dark + (255,))
    for side in (-1, 1):
        eye(d, 300 + side * 75, 235, 34, eyes)
    cheeks(im, [(195, 300), (405, 300)], 34, 20)
    d = ImageDraw.Draw(im)
    op = 14 * m
    d.polygon([(268, 280), (332, 280), (300, 335 + op)], fill=(250, 170, 60, 255), outline=OUT, width=6)
    if m:
        d.line([272, 292, 328, 292], fill=OUT, width=5)
    return finish(im, (int(h * W / H), h))


def nest(eyes="open", m=0, h=150):
    """Cosy woven twig nest (front half). List it AFTER the birds in the cast so they sit IN it."""
    W, H = 900, 380
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([20, -260, 880, 370], 0, 180, fill=(170, 120, 75, 255), outline=OUT, width=9)
    d.rectangle([28, 50, 872, 58], fill=(170, 120, 75, 255))
    rnd = random.Random(5)
    for i in range(46):  # woven twigs
        y = rnd.uniform(70, 330)
        half = math.sqrt(max(0.0, 1 - ((y - 55) / 315) ** 2)) * 420
        x0 = 450 + rnd.uniform(-half, half * 0.3)
        L = rnd.uniform(90, 220)
        a = rnd.uniform(-0.35, 0.35)
        x1 = min(450 + half, x0 + L * math.cos(a))
        d.line([x0, y, x1, y + L * math.sin(a)], fill=rnd.choice([(130, 88, 55, 255), (200, 150, 95, 255), (150, 105, 65, 255)]), width=10)
    d.rounded_rectangle([10, 22, 890, 78], 28, fill=(190, 138, 88, 255), outline=OUT, width=8)  # rim
    for x in range(60, 860, 70):
        d.arc([x - 40, 26, x + 40, 74], 200, 340, fill=(140, 95, 60, 255), width=7)
    return finish(im, (int(h * W / H), h))


def burrow_front(eyes="open", m=0, h=150):
    """Grassy earth lip at the burrow door. List it AFTER the bunny so only the head peeks out."""
    W, H = 900, 300
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([0, 40, 900, 560], 180, 360, fill=(150, 108, 78, 255), outline=OUT, width=8)
    d.rectangle([8, 296, 892, 300], fill=(150, 108, 78, 255))
    d.chord([40, 70, 860, 520], 180, 360, fill=(120, 196, 100, 255))
    rnd = random.Random(9)
    for i in range(40):  # grass blades on top of the lip
        x = rnd.uniform(60, 840)
        top = 300 - math.sqrt(max(0.0, 1 - ((x - 450) / 410) ** 2)) * 225
        d.polygon([(x - 14, top + 30), (x + rnd.uniform(-20, 20), top - rnd.uniform(20, 55)), (x + 14, top + 30)], fill=(95, 175, 85, 255))
    for x, c in ((180, (255, 240, 120)), (700, (255, 180, 210)), (520, (255, 255, 255))):  # tiny flowers
        y = 300 - math.sqrt(max(0.0, 1 - ((x - 450) / 410) ** 2)) * 200
        for k in range(5):
            a = k * 1.2566
            E(d, x + math.cos(a) * 16, y + math.sin(a) * 16, 13, 13, c + (255,), w=0)
        E(d, x, y, 10, 10, (255, 190, 70, 255), w=0)
    return finish(im, (int(h * W / H), h))


def hole_rim(eyes="open", m=0, h=150):
    """Lower part of Ollie's tree hole in trunk colour (owl_tree trunk). List it AFTER Ollie so he peeks out."""
    W, H = 700, 260
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([-30, -300, 730, 258], 0, 180, fill=(120, 84, 66, 255))
    mask = Image.new("L", (W, H), 255)
    ImageDraw.Draw(mask).ellipse([30, -230, 670, 110], fill=0)
    im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel("A")), np.array(mask))))
    d = ImageDraw.Draw(im)
    d.arc([30, -230, 670, 110], 8, 172, fill=(95, 62, 46, 255), width=26)
    return finish(im, (int(h * W / H), h))


def pet_bed(eyes="open", m=0, h=150):
    """Pip's cosy round sleepover basket bed with a blue star blanket (front rim). List it AFTER Pip."""
    W, H = 1000, 420
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([0, -120, 1000, 420], 0, 180, fill=(205, 150, 95, 255), outline=OUT, width=9)
    for k in range(1, 5):
        y = 150 + k * 50
        d.arc([30 + k * 30, -120 + k * 18, 970 - k * 30, 420 - k * 6], 20, 160, fill=(175, 122, 75, 255), width=7)
    # blanket draped over the front
    d.chord([120, -60, 880, 330], 0, 180, fill=(120, 170, 240, 255), outline=OUT, width=7)
    for x, y in ((250, 170), (420, 230), (600, 220), (760, 160), (500, 120)):
        d.polygon(star_pts(x, y, 30, 13), fill=(255, 230, 120, 255))
    d.rounded_rectangle([0, 120, 1000, 190], 34, fill=(225, 172, 112, 255), outline=OUT, width=8)  # rim
    return finish(im, (int(h * W / H), h))

def tub(eyes="open", m=0, h=150):
    """Front of a white claw-foot bathtub topped with a big soft mound of bubbles. List it AFTER the friend in the bath."""
    W, H = 1500, 760
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (230, 1270):  # little golden feet
        d.rounded_rectangle([x - 55, 640, x + 55, 750], 30, fill=(240, 195, 90, 255), outline=OUT, width=8)
    d.rounded_rectangle([60, 250, 1440, 700], 200, fill=(255, 255, 255, 255), outline=OUT, width=10)
    d.rounded_rectangle([40, 225, 1460, 300], 38, fill=(245, 248, 252, 255), outline=OUT, width=9)
    d.arc([180, 330, 1320, 660], 20, 160, fill=(215, 230, 240, 255), width=14)
    for x, c in ((360, (255, 170, 195, 255)), (750, (130, 200, 245, 255)), (1140, (255, 210, 90, 255))):
        d.polygon(star_pts(x, 470, 34, 15), fill=c)
    rnd = random.Random(5)
    for k in range(26):  # bubble foam along the rim
        x = 70 + k * 53 + rnd.uniform(-10, 10)
        r = rnd.uniform(48, 82)
        y = 222 - rnd.uniform(0, 60)
        E(d, x, y, r, r * 0.9, (255, 255, 255, 255), ol=(175, 205, 232, 255), w=6)
        E(d, x - r * 0.3, y - r * 0.35, r * 0.2, r * 0.14, (210, 238, 255, 255), w=0)
    return finish(im, (int(h * W / H), h))


def bigbubble(eyes="open", m=0, h=150):
    """One big shiny soap bubble (prop) with a rainbow sheen, for counting and popping."""
    S = 400
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([20, 20, 380, 380], fill=(200, 230, 255, 70), outline=(140, 190, 240, 255), width=10)
    d.arc([45, 45, 355, 355], 200, 260, fill=(255, 170, 210, 230), width=14)
    d.arc([45, 45, 355, 355], 20, 80, fill=(170, 230, 190, 220), width=12)
    d.arc([60, 60, 340, 340], 100, 150, fill=(255, 230, 140, 220), width=10)
    E(d, 125, 120, 46, 30, (255, 255, 255, 240), w=0)
    E(d, 95, 170, 14, 14, (255, 255, 255, 230), w=0)
    return finish(im, (h, h))


def duck_toy(eyes="open", m=0, h=150):
    """Little yellow rubber bath duck toy (plain, no brand)."""
    W, H = 500, 420
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    Y = (255, 215, 70, 255)
    E(d, 240, 300, 210, 110, Y)
    d.polygon([(400, 230), (480, 175), (450, 290)], fill=Y, outline=OUT, width=7)
    E(d, 170, 150, 115, 110, Y)
    d.polygon([(55, 150), (5, 175), (60, 195)], fill=(255, 140, 60, 255), outline=OUT, width=6)
    E(d, 140, 125, 17, 20, (45, 32, 40, 255), w=0)
    E(d, 146, 118, 6, 6, (255, 255, 255, 255), w=0)
    d.arc([180, 250, 360, 360], 200, 330, fill=(235, 180, 40, 255), width=10)
    return finish(im, (int(h * W / H), h))


def boat_toy(eyes="open", m=0, h=150):
    """Little blue toy boat with a white sail and a red flag."""
    W, H = 500, 460
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([250, 60, 250, 330], fill=(150, 105, 70, 255), width=14)
    d.polygon([(262, 80), (262, 300), (430, 300)], fill=(255, 255, 255, 255), outline=OUT, width=7)
    d.polygon([(238, 110), (238, 300), (100, 300)], fill=(240, 245, 255, 255), outline=OUT, width=7)
    d.polygon([(250, 60), (320, 80), (250, 100)], fill=(240, 80, 80, 255), outline=OUT, width=5)
    d.polygon([(20, 320), (480, 320), (410, 440), (90, 440)], fill=(90, 160, 240, 255), outline=OUT, width=8)
    for x in (170, 250, 330):
        E(d, x, 375, 16, 16, (255, 255, 255, 255), w=0)
    return finish(im, (int(h * W / H), h))


def cup_toy(eyes="open", m=0, h=150):
    """Red plastic bath cup for pouring water (prop)."""
    W, H = 380, 420
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc([230, 120, 370, 300], 270, 90, fill=OUT, width=36)
    d.arc([230, 120, 370, 300], 270, 90, fill=(240, 80, 80, 255), width=22)
    d.polygon([(20, 60), (300, 60), (260, 400), (60, 400)], fill=(240, 80, 80, 255), outline=OUT, width=8)
    d.ellipse([20, 35, 300, 85], fill=(200, 55, 60, 255), outline=OUT, width=7)
    d.line([80, 130, 95, 340], fill=(255, 170, 170, 255), width=14)
    return finish(im, (int(h * W / H), h))


def night_light(eyes="open", m=0, h=150, on=True):
    """Pip's little star night light (ep022): a smiley star on a round wooden base. on=False = pale and sleepy (switched off)."""
    W, H = 520, 600
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if on:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([90, 70, 430, 420], fill=(255, 230, 140, 150))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(28)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([150, 470, 370, 590], 40, fill=(205, 150, 100, 255), outline=OUT, width=8)
    d.rounded_rectangle([230, 420, 290, 480], 14, fill=(225, 172, 112, 255), outline=OUT, width=7)
    star = (255, 222, 95, 255) if on else (226, 220, 236, 255)
    d.polygon(star_pts(260, 250, 210, 105, rot=-math.pi / 2), fill=star, outline=OUT, width=9)
    if on:
        d.polygon(star_pts(260, 250, 150, 76), fill=(255, 240, 160, 255))
    for side in (-1, 1):
        if on:
            eye(d, 260 + side * 45, 245, 18, "open")
        else:
            d.arc([260 + side * 45 - 20, 232, 260 + side * 45 + 20, 262], 20, 160, fill=OUT, width=7)
    cheeks(im, [(195, 285), (325, 285)], 22, 13)
    d = ImageDraw.Draw(im)
    d.arc([235, 270, 285, 305], 20, 160, fill=OUT, width=7)
    return finish(im, (int(h * W / H), h))


def shadow(eyes="open", m=0, h=150, who="bunny"):
    """A soft, friendly wall shadow (ep022 shadow game): the silhouette of Honey (long ears) or Pip (floppy ears)."""
    src = bunny(h=1000) if who == "bunny" else puppy(h=1000)
    a = src.getchannel("A").point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.GaussianBlur(10))
    im = Image.new("RGBA", src.size, (82, 70, 150, 255))
    im.putalpha(a.point(lambda v: int(v * 0.55)))
    return finish(im, (int(h * src.width / src.height), h))


def star_friend(eyes="open", m=0, h=150, col=(255, 222, 95)):
    """A little twinkly star friend with a sleepy smile (prop for counting stars, no voice)."""
    S = 500
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([90, 90, 410, 410], fill=col + (110,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(25)))
    d = ImageDraw.Draw(im)
    d.polygon(star_pts(250, 265, 200, 100), fill=col + (255,), outline=OUT, width=9)
    for side in (-1, 1):
        eye(d, 250 + side * 45, 260, 17, eyes)
    cheeks(im, [(185, 300), (315, 300)], 22, 13)
    d = ImageDraw.Draw(im)
    d.arc([225, 285, 275, 320], 20, 160, fill=OUT, width=7)
    return finish(im, (h, h))


def firefly(eyes="open", m=0, h=150):
    """Tiny friendly firefly: round lavender body, see-through wings, and a glowing yellow-green tail light."""
    W, H = 520, 460
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([260, 210, 460, 410], fill=(230, 255, 140, 170))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    for (cx, cy, rot) in ((210, 140, -25), (300, 130, 25)):
        wing = Image.new("RGBA", (220, 160), (0, 0, 0, 0))
        ImageDraw.Draw(wing).ellipse([5, 5, 215, 155], fill=(235, 245, 255, 170), outline=(150, 170, 210, 255), width=6)
        wing = wing.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(wing, (int(cx - wing.width / 2), int(cy - wing.height / 2)))
    d = ImageDraw.Draw(im)
    E(d, 360, 310, 95, 85, (235, 255, 150, 255), ol=(170, 190, 80, 255))
    E(d, 360, 310, 60, 52, (255, 255, 210, 255), w=0)
    E(d, 240, 270, 105, 95, (160, 140, 220, 255))
    E(d, 150, 230, 85, 80, (175, 155, 230, 255))
    for side in (-1, 1):
        d.line([150 + side * 25, 160, 150 + side * 55, 80], fill=OUT, width=7)
        E(d, 150 + side * 55, 75, 14, 14, (255, 225, 120, 255), w=5)
    for side in (-1, 1):
        eye(d, 150 + side * 30, 225, 15, eyes)
    cheeks(im, [(105, 260), (195, 260)], 17, 10)
    d = ImageDraw.Draw(im)
    d.arc([130, 250, 170, 280], 20, 160, fill=OUT, width=6)
    return finish(im, (int(h * W / H), h))


def pup_sneeze(eyes="open", m=0, h=400):
    """Pip sneezing into his elbow (ep023): eyes squeezed shut, arm across his muzzle."""
    return puppy(eyes="closed", m=m, h=h, costume="elbow")


def knit_hat(eyes="open", m=0, h=150):
    """Pip's red knit hat with a white ribbed brim and a fluffy pompom (prop)."""
    W, H = 520, 460
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.chord([40, 90, 480, 640], 180, 360, fill=(236, 78, 82, 255), outline=OUT, width=9)
    for xx in (130, 195, 260, 325, 390):
        d.line([(xx, 140 + abs(xx - 260) * 0.4), (xx, 350)], fill=(250, 130, 130, 255), width=12)
    d.rounded_rectangle([25, 330, 495, 440], 40, fill=(255, 245, 240, 255), outline=OUT, width=9)
    for xx in range(60, 470, 36):
        d.line([(xx, 345), (xx, 425)], fill=(240, 215, 215, 255), width=7)
    E(d, 260, 82, 74, 68, (255, 255, 255, 255), w=8)
    E(d, 238, 62, 22, 16, (235, 240, 250, 255), w=0)
    return finish(im, (int(h * W / H), h))


def scarf(eyes="open", m=0, h=150):
    """A long blue striped scarf hanging over a peg-shape (prop), with fringe at both ends."""
    W, H = 520, 700
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    BLUE = (95, 155, 235, 255)
    d.arc([100, 30, 420, 330], 180, 360, fill=OUT, width=110)
    d.arc([108, 38, 412, 322], 180, 360, fill=BLUE, width=94)
    for (x0, x1) in ((100, 210), (310, 420)):
        d.rounded_rectangle([x0, 170, x1, 620], 20, fill=BLUE, outline=OUT, width=8)
        for yy in (300, 420, 540):
            d.rectangle([x0 + 6, yy, x1 - 6, yy + 28], fill=(255, 255, 255, 255))
        for k in range(5):
            xx = x0 + 14 + k * (x1 - x0 - 28) / 4
            d.line([(xx, 618), (xx, 680)], fill=BLUE, width=12)
    return finish(im, (int(h * W / H), h))


def mittens(eyes="open", m=0, h=150):
    """A pair of yellow mittens with white cuffs and a little heart (prop for counting: one, two)."""
    W, H = 640, 460
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    Y = (255, 210, 70, 255)
    for cx, side in ((170, -1), (470, 1)):
        E(d, cx + side * -88, 200, 42, 60, Y, w=8)                  # thumb
        d.rounded_rectangle([cx - 105, 70, cx + 105, 350], 100, fill=Y, outline=OUT, width=8)
        d.rounded_rectangle([cx - 112, 320, cx + 112, 430], 26, fill=(255, 255, 255, 255), outline=OUT, width=8)
        for xx in range(cx - 90, cx + 100, 30):
            d.line([(xx, 332), (xx, 418)], fill=(230, 230, 236, 255), width=6)
        hx, hy = cx, 190
        d.polygon([(hx - 34, hy - 8), (hx, hy + 36), (hx + 34, hy - 8)], fill=(255, 120, 150, 255))
        E(d, hx - 18, hy - 12, 19, 18, (255, 120, 150, 255), w=0)
        E(d, hx + 18, hy - 12, 19, 18, (255, 120, 150, 255), w=0)
    return finish(im, (int(h * W / H), h))


def tissue_box(eyes="open", m=0, h=150):
    """A plain pastel tissue box with a soft white tissue poking out (prop, no brand)."""
    W, H = 560, 480
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 200, 520, 460], 24, fill=(170, 220, 240, 255), outline=OUT, width=9)
    for (x, y) in ((120, 300), (260, 380), (400, 290), (450, 400), (170, 410)):
        E(d, x, y, 18, 18, (255, 255, 255, 255), w=0)
    d.rounded_rectangle([170, 190, 390, 236], 20, fill=(120, 185, 215, 255), outline=OUT, width=6)
    d.polygon([(200, 215), (230, 70), (280, 20), (300, 110), (350, 40), (370, 215)], fill=(255, 255, 255, 255), outline=OUT, width=7)
    return finish(im, (int(h * W / H), h))


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
    "honey_rain": dict(fn=bunny, kw=dict(costume="raincoat"), h=0.44),
    "dotty_beads": dict(fn=duckling, kw=dict(beads=True), h=0.28),
    "pip_drip": dict(fn=puppy, kw=dict(costume="drippy"), h=0.40),
    "cricket": dict(fn=cricket, kw=dict(), h=0.12),
    "frog": dict(fn=frog, kw=dict(), h=0.16),
    "ball": dict(fn=ball, kw=dict(), h=0.15),
    "block": dict(fn=block, kw=dict(), h=0.15),
    "sandwich": dict(fn=sandwich, kw=dict(), h=0.13),
    "pip_captain": dict(fn=puppy, kw=dict(costume="captain"), h=0.40),
    "pillow_pink": dict(fn=pillow, kw=dict(col=(255, 150, 185)), h=0.11),
    "pillow_blue": dict(fn=pillow, kw=dict(col=(110, 175, 245)), h=0.11),
    "pillow_yellow": dict(fn=pillow, kw=dict(col=(255, 210, 80)), h=0.11),
    "pillow_green": dict(fn=pillow, kw=dict(col=(130, 210, 120)), h=0.11),
    "snail": dict(fn=snail, kw=dict(), h=0.09),
    "basket": dict(fn=basket, kw=dict(), h=0.13),
    "bell": dict(fn=bell, kw=dict(), h=0.08),
    "mimi_nobell": dict(fn=kitten, kw=dict(bell=False), h=0.40),
    "leaf_red": dict(fn=leaf, kw=dict(col="red"), h=0.10),
    "leaf_orange": dict(fn=leaf, kw=dict(col="orange"), h=0.10),
    "leaf_yellow": dict(fn=leaf, kw=dict(col="yellow"), h=0.10),
    "leaf_brown": dict(fn=leaf, kw=dict(col="brown"), h=0.10),
    "leafpile": dict(fn=leafpile, kw=dict(), h=0.20),
    "rake": dict(fn=rake, kw=dict(), h=0.36),
    "pip_leafy": dict(fn=puppy, kw=dict(costume="leafy"), h=0.40),
    "tb_lulu": dict(fn=toothbrush, kw=dict(col="lavender"), h=0.17),
    "tb_honey": dict(fn=toothbrush, kw=dict(col="pink"), h=0.17),
    "tb_pip": dict(fn=toothbrush, kw=dict(col="blue"), h=0.17),
    "tb_dotty": dict(fn=toothbrush, kw=dict(col="yellow"), h=0.17),
    "tb_lulu_paste": dict(fn=toothbrush, kw=dict(col="lavender", paste=True), h=0.18),
    "toothpaste": dict(fn=toothpaste, kw=dict(), h=0.07),
    "lulu_foam": dict(fn=lamb, kw=dict(foam=True), h=0.40),
    "cloudy": dict(fn=cloudy, kw=dict(full=True), h=0.24),
    "cloudy_light": dict(fn=cloudy, kw=dict(full=False), h=0.24),
    "flowers_thirsty": dict(fn=flowerbed, kw=dict(thirsty=True), h=0.26),
    "flowers_happy": dict(fn=flowerbed, kw=dict(thirsty=False), h=0.26),
    "swing_empty": dict(fn=on_swing, kw=dict(), h=0.53),
    "pip_swing": dict(fn=on_swing, kw=dict(who=(puppy, dict(), 0.70)), h=0.53),
    "lulu_swing": dict(fn=on_swing, kw=dict(who=(lamb, dict(), 0.70)), h=0.53),
    "honey_swing": dict(fn=on_swing, kw=dict(who=(bunny, dict(), 0.78)), h=0.53),
    "dotty_swing": dict(fn=on_swing, kw=dict(who=(duckling, dict(), 0.50)), h=0.53),
    "pip_leafy_swing": dict(fn=on_swing, kw=dict(who=(puppy, dict(costume="leafy"), 0.70)), h=0.53),
    "birdie": dict(fn=birdie, kw=dict(), h=0.10),
    "birdie_pink": dict(fn=birdie, kw=dict(col=(250, 150, 190)), h=0.10),
    "birdie_yellow": dict(fn=birdie, kw=dict(col=(255, 210, 80)), h=0.10),
    "nest": dict(fn=nest, kw=dict(), h=0.09),
    "wildbun": dict(fn=bunny, kw=dict(fur=(196, 190, 200), inner=(250, 190, 205), bow=False), h=0.26),
    "burrow_front": dict(fn=burrow_front, kw=dict(), h=0.12),
    "hole_rim": dict(fn=hole_rim, kw=dict(), h=0.09),
    "pet_bed": dict(fn=pet_bed, kw=dict(), h=0.15),
    "pip_muddy": dict(fn=puppy, kw=dict(costume="muddy"), h=0.40),
    "pip_bubbly": dict(fn=puppy, kw=dict(costume="bubbly"), h=0.40),
    "pip_towel": dict(fn=puppy, kw=dict(costume="towel"), h=0.40),
    "tub": dict(fn=tub, kw=dict(), h=0.24),
    "bigbubble": dict(fn=bigbubble, kw=dict(), h=0.10),
    "duck_toy": dict(fn=duck_toy, kw=dict(), h=0.07),
    "boat_toy": dict(fn=boat_toy, kw=dict(), h=0.08),
    "cup_toy": dict(fn=cup_toy, kw=dict(), h=0.07),
    "pip_pj": dict(fn=puppy, kw=dict(costume="pajamas"), h=0.40),
    "nightlight": dict(fn=night_light, kw=dict(on=True), h=0.13),
    "nightlight_off": dict(fn=night_light, kw=dict(on=False), h=0.13),
    "shadow_bunny": dict(fn=shadow, kw=dict(who="bunny"), h=0.50),
    "shadow_puppy": dict(fn=shadow, kw=dict(who="puppy"), h=0.42),
    "star_friend": dict(fn=star_friend, kw=dict(), h=0.09),
    "star_pink": dict(fn=star_friend, kw=dict(col=(255, 170, 200)), h=0.09),
    "star_blue": dict(fn=star_friend, kw=dict(col=(150, 205, 255)), h=0.09),
    "firefly": dict(fn=firefly, kw=dict(), h=0.07),
    "pip_cosy": dict(fn=puppy, kw=dict(costume="cosy"), h=0.40),
    "pip_elbow": dict(fn=pup_sneeze, kw=dict(), h=0.40),
    "pip_bighat": dict(fn=puppy, kw=dict(costume="bighat"), h=0.40),
    "pip_soapy": dict(fn=puppy, kw=dict(costume="soapy"), h=0.40),
    "honey_cosy": dict(fn=bunny, kw=dict(costume="cosy"), h=0.44),
    "hat_red": dict(fn=knit_hat, kw=dict(), h=0.09),
    "scarf_blue": dict(fn=scarf, kw=dict(), h=0.15),
    "mittens_yellow": dict(fn=mittens, kw=dict(), h=0.08),
    "tissue_box": dict(fn=tissue_box, kw=dict(), h=0.08),
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
    elif kind == "rainy_garden":
        # soft, friendly rainy morning: lavender-blue sky, puffy rain clouds, cottage, tulips, puddles, duck pond
        L = W > H
        im = grad(W, H, (176, 190, 226), (222, 230, 246))
        d = ImageDraw.Draw(im)
        for (cx, cy, s_) in ((0.12, 0.10, 1.3), (0.45, 0.06, 1.5), (0.78, 0.12, 1.3), (0.30, 0.22, 0.9), (0.66, 0.26, 0.8)):
            cloud(d, W * cx - min(W, H) * 0.1, H * cy * (1 if L else 0.6), min(W, H) / 900 * s_, (238, 240, 250))
        hills(d, W, H, ground - 0.13, 0.07, (150, 205, 150), 2)
        # Honey's cottage, left (glowing window)
        hx, hw = W * (0.15 if L else 0.2), min(W, H) * (0.40 if L else 0.36)
        top = H * (ground - (0.36 if L else 0.21))
        d.rectangle([hx - hw / 2, top, hx + hw / 2, H * ground], fill=(255, 225, 190))
        d.polygon([(hx - hw * 0.62, top + 4), (hx, top - hw * 0.42), (hx + hw * 0.62, top + 4)], fill=(220, 100, 110))
        d.rounded_rectangle([hx - hw * 0.13, H * ground - (H * ground - top) * 0.55, hx + hw * 0.13, H * ground], 24, fill=(150, 100, 70))
        wx, wy, ws = hx + hw * 0.3, top + (H * ground - top) * 0.3, hw * 0.12
        d.rectangle([wx - ws, wy - ws, wx + ws, wy + ws], fill=(255, 230, 150), outline=(255, 255, 255), width=5)
        hills(d, W, H, ground - 0.02, 0.035, (125, 200, 115), 4)
        # duck pond at the back right
        px0, px1 = W * (0.62 if L else 0.5), W * (0.99 if L else 1.05)
        d.ellipse([px0, H * (ground - 0.06), px1, H * (ground + 0.02)], fill=(110, 165, 225))
        d.ellipse([px0 + W * 0.03, H * (ground - 0.05), px1 - W * 0.03, H * (ground + 0.01)], fill=(140, 190, 240))
        for k in range(3):  # reeds
            rx_ = px1 - W * 0.04 - k * W * 0.02
            d.line([rx_, H * (ground - 0.05), rx_ - 6, H * (ground - 0.14)], fill=(90, 150, 90), width=6)
            E(d, rx_ - 6, H * (ground - 0.14), 9, 22, (150, 100, 70, 255), w=0)
        # ground + tulips
        d.rectangle([0, H * ground, W, H], fill=(120, 196, 112))
        for k in range(14 if L else 8):
            tx = W * (0.03 + k * (0.94 / ((14 if L else 8) - 1)))
            ty = H * (ground + 0.01 + (k % 2) * 0.02)
            d.line([tx, ty, tx, ty - H * 0.05], fill=(80, 150, 80), width=5)
            c = [(255, 120, 150), (255, 200, 80), (200, 150, 240), (255, 160, 90)][k % 4]
            d.polygon([(tx - H * 0.016, ty - H * 0.05), (tx - H * 0.016, ty - H * 0.08), (tx - H * 0.005, ty - H * 0.065),
                       (tx, ty - H * 0.085), (tx + H * 0.005, ty - H * 0.065), (tx + H * 0.016, ty - H * 0.08), (tx + H * 0.016, ty - H * 0.05)], fill=c)
        # shiny puddles in the grass (front)
        for (cx, cw) in (((0.30, 0.13), (0.62, 0.10)) if L else ((0.28, 0.2), (0.72, 0.16))):
            cy = H * (ground + (0.07 if L else 0.05))
            d.ellipse([W * (cx - cw), cy - H * 0.025, W * (cx + cw), cy + H * 0.025], fill=(140, 180, 235))
            d.ellipse([W * (cx - cw * 0.7), cy - H * 0.012, W * (cx + cw * 0.2), cy + H * 0.006], fill=(200, 225, 250))
    elif kind == "stretch_room":
        # Honey's cosy stretch corner at dusk: lavender wall, arched window with stars, fairy lights,
        # floor lamp glow, a potted plant, and three pastel stretch mats on a soft round rug.
        land = W > H
        im = grad(W, H, (196, 170, 222), (226, 200, 226))
        d = ImageDraw.Draw(im)
        for i in range(int(60 * W * H / (1920 * 1080))):  # tiny wallpaper stars
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.08, H * (ground - 0.05))
            r = H * 0.006
            d.polygon(star_pts(x, y, r, r * 0.45), fill=(240, 226, 248))
        d.rectangle([0, H * ground, W, H], fill=(200, 150, 112))
        for k in range(1, 6):  # floor boards
            y = H * ground + (H - H * ground) * k / 6
            d.line([0, y, W, y], fill=(184, 134, 98), width=3)
        d.rectangle([0, H * ground - 10, W, H * ground + 6], fill=(240, 228, 238))  # skirting board
        # arched window
        wx, ww = W * (0.5 if land else 0.5), W * (0.16 if land else 0.27)
        wt, wb = H * (0.12 if land else 0.11), H * (0.52 if land else 0.40)
        fr = (250, 244, 236)
        d.rounded_rectangle([wx - ww - 16, wt - 16, wx + ww + 16, wb + 16], int(ww), fill=fr)
        win = grad(int(2 * ww), int(wb - wt), (30, 34, 92), (120, 86, 150))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, win.size[0] - 1, win.size[1] - 1], int(ww), fill=255)
        wd = ImageDraw.Draw(win)  # distant hills inside the window
        wh = win.size[1]
        wd.ellipse([-ww * 0.4, wh * 0.78, ww * 1.3, wh * 1.4], fill=(60, 90, 120))
        wd.ellipse([ww * 0.8, wh * 0.82, ww * 2.4, wh * 1.4], fill=(50, 105, 110))
        im.paste(win, (int(wx - ww), int(wt)), mask)
        d = ImageDraw.Draw(im)
        for _ in range(18):
            stars.append((rnd.uniform(wx - ww * 0.8, wx + ww * 0.8), rnd.uniform(wt + ww * 0.3, wb - (wb - wt) * 0.28), rnd.uniform(1.5, 3.5), rnd.uniform(0, 6.28)))
        d.rectangle([wx - ww - 30, wb + 10, wx + ww + 30, wb + 34], fill=fr)  # sill
        d.line([wx, wt, wx, wb], fill=fr, width=10)
        d.line([wx - ww, (wt + ww + wb) / 2, wx + ww, (wt + ww + wb) / 2], fill=fr, width=10)
        # curtains
        for s in (-1, 1):
            cx = wx + s * (ww + 40)
            d.polygon([(cx - 40, wt - 40), (cx + 40, wt - 40), (cx + s * 25 + 30, wb + 60), (cx + s * 25 - 30, wb + 60)], fill=(255, 196, 214))
        d.rectangle([wx - ww - 110, wt - 52, wx + ww + 110, wt - 38], fill=(190, 140, 110))
        # fairy lights (twinkle via stars list)
        for i in range(13):
            x = W * (0.02 + i * 0.08)
            y = H * 0.05 + math.sin(i * 1.1) * H * 0.012
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 100, 120))
            stars.append((x, y + 9, 6, i * 0.9))
        d.line([(W * (0.02 + i * 0.08), H * 0.05 + math.sin(i * 1.1) * H * 0.012) for i in range(13)], fill=(120, 100, 120), width=2)
        # floor lamp (right) with warm glow
        lx = W * (0.9 if land else 0.88)
        ly = H * (ground - (0.42 if land else 0.30))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - H * 0.22, ly - H * 0.18, lx + H * 0.22, ly + H * 0.26], fill=(255, 225, 150, 85))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        d = ImageDraw.Draw(im)
        d.rectangle([lx - 6, ly, lx + 6, H * ground], fill=(150, 110, 90))
        d.ellipse([lx - 45, H * ground - 14, lx + 45, H * ground + 8], fill=(150, 110, 90))
        d.polygon([(lx - 50, ly + 10), (lx + 50, ly + 10), (lx + 32, ly - H * 0.07), (lx - 32, ly - H * 0.07)], fill=(255, 236, 170), outline=OUT, width=4)
        # potted plant (left)
        px = W * (0.08 if land else 0.1)
        pb = H * ground
        for a, r in ((-0.5, 1.0), (0.0, 1.2), (0.5, 1.0), (-0.9, 0.8), (0.9, 0.8)):
            ex, ey = px + math.sin(a) * H * 0.06 * r, pb - H * 0.1 - math.cos(a) * H * 0.06 * r
            d.ellipse([ex - H * 0.022, ey - H * 0.04, ex + H * 0.022, ey + H * 0.04], fill=(110, 185, 120), outline=(70, 140, 90), width=3)
        d.polygon([(px - H * 0.045, pb - H * 0.09), (px + H * 0.045, pb - H * 0.09), (px + H * 0.033, pb), (px - H * 0.033, pb)], fill=(240, 150, 120), outline=OUT, width=4)
        # round fluffy rug + three stretch mats (pink, mint, sky)
        ry0 = H * (ground - 0.012)
        d.ellipse([W * 0.06, ry0, W * 0.94, ry0 + H * (0.13 if land else 0.09)], fill=(250, 238, 214), outline=(232, 214, 186), width=6)
        mats = ((0.25, (255, 182, 200)), (0.5, (170, 226, 200)), (0.75, (170, 205, 245))) if land else ((0.22, (255, 182, 200)), (0.5, (170, 226, 200)), (0.78, (170, 205, 245)))
        for mx, col in mats:
            mw = W * (0.1 if land else 0.13)
            d.rounded_rectangle([W * mx - mw, ry0 + H * 0.012, W * mx + mw, ry0 + H * 0.045], 18, fill=col, outline=OUT, width=4)
    elif kind in ("living_room", "fort_ship"):
        # Honey's cosy living room on a rainy day: striped cream wall, big rainy window, green sofa,
        # lamp glow, bookshelf, wooden floor. "fort_ship" adds the blanket-fort ship: two chairs, a
        # cardboard-box hull (front edge is a foreground layer, so friends stand IN the boat), a broom
        # mast with a sheet sail and a star flag, and a blue blanket "sea" with soft wave curls.
        L = W > H
        im = grad(W, H, (255, 240, 220), (250, 228, 205))
        d = ImageDraw.Draw(im)
        sw = int(W * (0.05 if L else 0.09))
        for xx in range(0, W, sw * 2):
            d.rectangle([xx, 0, xx + sw, H * ground], fill=(252, 232, 210))
        # big window with a soft rainy sky
        wx0, wx1 = W * (0.33 if L else 0.2), W * (0.67 if L else 0.8)
        wy0, wy1 = H * (0.1 if L else 0.07), H * (0.5 if L else 0.28)
        d.rounded_rectangle([wx0 - 18, wy0 - 18, wx1 + 18, wy1 + 18], 20, fill=(255, 252, 245), outline=OUT, width=5)
        sky = grad(int(wx1 - wx0), int(wy1 - wy0), (170, 180, 225), (215, 220, 240))
        sd = ImageDraw.Draw(sky)
        sw_, sh_ = sky.size
        sd.ellipse([-sw_ * 0.2, sh_ * 0.75, sw_ * 1.2, sh_ * 1.6], fill=(150, 195, 140))
        for (cx, cy, r) in ((0.25, 0.22, 0.2), (0.45, 0.16, 0.24), (0.7, 0.24, 0.2)):
            sd.ellipse([sw_ * cx - sh_ * r * 1.4, sh_ * cy - sh_ * r * 0.7, sw_ * cx + sh_ * r * 1.4, sh_ * cy + sh_ * r * 0.7], fill=(235, 238, 250))
        for i in range(40):
            x, y = rnd.uniform(0, sw_), rnd.uniform(sh_ * 0.3, sh_ * 0.95)
            sd.line([x, y, x - 4, y + sh_ * 0.06], fill=(240, 245, 255), width=3)
        im.paste(sky, (int(wx0), int(wy0)))
        d = ImageDraw.Draw(im)
        for i in range(10):  # shiny drops on the glass
            x, y = rnd.uniform(wx0 + 20, wx1 - 20), rnd.uniform(wy0 + 20, wy1 - 20)
            r = H * 0.007
            d.ellipse([x - r, y - r * 1.3, x + r, y + r * 1.3], fill=(250, 252, 255))
        d.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=(255, 252, 245), width=12)
        d.line([wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2], fill=(255, 252, 245), width=12)
        # curtains
        for (x0, x1) in ((wx0 - W * 0.07, wx0 + W * 0.01), (wx1 - W * 0.01, wx1 + W * 0.07)):
            d.rounded_rectangle([x0, wy0 - 34, x1, wy1 + H * 0.04], 30, fill=(255, 175, 160), outline=OUT, width=4)
        d.line([wx0 - W * 0.09, wy0 - 34, wx1 + W * 0.09, wy0 - 34], fill=(180, 120, 90), width=10)
        # lamp glow (left) + bookshelf (right)
        lx, ly = W * (0.07 if L else 0.1), H * (ground - (0.42 if L else 0.3))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - H * 0.16, ly - H * 0.14, lx + H * 0.16, ly + H * 0.18], fill=(255, 230, 160, 110))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(45)))
        d = ImageDraw.Draw(im)
        d.line([lx, ly, lx, H * ground], fill=(150, 110, 80), width=10)
        d.polygon([(lx - H * 0.05, ly), (lx + H * 0.05, ly), (lx + H * 0.035, ly - H * 0.07), (lx - H * 0.035, ly - H * 0.07)], fill=(255, 220, 140), outline=OUT)
        bx0, bx1 = W * (0.86 if L else 0.84), W * (0.98 if L else 1.0)
        by0 = H * (ground - (0.5 if L else 0.3))
        d.rectangle([bx0, by0, bx1, H * ground], fill=(200, 140, 95), outline=OUT, width=4)
        nshelf = 4
        for k in range(nshelf):
            y = by0 + (H * ground - by0) * (k + 1) / (nshelf + 0.3)
            d.line([bx0, y, bx1, y], fill=(150, 100, 70), width=6)
            x = bx0 + 8
            for j in range(5):
                bwid = (bx1 - bx0) * rnd.uniform(0.1, 0.16)
                bh = (H * ground - by0) / (nshelf + 0.3) * rnd.uniform(0.55, 0.8)
                col = [(255, 120, 150), (120, 200, 240), (255, 200, 80), (150, 215, 130), (200, 160, 240)][(j + k) % 5]
                if x + bwid < bx1 - 6:
                    d.rectangle([x, y - bh, x + bwid, y - 3], fill=col)
                x += bwid + 4
        # floor
        d.rectangle([0, H * ground, W, H], fill=(205, 150, 100))
        for k in range(1, 6):
            d.line([0, H * ground + k * H * 0.03, W, H * ground + k * H * 0.03], fill=(188, 134, 88), width=2)
        d.rectangle([0, H * ground - 6, W, H * ground + 4], fill=(240, 205, 165))
        if kind == "living_room":
            # green sofa (left) and a soft round rug
            sx0, sx1 = W * (0.0 if L else -0.05), W * (0.3 if L else 0.36)
            sy = H * (ground - (0.2 if L else 0.12))
            d.rounded_rectangle([sx0, sy - H * (0.1 if L else 0.06), sx1, sy + H * 0.04], 40, fill=(120, 190, 150), outline=OUT, width=5)
            d.rounded_rectangle([sx0 - 10, sy, sx1 + 20, H * ground + 2], 30, fill=(140, 205, 165), outline=OUT, width=5)
            d.line([(sx0 + sx1) / 2, sy + 10, (sx0 + sx1) / 2, sy + H * 0.06], fill=(110, 175, 135), width=5)
            d.ellipse([W * 0.32, H * (ground + 0.015), W * 0.82, H * (ground + 0.12)], fill=(255, 205, 140), outline=(240, 175, 110), width=6)
            d.ellipse([W * 0.39, H * (ground + 0.035), W * 0.75, H * (ground + 0.1)], outline=(255, 245, 230), width=5)
        else:
            # blue blanket sea with wave curls
            d.rectangle([0, H * (ground + 0.01), W, H], fill=(110, 170, 235))
            for row in range(3):
                y = H * (ground + 0.035 + row * 0.04)
                for k in range(-1, 12):
                    x = W * (k / 10.0) + (row % 2) * W * 0.05
                    d.arc([x, y - H * 0.015, x + W * 0.06, y + H * 0.02], 200, 340, fill=(235, 245, 255), width=5)
            # two little chairs holding up a polka-dot blanket roof
            hx0, hx1 = W * (0.14 if L else 0.03), W * (0.86 if L else 0.97)
            ry = H * (ground - (0.5 if L else 0.34))
            seat = H * (ground - (0.2 if L else 0.13))
            for cx in (hx0 + W * 0.025, hx1 - W * 0.025):
                cw = W * (0.035 if L else 0.05)
                for lx_ in (cx - cw * 0.8, cx + cw * 0.8):
                    d.line([lx_, seat, lx_, H * ground], fill=(170, 105, 65), width=10)
                d.rounded_rectangle([cx - cw, ry, cx + cw, seat], 14, fill=(200, 130, 85), outline=OUT, width=4)
                d.rounded_rectangle([cx - cw * 1.3, seat - H * 0.012, cx + cw * 1.3, seat + H * 0.012], 6, fill=(185, 115, 75), outline=OUT, width=3)
            sag = H * 0.035
            top_pts = [(hx0 - W * 0.01 + (hx1 - hx0 + W * 0.02) * k / 30, ry - H * 0.01 + math.sin(k / 30 * math.pi) * sag) for k in range(31)]
            bot_pts = [(x, y + H * 0.045 + (H * 0.012 if k % 3 == 1 else 0)) for k, (x, y) in enumerate(top_pts)][::-1]
            d.polygon(top_pts + bot_pts, fill=(190, 160, 235), outline=OUT, width=4)
            for k in range(2, 30, 3):
                x, y = top_pts[k]
                d.ellipse([x - 7, y + H * 0.018, x + 7, y + H * 0.018 + 14], fill=(255, 255, 255))
            # sheet sail on a broom mast with a star flag (pokes through the blanket)
            mx = W * 0.5
            top = H * (0.04 if L else 0.06)
            d.line([mx, top, mx, H * ground], fill=(190, 130, 80), width=int(H * 0.012))
            sb = ry - H * 0.03
            d.polygon([(mx + 10, top + H * 0.03), (mx + 10, sb), (mx + W * (0.18 if L else 0.32), sb)], fill=(255, 255, 250), outline=OUT, width=5)
            d.polygon([(mx - 10, top + H * 0.05), (mx - 10, sb), (mx - W * (0.13 if L else 0.24), sb)], fill=(255, 220, 150), outline=OUT, width=5)
            d.polygon([(mx, top), (mx, top + H * 0.035), (mx - W * (0.05 if L else 0.09), top + H * 0.0175)], fill=(255, 120, 150), outline=OUT)
            # back of the cardboard-box hull
            hy = H * (ground - (0.1 if L else 0.07))
            d.rectangle([hx0, hy, hx1, H * ground], fill=(205, 160, 110), outline=OUT, width=4)
            fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fd = ImageDraw.Draw(fg)
            fy = H * (ground - (0.05 if L else 0.04))
            hull = [(hx0 - W * 0.02, fy), (hx1 + W * 0.02, fy), (hx1 - W * 0.04, H * (ground + 0.03)), (hx0 + W * 0.04, H * (ground + 0.03))]
            fd.polygon(hull, fill=(225, 175, 120), outline=OUT, width=6)
            fd.line([hx0 + W * 0.02, fy + H * 0.025, hx1 - W * 0.02, fy + H * 0.025], fill=(195, 145, 95), width=4)
            for k in range(3):  # painted portholes
                x = hx0 + (hx1 - hx0) * (0.25 + 0.25 * k)
                r = H * 0.016
                fd.ellipse([x - r, fy + H * 0.012 - r, x + r, fy + H * 0.012 + r], fill=(150, 200, 250), outline=OUT, width=4)
    elif kind == "dusk_stage":
        # golden-hour meadow concert: lavender-peach sky, rising moon, lantern string, big tree-stump stage centre
        land = W > H
        im = grad(W, H, (118, 112, 196), (255, 192, 160))
        d = ImageDraw.Draw(im)
        mx, my, mr = W * (0.56 if land else 0.52), H * (0.36 if land else 0.34), min(W, H) * 0.07
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([mx - mr * 2.4, my - mr * 2.4, mx + mr * 2.4, my + mr * 2.4], fill=(255, 245, 200, 90))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 246, 205))
        for _ in range(int(35 * W * H / (1920 * 1080))):
            stars.append((rnd.uniform(0, W), rnd.uniform(H * 0.03, H * 0.3), rnd.uniform(1.2, 2.8), rnd.uniform(0, 6.28)))
        for i in range(3):
            cloud(d, rnd.uniform(0, W * 0.3 if land else W * 0.1), rnd.uniform(H * 0.22, H * 0.38), min(W, H) / 1100, (255, 205, 215))
        hills(d, W, H, ground - 0.13, 0.08, (190, 150, 190), 4)
        tree(d, W, H, W * (0.9 if land else 0.92), False)
        hills(d, W, H, ground - 0.03, 0.05, (130, 185, 125), 6)
        d.rectangle([0, H * ground, W, H], fill=(120, 180, 115))
        # big tree-stump stage
        sx, sw = W * 0.5, W * (0.13 if land else 0.24)
        top, bot = H * (ground - (0.1 if land else 0.065)), H * (ground + 0.01)
        eh = sw * 0.32
        d.rectangle([sx - sw, top, sx + sw, bot], fill=(150, 100, 70))
        for k in range(1, 6):
            xx = sx - sw + k * 2 * sw / 6
            d.line([xx, top + eh * 0.5, xx, bot - 6], fill=(125, 82, 58), width=5)
        d.ellipse([sx - sw - 12, bot - eh * 0.6, sx + sw + 12, bot + eh * 0.5], fill=(150, 100, 70))
        d.ellipse([sx - sw, top - eh / 2, sx + sw, top + eh / 2], fill=(222, 178, 130), outline=(150, 100, 70), width=8)
        for r in (0.7, 0.45, 0.2):
            d.ellipse([sx - sw * r, top - eh / 2 * r, sx + sw * r, top + eh / 2 * r], outline=(190, 140, 100), width=4)
        # lantern string with glowing paper lanterns
        x0, x1 = W * 0.03, W * 0.97
        yA, sag = H * (0.1 if land else 0.13), H * 0.07
        d.line([x0, yA - H * 0.02, x0, H * ground], fill=(130, 90, 70), width=10)
        d.line([x1, yA - H * 0.02, x1, H * ground], fill=(130, 90, 70), width=10)
        pts = [(x0 + (x1 - x0) * t, yA + sag * 4 * t * (1 - t)) for t in np.linspace(0, 1, 40)]
        d.line(pts, fill=(110, 80, 70), width=4)
        cols = [(255, 150, 170), (255, 215, 110), (150, 210, 255), (180, 235, 150), (210, 170, 255)]
        n = 9 if land else 6
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        lan = []
        for k in range(n):
            t = (k + 0.5) / n
            lx, ly = x0 + (x1 - x0) * t, yA + sag * 4 * t * (1 - t) + H * 0.035
            lr = min(W, H) * 0.028
            gd.ellipse([lx - lr * 2.5, ly - lr * 2.5, lx + lr * 2.5, ly + lr * 2.5], fill=cols[k % 5] + (110,))
            lan.append((lx, ly, lr, cols[k % 5]))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(25)))
        d = ImageDraw.Draw(im)
        for lx, ly, lr, c in lan:
            d.line([lx, ly - lr * 1.6, lx, ly - lr], fill=(110, 80, 70), width=3)
            d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr * 1.1], fill=c, outline=OUT, width=4)
            d.line([lx - lr * 0.5, ly - lr * 0.95, lx + lr * 0.5, ly - lr * 0.95], fill=(110, 80, 70), width=5)
        flowers(d, W, H, ground * H, 55, 21)
        for _ in range(8):
            stars.append((rnd.uniform(W * 0.05, W * 0.95), rnd.uniform(H * (ground - 0.3), H * (ground - 0.08)), rnd.uniform(3, 5), rnd.uniform(0, 6.28)))
    elif kind == "sunny_hill":
        # bright picnic hill: big tree + small sapling (big/small), slide (up/down), stepping-stone path
        land = W > H
        im = grad(W, H, (125, 200, 250), (250, 246, 220))
        d = ImageDraw.Draw(im)
        sx, sy, sr = W * (0.42 if land else 0.5), H * (0.13 if land else 0.1), min(W, H) * 0.07
        d.ellipse([sx - sr * 1.4, sy - sr * 1.4, sx + sr * 1.4, sy + sr * 1.4], fill=(255, 242, 175))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 216, 95))
        for cx, cy in ((0.12, 0.08), (0.6, 0.05), (0.78, 0.16)):
            cloud(d, W * cx, H * cy, min(W, H) / 1100, (255, 255, 255))
        hills(d, W, H, ground - 0.15, 0.09, (175, 225, 150), 12)
        # big tree (left) and a small sapling beside it
        bx = W * (0.07 if land else 0.12)
        U = H if land else W * 0.7
        tw, tb = U * 0.035, H * (ground - 0.01)
        d.rectangle([bx - tw, H * ground - U * 0.42, bx + tw, tb], fill=(120, 85, 62))
        for dx, dy, r in ((0, -0.5, 0.15), (-0.09, -0.42, 0.11), (0.09, -0.42, 0.11), (0, -0.62, 0.11)):
            d.ellipse([bx + dx * U - r * U, H * ground + dy * U - r * U * 0.85, bx + dx * U + r * U, H * ground + dy * U + r * U * 0.85], fill=(105, 185, 105))
        for (ax, ay) in ((-0.06, -0.5), (0.05, -0.45), (0.01, -0.6), (-0.03, -0.4)):
            d.ellipse([bx + ax * U - 9, H * ground + ay * U - 9, bx + ax * U + 9, H * ground + ay * U + 9], fill=(235, 70, 80))
        nx = W * (0.2 if land else 0.33)
        d.rectangle([nx - U * 0.007, H * ground - U * 0.12, nx + U * 0.007, tb], fill=(120, 85, 62))
        d.ellipse([nx - U * 0.04, H * ground - U * 0.17, nx + U * 0.04, H * ground - U * 0.1], fill=(140, 205, 120))
        hills(d, W, H, ground - 0.02, 0.035, (130, 205, 112), 13)
        d.rectangle([0, H * ground, W, H], fill=(128, 204, 110))
        slide(d, W, H, W * (0.86 if land else 0.8), ground - 0.005, 1.0 if land else 0.8)
        # stepping-stone path across the front
        for k in range(7):
            px = W * (0.08 + k * 0.14)
            py = H * (ground + 0.035 + 0.02 * math.sin(k * 1.3))
            d.ellipse([px - H * 0.04, py - H * 0.014, px + H * 0.04, py + H * 0.014], fill=(225, 215, 195))
        flowers(d, W, H, ground * H, 50, 31)
    elif kind == "autumn_park":
        # sunny autumn park: soft blue sky, three autumn trees, a curvy path, a green park bench (right),
        # scattered fallen leaves on the grass. Add "leaves": true to a scene for gently falling leaves.
        land = W > H
        im = grad(W, H, (140, 200, 245), (255, 236, 205))
        d = ImageDraw.Draw(im)
        sx, sy, sr = W * (0.5 if land else 0.62), H * (0.12 if land else 0.09), min(W, H) * 0.065
        d.ellipse([sx - sr * 1.4, sy - sr * 1.4, sx + sr * 1.4, sy + sr * 1.4], fill=(255, 238, 180))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 210, 95))
        for cx, cy in ((0.15, 0.07), (0.72, 0.1)):
            cloud(d, W * cx, H * cy, min(W, H) / 1100, (255, 252, 248))
        hills(d, W, H, ground - 0.15, 0.07, (200, 205, 130), 21)
        if land:
            autumn_tree(d, W, H, W * 0.08, ground - 0.06, 1.0)
            autumn_tree(d, W, H, W * 0.33, ground - 0.12, 0.55, ((255, 205, 80), (255, 170, 60), (240, 130, 60)))
            autumn_tree(d, W, H, W * 0.93, ground - 0.07, 0.95, ((245, 110, 70), (255, 185, 70), (200, 120, 70)))
        else:
            autumn_tree(d, W, H, W * 0.1, ground - 0.07, 0.6, sw=1.5)
            autumn_tree(d, W, H, W * 0.9, ground - 0.08, 0.65, ((245, 110, 70), (255, 185, 70), (200, 120, 70)), sw=1.6)
        hills(d, W, H, ground - 0.03, 0.03, (150, 200, 110), 22)
        d.rectangle([0, H * ground, W, H], fill=(140, 195, 100))
        # curvy sandy path
        pts_l, pts_r = [], []
        for k in range(21):
            tt = k / 20
            yy = H * (ground - 0.03 + (1 - ground + 0.03) * tt)
            xx = W * (0.5 + 0.12 * math.sin(tt * 3.0)) 
            wdt = W * (0.03 + 0.11 * tt) if land else W * (0.05 + 0.2 * tt)
            pts_l.append((xx - wdt, yy)); pts_r.append((xx + wdt, yy))
        d.polygon(pts_l + pts_r[::-1], fill=(240, 220, 175))
        # park bench (right, behind characters)
        bx, by, bw = W * (0.78 if land else 0.8), H * (ground - 0.01), min(W, H) * 0.22
        GREEN = (90, 160, 120)
        for k in range(3):
            d.rounded_rectangle([bx - bw / 2, by - bw * (0.55 - k * 0.09), bx + bw / 2, by - bw * (0.49 - k * 0.09)], 6, fill=GREEN)
        d.rounded_rectangle([bx - bw / 2 - 6, by - bw * 0.25, bx + bw / 2 + 6, by - bw * 0.19], 6, fill=GREEN)
        for lx in (bx - bw * 0.42, bx + bw * 0.42):
            d.rectangle([lx - 6, by - bw * 0.25, lx + 6, by], fill=(80, 80, 95))
        # fallen leaves scattered on the grass
        for i in range(70 if land else 55):
            lx = rnd.uniform(0, W)
            ly = H * rnd.uniform(ground - 0.01, 0.995)
            _leaf(d, lx, ly, H * rnd.uniform(0.018, 0.03), ["red", "orange", "yellow", "brown"][i % 4], rnd.uniform(0, 6.28), ol=False)
    elif kind == "autumn_swings":
        # Autumn park playground: soft peach-blue sky, autumn trees left/right, a big wooden A-frame swing set
        # in the middle (frame + beam only; seats are sprites: swing_empty / pip_swing / lulu_swing / honey_swing /
        # dotty_swing, top edge = pivot on the beam at y=BEAM), a little "wait here" leaf line and a sand path.
        land = W > H
        im = grad(W, H, (150, 205, 248), (255, 232, 200))
        d = ImageDraw.Draw(im)
        sx, sy, sr = W * (0.86 if land else 0.82), H * (0.12 if land else 0.08), min(W, H) * 0.06
        d.ellipse([sx - sr * 1.4, sy - sr * 1.4, sx + sr * 1.4, sy + sr * 1.4], fill=(255, 238, 180))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 210, 95))
        for cx, cy in ((0.2, 0.08), (0.58, 0.05)):
            cloud(d, W * cx, H * cy, min(W, H) / 1150, (255, 252, 248))
        hills(d, W, H, ground - 0.14, 0.06, (205, 200, 135), 31)
        if land:
            autumn_tree(d, W, H, W * 0.07, ground - 0.05, 1.0, ((255, 185, 70), (245, 110, 70), (255, 215, 90)))
            autumn_tree(d, W, H, W * 0.94, ground - 0.06, 0.9)
        else:
            autumn_tree(d, W, H, W * 0.06, ground - 0.08, 0.55, sw=1.4)
            autumn_tree(d, W, H, W * 0.95, ground - 0.09, 0.6, ((245, 110, 70), (255, 185, 70), (200, 120, 70)), sw=1.5)
        hills(d, W, H, ground - 0.03, 0.025, (150, 200, 110), 32)
        d.rectangle([0, H * ground, W, H], fill=(140, 195, 100))
        # soft wood-chip patch under the swings
        cx = W * 0.5
        d.ellipse([cx - W * (0.26 if land else 0.45), H * (ground - 0.03), cx + W * (0.26 if land else 0.45), H * (ground + 0.07)], fill=(225, 180, 130))
        # A-frame swing set
        BEAM = 0.255 if land else 0.29
        bl, br = W * (0.30 if land else 0.06), W * (0.70 if land else 0.94)
        WOOD, DARK = (205, 140, 90), (160, 100, 65)
        spread = W * (0.07 if land else 0.09)
        for px in (bl, br):
            for k in (-1, 1):
                d.line([(px, H * BEAM), (px + k * spread, H * (ground + 0.01))], fill=DARK, width=int(min(W, H) * 0.024))
                d.line([(px, H * BEAM), (px + k * spread, H * (ground + 0.01))], fill=WOOD, width=int(min(W, H) * 0.016))
        bh = min(W, H) * 0.028
        d.rounded_rectangle([bl - spread * 0.6, H * BEAM - bh, br + spread * 0.6, H * BEAM + bh * 0.6], int(bh * 0.6), fill=(230, 120, 110), outline=(150, 80, 80), width=4)
        for px in (bl, br):
            d.ellipse([px - bh, H * BEAM - bh * 0.7, px + bh, H * BEAM + bh * 0.9], fill=(255, 205, 90), outline=(150, 80, 80), width=3)
        # fallen leaves on the grass
        for i in range(60 if land else 48):
            lx = rnd.uniform(0, W)
            ly = H * rnd.uniform(ground + 0.005, 0.995)
            _leaf(d, lx, ly, H * rnd.uniform(0.016, 0.028), ["red", "orange", "yellow", "brown"][i % 4], rnd.uniform(0, 6.28), ol=False)
    elif kind == "mimi_room":
        # Mimi Kitten's cosy cottage bedroom at night: mint wall with cream dots, square window with
        # stars (Moon fits at x=0.74 y=0.36 scale 0.5 landscape / x=0.5 y=0.27 scale 0.55 vertical),
        # a warm mushroom night-light, a yarn basket, a little star picture, and a big round wicker
        # kitten bed with a pink cushion and blanket. The bed's front rim is a foreground layer, so
        # Mimi sits IN it at x=0.36 y=0.80 landscape / x=0.5 y=0.70 vertical (scale 0.9).
        land = W > H
        im = grad(W, H, (150, 196, 186), (186, 222, 206))
        d = ImageDraw.Draw(im)
        for i in range(int(70 * W * H / (1920 * 1080))):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.03, H * (ground - 0.04))
            r = H * 0.007
            d.ellipse([x - r, y - r, x + r, y + r], fill=(214, 236, 222))
        d.rectangle([0, H * ground, W, H], fill=(190, 140, 105))
        for k in range(1, 6):
            y = H * ground + (H - H * ground) * k / 6
            d.line([0, y, W, y], fill=(172, 124, 92), width=3)
        d.rectangle([0, H * ground - 10, W, H * ground + 6], fill=(246, 238, 226))
        # square window with night sky
        wx, wy = W * (0.74 if land else 0.5), H * (0.32 if land else 0.24)
        ww, wh = W * (0.11 if land else 0.22), H * (0.2 if land else 0.11)
        fr = (255, 248, 236)
        d.rounded_rectangle([wx - ww - 18, wy - wh - 18, wx + ww + 18, wy + wh + 18], 22, fill=fr)
        win = grad(int(2 * ww), int(2 * wh), (28, 32, 88), (96, 74, 150))
        im.paste(win, (int(wx - ww), int(wy - wh)))
        d = ImageDraw.Draw(im)
        for _ in range(16):
            stars.append((rnd.uniform(wx - ww * 0.9, wx + ww * 0.9), rnd.uniform(wy - wh * 0.9, wy + wh * 0.9), rnd.uniform(1.5, 3.5), rnd.uniform(0, 6.28)))
        d.line([wx, wy - wh, wx, wy + wh], fill=fr, width=10)
        d.line([wx - ww, wy, wx + ww, wy], fill=fr, width=10)
        d.rectangle([wx - ww - 34, wy + wh + 12, wx + ww + 34, wy + wh + 36], fill=fr)
        for s in (-1, 1):  # scalloped pink curtains
            cx = wx + s * (ww + 30)
            d.polygon([(cx - 36, wy - wh - 40), (cx + 36, wy - wh - 40), (cx + s * 20 + 26, wy + wh + 50), (cx + s * 20 - 26, wy + wh + 50)], fill=(255, 190, 210))
        d.rectangle([wx - ww - 100, wy - wh - 52, wx + ww + 100, wy - wh - 38], fill=(200, 150, 120))
        # star picture on the wall
        px, py = W * (0.12 if land else 0.11), H * (0.3 if land else 0.47)
        pr = H * (0.07 if land else 0.045)
        d.rounded_rectangle([px - pr, py - pr, px + pr, py + pr], 12, fill=(255, 236, 200), outline=(200, 150, 120), width=10)
        d.polygon(star_pts(px, py, pr * 0.6), fill=(255, 205, 80), outline=OUT, width=4)
        # mushroom night-light with warm glow (right)
        lx = W * (0.9 if land else 0.86)
        ly = H * (ground - 0.06)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - H * 0.17, ly - H * 0.17, lx + H * 0.17, ly + H * 0.15], fill=(255, 220, 150, 95))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(45)))
        d = ImageDraw.Draw(im)
        sr = H * (0.03 if land else 0.022)
        d.rounded_rectangle([lx - sr * 0.45, ly, lx + sr * 0.45, H * ground], 8, fill=(255, 246, 226), outline=OUT, width=4)
        d.pieslice([lx - sr * 1.4, ly - sr * 1.2, lx + sr * 1.4, ly + sr * 1.2], 180, 360, fill=(255, 150, 140), outline=OUT, width=4)
        for dx, dy in ((-0.6, -0.5), (0.3, -0.8), (0.75, -0.35)):
            d.ellipse([lx + dx * sr - 7, ly + dy * sr - 7, lx + dx * sr + 7, ly + dy * sr + 7], fill=(255, 250, 240))
        # yarn basket (far left)
        yx = W * (0.07 if land else 0.12)
        yr = H * (0.045 if land else 0.03)
        for k, col in enumerate(((150, 190, 250), (255, 170, 200), (255, 215, 110))):
            ex = yx + (k - 1) * yr * 0.9
            d.ellipse([ex - yr * 0.6, H * ground - yr * 2.0, ex + yr * 0.6, H * ground - yr * 0.8], fill=col, outline=OUT, width=4)
        d.rounded_rectangle([yx - yr * 1.7, H * ground - yr * 1.25, yx + yr * 1.7, H * ground], 14, fill=(214, 160, 100), outline=OUT, width=5)
        # soft round rug
        d.ellipse([W * 0.1, H * (ground - 0.01), W * 0.9, H * (ground + (0.11 if land else 0.08))], fill=(255, 226, 232), outline=(240, 200, 210), width=6)
        # round wicker kitten bed: back rim + cushion here, front rim in fg
        bx = W * (0.36 if land else 0.5)
        brx = W * (0.15 if land else 0.3)
        bty = H * (ground - (0.15 if land else 0.09))
        bby = H * (ground + 0.005)
        d.ellipse([bx - brx, bty, bx + brx, bby], fill=(214, 160, 100), outline=OUT, width=6)
        d.ellipse([bx - brx * 0.86, bty + (bby - bty) * 0.12, bx + brx * 0.86, bby - (bby - bty) * 0.2], fill=(255, 180, 205))
        fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fg)
        rim_t = bty + (bby - bty) * 0.5
        fd.chord([bx - brx, rim_t - (bby - rim_t), bx + brx, bby], 0, 180, fill=(214, 160, 100), outline=OUT, width=6)
        for k in range(1, 4):  # wicker weave lines
            yy = rim_t + (bby - rim_t) * k / 4
            hw = brx * math.sqrt(max(0, 1 - ((yy - rim_t) / (bby - rim_t)) ** 2))
            fd.line([bx - hw + 12, yy, bx + hw - 12, yy], fill=(186, 130, 78), width=5)
        # little lavender blanket folded over the rim
        fd.rounded_rectangle([bx - brx * 0.55, rim_t - H * 0.012, bx + brx * 0.25, rim_t + (bby - rim_t) * 0.55], 20, fill=(200, 180, 240), outline=OUT, width=5)
        for k in range(4):
            ex = bx - brx * 0.45 + k * brx * 0.2
            fd.ellipse([ex - 8, rim_t + 4, ex + 8, rim_t + 20], fill=(255, 250, 255))
    elif kind == "twilight_hill":
        # Honey's hilltop garden at twilight: blue-to-peach sky, the big sleepy cloud family up high,
        # little picket fence, a wooden post for Ollie on the right, soft grass
        land = W > H
        im = grad(W, H, (60, 70, 150), (250, 185, 175))
        d = ImageDraw.Draw(im)
        for _ in range(int(70 * W * H / (1920 * 1080))):
            stars.append((rnd.uniform(0, W), rnd.uniform(0, H * 0.32), rnd.uniform(1.5, 3.2), rnd.uniform(0, 6.28)))
        # big sleepy cloud family (soft lavender, sleepy faces)
        fam = [(0.20, 0.13, 1.25), (0.52, 0.09, 1.55), (0.83, 0.15, 1.15)] if land else [(0.22, 0.12, 1.0), (0.58, 0.08, 1.25), (0.86, 0.17, 0.85)]
        for (cx, cy, sc) in fam:
            s = min(W, H) / 900 * sc
            x, y = W * cx - 62 * s, H * cy
            cloud(d, x, y, s, (225, 215, 245))
            cloud(d, x + 8 * s, y + 6 * s, s * 0.93, (240, 234, 252))
            fx = x + 62 * s
            for side in (-1, 1):
                d.arc([fx + side * 24 * s - 11 * s, y - 2 * s, fx + side * 24 * s + 11 * s, y + 10 * s], 20, 160, fill=(130, 110, 150), width=max(2, int(3 * s)))
            d.ellipse([fx - 40 * s, y + 12 * s, fx - 26 * s, y + 20 * s], fill=(250, 190, 205))
            d.ellipse([fx + 26 * s, y + 12 * s, fx + 40 * s, y + 20 * s], fill=(250, 190, 205))
        # low peach sun glow on the horizon
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([W * 0.30, H * (ground - 0.32), W * 0.70, H * (ground - 0.02)], fill=(255, 210, 160, 120))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
        d = ImageDraw.Draw(im)
        hills(d, W, H, ground - 0.14, 0.06, (120, 130, 175), 4)
        hills(d, W, H, ground - 0.05, 0.05, (95, 150, 120), 6)
        d.rectangle([0, H * ground, W, H], fill=(95, 160, 115))
        # small picket fence on the left
        f0, f1 = (0.0, 0.26) if land else (0.0, 0.30)
        fy = H * (ground - (0.12 if land else 0.07))
        d.rectangle([W * f0, fy + H * 0.025, W * f1, fy + H * 0.04], fill=(250, 240, 230))
        for k in range(int((f1 - f0) * (18 if land else 10)) + 1):
            px = W * f0 + k * W * (1 / 18 if land else 1 / 10) + 10
            d.polygon([(px - 14, H * ground), (px - 14, fy + 12), (px, fy - 4), (px + 14, fy + 12), (px + 14, H * ground)], fill=(250, 240, 230), outline=(170, 140, 140))
        # wooden post for Ollie on the right
        px = W * (0.86 if land else 0.84)
        top = H * (ground - (0.24 if land else 0.16))
        pw = min(W, H) * 0.05
        d.rounded_rectangle([px - pw, top, px + pw, H * ground + 6], 14, fill=(150, 105, 80), outline=(110, 75, 65), width=5)
        d.ellipse([px - pw, top - pw * 0.35, px + pw, top + pw * 0.35], fill=(185, 140, 105), outline=(110, 75, 65), width=5)
        flowers(d, W, H, ground * H + H * 0.02, 35, 21)
    elif kind == "bathroom":
        # Honey's sunny morning bathroom: aqua wall with bubble dots above white square tiles, round
        # porthole window with the morning sun (left), towel hooks, and a low kid-height sink on the
        # right with a mirror, a cup of four toothbrushes (pink, blue, yellow, lavender) and a pink step
        # stool. Lavender/white checker floor and a round blue bath mat front-centre.
        L = W > H
        im = grad(W, H, (175, 225, 228), (200, 238, 236))
        d = ImageDraw.Draw(im)
        for i in range(int(46 * W * H / (1920 * 1080))):
            x, y, r = rnd.uniform(0, W), rnd.uniform(H * 0.03, H * 0.42), H * rnd.uniform(0.006, 0.014)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(235, 250, 252), width=3)
        ty = H * (0.47 if L else 0.44)
        d.rectangle([0, ty, W, H * ground], fill=(252, 252, 250))
        ts = H * (0.065 if L else 0.042)
        k = 0
        while ty + k * ts < H * ground:
            d.line([0, ty + k * ts, W, ty + k * ts], fill=(205, 228, 232), width=3); k += 1
        for xx in range(0, W + 1, int(ts)):
            d.line([xx, ty, xx, H * ground], fill=(205, 228, 232), width=3)
        d.rectangle([0, ty - 10, W, ty + 6], fill=(140, 205, 210))
        # porthole window with morning sun
        wx, wy, wr = W * (0.15 if L else 0.2), H * (0.24 if L else 0.15), H * (0.13 if L else 0.065)
        d.ellipse([wx - wr - 20, wy - wr - 20, wx + wr + 20, wy + wr + 20], fill=(255, 250, 240), outline=OUT, width=5)
        win = grad(int(2 * wr), int(2 * wr), (150, 205, 250), (255, 232, 200))
        wd = ImageDraw.Draw(win)
        s = win.size[0]
        wd.ellipse([s * 0.5, s * 0.18, s * 0.82, s * 0.5], fill=(255, 220, 110))
        wd.ellipse([-s * 0.2, s * 0.72, s * 1.2, s * 1.4], fill=(150, 210, 130))
        wd.ellipse([s * 0.1, s * 0.3, s * 0.42, s * 0.42], fill=(255, 255, 255))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, s, s], fill=255)
        im.paste(win, (int(wx - wr), int(wy - wr)), mask)
        d = ImageDraw.Draw(im)
        d.line([wx - wr, wy, wx + wr, wy], fill=(255, 250, 240), width=10)
        # towel hooks with a pink and a blue towel
        hx = W * (0.36 if L else 0.08)
        for i, col in enumerate(((255, 170, 195), (140, 195, 245))):
            x = hx + i * W * (0.08 if L else 0.13)
            top = H * (0.36 if L else 0.30)
            d.ellipse([x - 12, top - 12, x + 12, top + 12], fill=(230, 190, 120), outline=OUT, width=4)
            tw, th = W * (0.03 if L else 0.05), H * (0.2 if L else 0.12)
            d.rounded_rectangle([x - tw, top + 6, x + tw, top + th], 16, fill=col, outline=OUT, width=5)
            d.rectangle([x - tw + 6, top + th * 0.72, x + tw - 6, top + th * 0.8], fill=(255, 255, 255))
        # sink vanity (right)
        sx0, sx1 = W * (0.66 if L else 0.5), W * (0.95 if L else 0.98)
        cy0 = H * (ground - (0.30 if L else 0.2))
        # mirror
        mx0, mx1 = sx0 + (sx1 - sx0) * 0.18, sx1 - (sx1 - sx0) * 0.18
        my0, my1 = H * (0.08 if L else 0.2), cy0 - H * (0.1 if L else 0.06)
        d.rounded_rectangle([mx0 - 16, my0 - 16, mx1 + 16, my1 + 16], 60, fill=(255, 205, 150), outline=OUT, width=5)
        d.rounded_rectangle([mx0, my0, mx1, my1], 48, fill=(220, 240, 252))
        d.line([mx0 + (mx1 - mx0) * 0.2, my0 + (my1 - my0) * 0.45, mx0 + (mx1 - mx0) * 0.45, my0 + (my1 - my0) * 0.15], fill=(255, 255, 255), width=12)
        d.line([mx0 + (mx1 - mx0) * 0.3, my0 + (my1 - my0) * 0.55, mx0 + (mx1 - mx0) * 0.5, my0 + (my1 - my0) * 0.3], fill=(255, 255, 255), width=7)
        # cabinet + counter
        d.rounded_rectangle([sx0 + 10, cy0, sx1 - 10, H * ground + 4], 12, fill=(255, 238, 205), outline=OUT, width=5)
        midx = (sx0 + sx1) / 2
        d.line([midx, cy0 + H * 0.05, midx, H * ground - 8], fill=OUT, width=4)
        for x in (midx - W * 0.02, midx + W * 0.02):
            d.ellipse([x - 9, cy0 + H * 0.12 - 9, x + 9, cy0 + H * 0.12 + 9], fill=(150, 205, 210), outline=OUT, width=3)
        d.rounded_rectangle([sx0 - 10, cy0 - H * 0.035, sx1 + 10, cy0 + H * 0.01], 14, fill=(255, 255, 255), outline=OUT, width=5)
        # basin + tap
        d.ellipse([midx - (sx1 - sx0) * 0.22, cy0 - H * 0.05, midx + (sx1 - sx0) * 0.22, cy0 - H * 0.01], fill=(215, 240, 245), outline=OUT, width=4)
        d.rounded_rectangle([midx - 10, cy0 - H * 0.1, midx + 10, cy0 - H * 0.04], 8, fill=(200, 210, 220), outline=OUT, width=4)
        d.rounded_rectangle([midx - 10, cy0 - H * 0.1, midx + W * 0.03, cy0 - H * 0.085], 8, fill=(200, 210, 220), outline=OUT, width=4)
        # toothbrush cup with four brushes (left end of counter)
        ux = sx0 + (sx1 - sx0) * 0.1
        uh, uw = H * (0.07 if L else 0.045), W * (0.022 if L else 0.035)
        ut = cy0 - H * 0.035 - uh
        for j, c in enumerate(((255, 140, 180), (100, 170, 245), (255, 205, 70), (190, 155, 245))):
            bx = ux - uw * 0.6 + j * uw * 0.4
            bt = ut - H * (0.05 if L else 0.032) - (j % 2) * H * 0.012
            d.line([bx, ut + uh * 0.5, bx + (j - 1.5) * 6, bt], fill=c, width=int(H * 0.009))
            d.rounded_rectangle([bx + (j - 1.5) * 6 - 7, bt - H * 0.018, bx + (j - 1.5) * 6 + 7, bt], 4, fill=(255, 255, 255), outline=OUT, width=2)
        d.rounded_rectangle([ux - uw, ut, ux + uw, ut + uh], 10, fill=(255, 215, 90), outline=OUT, width=4)
        # little plant (right end of counter)
        px = sx1 - (sx1 - sx0) * 0.1
        for a in (-0.5, 0, 0.5):
            d.ellipse([px + a * 30 - 14, cy0 - H * 0.1 + abs(a) * 20, px + a * 30 + 14, cy0 - H * 0.05], fill=(120, 195, 120))
        d.rounded_rectangle([px - 20, cy0 - H * 0.065, px + 20, cy0 - H * 0.035], 6, fill=(240, 150, 120), outline=OUT, width=3)
        # floor: lavender/white checks + bath mat
        d.rectangle([0, H * ground, W, H], fill=(250, 248, 255))
        cs = H * (0.05 if L else 0.035)
        for r in range(int((H - H * ground) / cs) + 2):
            for c in range(int(W / cs) + 2):
                if (r + c) % 2 == 0:
                    d.rectangle([c * cs, H * ground + r * cs, (c + 1) * cs, H * ground + (r + 1) * cs], fill=(222, 210, 245))
        d.rectangle([0, H * ground - 8, W, H * ground + 4], fill=(140, 205, 210))
        d.ellipse([W * 0.25, H * (ground + 0.015), W * 0.62, H * (ground + 0.11)], fill=(130, 190, 240), outline=(105, 165, 225), width=6)
        d.ellipse([W * 0.31, H * (ground + 0.035), W * 0.56, H * (ground + 0.09)], outline=(255, 255, 255), width=5)
        # pink step stool in front of the sink
        st0, st1 = midx - W * (0.06 if L else 0.1), midx + W * (0.06 if L else 0.1)
        sty = H * (ground - (0.07 if L else 0.045))
        d.rounded_rectangle([st0, sty, st1, sty + H * 0.025], 10, fill=(255, 160, 190), outline=OUT, width=5)
        for x in (st0 + 18, st1 - 30):
            d.rectangle([x, sty + H * 0.02, x + 12, H * ground + H * 0.01], fill=(235, 130, 165), outline=OUT, width=3)
    elif kind in ("nest_tree", "burrow_bank", "owl_tree", "dusk_pond"):
        # ep020 "Where Do Animals Sleep?": golden-hour / dusk woodland walk.
        land = W > H
        sky = {"nest_tree": ((150, 185, 240), (255, 214, 168)), "burrow_bank": ((178, 168, 230), (255, 200, 170)),
               "owl_tree": ((96, 98, 170), (238, 170, 170)), "dusk_pond": ((210, 150, 200), (255, 190, 140))}[kind]
        im = grad(W, H, *sky)
        d = ImageDraw.Draw(im)
        if kind in ("nest_tree", "dusk_pond"):  # low warm sun
            sx, sy, sr = W * (0.8 if land else 0.75), H * (ground - 0.2 if land else ground - 0.22), min(W, H) * 0.07
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([sx - sr * 3, sy - sr * 3, sx + sr * 3, sy + sr * 3], fill=(255, 230, 170, 120))
            im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
            d = ImageDraw.Draw(im)
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 196, 100))
        if kind == "owl_tree":  # rising moon + first stars
            mx, my, mr = W * (0.8 if land else 0.78), H * (0.16 if land else 0.13), min(W, H) * 0.075
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([mx - mr * 2.4, my - mr * 2.4, mx + mr * 2.4, my + mr * 2.4], fill=(255, 250, 210, 90))
            im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
            d = ImageDraw.Draw(im)
            d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 246, 200))
            d.ellipse([mx - mr * 0.45, my - mr * 0.2, mx - mr * 0.15, my + mr * 0.1], fill=(245, 232, 180))
            for _ in range(22):
                stars.append((rnd.uniform(0, W), rnd.uniform(0, H * 0.4), rnd.uniform(1.8, 3.8), rnd.uniform(0, 6.28)))
        if kind == "burrow_bank":
            for cx, cy in ((0.62, 0.1), (0.15, 0.16)):
                cloud(d, W * cx, H * cy, min(W, H) / 1200, (255, 236, 236))
        dusk = kind == "owl_tree"
        hills(d, W, H, ground - 0.12, 0.06, (150, 160, 150) if dusk else (205, 190, 140), 31)
        hills(d, W, H, ground - 0.03, 0.03, (90, 130, 105) if dusk else (150, 195, 110), 32)
        d.rectangle([0, H * ground, W, H], fill=(80, 128, 96) if dusk else (135, 190, 100))
        TRUNK, BARK = (135, 92, 66), (110, 74, 54)
        if kind == "nest_tree":
            tx, tw = W * (0.17 if land else 0.13), W * (0.075 if land else 0.11)
            d.polygon([(tx - tw, H * ground), (tx - tw * 0.7, H * 0.1), (tx + tw * 0.7, H * 0.1), (tx + tw, H * ground)], fill=TRUNK)
            by, bx1 = H * (0.50 if land else 0.40), W * (0.63 if land else 0.80)
            bt = H * (0.03 if land else 0.022)
            d.polygon([(tx, by - bt * 1.6), (bx1, by - bt * 0.5), (bx1 + bt, by), (bx1, by + bt * 0.4), (tx, by + bt * 1.6)], fill=TRUNK)
            for k in range(6):
                d.line([tx - tw * 0.4 + k * tw * 0.15, H * (ground - 0.05), tx - tw * 0.35 + k * tw * 0.14, H * 0.2], fill=BARK, width=4)
            for i, (dx, dy, r) in enumerate(((0.0, 0.10, 0.17), (0.13, 0.06, 0.12), (-0.1, 0.18, 0.12), (0.22, 0.16, 0.10), (0.05, 0.24, 0.11))):
                rr = r * (W if land else W * 1.4)
                cx, cy = tx + dx * W, H * dy * (1 if land else 0.75)
                d.ellipse([cx - rr, cy - rr * 0.8, cx + rr, cy + rr * 0.8], fill=[(245, 150, 70), (255, 196, 80), (235, 110, 70), (250, 170, 60), (255, 210, 110)][i])
            for k in range(3):  # small leaves on the branch
                _leaf(d, tx + (bx1 - tx) * (0.35 + k * 0.25), by - bt * 1.8, H * 0.03, ["orange", "red", "yellow"][k], 0.6 + k)
        if kind == "burrow_bank":
            # big grassy bank with a burrow door; the bunny sits at x=0.42 (landscape) / 0.40 (vertical)
            hx = W * (0.42 if land else 0.40)
            d.ellipse([hx - W * (0.42 if land else 0.6), H * (ground - 0.26), hx + W * (0.42 if land else 0.6), H * (ground + 0.2)], fill=(120, 182, 98))
            hr, hh = W * (0.085 if land else 0.15), H * (0.10 if land else 0.075)
            hy = H * (ground - 0.02)
            d.ellipse([hx - hr - 14, hy - hh - 14, hx + hr + 14, hy + hh + 14], fill=(150, 108, 78))
            d.ellipse([hx - hr, hy - hh, hx + hr, hy + hh], fill=(70, 46, 40))
            d.ellipse([hx - hr * 0.7, hy - hh * 0.6, hx + hr * 0.7, hy + hh], fill=(52, 34, 32))
            for k in (-1, 1):  # roots arching over the door
                d.arc([hx - hr * 1.5 + k * hr * 0.3, hy - hh * 1.9, hx + hr * 1.5 + k * hr * 0.3, hy + hh * 0.6], 200, 340, fill=(130, 90, 62), width=12)
            for (mx, c) in ((0.12, (240, 100, 100)), (0.8, (255, 170, 80))):  # little mushrooms
                x0, y0, s0 = W * mx, H * (ground + 0.03), min(W, H) * 0.03
                d.rectangle([x0 - s0 * 0.35, y0 - s0 * 1.4, x0 + s0 * 0.35, y0], fill=(250, 240, 225))
                d.chord([x0 - s0 * 1.2, y0 - s0 * 2.6, x0 + s0 * 1.2, y0 - s0 * 0.6], 180, 360, fill=c)
                for dx in (-0.5, 0.4):
                    d.ellipse([x0 + s0 * dx - 6, y0 - s0 * 2.0 - 6, x0 + s0 * dx + 6, y0 - s0 * 2.0 + 6], fill=(255, 255, 255))
            flowers(d, W, H, H * (ground + 0.02), 30 if land else 22, 33)
            autumn_tree(d, W, H, W * (0.9 if land else 0.88), ground - 0.04, 0.85 if land else 0.6, sw=None if land else 1.5)
        if kind == "owl_tree":
            # thick trunk with Ollie's round home hole. Ollie: x=0.32 y=0.47 scale 0.55 + hole_rim x=0.32 y=0.505
            # (landscape); vertical: x=0.35, Ollie y=0.405 scale 0.45, hole_rim y=0.44 scale 0.6
            tx, tw = W * (0.32 if land else 0.35), W * (0.12 if land else 0.2)
            d.polygon([(tx - tw * 1.25, H * ground), (tx - tw, 0), (tx + tw, 0), (tx + tw * 1.25, H * ground)], fill=(120, 84, 66))
            for k in range(7):
                x0 = tx - tw * 0.85 + k * tw * 0.28
                d.line([x0, H * 0.02, x0 + tw * 0.05, H * (ground - 0.02)], fill=(98, 68, 54), width=5)
            hx, hy = tx, H * (0.40 if land else 0.37)
            hr, hh = (W * 0.06, H * 0.09) if land else (W * 0.097, H * 0.055)
            d.ellipse([hx - hr - 16, hy - hh - 16, hx + hr + 16, hy + hh + 16], fill=(95, 62, 46))
            d.ellipse([hx - hr, hy - hh, hx + hr, hy + hh], fill=(48, 32, 34))
            for i, (dx, r) in enumerate(((-0.12, 0.13), (0.1, 0.12), (0.0, 0.10))):  # leafy canopy at the top
                rr = r * (W if land else W * 1.6)
                d.ellipse([tx + dx * W - rr, -rr * 0.6, tx + dx * W + rr, rr * 0.9], fill=[(200, 110, 70), (220, 150, 70), (180, 95, 70)][i])
            for i in range(14):  # gentle fireflies
                stars.append((rnd.uniform(W * 0.5, W), rnd.uniform(H * 0.55, H * (ground - 0.02)), rnd.uniform(3, 5), rnd.uniform(0, 6.28)))
        if kind == "dusk_pond":
            # pond at sunset, reeds and lily pads; Dotty stands at the pond's edge x=0.56 (land) / 0.6 (vertical)
            px0, px1 = (W * 0.5, W * 1.15) if land else (W * 0.3, W * 1.3)
            py0, py1 = H * (ground - 0.06), H * (ground + 0.13)
            d.ellipse([px0 - 12, py0 - 10, px1 + 12, py1 + 12], fill=(170, 150, 110))
            d.ellipse([px0, py0, px1, py1], fill=(130, 170, 220))
            for k in range(4):  # sunset shimmer
                yy = py0 + (py1 - py0) * (0.25 + k * 0.15)
                d.line([px0 + W * 0.12, yy, px0 + W * (0.3 - k * 0.03), yy], fill=(255, 210, 170), width=5)
            for (lx, ly) in ((0.78, 0.04), (0.92, 0.09), (0.66, 0.1)):
                cx, cy, rr = W * lx if land else W * (lx * 1.05), H * (ground + ly), min(W, H) * 0.045
                d.pieslice([cx - rr, cy - rr * 0.5, cx + rr, cy + rr * 0.5], 30, 350, fill=(110, 185, 105))
            E(d, W * (0.83 if land else 0.85), H * (ground + 0.035), 14, 14, (255, 190, 210, 255), w=0)
            for k in range(9):  # reeds
                rx = W * (0.47 + k * 0.012) if land else W * (0.22 + k * 0.022)
                top = H * (ground - 0.16 - (k % 3) * 0.03)
                d.line([rx, H * (ground + 0.02), rx + (k % 2) * 6, top], fill=(110, 150, 80), width=6)
                if k % 2 == 0:
                    d.rounded_rectangle([rx - 9, top - 4, rx + 9, top + H * 0.045], 9, fill=(150, 100, 70))
            autumn_tree(d, W, H, W * (0.1 if land else 0.12), ground - 0.04, 0.8 if land else 0.55, sw=None if land else 1.5)
            flowers(d, W, H, H * (ground + 0.03), 16, 34)
    elif kind == "bath_time":
        # Honey's cosy evening bath-time corner (ep021): lilac wall with soft bubble wallpaper and a star
        # bunting, mint tiles below, big arched window with a pink-purple sunset, a wall shelf with plain
        # shampoo bottles and a sponge, a towel rail with a fluffy yellow towel, wooden floor + round pink mat.
        # The bathtub is the "tub" prop (list it AFTER the friend in the bath): landscape x=0.42 y=0.92
        # scale 1.0 (Pip inside at x=0.42 y=0.80), vertical x=0.5 y=0.80 scale 0.85 (Pip x=0.5 y=0.70).
        L = W > H
        im = grad(W, H, (226, 205, 245), (240, 222, 248))
        d = ImageDraw.Draw(im)
        for i in range(int(40 * W * H / (1920 * 1080))):
            x, y, r = rnd.uniform(0, W), rnd.uniform(H * 0.04, H * 0.45), H * rnd.uniform(0.008, 0.016)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(250, 240, 255), width=3)
        ty = H * (0.5 if L else 0.46)
        d.rectangle([0, ty, W, H * ground], fill=(190, 235, 215))
        ts = H * (0.06 if L else 0.04)
        k = 0
        while ty + k * ts < H * ground:
            d.line([0, ty + k * ts, W, ty + k * ts], fill=(160, 215, 195), width=3); k += 1
        for xx in range(0, W + 1, int(ts)):
            d.line([xx, ty, xx, H * ground], fill=(160, 215, 195), width=3)
        d.rectangle([0, ty - 10, W, ty + 6], fill=(150, 200, 185))
        # arched sunset window (centre-left, above the tub)
        wx, wy = W * (0.42 if L else 0.5), H * (0.24 if L else 0.2)
        ww, wh = W * (0.12 if L else 0.2), H * (0.16 if L else 0.1)
        d.rounded_rectangle([wx - ww - 18, wy - wh - 18, wx + ww + 18, wy + wh + 18], int(ww * 0.6), fill=(255, 250, 240), outline=OUT, width=5)
        win = grad(int(2 * ww), int(2 * wh), (150, 120, 200), (255, 180, 170))
        wd = ImageDraw.Draw(win)
        sw, sh = win.size
        wd.ellipse([sw * 0.55, sh * 0.5, sw * 0.85, sh * 0.5 + sw * 0.3], fill=(255, 215, 130))
        wd.ellipse([-sw * 0.2, sh * 0.78, sw * 1.2, sh * 1.5], fill=(140, 120, 170))
        for (cx, cy) in ((0.2, 0.25), (0.75, 0.18)):
            cloud(wd, sw * cx, sh * cy, sh / 500, (255, 225, 235))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], int(ww * 0.55), fill=255)
        im.paste(win, (int(wx - ww), int(wy - wh)), mask)
        d = ImageDraw.Draw(im)
        d.line([wx, wy - wh, wx, wy + wh], fill=(255, 250, 240), width=10)
        d.line([wx - ww, wy + wh * 0.1, wx + ww, wy + wh * 0.1], fill=(255, 250, 240), width=10)
        # star bunting across the top
        for i in range(9):
            sx = W * (0.04 + i * 0.12)
            d.polygon(star_pts(sx, H * 0.06, H * (0.025 if L else 0.016)), fill=[(255, 200, 90), (255, 160, 190), (140, 200, 245)][i % 3])
        d.line([0, H * 0.045, W, H * 0.045], fill=(200, 160, 200), width=3)
        # wall shelf with plain bottles + a sponge (right)
        shx0, shx1, shy = W * (0.72 if L else 0.6), W * (0.94 if L else 0.96), H * (0.33 if L else 0.36)
        d.rounded_rectangle([shx0, shy, shx1, shy + H * 0.018], 6, fill=(220, 170, 120), outline=OUT, width=4)
        bw = (shx1 - shx0) / 6
        for j, c in enumerate(((255, 170, 200), (140, 200, 245), (190, 230, 150))):
            bx = shx0 + bw * (0.6 + j * 1.25)
            bh = H * (0.08 if L else 0.05) * (1 - 0.15 * (j % 2))
            d.rounded_rectangle([bx - bw * 0.42, shy - bh, bx + bw * 0.42, shy], 14, fill=c, outline=OUT, width=4)
            d.rounded_rectangle([bx - bw * 0.18, shy - bh - H * 0.02, bx + bw * 0.18, shy - bh + 4], 5, fill=(255, 255, 255), outline=OUT, width=3)
        sx = shx0 + bw * 4.8
        d.rounded_rectangle([sx - bw * 0.7, shy - H * 0.04, sx + bw * 0.7, shy], 14, fill=(255, 220, 90), outline=OUT, width=4)
        for q in range(4):
            E(d, sx - bw * 0.4 + q * bw * 0.27, shy - H * 0.022, 5, 5, (235, 185, 60, 255), w=0)
        # towel rail with a fluffy yellow towel (far left)
        rx = W * (0.1 if L else 0.13)
        ry = H * (0.4 if L else 0.36)
        d.line([rx - W * 0.06, ry, rx + W * 0.06, ry], fill=(200, 205, 215), width=10)
        d.rounded_rectangle([rx - W * (0.045 if L else 0.08), ry - 6, rx + W * (0.045 if L else 0.08), ry + H * (0.22 if L else 0.14)], 18,
                            fill=(255, 225, 120), outline=OUT, width=5)
        d.rectangle([rx - W * (0.04 if L else 0.07), ry + H * (0.16 if L else 0.1), rx + W * (0.04 if L else 0.07), ry + H * (0.18 if L else 0.112)], fill=(255, 255, 255))
        # wooden floor + round pink bath mat
        d.rectangle([0, H * ground, W, H], fill=(225, 185, 145))
        for k in range(1, 6):
            yy = H * ground + k * (H - H * ground) / 5
            d.line([0, yy, W, yy], fill=(205, 165, 125), width=3)
        d.rectangle([0, H * ground - 8, W, H * ground + 4], fill=(150, 200, 185))
        mx = W * (0.8 if L else 0.82)
        d.ellipse([mx - W * 0.1, H * (ground + 0.02), mx + W * 0.1, H * (ground + 0.1)], fill=(255, 175, 200), outline=(240, 145, 175), width=6)
    elif kind in ("sleepover_room", "sleepover_dark"):
        # Honey's sleepover bedroom (ep022): periwinkle wall with little clouds and moons, a big arched
        # night window right (Moon fits at x=0.72 y=0.47 scale 0.55 landscape / x=0.5 y=0.33 scale 0.45 vertical),
        # star bunting, bookshelf far left, a warm floor lamp, a low round bedside table (night light ON it
        # at x=0.5 y=0.735 landscape / x=0.82 y=0.66 vertical), a soft rug, and an empty wall area for shadows
        # (x≈0.3 landscape / 0.3 vertical). sleepover_dark = the same room with the lamp off: soft moonlit
        # blue, a gentle moonbeam from the window (cosy, never scary).
        land = W > H
        dark = kind == "sleepover_dark"
        im = grad(W, H, (176, 186, 236), (204, 200, 240))
        d = ImageDraw.Draw(im)
        for i in range(int(26 * W * H / (1920 * 1080))):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.1, H * (ground - 0.08))
            if rnd.random() < 0.5:
                cloud(d, x, y, H / 2600, (214, 220, 248))
            else:
                r = H * 0.014
                d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 230, 200))
                d.ellipse([x - r * 0.4, y - r * 1.1, x + r * 1.4, y + r * 0.6], fill=(194, 196, 240))
        d.rectangle([0, H * ground, W, H], fill=(196, 150, 120))
        for k in range(1, 6):
            y = H * ground + (H - H * ground) * k / 6
            d.line([0, y, W, y], fill=(176, 132, 104), width=3)
        d.rectangle([0, H * ground - 10, W, H * ground + 6], fill=(246, 240, 232))
        # arched window
        wx = W * (0.72 if land else 0.5)
        wt, wb = H * (0.13 if land else 0.12), H * (0.58 if land else 0.40)
        ww = W * (0.12 if land else 0.27)
        fr = (255, 250, 240)
        d.rounded_rectangle([wx - ww - 20, wt - 20, wx + ww + 20, wb + 20], int(ww + 20), fill=fr)
        win = grad(int(2 * ww), int(wb - wt), (30, 34, 92), (104, 82, 158))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, win.size[0] - 1, win.size[1] - 1], int(ww), fill=255)
        hills(ImageDraw.Draw(win), win.size[0], win.size[1], 0.97, 0.05, (60, 92, 125), 2)
        im.paste(win, (int(wx - ww), int(wt)), mask)
        d = ImageDraw.Draw(im)
        for _ in range(22):
            stars.append((rnd.uniform(wx - ww * 0.8, wx + ww * 0.8), rnd.uniform(wt + ww * 0.4, wb - (wb - wt) * 0.08), rnd.uniform(1.5, 3.8), rnd.uniform(0, 6.28)))
        d.line([wx, wt + ww * 0.15, wx, wb], fill=fr, width=10)
        d.line([wx - ww, (wt + wb) / 2 + H * 0.04, wx + ww, (wt + wb) / 2 + H * 0.04], fill=fr, width=10)
        d.rectangle([wx - ww - 40, wb + 12, wx + ww + 40, wb + 38], fill=fr)
        for sdir in (-1, 1):  # soft lilac curtains with tie-backs
            cx = wx + sdir * (ww + 34)
            d.polygon([(cx - 40, wt - 36), (cx + 40, wt - 36), (cx + sdir * 26 + 30, wb + 56), (cx + sdir * 26 - 30, wb + 56)], fill=(214, 170, 230))
            d.ellipse([cx + sdir * 14 - 18, (wt + wb) / 2 - 18, cx + sdir * 14 + 18, (wt + wb) / 2 + 18], fill=(255, 210, 120), outline=OUT, width=3)
        d.rectangle([wx - ww - 110, wt - 50, wx + ww + 110, wt - 34], fill=(200, 150, 120))
        # star bunting across the top
        for i in range(9):
            sx = W * (0.04 + i * 0.12)
            sy = H * 0.05 + math.sin(i * 1.3) * H * 0.006
            d.polygon(star_pts(sx, sy + H * 0.02, H * 0.018), fill=[(255, 215, 110), (255, 175, 200), (160, 210, 250)][i % 3])
        d.line([0, H * 0.05, W, H * 0.05], fill=(200, 160, 130), width=3)
        # bookshelf far left
        bx = W * (0.05 if land else 0.08)
        bw, bt = W * (0.045 if land else 0.07), H * (ground - (0.36 if land else 0.2))
        d.rectangle([bx - bw, bt, bx + bw, H * ground], fill=(180, 125, 90), outline=OUT, width=4)
        nsh = 3
        for k in range(nsh):
            y0 = bt + (H * ground - bt) * k / nsh + 8
            y1 = bt + (H * ground - bt) * (k + 1) / nsh - 8
            x = bx - bw + 10
            for j, col in enumerate(((255, 150, 150), (130, 190, 240), (255, 215, 110), (150, 210, 150), (200, 170, 240))):
                bwid = bw * 0.32
                if x + bwid > bx + bw - 8:
                    break
                d.rectangle([x, y0 + (j % 2) * 8, x + bwid, y1], fill=col, outline=OUT, width=2)
                x += bwid + 4
            d.line([bx - bw, y1 + 6, bx + bw, y1 + 6], fill=(150, 100, 70), width=6)
        # floor lamp (left of centre)
        lx = W * (0.17 if land else 0.2)
        ltop = H * (ground - (0.42 if land else 0.24))
        lr = H * (0.06 if land else 0.035)
        if not dark:
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([lx - H * 0.22, ltop - H * 0.16, lx + H * 0.22, ltop + H * 0.24], fill=(255, 225, 150, 90))
            im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(55)))
            d = ImageDraw.Draw(im)
        d.line([lx, ltop + lr, lx, H * ground - 6], fill=(150, 100, 70), width=10)
        d.ellipse([lx - lr * 0.9, H * ground - 16, lx + lr * 0.9, H * ground + 6], fill=(150, 100, 70))
        shade = (255, 236, 170) if not dark else (220, 200, 210)
        d.polygon([(lx - lr * 0.6, ltop - lr * 0.4), (lx + lr * 0.6, ltop - lr * 0.4), (lx + lr * 1.1, ltop + lr), (lx - lr * 1.1, ltop + lr)], fill=shade, outline=OUT)
        # low round bedside table (right of centre landscape / right vertical)
        tx = W * (0.5 if land else 0.82)
        tt = H * (ground - (0.12 if land else 0.08))
        tr = W * (0.06 if land else 0.11)
        d.rounded_rectangle([tx - tr * 0.18, tt, tx + tr * 0.18, H * ground], 8, fill=(205, 150, 100), outline=OUT, width=4)
        d.ellipse([tx - tr * 0.6, H * ground - 14, tx + tr * 0.6, H * ground + 8], fill=(205, 150, 100), outline=OUT, width=4)
        d.ellipse([tx - tr, tt - H * 0.014, tx + tr, tt + H * 0.014], fill=(225, 172, 112), outline=OUT, width=5)
        # soft rug
        d.ellipse([W * 0.12, H * (ground + 0.01), W * 0.88, H * (ground + (0.12 if land else 0.09))], fill=(255, 220, 232), outline=(240, 196, 210), width=6)
        if dark:
            # cosy moonlit blue: tint everything except the window, add a soft moonbeam
            arr = np.asarray(im).astype(np.float32)
            tint = np.array([0.52, 0.54, 0.80, 1.0])
            lift = np.array([30, 30, 52, 0])
            out = arr * tint + lift
            wm = np.zeros((H, W), np.float32)
            mm = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mm).rounded_rectangle([wx - ww, wt, wx + ww, wb], int(ww), fill=255)
            wm = np.asarray(mm).astype(np.float32)[..., None] / 255.0
            out = out * (1 - wm) + arr * wm
            im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
            beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(beam).polygon([(wx - ww * 0.8, wb), (wx + ww * 0.8, wb), (wx + ww * 1.6, H * (ground + 0.1)), (wx - ww * 1.9, H * (ground + 0.1))], fill=(220, 225, 255, 55))
            im.alpha_composite(beam.filter(ImageFilter.GaussianBlur(30)))
    elif kind == "frosty_garden":
        # ep023: Honey's garden on the first chilly morning: pale winter sky with a soft low sun, frosty
        # white-tipped hills, Honey's cottage (left) with a warm window and chimney smoke, a white picket
        # fence, a nearly bare tree (right) with a few last orange leaves, frost sparkles on the grass and a
        # stepping-stone path. Gentle and cosy (no snow yet). Works with "leaves": true.
        L = W > H
        im = grad(W, H, (172, 210, 242), (252, 240, 228))
        d = ImageDraw.Draw(im)
        sx, sy, sr = W * (0.6 if L else 0.66), H * (0.13 if L else 0.1), min(W, H) * 0.06
        halo = Image.new("RGBA", (W, H), (255, 245, 210, 0))
        ImageDraw.Draw(halo).ellipse([sx - sr * 2.6, sy - sr * 2.6, sx + sr * 2.6, sy + sr * 2.6], fill=(255, 245, 210, 120))
        im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 236, 170))
        for cx, cy in ((0.08, 0.08), (0.78, 0.2), (0.4, 0.05)):
            cloud(d, W * cx, H * cy, min(W, H) / 1300, (250, 252, 255))
        hills(d, W, H, ground - 0.165, 0.07, (240, 246, 252), 31)
        hills(d, W, H, ground - 0.15, 0.07, (178, 205, 180), 31)
        hills(d, W, H, ground - 0.055, 0.035, (236, 244, 248), 33)
        hills(d, W, H, ground - 0.045, 0.035, (160, 200, 150), 33)
        # cottage (left)
        cx0, cx1 = (W * 0.015, W * 0.25) if L else (W * -0.04, W * 0.36)
        top = H * (ground - (0.36 if L else 0.21))
        cw = cx1 - cx0
        d.rectangle([cx0 + cw * 0.62, top - H * (0.17 if L else 0.1), cx0 + cw * 0.76, top], fill=(190, 120, 100), outline=OUT, width=5)
        for k, (dx, dy, r) in enumerate(((0.69, 0.21, 0.025), (0.74, 0.25, 0.032), (0.82, 0.29, 0.04))):
            rr = H * r * (1 if L else 0.65)
            yy = top - H * (dy if L else dy * 0.62)
            d.ellipse([cx0 + cw * dx - rr, yy - rr, cx0 + cw * dx + rr, yy + rr], fill=(240, 240, 248))
        d.polygon([(cx0 - cw * 0.08, top + H * 0.01), (cx0 + cw * 0.5, top - H * (0.13 if L else 0.08)), (cx1 + cw * 0.08, top + H * 0.01)],
                  fill=(205, 105, 95), outline=OUT, width=6)
        d.line([(cx0 - cw * 0.06, top + H * 0.004), (cx0 + cw * 0.5, top - H * (0.123 if L else 0.074)), (cx1 + cw * 0.06, top + H * 0.004)], fill=(255, 255, 255), width=8)
        d.rectangle([cx0, top, cx1, H * ground], fill=(255, 238, 212), outline=OUT, width=6)
        dx0, dx1 = cx0 + cw * 0.56, cx0 + cw * 0.86
        d.rounded_rectangle([dx0, H * ground - (H * 0.2 if L else H * 0.12), dx1, H * ground], 30, fill=(110, 160, 220), outline=OUT, width=5)
        d.ellipse([dx1 - cw * 0.08, H * ground - H * (0.1 if L else 0.06), dx1 - cw * 0.04, H * ground - H * (0.1 if L else 0.06) + cw * 0.04], fill=(255, 215, 90))
        wx0, wx1 = cx0 + cw * 0.12, cx0 + cw * 0.44
        wy0 = top + H * (0.06 if L else 0.035)
        wy1 = wy0 + (wx1 - wx0) * 0.9
        g = Image.new("RGBA", (W, H), (255, 220, 130, 0))
        ImageDraw.Draw(g).ellipse([wx0 - cw * 0.15, wy0 - cw * 0.15, wx1 + cw * 0.15, wy1 + cw * 0.15], fill=(255, 220, 130, 80))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(25)))
        d = ImageDraw.Draw(im)
        d.rectangle([wx0, wy0, wx1, wy1], fill=(255, 222, 140), outline=OUT, width=5)
        d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=OUT, width=4)
        d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=OUT, width=4)
        for k in range(6):  # frost in the window corners
            d.ellipse([wx0 + 4 + k * 6, wy1 - 16 - k * 3, wx0 + 16 + k * 6, wy1 - 4 - k * 3], fill=(255, 255, 255))
        # white picket fence
        fy0, fy1 = H * (ground - (0.12 if L else 0.075)), H * (ground - 0.005)
        fx0 = cx1 + W * 0.01
        fx1 = W * (0.84 if L else 0.8)
        d.rectangle([fx0, fy0 + (fy1 - fy0) * 0.3, fx1, fy0 + (fy1 - fy0) * 0.42], fill=(250, 250, 255), outline=OUT, width=3)
        d.rectangle([fx0, fy0 + (fy1 - fy0) * 0.66, fx1, fy0 + (fy1 - fy0) * 0.78], fill=(250, 250, 255), outline=OUT, width=3)
        step = W * (0.035 if L else 0.06)
        x = fx0
        while x < fx1:
            pw = step * 0.5
            d.polygon([(x, fy1), (x, fy0 + pw * 0.5), (x + pw / 2, fy0), (x + pw, fy0 + pw * 0.5), (x + pw, fy1)], fill=(255, 255, 255), outline=OUT, width=3)
            x += step
        # nearly bare tree (right) with a few last leaves
        tx = W * (0.9 if L else 0.86)
        tb = H * ground
        tt = H * (ground - (0.62 if L else 0.4))
        tw = W * (0.022 if L else 0.04)
        d.polygon([(tx - tw, tb), (tx - tw * 0.6, tt + H * 0.1), (tx + tw * 0.6, tt + H * 0.1), (tx + tw, tb)], fill=(140, 95, 75), outline=OUT)
        for (ax, ay, bx2, by2) in ((0, 0.15, -0.09, 0.0), (0, 0.22, 0.07, 0.08), (0, 0.12, 0.02, -0.02), (-0.05, 0.07, -0.12, 0.02), (0.04, 0.14, 0.1, 0.1)):
            x1, y1 = tx + ax * W * (1 if L else 1.6), tt + H * ay
            x2, y2 = tx + bx2 * W * (1 if L else 1.6), tt + H * by2
            d.line([(tx, y1 + H * 0.06), (x2, y2)], fill=(140, 95, 75), width=int(tw * 0.5))
            d.line([(x2 - 6, y2 + 2), (x2 + 18, y2 - 16)], fill=(255, 255, 255), width=5)
            _leaf(d, x2, y2 + H * 0.012, H * 0.03, ["orange", "red", "yellow"][int(abs(bx2) * 100) % 3], 0.6, ol=True)
        # frosty bushes
        for (bx, sc) in (((0.33 if L else 0.4), 1.0), ((0.72 if L else 0.66), 0.8)):
            bxx, byy = W * bx, H * (ground - 0.005)
            r = H * 0.045 * sc * (1 if L else 0.7)
            for (ox, oy, rr) in ((-1.1, 0, 0.8), (0, -0.4, 1.0), (1.1, 0, 0.8)):
                d.ellipse([bxx + ox * r - rr * r, byy + oy * r - rr * r, bxx + ox * r + rr * r, byy + oy * r + rr * r], fill=(120, 175, 130))
            for (ox, oy) in ((-1.3, -0.6), (-0.3, -1.25), (0.5, -1.2), (1.3, -0.6)):
                d.ellipse([bxx + ox * r - r * 0.35, byy + oy * r - r * 0.18, bxx + ox * r + r * 0.35, byy + oy * r + r * 0.18], fill=(250, 252, 255))
        # grass with frost sparkles + stepping stones
        d.rectangle([0, H * ground, W, H], fill=(165, 208, 158))
        for k in range(5):
            yy = H * (ground + 0.02 + k * (1 - ground) / 5.2)
            xx = W * (0.5 + 0.08 * math.sin(k * 1.3))
            rx = W * (0.05 + k * 0.012) * (1 if L else 1.6)
            d.ellipse([xx - rx, yy - H * 0.012, xx + rx, yy + H * 0.016 + k * 3], fill=(215, 215, 225), outline=(180, 180, 195), width=3)
            d.ellipse([xx - rx * 0.7, yy - H * 0.01, xx + rx * 0.2, yy], fill=(250, 252, 255))
        for i in range(int(160 * W * H / (1920 * 1080))):
            x, y = rnd.uniform(0, W), rnd.uniform(H * ground, H)
            r = rnd.uniform(2, 5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 253, 255))
            if i % 9 == 0:
                d.line([(x - 12, y), (x + 12, y)], fill=(255, 255, 255), width=3)
                d.line([(x, y - 12), (x, y + 12)], fill=(255, 255, 255), width=3)
    elif kind == "cosy_hall":
        # ep023: Honey's cosy front hall: warm peach wall with a heart garland, a coat rail with Mama's big
        # purple hat, a green scarf and a lilac coat, a wooden bench (left), a front door (right) with a round
        # frosty window, wooden floor and a soft blue striped runner rug front-centre.
        L = W > H
        im = grad(W, H, (255, 224, 202), (255, 236, 218))
        d = ImageDraw.Draw(im)
        for i in range(int(40 * W * H / (1920 * 1080))):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.03, H * (ground - 0.25))
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 205, 185))
        wy = H * (ground - (0.22 if L else 0.13))
        d.rectangle([0, wy, W, H * ground], fill=(240, 196, 168))
        for xx in range(0, W, int(W * (0.06 if L else 0.1))):
            d.rounded_rectangle([xx + 14, wy + 18, xx + W * (0.06 if L else 0.1) - 14, H * ground - 18], 10, outline=(225, 175, 145), width=4)
        d.rectangle([0, wy - 8, W, wy + 6], fill=(205, 150, 115))
        # heart garland
        gy = H * (0.07 if L else 0.1)
        d.line([(0, gy), (W, gy)], fill=(200, 150, 120), width=3)
        for i in range(9):
            hx = W * (0.05 + i * 0.112)
            hy = gy + H * 0.012 + (i % 2) * H * 0.008
            hs = H * (0.016 if L else 0.011)
            col = [(255, 130, 160), (255, 200, 90), (130, 190, 245)][i % 3]
            d.polygon([(hx - hs, hy), (hx, hy + hs * 1.3), (hx + hs, hy)], fill=col)
            d.ellipse([hx - hs, hy - hs * 0.6, hx, hy + hs * 0.35], fill=col)
            d.ellipse([hx, hy - hs * 0.6, hx + hs, hy + hs * 0.35], fill=col)
        # front door (right)
        dx0, dx1 = (W * 0.8, W * 0.97) if L else (W * 0.76, W * 1.02)
        dy0 = H * (0.2 if L else 0.4)
        d.rounded_rectangle([dx0 - 16, dy0 - 16, dx1 + 16, H * ground + 4], 30, fill=(205, 150, 115), outline=OUT, width=5)
        d.rounded_rectangle([dx0, dy0, dx1, H * ground], 24, fill=(120, 175, 225), outline=OUT, width=5)
        cxw, cyw, rw = (dx0 + dx1) / 2, dy0 + (dx1 - dx0) * 0.42, (dx1 - dx0) * 0.3
        win = grad(int(2 * rw), int(2 * rw), (180, 215, 245), (245, 248, 255))
        mask = Image.new("L", win.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, win.size[0], win.size[1]], fill=255)
        im.paste(win, (int(cxw - rw), int(cyw - rw)), mask)
        d = ImageDraw.Draw(im)
        d.ellipse([cxw - rw, cyw - rw, cxw + rw, cyw + rw], outline=OUT, width=6)
        for (ox, oy) in ((-0.5, 0.5), (0.4, 0.55), (-0.1, 0.7), (0.6, -0.1)):
            d.ellipse([cxw + ox * rw - 8, cyw + oy * rw - 8, cxw + ox * rw + 8, cyw + oy * rw + 8], fill=(255, 255, 255))
        d.ellipse([dx0 + (dx1 - dx0) * 0.12 - 12, H * (ground - 0.18 if L else ground - 0.1) - 12, dx0 + (dx1 - dx0) * 0.12 + 12, H * (ground - 0.18 if L else ground - 0.1) + 12], fill=(255, 215, 90), outline=OUT, width=3)
        # coat rail with pegs
        rx0, rx1 = (W * 0.3, W * 0.7) if L else (W * 0.08, W * 0.68)
        ry = H * (0.27 if L else 0.21)
        d.rounded_rectangle([rx0, ry - H * 0.018, rx1, ry + H * 0.018], 10, fill=(205, 150, 115), outline=OUT, width=4)
        pegs = [rx0 + (rx1 - rx0) * f for f in (0.15, 0.5, 0.85)]
        for px in pegs:
            d.ellipse([px - 12, ry - 12, px + 12, ry + 12], fill=(255, 215, 120), outline=OUT, width=3)
        u = H * (1 if L else 0.62)
        # Mama's big purple hat on peg 1
        px = pegs[0]
        d.chord([px - u * 0.07, ry - u * 0.02, px + u * 0.07, ry + u * 0.16], 180, 360, fill=(170, 120, 215), outline=OUT, width=5)
        d.rounded_rectangle([px - u * 0.09, ry + u * 0.05, px + u * 0.09, ry + u * 0.08], 12, fill=(200, 160, 240), outline=OUT, width=5)
        d.ellipse([px - u * 0.016, ry - u * 0.05, px + u * 0.016, ry - u * 0.018], fill=(255, 255, 255), outline=OUT, width=3)
        # green scarf on peg 2
        px = pegs[1]
        for sgn in (-1, 1):
            d.rounded_rectangle([px + sgn * u * 0.03 - u * 0.022, ry, px + sgn * u * 0.03 + u * 0.022, ry + u * (0.19 if sgn < 0 else 0.15)], 10, fill=(110, 195, 125), outline=OUT, width=4)
            for k in (0.06, 0.11):
                d.rectangle([px + sgn * u * 0.03 - u * 0.02, ry + u * k, px + sgn * u * 0.03 + u * 0.02, ry + u * (k + 0.015)], fill=(255, 255, 255))
        d.chord([px - u * 0.055, ry - u * 0.03, px + u * 0.055, ry + u * 0.05], 180, 360, fill=(110, 195, 125), outline=OUT, width=4)
        # lilac coat on peg 3
        px = pegs[2]
        d.polygon([(px - u * 0.04, ry + u * 0.01), (px + u * 0.04, ry + u * 0.01), (px + u * 0.08, ry + u * 0.24), (px - u * 0.08, ry + u * 0.24)], fill=(205, 180, 240), outline=OUT, width=5)
        d.line([(px, ry + u * 0.03), (px, ry + u * 0.24)], fill=OUT, width=3)
        for k in (0.08, 0.14, 0.2):
            d.ellipse([px + u * 0.012 - 7, ry + u * k - 7, px + u * 0.012 + 7, ry + u * k + 7], fill=(255, 215, 120), outline=OUT, width=2)
        # wooden bench (left) with a cushion
        bx0, bx1 = (W * 0.02, W * 0.22) if L else (W * -0.02, W * 0.28)
        by = H * (ground - (0.1 if L else 0.065))
        d.rounded_rectangle([bx0, by, bx1, by + H * 0.025], 8, fill=(185, 125, 90), outline=OUT, width=4)
        for x in (bx0 + 16, bx1 - 34):
            d.rectangle([x, by + H * 0.02, x + 18, H * ground + 6], fill=(165, 110, 80), outline=OUT, width=3)
        d.rounded_rectangle([bx0 + (bx1 - bx0) * 0.15, by - H * 0.03, bx0 + (bx1 - bx0) * 0.6, by + 4], 18, fill=(255, 165, 190), outline=OUT, width=4)
        # floor + runner rug
        d.rectangle([0, H * ground, W, H], fill=(205, 150, 110))
        for k in range(1, 6):
            yy = H * ground + k * (H - H * ground) / 5
            d.line([(0, yy), (W, yy)], fill=(185, 132, 95), width=3)
        rx0, rx1 = W * (0.24 if L else 0.1), W * (0.76 if L else 0.9)
        d.rounded_rectangle([rx0, H * (ground + 0.02), rx1, H * 0.985], 26, fill=(150, 200, 245), outline=(110, 165, 225), width=6)
        for k in range(1, 5):
            xx = rx0 + k * (rx1 - rx0) / 5
            d.line([(xx, H * (ground + 0.03)), (xx, H * 0.975)], fill=(255, 255, 255), width=10)
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
