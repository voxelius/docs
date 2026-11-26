"""The six facing illustrations of the block API page.

One model, painted per face, seen from one camera but rotated six ways.  The
model is rotated, not the camera: turning the camera about its own up axis
would flip the picture once the eye goes below the horizon.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import iso
import style as svg
from iso import face_text
from style import save

# axis, colour, label
FACES = [
    ((0, 1, 0), "#6fc652", "TOP"),
    ((0, -1, 0), "#c9b963", "BOTTOM"),
    ((0, 0, -1), "#1c5ad1", "NORTH"),
    ((0, 0, 1), "#69acca", "SOUTH"),
    ((1, 0, 0), "#da3a29", "EAST"),
    ((-1, 0, 0), "#d261a9", "WEST"),
]

# True isometric: the three edges of the near corner are 120 degrees apart and
# every axis is foreshortened by the same factor, so one text size fits all.
AZ, EL = 225.0, 35.264389682754654
CAP_H = 0.20

CAM = iso.Camera(azimuth=AZ, elevation=EL)


def rot_x(deg):
    a = math.radians(deg)
    return np.array([[1, 0, 0],
                     [0, math.cos(a), -math.sin(a)],
                     [0, math.sin(a), math.cos(a)]])


def rot_y(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), 0, math.sin(a)],
                     [0, 1, 0],
                     [-math.sin(a), 0, math.cos(a)]])


ROTATIONS = {
    "north": np.eye(3),
    "south": rot_y(180),
    "east": rot_y(-90),
    "west": rot_y(90),
    "top": rot_x(90),
    "bottom": rot_x(-90),
}


def visible(axis, R):
    """Is the face with this model normal turned towards the camera?"""
    n = R @ np.array(axis, dtype="f8")
    return float(np.dot(n, CAM.dir)) > 1e-6


def figure(name):
    R = ROTATIONS[name]
    colours = {axis: col for axis, col, _ in FACES}

    def build():
        s = iso.Scene(CAM.dir)
        for axis, idx in iso.FACE_CORNERS.items():
            if not visible(axis, R):
                continue
            pts = [R @ np.array(c, dtype="f8") for c in idx]
            s.items.append(("poly", (pts, colours[axis], iso.INK, 20.0)))
        return s

    geom, pr, H = iso.render(build, CAM, width=1100, margin=0.10, aspect=1.0)
    # the table gives this figure about a third of the column, and the labels
    # on the faces have to stay readable at that size
    fig = svg.SVG(1100, H, display=250)
    fig.parts.extend(geom)
    for axis, _, text in FACES:
        if not visible(axis, R):
            continue
        normal = R @ np.array(axis, dtype="f8")
        centre = R @ (np.array([0.5, 0.5, 0.5]) + np.array(axis, dtype="f8") * 0.5)
        face_text(fig, CAM, centre, normal, CAP_H, pr, text, fill="#000000")
    save(fig.to_string(), f"facing-{name}.svg")


NAMES = list(ROTATIONS)
