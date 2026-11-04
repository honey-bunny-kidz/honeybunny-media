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
- Backgrounds (art.background): `day`, `night`, `oak`, `bedroom`, `garden` (red rose bush + sunflower), `garden_pond` (blue pond), `porch` (Mimi's cottage with red roof) , `sunset` (pink-purple evening sky, low orange sun, oak tree), `meadow` (bright morning, pastel rainbow, tulips, butterflies), `pumpkin_patch` (autumn trees, wooden fence, hay bale, pumpkins on vines, falling leaves), `playground` (sunny park: round sun, A-frame swing set with triangle legs, tree, checkered picnic blanket front-centre — landscape subtitles cover the blanket, so stand props on the grass), `night_garden` (Honey's cottage porch at night: glowing window, lantern, oak tree with Ollie's branch at x=0.62 y=0.495 landscape, lily-pad pond bottom right, twinkling fireflies) , `autumn_porch` (Honey's cottage front porch on an autumn afternoon: door with leaf wreath, leaf garland, potted yellow flowers, wooden floor, and a long low pumpkin shelf — pumpkins stand on it at y=0.805 landscape / y=0.685 vertical) `playroom` (Honey's sunny dress-up playroom: peach polka-dot wall, window with autumn tree, bunting, round mirror right, costume trunk far left, blue rug front-centre), `stretch_room` (Honey's cosy stretch corner at dusk: lavender star wallpaper, arched night window — Moon fits in it at x=0.43 y=0.34 scale 0.5 landscape, Ollie on the sill at x=0.6 y=0.545 scale 0.55 — fairy lights, floor lamp, plant, round rug with pink/green/blue stretch mats), `rainy_garden` (soft rainy morning: lavender sky, puffy clouds, Honey's cottage left, duck pond with reeds right, tulips, puddles front; add `"rain": true` to a scene for animated rain streaks — works on any bg) , `living_room` (Honey's cosy living room on a rainy day: striped cream wall, big rainy window with curtains, green sofa left = "Sofa Island", lamp, bookshelf, round rug), `fort_ship` (same room with a blanket-fort ship: two chairs, polka-dot purple blanket roof, broom mast with sheet sails and a pink flag, cardboard-box hull whose front edge is a foreground layer so friends stand IN the boat, blue blanket "sea" with wave curls; landscape hull spans x 0.14–0.86, vertical 0.03–0.97) , `dusk_stage` (golden-hour meadow concert: lavender-peach sky, rising moon, string of glowing paper lanterns, oak tree right, big tree-stump stage centre — a singer stands ON the stump at x=0.5 y=0.77 landscape / y=0.685 vertical scale 0.8) — add new ones in art.py as needed (e.g. beach, garden, farm, snow).
- Characters (art.CHARS): `honey` (bunny, pink bow), `mama` (Mama Bunny), `dotty` (duckling), `ollie` (owl), `moon`, `mimi` (Mimi Kitten: cream fur, orange patch, pink collar with bell), `lulu` (Lulu Lamb: white wool, floppy pink ears, lavender bow; in bed use x=0.47, y=0.865, scale 0.92 next to Honey), `yarn` (pink yarn ball prop, no voice), `pip` (Pip Puppy: golden puppy, brown floppy ears, blue collar with gold star tag, waggy tail), props `pumpkin` and `pumpkin_smile` (carved smiley face; use scale 1.5–2), `pumpkinpip` (Pip in a pumpkin costume, eyes peeking, tail out; voice = pip), `cricket` (tiny green cricket, use scale 1.6–1.8) and `frog` (little green frog; on the night_garden pond use x=0.9 y=0.92 landscape) — no voices, use sound effects. Painted pumpkins (faces painted, never carved; scale 1.6 landscape, 0.8–1.2 vertical): `p_happy` (orange), `p_sleepy` (yellow, zz), `p_silly` (white, wink + tongue), `p_surprised` (green, O mouth), `p_giggle` (coral). Costume versions (same voices as the base character, voice keys already in render.VOICES): `honey_berry` (Honey as a strawberry, leaf hat), `honey_pj` (Honey in blue dotted pajamas; in bed use x=0.300 y=0.903), `pip_fire` (Pip as a pretend firefighter: red helmet with star, yellow coat), `mimi_star` (Mimi in a yellow star suit with star headband), `honey_rain` (Honey in a yellow raincoat and red rain boots), `dotty_beads` (Dotty with shiny raindrops beaded on her feathers), `pip_drip` (rain-soaked Pip with drops flying off). Helper `_drops(d, [(x, y, r)])` draws shiny water drops. bunny/puppy/kitten take a `costume=` kw, so new outfits can be added the same way (helpers `_suit`, `star_pts`). Pretend-play: `pip_captain` (Pip in a folded paper captain hat; voice = pip), cushion props `pillow_pink`, `pillow_blue`, `pillow_yellow`, `pillow_green` (scale 1.2 landscape on the floor; vertical: a row at y=0.36 scale 0.9 sits on the window sill). Shape props `ball` (red circle), `block` (blue square with star), `sandwich` (triangle jam sandwich; scale 1.2–1.4). Any cast entry can take `"glow": true` for a soft pulsing highlight (use it when a character 'finds' an object, or to reveal a guessed friend AFTER the pause — never in the question scene). The glow stays centred on characters near the frame edge (fixed 2026-11-04). Add new cute characters in art.py following the same pattern (eyes open/closed, mouth 0/1/2).
- Voices (render.VOICES): narrator af_heart, honey af_sky, mama af_bella, dotty af_nicole, ollie bm_fable, moon bm_george, mimi af_sky pitched up 1.13, lulu bf_lily pitched up 1.12, pip am_puck pitched up 1.12 (VOICES entries may have a 3rd value = pitch; 1.08–1.15 gives a soft, cute, young voice). New characters need a voice entry.
- Sound effects: a line `{"who": "frog", "sfx": "frog", "text": "Ribbit!", "dur": 2.0, "pause": 0.6}` plays an original synthesized sound (`cricket`, `wind`, `frog`, `owl`, `clap` = two soft hand claps, use dur 1.0; `splash` = puddle splash, dur 1.0; `rain` = gentle pitter-patter, dur 2–3); `text` is a caption only ("" = no caption) and `who` makes that character's mouth move.
- Vertical Shorts: captions sit in the lower-middle (y≈1290–1490), so keep faces above that; high spots (window sill, branch) are fine in vertical now.
- Episode JSON: scenes with bg, optional title/subtitle (title card), cast [{id,x,y,scale,flip,sleep}], lines [{who,text,pause}].
- Bedroom: Honey in bed uses x=0.300, y=0.903 (landscape).
- Unknown words: tts.MISSING lists them; add phonemes to the D.update({...}) line in tts.py.

## Thumbnails
- render.py automatically writes `out/<name>_thumb.jpg` (1280x720 landscape, or 1080x1920 for the vertical Short) via thumbnail.py and shows it as the first 0.5 s of the video, so platforms that pick a frame (Shorts, Reels) still get the thumbnail as the cover.
- Control it with a "thumbnail" block in the episode JSON:
  `"thumbnail": {"text": "Can't Sleep?", "badge": "Bedtime Story", "bg": "night", "cast": [{"id": "honey", "mouth": 2}, {"id": "dotty"}, {"id": "ollie", "scale": 0.8}]}`
  - text: 2-4 BIG words, a question or exclamation that makes a parent curious (not the full title).
  - badge: "Learn Shapes"/"Learn ..." (teal), "Bedtime Story" (purple), "Adventure Story" (green), "Kids Story" (blue) or "Sing-Along Rhyme" (orange).
  - cast: 1-3 characters, the star first with mouth 2 (excited face); use characters from the episode. Add "flip": true to mirror a character, and optional "x" (0–1) to place a character by hand (e.g. so Pip's tail doesn't cover a friend).
  - Run `python3 thumbnail.py episodes/epNNN.json out/test_thumb.jpg` and Read the image before rendering: text readable, faces fully visible, no overlap with text.
- Copy thumbnails to `thumbnails/` in the repo. Public URL: https://raw.githubusercontent.com/honey-bunny-kidz/honeybunny-media/main/thumbnails/FILE

## Extra Shorts (3 per episode)
- Each episode gets `epNNN_short.json`, `epNNN_short2.json` and `epNNN_short3.json`, each a self-contained vertical Short (15–90 s, aim 45–75 s; never over 90 s, Facebook's Reel limit) with a DIFFERENT hook and its own "thumbnail" block:
  short = guess-who/guess-what hook; short2 = learn-along (count, colors, shapes, big/small, animal sound) with a pause for the viewer; short3 = song/chorus or funniest moment, sing-along.
- Render each with `python3 render.py episodes/epNNN_short2.json out/epNNN_short2.mp4 vertical` (writes out/epNNN_short2_thumb.jpg).

## Weekly compilation (Sundays)
- `python3 compile.py episodes/compNNN.json "Title" "Thumb Words" "Kids Stories" BG ep001 ep002 ...` builds one long episode with fresh host bridges between stories (ask-and-pause), then
  `HB_CRF=29 python3 render.py episodes/compNNN.json out/compNNN.mp4` (tested: 11 min = 30 MB at crf 26, so use crf 29 to keep ~40 min under GitHub's 100 MB limit; re-encode at crf 31 if still over 95 MB).
- Badge containing "Bedtime" makes night-time breathing bridges (good for bedtime compilations).

## Standard rules for every Short, Reel and video (user, 2026-11-02 — override older notes)
1. **Mobile format:** Shorts/Reels are vertical 9:16, **1080x1920, 30 fps** (`vertical` flag; render.py FPS = 30). All text inside the safe area: x 90–990, below y 220, above y 1500 (platform buttons cover the bottom ~20% and the right edge).
2. **Length:** Shorts/Reels 15–90 s (aim 30–60 s). Check with ffprobe; trim or add a moment if outside.
3. **Closed captions:** render.py burns in big captions of every spoken line, one short phrase at a time (max 6 words vertical / 11 landscape, 1–2 lines), timed from each line's TTS audio: white rounded bold text, dark outline, soft translucent box. Vertical captions sit in the lower-middle safe area (box bottom at y=1490), landscape at the bottom. Captions also show on title-card scenes. A matching `.srt` is written next to each video (`out/<name>.srt`) — commit it to `videos/` beside the video.
   - Preview frames without encoding: `HB_STILLS="2,15,40" python3 render.py episodes/X.json out/X.mp4 vertical` writes `out/X_still_TTT.T.png` (times exclude the 0.5 s cover).
4. **Short post captions:** max 3 short lines (warm hook with one emoji, one lesson line, share line) + the cross-link line + 4–6 hashtags. YouTube Short titles ≤ 60 characters incl. #shorts. YouTube long-video description: 2–3 lines for parents + chapters + cross-link + hashtags.
5. **Ask to share:** every caption includes "💛 Share with a parent who'd love this!" (or close variant), and every Short and full video ends with the narrator saying "Share with a friend and subscribe to Honey Bunny Kidz!" before the closing line (Shorts: then "Watch the full story on Honey Bunny Kidz!").
- Characters stand on the ground line (74% height vertical), so captions cover only their lower bodies; keep faces above y≈1250.
