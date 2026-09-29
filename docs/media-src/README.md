# Where the media comes from

Everything in `docs/media/` that can be rebuilt is rebuilt from here.

| Output | Built by | From |
|---|---|---|
| `in-finder.png`, `hero.png`, `transparency.png`, `palette.png` | `build-stills.py` | the wallpaper, a Finder capture, the icons |
| `redline-dimensions.png`, `redline-detail.png` | `build-redlines.py` | the generator's geometry |
| `fold.mp4`, `fold.gif`, `records.mp4`, `records.gif` | `capture.py` | the fold module, frame by frame |

`anatomy.png`, `sizes.png` and `motion-fold.png` were made earlier and are kept as they are.

## What is in `local/`, and why it is not in the repository

`local/` is ignored by git. It holds sources that are not ours to hand out as files:

- `wallpaper.png`: the system's default desktop picture. It is Apple's. Convert your own with
  `sips -s format png /System/Library/CoreServices/DefaultDesktop.heic --out local/wallpaper.png`
- `finder-window.png`: a real Finder window, captured with `screencapture -l <window id>`.
  The folders in it were staged under `build/stage/` with neutral names, and the sidebar was
  hidden, because a real sidebar lists real folders.
- `icons/`: each colour at 1024, from `styles/crate/generate.py` and `lib/render.sh`.
- `frames/`: the frames of the last recording.

## The rule

Nothing is mocked. The Finder window is Finder. The icons are the icons. The video is the
animation, painted one position at a time, so it runs at the animation's own pace and not at
whatever this machine managed.
