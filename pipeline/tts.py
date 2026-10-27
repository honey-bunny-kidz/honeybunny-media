"""Offline kid-friendly narration: Kokoro ONNX + misaki US dictionary (no espeak needed)."""
import json, re, wave
import numpy as np, onnxruntime as ort

ROOT = "/home/claude"
CFG = json.load(open(f"{ROOT}/thewh1teagle/kokoro-onnx/src/kokoro_onnx/config.json"))
VOCAB = CFG["vocab"]
D = {}
for f in ("us_silver", "us_gold"):
    D.update(json.load(open(f"{ROOT}/hexgrad/misaki/misaki/data/{f}.json")))
D.update({"Kidz": "kˈɪdz", "kidz": "kˈɪdz", "hoo": "hˈu", "Hoo": "hˈu", "Ollie": "ˈɑli", "Dotty": "dˈɑɾi", "Mimi": "mˈimi", "meow": "miˈW", "Meow": "miˈW", "purr": "pˈɜɹ", "Purr": "pˈɜɹ", "Splish": "splˈɪʃ", "splish": "splˈɪʃ", "Lulu": "lˈulu", "Hee": "hˈi", "hee": "hˈi"})
VOICES = np.load(f"{ROOT}/hb/models/voices.bin")
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
