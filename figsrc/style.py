"""SVG writer and palette for the book figures.

Only what the figures need: paths, rects, circles, text and arrows.  Every
visible ink element carries a white casing, because the book has a light and a
dark theme and the figures are drawn on a transparent background.
"""

INK = "#1a1a1a"
RED = "#e0524e"
GREY = "#6b7076"
LGREY = "#eceef0"
CASING = "#fdfdfd"
TEXT_CASING = "#cfd3d8"   # softer than CASING: an outline this thin does not need to be white
FONT = "Anonymous Pro, ui-monospace, SFMono-Regular, Menlo, monospace"


def rgb(c):
    return "#%02x%02x%02x" % tuple(int(v) for v in c[:3])


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class SVG:
    def __init__(self, w, h, display=None):
        self.w = w
        self.h = h
        self.parts = []
        # display is the width in page pixels, for a figure inside a table:
        # its user units would otherwise decide the column width
        self.display = display

    # -- primitives ---------------------------------------------------------
    def path(self, d, stroke=INK, width=2.5, fill="none", casing=0, opacity=None,
             cap="round", join="round"):
        if casing:
            self.parts.append(
                f'<path d="{d}" fill="none" stroke="{CASING}" '
                f'stroke-width="{width + casing * 2}" stroke-linecap="{cap}" '
                f'stroke-linejoin="{join}"/>')
        op = f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.parts.append(
            f'<path d="{d}" fill="{fill}"{op} stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>')

    def polyline(self, pts, **kw):
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.path(d, **kw)

    def polygon(self, pts, **kw):
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
        self.path(d, **kw)

    def rect(self, x, y, w, h, fill="none", stroke=INK, width=2.5, casing=0):
        if casing:
            self.parts.append(
                f'<rect x="{x - casing}" y="{y - casing}" width="{w + casing * 2}" '
                f'height="{h + casing * 2}" fill="none" stroke="{CASING}" '
                f'stroke-width="{width + casing * 2}"/>')
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>')

    def circle(self, cx, cy, r, fill=INK, stroke="none", width=0, casing=0):
        if casing:
            self.parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r + casing}" fill="{CASING}"/>')
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"/>')

    def text(self, x, y, s, size=26, anchor="middle", fill=INK, weight="bold",
             casing=None, rotate=None, family=FONT):
        """Draw text with a white outline.

        The outline is a second copy of the text underneath, not a stroke with
        paint-order: a stroke paints over the fill in any engine that ignores
        paint-order, and the glyphs then read as a white ghost.
        """
        tr = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate else ""
        common = (f'x="{x:.2f}" y="{y:.2f}" font-family="{family}" '
                  f'font-size="{size}" font-weight="{weight}" '
                  f'text-anchor="{anchor}"{tr}')
        if casing is None:
            casing = max(1.1, round(size * 0.055, 1))
        if casing:
            self.parts.append(
                f'<text {common} fill="none" stroke="{TEXT_CASING}" '
                f'stroke-width="{casing * 2}" stroke-linejoin="round" '
                f'stroke-linecap="round">{esc(s)}</text>')
        self.parts.append(f'<text {common} fill="{fill}">{esc(s)}</text>')

    def chip(self, x, y, text, size=26, anchor="middle", pad=10, opacity=0.92):
        """A label on a soft plate, for text that has to sit over geometry."""
        w = len(text) * size * 0.62 + pad * 2
        h = size * 1.42
        if anchor == "start":
            rx = x - pad
        elif anchor == "end":
            rx = x - w + pad
        else:
            rx = x - w / 2
        ry = y - size * 0.95
        self.parts.append(
            f'<rect x="{rx:.2f}" y="{ry:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'rx="4" fill="#ffffff" fill-opacity="{opacity}"/>')
        self.text(x, y, text, size=size, anchor=anchor, casing=0)

    def arrow(self, a, b, shaft=5, head=16, fill=INK, casing=2.5):
        """A filled arrow with a white casing, built from a shaft and a head."""
        import math
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        neck = (b[0] - ux * head, b[1] - uy * head)
        w = shaft / 2.0
        hw = head * 0.5
        body = [(a[0] + px * w, a[1] + py * w), (neck[0] + px * w, neck[1] + py * w),
                (neck[0] - px * w, neck[1] - py * w), (a[0] - px * w, a[1] - py * w)]
        tip = [(neck[0] + px * hw, neck[1] + py * hw), b,
               (neck[0] - px * hw, neck[1] - py * hw)]
        if casing:
            parts = []
            for p in (body, tip):
                d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in p) + " Z"
                parts.append(f'<path d="{d}" fill="{CASING}" stroke="{CASING}" '
                             f'stroke-width="{casing * 2}" stroke-linejoin="round"/>')
            self.parts.extend(parts)
        for p in (body, tip):
            d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in p) + " Z"
            self.parts.append(f'<path d="{d}" fill="{fill}"/>')

    def add(self, part):
        self.parts.append(part)

    def line(self, pts, stroke=INK, width=2.5, casing=0):
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        if casing:
            self.parts.append(f'<path d="{d}" fill="none" stroke="{CASING}" '
                              f'stroke-width="{width + casing * 2}" '
                              f'stroke-linecap="round"/>')
        self.parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" '
                          f'stroke-width="{width}" stroke-linecap="round"/>')

    def leader(self, a, b, width=3.2, stroke="#e0524e"):
        """A callout line: solid, in the colour of its marker.

        A white casing suits the big arrows, but on a thin leader it reads as
        two lines, so the leader carries its own colour instead.
        """
        self.line([a, b], stroke=stroke, width=width, casing=0)

    # -- output -------------------------------------------------------------
    def to_string(self):
        # the intrinsic size keeps the ratio, and the inline style lets the
        # 750px page column shrink the figure without squashing it
        if self.display:
            dw = self.display
            dh = round(self.display * self.h / self.w)
        else:
            dw, dh = self.w, self.h
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {self.w} {self.h}" width="{dw}" height="{dh}" '
                f'style="max-width:100%;height:auto">\n'
                + "\n".join(self.parts) + "\n</svg>\n")

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}">\n')
        body = "\n".join(self.parts)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(head + body + "\n</svg>\n")
        import os
        print(f"  {os.path.basename(path):34s} {self.w}x{self.h}  "
              f"{os.path.getsize(path) / 1024:6.1f} KB")


# ---- palette used by the block figures --------------------------------
STONE = (150, 155, 162)
WOOD = (166, 124, 82)
WOOD_END = (238, 224, 196)
WATER = (72, 148, 232)
WATER_TOP = (118, 184, 246)
HILITE = (255, 196, 64)

OUTPUTS = {}


def save(text, name):
    OUTPUTS[name] = text


def write_figure(geom, pr, height, name, tail, width=1100):
    fig = SVG(width, height)
    fig.parts.extend(geom)
    tail(fig, pr)
    save(fig.to_string(), name)
