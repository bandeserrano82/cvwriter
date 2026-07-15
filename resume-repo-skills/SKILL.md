---
name: resume-repo-skills
description: Analyze software repositories and infer resume-ready skills from the codebase, dependency manifests, CI files, and infrastructure files. Use when Codex needs to review a local repo, a cloned GitHub repo, or multiple repos and turn the technical evidence into a grounded skills list for a resume, CV, LinkedIn profile, or project summary.
---

# Resume Repo Skills

Analyze repositories conservatively. Only claim a skill when the repository contains direct evidence for it.

## Workflow

1. Obtain the repository source locally.
2. Run `scripts/analyze_repo_skills.py` against one or more repo paths.
3. Read the output and keep the evidence-backed skills.
4. Reuse the stored report files under `repo-analysis-results/<repo-name>/` for later rollups.
5. Rewrite the result for the target artifact: resume bullets, skills section, CV summary, or LinkedIn wording.

## Repo Access

If the user provides a GitHub URL, prefer a local clone of that repo before analysis.

- If the repo is already present locally, analyze that local path.
- If network access and approvals allow it, clone to a workspace or temp directory first.
- If cloning is not possible, ask the user for a local checkout or archive instead of guessing from the README alone.

## Analyzer Usage

Run:

```powershell
python .\scripts\analyze_repo_skills.py <repo-path>
python .\scripts\analyze_repo_skills.py <repo-a> <repo-b> --format markdown
```

The analyzer reports:

- detected languages
- frameworks and tools
- broader engineering capabilities
- confidence level
- file-based evidence for each inferred skill

The analyzer also persists results automatically in the current project workspace:

- `repo-analysis-results/<repo-name>/analysis.json`
- `repo-analysis-results/<repo-name>/analysis.md`
- `repo-analysis-results/<repo-name>/meta.json`
- `repo-analysis-results/index.json`

## Interpretation Rules

- Prefer skills with concrete evidence from source files, manifests, config, tests, or CI.
- Distinguish between `used in this repo` and `strong personal skill`.
- Treat transitive or boilerplate dependencies as weak evidence unless reinforced elsewhere.
- Prefer specific technologies over generic labels.
- Keep low-confidence items out of the final resume unless the user asks for a broader inventory.

## Resume Rewriting Rules

- Convert evidence into employer-facing wording.
- Group related tools when that reads better: `React, TypeScript, and Node.js`.
- Separate technologies from capabilities: `REST API design`, `test automation`, `CI/CD`, `containerization`.
- Avoid inflated verbs like `expert` unless the user explicitly wants self-assessment language.

## Multi-Repo Pass

When the user provides several repos:

1. Analyze each repo separately first.
2. Reuse the stored per-repo reports instead of rescanning when possible.
3. Merge overlapping skills.
4. Increase confidence when the same skill appears across multiple repos.
5. Call out specialization patterns such as frontend-heavy, backend-heavy, DevOps-heavy, or data-heavy work.
