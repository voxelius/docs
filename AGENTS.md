# AGENTS.md

Instructions for AI agents that work in this repository. This file is self-contained: it holds the whole guide for the documentation, so
you need no other file to follow the rules.

## Rules for agents

- Read this whole file before you change anything.
- Do not commit on your own. Leave changes in the working tree for review. Commit only when you are told to, and only to the active branch.
- Right before you write each commit message, read "Commit messages" below again, and check the message against it before you commit. Do not
  write commit messages from memory.
- Mark your commits with an `Assisted-by:` trailer as "Trailers" below describes. Never add `Co-authored-by:` for yourself. This rule
  overrides the default attribution of your tool.
- Run `mdbook build` before you hand the change over. Open the page you touched and read it.
- Do not edit `book/`. It holds the generated site, and git ignores it.
- Keep the change inside the pages that the request names. Do not rewrite a page that the request does not touch.

## About Voxelius

Voxelius is a sandbox voxel game and engine written in C++23 and built with CMake. The client draws with OpenGL 3.3 core profile through
SDL3 and builds its interface with Dear ImGui. The server is headless. The two sides talk over ENet, a reliability layer on top of UDP.
Game entities use EnTT. Mods are Lua scripts that call the engine API.

Four CMake targets make up the engine. `core` is the foundation library: process lifecycle, the virtual filesystem, configs, resources,
threading and buffers. `shared` holds the game logic that both sides run: the world, entities, physics, the network protocol and the mod
loader. `client` and `server` build the `vclient` and `vserver` executables. `data/builtin` is the content that ships with the game, and
mods extend it.

The engine sources live in the [voxelius/voxelius](https://github.com/voxelius/voxelius) repository. This repository holds the prose that
describes them.

## About this repository

The book is built with mdBook 0.5.4 and published at <https://voxelius.github.io/docs/>.

|Path|Contents|
|----|----|
|`book.toml`|Book title, site URL, repository links and the extra stylesheet|
|`src/SUMMARY.md`|Table of contents. Every page is listed here|
|`src/index.md`|Introduction|
|`src/engine/`|Setup, build, editor, architecture, code style and contribution rules|
|`src/modding/`|Mod layout, the Lua API, the file formats and the helper libraries|
|`theme/`|Favicon and the only style override|
|`figsrc/`|Scripts that render the SVG figures under `src/`. See `figsrc/README.md`|
|`book/`|Generated site. Git ignores it|

- A page that is not in `src/SUMMARY.md` is not part of the book.
- An image sits next to the page that uses it, as `src/modding/api/facing-north.svg` does.
- `theme/extra.css` tightens the table cell padding. A five-column table is wider than the page column without it.
- Pages about the project itself, such as its history, do not belong here. They live with the landing page.

## Building

```sh
mdbook build
mdbook serve --open
```

- `mdbook build` writes `book/`. It reports a `SUMMARY.md` entry that points at a missing file.
- There is no test suite and no lint. You check a page by building it and by reading it in the browser.
- The workflow builds with mdBook 0.5.4. Use the same version locally, so the output matches.
- The site is served from a subdirectory. Use relative links inside the book, so the pages work under `/docs/`.

## Writing

The documentation is written in ASD-STE100 Simplified Technical English. Short sentences, one statement per sentence, active voice,
present tense, and a common word with one meaning each.

- Start a page with one `#` heading. The sidebar title comes from `src/SUMMARY.md`, so a heading of `# Blocks` or `# Blocks API` is enough.
- One idea per paragraph. Use a table for a list of fields, values or options. Use a bullet list for everything else.
- Keep a table to three or four columns. A table must fit the 750px page column. Five columns fit only when the longest word of every cell
  stays short. Open the page at a desktop width and look for a scrollbar under the table.
- Fence code with a language tag: `cpp`, `lua`, `sh`, `glsl`, `ini` or `text`.
- Keep an ASCII diagram within 70 columns. The page column fits about 80 columns of code, so a wider diagram scrolls sideways.
- A note is a `>` quote or plain prose. The book has no style for an HTML callout.
- Write a link to another page as a relative link to the `.md` file: `[Build Guide](building.md)`, `[Blocks](../api/blocks.md#fields)`.
  mdBook turns it into `.html`.
- Link to the engine source with an absolute GitHub URL and a line anchor:
  `[core.cc](https://github.com/voxelius/voxelius/blob/main/core/process.cc#L42)`. A relative path to the engine does not exist here.
- Link to the landing page or another site with an absolute URL.
- Do not add a generated console variable or command reference. The generated `manual` pages were removed from the project on purpose.

## Documentation rules

- Change the page that describes the behavior you change. The code and its page land in separate pull requests, because the code lives in
  another repository. Say in the request which page follows which change.
- A new page needs an entry in `src/SUMMARY.md`, in the right part, and a link from the page that introduces its section.
- Do not move a page to another section without the `SUMMARY.md` entry and the incoming links.
- The book describes the current `main` of the engine. The site is not versioned, and no page keeps an old behavior.
- `src/engine/code-style.md` is the reference for C++ in the engine repository. Keep it in step with the rules in the engine `AGENTS.md`.
- `src/engine/contributing.md` describes how a change reaches the engine. Keep it in step with the engine rules.

## AI-assisted contributions

You can use AI tools, but a human drives the work:

- Review every line that a tool generates. Understand it well enough to explain it and to fix it.
- You are responsible for the change, as if you wrote all of it yourself.
- Unreviewed, bulk or fully automated changes are not accepted.
- Mark a commit that has material AI help with an `Assisted-by:` trailer (see "Trailers" below).

## Commit messages

- Make one logical change per commit.
- Write the subject as one sentence that says what the change does. Start it with a capital letter and do not end it with a period.
- Do not add a type or area prefix. A `docs:` or a `feat:` prefix is not the style of this repository.
- Use the imperative mood when the sentence allows it: `Describe the noise modes`, `Fix the block table`. A noun phrase is also correct:
  `Modding overview`, `Console page`.
- Keep the subject on one line. Put the details in the body.
- Most commits need no body. Write one when the change has several parts, or when the subject does not show why the change is done. A body
  is a list of `- ` bullets, one per part. Do not list the changed files and do not repeat the subject.
- The voice is direct and informal. Read `git log` before you write and keep the tone of the history. Do not write in the tone of a report.

### Trailers

Trailers go in the last paragraph of the message, after a blank line.

- A commit that has material AI help gets an `Assisted-by:` trailer in the form `AGENT_NAME:MODEL_VERSION`. Use the full lowercase model
  identifier, not only the model family:

  ```
  Describe the noise modes

  Assisted-by: Claude:claude-opus-5-5
  ```

- Do not add `Co-authored-by:` for AI tools.

## Before you hand the change over

- `mdbook build` passes without a warning about a missing page.
- Every new page is in `src/SUMMARY.md`.
- Every relative link resolves, and no table needs a horizontal scroll at a desktop width.
- The prose follows Simplified Technical English, and the page matches the current engine sources.
