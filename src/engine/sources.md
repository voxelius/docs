# Source Hierarchy

> **NOTE:** This file exists so I do not move sources again. I do not want to rewrite docs every time the tree changes.

## In-tree directories

|Directory|Description|
|----|----|
|`client`|Client executable sources|
|`core`|Core library. Useful without depending on block-related code|
|`data`|Content packed with release executables. At least the `builtin` mod. More may appear later if people contribute|
|`deps`|Third-party dependencies|
|`misc`|Small generators for the data assets|
|`scripts`|Scripts used during build and elsewhere|
|`server`|Server executable sources|
|`shared`|Shared game library. Most game logic, networking, and other client/server shared code|

The documentation is a separate repository: [voxelius/docs](https://github.com/voxelius/docs).

## Ignored directories

These appear when you run or build the game with the scripts. `.gitignore` lists them, and git does not track them.

|Directory|Description|
|----|----|
|`build`|Root build directory|
|`dist`|CPack output directory|

## Directory tree

Produced by running `tree.exe` on the repository root.

```
C:\PATH\TO\REPOSITORY
├───.vscode
├───build
├───client
│   ├───api
│   ├───gui
│   ├───input
│   ├───net
│   ├───res
│   ├───system
│   ├───utils
│   └───world
├───core
│   ├───config
│   ├───cvar
│   ├───msg
│   ├───res
│   └───utils
├───data
│   └───builtin
│       ├───collisions
│       │   └───block
│       ├───features
│       ├───fonts
│       ├───lang
│       ├───lib
│       ├───misc
│       ├───models
│       │   └───block
│       ├───scripts
│       │   ├───biome
│       │   ├───block
│       │   ├───entity
│       │   ├───fluid
│       │   ├───precip
│       │   └───weather
│       ├───shaders
│       └───textures
│           ├───block
│           ├───environment
│           ├───gui
│           └───precip
├───deps
│   ├───ed25519
│   ├───eigen
│   ├───emhash
│   ├───enet
│   ├───entt
│   ├───fastnoiselite
│   ├───glad
│   ├───imgui
│   ├───lua
│   ├───miniz
│   ├───parson
│   ├───physfs
│   ├───SDL3
│   ├───stb
│   ├───thread_pool
│   └───tracy
├───misc
├───scripts
├───server
│   ├───api
│   ├───entity
│   ├───net
│   ├───system
│   ├───utils
│   └───world
└───shared
    ├───api
    ├───component
    ├───cvar
    ├───entity
    ├───net
    ├───physics
    ├───res
    ├───system
    ├───utils
    └───world
```
