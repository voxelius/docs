"""Block figures: shapes, orientations, a hit target and a model grid.

Geometry goes through iso.py, the SVG text through style.py.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iso as svg3d
import style as svg
from iso import below, face_text, plate, wire
from style import (RED, STONE, WATER, WATER_TOP, WOOD, WOOD_END, save,
                   write_figure)

W = 1100


def cell_edges(lo=(0, 0, 0), hi=(1, 1, 1)):
    """The twelve edges of a cell, as endpoints."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    for y in (y0, y1):
        for z in (z0, z1):
            yield (x0, y, z), (x1, y, z)
    for x in (x0, x1):
        for z in (z0, z1):
            yield (x, y0, z), (x, y1, z)
    for x in (x0, x1):
        for y in (y0, y1):
            yield (x, y, z0), (x, y, z1)


# ------------------------------------------------------------------ bcoll
def bcoll_shapes():
    cam = svg3d.Camera(elevation=30)
    sp = 1.80

    def build():
        s = svg3d.Scene(cam.dir)
        for i in range(3):
            p = cam.right() * (i * sp)
            cx, cz = p[0], p[2]
            plate(s, cx, cz)
            if i == 0:
                s.box((cx, 0, cz), (cx + 1, 1, cz + 1), STONE, edge_px=7)
            elif i == 1:
                s.box((cx, 0, cz), (cx + 1, 0.5, cz + 1), STONE, edge_px=7)
            else:
                s.box((cx, 0, cz), (cx + 1, 0.5, cz + 1), STONE, edge_px=7)
                s.box((cx, 0.5, cz), (cx + 0.5, 1, cz + 1), STONE, edge_px=7)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.10, extra=(0, 0, 0, 70))

    def tail(fig, pr):
        for i, name in enumerate(("cube", "slab", "stairs")):
            p = cam.right() * (i * sp)
            below(fig, pr, p[0], p[2], name)

    write_figure(geom, pr, H, "bcoll-shapes.svg", tail)


# ------------------------------------------------------------------ slabs
def slabs_orientation():
    cam = svg3d.Camera(elevation=30)
    sp = 1.80

    def build():
        s = svg3d.Scene(cam.dir)
        p = cam.right() * 0
        plate(s, p[0], p[2])
        s.box((p[0], 0, p[2]), (p[0] + 1, 0.5, p[2] + 1), STONE, edge_px=7)
        s.box((p[0], 0.5, p[2]), (p[0] + 1, 1, p[2] + 1), WATER,
              faces={(0, 1, 0): WATER_TOP}, edge_px=6)
        p = cam.right() * sp
        plate(s, p[0], p[2])
        s.box((p[0], 0.5, p[2]), (p[0] + 1, 1, p[2] + 1), STONE, edge_px=7)
        s.box((p[0], 0, p[2]), (p[0] + 1, 0.5, p[2] + 1), WATER,
              faces={(0, 1, 0): WATER_TOP}, edge_px=6)
        p = cam.right() * (2 * sp)
        plate(s, p[0], p[2])
        s.box((p[0], 0, p[2]), (p[0] + 1, 1, p[2] + 1), STONE, edge_px=7)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.10, extra=(0, 0, 0, 70))

    def tail(fig, pr):
        for i, name in enumerate(("bottom", "top", "double")):
            p = cam.right() * (i * sp)
            below(fig, pr, p[0], p[2], name)
        p = cam.right() * 0
        face_text(fig, cam, (p[0] + 0.5, 1.0, p[2] + 0.5), (0, 1, 0), 0.20, pr,
                  "fluid", fill="#0d2a56")

    write_figure(geom, pr, H, "slabs-orientation.svg", tail)


# ------------------------------------------------------------------ logs
def logs_orientation():
    cam = svg3d.Camera(elevation=30)
    sp = 1.80

    RINGS = [(0.10, (232, 217, 187)), (0.17, (223, 205, 170)),
             (0.23, (238, 227, 201)), (0.29, (212, 193, 156))]

    def caps(axis, x0, y0, z0, n, e):
        """The two end caps of a log, inset by n and lifted by e."""
        if axis == "z":
            return [((x0 + n, y0 + n, z0 - e), (x0 + 1 - n, y0 + 1 - n, z0)),
                    ((x0 + n, y0 + n, z0 + 1), (x0 + 1 - n, y0 + 1 - n, z0 + 1 + e))]
        if axis == "x":
            return [((x0 - e, y0 + n, z0 + n), (x0, y0 + 1 - n, z0 + 1 - n)),
                    ((x0 + 1, y0 + n, z0 + n), (x0 + 1 + e, y0 + 1 - n, z0 + 1 - n))]
        return [((x0 + n, y0 - e, z0 + n), (x0 + 1 - n, y0, z0 + 1 - n)),
                ((x0 + n, y0 + 1, z0 + n), (x0 + 1 - n, y0 + 1 + e, z0 + 1 - n))]

    def log(s, lo, axis):
        x0, y0, z0 = lo
        s.box((x0, y0, z0), (x0 + 1, y0 + 1, z0 + 1), WOOD, edge_px=7)
        # concentric plates read as growth rings on the cut face
        for k, (n, col) in enumerate(RINGS):
            e = 0.008 + k * 0.004
            for lo2, hi2 in caps(axis, x0, y0, z0, n, e):
                s.box(lo2, hi2, col, edges=False, flat=True)

    def build():
        s = svg3d.Scene(cam.dir)
        for i, axis in enumerate(("z", "x", "y")):
            p = cam.right() * (i * sp)
            plate(s, p[0], p[2])
            log(s, (p[0], 0, p[2]), axis)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.10, extra=(0, 0, 0, 70))

    def tail(fig, pr):
        for i, name in enumerate(("north", "east", "up")):
            p = cam.right() * (i * sp)
            below(fig, pr, p[0], p[2], name)

    write_figure(geom, pr, H, "logs-orientation.svg", tail)


# ------------------------------------------------------------------ fluids
def fluids_gravity():
    cam = svg3d.Camera(elevation=30)
    sp = 1.95

    def build():
        s = svg3d.Scene(cam.dir)
        p = cam.right() * 0
        plate(s, p[0], p[2])
        wire(s, (p[0], 0, p[2]), (p[0] + 1, 1, p[2] + 1), 2.6, (150, 156, 163))
        s.box((p[0], 0, p[2]), (p[0] + 1, 0.68, p[2] + 1), WATER,
              faces={(0, 1, 0): WATER_TOP}, edge_px=6)
        p = cam.right() * sp
        plate(s, p[0], p[2])
        wire(s, (p[0], 0, p[2]), (p[0] + 1, 1, p[2] + 1), 2.6, (150, 156, 163))
        s.box((p[0], 0.32, p[2]), (p[0] + 1, 1, p[2] + 1), WATER,
              faces={(0, 1, 0): WATER_TOP}, edge_px=6)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.10, extra=(0, 0, 0, 70))

    def tail(fig, pr):
        for i, name in enumerate(("fluids.GRAVITY_DOWN", "fluids.GRAVITY_UP")):
            p = cam.right() * (i * sp)
            below(fig, pr, p[0], p[2], name, size=28)

    write_figure(geom, pr, H, "fluids-gravity.svg", tail)


# ------------------------------------------------------------------ target
def block_target():
    cam = svg3d.Camera(elevation=34)
    hit = (0.62, 1.0, 0.36)
    tip = (0.62, 1.56, 0.36)
    eye = (1.22, 1.82, 0.30)

    def build():
        s = svg3d.Scene(cam.dir)
        s.box((0, 0, 0), (1, 1, 1), STONE, edge_px=7)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.20,
                               extra=(70, 70, 60, 50), aspect=1.25,
                               points=[eye, tip, hit])

    def tail(fig, pr):
        ph = pr(hit)
        pt = pr(tip)
        pe = pr(eye)
        box = [pr((x, y, z)) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
        x0 = min(b[0] for b in box)
        x1 = max(b[0] for b in box)
        y0 = min(b[1] for b in box)
        y1 = max(b[1] for b in box)

        fig.arrow(pe, ph, shaft=7, head=22)
        fig.arrow(ph, pt, shaft=7, head=22)
        fig.circle(ph[0], ph[1], 8, fill=RED, stroke="#ffffff", width=3)

        # every label sits in the margin beside the silhouette, never on it
        fig.chip(pe[0] - 20, pe[1] + 6, "ray", size=25, anchor="end")
        pm = ((ph[0] + pt[0]) / 2.0, (ph[1] + pt[1]) / 2.0)
        fig.leader(pm, (x1 + 20, pm[1] - 16))
        fig.chip(x1 + 26, pm[1] - 22, "normal", size=25, anchor="start")

        fig.leader(ph, (x1 + 20, ph[1] - 10))
        fig.chip(x1 + 26, ph[1], "point (lx, ly, lz)", size=25, anchor="start")

        c = pr((0.0, 0.0, 1.0))
        fig.circle(c[0], c[1], 8, fill=RED, stroke="#ffffff", width=3)
        fig.leader(c, (x0 - 18, y1 - 10))
        fig.chip(x0 - 24, y1, "bpos (bx, by, bz)", size=25, anchor="end")

        f = pr((0.10, 1.0, 0.10))
        fig.circle(f[0], f[1], 8, fill=RED, stroke="#ffffff", width=3)
        fig.leader(f, (x0 - 18, f[1]))
        fig.chip(x0 - 24, f[1] + 12, "face = FACE_TOP", size=25, anchor="end")

    write_figure(geom, pr, H, "block-target.svg", tail)


# ------------------------------------------------------------------ bmodel
def bmodel_grid():
    cam = svg3d.Camera(elevation=34)
    N = 16
    LO = (2 / N, 0.0, 5 / N)
    HI = (11 / N, 7 / N, 14 / N)
    MINOR = (198, 204, 210)
    MAJOR = (170, 177, 185)
    EDGE = (120, 128, 138)

    def style(i):
        """Every fourth line is a major one, so the eye can count sixteenths."""
        if i % 4:
            return (1.0, MINOR, 0.30)
        return (1.6, MAJOR, 0.45)

    def plane(fn, s, fixed):
        for i in range(N + 1):
            t = i / N
            w, col, op = style(i)
            for a, b in fn(t, fixed):
                s.bar(a, b, w, col, opacity=op)

    def build():
        s = svg3d.Scene(cam.dir)
        # three grid planes and no fills: the cell reads as graph paper
        plane(lambda t, z: (((t, 0, z), (t, 1, z)), ((0, t, z), (1, t, z))), s, 1.0)
        plane(lambda t, x: (((x, 0, t), (x, 1, t)), ((x, t, 0), (x, t, 1))), s, 1.0)
        plane(lambda t, y: (((t, y, 0), (t, y, 1)), ((0, y, t), (1, y, t))), s, 0.0)
        for a, b in cell_edges():
            s.bar(a, b, 2.4, EDGE, opacity=0.75)
        s.box(LO, HI, STONE, edge_px=7)
        return s

    geom, pr, H = svg3d.render(build, cam, width=W, margin=0.06,
                               extra=(80, 80, 70, 70), aspect=1.25)

    def tail(fig, pr):
        pmin = pr(LO)
        pmax = pr(HI)
        fig.circle(pmin[0], pmin[1], 8, fill="#e0524e", stroke="#ffffff", width=3)
        fig.leader(pmin, (pmin[0] - 54, pmin[1] + 62))
        fig.chip(pmin[0] - 62, pmin[1] + 76, "min [2, 0, 5]", size=26, anchor="end")
        fig.circle(pmax[0], pmax[1], 8, fill="#e0524e", stroke="#ffffff", width=3)
        fig.leader(pmax, (pmax[0] + 46, pmax[1] - 62))
        fig.chip(pmax[0] + 52, pmax[1] - 66, "max [11, 7, 14]", size=26, anchor="start")

    write_figure(geom, pr, H, "bmodel-grid.svg", tail)
