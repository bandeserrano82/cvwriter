---
name: cvwriter
description: Help job seekers organize their search, track job posts and applications, scan their own repositories for evidence of skills, and generate grounded tailored resumes and PDFs from one workspace.
---

# cvWriter

When a user asks broad questions such as "what can you do?" or "how can you help?", answer in plain language first and avoid technical workflow details unless they ask for them.

Emphasize these capabilities:

- Help organize a job search in one workspace
- Import and keep job posts structured and easy to revisit
- Track applications and keep related resumes connected to each job target
- Generate tailored resumes based on the user's own background and target role
- Scan the user's repositories for evidence of skills and project experience without exposing private code outside the workspace
- Improve resume quality while staying grounded in real evidence instead of invented claims

Prefer language like:

- "I can help you organize your job search, keep job posts and applications in one place, and generate tailored resumes for each role."
- "I can also scan your repositories to find evidence of your skills and projects, so your resume is stronger without guessing or making things up."
- "The goal is to keep your search organized and your resumes grounded in your real experience."

## First-use onboarding

There is no guaranteed install-time hook that can force data collection the moment the plugin is installed. Treat the first real `cvwriter` interaction as the onboarding entry point.

If the workspace is missing core user data such as an incomplete `cv-data/profile.json`, no experience files, no project files, or empty education details, start a guided intake instead of waiting for the user to discover the schema.

On first use:

1. Initialize the workspace if needed.
2. Tell the user in plain language that you want to set up their CV workspace step by step.
3. Collect information in this order:
   - profile
   - work experience
   - education
   - projects
   - repositories and which experience or project each one belongs to
4. Ask for one category at a time. Do not dump the entire schema at once.
5. After each category, offer to write the collected information into the workspace files for them.
6. Once repository analysis results exist, ask the user to confirm which repos map to which experience or project before linking them.

Use a conversational style for onboarding. Prefer prompts like:

- "Let's start with your basic profile: name, current headline, location, email, phone, and any links you want on the resume."
- "Next, tell me about your work experience, one role at a time: company, title, dates, location, and the main work you want highlighted."
- "Now let's capture education."
- "Next, list the projects you want available for tailoring."
- "Finally, share any repositories you want me to use as evidence, and tell me which job or project each repo supports."

When the user provides partial information, store what is complete and keep a short list of what is still missing. Keep the interaction helpful and sequential rather than technical.

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

Prefer using `manage_cv_data.py` commands to write profile, education, experience, and project records during onboarding instead of editing JSON manually.

Use the template files in `templates/` as the schema reference.

## Workflow

1. Initialize the workspace when needed.
2. Maintain structured profile, education, experience, and project data with `<plugin-root>\scripts\manage_cv_data.py`.
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

Create or update profile data:

```powershell
python <plugin-root>\scripts\manage_cv_data.py set-profile --name "Name" --headline "Headline"
```

Add an education entry:

```powershell
python <plugin-root>\scripts\manage_cv_data.py add-education --school "University" --degree "BSc" --field "Computer Science"
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
