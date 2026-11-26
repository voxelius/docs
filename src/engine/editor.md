# Editor Setup

The repository works with any editor. Visual Studio Code gets a little extra: a script that configures one of the two C/C++ engines for the current machine.

## Which engine

Two extensions can give you completion, navigation, diagnostics and formatting:

|Engine|Extension|Notes|
|----|----|----|
|clangd|`llvm-vs-code-extensions.vscode-clangd`|Recommended. Reads the CMake compilation database, so it agrees with the build|
|IntelliSense|`ms-vscode.cpptools`|Uses a hand-written include list instead of the build flags|

Both engines cannot run at the same time on one file. The script turns one of them off and the other on.

## Running the script

|Shell|clangd|IntelliSense|
|----|----|----|
|Windows PowerShell|`.\setup_clangd.ps1`|`.\setup_intellisense.ps1`|
|Windows cmd.exe|`setup_clangd.bat`|`setup_intellisense.bat`|
|POSIX shell|`./setup_clangd.sh`|`./setup_intellisense.sh`|

Configure and build a preset once before you run the script in the clangd mode.

If the Windows execution policy blocks a PowerShell script, use the `.bat` wrapper or call the Python file directly: `py -3 scripts/setup_environment.py clangd`.

The script edits `.vscode/settings.json` in place. It owns the engine settings, so it overwrites them on every run. It also removes the settings that belong only to the other engine. It writes the common settings (format on save, rulers, the include guard extension) only when the key is missing. A value you change by hand then survives. Remove the key and run the script again to get the default back.

## The compilation database

clangd asks the build system what flags a file gets. CMake answers with `compile_commands.json`, but only for the Ninja and Makefile generators. The Visual Studio generator writes no database.

Each preset configures into its own directory, and clangd searches upward from the file it parses. A copy of the database in the repository root therefore serves every file. CMake keeps that copy fresh: the `copy-compile-commands` target runs on every build and copies `build/<preset>/compile_commands.json` to `<root>/compile_commands.json`.

Build a preset once, and check that the root copy exists:

```sh
./setup_clangd.sh
```

The script only checks the root copy and prints a warning when it is missing. It does not copy anything, and `--preset` only names the preset in that warning. Configure and build after a change that adds files, and the build refreshes the copy.

Only the Ninja and Makefile generators write the database. If no preset has a Ninja configuration, configure a separate directory:

```sh
cmake -S . -B build/clangd -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

## Tracked files

|File|Tracked|Contents|
|----|----|----|
|`.clangd`|Yes|Project-wide clangd switches: the module precompiled header is not reported as an unused include, and headers parse as C++23|
|`.vscode/settings.json`|No|Engine choice and editor defaults for this machine|
|`.vscode/c_cpp_properties.json`|Yes|Include paths for the Microsoft engine, all relative to the workspace|
|`.vscode/launch.json`|Yes|Debug configurations for both platforms|
|`compile_commands.json`|No|Copy of the database of the last built preset, refused by git|

`.clangd` is the only editor file that changes behaviour for everybody. Edit it there, not in the generated files.
