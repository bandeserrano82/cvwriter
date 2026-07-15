#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
JOB_TARGETS_DIR = ROOT / "job-targets"
ALLOWED_TEXT_EXTENSIONS = {".txt", ".md", ".json", ".html", ".htm"}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Value cannot be normalized into a non-empty slug.")
    return slug


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_job_dirs(job_slug: str) -> tuple[Path, Path, Path]:
    job_dir = JOB_TARGETS_DIR / job_slug
    source_dir = job_dir / "source"
    parsed_dir = job_dir / "parsed"
    output_dir = job_dir / "output"
    for path in (JOB_TARGETS_DIR, job_dir, source_dir, parsed_dir, output_dir):
        path.mkdir(parents=True, exist_ok=True)
    return source_dir, parsed_dir, output_dir


def contains_term(text: str, term: str) -> bool:
    pattern = re.compile(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", re.IGNORECASE)
    return bool(pattern.search(text))


def keyword_extract(text: str) -> list[str]:
    candidates = [
        "angular", "java", "spring", "spring boot", "springboot",
        "asp.net core", ".net core", "c#", ".net", "react", "next.js",
        "typescript", "javascript", "html", "css", "html/css", "python", "node.js",
        "express", "django", "flask", "fastapi", "ruby", "ruby on rails", "rails",
        "spring mvc", "asp.net mvc", "laravel", "azure", "aws", "gcp", "google cloud platform",
        "postgresql", "sql", "mysql", "redis", "elasticsearch", "playwright", "docker", "kubernetes",
        "linux", "kafka", "ci/cd", "unit testing", "integration testing", "end-to-end testing",
        "openai", "llm", "ai", "graphql", "rest", "restful", "api", "apis",
        "microservices", "microservice", "soa", "event-driven", "oop", "design patterns",
        "relational databases", "dataverse", "auth0", "entra id", "powerapps",
        "power automate", "nuxt.js", "vue.js", "php", "codex", "cursor", "claude code",
        "snowflake", "salesforce", "slack", "zoom", "gmail", "rag",
        "retrieval augmented generation", "distributed systems", "distributed system",
        "architecture", "technical leadership", "mentoring", "operations", "testing",
        "foundation models", "data pipelines", "operational excellence",
    ]
    lowered = text.lower()
    found = {item for item in candidates if contains_term(lowered, item)}

    if contains_term(lowered, "js/ts") or contains_term(lowered, "modern js/ts"):
        found.update({"javascript", "typescript"})
    if contains_term(lowered, "agentic"):
        found.add("ai")
    if contains_term(lowered, "agents"):
        found.add("ai")

    return sorted(found)


def collect_lines(text: str, heading_terms: list[str]) -> list[str]:
    lines = [line.strip(" -\t") for line in text.splitlines()]
    results: list[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if capture and results:
                capture = False
            continue
        if any(term in stripped.lower() for term in heading_terms):
            capture = True
            continue
        if capture:
            results.append(stripped)
    return results


def parse_job_text(text: str, title: str, company: str, source_type: str, source_path: str = "", source_url: str = "") -> dict:
    requirements = collect_lines(text, ["requirement", "qualification", "what you bring"])
    responsibilities = collect_lines(text, ["responsibilit", "what you'll do", "what you will do"])
    preferred = collect_lines(text, ["preferred", "nice to have", "bonus"])
    payload = {
        "id": slugify(f"{company}-{title}" if company else title),
        "title": title,
        "company": company,
        "location": "",
        "source_type": source_type,
        "source_path": source_path,
        "source_url": source_url,
        "summary": text[:800].strip(),
        "requirements": requirements,
        "preferred_qualifications": preferred,
        "responsibilities": responsibilities,
        "keywords": keyword_extract(text),
        "tech_stack": keyword_extract(text),
        "seniority": "",
        "work_mode": "",
        "updated_at": now_utc(),
    }
    return payload


def save_job_target(job: dict, raw_text: str, source_filename: str | None = None, attachment_paths: list[Path] | None = None) -> Path:
    job_slug = job["id"]
    source_dir, parsed_dir, output_dir = ensure_job_dirs(job_slug)
    if source_filename:
        (source_dir / source_filename).write_text(raw_text, encoding="utf-8")
    else:
        (source_dir / "job-description.txt").write_text(raw_text, encoding="utf-8")

    if attachment_paths:
        attachments_dir = source_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        for attachment in attachment_paths:
            target = attachments_dir / attachment.name
            if attachment.is_file():
                shutil.copy2(attachment, target)

    write_json(parsed_dir / "job.json", job)
    write_json(
        parsed_dir / "skill-targets.json",
        {
            "must_have": job["keywords"],
            "nice_to_have": [],
            "matched_experiences": [],
            "matched_projects": [],
            "matched_repos": [],
            "gaps": [],
            "updated_at": now_utc(),
        },
    )
    write_json(
        JOB_TARGETS_DIR / job_slug / "meta.json",
        {
            "id": job_slug,
            "title": job["title"],
            "company": job["company"],
            "source_type": job["source_type"],
            "paths": {
                "source": str(source_dir),
                "parsed": str(parsed_dir),
                "output": str(output_dir),
            },
            "updated_at": now_utc(),
        },
    )
    return JOB_TARGETS_DIR / job_slug


def import_text(args: argparse.Namespace) -> None:
    text = Path(args.text_file).read_text(encoding="utf-8") if args.text_file else args.text
    job = parse_job_text(text, args.title, args.company or "", "text")
    print(save_job_target(job, text))


def import_file(args: argparse.Namespace) -> None:
    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    title = args.title or path.stem
    job = parse_job_text(text, title, args.company or "", "file", source_path=str(path))
    print(save_job_target(job, text, source_filename=path.name, attachment_paths=[path]))


def import_folder(args: argparse.Namespace) -> None:
    folder = Path(args.path)
    files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED_TEXT_EXTENSIONS]
    files = files[:20]
    text_parts = []
    for file in files:
        try:
            text_parts.append(f"# FILE: {file.name}\n{file.read_text(encoding='utf-8')}")
        except Exception:
            continue
    combined = "\n\n".join(text_parts)
    title = args.title or folder.name
    job = parse_job_text(combined, title, args.company or "", "folder", source_path=str(folder))
    print(save_job_target(job, combined, attachment_paths=files))


def import_link(args: argparse.Namespace) -> None:
    title = args.title or args.url
    raw_text = args.text or ""
    job = parse_job_text(raw_text, title, args.company or "", "link", source_url=args.url)
    job_dir = save_job_target(job, raw_text or args.url, source_filename="job-description.txt")
    (job_dir / "source" / "posting-url.txt").write_text(args.url, encoding="utf-8")
    print(job_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Store and parse job descriptions for targeted CV generation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    text = subparsers.add_parser("import-text")
    text.add_argument("--title", required=True)
    text.add_argument("--company")
    text.add_argument("--text")
    text.add_argument("--text-file")

    file_parser = subparsers.add_parser("import-file")
    file_parser.add_argument("--path", required=True)
    file_parser.add_argument("--title")
    file_parser.add_argument("--company")

    folder = subparsers.add_parser("import-folder")
    folder.add_argument("--path", required=True)
    folder.add_argument("--title")
    folder.add_argument("--company")

    link = subparsers.add_parser("import-link")
    link.add_argument("--url", required=True)
    link.add_argument("--title")
    link.add_argument("--company")
    link.add_argument("--text")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "import-text":
        import_text(args)
    elif args.command == "import-file":
        import_file(args)
    elif args.command == "import-folder":
        import_folder(args)
    elif args.command == "import-link":
        import_link(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
