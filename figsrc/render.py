"""Render every figure into the page that uses it.

    python figsrc/render.py [name ...]

With no arguments it renders every figure and writes each one next to its page.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arch
import blocks
import charts
import facing
import net
import style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# figure -> the page directory it belongs to
DESTINATIONS = {
    "frame-pipeline.svg": "src/engine",
    "cloud-rings.svg": "src/engine",
    "boot-stages.svg": "src/engine",
    "resource-life.svg": "src/engine",
    "status-ping.svg": "src/engine",
    "login.svg": "src/engine",
    "bcoll-shapes.svg": "src/modding/formats",
    "bmodel-grid.svg": "src/modding/formats",
    "slabs-orientation.svg": "src/modding/libs",
    "logs-orientation.svg": "src/modding/libs",
    "flow-levels.svg": "src/modding/libs",
    "fluids-gravity.svg": "src/modding/api",
    "block-target.svg": "src/modding/api",
    "weather-climate-square.svg": "src/modding/api",
    "precip-fade.svg": "src/modding/api",
}
for _n in facing.NAMES:
    DESTINATIONS[f"facing-{_n}.svg"] = "src/modding/api"

FIGURES = {
    "frame-pipeline": arch.pipeline,
    "cloud-rings": arch.cloud_rings,
    "boot-stages": arch.stages,
    "resource-life": arch.resources,
    "status-ping": net.status,
    "login": net.login,
    "bcoll-shapes": blocks.bcoll_shapes,
    "bmodel-grid": blocks.bmodel_grid,
    "slabs-orientation": blocks.slabs_orientation,
    "logs-orientation": blocks.logs_orientation,
    "fluids-gravity": blocks.fluids_gravity,
    "block-target": blocks.block_target,
    "flow-levels": charts.flow_levels,
    "weather-climate-square": charts.climate_square,
    "precip-fade": charts.precip_fade,
}


def main(wanted):
    for name, fn in FIGURES.items():
        if wanted and name not in wanted:
            continue
        style.OUTPUTS.pop(f"{name}.svg", None)
        fn()
    for name in facing.NAMES:
        if wanted and f"facing-{name}" not in wanted:
            continue
        style.OUTPUTS.pop(f"facing-{name}.svg", None)
        facing.figure(name)

    total = 0
    for name, text in sorted(style.OUTPUTS.items()):
        dest = DESTINATIONS[name]
        path = os.path.join(ROOT, dest, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        size = os.path.getsize(path)
        total += size
        print(f"  {dest + '/' + name:52s} {size / 1024:6.1f} KB")
    if style.OUTPUTS:
        print(f"\n{len(style.OUTPUTS)} figures, {total / 1024:.1f} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
