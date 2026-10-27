"""Build a long compilation episode (30-45 min) from several episode JSONs, with fresh host bridges.

Usage: python3 compile.py OUT.json "Compilation Title" "Thumb Words" BADGE BG ep001 ep002 ...
Then: HB_CRF=29 python3 render.py OUT.json out/compNNN.mp4   (crf 29 keeps ~40 min under ~95 MB for GitHub)
Bridges are new scenes (a host introduces each story with an ask-and-pause question), so the
compilation is more than a plain re-upload. Episode title cards are kept so viewers see each story name.
"""
import json, sys

HOSTS = ["honey", "mimi", "pip", "lulu", "dotty"]
BRIDGE_BG = ["meadow", "garden", "day", "porch", "pumpkin_patch", "sunset"]


def load(eid):
    return json.load(open(f"episodes/{eid}.json"))


def star(ep):
    for sc in ep["scenes"]:
        for c in sc.get("cast", []):
            if c["id"] in HOSTS + ["mama", "ollie"]:
                return c["id"]
    return "honey"


def build(title, words, badge, bg, ids, bedtime=False):
    eps = [load(i) for i in ids]
    scenes = [{
        "bg": bg, "title": title, "subtitle": "Honey Bunny Kidz  •  Story Time", "lead": 0.8, "tail": 1.0,
        "cast": [{"id": "honey", "x": 0.5}],
        "lines": [{"who": "narrator", "text": f"Welcome to Honey Bunny Kidz story time! Today we have {len(eps)} stories for you."}]}]
    for k, ep in enumerate(eps):
        host = HOSTS[k % len(HOSTS)]
        guest = star(ep)
        cast = [{"id": host, "x": 0.35}]
        if guest != host:
            cast.append({"id": guest, "x": 0.65})
        nxt = "first" if k == 0 else ("last" if k == len(eps) - 1 else "next")
        lines = [{"who": host, "text": f"Are you ready for the {nxt} story? Say, yes!", "pause": 2.0},
                 {"who": host, "text": f"Yay! It's called: {ep['title']}. Let's watch!"}]
        if bedtime and k > 0:
            lines.insert(0, {"who": host, "text": "First, let's take a big, slow breath together. Breathe in... and out.", "pause": 1.6})
        scenes.append({"bg": "night" if bedtime else BRIDGE_BG[k % len(BRIDGE_BG)], "cast": cast, "lines": lines})
        scenes += ep["scenes"]
    scenes.append({"bg": "night" if bedtime else bg, "title": "Thank You for Watching!",
                   "subtitle": "More stories every day on Honey Bunny Kidz", "lead": 0.5, "tail": 2.0,
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
