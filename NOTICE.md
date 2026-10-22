# NOTICE

## Attribution

This repository adapts the workflow / router / agent-role structure of **Academic Research Skills (ARS)**:

- Upstream project: <https://github.com/Imbad0202/academic-research-skills>
- Codex distribution referenced: `academic-research-suite` in <https://github.com/Imbad0202/academic-research-skills-codex>
- Author / maintainer: Cheng-I Wu (吳政宜)
- Upstream license: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

## What was adapted

- The five-workflow concept (deep research, paper writing, paper review, end-to-end pipeline, experiment design).
- The intent-based routing pattern, `ars-*` alias shortcuts, and the "vague topic → Socratic scoping first" override.
- The agent-role pattern (role cards with input/output contracts, devil's advocate, editor-in-chief).
- The integrity-gate idea and the "verify sources; mark unverifiable items" evidence discipline.
- The review report / decision letter / revision roadmap shapes.

## What is new in this repository

All prose in `SKILL.md`, `workflows/`, `agents/`, `references/`, `templates/`, and `scripts/` was written for DeepSeek Harness (DSH). No upstream file is vendored or copied verbatim. Upstream mechanisms that do not exist in DSH (Claude Code hooks, plugin marketplace, slash-command registry, fixed agent-team topology, 0–100 review scoring) were removed rather than ported.

## Disclaimer

This is **not** an official distribution of ARS, and it is not endorsed by the upstream author. The name `academic-research-suite` belongs to the upstream Codex distribution; this repository uses `ars-research-suite` as its DSH skill name.

## License of this repository

CC BY-NC 4.0 (see [LICENSE](LICENSE)). Non-commercial use only; attribution required.

Attribution format suggestion:

```text
Based on Academic Research Skills by Cheng-I Wu (https://github.com/Imbad0202/academic-research-skills, CC BY-NC 4.0),
adapted for DeepSeek Harness as ars-research-suite.
```
