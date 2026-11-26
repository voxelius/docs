"""Architecture diagrams: the frame pipeline, the cloud rings and the core page."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import style
from style import save

W, H = 700, 810
RW, RH = 760, 452        # the ring figure is a square plus a key
INK = style.INK
MUTED = "#5b6168"

# The nodes are opaque, so the text inside them needs no outline and reads on
# any backdrop.  The arrows and the few labels between the nodes sit on the
# page, and those keep the soft outline the other figures use.
NODE = "#eaeef2"
NODE_EDGE = "#a8b1bb"
RULE = "#5b6168"
# Text that sits on the page rather than on a filled node: a mid grey reads on
# both themes, and unlike a black glyph with a white outline it stays crisp.
PAGE = "#7a818a"

# Anonymous Pro is monospaced at 0.6 em, which is enough to check the layout
CHAR = 0.6


def text(fig, x, y, s, size=20, anchor="start", fill=PAGE, casing=0,
         weight="bold", rotate=None):
    fig.text(x, y, s, size=size, anchor=anchor, fill=fill, weight=weight,
             casing=casing, rotate=rotate)
    return len(s) * CHAR * size


def node(fig, x, y, w, h, title, note=None, strong=False):
    fig.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
            f'fill="{NODE}" stroke="{INK if strong else NODE_EDGE}" '
            f'stroke-width="{2.4 if strong else 1.6}"/>')
    text(fig, x + 16, y + h / 2 + 7, title, 22, fill=INK)
    if note:
        text(fig, x + w - 16, y + h / 2 + 6, note, 17, anchor="end", fill=MUTED,
             weight="normal")


def arrow(fig, a, b, width=2.6, colour=INK, head=13):
    fig.arrow(a, b, shaft=width, head=head, fill=colour, casing=2.5)




def cased_path(fig, d, colour=RULE, width=2.0, dash=None, fill="none"):
    """A structural line over a light casing.

    A light grey line reads on a dark page and vanishes on a light one; a dark
    line does the opposite.  The pair reads on both.
    """
    fig.add(f'<path d="{d}" fill="{fill}" stroke="{style.CASING}" '
            f'stroke-width="{width + 4}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    fig.add(f'<path d="{d}" fill="{fill}" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round"{extra}/>')


def dashed(fig, a, b, width=2.2, colour="#6f777f"):
    """A dashed line with the same casing as a solid one, so the gaps do not
    decide how well it reads on a grey or a dark backdrop."""
    cased_path(fig, f'M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}',
               colour=colour, width=width, dash="9 7")


def pipeline():
    # Portrait: the column of the book is 750 px, so a 700 px wide figure is
    # shown almost 1:1 and the labels keep the size of the body text.
    rows = [
        ("Diffuse", "opaque + depth"),
        ("Clouds", "own depth range"),
        ("Alpha", "leaves, glass"),
        ("Fluid", "water, lava"),
        ("Precip", "camera quads"),
    ]
    rx, rw, rh, gap = 90, 510, 54, 14
    ys = [110 + i * (rh + gap) for i in range(len(rows))]
    centres = [y + rh / 2 for y in ys]
    last = ys[-1] + rh
    CH = 148                           # height of the composite box
    cy = last + 82                     # top of the composite
    by = cy + CH + 22                  # top of the backbuffer row
    H = by + 92 + 24 + 46 + 16         # backbuffer row, gap, legend, margin
    fig = style.SVG(W, H)

    # the frame feeds one pass per layer, down a bus on the left
    node(fig, 30, 20, 660, 56, "Frame", "five passes")
    cased_path(fig, f"M 52,76 L 52,{centres[-1]}")
    for y, c in zip(ys, centres):
        arrow(fig, (52, c), (rx - 4, c), width=2.0, head=10)
        node(fig, rx, y, rw, rh, rows[ys.index(y)][0], rows[ys.index(y)][1])

    # the diffuse depth is copied into the translucent layers; the clouds keep a
    # depth range of their own and the composite compares the two
    spine = rx + rw + 26
    translucent = centres[2:]
    # the source sits above the clouds, so its stubs go out at a right angle and
    # the bus runs past that row without a stub of its own
    dashed(fig, (rx + rw, centres[0]), (spine, centres[0]))
    dashed(fig, (spine, centres[0]), (spine, translucent[-1]))
    for c in translucent:
        dashed(fig, (rx + rw, c), (spine, c))
    text(fig, spine + 16, (centres[2] + translucent[-1]) / 2, "depth copy", 17,
         anchor="middle", fill=MUTED, weight="normal", rotate=-90)

    # every layer goes into the composite
    cased_path(fig, f"M {rx},{last + 40} L {rx},{last + 52} L {rx + rw},{last + 52} "
                    f"L {rx + rw},{last + 40}")
    arrow(fig, (rx + rw / 2, last + 52), (rx + rw / 2, last + 82))

    fig.add(f'<rect x="{rx}" y="{cy}" width="{rw}" height="{CH}" rx="6" '
            f'fill="{NODE}" stroke="{INK}" stroke-width="2.4"/>')
    text(fig, rx + rw / 2, cy + 32, "Composite", 22, anchor="middle", casing=0)
    for i, line in enumerate(("one full-screen triangle",
                              "sorts the layers by depth",
                              "blends them far to near",
                              "precipitation over the result",
                              "renders at the internal resolution")):
        text(fig, rx + rw / 2, cy + 60 + i * 18, line, 15, anchor="middle",
             fill=MUTED, weight="normal", casing=0)

    # the result is upscaled into the window, and ImGui draws on top
    arrow(fig, (rx + rw / 2, cy + CH), (rx + rw / 2, cy + CH + 22))

    fig.add(f'<rect x="{rx}" y="{by}" width="280" height="92" rx="6" '
            f'fill="{NODE}" stroke="{NODE_EDGE}" stroke-width="1.6"/>')
    text(fig, rx + 140, by + 32, "Backbuffer", 22, anchor="middle", casing=0)
    text(fig, rx + 140, by + 56, "window size", 16, anchor="middle", fill=MUTED,
         weight="normal", casing=0)
    text(fig, rx + 140, by + 76, "nearest upscale", 16, anchor="middle", fill=MUTED,
         weight="normal", casing=0)

    gx = rx + 340
    fig.add(f'<rect x="{gx}" y="{by}" width="170" height="92" rx="6" '
            f'fill="{NODE}" stroke="{NODE_EDGE}" stroke-width="1.6"/>')
    text(fig, gx + 85, by + 36, "ImGui", 22, anchor="middle", casing=0)
    text(fig, gx + 85, by + 60, "on top", 16, anchor="middle", fill=MUTED,
         weight="normal", casing=0)
    arrow(fig, (gx, by + 46), (rx + 284, by + 46))

    # legend
    fig.add(f'<rect x="28" y="{H - 70}" width="470" height="46" rx="8" '
            f'fill="none" stroke="{style.CASING}" stroke-width="5"/>')
    fig.add(f'<rect x="30" y="{H - 68}" width="466" height="42" rx="8" '
            f'fill="none" stroke="{RULE}" stroke-width="1.8"/>')
    ly = H - 41
    arrow(fig, (48, ly), (104, ly), width=2.4, head=11)
    text(fig, 116, ly + 6, "colour texture", 17, fill=PAGE, weight="normal")
    dashed(fig, (296, ly), (352, ly))
    text(fig, 364, ly + 6, "depth copy", 17, fill=PAGE, weight="normal")

    save(fig.to_string(), "frame-pipeline.svg")


if __name__ == "__main__":
    pipeline()


# ---- cloud deck rings -------------------------------------------------
# name, second line, tint, outer half-side in pixels
RINGS = [
    ("0-512 blocks", "32 chunks, 8 per cell", "#e6eef9", 56),
    ("512-1536 blocks", "96 chunks, 32 per cell", "#c4dbef", 112),
    ("1536-4096 blocks", "256 chunks, 128 per cell", "#9cc1e2", 168),
]
BAND = 56
SEAM = "#7fa8cd"


def cloud_rings():
    """The deck seen from above: three rings with a growing cell.

    The drawing is a schematic.  The outer ring really reaches eight times
    further than the inner one, and to scale the middle ring would be a line.
    """
    fig = style.SVG(RW, RH)
    cx, cy = 180, 262

    # one stroked square per ring: the stroke is the band it covers
    for _, _, tint, outer in RINGS:
        half = outer - BAND / 2
        fig.add(f'<rect x="{cx - half}" y="{cy - half}" width="{2 * half}" '
                f'height="{2 * half}" fill="none" stroke="{tint}" '
                f'stroke-width="{BAND}" stroke-linejoin="miter"/>')

    # a line on every seam, or the bands read as one flat square
    for _, _, _, outer in RINGS:
        half = outer - BAND / 2
        fig.add(f'<rect x="{cx - half}" y="{cy - half}" width="{2 * half}" '
                f'height="{2 * half}" fill="none" stroke="{SEAM}" '
                f'stroke-width="1.2"/>')

    # the camera sits at the middle of the innermost ring
    fig.add(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{INK}" '
            f'stroke="{style.CASING}" stroke-width="3"/>')
    text(fig, cx, cy + 30, "camera", 19, anchor="middle", fill=MUTED,
         weight="normal")

    # the seam between the two inner rings, where they overlap by one cell
    sx, sy = cx + RINGS[0][3], cy - RINGS[0][3]
    cased_path(fig, f"M {sx},{sy} L {sx + 30},{sy - 18}")
    text(fig, sx + 36, sy - 24, "seam", 19, fill=PAGE, weight="normal")

    # the key
    lx, ly = 380, 108
    for i, (name, detail, tint, _) in enumerate(RINGS):
        y = ly + i * 74
        fig.add(f'<rect x="{lx}" y="{y - 17}" width="28" height="28" rx="4" '
                f'fill="{tint}"/>')
        text(fig, lx + 42, y + 2, name, 20)
        text(fig, lx + 42, y + 26, detail, 19, fill=PAGE, weight="normal")

    for i, line in enumerate(("Rings overlap by two cells.",
                              "The coarse ring is meshed first.",
                              "Not to scale.")):
        text(fig, lx, 330 + i * 32, line, 19, fill=PAGE, weight="normal")

    save(fig.to_string(), "cloud-rings.svg")


# ---- core.md ---------------------------------------------------------
def stage_box(fig, x, y, w, h, title, size=17, strong=False):
    """A box with its label in the middle."""
    fig.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
            f'fill="{NODE}" stroke="{INK if strong else NODE_EDGE}" '
            f'stroke-width="{2.2 if strong else 1.6}"/>')
    text(fig, x + w / 2, y + h / 2 + 6, title, size, anchor="middle", fill=INK)


def stages():
    """init -> config -> init_late, as the client registers them."""
    W, H = 700, 470
    fig = style.SVG(W, H)

    # the config stage names real files, so its boxes are wider
    rows = [
        ("init", [118, 118, 118, 118, 118], ["net", "mods", "render", "atlas", "gui"],
         "the subsystems start, in this order"),
        ("config", [190, 190], ["client.conf", "client.user.conf"],
         "the two files are read here, in this order"),
        ("init_late", [118, 118, 118, 118], ["video", "assets", "world", "menu"],
         "the values that other subsystems depend on are applied"),
    ]
    bh, gap = 46, 10
    x0, y, pitch = 40, 70, 130
    for r, (phase, widths, items, note) in enumerate(rows):
        top = y + r * pitch
        text(fig, x0, top - 14, phase, 20, fill=PAGE)
        x = x0
        for w, item in zip(widths, items):
            stage_box(fig, x, top, w, bh, item)
            x += w + gap
        text(fig, x0, top + bh + 26, note, 15, fill=PAGE, weight="normal")

    # one spine on the left, in the margin: arrows between the rows would run
    # through the note under each row
    arrow(fig, (18, y), (18, y + 2 * pitch + bh), width=2.0, head=12)

    text(fig, x0, H - 24,
         "The stages run one by one, with the boot screen between them.",
         15, fill=PAGE, weight="normal")

    save(fig.to_string(), "boot-stages.svg")


def resources():
    """Request, cache and the two purges."""
    W, H = 700, 520
    fig = style.SVG(W, H)

    stage_box(fig, 40, 24, 170, 42, "load(id)")
    arrow(fig, (125, 66), (125, 90))
    stage_box(fig, 40, 90, 250, 44, "in the registry?")
    arrow(fig, (290, 112), (356, 112))
    text(fig, 300, 100, "yes", 14, fill=MUTED, weight="normal")
    fig.add(f'<rect x="360" y="90" width="300" height="44" rx="6" '
            f'fill="{NODE}" stroke="{INK}" stroke-width="2.2"/>')
    text(fig, 510, 118, "return the handle", 17, anchor="middle", fill=INK)
    arrow(fig, (125, 134), (125, 166))
    text(fig, 133, 156, "no", 14, fill=MUTED, weight="normal")

    stage_box(fig, 40, 166, 250, 44, "load_fn(path)")
    arrow(fig, (125, 210), (125, 242))
    stage_box(fig, 40, 242, 250, 46, "store it in the registry")

    # both paths end at the same return
    fig.add(f'<path d="M 290,265 L 330,265 L 330,112" fill="none" '
            f'stroke="{style.CASING}" stroke-width="6"/>')
    fig.add(f'<path d="M 290,265 L 330,265 L 330,112" fill="none" stroke="{RULE}" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')

    text(fig, 40, 316, "RESFLAG_CACHE also pushes the handle into the cache,",
         15, fill=PAGE, weight="normal")
    text(fig, 40, 338, "which then owns a reference of its own.", 15, fill=PAGE,
         weight="normal")

    # the two purges
    for i, (title, when, what) in enumerate((
            ("soft purge", "runs after every frame",
             "drops what nothing else holds"),
            ("hard purge", "runs at shutdown",
             "drops everything, warns if in use"))):
        x = 40 + i * 340
        fig.add(f'<rect x="{x}" y="380" width="320" height="100" rx="6" '
                f'fill="{NODE}" stroke="{NODE_EDGE}" stroke-width="1.6"/>')
        text(fig, x + 20, 412, title, 19, fill=INK)
        text(fig, x + 20, 438, when, 15, fill=MUTED, weight="normal")
        text(fig, x + 20, 462, what, 15, fill=MUTED, weight="normal")

    save(fig.to_string(), "resource-life.svg")
