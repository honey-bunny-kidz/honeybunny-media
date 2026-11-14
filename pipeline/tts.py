"""Offline kid-friendly narration: Kokoro ONNX + misaki US dictionary (no espeak needed)."""
import json, re, wave
import numpy as np, onnxruntime as ort

ROOT = "/home/claude"
CFG = json.load(open(f"{ROOT}/thewh1teagle/kokoro-onnx/src/kokoro_onnx/config.json"))
VOCAB = CFG["vocab"]
D = {}
for f in ("us_silver", "us_gold"):
    D.update(json.load(open(f"{ROOT}/hexgrad/misaki/misaki/data/{f}.json")))
D.update({"Bunnies": "bˈʌniz", "bunnies": "bˈʌniz", "Kidz": "kˈɪdz", "kidz": "kˈɪdz", "hoo": "hˈu", "Hoo": "hˈu", "Ollie": "ˈɑli", "Dotty": "dˈɑɾi", "Mimi": "mˈimi", "meow": "miˈW", "Meow": "miˈW", "purr": "pˈɜɹ", "Purr": "pˈɜɹ", "Splish": "splˈɪʃ", "splish": "splˈɪʃ", "Lulu": "lˈulu", "Hee": "hˈi", "hee": "hˈi", "Shh": "ʃːː", "shh": "ʃːː", "Aaah": "ˈɑɑɑ", "aaah": "ˈɑɑɑ", "twinkliest": "twˈɪŋkᵊliəst", "Pitter": "pˈɪɾəɹ", "pitter": "pˈɪɾəɹ", "puppies": "pˈʌpiz", "bodies": "bˈɑdiz", "Wheee": "wˈiː", "wheee": "wˈiː", "Achoo": "ɑʧˈu", "achoo": "ɑʧˈu", "fireflies": "fˈIəɹflˌIz", "Fireflies": "fˈIəɹflˌIz", "Brrr": "bɹːː", "brrr": "bɹːː", "choo": "ʧˈu", "Choo": "ʧˈu"})
VOICES = dict(np.load(f"{ROOT}/hb/models/voices.bin"))
# Blended "cute" voices (2026-11-09, user asked for cute, attractive voices):
#   hb_narr  = warm af_heart + bright af_sky  -> friendly, smiling storyteller
#   hb_honey = af_sky + a touch of soft af_nicole -> sweet little bunny
VOICES["hb_narr"] = 0.65 * VOICES["af_heart"] + 0.35 * VOICES["af_sky"]
VOICES["hb_honey"] = 0.75 * VOICES["af_sky"] + 0.25 * VOICES["af_nicole"]
# Soft KID voices (2026-11-09, user: grown-ups keep the new voices, children get a soft kid voice).
# Bases are the highest Kokoro voices (bf_alice ~235 Hz, af_jessica ~217, bf_isabella ~214, af_sarah ~203) so a 1.2-1.3
# pitch-up lands in a small child's range (~250-280 Hz) without sounding like a chipmunk; soften() rounds off the edge.
VOICES["kid_honey"] = 0.65 * VOICES["af_jessica"] + 0.15 * VOICES["af_sky"] + 0.20 * VOICES["af_nicole"]
VOICES["kid_lulu"] = 0.70 * VOICES["bf_alice"] + 0.30 * VOICES["bf_lily"]
VOICES["kid_mimi"] = 0.70 * VOICES["bf_isabella"] + 0.30 * VOICES["af_nicole"]
VOICES["kid_dotty"] = 0.60 * VOICES["af_sarah"] + 0.20 * VOICES["af_jessica"] + 0.20 * VOICES["af_nicole"]
VOICES["kid_cloudy"] = 0.60 * VOICES["bf_alice"] + 0.40 * VOICES["bf_emma"]
VOICES["kid_pip"] = 0.50 * VOICES["am_eric"] + 0.50 * VOICES["af_jessica"]


def soften(a, gain=0.9, k=0.55):
    """Gentle low-pass (takes the edge off pitched-up voices) and a slightly lower level: a soft, cosy kid voice."""
    out = np.empty_like(a)
    y = 0.0
    for i, x in enumerate(a):  # one-pole IIR
        y += k * (x - y)
        out[i] = y
    return out * gain
_sess = None
SR = 24000
MISSING = set()

NUM = {str(i): w for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve".split())}


def _lookup(w):
    for cand in (w, w.lower(), w.capitalize()):
        p = D.get(cand)
        if p is None:
            continue
        if isinstance(p, dict):
            p = p.get("DEFAULT") or next(iter(v for v in p.values() if v))
        return p
    # simple suffix fallbacks
    lw = w.lower()
    for suf, add in (("'s", "z"), ("s", "z"), ("es", "ᵻz"), ("ed", "d"), ("d", "d"), ("ing", "ɪŋ"), ("y", "i")):
        if lw.endswith(suf) and len(lw) > len(suf) + 1:
            base = _lookup(lw[: -len(suf)])
            if base:
                return base + add
    return None


def phonemize(text):
    text = text.replace("’", "'").replace("—", ", ").replace("…", "...")
    out = []
    for tok in re.findall(r"[A-Za-z']+|\d+|[.,!?;:]", text):
        if tok in NUM:
            tok = NUM[tok]
        if re.match(r"[.,!?;:]", tok):
            if out and out[-1] == " ":
                out.pop()
            out.append(tok + " ")
            continue
        p = _lookup(tok.strip("'"))
        if p is None:
            MISSING.add(tok)
            # split hyphen-less compounds like "Bunnyland"
            parts = re.findall(r"[A-Z]?[a-z]+", tok)
            ps = [_lookup(x) for x in parts]
            p = "".join(x for x in ps if x) if all(ps) and parts else ""
        if p:
            out.append(p + " ")
    return "".join(out).strip()


def synth(text, voice="af_heart", speed=0.88, pitch=1.0):
    global _sess
    if _sess is None:
        _sess = ort.InferenceSession(f"{ROOT}/hb/models/kokoro.onnx")
    ph = phonemize(text)
    toks = [VOCAB[c] for c in ph if c in VOCAB][:500]
    style = VOICES[voice][len(toks)]
    speed = speed / pitch
    audio = _sess.run(None, {"tokens": np.array([[0, *toks, 0]], dtype=np.int64),
                             "style": style.astype(np.float32),
                             "speed": np.array([speed], dtype=np.float32)})[0]
    a = np.asarray(audio, dtype=np.float64).reshape(-1)
    if pitch != 1.0:  # raise pitch by resampling (synth slower first so the pace stays the same)
        n = int(len(a) / pitch)
        a = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a)
    return a


def save_wav(path, audio):
    a = np.clip(audio, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    a = synth("Once upon a time, in a cozy little meadow, lived a fluffy bunny named Honey. Goodnight, little friends!")
    save_wav("/home/claude/hb/test.wav", a)
    print(len(a) / SR, "sec; missing:", MISSING)
