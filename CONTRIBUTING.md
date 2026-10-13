# Contributing

Improvements are welcome when they help a learner understand **every substantive page**, preserve one evolving Markdown document, or make source coverage more reliable.

1. Open an issue describing a reproducible teaching or tooling problem. Include a small **self-authored or synthetic** example instead of someone else's slides or private notes.
2. Make a focused change. Keep the skill usable without optional scripts and avoid turning it into a slide generator, summary-only workflow, or general learning platform.
3. Run `python -m unittest discover -s tests -v`. For changes to `SKILL.md`, also run Codex's `skill-creator` validator if available and test the behavior on a realistic, shareable example.
4. Explain what changed, how you tested it, and any remaining limitations in the pull request.

Please do not commit credentials, real courseware, learner progress files, generated personal notes, or copyrighted slide images. The project uses the [MIT License](LICENSE).
