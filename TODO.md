# TODO

## Navigation

- [x] Reduce top navigation to: Home, Blog, About, Docs
- [x] Keep Join + Contact as a persistent CTA (sidebar card)
- [ ] Add redirect/stub pages for renamed routes (`news` -> Blog, `resources` -> Docs)

## Blog

- [x] Create Blog hub with listing + category filter (Blog Post vs Event)
- [x] Enforce folder-per-entry structure (`posts/<date>-<slug>/`)
- [x] Add repost #1 (SYoS, 31 Oct 2025) with local images and attribution
- [x] Add repost #2 (UZH, 12 Nov 2025) with local images and attribution
- [x] Migrate remaining legacy content into individual entries
- [x] Decide whether to add RSS feed for Blog

## About

- [x] Consolidate project context + Tracks 1-4 + Team into `about.qmd`
- [x] Review copy for plain-language tone and consistency

## Docs

- [x] Replace Resources with Docs (Zenodo portal)
- [ ] Curate a short list of “key deliverables” (DOI-first) to feature on Docs

## Repo hygiene

- [x] Add Prettier for Markdown formatting (`npm run format`)
- [x] Add `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`
- [x] Add licenses (AGPLv3 for code, CC BY 4.0 for content)
- [x] Add GitHub PR + Issue templates

## Build

- [x] Run `npm run format`
- [x] Run `quarto render`
