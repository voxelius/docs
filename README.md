# Voxelius documentation

The engine development and modding documentation for [Voxelius](https://github.com/voxelius/voxelius).
It builds into the book at <https://voxelius.github.io/docs/>.

## Building

```sh
mdbook build
```

The result lands in `book/`. For a live preview on <http://localhost:3000>:

```sh
mdbook serve --open
```

## Structure

- `src/SUMMARY.md` lists every page and sets the sidebar order. A new page needs an entry here.
- `src/engine/` covers setup, build, architecture and contribution rules.
- `src/modding/` covers mod layout, the Lua API and the file formats.
- Images sit next to the page that uses them.
- `book.toml` holds the site URL and the repository links.

Pages about the project itself, such as the history, live outside this repository.

## Writing

`src/engine/code-style.md` holds the rules for code. Prose follows the same habit: short sentences, one statement each,
active voice, present tense, and a common word with one meaning.
