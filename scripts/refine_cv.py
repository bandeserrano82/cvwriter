#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime


PRIMARY_SKILL_ORDER = [
    "Codex", "OpenAI", "AI Agents", "AI-Assisted Development", "Python",
    "JavaScript", "TypeScript", "React", "Next.js", "Vue.js", "Nuxt.js",
    "Node.js", "SQL", "PostgreSQL", "Azure", "Docker", "REST APIs", "CI/CD",
    ".NET", "ASP.NET", "C#", "PHP", "Linux",
]

CATEGORY_RULES = {
    "frontend": {"React", "Next.js", "Vue.js", "Nuxt.js", "JavaScript", "TypeScript", "HTML", "CSS"},
    "backend": {"Python", "PHP", ".NET", "ASP.NET", "C#", "Django", "FastAPI", "RabbitMQ", "REST APIs"},
    "cloud": {"Azure", "AWS", "Docker", "Kubernetes", "CI/CD", "Linux", "Azure Functions", "Azure App Service"},
    "data": {"SQL", "SQL Server", "PostgreSQL", "Database Design", "ETL", "Dataverse", "Azure SQL"},
    "automation": {"AI Agents", "Power Automate", "GitHub Actions", "Testing", "DevOps"},
}


def format_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def infer_years(experiences: list[dict]) -> str:
    years: list[int] = []
    for exp in experiences:
        match = re.match(r"(\d{4})", exp.get("start_date", ""))
        if match:
            years.append(int(match.group(1)))
    if not years:
        return ""
    total = max(datetime.now().year - min(years), 1)
    return f"{total}+ years"


def select_primary_skills(skills: list[str], limit: int = 6) -> list[str]:
    ordered: list[str] = []
    skill_set = set(skills)
    for skill in PRIMARY_SKILL_ORDER:
        if skill in skill_set:
            ordered.append(skill)
    for skill in skills:
        if skill not in ordered:
            ordered.append(skill)
    return ordered[:limit]


def present_categories(skills: list[str]) -> list[str]:
    skill_set = set(skills)
    labels: list[str] = []
    if CATEGORY_RULES["frontend"] & skill_set:
        labels.append("frontend")
    if CATEGORY_RULES["backend"] & skill_set:
        labels.append("backend")
    if CATEGORY_RULES["cloud"] & skill_set:
        labels.append("cloud")
    if CATEGORY_RULES["data"] & skill_set:
        labels.append("data")
    if CATEGORY_RULES["automation"] & skill_set:
        labels.append("automation")
    return labels


def matched_job_skills(skills: list[str], keywords: list[str]) -> list[str]:
    matches: list[str] = []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for skill in skills:
        skill_lower = skill.lower()
        if any(keyword in skill_lower or skill_lower in keyword for keyword in lowered_keywords):
            matches.append(skill)
    return matches


def frontend_primary(skills: list[str]) -> list[str]:
    preferred = [
        "TypeScript", "React", "Next.js", "Vue.js", "Nuxt.js",
        "JavaScript", "HTML", "CSS", "Tailwind CSS", "TanStack", "TanStack Table",
    ]
    result: list[str] = []
    skill_set = set(skills)
    for skill in preferred:
        if skill in skill_set:
            result.append(skill)
    return result


def leadership_primary(skills: list[str]) -> list[str]:
    preferred = [
        "System Architecture", "Azure", "CI/CD", ".NET", "Node.js",
        "REST APIs", "SQL", "PostgreSQL", "DevOps", "Code Review",
        "Project Management", "Team Leadership",
    ]
    result: list[str] = []
    skill_set = set(skills)
    for skill in preferred:
        if skill in skill_set:
            result.append(skill)
    return result


def backend_platform_primary(skills: list[str]) -> list[str]:
    preferred = [
        "Python", "Django", "FastAPI", "PostgreSQL", "Redis",
        "REST APIs", "React", "Next.js", "TypeScript", "CI/CD",
        "Docker", "System Architecture", "Node.js", "Azure",
    ]
    result: list[str] = []
    skill_set = set(skills)
    for skill in preferred:
        if skill in skill_set:
            result.append(skill)
    return result


def backend_service_primary(skills: list[str]) -> list[str]:
    preferred = [
        ".NET", "C#", "Node.js", "SQL", "SQL Server", "REST APIs",
        "React", "TypeScript", "CI/CD", "Docker", "Testing",
        "Azure", "System Architecture", "ASP.NET", "PostgreSQL",
    ]
    result: list[str] = []
    skill_set = set(skills)
    for skill in preferred:
        if skill in skill_set:
            result.append(skill)
    return result


def build_summary(profile: dict, selected: dict, target_job: dict | None) -> str:
    headline = profile.get("headline", "Full-stack Software Engineer")
    years = infer_years(selected.get("experiences", []))
    skills = selected.get("selected_skills") or selected.get("skills", [])
    primary = select_primary_skills(skills)
    categories = present_categories(skills)

    if target_job:
        keywords = target_job.get("keywords", [])
        frontend_emphasis = selected.get("frontend_emphasis", False)
        dashboard_emphasis = selected.get("dashboard_emphasis", False)
        leadership_emphasis = selected.get("leadership_emphasis", False)
        backend_platform_emphasis = selected.get("backend_platform_emphasis", False)
        keyword_set = {keyword.lower() for keyword in keywords}
        if dashboard_emphasis:
            frontend = frontend_primary(skills)[:6]
            support = [skill for skill in primary if skill not in frontend][:4]
            frontend_text = format_list(frontend) if frontend else "React, TypeScript, and modern dashboard-oriented frontend delivery"
            support_text = format_list(support) if support else "API integration, cloud delivery, and data-driven application work"
            return (
                f"{headline} with {years} of experience building production full-stack applications with strong frontend depth for data-driven and workflow-heavy business systems. "
                f"Offers hands-on evidence in {frontend_text}, with additional experience across {support_text}. "
                f"Background includes responsive dashboards, complex UI development, API-integrated workflows, and cloud-based application delivery."
            )
        if backend_platform_emphasis and {".net", "c#", "node.js", "sql", "restful", "api", "testing"} & keyword_set:
            backend = backend_service_primary(skills)[:6]
            support = [skill for skill in primary if skill not in backend][:4]
            backend_text = format_list(backend) if backend else "backend services, APIs, databases, and delivery automation"
            support_text = format_list(support) if support else "full-stack product delivery"
            return (
                f"{headline} with {years} of experience building production full-stack applications with strong backend service and platform delivery depth. "
                f"Offers hands-on evidence in {backend_text}, with additional experience across {support_text}. "
                f"Background includes responsive frontend delivery, cloud services, testing, CI/CD, and maintainable API-driven systems."
            )
        if leadership_emphasis and {"python", "django", "postgresql", "redis", "rest", "api", "apis"} & keyword_set:
            backend = backend_platform_primary(skills)[:6]
            support = [skill for skill in primary if skill not in backend][:4]
            backend_text = format_list(backend) if backend else "Python backend services, APIs, and production platform delivery"
            support_text = format_list(support) if support else "technical leadership and full-stack delivery"
            return (
                f"{headline} with {years} of experience delivering production full-stack systems with hands-on ownership across backend services, APIs, data workflows, and modern frontend applications. "
                f"Offers strong evidence in {backend_text}, with additional experience across {support_text}. "
                f"Background includes platform architecture, CI/CD, cloud delivery, and building scalable workflow-driven applications."
            )
        if leadership_emphasis:
            leadership = leadership_primary(skills)[:6]
            support = [skill for skill in primary if skill not in leadership][:4]
            leadership_text = format_list(leadership) if leadership else "architecture, delivery leadership, and full-stack engineering"
            support_text = format_list(support) if support else "enterprise software delivery"
            return (
                f"{headline} with {years} of experience delivering end-to-end software solutions and leading technical execution across complex engineering initiatives. "
                f"Offers hands-on evidence in {leadership_text}, with additional experience across {support_text}. "
                f"Background includes architecture, team leadership, CI/CD, code reviews, and full-stack delivery for production systems."
            )
        if frontend_emphasis:
            frontend = frontend_primary(skills)[:6]
            support = [skill for skill in primary if skill not in frontend][:4]
            frontend_text = format_list(frontend) if frontend else "modern frontend application development"
            support_text = format_list(support) if support else "cross-stack product delivery"
            return (
                f"{headline} with {years} of experience building production, client-facing applications with strong frontend depth. "
                f"Offers hands-on evidence in {frontend_text}, with additional experience across {support_text}. "
                f"Background includes complex UI development, API-integrated workflows, and full-stack delivery in collaborative engineering environments."
            )
        matched = select_primary_skills(matched_job_skills(skills, keywords), 6)
        support = [skill for skill in primary if skill not in matched][:4]
        matched_text = format_list(matched) if matched else "API-driven application delivery, database work, and modern engineering practices"
        support_text = format_list(support) if support else "production software delivery"
        return (
            f"{headline} with {years} of experience building production applications in collaborative engineering environments. "
            f"Offers strong evidence in {matched_text}, with additional hands-on background in {support_text}. "
            f"Experience spans APIs, data-intensive systems, automation platforms, and cloud-based application delivery."
        )

    category_text = format_list(categories) if categories else "software delivery"
    primary_text = format_list(primary) if primary else "production engineering"
    return (
        f"{headline} with {years} of experience building production systems across {category_text}. "
        f"Background spans {primary_text}, with hands-on work in APIs, data systems, modernization, cloud services, and operational automation."
    )


def rewrite_bullet(bullet: str) -> str:
    bullet = bullet.strip()
    match = re.match(r"Worked across (.+) codebases using (.+)\.$", bullet)
    if match:
        return f"Developed and maintained production systems across {match.group(1)} using {match.group(2)}."

    match = re.match(r"Implemented (.+) patterns in linked production systems\.$", bullet)
    if match:
        return f"Applied {match.group(1)} practices in production systems."

    if bullet == "Built frontend and API-connected application flows backed by linked production repositories.":
        return "Delivered frontend features and API-integrated workflows in production systems."

    if bullet == "Contributed to tested production systems with automated quality checks in linked repositories.":
        return "Supported automated testing and quality controls across production systems."

    return bullet


def refine_cv_markdown(markdown: str, profile: dict, selected: dict, target_job: dict | None = None) -> str:
    lines = markdown.splitlines()
    refined: list[str] = []
    in_summary = False
    inserted_summary = False

    for line in lines:
        if line == "## Professional Summary":
            refined.append(line)
            refined.append("")
            refined.append(build_summary(profile, selected, target_job))
            refined.append("")
            in_summary = True
            inserted_summary = True
            continue

        if in_summary:
            if line.startswith("## "):
                in_summary = False
                if refined and refined[-1] != "":
                    refined.append("")
                refined.append(line)
            continue

        if line.startswith("- "):
            refined.append(f"- {rewrite_bullet(line[2:])}")
        else:
            refined.append(line)

    if not inserted_summary:
        return markdown
    return "\n".join(refined).strip() + "\n"
