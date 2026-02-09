# AGENTS.md

## Purpose

This repository contains the NAIF project website.

- Website: https://eth-library.github.io/naif/
- Repository: https://github.com/eth-library/naif

## Tech

- Quarto website (`.qmd` + `_quarto.yml`)
- Output is rendered into `_site/` (do not edit `_site/` manually)

## Required commands (always run)

Before opening a PR:

```bash
npm run format
uv run quarto render
```

## Python tooling

- Python version: `3.14` (see `.python-version`)
- Environment manager: `uv`
- Quarto execution support: `jupyter`, `ipykernel`
- Dev tooling: `ruff`, `ty`, `pytest`, `pytest-cov`

### Agents tooling specification

This repository uses the following default Python tooling for agentic workflows.

#### 1. Core development tooling (Astral + testing)

- uv
- ruff
- ty
- pytest
- pytest-cov

#### 2. Service and I/O

- httpx

#### 3. Data and models

- pydantic
- pydantic-settings
- pandas

#### 4. Interaction and orchestration

- marimo

#### 5. Observability

- structlog

#### 6. Visualisation

- altair
- matplotlib

#### Coding guidelines

- **Type safety:** use type hints throughout all code.
- **Data structure:** use Pydantic models or Python dataclasses for structured data.
- **Documentation:** include docstrings for all functions, including examples that serve as tests.
- **Testing:** aim for and maintain 100% test coverage on core logic and tool definitions.
- **Paradigm:** prefer functional programming patterns over object-oriented programming.

#### Pyodide and runtime constraints

- **Browser compatibility:** all simple applications and tools should be compatible with Pyodide
  (WASM). Avoid libraries with heavy C-extensions or system-level dependencies not supported in
  WASM.
- **Development vs. runtime:** core development tooling is development-only; service, data,
  interaction, observability, and visualisation libraries are runtime-usable.

Common commands:

```bash
uv sync
uv run ruff check .
uv run ty check
uv run pytest
uv run quarto render
```

## Blog content model

### Folder structure (required)

- Blog posts: `posts/<yyyy-mm-dd>-<slug>/index.qmd`
- Events: `events/<yyyy-mm-dd>-<slug>/index.qmd`
- Post assets live next to the entry: `posts/<entry>/images/*`
- Event assets live next to the entry: `events/<entry>/images/*`

### Front matter (recommended minimum)

- `title`
- `date`
- `author` (for events: organizer)
- `author-title` (for events: set to `Organizer`)
- `description` (teaser)
- `categories`:
  - Blog posts: exactly one of: `Track 1`, `Track 2`, `Track 3`, `Track 4`, `General`
  - Events: exactly one of `NAIF event`, `NAIF participation`, `NAIF related`
- `tags`: exactly 3 tags
- `proofread`: `true` or `false`
- `image`: a local image path (used for listing cards)

### Images

- Use 1-3 high-resolution images where possible.
- Every image must have:
  - descriptive alt text
  - a caption
  - rights attribution (in the caption)

### Reposts

- Reposts are allowed only with permission.
- Add a visible note near the top linking back to the original URL.

### Events: registration links

- Future events: keep `Registration` and `Event page` as clickable links.
- Past events: disable registration links (render as plain text and strikethrough) and add a short
  note that the event already took place.

## Drafts (work-in-progress content)

- Use `draft: true` in the front matter for work-in-progress posts/events.
- Drafts are not included in navigation, listings, search results, or the sitemap on
  `quarto render`.
- Drafts are visible when using `quarto preview` (they render with a "Draft" banner).

## Links

- Use:
  - https://eth-library.github.io/naif/
  - https://github.com/eth-library/naif

## URL aliases (required)

When pages are moved or deleted, always preserve old URLs by adding `aliases` to the destination
page.

- Quarto reference: https://quarto.org/docs/reference/formats/html.html#website
- Use the previously published sitemap (`https://eth-library.github.io/naif/sitemap.xml`) as the
  source of truth for legacy URLs.
