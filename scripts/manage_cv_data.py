#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
CV_DATA_DIR = ROOT / "cv-data"
EXPERIENCES_DIR = CV_DATA_DIR / "experiences"
PROJECTS_DIR = CV_DATA_DIR / "projects"
LINKS_DIR = CV_DATA_DIR / "links"
SOURCE_DOCS_DIR = CV_DATA_DIR / "source-documents"
PROFILE_PATH = CV_DATA_DIR / "profile.json"
REPO_LINKS_PATH = LINKS_DIR / "repo-links.json"
REPO_RESULTS_INDEX = ROOT / "repo-analysis-results" / "index.json"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Value cannot be normalized into a non-empty id.")
    return slug


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dirs() -> None:
    for path in (CV_DATA_DIR, EXPERIENCES_DIR, PROJECTS_DIR, LINKS_DIR, SOURCE_DOCS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_base_files() -> None:
    ensure_dirs()

    if not PROFILE_PATH.exists():
        write_json(
            PROFILE_PATH,
            {
                "name": "",
                "headline": "",
                "summary": "",
                "location": "",
                "email": "",
                "phone": "",
                "links": {
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "updated_at": now_utc(),
            },
        )

    if not REPO_LINKS_PATH.exists():
        write_json(
            REPO_LINKS_PATH,
            {
                "updated_at": now_utc(),
                "repos": {},
            },
        )

    experience_template = EXPERIENCES_DIR / "_template.json"
    if not experience_template.exists():
        write_json(
            experience_template,
            {
                "id": "example-experience-id",
                "company": "",
                "title": "",
                "employment_type": "",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM or present",
                "location": "",
                "summary": "",
                "highlights": [],
                "skills_override": [],
                "manual_skills": [],
                "manual_tools": [],
                "manual_highlights": [],
                "manual_notes": [],
                "repo_links": [],
                "project_links": [],
                "source": {
                    "cv_file": "",
                    "notes": "",
                },
                "updated_at": now_utc(),
            },
        )

    project_template = PROJECTS_DIR / "_template.json"
    if not project_template.exists():
        write_json(
            project_template,
            {
                "id": "example-project-id",
                "name": "",
                "type": "project",
                "start_date": "",
                "end_date": "",
                "summary": "",
                "highlights": [],
                "skills_override": [],
                "manual_skills": [],
                "manual_tools": [],
                "manual_highlights": [],
                "manual_notes": [],
                "repo_links": [],
                "experience_links": [],
                "source": {
                    "cv_file": "",
                    "notes": "",
                },
                "updated_at": now_utc(),
            },
        )


def sync_repo_links() -> dict:
    ensure_base_files()
    repo_links = read_json(REPO_LINKS_PATH, {"updated_at": now_utc(), "repos": {}})
    if not REPO_RESULTS_INDEX.exists():
        write_json(REPO_LINKS_PATH, repo_links)
        return repo_links

    index = read_json(REPO_RESULTS_INDEX, {"repos": []})
    repo_map = repo_links.setdefault("repos", {})
    for repo in index.get("repos", []):
        slug = repo["repo_slug"]
        repo_map.setdefault(
            slug,
            {
                "repo_name": repo["repo_name"],
                "repo_path": repo["repo_path"],
                "analysis_dir": f"repo-analysis-results/{slug}",
                "experience_ids": [],
                "project_ids": [],
                "notes": "",
            },
        )
        repo_map[slug]["repo_name"] = repo["repo_name"]
        repo_map[slug]["repo_path"] = repo["repo_path"]

    repo_links["updated_at"] = now_utc()
    write_json(REPO_LINKS_PATH, repo_links)
    return repo_links


def create_experience(args: argparse.Namespace) -> None:
    ensure_base_files()
    exp_id = slugify(args.id or f"{args.company}-{args.title}")
    path = EXPERIENCES_DIR / f"{exp_id}.json"
    payload = {
        "id": exp_id,
        "company": args.company,
        "title": args.title,
        "employment_type": args.employment_type or "",
        "start_date": args.start_date or "",
        "end_date": args.end_date or "",
        "location": args.location or "",
        "summary": args.summary or "",
        "highlights": [],
        "skills_override": [],
        "manual_skills": [],
        "manual_tools": [],
        "manual_highlights": [],
        "manual_notes": [],
        "repo_links": [],
        "project_links": [],
        "source": {
            "cv_file": args.cv_file or "",
            "notes": args.notes or "",
        },
        "updated_at": now_utc(),
    }
    write_json(path, payload)
    print(str(path))


def create_project(args: argparse.Namespace) -> None:
    ensure_base_files()
    project_id = slugify(args.id or args.name)
    path = PROJECTS_DIR / f"{project_id}.json"
    payload = {
        "id": project_id,
        "name": args.name,
        "type": args.project_type or "project",
        "start_date": args.start_date or "",
        "end_date": args.end_date or "",
        "summary": args.summary or "",
        "highlights": [],
        "skills_override": [],
        "manual_skills": [],
        "manual_tools": [],
        "manual_highlights": [],
        "manual_notes": [],
        "repo_links": [],
        "experience_links": [],
        "source": {
            "cv_file": args.cv_file or "",
            "notes": args.notes or "",
        },
        "updated_at": now_utc(),
    }
    write_json(path, payload)
    print(str(path))


def load_entity(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return read_json(path, {})


def save_entity(path: Path, payload: dict) -> None:
    payload["updated_at"] = now_utc()
    write_json(path, payload)


def append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def ensure_manual_fields(payload: dict) -> None:
    payload.setdefault("manual_skills", [])
    payload.setdefault("manual_tools", [])
    payload.setdefault("manual_highlights", [])
    payload.setdefault("manual_notes", [])


def add_manual_evidence(args: argparse.Namespace) -> None:
    ensure_base_files()
    if args.experience:
        entity_id = slugify(args.experience)
        path = EXPERIENCES_DIR / f"{entity_id}.json"
    else:
        entity_id = slugify(args.project)
        path = PROJECTS_DIR / f"{entity_id}.json"

    payload = load_entity(path)
    ensure_manual_fields(payload)

    for skill in args.skill or []:
        append_unique(payload["manual_skills"], skill)
    for tool in args.tool or []:
        append_unique(payload["manual_tools"], tool)
    for highlight in args.highlight or []:
        append_unique(payload["manual_highlights"], highlight)

    if args.note:
        payload["manual_notes"].append(
            {
                "note": args.note,
                "source": "user-provided",
                "added_at": now_utc(),
            }
        )

    save_entity(path, payload)
    print(str(path))


def link_repo(args: argparse.Namespace) -> None:
    repo_links = sync_repo_links()
    repo_slug = slugify(args.repo_slug)
    repo_entry = repo_links["repos"].get(repo_slug)
    if repo_entry is None:
        raise KeyError(f"Unknown repo slug: {repo_slug}")

    if args.experience:
        exp_id = slugify(args.experience)
        exp_path = EXPERIENCES_DIR / f"{exp_id}.json"
        exp = load_entity(exp_path)
        append_unique(repo_entry["experience_ids"], exp_id)
        append_unique(exp.setdefault("repo_links", []), repo_slug)
        save_entity(exp_path, exp)

    if args.project:
        project_id = slugify(args.project)
        project_path = PROJECTS_DIR / f"{project_id}.json"
        project = load_entity(project_path)
        append_unique(repo_entry["project_ids"], project_id)
        append_unique(project.setdefault("repo_links", []), repo_slug)
        save_entity(project_path, project)

    if args.note:
        repo_entry["notes"] = args.note

    repo_links["updated_at"] = now_utc()
    write_json(REPO_LINKS_PATH, repo_links)
    print(str(REPO_LINKS_PATH))


def list_unlinked() -> None:
    repo_links = sync_repo_links()
    unlinked = {
        slug: payload
        for slug, payload in repo_links["repos"].items()
        if not payload.get("experience_ids") and not payload.get("project_ids")
    }
    print(json.dumps(unlinked, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage structured CV data and repo links.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the cv-data structure and templates.")
    subparsers.add_parser("sync-repos", help="Sync repo-analysis-results into cv-data links.")
    subparsers.add_parser("list-unlinked", help="Show analyzed repos with no experience/project link.")

    exp = subparsers.add_parser("create-experience", help="Create an experience entry.")
    exp.add_argument("--id")
    exp.add_argument("--company", required=True)
    exp.add_argument("--title", required=True)
    exp.add_argument("--employment-type")
    exp.add_argument("--start-date")
    exp.add_argument("--end-date")
    exp.add_argument("--location")
    exp.add_argument("--summary")
    exp.add_argument("--cv-file")
    exp.add_argument("--notes")

    project = subparsers.add_parser("create-project", help="Create a project entry.")
    project.add_argument("--id")
    project.add_argument("--name", required=True)
    project.add_argument("--project-type")
    project.add_argument("--start-date")
    project.add_argument("--end-date")
    project.add_argument("--summary")
    project.add_argument("--cv-file")
    project.add_argument("--notes")

    link = subparsers.add_parser("link-repo", help="Link a repo to an experience and/or project.")
    link.add_argument("--repo-slug", required=True)
    link.add_argument("--experience")
    link.add_argument("--project")
    link.add_argument("--note")

    manual = subparsers.add_parser(
        "add-manual-evidence",
        help="Attach manual skills, tools, highlights, or notes to an experience or project.",
    )
    manual.add_argument("--experience")
    manual.add_argument("--project")
    manual.add_argument("--skill", action="append")
    manual.add_argument("--tool", action="append")
    manual.add_argument("--highlight", action="append")
    manual.add_argument("--note")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        ensure_base_files()
        sync_repo_links()
    elif args.command == "sync-repos":
        sync_repo_links()
    elif args.command == "create-experience":
        create_experience(args)
    elif args.command == "create-project":
        create_project(args)
    elif args.command == "link-repo":
        link_repo(args)
    elif args.command == "add-manual-evidence":
        add_manual_evidence(args)
    elif args.command == "list-unlinked":
        list_unlinked()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
