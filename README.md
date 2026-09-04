# cvWriter

`cvWriter` is primarily a repo-local Codex plugin for the ChatGPT desktop app. It gives you a guided workflow for organizing resume data, tracking job targets, grounding claims in repository evidence, and producing tailored CV outputs. The repository also includes the underlying workspace folders and scripts that power that plugin.

Use this repository if you want to:

- install a shareable Codex plugin from a local repository
- keep resume source data in structured JSON instead of scattered notes
- track job descriptions alongside tailored application outputs
- connect projects and repositories to specific experience bullets
- generate CV authoring payloads for AI-assisted resume drafting
- render finalized markdown CVs to PDF

## Plugin-first workflow

The intended way to use `cvWriter` is through the bundled plugin in `plugins/cvwriter` from the ChatGPT desktop application. The root workspace and scripts exist to support that plugin and to make the repository portable.

## Quick start

Install and use the plugin from the ChatGPT app:

1. Open the ChatGPT desktop app.
2. Open Codex and point it at this repository folder.
3. Add this repository as a local plugin marketplace in the app.
4. Install the `cvwriter` plugin from that marketplace.
5. Start a new Codex task so the `cvwriter` skill loads.
6. Ask Codex to help you set up or update your CV workspace.

The plugin is meant to guide onboarding instead of making you learn the folder structure first.

## Repository layout

```text
cv-data/            Structured profile, experience, project, and link data
generated-cvs/      Drafts and finalized CV outputs
job-targets/        Imported job postings and parsed targeting data
plugins/cvwriter/   Repo-local Codex plugin and templates
scripts/            Root entrypoints for the main workflow
SHARE-CVWRITER.md   Notes for sharing the plugin with another user
```

The root `scripts/` directory contains manual entrypoints for the same workflow. Some are thin wrappers around the bundled plugin implementation so the repo can be used both as a standalone workspace and as a shared plugin source.

## Requirements

- Python 3.11+
- `reportlab` for PDF output

Install the PDF dependency with:

```powershell
python -m pip install reportlab
```

## Manual workflow

If you want to work without the plugin, the repository can still be used directly from the workspace root.

Initialize the structured CV data folders:

```powershell
python scripts/manage_cv_data.py init
```

Create a first experience entry:

```powershell
python scripts/manage_cv_data.py create-experience `
  --company "Example Corp" `
  --title "Software Engineer" `
  --employment-type "Hire (W2)" `
  --work-mode "full-time"
```

For W2 through staffing-company engagements, provide the proxy company in a
separate JSON file and reference it when creating the experience:

```json
{
  "name": "Example Staffing",
  "website": "https://example.com",
  "address": {
    "line1": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "phone": "+1-555-0100",
  "email": "contact@example.com",
  "contact_person": {
    "name": "Jane Smith",
    "title": "Account Manager",
    "email": "jane.smith@example.com",
    "phone": "+1-555-0101",
    "linkedin": "https://www.linkedin.com/in/janesmith"
  }
}
```

```powershell
python scripts/manage_cv_data.py create-experience `
  --company "Client Corp" `
  --title "Software Engineer" `
  --employment-type "W2 through Staffing Company" `
  --work-mode "full-time" `
  --proxy-company-file .\example-staffing.json
```

Supported employment relationships are `Hire (W2)`, `W2 through Staffing Company`,
`Contract (1099)`, `Hire`, and `Contract`. `proxy_company` is `null` for direct
engagements. For W2 through staffing-company relationships, it is a company object with `name`, `website`,
`address`, `phone`, `email`, and a nested `contact_person` record containing
their name, title, department, email, phone, and LinkedIn URL. This private
data is not included in generated CVs by default.

Each generated CV experience heading uses this order: job title, company,
employment type, proxy company name when present, work mode, and location.
Only the proxy company name is rendered; its address and contact details remain
private.

Generated CVs use the employment type value as written.

Experience entries render across three lines: a title and company heading, an
employment-type and proxy-company subheading, and a work-mode, location, and
dates subsubheading.

Create a project entry:

```powershell
python scripts/manage_cv_data.py create-project `
  --name "cvWriter"
```

Import a job posting from a text file:

```powershell
python scripts/manage_job_targets.py import-file `
  --path .\job-posting.txt `
  --company "Example Corp"
```

Prepare the authoring payload for a targeted CV:

```powershell
python scripts/prepare_cv_payload.py
```

Render a finished markdown CV to PDF:

```powershell
python scripts/render_cv_pdf.py `
  --input .\generated-cvs\example\cv.md `
  --output .\generated-cvs\example\cv.pdf
```

## Main commands

### `manage_cv_data.py`

Manages structured resume content under `cv-data/`.

- `init`
- `sync-repos`
- `create-experience`
- `create-project`
- `link-repo`
- `add-manual-evidence`
- `list-unlinked`

This script creates and updates:

- `cv-data/profile.json`
- `cv-data/experiences/*.json`
- `cv-data/projects/*.json`
- `cv-data/links/repo-links.json`

### `manage_job_targets.py`

Imports job descriptions into `job-targets/` and produces parsed targeting metadata.

Supported entrypoints:

- `import-text`
- `import-file`
- `import-folder`
- `import-link`

Each imported job target gets its own folder with source material, parsed JSON, and output space.

### `prepare_cv_payload.py`

Builds the structured authoring payload used for AI-assisted CV drafting. The plugin implementation writes deterministic workspace artifacts such as:

- `authoring-payload.json`
- `authoring-brief.md`

### `render_cv_pdf.py`

Converts a markdown CV into a simple PDF using ReportLab.

## Plugin details

This repo includes a shareable Codex plugin in `plugins/cvwriter`. More detail on sharing and updating it is in [SHARE-CVWRITER.md](/C:/Users/Bande/OneDrive/Documents/cvWriter/SHARE-CVWRITER.md).

## Notes

- Personal resume data is expected to live in `cv-data/` and generated outputs in `generated-cvs/`.
- The bundled plugin is designed to be shared without shipping anyone's personal resume content.
- Root scripts should be run from the repository root so files land in the expected workspace folders.
