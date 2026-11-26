"""Isometric block geometry as SVG.

The scenes are axis-aligned boxes seen through an orthographic isometric
camera, so no rasteriser is needed: collect the faces, drop the ones that point
away from the eye, sort the rest back to front and emit polygons.  The result
scales, keeps its line widths and takes the colour of the page.

World axes match the engine: +X east, +Y up, +Z south.
"""

import math

import numpy as np

import style
import style as svg

INK = "#1a1a1a"
CASING = "#fdfdfd"

SHADE = {
    (1, 0, 0): 0.88,
    (-1, 0, 0): 0.74,
    (0, 1, 0): 1.00,
    (0, -1, 0): 0.58,
    (0, 0, 1): 0.80,
    (0, 0, -1): 0.68,
}


def hexcol(rgb, k=1.0):
    if isinstance(rgb, str):
        return rgb
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(round(c * k)))) for c in rgb[:3])


FACE_CORNERS = {
    (1, 0, 0): ((1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)),
    (-1, 0, 0): ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)),
    (0, 1, 0): ((0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)),
    (0, -1, 0): ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
    (0, 0, 1): ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
    (0, 0, -1): ((1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)),
}


class Scene:
    """Collects faces and lines with their style.

    view is the direction towards the eye; when it is known the faces that
    point away are dropped, which halves the output and removes any tie
    between a front face and the back face of the same box.
    """

    def __init__(self, view=None):
        self.items = []   # (kind, payload)
        self.view = None if view is None else np.asarray(view, dtype="f8")

    # -- primitives ---------------------------------------------------------
    def box(self, lo, hi, rgb, edges=True, faces=None, skip=(), edge_px=6.0,
            flat=False):
        lo = np.array(lo, dtype="f8")
        hi = np.array(hi, dtype="f8")
        for i in range(3):
            if hi[i] <= lo[i]:
                hi[i] = lo[i] + 1e-4
        for axis, idx in FACE_CORNERS.items():
            if axis in skip:
                continue
            if self.view is not None and float(np.dot(axis, self.view)) <= 1e-6:
                continue
            col = (faces or {}).get(axis, rgb)
            if col is None:
                continue
            fill = hexcol(col) if flat else hexcol(col, SHADE[axis])
            pts = [np.array([lo[0] if c[0] == 0 else hi[0],
                             lo[1] if c[1] == 0 else hi[1],
                             lo[2] if c[2] == 0 else hi[2]]) for c in idx]
            self.items.append(("poly", (pts, fill,
                                        INK if edges else "none", edge_px)))

    def bar(self, a, b, width_px=3.0, rgb=INK, edges=False, casing=False,
            opacity=1.0):
        """A thin line.  Grid lines sit on opaque geometry, so they need no
        white casing: a casing wider than the line paints bands over it."""
        self.items.append(("line", (np.asarray(a, dtype="f8"),
                                    np.asarray(b, dtype="f8"),
                                    hexcol(rgb), width_px, casing, opacity)))

    def line(self, p0, p1, width_px=5.0, rgb=INK, casing=True, opacity=1.0):
        self.items.append(("line", (np.asarray(p0, dtype="f8"),
                                    np.asarray(p1, dtype="f8"),
                                    hexcol(rgb), width_px, casing, opacity)))


class Camera:
    def __init__(self, azimuth=225.0, elevation=32.0):
        self.az = math.radians(azimuth)
        self.el = math.radians(elevation)
        self.dir = np.array([math.sin(self.az) * math.cos(self.el),
                             math.sin(self.el),
                             math.cos(self.az) * math.cos(self.el)])

    def right(self):
        s = np.cross(-self.dir, np.array([0.0, 1.0, 0.0]))
        return s / np.linalg.norm(s)

    def basis(self):
        f = -self.dir
        s = np.cross(f, np.array([0.0, 1.0, 0.0]))
        s /= np.linalg.norm(s)
        u = np.cross(s, f)
        return s, u

    def axes(self):
        s, u = self.basis()
        return np.array([np.dot([1, 0, 0], s), np.dot([0, 1, 0], s), np.dot([0, 0, 1], s)]), \
               np.array([np.dot([1, 0, 0], u), np.dot([0, 1, 0], u), np.dot([0, 0, 1], u)])


def project_all(scene, cam):
    """World point -> view plane (x right, y up), plus depth."""
    s, u = cam.basis()
    def pr(p):
        p = np.asarray(p, dtype="f8")
        return np.array([float(np.dot(p, s)), float(np.dot(p, u))])
    def depth(p):
        return float(np.dot(np.asarray(p, dtype="f8"), cam.dir))
    return pr, depth


def render(build, cam=None, width=1100, margin=0.08, aspect=None,
           extra=(0, 0, 0, 0), title=None, points=()):
    """Build the scene and return an SVG string plus a world->svg projection."""
    cam = cam or Camera()
    scene = build()
    pr, depth = project_all(scene, cam)

    pts = []
    for kind, payload in scene.items:
        if kind == "poly":
            pts.extend(payload[0])
        else:
            pts.extend([payload[0], payload[1]])
    pts = list(pts) + list(points)
    pts = np.array(pts)
    v = np.array([pr(p) for p in pts])
    lo, hi = v.min(axis=0), v.max(axis=0)
    size = np.maximum(hi - lo, 1e-6)

    left, right, top, bottom = extra
    avail_w = width - left - right
    if aspect:
        height = int(round(width / aspect))
        avail_h = height - top - bottom
        scale = min(avail_w / (size[0] * (1 + 2 * margin)),
                    avail_h / (size[1] * (1 + 2 * margin)))
    else:
        scale = avail_w / (size[0] * (1 + 2 * margin))
        height = int(round(size[1] * scale * (1 + 2 * margin) + top + bottom))
        avail_h = height - top - bottom

    cx = (lo[0] + hi[0]) / 2.0
    cy = (lo[1] + hi[1]) / 2.0
    ox = left + avail_w / 2.0
    oy = top + avail_h / 2.0

    def to_svg(p):
        q = pr(p)
        return (ox + (q[0] - cx) * scale, oy - (q[1] - cy) * scale)

    # painter's algorithm: depth grows towards the eye, so the smallest value
    # is the farthest face and it has to go down first
    order = []
    for kind, payload in scene.items:
        if kind == "poly":
            c = np.mean(payload[0], axis=0)
        else:
            c = (payload[0] + payload[1]) / 2.0
        order.append((depth(c), kind, payload))
    order.sort(key=lambda t: t[0])

    parts = []
    for _, kind, payload in order:
        if kind == "poly":
            pts3, fill, stroke, sw = payload
            d = "M " + " L ".join("%.2f,%.2f" % to_svg(p) for p in pts3) + " Z"
            stroke_attr = (f' stroke="{stroke}" stroke-width="{sw}" '
                           f'stroke-linejoin="round"' if stroke != "none" else "")
            parts.append(f'<path d="{d}" fill="{fill}"{stroke_attr}/>')
        else:
            p = list(payload) + [False, 1.0]
            a, b, stroke, sw, casing, opacity = p[:6]
            x1, y1 = to_svg(a)
            x2, y2 = to_svg(b)
            if casing:
                parts.append(f'<path d="M {x1:.2f},{y1:.2f} L {x2:.2f},{y2:.2f}" '
                             f'stroke="{CASING}" stroke-width="{sw + 6}" '
                             f'stroke-linecap="round"/>')
            op = f' stroke-opacity="{opacity}"' if opacity < 1.0 else ""
            parts.append(f'<path d="M {x1:.2f},{y1:.2f} L {x2:.2f},{y2:.2f}" '
                         f'stroke="{stroke}" stroke-width="{sw}"{op} '
                         f'stroke-linecap="round"/>')

    return parts, to_svg, height


# ---- shared helpers ---------------------------------------------------
def plate(s, cx, cz, m=0.05, y=-0.02):
    """A light tile centred under the cell that starts at cx, cz."""
    s.box((cx - m, y - 0.045, cz - m), (cx + 1 + m, y, cz + 1 + m),
          style.LGREY, edges=True, edge_px=3.0)

def wire(s, lo, hi, width, rgb):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    for y in (y0, y1):
        for z in (z0, z1):
            s.bar((x0, y, z), (x1, y, z), width, rgb)
    for x in (x0, x1):
        for z in (z0, z1):
            s.bar((x, y0, z), (x, y1, z), width, rgb)
    for x in (x0, x1):
        for y in (y0, y1):
            s.bar((x, y, z0), (x, y, z1), width, rgb)

def below(fig, pr, cx, cz, text, size=32, dy=42):
    pts = [pr((cx + sx, -0.065, cz + sz))
           for sx in (-0.06, 1.06) for sz in (-0.06, 1.06)]
    ys = max(p[1] for p in pts)
    xs = sum(p[0] for p in pts) / 4.0
    fig.chip(xs, ys + dy, text, size=size)

def face_text(fig, cam, center, normal, world_h, pr, text, fill=svg.INK):
    """Place text in a face plane with an SVG matrix, so it foreshortens.

    The basis is snapped to the face edges rather than to the screen, because
    that is how a texture sits on a block in the game: the glyphs shear with
    the face instead of stretching along its diagonal.
    """
    n = np.asarray(normal, dtype="f8")
    n /= np.linalg.norm(n)
    axes = [np.array(v, dtype="f8") for v in
            ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
    plane = [a for a in axes if abs(float(np.dot(a, n))) < 1e-6]
    o = np.zeros(3)

    def img(v):
        return np.asarray(pr(o + v)) - np.asarray(pr(o))

    best = None
    for u in plane:
        for v in plane:
            if abs(float(np.dot(u, v))) > 1e-6:
                continue
            ui, vi = img(u), img(v)
            det = ui[0] * vi[1] - ui[1] * vi[0]
            if det <= 0 or vi[1] <= 0 or ui[0] <= 0:
                continue                     # mirrored, upside down, or leftward
            score = ui[0] - vi[1]            # most rightward u, most downward v
            if best is None or score > best[0]:
                best = (score, u, v)
    if best is None:                          # degenerate view, fall back
        u = plane[0]
        v = [a for a in plane if abs(float(np.dot(a, u))) < 1e-6][0]
    else:
        _, u, v = best

    du, dv = img(u), img(v)
    cx, cy = pr(center)
    # normalise by the vertical scale: the matrix keeps the foreshortening
    # between u and v, and the font then stays in ordinary pixels
    k = math.hypot(*dv) or 1.0
    a, b = du[0] / k, du[1] / k
    c, d = dv[0] / k, dv[1] / k
    m = (f"matrix({a:.4f} {b:.4f} {c:.4f} {d:.4f} {cx:.2f} {cy:.2f})")
    size = world_h * k * 0.95
    fig.add(f'<text transform="{m}" x="0" y="0" font-family="{svg.FONT}" '
            f'font-size="{size:.2f}" font-weight="bold" fill="{fill}" '
            f'text-anchor="middle" dominant-baseline="middle">{svg.esc(text)}'
            f'</text>')
