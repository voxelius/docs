# Precipitation API

A mod registers precipitation types for [weather](weather.md) fronts. Both sides run the registry, and the login checksum covers it.

## Constant: null type

`precip.NULL_TYPE` is an empty, undefined, or otherwise invalid precipitation type ID. Treat it as no precipitation.

## Functions

### Function: `precip.add(name, def) -> integer`

Registers a precipitation type.

#### Arguments

- `name` is the namespaced type ID
- `def` is the type definition table

#### Return value

- The numeric precipitation type ID

A duplicate name gets a `~N` suffix and a warning. See [Namespaced identifiers](../overview.md#namespaced-identifiers).

A malformed name, a wrong field type, or a value outside its range raises a Lua error and fails the mod.

### Function: `precip.get(name) -> integer`

Resolves a precipitation type name to its numeric ID.

#### Arguments

- `name` is the type ID. A name without a namespace resolves in the `builtin` namespace

#### Return value

- The numeric precipitation type ID

An unknown name returns `precip.NULL_TYPE`. A value that is not a string raises a Lua error.

## Type definition

|Field|Type|Default|Description|
|----|----|----|----|
|`temperature`|`table`|open band|Temperature band in degrees Celsius|
|`humidity`|`table`|full band|Humidity band, 0 to 1|
|`priority`|`number`|`1.0`|Score multiplier. It must be positive|
|`texture`|`string`|none|Texture under `textures/precip`. The type does not draw without it|
|`tint`|`string`|none|Tint group that colors the type per biome|
|`width`|`number`|`1.0`|Width of one quad in blocks. It must be positive|
|`height`|`number`|`12.0`|Half the height of the band around the camera, in blocks|
|`fall`|`number`|`4.0`|Texture scroll in tiles per second. One tile spans four blocks|
|`density`|`number`|`1.0`|Draw chance per column at full front share. A value of 1 draws every column there|
|`opacity`|`number`|`0.6`|Alpha of one quad at full front share, 0 to 1|
|`color`|`number[3]`|white|Base RGB color|
|`light_boost`|`number`|`0.0`|How far the light rises toward full, 0 to 1|

### Climate bands

`temperature` and `humidity` select the type from the local climate. A band is a table with `min`, `max` and `fade`:

```lua
precip.add("snow", {
  temperature = { max = 1, fade = 2 },
})
```

- Inside `min` to `max`, the weight is 1
- Outside the band, the weight falls to 0 over `fade` units
- `fade = 0` makes a hard cut at the edge
- `min` must not exceed `max`, and `fade` must not be negative

The default temperature band is `-1000` to `1000`. The default humidity band is `0` to `1`. A type that names no band always fits that axis.

`humidity` is a fraction from 0 to 1. The engine divides the humidity percentage of a biome by 100 before it compares them.

The engine scores every type that the front names with `temperature weight * humidity weight * priority`. The type with the highest score wins. The lower type ID wins a tie. If no type scores above zero, no precipitation shows. A `density` of 0 makes a type that suppresses precipitation in its climate band.

### Texture and tint

The client loads `textures/precip/<name>.png` from the mod that owns the type. The texture uses nearest filtering. It supplies the shape in its alpha channel and multiplies the color. A type without a valid `texture` stays invisible.

`tint` names a tint group from the [tints API](tints.md). The engine takes the tint color of the biome at the column, or the default color of the tint group. It multiplies that color by `color`.

The client lights each column from the sky and block light at the eye, or at the ground when the ground is above the eye. `light_boost` raises both values toward full.

## Where the precipitation shows

A weather front names the precipitation types that it can carry. The share of the front at a point scales the amount. The client draws columns around the camera and cuts each column at the ground, so a roof and the terrain hide the precipitation.

`r_precip` turns the pass off. `r_precip_radius` sets the radius of the column volume in blocks.

A weather type can name the precipitation types of its own mod and of the mods that loaded before it. The engine drops a name that is not registered at that point and logs a warning.
