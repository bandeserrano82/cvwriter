#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from refine_cv import refine_cv_markdown


ROOT = Path.cwd()
CV_DATA_DIR = ROOT / "cv-data"
JOB_TARGETS_DIR = ROOT / "job-targets"
GENERATED_CVS_DIR = ROOT / "generated-cvs"
REPO_ANALYSIS_DIR = ROOT / "repo-analysis-results"
IMPACT_TERMS = (
    "architected", "implemented", "built", "delivered", "developed", "designed",
    "created", "improved", "optimized", "migrated", "deployed", "integrated",
    "automated", "reduced", "scaled", "led", "authored", "provisioned",
)
TECH_TERMS = (
    "react", "next.js", "typescript", "javascript", "node", "python", "php",
    "vue", "nuxt", "azure", "sql", "postgres", "docker", "api", "github",
    "jira", "entra", "power", "dataverse", "teams", "auth", "ci/cd", "pipeline",
)
FRONTEND_SKILLS = {
    "React", "React.js", "Next.js", "Vue", "Vue.js", "Nuxt.js", "TypeScript",
    "JavaScript", "HTML", "CSS", "SCSS", "Tailwind CSS", "TanStack",
    "TanStack Table", "Bootstrap",
}
LEADERSHIP_SKILLS = {
    "System Architecture", "Azure", "Azure DevOps", "Azure Functions", "CI/CD",
    ".NET", "ASP.NET", "Node.js", "REST APIs", "SQL", "PostgreSQL",
    "DevOps", "Code Review", "Team Leadership", "Project Management",
    "Testing", "Docker", "Containerization",
}
BACKEND_PLATFORM_SKILLS = {
    "Python", "Django", "FastAPI", "Node.js", ".NET", "ASP.NET", "C#",
    "REST APIs", "SQL", "SQL Server", "PostgreSQL", "Redis", "CI/CD",
    "Docker", "Containerization", "Azure", "Azure DevOps", "Azure Functions",
    "System Architecture", "Testing",
}
CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}
LANGUAGE_BULLET_EXCLUDE = {"JSON", "YAML", "HTML", "CSS", "SCSS", "Sass", "Less", "Shell", "PowerShell"}
SUMMARY_SKILL_EXCLUDE = {"JSON", "YAML", "HTML", "CSS", "SCSS", "Sass", "Less", "Shell", "PowerShell", "Bootstrap", "ESLint", "Prettier", "Jest"}
SELECTED_SKILL_EXCLUDE = {"JSON", "YAML", "Shell", "Less", "SCSS", "Sass", "Prettier", "ESLint", "Jest", "Webpack"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_profile() -> dict:
    return read_json(CV_DATA_DIR / "profile.json", {})


def load_items(folder: Path) -> list[dict]:
    items = []
    for path in sorted(folder.glob("*.json")):
        if path.name.startswith("_"):
            continue
        items.append(read_json(path, {}))
    return items


def load_repo_analysis(slug: str) -> dict:
    return read_json(REPO_ANALYSIS_DIR / slug / "analysis.json", {})


def extract_repo_skills(repo_slugs: list[str]) -> list[str]:
    skills: set[str] = set()
    for slug in repo_slugs:
        analysis = load_repo_analysis(slug)
        for item in analysis.get("languages", []):
            # Ignore incidental single-file language detections that are not strong enough
            # to claim as resume-level experience.
            if item.get("file_count", 0) >= 3:
                skills.add(item["skill"])
        for category in ("frameworks_tools", "engineering_capabilities"):
            for item in analysis.get(category, []):
                skills.add(item["skill"])
    return sorted(skills)


def extract_manual_skills(items: list[dict]) -> list[str]:
    skills: set[str] = set()
    for item in items:
        for skill in item.get("manual_skills", []):
            skills.add(skill)
        for tool in item.get("manual_tools", []):
            skills.add(tool)
        for skill in item.get("skills_override", []):
            skills.add(skill)
    return sorted(skills)


def build_master_data() -> dict:
    return {
        "profile": load_profile(),
        "experiences": load_items(CV_DATA_DIR / "experiences"),
        "projects": load_items(CV_DATA_DIR / "projects"),
    }


def score_text_against_keywords(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def score_frontend_text(text: str) -> int:
    lowered = text.lower()
    frontend_terms = (
        "frontend", "react", "next.js", "vue", "vue.js", "nuxt", "nuxt.js",
        "typescript", "javascript", "ui", "client-facing",
    )
    return sum(1 for term in frontend_terms if term in lowered)


def score_skill_against_keywords(skill: str, keywords: list[str]) -> int:
    skill_lower = skill.lower()
    score = 0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if skill_lower == keyword_lower:
            score += 4
        elif keyword_lower in skill_lower or skill_lower in keyword_lower:
            score += 1
    return score


def has_frontend_emphasis(job_or_text: dict | str | None) -> bool:
    if not job_or_text:
        return False
    if isinstance(job_or_text, dict):
        text = " ".join(
            [
                job_or_text.get("title", ""),
                job_or_text.get("summary", ""),
                *job_or_text.get("responsibilities", []),
                *job_or_text.get("requirements", []),
            ]
        ).lower()
    else:
        text = str(job_or_text).lower()
    return any(term in text for term in ("frontend", "front-end", "typescript", "client-facing", "usability", "ui"))


def has_dashboard_ui_emphasis(job_or_text: dict | str | None) -> bool:
    if not job_or_text:
        return False
    if isinstance(job_or_text, dict):
        text = " ".join(
            [
                job_or_text.get("title", ""),
                job_or_text.get("summary", ""),
                *job_or_text.get("responsibilities", []),
                *job_or_text.get("requirements", []),
                *job_or_text.get("preferred_qualifications", []),
            ]
        ).lower()
    else:
        text = str(job_or_text).lower()
    dashboard_terms = (
        "dashboard", "dashboards", "reporting", "reporting views", "data visualization",
        "data visualizations", "interactive user interfaces", "interactive ui",
        "business users", "analytics", "filters",
    )
    return any(term in text for term in dashboard_terms)


def has_leadership_emphasis(job_or_text: dict | str | None) -> bool:
    if not job_or_text:
        return False
    if isinstance(job_or_text, dict):
        text = " ".join(
            [
                job_or_text.get("title", ""),
                job_or_text.get("summary", ""),
                *job_or_text.get("responsibilities", []),
                *job_or_text.get("requirements", []),
            ]
        ).lower()
    else:
        text = str(job_or_text).lower()
    leadership_terms = (
        "technical lead", "delivery lead", "technical leadership", "architecture",
        "architectural", "stakeholder", "mentor", "mentoring", "team leadership",
        "delivery lifecycle", "solution delivery", "cross-team", "qa", "devops",
    )
    return any(term in text for term in leadership_terms)


def has_backend_platform_emphasis(job_or_text: dict | str | None) -> bool:
    if not job_or_text:
        return False
    if isinstance(job_or_text, dict):
        text = " ".join(
            [
                job_or_text.get("title", ""),
                job_or_text.get("summary", ""),
                *job_or_text.get("responsibilities", []),
                *job_or_text.get("requirements", []),
            ]
        ).lower()
    else:
        text = str(job_or_text).lower()
    backend_terms = (
        "backend", "server-side", "node.js", ".net", "c#", "sql", "mssql",
        "restful api", "rest api", "testing", "terraform", "aws", "infrastructure",
    )
    return any(term in text for term in backend_terms)


def prioritize_skills_for_job(
    skills: list[str],
    keywords: list[str],
    frontend_emphasis: bool = False,
    dashboard_emphasis: bool = False,
    leadership_emphasis: bool = False,
    backend_platform_emphasis: bool = False,
) -> list[str]:
    def sort_key(skill: str):
        frontend_focus = (frontend_emphasis or dashboard_emphasis) and not leadership_emphasis
        frontend_boost = 3 if frontend_focus and skill in FRONTEND_SKILLS else 0
        leadership_boost = 3 if leadership_emphasis and skill in LEADERSHIP_SKILLS else 0
        backend_boost = 3 if backend_platform_emphasis and skill in BACKEND_PLATFORM_SKILLS else 0
        return (-(score_skill_against_keywords(skill, keywords) + frontend_boost + leadership_boost + backend_boost), skill.lower())

    return sorted(skills, key=sort_key)


def years_of_experience(experiences: list[dict]) -> str:
    years: list[int] = []
    for exp in experiences:
        start = exp.get("start_date", "")
        match = re.match(r"(\d{4})", start)
        if match:
            years.append(int(match.group(1)))
    if not years:
        return ""
    total = max(datetime.now().year - min(years), 1)
    return f"{total}+ years"


def sort_items_chronologically(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda item: item.get("start_date", ""), reverse=True)


def top_summary_skills(selected: dict, keywords: list[str], limit: int) -> list[str]:
    skills = [skill for skill in selected.get("skills", []) if skill not in SUMMARY_SKILL_EXCLUDE]
    frontend_emphasis = selected.get("frontend_emphasis", False)
    dashboard_emphasis = selected.get("dashboard_emphasis", False)
    leadership_emphasis = selected.get("leadership_emphasis", False)
    backend_platform_emphasis = selected.get("backend_platform_emphasis", False)
    if keywords:
        ranked = prioritize_skills_for_job(skills, keywords, frontend_emphasis, dashboard_emphasis, leadership_emphasis, backend_platform_emphasis)
    else:
        ranked = skills
    return ranked[:limit]


def curated_selected_skills(selected: dict) -> list[str]:
    skills = [skill for skill in selected.get("skills", []) if skill not in SELECTED_SKILL_EXCLUDE]
    frontend_emphasis = selected.get("frontend_emphasis", False)
    dashboard_emphasis = selected.get("dashboard_emphasis", False)
    leadership_emphasis = selected.get("leadership_emphasis", False)
    backend_platform_emphasis = selected.get("backend_platform_emphasis", False)
    keywords = {keyword.lower() for keyword in selected.get("keywords", [])}

    if leadership_emphasis:
        preferred = [
            "System Architecture", "Azure", "CI/CD", ".NET", "Node.js",
            "REST APIs", "SQL", "PostgreSQL", "DevOps", "Code Review",
            "Project Management", "Team Leadership", "Azure DevOps",
            "Azure Functions", "Docker", "Containerization",
        ]
        if {"python", "django", "postgresql", "redis", "rest", "api", "apis"} & keywords:
            preferred = [
                "Python", "Django", "FastAPI", "PostgreSQL", "Redis",
                "REST APIs", "React", "Next.js", "TypeScript", "CI/CD",
                "Docker", "System Architecture", "Node.js", "Azure",
                "Project Management", "Team Leadership",
            ]
        chosen = [skill for skill in preferred if skill in skills]
        return chosen[:16]

    if dashboard_emphasis:
        preferred = [
            "React", "Next.js", "TypeScript", "JavaScript", "HTML", "CSS",
            "TanStack", "TanStack Table", "REST APIs", "Node.js", "Azure",
            "SQL", "PostgreSQL", "Auth0", "CI/CD", "Vue.js",
        ]
        chosen = [skill for skill in preferred if skill in skills]
        return chosen[:16]

    if backend_platform_emphasis:
        preferred = [
            ".NET", "C#", "Node.js", "SQL", "SQL Server", "REST APIs",
            "React", "TypeScript", "CI/CD", "Docker", "Testing",
            "Azure", "System Architecture", "ASP.NET", "PostgreSQL", "Code Review",
        ]
        chosen = [skill for skill in preferred if skill in skills]
        return chosen[:16]

    if frontend_emphasis:
        preferred = [
            "TypeScript", "React", "Next.js", "Vue.js", "Nuxt.js",
            "JavaScript", "HTML", "CSS", "Tailwind CSS", "TanStack",
            "TanStack Table", "REST APIs", "Auth0", "Azure",
            "CI/CD", "Node.js",
        ]
        chosen = [skill for skill in preferred if skill in skills]
        return chosen[:16]

    return skills[:20]


def synthesize_summary(profile: dict, selected: dict, target_job: dict | None = None) -> str:
    experiences = selected.get("experiences", [])
    keywords = selected.get("keywords", [])
    years = years_of_experience(experiences)

    if target_job:
        skills = top_summary_skills(selected, keywords, 6)
        role = target_job.get("title", "software engineering role")
        if skills:
            return (
                f"Full-stack Software Engineer with {years} of experience delivering production systems across "
                f"{format_skill_list(skills)}. Brings hands-on experience building APIs, data-driven applications, "
                f"and modern delivery workflows with emphasis on the technologies most relevant to this {role.lower()}."
            )
        return (
            f"Full-stack Software Engineer with {years} of experience delivering production systems, APIs, and "
            f"business-critical applications in collaborative engineering environments."
        )

    skills = top_summary_skills(selected, [], 6)
    headline = profile.get("headline", "Full-stack Software Engineer")
    if skills:
        return (
            f"{headline} with {years} of experience designing and delivering production systems across "
            f"{format_skill_list(skills)}, spanning frontend, backend, cloud, data, and automation work."
        )
    return profile.get("summary", "")


def format_skill_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = " ".join(item.lower().split())
        if not item or normalized in seen:
            continue
        seen.add(normalized)
        result.append(item)
    return result


def score_bullet(text: str, keywords: list[str], source: str, index: int) -> tuple[int, int, int]:
    lowered = text.lower()
    keyword_score = sum(3 for keyword in keywords if keyword.lower() in lowered)
    impact_score = sum(1 for term in IMPACT_TERMS if term in lowered)
    tech_score = sum(1 for term in TECH_TERMS if term in lowered)
    metric_score = 2 if re.search(r"\b\d+[%+]?\b|\bdozens\b|\btens\b|\bthousands\b", lowered) else 0
    manual_bonus = 1 if source == "manual" else 0
    # Earlier bullets remain slightly preferred when scores tie.
    order_score = -index
    return (keyword_score + impact_score + tech_score + metric_score + manual_bonus, order_score, 0)


def select_bullets(item: dict, limit: int, keywords: list[str] | None = None) -> list[str]:
    keywords = keywords or []
    candidates: list[tuple[str, int, str]] = []
    for index, bullet in enumerate(dedupe_preserve_order(item.get("manual_highlights", []))):
        candidates.append(("manual", index, bullet))

    ranked = sorted(
        candidates,
        key=lambda candidate: score_bullet(candidate[2], keywords, candidate[0], candidate[1]),
        reverse=True,
    )

    selected: list[str] = []
    for _, _, bullet in ranked:
        if bullet not in selected:
            selected.append(bullet)
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        for bullet in synthesize_repo_bullets(item, keywords):
            if bullet not in selected:
                selected.append(bullet)
            if len(selected) >= limit:
                break
    return selected


def collect_repo_signals(repo_slugs: list[str], category: str) -> list[dict]:
    signals: dict[str, dict] = {}
    for slug in repo_slugs:
        analysis = load_repo_analysis(slug)
        for item in analysis.get(category, []):
            skill = item.get("skill")
            if not skill:
                continue
            current = signals.get(skill)
            if current is None:
                signals[skill] = dict(item)
                continue
            current["file_count"] = current.get("file_count", 0) + item.get("file_count", 0)
            current["evidence_count"] = current.get("evidence_count", 0) + item.get("evidence_count", 0)
            if CONFIDENCE_RANK.get(item.get("confidence", "low"), 0) > CONFIDENCE_RANK.get(current.get("confidence", "low"), 0):
                current["confidence"] = item.get("confidence", "low")
    return list(signals.values())


def top_repo_languages(repo_slugs: list[str]) -> list[str]:
    items = [
        item for item in collect_repo_signals(repo_slugs, "languages")
        if item.get("skill") not in LANGUAGE_BULLET_EXCLUDE
    ]
    items.sort(key=lambda item: (-item.get("file_count", 0), item.get("skill", "")))
    return [item["skill"] for item in items[:3]]


def top_repo_frameworks(repo_slugs: list[str], keywords: list[str]) -> list[str]:
    items = [
        item for item in collect_repo_signals(repo_slugs, "frameworks_tools")
        if CONFIDENCE_RANK.get(item.get("confidence", "low"), 0) >= 2
    ]
    items.sort(
        key=lambda item: (
            -score_skill_against_keywords(item.get("skill", ""), keywords),
            -CONFIDENCE_RANK.get(item.get("confidence", "low"), 0),
            -item.get("evidence_count", 0),
            item.get("skill", ""),
        )
    )
    return [item["skill"] for item in items[:4]]


def top_repo_capabilities(repo_slugs: list[str], keywords: list[str]) -> list[str]:
    items = [
        item for item in collect_repo_signals(repo_slugs, "engineering_capabilities")
        if CONFIDENCE_RANK.get(item.get("confidence", "low"), 0) >= 2
    ]
    items.sort(
        key=lambda item: (
            -score_skill_against_keywords(item.get("skill", ""), keywords),
            -CONFIDENCE_RANK.get(item.get("confidence", "low"), 0),
            -item.get("evidence_count", 0),
            item.get("skill", ""),
        )
    )
    return [item["skill"] for item in items[:3]]


def synthesize_repo_bullets(item: dict, keywords: list[str]) -> list[str]:
    repo_slugs = item.get("repo_links", [])
    if not repo_slugs:
        return []

    bullets: list[str] = []
    frameworks = top_repo_frameworks(repo_slugs, keywords)
    languages = top_repo_languages(repo_slugs)
    capabilities = top_repo_capabilities(repo_slugs, keywords)

    if frameworks and languages:
        bullets.append(
            f"Worked across {format_skill_list(languages)} codebases using {format_skill_list(frameworks[:4])}."
        )
    elif frameworks:
        bullets.append(f"Worked with {format_skill_list(frameworks[:4])} across linked production codebases.")
    elif languages:
        bullets.append(f"Worked across {format_skill_list(languages)} codebases in linked production repositories.")

    if capabilities:
        bullets.append(
            f"Implemented {format_skill_list(capabilities)} patterns in linked production systems."
        )

    if "REST APIs" in capabilities and any(skill in frameworks for skill in ("Vue.js", "Nuxt.js", "React", "Next.js")):
        bullets.append("Built frontend and API-connected application flows backed by linked production repositories.")
    elif "Testing" in capabilities:
        bullets.append("Contributed to tested production systems with automated quality checks in linked repositories.")

    return dedupe_preserve_order(bullets)


def experience_search_text(exp: dict) -> str:
    parts = [
        exp.get("company", ""),
        exp.get("title", ""),
        exp.get("summary", ""),
        *exp.get("manual_highlights", []),
        *exp.get("manual_skills", []),
        *exp.get("manual_tools", []),
        *exp.get("skills_override", []),
    ]
    return " ".join(parts)


def project_search_text(project: dict) -> str:
    parts = [
        project.get("name", ""),
        project.get("summary", ""),
        *project.get("manual_highlights", []),
        *project.get("manual_skills", []),
        *project.get("manual_tools", []),
        *project.get("skills_override", []),
    ]
    return " ".join(parts)


def select_for_job(master: dict, job: dict) -> dict:
    keywords = job.get("keywords", [])
    frontend_emphasis = has_frontend_emphasis(job)
    dashboard_emphasis = has_dashboard_ui_emphasis(job)
    leadership_emphasis = has_leadership_emphasis(job)
    backend_platform_emphasis = has_backend_platform_emphasis(job)

    selected_experiences = []
    for exp in master["experiences"]:
        haystack = experience_search_text(exp)
        score = score_text_against_keywords(haystack, keywords)
        if (frontend_emphasis or dashboard_emphasis) and not leadership_emphasis:
            score += score_frontend_text(haystack) * 2
        if leadership_emphasis:
            score += score_text_against_keywords(haystack, ["architecture", "lead", "mentor", "ci/cd", "code review", "devops", "team"])
        if backend_platform_emphasis:
            score += score_text_against_keywords(haystack, ["node.js", ".net", "c#", "sql", "rest", "api", "testing", "ci/cd", "docker", "backend"])
        if score > 0 or exp.get("repo_links"):
            selected_experiences.append((score, exp))
    selected_experiences.sort(key=lambda item: item[0], reverse=True)

    selected_projects = []
    for project in master["projects"]:
        haystack = project_search_text(project)
        score = score_text_against_keywords(haystack, keywords)
        if (frontend_emphasis or dashboard_emphasis) and not leadership_emphasis:
            score += score_frontend_text(haystack) * 2
        if leadership_emphasis:
            score += score_text_against_keywords(haystack, ["architecture", "lead", "mentor", "ci/cd", "code review", "devops", "team"])
        if backend_platform_emphasis:
            score += score_text_against_keywords(haystack, ["node.js", ".net", "c#", "sql", "rest", "api", "testing", "ci/cd", "docker", "backend"])
        if score > 0 or project.get("repo_links"):
            selected_projects.append((score, project))
    selected_projects.sort(key=lambda item: item[0], reverse=True)

    experiences = sort_items_chronologically([item[1] for item in selected_experiences[:5]])
    projects = [item[1] for item in selected_projects[:3]]
    repo_slugs = []
    for exp in experiences:
        repo_slugs.extend(exp.get("repo_links", []))
    for project in projects:
        repo_slugs.extend(project.get("repo_links", []))
    repo_slugs = sorted(set(repo_slugs))
    all_skills = sorted(set(extract_repo_skills(repo_slugs) + extract_manual_skills(experiences + projects)))

    return {
        "experiences": experiences,
        "projects": projects,
        "repo_slugs": repo_slugs,
        "skills": prioritize_skills_for_job(all_skills, keywords, frontend_emphasis, dashboard_emphasis, leadership_emphasis, backend_platform_emphasis),
        "keywords": keywords,
        "frontend_emphasis": frontend_emphasis,
        "dashboard_emphasis": dashboard_emphasis,
        "leadership_emphasis": leadership_emphasis,
        "backend_platform_emphasis": backend_platform_emphasis,
    }


def select_general(master: dict) -> dict:
    experiences = sorted(
        master["experiences"], key=lambda exp: exp.get("start_date", ""), reverse=True
    )
    projects = master["projects"]
    repo_slugs = []
    for exp in experiences:
        repo_slugs.extend(exp.get("repo_links", []))
    for project in projects:
        repo_slugs.extend(project.get("repo_links", []))
    repo_slugs = sorted(set(repo_slugs))

    return {
        "experiences": experiences,
        "projects": projects,
        "repo_slugs": repo_slugs,
        "skills": sorted(set(extract_repo_skills(repo_slugs) + extract_manual_skills(experiences + projects))),
        "keywords": [],
    }


def render_cv(profile: dict, selected: dict, target_job: dict | None = None) -> str:
    lines = []
    lines.append(f"# {profile.get('name', '')}")
    lines.append("")

    headline = profile.get("headline", "")
    if headline:
        lines.append(headline)

    contact = " | ".join(
        filter(
            None,
            [
                profile.get("location", ""),
                profile.get("email", ""),
                profile.get("phone", ""),
                profile.get("links", {}).get("linkedin", ""),
            ],
        )
    )
    if contact:
        lines.append(contact)

    lines.append("")
    lines.append("## Professional Summary")
    lines.append("")
    lines.append(synthesize_summary(profile, selected, target_job))

    if selected["skills"]:
        lines.append("")
        lines.append("## Selected Skills")
        lines.append("")
        lines.append(", ".join(curated_selected_skills(selected)))

    lines.append("")
    lines.append("## Professional Experience")
    lines.append("")

    for exp in selected["experiences"]:
        lines.append(f"### {exp.get('company', '')} - {exp.get('title', '')}")
        date_line = " | ".join(
            filter(None, [f"{exp.get('start_date', '')} - {exp.get('end_date', '')}", exp.get("location", "")])
        )
        if date_line:
            lines.append(date_line)
        lines.append("")
        if exp.get("summary"):
            lines.append(exp["summary"])
            lines.append("")
        for bullet in select_bullets(exp, 5, selected.get("keywords", [])):
            lines.append(f"- {bullet}")
        lines.append("")

    if selected["projects"]:
        lines.append("## Projects")
        lines.append("")
        for project in selected["projects"]:
            lines.append(f"### {project.get('name', '')}")
            if project.get("summary"):
                lines.append(project["summary"])
            for bullet in select_bullets(project, 4, selected.get("keywords", [])):
                lines.append(f"- {bullet}")
            lines.append("")

    education = profile.get("education", [])
    if education:
        lines.append("## Education")
        lines.append("")
        for item in education:
            degree = item.get("degree", "")
            major = item.get("major", "")
            institution = item.get("institution", "")
            location = item.get("location", "")
            years = " - ".join(filter(None, [item.get("start_year", ""), item.get("end_year", "")]))

            title = degree
            if major:
                title = f"{degree}, {major}" if degree else major
            if title:
                lines.append(f"### {title}")

            details = " | ".join(filter(None, [institution, location, years]))
            if details:
                lines.append(details)
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_payload(selected: dict, target_job_id: str | None) -> dict:
    return {
        "profile_used": "cv-data/profile.json",
        "target_job_id": target_job_id or "",
        "selected_experiences": [item["id"] for item in selected["experiences"]],
        "selected_projects": [item["id"] for item in selected["projects"]],
        "selected_repos": selected["repo_slugs"],
        "selected_skills": selected["skills"],
        "generated_at": now_utc(),
    }


def generate_general() -> None:
    master = build_master_data()
    selected = select_general(master)
    draft_md = render_cv(master["profile"], selected, None)
    final_md = refine_cv_markdown(draft_md, master["profile"], {**selected, "selected_skills": selected["skills"]}, None)
    payload = render_payload(selected, None)
    out_dir = GENERATED_CVS_DIR / "general"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cv.draft.md").write_text(draft_md, encoding="utf-8")
    (out_dir / "cv.md").write_text(final_md, encoding="utf-8")
    write_json(out_dir / "cv.json", payload)
    write_json(out_dir / "meta.json", {"type": "general", "generated_at": now_utc()})
    print(out_dir)


def generate_for_job(job_slug: str) -> None:
    master = build_master_data()
    job = read_json(JOB_TARGETS_DIR / job_slug / "parsed" / "job.json", {})
    if not job:
        raise FileNotFoundError(f"Unknown job target: {job_slug}")
    selected = select_for_job(master, job)
    draft_md = render_cv(master["profile"], selected, job)
    final_md = refine_cv_markdown(draft_md, master["profile"], {**selected, "selected_skills": selected["skills"]}, job)
    payload = render_payload(selected, job_slug)
    out_dir = JOB_TARGETS_DIR / job_slug / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cv.draft.md").write_text(draft_md, encoding="utf-8")
    (out_dir / "cv.md").write_text(final_md, encoding="utf-8")
    write_json(out_dir / "cv.json", payload)
    generated_dir = GENERATED_CVS_DIR / job_slug
    generated_dir.mkdir(parents=True, exist_ok=True)
    (generated_dir / "latest.draft.md").write_text(draft_md, encoding="utf-8")
    (generated_dir / "latest.md").write_text(final_md, encoding="utf-8")
    write_json(generated_dir / "latest.json", payload)
    print(out_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate general or job-targeted CVs from stored data."
    )
    parser.add_argument("--general", action="store_true")
    parser.add_argument("--job")
    args = parser.parse_args()
    if not args.general and not args.job:
        parser.error("Pass --general or --job <job-slug>.")
    return args


def main() -> int:
    args = parse_args()
    if args.general:
        generate_general()
    else:
        generate_for_job(slugify(args.job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
