---
name: cvwriter
description: Create and maintain a structured CV workspace, import job descriptions, prepare grounded CV evidence payloads, draft CVs from that evidence, and render final PDFs. Use when Codex should help a user set up resume data, tailor a CV to a role, or prepare a polished CV artifact from a local workspace.
---

# cvWriter

This skill operates on the current workspace. The workspace root is expected to contain:

- `cv-data/`
- `job-targets/`
- `generated-cvs/`
- `repo-analysis-results/` when repo-skill analysis is used

The reusable scripts live under `scripts/` inside this plugin package, not inside the user's workspace.

Before running a plugin script, resolve the plugin root from this skill file and use an absolute script path under that root.

- Treat the plugin root as two directories above this `SKILL.md`
- Use `<plugin-root>/scripts/...` when invoking bundled Python scripts
- Do not assume `scripts/` exists in the workspace root

## Setup

If the workspace does not already contain `cv-data/profile.json`, initialize it first:

```powershell
python <plugin-root>\scripts\bootstrap_cv_workspace.py --workspace <workspace-root>
```

Then ask the user to provide or update:

- `cv-data/profile.json`
- `cv-data/experiences/*.json`
- `cv-data/projects/*.json`
- `cv-data/source-documents/` when source resume text is available

Use the template files in `templates/` as the schema reference.

## Workflow

1. Initialize the workspace when needed.
2. Maintain structured profile, experience, and project data with `<plugin-root>\scripts\manage_cv_data.py`.
3. Import a job posting with `<plugin-root>\scripts\manage_job_targets.py`.
4. Export a general or job-targeted workspace payload with `<plugin-root>\scripts\prepare_cv_payload.py`.
5. Read the generated `authoring-payload.json` and draft the CV yourself in markdown.
6. Save a reviewable draft to `cv.draft.md`, refine it into `cv.md`, and mirror `latest.md` when the payload brief specifies one.
7. Render the approved markdown to PDF with `<plugin-root>\scripts\render_cv_pdf.py`.

## AI Authoring Contract

`prepare_cv_payload.py` does not write the CV body. It exports the structured workspace data for you to author from.

After running it:

- Read `authoring-payload.json`
- Read `authoring-brief.md`
- Draft the CV in markdown using only the supplied evidence
- Write the first pass to `cv.draft.md`
- Save the refined final version to `cv.md`
- If the brief names a generated-cvs mirror target such as `latest.md`, keep it in sync

When writing:

- Do not invent metrics, dates, tools, projects, or responsibilities
- Make all selection, prioritization, grouping, and emphasis decisions yourself
- Prefer explicit manual highlights and notes over inferred repo evidence
- Use repo evidence to support technical depth, not to fabricate ownership claims
- Omit unsupported claims instead of guessing
- Keep the output concise, credible, and role-aligned
- Include only sections with grounded content

## Commands

Initialize a workspace:

```powershell
python <plugin-root>\scripts\bootstrap_cv_workspace.py --workspace <workspace-root>
```

Create an experience record:

```powershell
python <plugin-root>\scripts\manage_cv_data.py create-experience --company "Company" --title "Role"
```

Create a project record:

```powershell
python <plugin-root>\scripts\manage_cv_data.py create-project --name "Project"
```

Import a job description file:

```powershell
python <plugin-root>\scripts\manage_job_targets.py import-file --path <job-file> --title "Role" --company "Company"
```

Import pasted job text:

```powershell
python <plugin-root>\scripts\manage_job_targets.py import-text --title "Role" --company "Company" --text-file <path-to-text>
```

Prepare a general CV authoring payload:

```powershell
python <plugin-root>\scripts\prepare_cv_payload.py --general
```

Prepare a targeted CV authoring payload:

```powershell
python <plugin-root>\scripts\prepare_cv_payload.py --job <job-slug>
```

After payload generation, author the markdown CV yourself and save it to the output paths named in the generated brief.

`generate_cv.py` remains available as a compatibility wrapper, but new workflows should call `prepare_cv_payload.py`.

Render PDF output:

```powershell
python <plugin-root>\scripts\render_cv_pdf.py --input <cv-markdown> --output <cv-pdf>
```

## Working rules

- Do not invent resume content. Keep profile and experience data user-authored.
- Preserve the user's existing CV data and generated outputs unless they ask for cleanup.
- Treat repo analysis as evidence-backed input, not as a replacement for user confirmation.
- Prefer generating markdown first, then PDF, so the user can review the draft.
- Treat the payload as the evidence boundary. Do not roam the workspace for extra facts unless the user explicitly asks you to.
- Do not assume the payload has already selected the best experiences or skills. That judgment belongs to the AI authoring step.
- Run `<plugin-root>\scripts\validate_cv_workspace.py` when workspace data looks suspicious or payload preparation fails.

## Templates

The plugin provides:

- `templates/profile.template.json`
- `templates/experience.template.json`
- `templates/project.template.json`

Use them when creating or validating a workspace schema.
