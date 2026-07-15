---
name: cvwriter
description: Create and maintain a structured CV workspace, import job descriptions, generate targeted CV drafts, and render final PDFs. Use when Codex should help a user set up resume data, tailor a CV to a role, or prepare a polished CV artifact from a local workspace.
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
4. Generate a general or job-targeted CV with `<plugin-root>\scripts\generate_cv.py`.
5. Render the generated markdown to PDF with `<plugin-root>\scripts\render_cv_pdf.py`.

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

Generate a general CV:

```powershell
python <plugin-root>\scripts\generate_cv.py --general
```

Generate a targeted CV:

```powershell
python <plugin-root>\scripts\generate_cv.py --job <job-slug>
```

Render PDF output:

```powershell
python <plugin-root>\scripts\render_cv_pdf.py --input <cv-markdown> --output <cv-pdf>
```

## Working rules

- Do not invent resume content. Keep profile and experience data user-authored.
- Preserve the user's existing CV data and generated outputs unless they ask for cleanup.
- Treat repo analysis as evidence-backed input, not as a replacement for user confirmation.
- Prefer generating markdown first, then PDF, so the user can review the draft.

## Templates

The plugin provides:

- `templates/profile.template.json`
- `templates/experience.template.json`
- `templates/project.template.json`

Use them when creating or validating a workspace schema.
