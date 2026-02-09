# NAIF

[![DOI](https://zenodo.org/badge/GITHUB_REPO_ID.svg)](https://zenodo.org/badge/latestdoi/ZENODO_RECORD)

National Approach for Interoperable repositories and Findable research results (NAIF) is a project
initiated and funded by eight Swiss Higher Education Institutions and co-funded by
swissuniversities.

- Website: https://eth-library.github.io/naif/
- Repository: https://github.com/eth-library/naif

## About

This repository contains the source for the NAIF project website, built with
[Quarto](https://quarto.org/) (`.qmd` + `_quarto.yml`).

## Getting started

### Requirements

- Quarto
- Node.js (for formatting Markdown with Prettier)
- Python 3.14
- uv

### Install

```bash
npm install
uv sync
```

### Format and build

```bash
npm run format
uv run quarto render
```

### Preview locally

```bash
uv run quarto preview
```

## Content workflow

- Blog entries live in `posts/<yyyy-mm-dd>-<slug>/index.qmd`.
- Every blog entry has its own folder and keeps assets (images) in a local `images/` subfolder.
- Reposts must include a clear source note and link back to the original publication.

## Support

- Bug reports / requests: https://github.com/eth-library/naif/issues
- Security issues: see `SECURITY.md`

## Contributing

See `CONTRIBUTING.md`.

## Citation

If you reuse this repository's code or content, please cite it using `CITATION.cff`.

## License

- Code: GNU AGPLv3, see `LICENSE-AGPL.md`
- Content (text and media unless noted otherwise): CC BY 4.0, see `LICENSE-CCBY.md`
