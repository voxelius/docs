# World definitions

The server reads its worlds from `worlds.jsonc` in the user directory, next to `server.conf`. The file is JSON with comments. Each key is a world name. The engine writes a default file when the file is missing or malformed.

World definitions are server configuration. They are not a Lua API, and a mod cannot add a world at runtime.

## Example

```text
{
  "overworld": {
    "default": true,
    "generator": "vox17",

    "min_y": -64,
    "max_y": 255,
    "spawn": [0, 32, 0],

    "weather": ["clear", "overcast", "rain", "thunderstorm"],

    "biome_selector": {
      "strategy": "nearest",
      "axes": ["temperature", "humidity", "continentalness",
               "erosion", "weirdness"],
      "weights": [1.0, 1.0, 0.75, 1.0, 1.5],
      "entries": [
        { "biome": "surface_plains", "target": [50, 55, 55, 70, 50] }
      ]
    }
  }
}
```

## World fields

|Field|Type|Default|Description|
|----|----|----|----|
|`default`|`boolean`|`false`|The world that `sv_spawn_world` selects when it is empty|
|`generator`|`string`|required|`vox17` or `superflat`|
|`generator_settings`|`object`|`{}`|Settings for the generator|
|`min_y`, `max_y`|`integer`|`-64`, `255`|Lowest and highest world block Y|
|`spawn`|`integer[3]`|`[0, 32, 0]`|Spawn block position|
|`weather`|`string[]`|`[]`|Weather types that the world allows|
|`biome_selector`|`object`|required|How the generator picks a biome|
|`visuals`|`object`|none|Optional sky, sun, moon, stars and clouds|

Each key is the world name. The name is also the directory under `save/` that holds the world. It may use letters, digits, `_`, `-` and `.`. The terrain seed derives from the name and the universe seed, so a renamed world starts from scratch.

Set `default` to true on one world. The `sv_spawn_world` cvar selects a world by name, and an empty value selects the default world. Without a marked default, the first world is used.

`weather` lists the weather types that the world may pick. A name without a namespace resolves in the `builtin` namespace. The engine resolves the names after all mods load, so a mod can add a type that this file names. An unknown name is dropped with a warning.

## Biome selector

`biome_selector` is required. `strategy` is `constant`, `nearest` or `grid`.

A biome name without a namespace resolves in the `builtin` namespace. A mod biome needs its namespace.

### Constant

```text
"biome_selector": {
  "strategy": "constant",
  "biome": "surface_plains"
}
```

The `superflat` generator needs a constant selector.

### Nearest

```text
"biome_selector": {
  "strategy": "nearest",
  "axes": ["temperature", "humidity", "continentalness",
           "erosion", "weirdness"],
  "weights": [1.0, 1.0, 0.75, 1.0, 1.5],
  "entries": [
    { "biome": "surface_plains", "target": [50, 55, 55, 70, 50] },
    { "biome": "surface_desert", "target": [80, 20, 60, 65, 50] }
  ]
}
```

`axes` and `weights` must have the same length and may not be empty. `entries` is required. `target` holds one integer from 0 to 99 per axis. `priority` (default 0) breaks a tie, and `offset` (default 0.0) biases the distance. The engine nudges colliding targets until each is unique.

The `vox17` generator needs the five axes in the order above.

### Grid

```text
"biome_selector": {
  "strategy": "grid",
  "axes": ["temperature", "humidity"],
  "grid_size": 2,
  "lookup": [
    ["surface_desert", "surface_plains"],
    ["surface_forest_oak", "surface_plains"]
  ]
}
```

`axes` holds exactly two names. The `vox17` generator needs `temperature` first and `humidity` second. `grid_size` is 1 to 128. `lookup` has `grid_size` rows of `grid_size` names. The row is the second axis and the column is the first axis. `weights` and `entries` do not apply to the grid.

## Generator settings

`generator_settings` is optional. An invalid value logs a warning. The engine uses the default or clamps the value.

### `vox17`

|Key|Default|Range|
|----|----|----|
|`terrain_frequency`|`0.005`|greater than 0|
|`terrain_octaves`|`4`|1 to 8|
|`terrain_density_peak`|`0.385`|0 to 1|
|`sea_level`|`0`|`min_y` to `max_y`. Outside this range it is clamped|
|`base_min`|`-24`|not greater than `base_max`|
|`base_max`|`16`|not less than `base_min`|
|`variation_min`|`16`|0 or greater, not greater than `variation_max`|
|`variation_max`|`96`|not less than `variation_min`|
|`pv_valley_offset`|`-32`|not greater than `pv_peak_offset`|
|`pv_peak_offset`|`12`|not less than `pv_valley_offset`|

`climate_frequencies` holds one entry per climate axis:

|Key|Default|
|----|----|
|`temperature`|`0.0007`|
|`humidity`|`0.0007`|
|`continentalness`|`0.00035`|
|`erosion`|`0.00075`|
|`weirdness`|`0.001`|

`vox17` needs a `nearest` selector with the five axes in the order above, or a `grid` selector with `temperature` and `humidity`.

### `superflat`

|Key|Default|Range|
|----|----|----|
|`surface_y`|`0`|`min_y` to `max_y`. Outside this range it is clamped|
|`filler_depth`|`3`|0 or greater. The filler must not reach below `min_y`|

The selector must be `constant`.

## Visuals

`visuals` holds optional groups. A missing group disables that part of the sky. A group with missing fields is ignored with a warning. Colors are arrays of three numbers.

|Group|Fields|
|----|----|
|`sky`|`day`, `night` (`horizon` and `zenith` colors), `twilight_height`|
|`sun`|`tilt`|
|`moon`|`color`|
|`stars`|`count`|
|`clouds`|empty object|

The `sky` group draws the sky dome, the day and night gradient and the sunset glow. If `visuals.sky` is absent, the client does not draw the sky dome. `sun`, `moon`, `stars` and `clouds` stay independent groups.

## Loading

The engine loads the file at server start, after the mods load. It skips a world with an unknown generator, a missing or invalid `biome_selector`, or an unknown constant biome, and logs the reason. The other worlds keep loading. The server stops before the first frame when no world loads.

The `world.name` function returns the key of the world. See the [World API](api/world.md).
