#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path.cwd()
CV_DATA_DIR = ROOT / "cv-data"
JOB_TARGETS_DIR = ROOT / "job-targets"
GENERATED_CVS_DIR = ROOT / "generated-cvs"
REPO_ANALYSIS_DIR = ROOT / "repo-analysis-results"
EMPLOYMENT_TYPES = {
    "Hire (W2)",
    "W2 through Staffing Company",
    "Contract (1099)",
    "Hire",
    "Contract",
}
PROXY_REQUIRED_EMPLOYMENT_TYPES = {
    "W2 through Staffing Company",
}
PROXY_COMPANY_FIELDS = {"name", "website", "phone", "email"}
PROXY_ADDRESS_FIELDS = {"line1", "line2", "city", "state", "postal_code", "country"}
PROXY_CONTACT_FIELDS = {"name", "title", "department", "email", "phone", "linkedin"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_list_of_strings_or_notes(values, field_name: str, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"{field_name} must be a list.")
        return
    for index, value in enumerate(values):
        if isinstance(value, str):
            continue
        if isinstance(value, dict) and "note" in value:
            continue
        errors.append(f"{field_name}[{index}] must be a string or an object containing a 'note' field.")


def ensure_list_of_strings(values, field_name: str, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"{field_name} must be a list.")
        return
    for index, value in enumerate(values):
        if not isinstance(value, str):
            errors.append(f"{field_name}[{index}] must be a string.")


def ensure_optional_string_fields(
    values: dict, allowed_fields: set[str], field_name: str, errors: list[str]
) -> None:
    for field in allowed_fields:
        value = values.get(field, "")
        if value is not None and not isinstance(value, str):
            errors.append(f"{field_name}.{field} must be a string when present.")


def validate_proxy_company(payload: dict, path: Path, errors: list[str]) -> None:
    proxy_company = payload.get("proxy_company")
    employment_type = payload.get("employment_type", "")

    if isinstance(employment_type, str) and employment_type in PROXY_REQUIRED_EMPLOYMENT_TYPES and not isinstance(proxy_company, dict):
        errors.append(f"{path.name}.proxy_company is required for {employment_type}.")
        return
    if proxy_company is None:
        return
    if not isinstance(proxy_company, dict):
        errors.append(f"{path.name}.proxy_company must be an object when present.")
        return
    if not isinstance(employment_type, str) or employment_type not in PROXY_REQUIRED_EMPLOYMENT_TYPES:
        errors.append(f"{path.name}.proxy_company is only allowed for W2 through Staffing Company arrangements.")

    name = proxy_company.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{path.name}.proxy_company.name must be a non-empty string.")
    ensure_optional_string_fields(proxy_company, PROXY_COMPANY_FIELDS, f"{path.name}.proxy_company", errors)

    address = proxy_company.get("address")
    if address is not None:
        if not isinstance(address, dict):
            errors.append(f"{path.name}.proxy_company.address must be an object when present.")
        else:
            ensure_optional_string_fields(
                address,
                PROXY_ADDRESS_FIELDS,
                f"{path.name}.proxy_company.address",
                errors,
            )

    contact_person = proxy_company.get("contact_person")
    if contact_person is not None:
        if not isinstance(contact_person, dict):
            errors.append(f"{path.name}.proxy_company.contact_person must be an object when present.")
        else:
            ensure_optional_string_fields(
                contact_person,
                PROXY_CONTACT_FIELDS,
                f"{path.name}.proxy_company.contact_person",
                errors,
            )


def validate_profile(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Missing required file: {path}"]
    try:
        payload = read_json(path)
    except Exception as exc:
        return [f"Could not parse {path}: {exc}"]

    if not isinstance(payload, dict):
        return [f"{path} must contain a JSON object."]

    for field in ("name", "headline", "summary", "location", "email", "phone"):
        value = payload.get(field, "")
        if value and not isinstance(value, str):
            errors.append(f"{path.name}.{field} must be a string when present.")

    links = payload.get("links", {})
    if links and not isinstance(links, dict):
        errors.append(f"{path.name}.links must be an object.")

    education = payload.get("education", [])
    if education and not isinstance(education, list):
        errors.append(f"{path.name}.education must be a list.")

    return errors


def validate_item(path: Path, kind: str) -> list[str]:
    errors: list[str] = []
    try:
        payload = read_json(path)
    except Exception as exc:
        return [f"Could not parse {path}: {exc}"]

    if not isinstance(payload, dict):
        return [f"{path} must contain a JSON object."]

    identity_field = "company" if kind == "experience" else "name"
    required_fields = ["id", identity_field]
    for field in required_fields:
        value = payload.get(field, "")
        if value and not isinstance(value, str):
            errors.append(f"{path.name}.{field} must be a string.")

    fields = ("summary", "title", "location", "start_date", "end_date")
    if kind == "experience":
        fields += ("employment_type", "work_mode")
    for field in fields:
        value = payload.get(field, "")
        if value and not isinstance(value, str):
            errors.append(f"{path.name}.{field} must be a string when present.")

    if kind == "experience":
        employment_type = payload.get("employment_type", "")
        work_mode = payload.get("work_mode", "")
        if isinstance(employment_type, str) and employment_type and employment_type not in EMPLOYMENT_TYPES:
            errors.append(f"{path.name}.employment_type is not a supported employment relationship.")
        validate_proxy_company(payload, path, errors)

    ensure_list_of_strings(payload.get("manual_skills", []), f"{path.name}.manual_skills", errors)
    ensure_list_of_strings(payload.get("manual_tools", []), f"{path.name}.manual_tools", errors)
    ensure_list_of_strings(payload.get("manual_highlights", []), f"{path.name}.manual_highlights", errors)
    ensure_list_of_strings_or_notes(payload.get("manual_notes", []), f"{path.name}.manual_notes", errors)
    ensure_list_of_strings(payload.get("skills_override", []), f"{path.name}.skills_override", errors)
    ensure_list_of_strings(payload.get("repo_links", []), f"{path.name}.repo_links", errors)

    related_field = "project_links" if kind == "experience" else "experience_links"
    ensure_list_of_strings(payload.get(related_field, []), f"{path.name}.{related_field}", errors)

    return errors


def validate_repo_analysis(path: Path) -> list[str]:
    try:
        payload = read_json(path)
    except Exception as exc:
        return [f"Could not parse {path}: {exc}"]

    if not isinstance(payload, dict):
        return [f"{path} must contain a JSON object."]
    return []


def validate_workspace(root: Path) -> list[str]:
    errors: list[str] = []
    profile_path = root / "cv-data" / "profile.json"
    errors.extend(validate_profile(profile_path))

    experiences_dir = root / "cv-data" / "experiences"
    if experiences_dir.exists():
        for path in sorted(experiences_dir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            errors.extend(validate_item(path, "experience"))

    projects_dir = root / "cv-data" / "projects"
    if projects_dir.exists():
        for path in sorted(projects_dir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            errors.extend(validate_item(path, "project"))

    repo_dir = root / "repo-analysis-results"
    if repo_dir.exists():
        for path in sorted(repo_dir.glob("*/analysis.json")):
            errors.extend(validate_repo_analysis(path))

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate cvWriter workspace data files.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Path to the workspace root. Defaults to the current directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    errors = validate_workspace(workspace)
    if errors:
        print("Workspace validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
