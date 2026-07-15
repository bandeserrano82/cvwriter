# cvWriter

`cvWriter` is a Codex plugin that packages the reusable CV-generation workflow from this repository.

The plugin contains:

- a `cvwriter` skill for Codex
- reusable Python scripts for managing CV data and job targets
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
2. Fill `cv-data/profile.json`.
3. Add experiences and projects under `cv-data/`.
4. Import a job posting with `<plugin-root>\scripts\manage_job_targets.py`.
5. Generate a CV with `<plugin-root>\scripts\generate_cv.py`.
6. Render the markdown to PDF with `<plugin-root>\scripts\render_cv_pdf.py`.

The `cvwriter` skill in Codex wraps this workflow and should be preferred over invoking the scripts manually.

## Install and update

This repository uses a repo-local marketplace file at `.agents/plugins/marketplace.json`.

Another user can install the plugin by pointing Codex at the repository root:

```powershell
codex plugin marketplace add C:\path\to\cvWriter
codex plugin add cvwriter@personal
```

When updating an already-installed local plugin, reinstall it after bumping the Codex cachebuster, then start a new Codex task so the refreshed skill is loaded.
