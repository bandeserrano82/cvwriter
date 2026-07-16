#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from validate_cv_workspace import validate_workspace


ROOT = Path.cwd()
CV_DATA_DIR = ROOT / "cv-data"
JOB_TARGETS_DIR = ROOT / "job-targets"
GENERATED_CVS_DIR = ROOT / "generated-cvs"
REPO_ANALYSIS_DIR = ROOT / "repo-analysis-results"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_profile() -> dict:
    return read_json(CV_DATA_DIR / "profile.json", {})


def load_items(folder: Path) -> list[dict]:
    items = []
    if not folder.exists():
        return items
    for path in sorted(folder.glob("*.json")):
        if path.name.startswith("_"):
            continue
        items.append(read_json(path, {}))
    return items


def load_repo_analyses() -> dict[str, dict]:
    analyses: dict[str, dict] = {}
    if not REPO_ANALYSIS_DIR.exists():
        return analyses
    for path in sorted(REPO_ANALYSIS_DIR.glob("*/analysis.json")):
        analyses[path.parent.name] = read_json(path, {})
    return analyses


def normalize_list(values) -> list:
    if not isinstance(values, list):
        return []
    normalized = []
    for value in values:
        if value is None:
            continue
        normalized.append(value)
    return normalized


def normalize_item(item: dict, kind: str) -> dict:
    normalized = dict(item)
    normalized["kind"] = kind
    for field in (
        "manual_highlights",
        "manual_notes",
        "manual_skills",
        "manual_tools",
        "skills_override",
        "repo_links",
        "project_links",
        "experience_links",
        "highlights",
    ):
        normalized[field] = normalize_list(normalized.get(field, []))
    return normalized


def build_workspace_payload(mode: str, job: dict | None, target_job_id: str | None) -> dict:
    profile = load_profile()
    experiences = [normalize_item(item, "experience") for item in load_items(CV_DATA_DIR / "experiences")]
    projects = [normalize_item(item, "project") for item in load_items(CV_DATA_DIR / "projects")]
    repo_analyses = load_repo_analyses()

    return {
        "generated_at": now_utc(),
        "mode": mode,
        "target_job_id": target_job_id or "",
        "profile": profile,
        "job_target": job or {},
        "workspace_data": {
            "experiences": experiences,
            "projects": projects,
            "repo_analyses": repo_analyses,
        },
        "authoring_rules": [
            "Use only evidence present in this payload.",
            "Do not invent metrics, tools, responsibilities, dates, or project ownership claims.",
            "Treat this payload as raw source material; selection, prioritization, and wording decisions belong to the AI authoring step.",
            "Prefer explicit user-authored manual content over inferred repo evidence when they conflict.",
            "Use repo evidence to support technical depth, not to fabricate ownership or impact.",
            "If evidence is weak or ambiguous, omit the claim or phrase it conservatively.",
        ],
        "output_contract": {
            "format": "markdown",
            "required_sections": [
                "Professional Summary",
                "Selected Skills",
                "Professional Experience",
            ],
            "optional_sections": [
                "Projects",
                "Education",
            ],
            "style_rules": [
                "Start with '# <name>' on the first line.",
                "Put headline on the next non-empty line when available.",
                "Put contact details on the next non-empty line when available.",
                "Use '##' for section headings and '###' for each experience or project heading.",
                "Use bullet lists for achievements under experience and project entries.",
                "Do not include any section that has no grounded content.",
            ],
        },
    }


def build_authoring_brief(payload_path: Path, draft_path: Path, final_path: Path, latest_path: Path | None) -> str:
    lines = [
        "# cvWriter Authoring Brief",
        "",
        f"- Payload: `{payload_path}`",
        f"- Draft markdown target: `{draft_path}`",
        f"- Final markdown target: `{final_path}`",
    ]
    if latest_path:
        lines.append(f"- Latest mirror target: `{latest_path}`")
    lines.extend(
        [
            "",
            "Read the payload as raw source material.",
            "Make all selection, prioritization, grouping, and wording decisions in the AI authoring step.",
            "Write the first version to the draft path, then refine it and save the final version to the final path.",
            "If a latest mirror target is present, keep it in sync with the final markdown.",
            "Do not invent missing facts; omit or soften unsupported claims instead.",
            "",
        ]
    )
    return "\n".join(lines)


def write_payload_outputs(payload: dict, output_dir: Path, generated_dir: Path | None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_path = output_dir / "authoring-payload.json"
    draft_path = output_dir / "cv.draft.md"
    final_path = output_dir / "cv.md"
    brief_path = output_dir / "authoring-brief.md"

    write_json(payload_path, payload)

    latest_path = None
    if generated_dir is not None:
        generated_dir.mkdir(parents=True, exist_ok=True)
        write_json(generated_dir / "latest.payload.json", payload)
        latest_path = generated_dir / "latest.md"

    write_text(brief_path, build_authoring_brief(payload_path, draft_path, final_path, latest_path))
    write_json(
        output_dir / "meta.json",
        {
            "type": payload["mode"],
            "generated_at": payload["generated_at"],
            "paths": {
                "payload": str(payload_path),
                "draft_markdown": str(draft_path),
                "final_markdown": str(final_path),
                "brief": str(brief_path),
            },
        },
    )


def generate_general() -> None:
    payload = build_workspace_payload("general", None, None)
    out_dir = GENERATED_CVS_DIR / "general"
    write_payload_outputs(payload, out_dir, out_dir)
    print(out_dir)


def generate_for_job(job_slug: str) -> None:
    job = read_json(JOB_TARGETS_DIR / job_slug / "parsed" / "job.json", {})
    if not job:
        raise FileNotFoundError(f"Unknown job target: {job_slug}")
    payload = build_workspace_payload("job-targeted", job, job_slug)
    out_dir = JOB_TARGETS_DIR / job_slug / "output"
    generated_dir = GENERATED_CVS_DIR / job_slug
    write_payload_outputs(payload, out_dir, generated_dir)
    print(out_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a single structured workspace payload for AI-authored general or job-targeted CVs."
    )
    parser.add_argument("--general", action="store_true")
    parser.add_argument("--job")
    args = parser.parse_args()
    if not args.general and not args.job:
        parser.error("Pass --general or --job <job-slug>.")
    return args


def main() -> int:
    args = parse_args()
    errors = validate_workspace(ROOT)
    if errors:
        print("Workspace validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    if args.general:
        generate_general()
    else:
        generate_for_job(slugify(args.job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
