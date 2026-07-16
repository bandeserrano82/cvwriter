# cvWriter

`cvWriter` is a Codex plugin for people looking for work who want one organized place to manage job posts, applications, repository-backed skill evidence, and tailored resumes.

In plain language, `cvWriter` helps users:

- organize their job search in a structured workspace
- keep job posts and application materials connected
- scan their own repositories for evidence of skills and experience without exposing private code outside their environment
- generate tailored resumes grounded in real evidence
- produce polished final PDFs when they are ready to apply

On first use, the intended experience is guided onboarding. Instead of expecting users to know the file structure, Codex should walk them through profile details, work experience, education, projects, and repository links step by step, then write that information into the workspace.

The plugin contains:

- a `cvwriter` skill for Codex
- reusable Python scripts for managing CV data, job targets, and CV authoring payloads
- starter JSON templates for each user to fill with their own background

The plugin does not include personal resume data or generated outputs.

## Important path behavior

The scripts are bundled inside the plugin package. They are not copied into the user's workspace.

- Run plugin scripts from `<plugin-root>\scripts\...`
- The scripts read and write data in the current workspace unless a command exposes an explicit `--workspace` flag
- `bootstrap_cv_workspace.py` is the only setup command that takes a target workspace path directly

## What users need

Each user needs:

- Codex with this plugin installed
- Python 3.11+ available in the environment
- `reportlab` installed if they want PDF output

Install the PDF dependency with:

```powershell
python -m pip install reportlab
```

## Expected workspace layout

The scripts operate on the current workspace directory and expect these folders at the workspace root:

```text
cv-data/
job-targets/
generated-cvs/
repo-analysis-results/
```

Users can bootstrap a fresh workspace from the included templates:

```powershell
python <plugin-root>\scripts\bootstrap_cv_workspace.py --workspace <their-workspace>
```

After bootstrap, run the remaining commands from the workspace root so generated files land in the expected folders.

## Typical workflow

1. Initialize the workspace.
2. Add profile and education details.
3. Add experiences and projects under `cv-data/`.
4. Import a job posting with `<plugin-root>\scripts\manage_job_targets.py`.
5. Export a single structured workspace payload with `<plugin-root>\scripts\prepare_cv_payload.py`.
6. Let Codex read that payload and decide how to select, prioritize, and phrase the CV content.
7. Render the markdown to PDF with `<plugin-root>\scripts\render_cv_pdf.py`.

The `cvwriter` skill in Codex wraps this workflow and should be preferred over invoking the scripts manually.

## AI-authored CVs

`prepare_cv_payload.py` does not write the CV itself. Instead, it creates a single structured JSON payload plus brief/output metadata:

- `authoring-payload.json`
- `authoring-brief.md`

Codex reads those files and writes:

- `cv.draft.md`
- `cv.md`
- `latest.md` for generated-cvs mirrors when applicable

This keeps workspace export deterministic while moving all selection and writing decisions into the model.

`generate_cv.py` remains as a compatibility wrapper that forwards to `prepare_cv_payload.py`.

## Install and update

This repository uses a repo-local marketplace file at `.agents/plugins/marketplace.json`.

Another user can install the plugin by pointing Codex at the repository root:

```powershell
codex plugin marketplace add C:\path\to\cvWriter
codex plugin add cvwriter@personal
```

When updating an already-installed local plugin, reinstall it after bumping the Codex cachebuster, then start a new Codex task so the refreshed skill is loaded.
