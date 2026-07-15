# Share cvWriter

This repository now contains a repo-local Codex plugin for `cvwriter`.

## Plugin files

- Plugin package: `plugins/cvwriter`
- Marketplace file: `.agents/plugins/marketplace.json`

## How another user installs it

1. Clone or copy this repository locally.
2. Add the repo-local marketplace to Codex:

```powershell
codex plugin marketplace add C:\path\to\cvWriter
```

3. Install the plugin from that marketplace:

```powershell
codex plugin add cvwriter@personal
```

4. Start a new Codex task so the new skill is loaded.

## Updating an installed copy

If the plugin source changes after installation, reinstall it instead of editing marketplace files by hand:

```powershell
python C:\Users\Bande\.codex\skills\.system\plugin-creator\scripts\update_plugin_cachebuster.py C:\path\to\cvWriter\plugins\cvwriter
codex plugin add cvwriter@personal
```

Then start a new Codex task so Codex picks up the refreshed skill bundle.

## What the other user still needs

- Their own `cv-data/` content
- Python available in the environment
- `reportlab` installed for PDF generation

## Recommended usage model

Keep the plugin source as the shared package and keep each user's CV workspace separate. The plugin includes a bootstrap script and templates so each person can initialize their own workspace without copying your personal resume data.
