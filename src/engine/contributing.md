# Contributing

Voxelius is a sandbox voxel game and engine written in C++23. This page describes how to send a change.

Read the [Code Style](code-style.md) page before you start. Formatting and naming are part of the review. The [Build Guide](building.md) and the [Requirements](requirements.md) pages explain how to build the project. The [Editor Setup](editor.md) page configures the C/C++ engine in Visual Studio Code.

The project uses the BSD 3-Clause license. See `LICENSE`. A change that you send uses the same license.

## Before you start

- Open an issue for a large change: a new subsystem, a new file format, a change to the network protocol. Explain what you want to do and why. Wait for an answer before you write much code.
- Send a small fix directly. A typo, a crash, a wrong number: these need no discussion.
- Do not edit `deps/`. It holds vendored third-party code and the CMake glue that builds it.
- Do not commit `build/`, `dist/` or `.vscode/settings.json`. The build writes the first two, and the last one belongs to your machine.

## Making a change

- Make one logical change per commit. Do not mix a refactor with a change of behaviour.
- Keep the change inside one area when you can. A commit that touches unrelated areas is hard to review.
- Format every changed C++ file with `clang-format` and the repository `.clang-format`, and check the result with
  `clang-format --dry-run --Werror <files>`. The [Code Style](code-style.md) page lists the settings.
- Build the target that you change. Run the client or the server when the change can affect them.
- Send a page change to the [documentation repository](https://github.com/voxelius/docs) when the change modifies a
  documented behaviour. The page and the code may land in separate pull requests.

## Testing

There is no test suite. You test a change by building it and by running the game:

- Run the client for a change to rendering, the interface or the client systems.
- Run the server for a change to the world, entities, physics or the network.
- Run both sides against each other for a change to the network protocol or to the shared game logic. The two sides must agree on every registry: the block, biome, fluid, tint, entity, weather and precipitation ones.

Describe the test in the pull request. A reviewer cannot see your machine.

## Commit messages

### Subject

- Write the subject as one sentence that says what the change does.
- Start it with a capital letter. Do not end it with a period.
- Do not add a type or area prefix. A `core:` or a `feat:` prefix is not the style of this repository.
- Use the imperative mood when the sentence allows it: `Move worldgen code to server`, `Fix crashing`. A noun phrase also works: `Client connections`, `Checkpoint`.
- Keep the subject on one line. Put the details in the body.

> **NOTE:** Older commits use a `<area>: <summary>` prefix, for example `shared: test identifiers`. Do not copy that form.

### Body

Most commits need no body. Write one when the change has several parts, or when the subject does not show why you make the change.

- Write the body as a list of `- ` bullets, one per part of the change.
- Do not list the changed files. Do not repeat the subject.
- Keep the voice direct and informal. Read `git log` before you write.

### Trailers

Trailers go in the last paragraph of the message, after a blank line.

A commit that has material AI help gets an `Assisted-by:` trailer. Use the full lowercase model identifier, not only the model family:

```
Keep the config file open across a reload

Assisted-by: Claude:claude-opus-5-5
```

Do not add `Co-authored-by:` for AI tools.

## AI-assisted contributions

You can use AI tools, but a human drives the work:

- Review every line that a tool generates. Understand it well enough to explain it and to fix it.
- You are responsible for the change, as if you wrote all of it yourself.
- Unreviewed, bulk or fully automated changes are not accepted.
- Mark a commit that has material AI help with an `Assisted-by:` trailer (see [Trailers](#trailers)).

## Pull requests

No workflow compiles the game or blocks a pull request, so the checks on this page are yours to run. A maintainer reads the
change and merges it as a merge commit.

- Open the pull request against the default branch.
- Describe what the change does and how you tested it. Do not repeat the diff.
- Keep one topic per pull request. A reviewer can ask for a split.
- Answer each review comment. Push the fix as a new commit.
- Do not rewrite the history of a branch that is under review.
- Rebase on the default branch when your branch conflicts with it.

## Reporting a problem

Open an issue and add:

- the steps that lead to the problem.
- what you expected and what happened.
- the build (debug or release), the platform and the version.
- the log output, when the engine wrote one.

Try to find the smallest series of steps that shows the problem. A report without a reproduction is hard to use.
