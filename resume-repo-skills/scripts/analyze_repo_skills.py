#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".azcfg",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "venv",
    "env",
    "myenv",
    "site-packages",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    "bin",
    "obj",
    "__pycache__",
}

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sql": "SQL",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".tf": "Terraform",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".dockerfile": "Docker",
}

SPECIAL_FILENAMES = {
    "dockerfile": "Docker",
}

DEPENDENCY_SKILLS = {
    "react": "React",
    "next": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "nuxt": "Nuxt.js",
    "svelte": "Svelte",
    "angular": "Angular",
    "express": "Express",
    "nestjs": "NestJS",
    "fastify": "Fastify",
    "koa": "Koa",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "sqlalchemy": "SQLAlchemy",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "scikit-learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "prisma": "Prisma",
    "typeorm": "TypeORM",
    "mongoose": "Mongoose",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psycopg2": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "jest": "Jest",
    "vitest": "Vitest",
    "pytest": "pytest",
    "playwright": "Playwright",
    "cypress": "Cypress",
    "storybook": "Storybook",
    "webpack": "Webpack",
    "vite": "Vite",
    "eslint": "ESLint",
    "prettier": "Prettier",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "aws-sdk": "AWS",
    "boto3": "AWS",
    "azure-identity": "Azure",
    "azure-storage-blob": "Azure",
    "@azure/identity": "Azure",
    "@azure/storage-blob": "Azure",
    "@prisma/client": "Prisma",
}

FILENAME_SKILLS = {
    ".github/workflows": "GitHub Actions",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "compose.yml": "Docker Compose",
    "compose.yaml": "Docker Compose",
    "terraform.tfvars": "Terraform",
    "main.tf": "Terraform",
    "kustomization.yaml": "Kubernetes",
    "kustomization.yml": "Kubernetes",
    "chart.yaml": "Helm",
}

TEXT_PATTERNS = {
    "REST APIs": [
        re.compile(r"\b(app|router)\.(get|post|put|patch|delete)\b"),
        re.compile(r"@(?:Get|Post|Put|Patch|Delete)\b"),
        re.compile(r"\bAPIRouter\b"),
    ],
    "GraphQL": [
        re.compile(r"\bgraphql(schema|http)?\b", re.IGNORECASE),
        re.compile(r"\bapolloserver\b", re.IGNORECASE),
        re.compile(r"\bgql\s*`", re.IGNORECASE),
    ],
    "Authentication": [
        re.compile(r"\bauth\b", re.IGNORECASE),
        re.compile(r"\bjwt\b", re.IGNORECASE),
        re.compile(r"\boauth\b", re.IGNORECASE),
        re.compile(r"\bpassport\b", re.IGNORECASE),
    ],
    "Testing": [
        re.compile(r"\bdescribe\s*\("),
        re.compile(r"\bit\s*\("),
        re.compile(r"\btest\s*\("),
        re.compile(r"\bassert\b"),
        re.compile(r"\bpytest\b", re.IGNORECASE),
    ],
    "CI/CD": [
        re.compile(r"(?mi)^\s*jobs\s*:"),
        re.compile(r"(?mi)uses:\s+actions/"),
        re.compile(r"(?mi)^\s*stages\s*:"),
    ],
    "Containerization": [
        re.compile(r"(?mi)^\s*FROM\s+\S+"),
        re.compile(r"\bdocker-compose\b", re.IGNORECASE),
    ],
    "Infrastructure as Code": [
        re.compile(r"\bresource\s+\"[^\"]+\"\s+\"[^\"]+\"", re.IGNORECASE),
        re.compile(r"\bterraform\b", re.IGNORECASE),
    ],
    "Database Design": [
        re.compile(r"\bcreate table\b", re.IGNORECASE),
        re.compile(r"\bmodel\s+\w+\s*\{", re.IGNORECASE),
        re.compile(r"\bschema\b", re.IGNORECASE),
    ],
}

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".cs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".sql",
    ".sh",
    ".ps1",
    ".tf",
}

MAX_FILE_BYTES = 256_000
RESULTS_DIRNAME = "repo-analysis-results"


@dataclass
class SkillEvidence:
    hits: int = 0
    files: set[str] = field(default_factory=set)

    def add(self, file_path: Path, count: int = 1) -> None:
        self.hits += count
        self.files.add(str(file_path))


def add_skill(store: dict[str, SkillEvidence], skill: str, file_path: Path, count: int = 1) -> None:
    store.setdefault(skill, SkillEvidence()).add(file_path, count)


def iter_files(repo_path: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [name for name in dirs if name.lower() not in SKIP_DIRS]
        root_path = Path(root)
        for name in files:
            path = root_path / name
            if any(part.lower() in SKIP_DIRS for part in path.parts):
                continue
            yield path


def normalize_dependency_name(name: str) -> str:
    return name.strip().lower()


def parse_package_json(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        values = data.get(key, {})
        if isinstance(values, dict):
            deps.update({str(k): str(v) for k, v in values.items()})
    return deps


def parse_pyproject(path: Path) -> dict[str, str]:
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    deps: dict[str, str] = {}
    project = data.get("project", {})
    for item in project.get("dependencies", []):
        name = re.split(r"[<>=!~\[]", item, maxsplit=1)[0].strip()
        if name:
            deps[name] = item

    optional = project.get("optional-dependencies", {})
    for values in optional.values():
        for item in values:
            name = re.split(r"[<>=!~\[]", item, maxsplit=1)[0].strip()
            if name:
                deps[name] = item

    poetry = data.get("tool", {}).get("poetry", {})
    for name, value in poetry.get("dependencies", {}).items():
        if name != "python":
            deps[str(name)] = str(value)
    return deps


def parse_requirements(path: Path) -> dict[str, str]:
    deps: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return deps
    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        name = re.split(r"[<>=!~\[]", raw, maxsplit=1)[0].strip()
        if name:
            deps[name] = raw
    return deps


def parse_go_mod(path: Path) -> dict[str, str]:
    deps: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return deps
    for line in lines:
        if line.strip().startswith(("require ", "replace ")):
            parts = line.split()
            if len(parts) >= 2:
                deps[parts[1]] = line.strip()
    return deps


def parse_cargo_toml(path: Path) -> dict[str, str]:
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    deps: dict[str, str] = {}
    for key in ("dependencies", "dev-dependencies"):
        values = data.get(key, {})
        if isinstance(values, dict):
            for name, value in values.items():
                deps[str(name)] = str(value)
    return deps


def collect_dependencies(path: Path) -> dict[str, str]:
    name = path.name.lower()
    if name == "package.json":
        return parse_package_json(path)
    if name == "pyproject.toml":
        return parse_pyproject(path)
    if name.startswith("requirements") and path.suffix == ".txt":
        return parse_requirements(path)
    if name == "go.mod":
        return parse_go_mod(path)
    if name == "cargo.toml":
        return parse_cargo_toml(path)
    return {}


def infer_confidence(hits: int, file_count: int) -> str:
    score = hits + min(file_count, 3)
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def slugify_repo_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "repo"


def get_results_root() -> Path:
    return Path.cwd() / RESULTS_DIRNAME


def analyze_repo(repo_path: Path) -> dict:
    if not repo_path.exists() or not repo_path.is_dir():
        raise FileNotFoundError(f"Repository path does not exist or is not a directory: {repo_path}")

    language_counts: Counter[str] = Counter()
    frameworks: dict[str, SkillEvidence] = {}
    capabilities: dict[str, SkillEvidence] = {}
    file_count = 0

    for file_path in iter_files(repo_path):
        file_count += 1
        rel_path = file_path.relative_to(repo_path)
        suffix = file_path.suffix.lower()
        lower_name = file_path.name.lower()
        rel_text = str(rel_path).replace("\\", "/")

        language = LANGUAGE_EXTENSIONS.get(suffix) or SPECIAL_FILENAMES.get(lower_name)
        if language:
            language_counts[language] += 1

        for marker, skill in FILENAME_SKILLS.items():
            if (
                rel_text.endswith(marker)
                or rel_text == marker
                or rel_text.startswith(f"{marker}/")
            ):
                add_skill(frameworks, skill, rel_path)
                if skill in {"GitHub Actions"}:
                    add_skill(capabilities, "CI/CD", rel_path)
                if skill in {"Docker Compose", "Helm", "Kubernetes"}:
                    add_skill(capabilities, "Containerization", rel_path)

        dependencies = collect_dependencies(file_path)
        for dep_name in dependencies:
            skill = DEPENDENCY_SKILLS.get(normalize_dependency_name(dep_name))
            if skill:
                add_skill(frameworks, skill, rel_path)
                if skill in {"Jest", "Vitest", "pytest", "Playwright", "Cypress"}:
                    add_skill(capabilities, "Testing", rel_path)
                if skill in {"Docker", "Kubernetes", "Terraform"}:
                    add_skill(capabilities, "Infrastructure as Code", rel_path)

        if suffix not in TEXT_EXTENSIONS and lower_name not in SPECIAL_FILENAMES:
            continue
        if file_path.stat().st_size > MAX_FILE_BYTES:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="utf-8-sig")
            except Exception:
                continue
        except Exception:
            continue

        lowered = content.lower()
        if "tailwind.config" in lowered:
            add_skill(frameworks, "Tailwind CSS", rel_path)
        if "github actions" in lowered:
            add_skill(frameworks, "GitHub Actions", rel_path)

        for capability, patterns in TEXT_PATTERNS.items():
            matches = sum(len(pattern.findall(content)) for pattern in patterns)
            if matches:
                add_skill(capabilities, capability, rel_path, matches)

    languages = [
        {"skill": name, "file_count": count}
        for name, count in language_counts.most_common()
    ]

    framework_items = []
    for skill, evidence in sorted(frameworks.items()):
        framework_items.append(
            {
                "skill": skill,
                "confidence": infer_confidence(evidence.hits, len(evidence.files)),
                "evidence_count": evidence.hits,
                "files": sorted(evidence.files)[:5],
            }
        )

    capability_items = []
    for skill, evidence in sorted(capabilities.items()):
        capability_items.append(
            {
                "skill": skill,
                "confidence": infer_confidence(evidence.hits, len(evidence.files)),
                "evidence_count": evidence.hits,
                "files": sorted(evidence.files)[:5],
            }
        )

    return {
        "repo": str(repo_path),
        "repo_name": repo_path.name,
        "summary": {
            "files_scanned": file_count,
            "languages_detected": len(languages),
            "frameworks_detected": len(framework_items),
            "capabilities_detected": len(capability_items),
        },
        "languages": languages,
        "frameworks_tools": framework_items,
        "engineering_capabilities": capability_items,
    }


def merge_reports(reports: list[dict]) -> dict:
    merged_languages: Counter[str] = Counter()
    merged_skills: dict[str, SkillEvidence] = defaultdict(SkillEvidence)
    merged_capabilities: dict[str, SkillEvidence] = defaultdict(SkillEvidence)
    total_files = 0

    for report in reports:
        total_files += report["summary"]["files_scanned"]
        for item in report["languages"]:
            merged_languages[item["skill"]] += item["file_count"]

        for category, store in (
            ("frameworks_tools", merged_skills),
            ("engineering_capabilities", merged_capabilities),
        ):
            for item in report[category]:
                evidence = store[item["skill"]]
                evidence.hits += item["evidence_count"]
                evidence.files.update(item["files"])

    def serialize(store: dict[str, SkillEvidence]) -> list[dict]:
        items = []
        for skill, evidence in sorted(store.items()):
            items.append(
                {
                    "skill": skill,
                    "confidence": infer_confidence(evidence.hits, len(evidence.files)),
                    "evidence_count": evidence.hits,
                    "files": sorted(evidence.files)[:8],
                }
            )
        return items

    return {
        "repo_count": len(reports),
        "summary": {
            "files_scanned": total_files,
            "languages_detected": len(merged_languages),
            "frameworks_detected": len(merged_skills),
            "capabilities_detected": len(merged_capabilities),
        },
        "languages": [
            {"skill": name, "file_count": count}
            for name, count in merged_languages.most_common()
        ],
        "frameworks_tools": serialize(merged_skills),
        "engineering_capabilities": serialize(merged_capabilities),
        "repos": reports,
    }


def render_markdown(report: dict) -> str:
    lines: list[str] = []
    if "repo_count" in report:
        lines.append(f"# Combined Skill Report ({report['repo_count']} repos)")
    else:
        lines.append(f"# Skill Report: {Path(report['repo']).name}")

    summary = report["summary"]
    lines.append("")
    lines.append(
        f"Scanned {summary['files_scanned']} files. "
        f"Detected {summary['languages_detected']} languages, "
        f"{summary['frameworks_detected']} frameworks/tools, and "
        f"{summary['capabilities_detected']} broader engineering capabilities."
    )

    def section(title: str, items: list[dict], count_key: str) -> None:
        lines.append("")
        lines.append(f"## {title}")
        if not items:
            lines.append("")
            lines.append("No strong signals detected.")
            return
        for item in items:
            files = ", ".join(item.get("files", []))
            lines.append("")
            lines.append(
                f"- **{item['skill']}** ({item.get('confidence', 'n/a')} confidence, "
                f"{item[count_key]} evidence)"
            )
            if files:
                lines.append(f"  Evidence: `{files}`")

    section("Languages", report["languages"], "file_count")
    section("Frameworks And Tools", report["frameworks_tools"], "evidence_count")
    section("Engineering Capabilities", report["engineering_capabilities"], "evidence_count")
    return "\n".join(lines)


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def persist_repo_report(report: dict, results_root: Path) -> dict:
    repo_name = report.get("repo_name") or Path(report["repo"]).name
    repo_slug = slugify_repo_name(repo_name)
    repo_dir = results_root / repo_slug
    repo_dir.mkdir(parents=True, exist_ok=True)

    analyzed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metadata = {
        "repo_name": repo_name,
        "repo_slug": repo_slug,
        "repo_path": report["repo"],
        "analyzed_at": analyzed_at,
        "summary": report["summary"],
        "files": {
            "analysis_json": "analysis.json",
            "analysis_markdown": "analysis.md",
            "meta_json": "meta.json",
        },
    }

    write_json(repo_dir / "analysis.json", report)
    (repo_dir / "analysis.md").write_text(render_markdown(report), encoding="utf-8")
    write_json(repo_dir / "meta.json", metadata)
    return metadata


def update_index(results_root: Path, entries: list[dict]) -> None:
    index_path = results_root / "index.json"
    if index_path.exists():
        try:
            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            index_payload = {"repos": []}
    else:
        index_payload = {"repos": []}

    existing = {
        item.get("repo_slug"): item
        for item in index_payload.get("repos", [])
        if isinstance(item, dict) and item.get("repo_slug")
    }

    for entry in entries:
        existing[entry["repo_slug"]] = entry

    index_payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "results_root": str(results_root),
        "repos": sorted(existing.values(), key=lambda item: item["repo_slug"]),
    }
    write_json(index_path, index_payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze one or more repositories and infer resume-relevant skills."
    )
    parser.add_argument("repo_paths", nargs="+", help="One or more local repository paths.")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = [analyze_repo(Path(path).resolve()) for path in args.repo_paths]
    results_root = get_results_root()
    results_root.mkdir(parents=True, exist_ok=True)
    entries = [persist_repo_report(report, results_root) for report in reports]
    update_index(results_root, entries)
    payload = reports[0] if len(reports) == 1 else merge_reports(reports)
    if args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
