"""Eye-catching thumbnails for Honey Bunny Kidz videos.

Episode JSON may contain:
  "thumbnail": {"text": "Can't Sleep?", "badge": "Bedtime Story", "bg": "night",
                "cast": [{"id": "honey", "mouth": 2}, {"id": "ollie"}]}
Missing fields fall back to the episode title / first non-title scene.
"""
import json, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import art

FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
BADGE_COLORS = {"bedtime": (120, 90, 220), "rhyme": (240, 110, 60), "adventure": (40, 170, 120), "kids": (30, 150, 215)}


def _outlined(d, xy, text, font, fill, outline, width):
    d.text(xy, text, font=font, fill=fill, stroke_width=width, stroke_fill=outline)


def _fit_lines(text, max_w, max_h, max_lines=3, start=190):
    words = text.upper()
    for size in range(start, 40, -6):
        font = ImageFont.truetype(FONT, size)
        for wrap in range(6, 30):
            lines = textwrap.wrap(words, wrap, break_long_words=False)
            if len(lines) <= max_lines and max(font.getlength(l) for l in lines) <= max_w:
                if len(lines) * size * 1.05 <= max_h:
                    return font, lines
                break
    return ImageFont.truetype(FONT, 40), textwrap.wrap(words, 20)


def make(ep, out_path, vertical=False):
    W, H = (1080, 1920) if vertical else (1280, 720)
    th = ep.get("thumbnail", {})
    scene = next((s for s in ep["scenes"] if not s.get("title")), ep["scenes"][0])
    bg_kind = th.get("bg", scene["bg"])
    cast = th.get("cast") or [{"id": c["id"]} for c in scene.get("cast", []) if c["id"] != "moon"][:3]
    text = th.get("text", ep["title"])
    badge = th.get("badge", "Bedtime Story")

    bg, _, stars = art.background(bg_kind, W, H)
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(bg)
    for (x, y, r, _) in stars:
        d.ellipse([x - r * 1.6, y - r * 1.6, x + r * 1.6, y + r * 1.6], fill=(255, 250, 220))
    # soft spotlight behind characters
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gx, gy = (W * 0.70, H * 0.58) if not vertical else (W * 0.5, H * 0.66)
    ImageDraw.Draw(glow).ellipse([gx - W * 0.33, gy - H * 0.38, gx + W * 0.33, gy + H * 0.38], fill=(255, 240, 200, 120))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))

    # characters, big and expressive
    n = len(cast)
    ref = H if not vertical else W * 1.25
    for i, c in enumerate(cast):
        scale = c.get("scale", 1.0) * (1.45 if i == 0 else 1.15)
        spr = art.sprites(c["id"], ref, scale)[("open", c.get("mouth", 2 if i == 0 else 0))]
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT) if c.get("flip") else spr
        if not vertical:
            cx = W * (0.72 + (i - (n - 1) / 2) * 0.22)
            bottom = H * (1.02 if c["id"] != "ollie" else 0.95)
        else:
            cx = W * (0.5 + (i - (n - 1) / 2) * 0.34)
            bottom = H * 0.97
        if i == 0 and n > 1:  # star of the show sits in front
            continue
        bg.alpha_composite(spr, (int(cx - spr.width / 2), int(bottom - spr.height)))
    if n > 1:  # draw the main character last (on top)
        c = cast[0]
        spr = art.sprites(c["id"], ref, c.get("scale", 1.0) * 1.45)[("open", c.get("mouth", 2))]
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT) if c.get("flip") else spr
        cx = W * (0.72 - (n - 1) / 2 * 0.22) if not vertical else W * (0.5 - (n - 1) / 2 * 0.34)
        bg.alpha_composite(spr, (int(cx - spr.width / 2), int(H * (1.02 if not vertical else 0.97) - spr.height)))
    elif n == 1:
        c = cast[0]
        spr = art.sprites(c["id"], ref, c.get("scale", 1.0) * 1.45)[("open", c.get("mouth", 2))]
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT) if c.get("flip") else spr
        cx = W * 0.70 if not vertical else W * 0.5
        bg.alpha_composite(spr, (int(cx - spr.width / 2), int(H * (1.02 if not vertical else 0.97) - spr.height)))

    d = ImageDraw.Draw(bg)
    # big title text
    if not vertical:
        box = (40, 125, W * 0.47, H * 0.60)
    else:
        box = (70, 250, W - 70, H * 0.40)
    font, lines = _fit_lines(text, box[2] - box[0], box[3] - box[1], start=180 if not vertical else 240)
    y = box[1]
    for l in lines:
        x = box[0] if not vertical else (W - font.getlength(l)) / 2
        _outlined(d, (x + 6, y + 8), l, font, (60, 20, 50), (60, 20, 50), 16)  # drop shadow
        _outlined(d, (x, y), l, font, (255, 222, 60), (110, 30, 80), 14)
        y += font.size * 1.05

    # badge (story type)
    key = next((k for k in BADGE_COLORS if k in badge.lower()), "bedtime")
    bf = ImageFont.truetype(FONT, 44 if not vertical else 58)
    bw, bh = bf.getlength(badge) + 60, bf.size + 34
    bx, by = (40, 34) if not vertical else ((W - bw) / 2, 120)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], bh / 2, fill=BADGE_COLORS[key], outline=(255, 255, 255), width=5)
    d.text((bx + 30, by + 12), badge, font=bf, fill=(255, 255, 255))

    # brand tag
    tf = ImageFont.truetype(FONT, 34 if not vertical else 46)
    brand = "🐰 Honey Bunny Kidz".replace("🐰 ", "")
    tw = tf.getlength(brand) + 50
    tx, ty = (40, H - 80) if not vertical else ((W - tw) / 2, H * 0.43)
    if not vertical:
        d.rounded_rectangle([tx, ty, tx + tw, ty + 58], 29, fill=(255, 120, 170), outline=(255, 255, 255), width=4)
        d.text((tx + 25, ty + 6), brand, font=tf, fill=(255, 255, 255))
    else:
        d.rounded_rectangle([tx, ty, tx + tw, ty + 72], 36, fill=(255, 120, 170), outline=(255, 255, 255), width=4)
        d.text((tx + 25, ty + 8), brand, font=tf, fill=(255, 255, 255))

    bg.convert("RGB").save(out_path, "JPEG", quality=92)
    return out_path


if __name__ == "__main__":
    ep = json.load(open(sys.argv[1]))
    make(ep, sys.argv[2], vertical=len(sys.argv) > 3 and sys.argv[3] == "vertical")
    print("saved", sys.argv[2])
