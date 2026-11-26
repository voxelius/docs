"""Charts: the climate square, the flow levels and the precipitation bands."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import style as svg
from style import RED, save


# --------------------------------------------------------- climate square
def climate_square():
    W2, H2 = 1000, 900
    x0, y0, x1, y1 = 120, 80, 950, 790
    pw, ph = x1 - x0, y1 - y0
    kinds = [
        ("clear", (0.26, 0.72), 1.00, "#f4c44a"),
        ("rain",  (0.64, 0.40), 1.30, "#4a94e8"),
        ("storm", (0.80, 0.66), 0.62, "#7e60be"),
        ("snow",  (0.40, 0.18), 0.55, "#8fd0de"),
    ]

    def best(pt):
        bi, bv = -1, 1e18
        for i, (_, (tx, ty), wt, _) in enumerate(kinds):
            d = ((pt[0] - tx) ** 2 + (pt[1] - ty) ** 2) / wt
            if d < bv:
                bi, bv = i, d
        return bi

    def to_px(pt):
        return (x0 + pt[0] * pw, y1 - pt[1] * ph)

    def border_t(pt, d):
        ts = []
        for lim, o, dd in ((0.0, pt[0], d[0]), (1.0, pt[0], d[0]),
                           (0.0, pt[1], d[1]), (1.0, pt[1], d[1])):
            if abs(dd) > 1e-9:
                t = (lim - o) / dd
                if t > 1e-6:
                    ts.append(t)
        return min(ts) if ts else 1.0

    fig = svg.SVG(W2, H2)
    nang = 240
    for i, (_, site, _, color) in enumerate(kinds):
        pts = []
        for k in range(nang):
            a = 2 * math.pi * k / nang
            d = (math.cos(a), math.sin(a))
            tmax = border_t(site, d)
            if best((site[0] + d[0] * tmax, site[1] + d[1] * tmax)) == i:
                r = tmax
            else:
                lo, hi = 0.0, tmax
                for _ in range(34):
                    mid = (lo + hi) / 2
                    if best((site[0] + d[0] * mid, site[1] + d[1] * mid)) == i:
                        lo = mid
                    else:
                        hi = mid
                r = lo
            pts.append(to_px((site[0] + d[0] * r, site[1] + d[1] * r)))
        fig.polygon(pts, fill=color, stroke="#5a6068", width=2, opacity=0.34)

    fig.rect(x0, y0, pw, ph, fill="none", stroke=svg.INK, width=3)

    for name, site, _, _ in kinds:
        px_, py_ = to_px(site)
        fig.circle(px_, py_, 7, fill=svg.INK)
        fig.circle(px_, py_, 3, fill="#ffffff")
        fig.text(px_, py_ - 20, name, size=28)

    sx, sy = to_px((0.5, 0.5))
    fig.circle(sx, sy, 8, fill=RED, stroke="#ffffff", width=3)
    fig.leader((sx, sy), (sx - 62, sy - 52))
    fig.chip(sx - 70, sy - 64, "sample (x, z)", size=25, anchor="end")

    ax, ay = to_px((0.68, 0.955))
    fig.arrow((ax, ay), (ax + 150, ay - 34), shaft=4, head=16)
    fig.text(ax - 10, ay + 6, "drift", size=25, anchor="end")

    fig.text((x0 + x1) / 2, y1 + 56, "axis 1: 1536 blocks per noise cell", size=25)
    fig.text(60, (y0 + y1) / 2, "axis 2: 1024 blocks per noise cell", size=25,
             rotate=-90)
    save(fig.to_string(), "weather-climate-square.svg")


# ------------------------------------------------------------- flow levels
def flow_levels():
    n, cell = 7, 116
    W2 = n * cell + 90
    H2 = n * cell + 90
    ox = oy = 45
    src = (3, 3)
    MAX = 8

    fig = svg.SVG(W2, H2)
    for j in range(n):
        for i in range(n):
            lvl = MAX - (abs(i - src[0]) + abs(j - src[1]))
            if lvl < 1:
                continue
            t = (lvl - 1) / (MAX - 1)
            col = "#%02x%02x%02x" % (
                int(126 + 74 * (1 - t)), int(172 + 56 * (1 - t)),
                int(236 + 12 * (1 - t)))
            if (i, j) == src:
                col = "#2a60b2"
            x, y = ox + i * cell, oy + j * cell
            fig.rect(x + 2, y + 2, cell - 4, cell - 4, fill=col,
                     stroke="#9aa3ac", width=2)
            lit = "#ffffff" if (i, j) == src else svg.INK
            fig.text(x + cell / 2, y + cell / 2 + 15, str(lvl), size=38, fill=lit,
                     casing=0)
    save(fig.to_string(), "flow-levels.svg")


# ------------------------------------------------------------ precip bands
def precip_fade():
    # The page column is 750 px, so the canvas is sized to render almost 1:1
    # and the axis labels keep the size of the body text.
    W2, H2 = 760, 600
    x0, y0, x1, y1 = 92, 70, 712, 450
    tmin, tmax = -20.0, 40.0
    MINOR, MAJOR = (198, 204, 210), (170, 177, 185)
    FRAME = "#8f98a2"

    def px_(t):
        return x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)

    def py_(v):
        return y1 - v * (y1 - y0)

    fig = svg.SVG(W2, H2)

    # the same graph paper as bmodel-grid: faint minors, majors every fourth
    for t in range(-20, 41, 5):
        major = t % 20 == 0
        fig.line([(px_(t), y0), (px_(t), y1)],
                 stroke=svg.rgb(MAJOR if major else MINOR),
                 width=1.5 if major else 1.0, casing=0)
    for k in range(11):
        v = k / 10.0
        major = k % 5 == 0
        fig.line([(x0, py_(v)), (x1, py_(v))],
                 stroke=svg.rgb(MAJOR if major else MINOR),
                 width=1.5 if major else 1.0, casing=0)
    for x in (x0, x1):
        fig.line([(x, y0), (x, y1)], stroke=FRAME, width=2.0, casing=0)
    for y in (y0, y1):
        fig.line([(x0, y), (x1, y)], stroke=FRAME, width=2.0, casing=0)

    def band(min_v, max_v, fade, color):
        pts = []
        for k in range(241):
            t = tmin + (tmax - tmin) * k / 240.0
            if t < min_v - fade or t > max_v + fade:
                v = 0.0
            elif t < min_v:
                v = (t - (min_v - fade)) / fade if fade > 0 else 1.0
            elif t > max_v:
                v = ((max_v + fade) - t) / fade if fade > 0 else 1.0
            else:
                v = 1.0
            pts.append((px_(t), py_(max(0.0, min(1.0, v)))))
        fig.polyline(pts, stroke=color, width=5, casing=0)

    band(-1000, 0, 4, "#4a94e8")
    band(-2, 14, 6, "#7e60be")

    for v in (0.0, 0.5, 1.0):
        fig.line([(x0 - 9, py_(v)), (x0, py_(v))], stroke=FRAME, width=2.0, casing=0)
        fig.text(x0 - 18, py_(v) + 7, f"{v:g}", size=20, anchor="end")
    for t in (-20, 0, 20, 40):
        fig.line([(px_(t), y1), (px_(t), y1 + 9)], stroke=FRAME, width=2.0, casing=0)
        fig.text(px_(t), y1 + 34, f"{t}", size=20)

    # the key sits in the free corner above the rain plateau
    lx, ly = x1 - 168, y0 + 34
    for k, (nm, color) in enumerate((("snow", "#4a94e8"), ("rain", "#7e60be"))):
        yy = ly + k * 42
        fig.polyline([(lx, yy), (lx + 44, yy)], stroke=color, width=5, casing=0)
        fig.chip(lx + 56, yy, nm, size=20, anchor="start")

    fig.arrow((px_(23.4), py_(0.45)), (px_(17.4), py_(0.44)), shaft=3, head=13)
    fig.chip(px_(24.0), py_(0.45), "fade", size=20, anchor="start")

    fig.text((x0 + x1) / 2, y1 + 68, "temperature, degrees Celsius", size=21)
    fig.text(x0 + 2, y0 - 22, "weight", size=21, anchor="start")
    save(fig.to_string(), "precip-fade.svg")
