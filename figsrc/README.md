# figure sources

The scripts that render the SVG figures under `src/`. Every figure is
generated text: there is no raster step, no image editor and no binary source
to keep in sync.

```sh
python figsrc/render.py            # every figure, into the page that uses it
python figsrc/render.py bcoll-shapes block-target   # only these two
```

Needs Python 3 and `numpy`. Nothing else: the SVG is written as text.

## Layout

|File|Contents|
|----|----|
|`render.py`|Entry point. Maps a figure to the page directory it belongs to|
|`style.py`|The SVG writer, the palette and the font stack|
|`iso.py`|Isometric camera, box geometry, painter's algorithm, callout helpers|
|`blocks.py`|Block shapes, slab and log orientation, the hit target, the model grid|
|`charts.py`|The climate square, the flow levels, the precipitation bands|
|`facing.py`|The six `facing-*` illustrations of the block API page|

A figure function calls `save(text, name)`, and `render.py` writes the result
next to the page. An image sits beside the page that uses it, as
`src/modding/api/facing-north.svg` does.

## Why it is drawn by hand

The book has a light and a dark theme, and the figures have a transparent
background. Every piece of ink therefore carries its own casing: text has a
white outline, arrows have a white casing, and callout lines are red so that
they read on a grey block and on a dark page alike.

Text that belongs to a face is not placed on the screen. It is placed in the
face plane with an SVG `matrix()`, so it foreshortens with the face the way a
block texture does.

## Adding a figure

1. Write the function in `blocks.py` or `charts.py`. Hand the SVG to `save` at
   the end of it.
2. Add the name to `FIGURES` in `render.py` and to `DESTINATIONS`.
3. Render, then look at the page with `mdbook build` or `mdbook serve`.
