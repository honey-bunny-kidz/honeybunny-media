"""Render a Honey Bunny Kidz episode JSON into an MP4 (landscape or vertical)."""
import json, math, os, re, subprocess, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import art, tts, thumbnail
COVER = 0.5  # seconds the thumbnail is shown as the opening frame

FPS = 24
SR = tts.SR
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
VOICES = {"narrator": ("af_heart", 0.84), "honey": ("af_sky", 0.92), "mama": ("af_bella", 0.86),
          "dotty": ("af_nicole", 0.95), "ollie": ("bm_fable", 0.86), "moon": ("bm_george", 0.82), "mimi": ("af_sky", 0.90, 1.13),
          "lulu": ("bf_lily", 0.90, 1.12), "pip": ("am_puck", 0.92, 1.12),
          "pumpkinpip": ("am_puck", 0.92, 1.12)}


def sentences(t):
    parts = re.split(r"(?<=[.!?])\s+", t.strip())
    out, cur = [], ""
    for p in parts:  # merge very short bits so subtitles don't flicker
        cur = (cur + " " + p).strip()
        if len(cur) > 25:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return out


def music(seconds):
    """Original gentle music-box lullaby loop (3/4, ~66 bpm)."""
    beat = 60 / 66
    f = lambda n: 440 * 2 ** ((n - 69) / 12)
    mel = [72, 76, 79, 77, 76, 74, 72, 74, 76, 74, 71, 67, 69, 72, 76, 74, 72, 71, 72, 76, 79, 81, 79, 76,
           77, 76, 74, 72, 71, 74, 72, 67, 72, 0, 0, 0]
    bass = [48, 55, 52, 53, 48, 55, 43, 50, 45, 52, 50, 43]  # one per bar
    n = len(mel)
    L = int(n * beat * SR)
    buf = np.zeros(L)
    t = np.arange(int(beat * 3 * SR)) / SR

    def note(start, freq, dur, amp):
        tt = t[: int(dur * SR)]
        env = np.exp(-tt * 3.2) * (1 - np.exp(-tt * 200))
        w = (np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(4 * np.pi * freq * tt) + 0.12 * np.sin(6 * np.pi * freq * tt)) * env * amp
        s = int(start * SR)
        e = min(L, s + len(w))
        buf[s:e] += w[: e - s]

    for i, m in enumerate(mel):
        if m:
            note(i * beat, f(m), beat * 2.5, 0.25)
    for b, m in enumerate(bass):
        for k, off in enumerate((0, 7, 12)):
            note((b * 3 + k) * beat, f(m + off), beat * 2.5, 0.12 if k else 0.16)
    reps = int(math.ceil(seconds * SR / L)) + 1
    out = np.tile(buf, reps)[: int(seconds * SR)]
    fade = int(3 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[:SR] *= np.linspace(0, 1, SR)
    return out / (np.abs(out).max() + 1e-9)


def sfx(kind, dur=1.8):
    """Soft, original synthesized nature sounds (no samples)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    if kind == "cricket":  # gentle chirp-chirp-chirp
        gate = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.3, 0.5):
            for k in range(3):
                s0 = int((c0 + k * 0.045) * SR)
                L = int(0.028 * SR)
                gate[s0:s0 + L] += np.hanning(L)
        a = np.sin(2 * np.pi * 4300 * t) * gate * 0.22
    elif kind == "wind":  # soft whoosh: band-passed noise with slow swells
        x = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        x *= np.exp(-((f - 450) / 260) ** 2)
        a = np.fft.irfft(x, n)
        a /= np.abs(a).max() + 1e-9
        a *= (0.15 + 0.85 * np.sin(np.pi * t / dur) ** 2) * 0.45
    elif kind == "frog":  # cute two-part "rib-bit" croaks
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.35, 0.6):
            for k, (f0, L) in enumerate(((210, 0.11), (260, 0.13))):
                s0 = int((c0 + k * 0.16) * SR)
                tt = np.arange(int(L * SR)) / SR
                fr = f0 * (1 + 0.25 * tt / L)
                ph = 2 * np.pi * np.cumsum(fr) / SR
                w = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * (0.55 + 0.45 * np.sin(2 * np.pi * 45 * tt))
                w *= np.hanning(len(tt)) * 0.3
                a[s0:s0 + len(w)] += w[: max(0, min(len(w), n - s0))]
    elif kind == "owl":  # soft hoo... hoo
        a = np.zeros(n)
        for c0, L in ((0.05, 0.45), (0.75, 0.6)):
            s0 = int(c0 * SR)
            tt = np.arange(int(L * SR)) / SR
            fr = 390 * (1 - 0.08 * tt / L) * (1 + 0.01 * np.sin(2 * np.pi * 6 * tt))
            w = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tt / L) ** 1.5 * 0.4
            a[s0:s0 + len(w)] += w[: max(0, min(len(w), n - s0))]
    else:
        raise ValueError(kind)
    fade = int(0.05 * SR)
    a[:fade] *= np.linspace(0, 1, fade)
    a[-fade:] *= np.linspace(1, 0, fade)
    return a


def build_timeline(ep):
    """Synthesize all lines; return scenes with absolute timing and the voice track."""
    t, voice, scenes = 0.0, [], []
    for sc in ep["scenes"]:
        start = t
        chunks = []
        t += sc.get("lead", 0.9)
        for ln in sc["lines"]:
            if ln.get("sfx"):  # sound effect; optional "text" is shown as a caption only
                a = sfx(ln["sfx"], ln.get("dur", 1.8))
                chunks.append(dict(who=ln.get("who", "sfx"), text=ln.get("text", ""), t0=t, t1=t + len(a) / SR, audio=a))
                t += len(a) / SR + ln.get("pause", 0.6)
                continue
            v, sp, *pt = VOICES[ln["who"]]
            for k, s in enumerate(sentences(ln["text"])):
                a = tts.synth(s, v, sp, pt[0] if pt else 1.0)
                chunks.append(dict(who=ln["who"], text=s, t0=t, t1=t + len(a) / SR, audio=a))
                t += len(a) / SR + (0.35 if k < len(sentences(ln["text"])) - 1 else ln.get("pause", 0.75))
        t += sc.get("tail", 1.0)
        scenes.append(dict(sc, t0=start, t1=t, chunks=chunks))
    track = np.zeros(int((t + 0.5) * SR))
    for sc in scenes:
        for c in sc["chunks"]:
            s = int(c["t0"] * SR)
            track[s:s + len(c["audio"])] += c["audio"]
            # mouth levels per video frame
            a = np.abs(c["audio"])
            n = max(1, int(len(a) / SR * FPS))
            rms = np.array([a[int(i * SR / FPS): int((i + 1) * SR / FPS)].mean() if int(i * SR / FPS) < len(a) else 0 for i in range(n)])
            hi = np.percentile(rms, 85) + 1e-6
            c["mouth"] = np.where(rms > hi * 0.7, 2, np.where(rms > hi * 0.25, 1, 0))
            del c["audio"]
    return scenes, track, t


def text_box(text, W, H, vertical):
    fs = 58 if vertical else 46
    font = ImageFont.truetype(FONT, fs)
    lines = textwrap.wrap(text, 24 if vertical else 44)
    lh = int(fs * 1.25)
    bw = max(font.getlength(l) for l in lines) + 70
    bh = lh * len(lines) + 40
    im = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], 30, fill=(40, 25, 60, 165))
    for i, l in enumerate(lines):
        x = (bw - font.getlength(l)) / 2
        d.text((x + 2, 22 + i * lh + 3), l, font=font, fill=(0, 0, 0, 120))
        d.text((x, 22 + i * lh), l, font=font, fill=(255, 250, 235, 255))
    return im


def title_card(text, sub, W, H, vertical):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fs = 96 if vertical else 104
    font = ImageFont.truetype(FONT, fs)
    lines = textwrap.wrap(text, 14 if vertical else 24)
    y = H * (0.12 if vertical else 0.08)
    for l in lines:
        x = (W - font.getlength(l)) / 2
        for dx in range(-6, 7, 3):
            for dy in range(-6, 7, 3):
                d.text((x + dx, y + dy), l, font=font, fill=(150, 60, 110, 255))
        d.text((x, y), l, font=font, fill=(255, 245, 200, 255))
        y += fs * 1.15
    if sub:
        f2 = ImageFont.truetype(FONT, 48)
        x = (W - f2.getlength(sub)) / 2
        d.text((x + 2, y + 12), sub, font=f2, fill=(0, 0, 0, 120))
        d.text((x, y + 10), sub, font=f2, fill=(255, 255, 255, 255))
    return im


def render(ep_path, out_path, vertical=False):
    ep = json.load(open(ep_path))
    W, H = (1080, 1920) if vertical else (1920, 1080)
    scenes, voice, total = build_timeline(ep)
    print("duration", round(total, 1), "s; unknown words:", sorted(tts.MISSING), flush=True)
    mus = music(len(voice) / SR + 0.1)[: len(voice)]
    mus = np.pad(mus, (0, len(voice) - len(mus)))
    mix = voice / (np.abs(voice).max() + 1e-9) * 0.92 + mus * 0.11
    thumb_path = re.sub(r'\.mp4$', '', out_path) + '_thumb.jpg'
    thumbnail.make(ep, thumb_path, vertical=vertical)
    cover = Image.open(thumb_path).convert('RGB').resize((W, H))
    mix = np.concatenate([np.zeros(int(COVER * SR)), mix])
    tts.save_wav(out_path + ".wav", mix / np.abs(mix).max() * 0.95)

    cache_bg, cache_spr, cache_txt = {}, {}, {}
    for sc in scenes:
        if sc["bg"] not in cache_bg:
            cache_bg[sc["bg"]] = art.background(sc["bg"], W, H)
        for c in sc.get("cast", []):
            key = (c["id"], c.get("scale", 1.0))
            if key not in cache_spr:
                spr = art.sprites(c["id"], H, c.get("scale", 1.0) * (0.85 if vertical else 1))
                cache_spr[key] = spr
        sc["overlay"] = title_card(sc["title"], sc.get("subtitle"), W, H, vertical) if sc.get("title") else None

    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", out_path + ".wav", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", os.environ.get("HB_CRF", "21"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                           "-af", "loudnorm=I=-16:TP=-1.5", "-shortest", "-movflags", "+faststart", out_path],
                          stdin=subprocess.PIPE)
    ground = 0.74 if vertical else 0.86
    for _ in range(int(COVER * FPS)):
        ff.stdin.write(cover.tobytes())
    nframes = int(total * FPS)
    si = 0
    for fi in range(nframes):
        t = fi / FPS
        while si < len(scenes) - 1 and t >= scenes[si]["t1"]:
            si += 1
        sc = scenes[si]
        bg, fg, stars = cache_bg[sc["bg"]]
        frame = bg.copy()
        d = ImageDraw.Draw(frame)
        for (x, y, r, ph) in stars:
            b = 0.55 + 0.45 * math.sin(t * 1.6 + ph)
            rr = r * (0.8 + 0.4 * b)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 250, int(200 + 55 * b), int(255 * b)))
        cur = next((c for c in sc["chunks"] if c["t0"] <= t < c["t1"]), None)
        for k, c in enumerate(sc.get("cast", [])):
            spr = cache_spr[(c["id"], c.get("scale", 1.0))]
            eyes = "closed" if c.get("sleep") else "open"
            ph = (k * 1.7 + len(c["id"])) % 4.0
            if not c.get("sleep") and ((t + ph) % 4.2) < 0.14:
                eyes = "closed"
            m = 0
            if cur is not None and cur["who"] == c["id"]:
                j = int((t - cur["t0"]) * FPS)
                m = int(cur["mouth"][min(j, len(cur["mouth"]) - 1)])
            im = spr[(eyes, m)]
            if c.get("flip"):
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            bob = 0 if c.get("sleep") else math.sin(t * 2.2 + ph) * H * 0.005
            if cur is not None and cur["who"] == c["id"]:
                bob += math.sin(t * 9) * H * 0.003
            x = int(c["x"] * W - im.width / 2)
            y = int(c.get("y", ground) * H - im.height + bob)
            if c.get("glow"):  # soft pulsing highlight behind a found object
                gk = ("glow", im.width, im.height)
                if gk not in cache_spr:
                    g = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0))
                    ImageDraw.Draw(g).ellipse([im.width * 0.35, im.height * 0.35, im.width * 1.65, im.height * 1.65], fill=(255, 240, 150, 210))
                    cache_spr[gk] = g.filter(ImageFilter.GaussianBlur(max(6, im.width // 10)))
                g = cache_spr[gk]
                pul = 0.75 + 0.25 * math.sin(t * 4)
                ga = g.copy(); ga.putalpha(Image.eval(g.getchannel("A"), lambda v, p=pul: int(v * p)))
                frame.alpha_composite(ga, (max(0, x - im.width // 2), max(0, y - im.height // 2)))
            frame.alpha_composite(im, (max(-im.width + 1, x), max(-im.height + 1, y)))
        if fg is not None:
            frame.alpha_composite(fg)
        if sc["overlay"] is not None:
            frame.alpha_composite(sc["overlay"])
        if cur is not None and cur["text"] and not sc.get("title"):
            if cur["text"] not in cache_txt:
                cache_txt[cur["text"]] = text_box(cur["text"], W, H, vertical)
            tb = cache_txt[cur["text"]]
            frame.alpha_composite(tb, ((W - tb.width) // 2, int(H * 0.30) if vertical else int(H * 0.97 - tb.height)))
        # fades at scene edges
        a = min(1, (t - sc["t0"]) / 0.5, (sc["t1"] - t) / 0.5)
        rgb = frame.convert("RGB")
        if a < 1:
            rgb = Image.eval(rgb, lambda v, a=max(a, 0): int(v * a))
        ff.stdin.write(rgb.tobytes())
        if fi % (FPS * 30) == 0:
            print(f"{t:.0f}s / {total:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], vertical=len(sys.argv) > 3 and sys.argv[3] == "vertical")
