"""Render a Honey Bunny Kidz episode JSON into an MP4 (landscape or vertical)."""
import json, math, os, re, subprocess, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import art, tts, thumbnail
COVER = 0.5  # seconds the thumbnail is shown as the opening frame

FPS = 30
SR = tts.SR
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
VOICES = {"narrator": ("hb_narr", 0.90, 1.06), "mama": ("af_bella", 0.88, 1.03),   # grown-ups: warm parent voices
          "ollie": ("bm_fable", 0.90, 1.07), "moon": ("bm_george", 0.84, 1.02),
          # children: soft kid voices (blended with breathy af_nicole, pitched up, gently low-passed)
          "honey": ("kid_honey", 0.90, 1.27), "lulu": ("kid_lulu", 0.88, 1.22), "mimi": ("kid_mimi", 0.88, 1.30),
          "pip": ("kid_pip", 0.92, 1.30), "dotty": ("kid_dotty", 0.90, 1.30), "cloudy": ("kid_cloudy", 0.86, 1.20)}
KIDS = {"honey", "lulu", "mimi", "pip", "dotty", "cloudy"}
# costume / variant sprites speak with the base character's voice
for _k, _base in {"honey_berry": "honey", "honey_pj": "honey", "honey_rain": "honey", "pumpkinpip": "pip", "pip_fire": "pip",
                  "pip_drip": "pip", "pip_captain": "pip", "pip_leafy": "pip", "mimi_star": "mimi", "mimi_nobell": "mimi",
                  "dotty_beads": "dotty", "lulu_foam": "lulu", "cloudy_light": "cloudy",
                  "pip_muddy": "pip", "pip_bubbly": "pip", "pip_towel": "pip", "pip_pj": "pip",
                  "pip_cosy": "pip", "pip_elbow": "pip", "pip_bighat": "pip", "pip_soapy": "pip", "honey_cosy": "honey"}.items():
    VOICES[_k] = VOICES[_base]
    if _base in KIDS:
        KIDS.add(_k)


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


def phrases(text, max_words):
    """Split one spoken sentence into short caption phrases (1-2 lines each), breaking at punctuation first."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?,;:\u2014])\s+", text) if p.strip()]
    merged = []
    for p in parts:  # glue very short bits to the previous phrase when it still fits
        prev_end = merged and merged[-1][-1] in ".!?"
        if merged and ((len(p.split()) < 3 and not prev_end) or len(merged[-1].split()) < 2) \
                and len((merged[-1] + " " + p).split()) <= max_words:
            merged[-1] += " " + p
        else:
            merged.append(p)
    out = []
    for p in merged:  # long phrases: split into balanced word groups
        w = p.split()
        n = -(-len(w) // max_words)
        k = -(-len(w) // n)
        out += [" ".join(w[i:i + k]) for i in range(0, len(w), k)]
    return out or [text]


def caption_cues(c, max_words):
    """Time each phrase of a spoken chunk in proportion to its length (synced to the TTS audio)."""
    ps = phrases(c["text"], max_words)
    wts = [len(p) + 3 for p in ps]
    tot, t, cues = sum(wts), c["t0"], []
    for p, w in zip(ps, wts):
        d = (c["t1"] - c["t0"]) * w / tot
        cues.append((t, t + d, p)); t += d
    return cues


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
    elif kind == "clap":  # two soft hand claps
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.2, 0.42):
            L = int(0.09 * SR)
            x = np.fft.rfft(rng.standard_normal(L))
            f = np.fft.rfftfreq(L, 1 / SR)
            x *= np.exp(-((f - 1400) / 900) ** 2)
            w = np.fft.irfft(x, L)
            w = w / (np.abs(w).max() + 1e-9) * np.exp(-np.arange(L) / SR * 45) * 0.5
            s0 = int(c0 * SR)
            a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "splash":  # soft puddle splash: watery whoosh plus a few bubbly blips
        x = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        x *= np.exp(-((f - 2200) / 1500) ** 2)
        a = np.fft.irfft(x, n)
        a = a / (np.abs(a).max() + 1e-9) * np.exp(-t * 5) * 0.35
        for k, (c0, f0) in enumerate(((0.12, 900), (0.22, 1200), (0.33, 1000), (0.45, 1400))):
            L = int(0.06 * SR); tt = np.arange(L) / SR
            w = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * tt / 0.06)) / SR) * np.hanning(L) * 0.18
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "rain":  # gentle pitter-patter
        x = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        x *= np.exp(-((f - 3000) / 2500) ** 2)
        a = np.fft.irfft(x, n)
        a = a / (np.abs(a).max() + 1e-9) * 0.10
        for c0 in rng.uniform(0, dur - 0.05, int(dur * 14)):
            L = int(0.02 * SR); tt = np.arange(L) / SR
            w = np.sin(2 * np.pi * rng.uniform(1500, 2800) * tt) * np.exp(-tt * 250) * 0.25
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
        a *= np.minimum(1, np.minimum(t / 0.4, (dur - t) / 0.4))
    elif kind == "bell":  # soft little jingle: tiny bell rings with shimmering, fast-decaying partials
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.35, 0.32):
            for k, (c1, f0) in enumerate(((0.0, 2350), (0.07, 2650), (0.13, 2450))):
                L = int(0.45 * SR); tt = np.arange(L) / SR
                w = sum(g * np.sin(2 * np.pi * f0 * p * tt) for p, g in ((1, 1.0), (2.76, 0.35), (5.4, 0.12)))
                w *= np.exp(-tt * 11) * (1 + 0.15 * np.sin(2 * np.pi * 9 * tt)) * 0.12
                s0 = int((c0 + c1) * SR)
                a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "crunch":  # soft crunchy-leaf steps: short bursts of crackly filtered noise
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.2, 0.42):
            L = int(0.22 * SR); tt = np.arange(L) / SR
            w = rng.standard_normal(L) * (rng.random(L) > 0.55)
            w = np.convolve(w, np.ones(6) / 6, mode="same")
            w *= np.exp(-tt * 18) * 0.5
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "brush":  # soft toothbrush scrub: gentle swishy band-passed noise, swish-swish rhythm
        x = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        x *= np.exp(-((f - 3800) / 1800) ** 2)
        a = np.fft.irfft(x, n)
        a = a / (np.abs(a).max() + 1e-9) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t) ** 2) * 0.22
    elif kind == "tweet":  # soft little bird chirps: quick rising whistles, tweet-tweet
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.25, 0.38):
            for k in range(2):
                L = int(0.09 * SR); tt = np.arange(L) / SR
                fr = 2600 + 1600 * (tt / 0.09) - 700 * (tt / 0.09) ** 2
                w = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.hanning(L) * 0.22
                s0 = int((c0 + k * 0.12) * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "pop":  # soft bubble pops: tiny rising "blip" plops, one every 0.35 s
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.1, 0.35):
            L = int(0.07 * SR); tt = np.arange(L) / SR
            fr = 500 + 2600 * (tt / 0.07) ** 0.6
            w = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 55) * 0.4
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "click":  # soft little lamp-switch click (one gentle tick-tock click)
        a = np.zeros(n)
        for c0, f0 in ((0.08, 2200), (0.16, 1500)):
            L = int(0.03 * SR); tt = np.arange(L) / SR
            w = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 160) * 0.35
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
    elif kind == "squeak":  # cute rubber-toy squeak: two quick squeezy up-down whistles
        a = np.zeros(n)
        for c0 in np.arange(0.05, dur - 0.25, 0.45):
            L = int(0.2 * SR); tt = np.arange(L) / SR
            fr = 1300 + 900 * np.sin(np.pi * tt / 0.2)
            ph = 2 * np.pi * np.cumsum(fr) / SR
            w = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * np.hanning(L) * 0.2
            s0 = int(c0 * SR); a[s0:s0 + L] += w[: max(0, min(L, n - s0))]
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
        t += sc.get("lead", 0.6)
        prompts = []
        for ln in sc["lines"]:
            if ln.get("sfx"):  # sound effect; optional "text" is shown as a caption only
                a = sfx(ln["sfx"], ln.get("dur", 1.8))
                chunks.append(dict(who=ln.get("who", "sfx"), text=ln.get("text", ""), t0=t, t1=t + len(a) / SR, audio=a))
                t += len(a) / SR + ln.get("pause", 0.5)
                continue
            v, sp, *pt = VOICES[ln["who"]]
            for k, s in enumerate(sentences(ln["text"])):
                a = tts.synth(s, v, sp, pt[0] if pt else 1.0)
                if ln["who"] in KIDS:
                    a = tts.soften(a)
                chunks.append(dict(who=ln["who"], text=s, t0=t, t1=t + len(a) / SR, audio=a))
                last = k == len(sentences(ln["text"])) - 1
                gap = 0.25 if not last else ln.get("pause", 0.55)
                if last and gap >= 1.4:  # ask-and-pause: animate a bouncing "?" (or a twinkling star) so the screen never sits still
                    prompts.append((t + len(a) / SR, t + len(a) / SR + gap, "?" if ln["text"].strip().endswith("?") else "star"))
                t += len(a) / SR + gap
        t += sc.get("tail", 0.7)
        scenes.append(dict(sc, t0=start, t1=t, chunks=chunks, prompts=prompts))
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
    """Closed caption: big white rounded bold text, dark outline, soft translucent box (1-2 lines)."""
    fs = 66 if vertical else 50
    font = ImageFont.truetype(FONT, fs)
    maxw = W * (0.74 if vertical else 0.7)
    words, lines = text.split(), [""]
    for w in words:
        t = (lines[-1] + " " + w).strip()
        if font.getlength(t) <= maxw or not lines[-1]:
            lines[-1] = t
        else:
            lines.append(w)
    while len(lines) > 2:  # never more than 2 lines: shrink the font
        fs -= 6; font = ImageFont.truetype(FONT, fs)
        words, lines = text.split(), [""]
        for w in words:
            t = (lines[-1] + " " + w).strip()
            if font.getlength(t) <= maxw * 1.08 or not lines[-1]:
                lines[-1] = t
            else:
                lines.append(w)
    lh = int(fs * 1.22)
    sw = max(4, fs // 11)
    bw = max(font.getlength(l) for l in lines) + 80
    bh = lh * len(lines) + 44
    im = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], 36, fill=(45, 28, 70, 150))
    for i, l in enumerate(lines):
        x = (bw - font.getlength(l)) / 2
        d.text((x, 20 + i * lh), l, font=font, fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(40, 22, 60, 255))
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


def banner(text, W, H, vertical):
    fs = 54 if vertical else 50
    font = ImageFont.truetype(FONT, fs)
    while font.getlength(text) > W * (0.8 if vertical else 0.7) and fs > 30:
        fs -= 4; font = ImageFont.truetype(FONT, fs)
    bw, bh = int(font.getlength(text) + 70), int(fs * 1.6)
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], bh // 2, fill=(255, 120, 170, 235), outline=(255, 255, 255, 255), width=5)
    d.text((35, (bh - fs * 1.25) / 2), text, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(150, 50, 100, 255))
    return im


def draw_prompt(frame, pr, t, W, H, vertical):
    """Bouncing question bubble (or twinkling star) during ask-and-pause moments."""
    t0, t1, kind = pr
    k = t - t0
    pop = min(1.0, k / 0.25) * min(1.0, (t1 - t) / 0.2)
    if pop <= 0:
        return
    r = (H * 0.075 if not vertical else W * 0.11) * (0.6 + 0.4 * pop)
    cx = W * 0.5
    cy = H * (0.15 if not vertical else 0.21) - abs(math.sin(k * 5.0)) * r * 0.35
    d = ImageDraw.Draw(frame)
    if kind == "?":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 215, 70, 255), outline=(150, 60, 110, 255), width=8)
        f = ImageFont.truetype(FONT, int(r * 1.45))
        tw = f.getlength("?")
        d.text((cx - tw / 2, cy - r * 0.98), "?", font=f, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(150, 60, 110, 255))
        left = max(0, int(math.ceil(t1 - t)))  # tiny countdown dots under the bubble
        for i in range(min(left, 3)):
            dx = (i - (min(left, 3) - 1) / 2) * r * 0.45
            d.ellipse([cx + dx - r * 0.1, cy + r * 1.2 - r * 0.1, cx + dx + r * 0.1, cy + r * 1.2 + r * 0.1], fill=(255, 255, 255, 230))
    else:
        rr = r * (0.85 + 0.15 * math.sin(k * 6))
        d.polygon(art.star_pts(cx, cy, rr, rr * 0.48, -math.pi / 2 + math.sin(k * 3) * 0.15), fill=(255, 225, 90, 255), outline=(150, 60, 110, 255), width=7)


def write_srt(scenes, path, cover=COVER):
    """Closed-caption file (SRT) matching the burned-in subtitles; times include the opening cover frame."""
    ts = lambda x: "%02d:%02d:%02d,%03d" % (int(x // 3600), int(x % 3600 // 60), int(x % 60), int(round((x % 1) * 1000)) % 1000)
    out, n = [], 0
    for sc in scenes:
        for c in sc["chunks"]:
            if c["text"]:
                for (a, b, p) in c["cues"]:
                    n += 1
                    out.append(f"{n}\n{ts(a + cover)} --> {ts(b + cover)}\n{p}\n")
    open(path, "w").write("\n".join(out))


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
    # thumbnail cover frame only on vertical Shorts/Reels (they pick a frame); full videos start straight on the action
    cov = COVER if (vertical or os.environ.get("HB_COVER")) else 0.0
    mix = np.concatenate([np.zeros(int(cov * SR)), mix])
    tts.save_wav(out_path + ".wav", mix / np.abs(mix).max() * 0.95)
    for sc in scenes:
        for c in sc["chunks"]:
            c["cues"] = caption_cues(c, 6 if vertical else 11) if c["text"] else []
    write_srt(scenes, re.sub(r'\.mp4$', '', out_path) + '.srt', cov)
    stills = [float(x) for x in os.environ.get("HB_STILLS", "").split(",") if x]

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
        sc["banner_im"] = banner(sc["banner"], W, H, vertical) if sc.get("banner") else None

    if stills:  # HB_STILLS="3,10.5": save PNG frames at those times (no cover offset) instead of encoding
        ff = subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
    else:
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", out_path + ".wav", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", os.environ.get("HB_CRF", "21"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                           "-af", "loudnorm=I=-16:TP=-1.5", "-shortest", "-movflags", "+faststart", out_path],
                          stdin=subprocess.PIPE)
    ground = 0.74 if vertical else 0.86
    for _ in range(int(cov * FPS)):
        ff.stdin.write(cover.tobytes())
    nframes = int(total * FPS)
    si = 0
    for fi in range(nframes):
        t = fi / FPS
        if stills and not any(abs(t - x) < 0.5 / FPS for x in stills):
            continue
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
        if sc.get("rain"):  # gentle animated rain streaks (behind the characters)
            for i in range(110 if not vertical else 90):
                rx = (i * 397.13) % W
                sp = H * (0.55 + (i % 7) * 0.05)
                ry = ((i * 211.7) % H + t * sp) % (H * 1.1) - H * 0.05
                dx = -H * 0.006
                d.line([rx, ry, rx + dx, ry + H * 0.028], fill=(232, 240, 255), width=3)
        if sc.get("rainbow"):  # soft pastel rainbow that fades in (behind the characters)
            ra = min(1.0, (t - sc["t0"]) / 2.0)
            rb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rd = ImageDraw.Draw(rb)
            cx, cy, R = W * 0.5, H * (ground + 0.02), min(W, H) * (0.62 if not vertical else 0.48)
            for i, col in enumerate([(255, 140, 150), (255, 190, 120), (255, 235, 130), (150, 225, 150), (140, 190, 255), (190, 160, 245)]):
                rr = R - i * R * 0.07
                rd.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=col + (int(170 * ra),), width=int(R * 0.07) + 2)
            frame.alpha_composite(rb)
            d = ImageDraw.Draw(frame)
        if sc.get("leaves"):  # gently falling, swaying autumn leaves (behind the characters)
            for i in range(14 if not vertical else 12):
                lx = (i * 151.7) % W + math.sin(t * 1.3 + i) * W * 0.03
                sp = H * (0.07 + (i % 5) * 0.015)
                ly = ((i * 233.3) % H + t * sp) % (H * 0.9) - H * 0.05
                art._leaf(d, lx, ly, H * 0.028, ["red", "orange", "yellow", "brown"][i % 4], t * 0.8 + i, ol=False)
        if sc.get("bubbles"):  # soft soap bubbles drifting up and wobbling (behind the characters)
            for i in range(16 if not vertical else 14):
                bx = (i * 173.3) % W + math.sin(t * 1.1 + i * 1.7) * W * 0.025
                sp = H * (0.05 + (i % 5) * 0.012)
                by = H * 1.05 - ((i * 271.9) % H + t * sp) % (H * 1.1)
                br = H * (0.012 + (i % 4) * 0.006)
                d.ellipse([bx - br, by - br, bx + br, by + br], outline=(255, 255, 255, 235), width=max(2, int(br * 0.18)))
                d.arc([bx - br * 0.75, by - br * 0.75, bx + br * 0.75, by + br * 0.75], 200, 250, fill=(255, 190, 220), width=max(2, int(br * 0.15)))
                d.ellipse([bx - br * 0.5, by - br * 0.55, bx - br * 0.15, by - br * 0.3], fill=(255, 255, 255, 230))
        if sc.get("fireflies"):  # tiny blinking firefly lights drifting slowly (behind the characters)
            fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fd = ImageDraw.Draw(fl)
            for i in range(14 if not vertical else 11):
                fx = (i * 263.7) % W + math.sin(t * 0.6 + i * 2.1) * W * 0.04
                fy = H * (0.35 + ((i * 0.137) % 0.45)) + math.cos(t * 0.8 + i) * H * 0.03
                b = max(0.0, math.sin(t * 2.0 + i * 1.9))
                if b > 0.05:
                    fr_ = H * 0.022
                    fd.ellipse([fx - fr_, fy - fr_, fx + fr_, fy + fr_], fill=(230, 255, 120, int(90 * b)))
                    fd.ellipse([fx - fr_ * 0.35, fy - fr_ * 0.35, fx + fr_ * 0.35, fy + fr_ * 0.35], fill=(255, 255, 200, int(255 * b)))
            frame.alpha_composite(fl.filter(ImageFilter.GaussianBlur(2)))
            d = ImageDraw.Draw(frame)
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
            if c.get("swing") is not None:  # swing sprites: top-centre is the pivot on the beam ("y" = beam), rock like a pendulum
                amp = float(c["swing"])
                ang = round(amp * math.sin((t - sc["t0"]) * 2.6) * 2) / 2 if amp else 0.0
                rk = ("swing", c["id"], c.get("scale", 1.0), eyes, m, bool(c.get("flip")), ang)
                if rk not in cache_spr:
                    pw = im.width + 2 * int(im.height * math.sin(math.radians(max(abs(amp), 1))) + 4)
                    pad = Image.new("RGBA", (pw, im.height), (0, 0, 0, 0))
                    pad.alpha_composite(im, ((pw - im.width) // 2, 0))
                    cache_spr[rk] = pad.rotate(ang, resample=Image.BICUBIC, center=(pw / 2, 0)) if ang else pad
                im = cache_spr[rk]
                x = int(c["x"] * W - im.width / 2)
                y = int(c.get("y", 0.255) * H)
            if c.get("glow"):  # soft pulsing highlight behind a found object
                gk = ("glow", im.width, im.height)
                if gk not in cache_spr:
                    g = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0))
                    ImageDraw.Draw(g).ellipse([im.width * 0.35, im.height * 0.35, im.width * 1.65, im.height * 1.65], fill=(255, 240, 150, 210))
                    cache_spr[gk] = g.filter(ImageFilter.GaussianBlur(max(6, im.width // 10)))
                g = cache_spr[gk]
                pul = 0.75 + 0.25 * math.sin(t * 4)
                ga = g.copy(); ga.putalpha(Image.eval(g.getchannel("A"), lambda v, p=pul: int(v * p)))
                gx, gy = x - im.width // 2, y - im.height // 2
                ga = ga.crop((max(0, -gx), max(0, -gy), ga.width, ga.height))  # keep the glow centred even near the frame edge
                frame.alpha_composite(ga, (max(0, gx), max(0, gy)))
            frame.alpha_composite(im, (max(-im.width + 1, x), max(-im.height + 1, y)))
        if fg is not None:
            frame.alpha_composite(fg)
        if sc["overlay"] is not None:
            frame.alpha_composite(sc["overlay"])
        if sc["banner_im"] is not None and t - sc["t0"] < 6.0:  # small episode-name banner over the action (no long title card)
            bt = t - sc["t0"]
            ba = max(0.0, min(1.0, (bt - 0.4) / 0.4, (6.0 - bt) / 0.5))
            if ba > 0:
                bi = sc["banner_im"].copy()
                bi.putalpha(Image.eval(bi.getchannel("A"), lambda v, a=ba: int(v * a)))
                frame.alpha_composite(bi, ((W - bi.width) // 2, int(H * (0.125 if vertical else 0.04))))
        pr = next((p for p in sc["prompts"] if p[0] <= t < p[1]), None)
        if pr is not None:
            draw_prompt(frame, pr, t, W, H, vertical)
        cue = None
        if cur is not None and cur["text"]:  # burned-in captions on every spoken line, one short phrase at a time
            cue = next((p for (a, b, p) in cur["cues"] if a <= t < b), cur["cues"][-1][2])
        if cue:
            if cue not in cache_txt:
                cache_txt[cue] = text_box(cue, W, H, vertical)
            tb = cache_txt[cue]
            # vertical: lower-middle safe area (bottom edge at y=1490, above the platform buttons; x 90-990)
            frame.alpha_composite(tb, ((W - tb.width) // 2, int(H * 0.776 - tb.height) if vertical else int(H * 0.97 - tb.height)))
        # fades at scene edges
        a = min(1, (t - sc["t0"]) / 0.5 if si > 0 else 1, (sc["t1"] - t) / 0.5)  # first scene starts bright (no fade from black)
        rgb = frame.convert("RGB")
        if a < 1:
            rgb = Image.eval(rgb, lambda v, a=max(a, 0): int(v * a))
        if stills:
            if any(abs(t - x) < 0.5 / FPS for x in stills):
                rgb.save(re.sub(r'\.mp4$', '', out_path) + f"_still_{t:05.1f}.png")
        else:
            ff.stdin.write(rgb.tobytes())
        if fi % (FPS * 30) == 0:
            print(f"{t:.0f}s / {total:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], vertical=len(sys.argv) > 3 and sys.argv[3] == "vertical")
