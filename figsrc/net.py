"""Sequence diagrams: the status ping and the login exchange."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import style
from style import save

INK = style.INK
PAGE = "#7a818a"
RULE = "#5b6168"
NODE = "#eaeef2"
NODE_EDGE = "#a8b1bb"


def text(fig, x, y, s, size=16, anchor="middle", fill=PAGE, weight="bold"):
    fig.text(x, y, s, size=size, anchor=anchor, fill=fill, weight=weight,
             casing=0)


CX1, CX2 = 108, 592       # the two lifelines
LABEL_X = (CX1 + CX2) / 2


def text(fig, x, y, s, size=16, anchor="middle", fill=PAGE, weight="bold"):
    fig.text(x, y, s, size=size, anchor=anchor, fill=fill, weight=weight,
             casing=0)


def wrap(s, limit=46):
    words, lines, line = s.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > limit:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    return lines


def head(fig, x, name):
    fig.add(f'<rect x="{x - 64}" y="16" width="128" height="38" rx="6" '
            f'fill="{NODE}" stroke="{NODE_EDGE}" stroke-width="1.6"/>')
    text(fig, x, 41, name, 18, fill=INK)


def lifeline(fig, x, y0, y1):
    fig.add(f'<path d="M {x},{y0} L {x},{y1}" fill="none" stroke="{RULE}" '
            f'stroke-width="1.4" stroke-dasharray="7 7"/>')


def step(fig, y, sender, label, number):
    """One arrow between the lifelines, with its label above it."""
    a, b = (CX1, CX2) if sender == "c" else (CX2, CX1)
    d = 4 if sender == "c" else -4
    fig.arrow((a, y), (b - d, y), shaft=2.0, head=11, fill=INK, casing=2.5)
    lines = wrap(label)
    for i, line in enumerate(lines):
        text(fig, LABEL_X, y - 12 - (len(lines) - 1 - i) * 18, line, 16)
    text(fig, 20, y + 5, str(number), 14, anchor="start", fill=PAGE,
         weight="normal")


def sequence(name, w, steps, last_note=None, first_label=None):
    h = 96 + len(steps) * 62 + (56 if last_note else 24)
    fig = style.SVG(w, h)
    head(fig, CX1, "Client")
    head(fig, CX2, "Server")
    lifeline(fig, CX1, 54, h - 18)
    lifeline(fig, CX2, 54, h - 18)

    y = 96
    for i, (sender, label) in enumerate(steps, start=1):
        step(fig, y, sender, label, i)
        y += 62

    if last_note:
        fig.add(f'<rect x="60" y="{y - 26}" width="{CX2 - 60 + 52}" height="34" '
                f'rx="6" fill="{NODE}" stroke="{NODE_EDGE}" stroke-width="1.4"/>')
        text(fig, LABEL_X + 4, y - 4, last_note, 16, fill=INK)

    save(fig.to_string(), name)


def status():
    sequence("status-ping.svg", 700, [
        ("c", "The client connects"),
        ("c", "StatusRequestPacket: the major, minor and patch version"),
        ("s", "StatusResponsePacket: versions, tags, motd, players, slots"),
        ("s", "The server closes the connection"),
    ])


def login():
    sequence("login.svg", 700, [
        ("c", "The client connects"),
        ("c", "AuthRequestPacket: username, public key, invite code, versions, "
              "seven registry hashes"),
        ("s", "AuthChallengePacket: a random 64-byte nonce"),
        ("c", "AuthResponsePacket: the nonce and the UTC minute, signed"),
        ("s", "AuthAdmissionPacket: client id, identity, username"),
    ], last_note="From here the entity and game packets flow")
