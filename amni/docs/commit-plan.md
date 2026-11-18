# Retrospective commit plan

This plan organizes the existing AMNI prototype into feature-sized commits.
The proposed dates, October 30–November 18, 2026, form a reconstructed timeline;
they are not recovered records of work performed on those days.

The initial history follows the milestones below. Each reconstructed commit
includes its retrospective context in the commit body. The destination is
`https://github.com/Aishagojo/Amni.git`, using the account’s public GitHub
noreply author address. See [the history note](history-reconstruction.md).

| Proposed date | Commit subject |
| --- | --- |
| 2026-10-30 | `chore(repo): initialize AMNI workspace and ignore generated files` |
| 2026-10-31 | `chore(frontend): configure Next.js, TypeScript, and Tailwind` |
| 2026-11-01 | `feat(frontend): add the application shell and homepage foundation` |
| 2026-11-02 | `feat(branding): introduce the custom AMNI mark and app icon` |
| 2026-11-03 | `feat(home): add the connected support illustration` |
| 2026-11-04 | `feat(cases): define case types and sample workspace data` |
| 2026-11-05 | `feat(cases): add queue search and status filters` |
| 2026-11-06 | `feat(cases): add case creation and detail dialogs` |
| 2026-11-07 | `feat(cases): persist demo cases in browser storage` |
| 2026-11-08 | `feat(cases): support investigation, resolution, and reopening` |
| 2026-11-09 | `feat(knowledge): add topic filters and troubleshooting guides` |
| 2026-11-10 | `feat(diagnostics): add the simulated connectivity-check workflow` |
| 2026-11-11 | `feat(platform): add the planned architecture overview` |
| 2026-11-12 | `feat(design): introduce the responsive teal, cream, and yellow theme` |
| 2026-11-13 | `chore(assets): bundle self-hosted typography and font licensing` |
| 2026-11-14 | `chore(backend): scaffold Python application and test directories` |
| 2026-11-15 | `chore(infra): add Compose, Nginx, and CI directory placeholders` |
| 2026-11-16 | `docs(architecture): describe the planned backend and AWS deployment` |
| 2026-11-17 | `docs(design): document the visual system and verified previews` |
| 2026-11-18 | `docs(readme): document setup, project status, and implementation roadmap` |

## Commit boundaries

Each commit should introduce a coherent part of the project, with actual file
changes rather than empty commits. Infrastructure and backend subjects describe
scaffolds because those services are not implemented. The final tree should
preserve the current working application and documentation.

Use the repository-local author identity supplied by the project owner. Push the
project only to the supplied destination. The later owner-requested removal of
the standalone layout commit normalizes the initial history under `amni/`; its
push must use an explicit lease against the previously verified remote tip.
