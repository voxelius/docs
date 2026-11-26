# World definitions

The server reads its worlds from `worlds.yml` in the user directory, next to `server.conf`. The file is YAML. Each top-level key is a world name. When the file is missing, the engine copies the shipped `defaults/worlds.yml` into the user directory and reads the copy. A file that is not valid YAML stops the server.

World definitions are server configuration. They are not a Lua API, and a mod cannot add a world at runtime.

## Example

```text
overworld:
  default: true
  generator: vox2

  min_y: 0
  max_y: 127
  spawn: [0, 72, 0]

  weather:
    - builtin:clear
    - builtin:overcast
    - builtin:rain
    - builtin:thunderstorm

  biome_selector:
    strategy: nearest
    axes: [temperature, humidity]
    weights: [1.0, 1.0]
    entries:
      - biome: builtin:vox2_plains
        target: [55, 30]
      - biome: builtin:vox2_desert
        target: [95, 8]

superflat:
  generator: superflat
  spawn: [0, 1, 0]

  biome_selector:
    strategy: constant
    biome: builtin:vox2_plains
```

## World fields

|Field|Type|Default|Description|
|----|----|----|----|
|`default`|`boolean`|`false`|The world that a new session joins|
|`generator`|`string`|required|`vox2` or `superflat`|
|`generator_settings`|`mapping`|`{}`|Settings for the generator|
|`min_y`, `max_y`|`integer`|`-64`, `255`|Lowest and highest world block Y|
|`spawn`|`integer[3]`|`[0, 32, 0]`|Spawn block position|
|`weather`|`string[]`|`[]`|Weather types that the world allows|
|`biome_selector`|`mapping`|required|How the generator picks a biome|
|`visuals`|`mapping`|none|Optional sky, sun, moon, stars and clouds|

Each key is the world name. The name is also the directory under `save/` that holds the world. It may use letters, digits, `_`, `-` and `.`. The terrain seed derives from the name and the universe seed, so a renamed world starts from scratch.

The engine ignores an entry whose value is not a mapping, and one whose name holds any other character. A repeated name keeps the first entry. It logs a warning in each case.

Set `default` to true on one world. Every admitted session joins that world. Without a marked default, the server uses the first world in the file. A second mark is ignored with a warning.

`min_y` above `max_y` resets both bounds to the defaults, with a warning.

`weather` lists the weather types that the world may pick. The name is a full identifier, so it needs its namespace, as in `builtin:rain`. The engine resolves the names after all mods load, so a mod can add a type that this file names. It drops a name without a namespace, and one that no mod registers, with a warning.

## Biome selector

`biome_selector` is required. `strategy` is `constant`, `nearest` or `grid`.

A biome name is a full identifier too, so it needs its namespace, as in `builtin:vox2_plains` or `mymod:custom_biome`. A bare name is rejected: the `nearest` strategy drops the entry, and the other strategies skip the world.

### Constant

```text
biome_selector:
  strategy: constant
  biome: builtin:vox2_plains
```

The `superflat` generator needs a constant selector.

### Nearest

```text
biome_selector:
  strategy: nearest
  axes: [temperature, humidity]
  weights: [1.0, 1.0]
  entries:
    - biome: builtin:vox2_plains
      target: [55, 30]
    - biome: builtin:vox2_desert
      target: [95, 8]
```

`axes` and `weights` must have the same length and may not be empty. `entries` is required. `target` holds one integer from 0 to 99 per axis. `priority` (default 0) breaks a tie, and `offset` (default 0.0) biases the distance. During load, the engine nudges colliding targets until each is unique.

The `vox2` generator knows two axes: `temperature` and `humidity`. A nearest selector may list them in either order, but may not repeat one. A world with an unknown or a repeated axis is skipped.

A nearest selector without a usable entry skips the world.

### Grid

```text
biome_selector:
  strategy: grid
  axes: [temperature, humidity]
  grid_size: 2
  lookup:
    - [builtin:vox2_taiga, builtin:vox2_forest]
    - [builtin:vox2_plains, builtin:vox2_desert]
```

`axes` holds exactly two names. For `vox2`, both must be `temperature` and `humidity`, in either order. `grid_size` is 1 to 128. `lookup` has `grid_size` rows of `grid_size` names. The row is the second axis and the column is the first axis. `weights` and `entries` do not apply to the grid. Every entry needs a namespace, and an unknown name skips the world.

## Generator settings

`generator_settings` is optional. An invalid value logs a warning. The engine uses the default or clamps the value.

### `vox2`

|Key|Default|Range|
|----|----|----|
|`base_min`|`44`|within `min_y` to `max_y`. Not greater than `base_max`|
|`base_max`|`92`|within `min_y` to `max_y`. Not less than `base_min`|
|`variation_min`|`16`|0 or greater. Not greater than `variation_max`|
|`variation_max`|`48`|0 or greater. Not less than `variation_min`|
|`terrain_frequency`|`0.03`|greater than 0|
|`terrain_octaves`|`4`|1 to 8|
|`sea_level`|`64`|`min_y` to `max_y`. Outside this range it is clamped|
|`surface_depth`|`4`|0 to 8|

`vox2` is a surface generator. A base height noise picks a height between `base_min` and `base_max`. A variation noise and a three-dimensional detail noise then shape the terrain around it: a cell is solid while the base height plus the scaled detail stays above it.

Two climate noises, temperature and humidity, pick the biome. They do not depend on the terrain.

The empty cells below `sea_level` take the fluid of the biome. The palette fields decide the solid blocks:

- The top solid cell of a column takes the land surface when it sits at or above one block below `sea_level`. Lower than that, it takes the land filler.
- The `surface_depth` cells below the top cell take the land filler, and the cells below them take the base block.
- When the top cell sits in the band from four blocks below `sea_level` to one block above it, it takes `shore_surface` or `shore_filler` in place of `land_surface` or `land_filler`.

See [Biomes](api/biomes.md#palette-table) for the palette fields.

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
|`clouds`|none. An empty mapping enables the group|

The `sky` group draws the sky dome, the day and night gradient and the sunset glow. If `visuals.sky` is absent, the client does not draw the sky dome. `sun`, `moon`, `stars` and `clouds` stay independent groups.

## Loading

The engine loads the file at server start, after the mods load. It skips a world with an unknown generator or a missing or invalid `biome_selector`, and logs the reason. The other worlds keep loading. An unknown key is ignored. The server stops when the file defines no world or when every world is skipped.

The `world.name` function returns the key of the world. See the [World API](api/world.md).
