# Honey Bunny Kidz daily pipeline — environment setup

Run from a fresh session (Linux workspace, Python 3 with numpy, PIL, onnxruntime, ffmpeg; PyPI and huggingface are blocked, github.com works).

```bash
# 1. media repo (attach with add_repo owner=honey-bunny-kidz repo=honeybunny-media access=push first)
git clone https://github.com/honey-bunny-kidz/honeybunny-media /home/claude/honeybunny-media

# 2. voice + pronunciation data
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/hexgrad/misaki /home/claude/hexgrad/misaki
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/thewh1teagle/kokoro-onnx /home/claude/thewh1teagle/kokoro-onnx
mkdir -p /home/claude/hb/models /home/claude/hb/out
B=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
curl -sL -o /home/claude/hb/models/kokoro.onnx $B/kokoro-v1.0.onnx
curl -sL -o /home/claude/hb/models/voices.bin  $B/voices-v1.0.bin

# 3. pipeline code
cp /home/claude/honeybunny-media/pipeline/*.py /home/claude/hb/   # tts.py art.py render.py thumbnail.py
mkdir -p /home/claude/hb/episodes && cp /home/claude/honeybunny-media/pipeline/episodes/*.json /home/claude/hb/episodes/

# 4. render
cd /home/claude/hb
python3 render.py episodes/epNNN.json out/epNNN_full.mp4
python3 render.py episodes/epNNN_short.json out/epNNN_short.mp4 vertical
```

## Building blocks available
- Backgrounds (art.background): `day`, `night`, `oak`, `bedroom`, `garden` (red rose bush + sunflower), `garden_pond` (blue pond), `porch` (Mimi's cottage with red roof) , `sunset` (pink-purple evening sky, low orange sun, oak tree), `meadow` (bright morning, pastel rainbow, tulips, butterflies), `pumpkin_patch` (autumn trees, wooden fence, hay bale, pumpkins on vines, falling leaves) — add new ones in art.py as needed (e.g. beach, garden, farm, snow).
- Characters (art.CHARS): `honey` (bunny, pink bow), `mama` (Mama Bunny), `dotty` (duckling), `ollie` (owl), `moon`, `mimi` (Mimi Kitten: cream fur, orange patch, pink collar with bell), `lulu` (Lulu Lamb: white wool, floppy pink ears, lavender bow; in bed use x=0.47, y=0.865, scale 0.92 next to Honey), `yarn` (pink yarn ball prop, no voice), `pip` (Pip Puppy: golden puppy, brown floppy ears, blue collar with gold star tag, waggy tail), props `pumpkin` and `pumpkin_smile` (carved smiley face; use scale 1.5–2), `pumpkinpip` (Pip in a pumpkin costume, eyes peeking, tail out; voice = pip). Add new cute characters in art.py following the same pattern (eyes open/closed, mouth 0/1/2).
- Voices (render.VOICES): narrator af_heart, honey af_sky, mama af_bella, dotty af_nicole, ollie bm_fable, moon bm_george, mimi af_sky pitched up 1.13, lulu bf_lily pitched up 1.12, pip am_puck pitched up 1.12 (VOICES entries may have a 3rd value = pitch; 1.08–1.15 gives a soft, cute, young voice). New characters need a voice entry.
- Episode JSON: scenes with bg, optional title/subtitle (title card), cast [{id,x,y,scale,flip,sleep}], lines [{who,text,pause}].
- Bedroom: Honey in bed uses x=0.300, y=0.903 (landscape).
- Unknown words: tts.MISSING lists them; add phonemes to the D.update({...}) line in tts.py.

## Thumbnails
- render.py automatically writes `out/<name>_thumb.jpg` (1280x720 landscape, or 1080x1920 for the vertical Short) via thumbnail.py and shows it as the first 0.5 s of the video, so platforms that pick a frame (Shorts, Reels) still get the thumbnail as the cover.
- Control it with a "thumbnail" block in the episode JSON:
  `"thumbnail": {"text": "Can't Sleep?", "badge": "Bedtime Story", "bg": "night", "cast": [{"id": "honey", "mouth": 2}, {"id": "dotty"}, {"id": "ollie", "scale": 0.8}]}`
  - text: 2-4 BIG words, a question or exclamation that makes a parent curious (not the full title).
  - badge: "Bedtime Story" (purple), "Adventure Story" (green), "Kids Story" (blue) or "Sing-Along Rhyme" (orange).
  - cast: 1-3 characters, the star first with mouth 2 (excited face); use characters from the episode. Add "flip": true to mirror a character (e.g. so Pip's tail doesn't cover a friend).
  - Run `python3 thumbnail.py episodes/epNNN.json out/test_thumb.jpg` and Read the image before rendering: text readable, faces fully visible, no overlap with text.
- Copy thumbnails to `thumbnails/` in the repo. Public URL: https://raw.githubusercontent.com/honey-bunny-kidz/honeybunny-media/main/thumbnails/FILE
