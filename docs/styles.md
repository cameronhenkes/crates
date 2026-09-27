# Writing a style

A style is a directory under `styles/` containing `style.json`. It can either
generate artwork from a colour, or ship pre-made icons.

## Pre-made icons

The simplest kind. Drop `.icns` files in an `icons/` directory and name them
after the variant:

```
styles/mystyle/
├── style.json
└── icons/
    ├── red.icns
    └── blue.icns
```

```json
{ "name": "mystyle", "label": "My icons" }
```

Then `crates apply mystyle:red ~/Documents`.

## Generated artwork

A generated style draws SVG from a colour, which is what makes arbitrary
hexes work (`crates apply mystyle:#7B9E89 ~/Notes`).

```
styles/mystyle/
├── style.json
├── generate.py       any executable, any language
└── palette.json      named colours
```

```json
{
  "name": "mystyle",
  "label": "My generated style",
  "generator": "generate.py",
  "palette": "palette.json"
}
```

`palette.json` maps a variant name to a colour:

```json
{ "moss": { "hex": "#7B9E89", "label": "Moss" } }
```

### The generator contract

`crates` calls your generator twice, and expects an SVG written to `-o`:

```bash
./generate.py "#7B9E89" --name moss -o out.svg                    # full detail
./generate.py "#7B9E89" --name moss --detail simple -o out.svg    # small sizes
```

If your generator doesn't understand `--detail simple`, it should exit
non-zero for that call — `crates` falls back to using the full artwork at
every size. That works, it just gets muddy at 16 and 32px.

Draw into a **1024×1024** viewBox on a transparent background. macOS folder
icons are wider than they are tall, so leave the top and bottom empty rather
than filling the square.

### Why two detail levels

Below about 48px, fine detail stops being detail and becomes grey haze. A
16px icon can carry a silhouette and maybe three or four marks. Apple draws
simplified versions of its own icons for these slots, and the difference is
the difference between a recognisable folder and a smudge.

`crates` uses your simple variant for the 16 and 32px slots and the full
artwork from 64px up.

### Testing

```bash
crates build mystyle          # build every variant
crates apply mystyle:moss /tmp/test-folder
```

There's no preview command — open the folder in Finder and look at it at a
few icon sizes. The Finder sidebar and list views are where small sizes
actually get used, so check those rather than only the desktop.
