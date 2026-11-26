"""Architecture diagrams: the frame pipeline of the rendering page."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import style
from style import save

W, H = 700, 810
INK = style.INK
MUTED = "#5b6168"

# The nodes are opaque, so the text inside them needs no outline and reads on
# any backdrop.  The arrows and the few labels between the nodes sit on the
# page, and those keep the soft outline the other figures use.
NODE = "#eaeef2"
NODE_EDGE = "#a8b1bb"

# Anonymous Pro is monospaced at 0.6 em, which is enough to check the layout
CHAR = 0.6


def text(fig, x, y, s, size=20, anchor="start", fill=INK, casing=None,
         weight="bold", rotate=None):
    fig.text(x, y, s, size=size, anchor=anchor, fill=fill, weight=weight,
             casing=casing, rotate=rotate)
    return len(s) * CHAR * size


def node(fig, x, y, w, h, title, note=None, strong=False):
    fig.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
            f'fill="{NODE}" stroke="{INK if strong else NODE_EDGE}" '
            f'stroke-width="{2.4 if strong else 1.6}"/>')
    text(fig, x + 16, y + h / 2 + 7, title, 22, casing=0)
    if note:
        text(fig, x + w - 16, y + h / 2 + 6, note, 17, anchor="end", fill=MUTED,
             weight="normal", casing=0)


def arrow(fig, a, b, width=2.6, colour=INK, head=13):
    fig.arrow(a, b, shaft=width, head=head, fill=colour, casing=2.5)


RULE = "#5b6168"


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
        ("Clouds", "borrows depth"),
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

    # the diffuse depth is copied into every other layer
    spine = rx + rw + 26
    for c in centres:
        dashed(fig, (rx + rw, c), (spine, c))
    dashed(fig, (spine, centres[0]), (spine, centres[-1]))
    text(fig, spine + 16, centres[len(centres) // 2], "depth copy", 17,
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
    text(fig, 116, ly + 6, "colour texture", 17, fill=MUTED, weight="normal")
    dashed(fig, (296, ly), (352, ly))
    text(fig, 364, ly + 6, "depth copy", 17, fill=MUTED, weight="normal")

    save(fig.to_string(), "frame-pipeline.svg")


if __name__ == "__main__":
    pipeline()
