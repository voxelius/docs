"""World schematics: the biome palette and the feature parts."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iso as svg3d
import style
from style import save

INK = style.INK
PAGE = "#7a818a"
RULE = "#5b6168"


PW, PH = 700, 420        # the palette figure
INK = style.INK
PAGE = "#7a818a"
RULE = "#5b6168"

SURFACE = "#6fc652"
FILLER = "#8c6b4a"
BASIC = "#9aa0a6"
FLUID = "#5fa2e0"

CELL = 34
X0, Y0 = 140, 318          # bottom left of the cut
HEIGHTS = [8, 8, 8, 6, 4, 3, 3, 4, 6, 8]
FILLER_DEPTH = 3
SEA = 6                    # sea level, in cells above the base


def text(fig, x, y, s, size=21, anchor="start", fill=PAGE, weight="bold"):
    fig.text(x, y, s, size=size, anchor=anchor, fill=fill, weight=weight,
             casing=0)


def leader(fig, a, b):
    fig.add(f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" '
            f'fill="none" stroke="{style.CASING}" stroke-width="5.5" '
            f'stroke-linecap="round"/>')
    fig.add(f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" '
            f'fill="none" stroke="{RULE}" stroke-width="1.8" '
            f'stroke-linecap="round"/>')
    fig.add(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="4" fill="{RULE}" '
            f'stroke="{style.CASING}" stroke-width="2"/>')


def cell(fig, col, row, fill, opacity=1.0):
    x = X0 + col * CELL
    y = Y0 - (row + 1) * CELL
    fig.add(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{CELL - 1}" '
            f'height="{CELL - 1}" fill="{fill}" fill-opacity="{opacity}"/>')


def palette():
    fig = style.SVG(PW, PH)

    for col, h in enumerate(HEIGHTS):
        for row in range(h):
            if row == h - 1:
                # vox17 gives the top cell `filler` under water, never `surface`
                fill = FILLER if h <= SEA else SURFACE
            elif row >= h - 1 - FILLER_DEPTH:
                fill = FILLER
            else:
                fill = BASIC
            cell(fig, col, row, fill)
        for row in range(h, SEA):
            cell(fig, col, row, FLUID, 0.8)

    # the outline of the cut
    pts = []
    for col, h in enumerate(HEIGHTS):
        x = X0 + col * CELL
        pts.append((x, Y0 - h * CELL))
    pts.append((X0 + len(HEIGHTS) * CELL, Y0 - HEIGHTS[-1] * CELL))
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    fig.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.4" '
            f'stroke-linejoin="round"/>')

    # sea level
    sea_y = Y0 - SEA * CELL
    fig.add(f'<path d="M {X0 - 18},{sea_y} L {X0 + len(HEIGHTS) * CELL + 6},{sea_y}" '
            f'fill="none" stroke="{style.CASING}" stroke-width="6"/>')
    fig.add(f'<path d="M {X0 - 18},{sea_y} L {X0 + len(HEIGHTS) * CELL + 6},{sea_y}" '
            f'fill="none" stroke="{RULE}" stroke-width="1.6" '
            f'stroke-dasharray="8 6"/>')
    text(fig, X0 - 26, sea_y + 7, "sea level", 19, anchor="end", fill=PAGE,
         weight="normal")

    # the four fields, with leaders into the cut
    lx = X0 + len(HEIGHTS) * CELL + 34

    def at(col, row, label, yoff=0):
        cx = X0 + col * CELL + CELL / 2
        cy = Y0 - row * CELL - CELL / 2
        fig.add(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{RULE}" '
                f'stroke="{style.CASING}" stroke-width="2"/>')
        fig.add(f'<path d="M {cx},{cy} L {lx - 8},{cy + yoff}" fill="none" '
                f'stroke="{style.CASING}" stroke-width="5.5"/>')
        fig.add(f'<path d="M {cx},{cy} L {lx - 8},{cy + yoff}" fill="none" '
                f'stroke="{RULE}" stroke-width="1.8"/>')
        text(fig, lx, cy + yoff + 7, label, 21)

    at(1, 7, "surface")
    at(1, 6, "filler")
    at(1, 1, "basic")
    at(5, 4, "fluid")

    text(fig, X0 + len(HEIGHTS) * CELL / 2, Y0 + 46,
         "Under water the top cell is filler.", 18, anchor="middle",
         fill=PAGE, weight="normal")

    save(fig.to_string(), "biome-palette.svg")


# ---- feature.md ------------------------------------------------------
FW = 760                  # the feature figure
DIRT = (139, 107, 74)
LOG = (107, 74, 47)
LEAF = (79, 158, 58)

PALETTE = [(DIRT, "dirt"), (LOG, "oak_log"), (LEAF, "oak_leaves")]

PARTS = [
    (0, (0, 0, 0)),                                    # replaces the turf
    (1, (0, 1, 0)), (1, (0, 2, 0)), (1, (0, 3, 0)),
    (2, (-1, 3, 0)), (2, (1, 3, 0)), (2, (0, 3, -1)), (2, (0, 3, 1)),
    (2, (0, 4, 0)), (2, (-1, 4, 0)), (2, (1, 4, 0)),
    (2, (0, 4, -1)), (2, (0, 4, 1)),
    (2, (0, 5, 0)),
]


def feature():
    cam = svg3d.Camera(elevation=30)

    def build():
        s = svg3d.Scene(cam.dir)
        for index, off in PARTS:
            lo = (off[0], off[1], off[2])
            hi = (off[0] + 1, off[1] + 1, off[2] + 1)
            s.box(lo, hi, PALETTE[index][0], edge_px=5)
        return s

    # the scene sits left of the callout column
    geom, pr, H = svg3d.render(build, cam, width=FW, margin=0.08,
                               extra=(226, 244, 30, 40))

    def tail(fig, pr):
        FACES = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))

        def near_face(off, target):
            """The middle of the visible side of the block that faces the plate."""
            best = None
            for n in FACES:
                if sum(n[i] * cam.dir[i] for i in range(3)) <= 1e-6:
                    continue
                c = (off[0] + 0.5 + n[0] * 0.5,
                     off[1] + 0.5 + n[1] * 0.5,
                     off[2] + 0.5 + n[2] * 0.5)
                q = pr(c)
                d = (q[0] - target[0]) ** 2 + (q[1] - target[1]) ** 2
                if best is None or d < best[0]:
                    best = (d, q)
            return best[1]

        def chip_at(off, text, at, anchor="start", size=16):
            """A callout that joins the side of a block and the side of a plate."""
            w = len(text) * size * 0.62 + 20
            left = at[0] - 10 if anchor == "start" else at[0] - w + 10
            edge = left if pr((off[0] + 0.5, off[1] + 0.5, off[2] + 0.5))[0] < left else left + w
            p = near_face(off, (edge, at[1]))
            w = len(text) * size * 0.62 + 20
            fig.leader(p, (edge, at[1]))
            fig.chip(at[0], at[1], text, size=size, anchor=anchor)

        chip_at((0, 4, -1), "palette 2, [0, 4, -1]", (26, 312))
        chip_at((0, 1, 0), "palette 1, [0, 1, 0]", (500, H - 150))
        chip_at((0, 0, 0), "origin: the ground block", (300, H - 46),
                anchor="end")

        lx, ly = 26, 30
        fig.text(lx, ly, "palette", 18, anchor="start", casing=0)
        for i, (colour, name) in enumerate(PALETTE):
            y = ly + 34 + i * 34
            fig.add(f'<rect x="{lx}" y="{y - 16}" width="24" height="24" rx="3" '
                    f'fill="{style.rgb(colour)}"/>')
            fig.text(lx + 34, y + 4, f"{i}  {name}", 17, anchor="start", casing=0)
        fig.text(lx, ly + 34 + 3 * 34 + 16, "overwrite: turf", 16,
                 anchor="start", weight="normal")

    style.write_figure(geom, pr, H, "feature-parts.svg", tail, width=FW)
    save(style.OUTPUTS.pop("feature-parts.svg"), "feature-parts.svg")
