"""Build a compilation from several episode JSONs, with fresh host bridges.

Usage: python3 compile.py OUT.json "Compilation Title" "Thumb Words" BADGE BG ep001 ep002 ...
  - Sunday story time: 30-45 min, then HB_CRF=29 python3 render.py OUT.json out/compNNN.mp4 (keeps ~40 min < 95 MB)
  - Wed/Sat 10-minute mini compilation ("mini"): 2-3 episodes, ~9:30-11 min, render with HB_CRF=26.
Retention rules (2026-11-09): no welcome title card and no "presents" lines. The video opens straight on the first
story's opening scene; each story's name shows as a small banner over the action; bridges are short new host scenes
with an ask-and-pause question (so the compilation adds something new rather than being a plain re-upload).
"""
import json, sys

HOSTS = ["honey", "mimi", "pip", "lulu", "dotty"]
BRIDGE_BG = ["meadow", "garden", "day", "porch", "pumpkin_patch", "sunset", "autumn_park", "sunny_hill"]


def load(eid):
    return json.load(open(f"episodes/{eid}.json"))


def star(ep):
    for sc in ep["scenes"]:
        for c in sc.get("cast", []):
            if c["id"] in HOSTS + ["mama", "ollie"]:
                return c["id"]
    return "honey"


def story_scenes(ep):
    """Episode scenes without the old title card / "presents" line; the story name becomes a banner on its first scene."""
    out = []
    for sc in ep["scenes"]:
        sc = dict(sc)
        if sc.get("title"):
            lines = [l for l in sc["lines"] if "presents" not in l.get("text", "")]
            if not lines:
                continue
            sc.pop("title"); sc.pop("subtitle", None); sc["lines"] = lines
        sc.pop("banner", None)
        out.append(sc)
    if out:
        out[0]["banner"] = ep["title"]
    return out


def build(title, words, badge, bg, ids, bedtime=False):
    eps = [load(i) for i in ids]
    scenes = []
    for k, ep in enumerate(eps):
        if k > 0:  # short host bridge between stories
            host = HOSTS[k % len(HOSTS)]
            guest = star(ep)
            cast = [{"id": host, "x": 0.35}]
            if guest != host:
                cast.append({"id": guest, "x": 0.65})
            nxt = "last" if k == len(eps) - 1 else "next"
            lines = [{"who": host, "text": f"Are you ready for the {nxt} story? Say, yes!", "pause": 2.0},
                     {"who": host, "text": f"Yay! It's {ep['title']}. Let's watch!"}]
            if bedtime:
                lines.insert(0, {"who": host, "text": "First, let's take a big, slow breath together. Breathe in... and out.", "pause": 1.6})
            scenes.append({"bg": "night" if bedtime else BRIDGE_BG[k % len(BRIDGE_BG)], "lead": 0.4, "tail": 0.5, "cast": cast, "lines": lines})
        scenes += story_scenes(ep)
    scenes.append({"bg": "night" if bedtime else bg, "banner": "Thank you for watching!", "lead": 0.4, "tail": 1.5,
                   "cast": [{"id": "honey", "x": 0.3}, {"id": "pip", "x": 0.5}, {"id": "mimi", "x": 0.7}],
                   "lines": [{"who": "narrator", "text": "That's all for now, friends! Come back soon for more stories and songs on Honey Bunny Kidz. Bye bye!"}]})
    cast = [{"id": star(eps[0]), "mouth": 2}] + [{"id": star(e)} for e in eps[1:] if star(e) != star(eps[0])][:2]
    return {"id": "compilation", "title": title, "episodes": ids,
            "thumbnail": {"text": words, "badge": badge, "bg": bg, "cast": cast}, "scenes": scenes}


if __name__ == "__main__":
    out, title, words, badge, bg, *ids = sys.argv[1:]
    comp = build(title, words, badge, bg, ids, bedtime="bedtime" in badge.lower())
    json.dump(comp, open(out, "w"), indent=1)
    print("wrote", out, "with", len(comp["scenes"]), "scenes from", ids)
