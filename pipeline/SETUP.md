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
cp /home/claude/honeybunny-media/pipeline/*.py /home/claude/hb/
mkdir -p /home/claude/hb/episodes && cp /home/claude/honeybunny-media/pipeline/episodes/*.json /home/claude/hb/episodes/

# 4. render
cd /home/claude/hb
python3 render.py episodes/epNNN.json out/epNNN_full.mp4
python3 render.py episodes/epNNN_short.json out/epNNN_short.mp4 vertical
```

## Building blocks available
- Backgrounds (art.background): `day`, `night`, `oak`, `bedroom` — add new ones in art.py as needed (e.g. beach, garden, farm, snow).
- Characters (art.CHARS): `honey` (bunny, pink bow), `mama` (Mama Bunny), `dotty` (duckling), `ollie` (owl), `moon`. Add new cute characters in art.py following the same pattern (eyes open/closed, mouth 0/1/2).
- Voices (render.VOICES): narrator af_heart, honey af_sky, mama af_bella, dotty af_nicole, ollie bm_fable, moon bm_george. New characters need a voice entry.
- Episode JSON: scenes with bg, optional title/subtitle (title card), cast [{id,x,y,scale,flip,sleep}], lines [{who,text,pause}].
- Bedroom: Honey in bed uses x=0.300, y=0.903 (landscape).
- Unknown words: tts.MISSING lists them; add phonemes to the D.update({...}) line in tts.py.
