# Filesystem

## Mod root

A mod's root directory is `data/<namespace>` in the virtual filesystem, where `<namespace>` is the mod's name. Each mod may use these directories:

|Directory|Description|
|----|----|
|`collisions`|Collision models for blocks|
|`features`|World generation feature templates|
|`fonts`|Fonts in binary form. Currently the engine uses them only in `builtin`. Font paths are hard-coded in the engine|
|`lang`|Translation files|
|`lib`|Lua libraries for `require`|
|`misc`|Miscellaneous files|
|`models`|3D models for blocks|
|`scripts`|Lua scripts|
|`shaders`|GLSL shader sources. Currently the engine uses them only in `builtin`. Shader paths are hard-coded in the engine|
|`textures`|Textures|

## Virtual filesystem

The engine uses PhysFS for the VFS. The user directory is `%APPDATA%/voxelius-client` on Windows and `voxelius-server` for the
server, or `$XDG_DATA_HOME/<name>` and `~/.local/share/<name>` on a POSIX host. The `-user` option overrides it. The engine mounts
these system paths:

|Mount|Path|Access|Description|
|----|----|----|----|
|`/data`|`${PWD}/data`|Read-only|Vendored mods, including `builtin`|
|`/`|the user directory|Read/Write|Settings and world saves live here|
|`/data`|`<user>/mods`|Read-only, appended|User-provided mods. The mount is appended, so a game mod of the same name wins|
