# Final Release Candidate — 2026-04-15

**Git tag / release title:** Final Release Candidate  

Brief notes derived from [CHANGELOG.md](CHANGELOG.md). Full detail and PR references are in the changelog.

## Highlights

- **Run Matrix** — Pick solver × system cells, optional session label, background runs via `POST /api/run_solvers`, live status in the grid, saved matrix presets.
- **Job Activity** — One place for active invocations and stored runs: filters, live logs, cancel, baseline, delete, SLURM refresh when applicable.
- **Navigation** — Home → Run Matrix → Job Activity → Individual Trends → Long-Term Trends → Configs (default page: Home). Legacy sidebar names map to Run Matrix / Job Activity.
- **UX** — Completion toasts when background work finishes; Long-Term Trends metric clicks can open Job Activity with a run pre-selected.
- **Solvers & ops** — OpenMM example solver; GROMACS example hardening (inputs, Docker, logging/parser); live log streaming refactor; Playwright E2E aligned with `data-testid` and new pages.

## Documentation

- Guides under `docs/` use consistent **UPPER_SNAKE_CASE** names; see **UI_DESIGN.md** for the Streamlit spec and **TESTING_SLURM.md** for SLURM smoke workflows.
- Post–FRC doc updates (e.g. **ARCHITECTURE.md** async invocation section) may appear under the **Released** section in the changelog after this tag.

## Removed / tightened

- Redundant Streamlit pages consolidated into Run Matrix + Job Activity; in-app **Tests** removed (use `make test` / `make test-e2e`).
- **`docs/demo/`** course walkthrough markdown removed from the repo.
- GROMACS multi-GPU scripting disabled until validated.

## Upgrade notes

- Prefer **`run_solvers`** and the **Run Matrix** / **Job Activity** UI over legacy “Run Jobs” / “Solvers” language. See **UI_DESIGN.md** and changelog **Breaking changes** under **[0.0.0]**.
