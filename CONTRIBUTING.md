# Contributing

Thanks for considering a contribution.

## Ground rules

- Please discuss significant changes via an issue first.
- Be respectful and follow `CODE_OF_CONDUCT.md`.

## Pull request process

1. Create a branch.
2. Make your changes.
3. Run:

   ```bash
   npm install
   uv sync
   npm run format
   uv run quarto render
   ```

4. Open a pull request.

## Content contributions

- Blog entries must follow the folder-per-entry structure described in `AGENTS.md`.
- British English is preferred for posts and event pages, except reposts where source wording may be
  preserved.
- Keep images local to the entry folder and include alt text, caption, and rights attribution.
