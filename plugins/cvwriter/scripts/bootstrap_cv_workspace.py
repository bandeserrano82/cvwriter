#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PLUGIN_ROOT / "templates"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_template(src: Path, dest: Path) -> None:
    if dest.exists():
        return
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def bootstrap(workspace: Path) -> None:
    cv_data = workspace / "cv-data"
    experiences = cv_data / "experiences"
    projects = cv_data / "projects"
    links = cv_data / "links"
    source_documents = cv_data / "source-documents"
    job_targets = workspace / "job-targets"
    generated_cvs = workspace / "generated-cvs"
    repo_analysis = workspace / "repo-analysis-results"

    for path in (
        cv_data,
        experiences,
        projects,
        links,
        source_documents,
        job_targets,
        generated_cvs,
        repo_analysis,
    ):
        ensure_dir(path)

    copy_template(TEMPLATES_DIR / "profile.template.json", cv_data / "profile.json")
    copy_template(TEMPLATES_DIR / "experience.template.json", experiences / "_template.json")
    copy_template(TEMPLATES_DIR / "project.template.json", projects / "_template.json")

    repo_links_path = links / "repo-links.json"
    if not repo_links_path.exists():
        write_json(
            repo_links_path,
            {
                "updated_at": now_utc(),
                "repos": {},
            },
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a cvWriter workspace with starter files.")
    parser.add_argument(
        "--workspace",
        required=True,
        help="Path to the target workspace root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    ensure_dir(workspace)
    bootstrap(workspace)
    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
