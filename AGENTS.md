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
quarto render
```

## Blog content model

### Folder structure (required)

- Blog posts: `blog/posts/<yyyy-mm-dd>-<slug>/index.qmd`
- Events: `blog/events/<yyyy-mm-dd>-<slug>/index.qmd`
- Assets live next to the entry: `blog/.../<entry>/images/*`

### Front matter (recommended minimum)

- `title`
- `date`
- `author`
- `description` (teaser)
- `categories`: exactly one of `Blog Post` or `Event`
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
