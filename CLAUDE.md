# CLAUDE.md — alihusseini07 profile repo

## Git rules
- **Never push to remote.** Local commits only. User pushes manually.
- **Never commit without explicit user instruction.** Do not auto-commit after edits.
- Never amend published commits.
- Never force-push.

## Project overview
GitHub profile README repo for Ali Husseini (alihusseini07).

## Key files
- `README.md` — profile page rendered on github.com/alihusseini07
- `assets/hero.svg` — terminal-style hero banner (hand-crafted SVG)
- `assets/stack-tree.svg` — tech stack visualization
- `assets/project-cards.svg` — featured project cards (generated SVG)
- `assets/contributions-v2.svg` — 30-day contribution graph (auto-generated)
- `scripts/generate_contributions.py` — fetches GitHub GraphQL API, pads missing days to today, writes contributions-v2.svg
- `scripts/generate_project_cards.py` — generates project-cards.svg
- `.github/workflows/update-contributions.yml` — runs daily at 1 AM UTC, commits contributions-v2.svg

## Contact info
- Email: ahusseini007@gmail.com
- Portfolio: https://alihusseini.ca/
- LinkedIn: https://www.linkedin.com/in/ahusseini-profile
- Devpost: https://devpost.com/ahusseini007

## Contribution graph notes
- GitHub GraphQL API lags 1-2 days; script pads missing days with 0 to always show current date
- Workflow stages `assets/contributions-v2.svg` (not `contributions.svg`)
- README references `contributions-v2.svg`

## Style
- SVGs use dark terminal aesthetic: bg `#06080C`/`#0A1118`, cyan `#22D3EE`, green `#4ADE80`, muted `#7E94A8`
- Monospace font stack: `ui-monospace, SFMono-Regular, Menlo, Consolas, 'Courier New', monospace`
