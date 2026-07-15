#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=HexColor("#111827"),
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
        "headline": ParagraphStyle(
            "Headline",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=HexColor("#1f2937"),
            spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            textColor=HexColor("#4b5563"),
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=HexColor("#111827"),
            spaceBefore=6,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=HexColor("#1f2937"),
            spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=HexColor("#6b7280"),
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=12.5,
            textColor=HexColor("#1f2937"),
            leftIndent=14,
            firstLineIndent=-8,
            bulletIndent=4,
            spaceAfter=3,
        ),
    }


def escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def parse_markdown(markdown: str):
    lines = markdown.splitlines()
    items: list[tuple[str, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            items.append(("blank", ""))
        elif stripped.startswith("# "):
            items.append(("h1", stripped[2:].strip()))
        elif stripped.startswith("## "):
            items.append(("h2", stripped[3:].strip()))
        elif stripped.startswith("### "):
            items.append(("h3", stripped[4:].strip()))
        elif stripped.startswith("- "):
            items.append(("bullet", stripped[2:].strip()))
        else:
            items.append(("p", stripped))
    return items


def render_pdf(markdown_path: Path, pdf_path: Path) -> None:
    styles = build_styles()
    items = parse_markdown(markdown_path.read_text(encoding="utf-8"))
    story = []

    after_h1 = 0
    current_section = ""
    for kind, text in items:
        if kind == "blank":
            story.append(Spacer(1, 0.08 * inch))
            continue
        if kind == "h1":
            story.append(Paragraph(escape_text(text), styles["name"]))
            after_h1 = 1
            continue
        if after_h1 == 1 and kind == "p":
            story.append(Paragraph(escape_text(text), styles["headline"]))
            after_h1 = 2
            continue
        if after_h1 == 2 and kind == "p":
            story.append(Paragraph(escape_text(text), styles["contact"]))
            after_h1 = 0
            continue

        if kind == "h2":
            current_section = text
            story.append(Paragraph(escape_text(text), styles["h2"]))
        elif kind == "h3":
            story.append(Paragraph(escape_text(text), styles["h3"]))
        elif kind == "bullet":
            story.append(Paragraph(escape_text(text), styles["bullet"], bulletText="•"))
        elif kind == "p":
            style = styles["body"]
            if current_section == "Professional Experience" and re_date_line(text):
                style = styles["meta"]
            story.append(Paragraph(escape_text(text), style))

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=markdown_path.stem,
        author="Codex",
    )
    doc.build(story)


def re_date_line(text: str) -> bool:
    return bool(text[:7].count("-") == 1 and text[:4].isdigit())


def parse_args():
    parser = argparse.ArgumentParser(description="Render a generated CV markdown file to PDF.")
    parser.add_argument("--input", required=True, help="Path to input markdown CV")
    parser.add_argument("--output", required=True, help="Path to output PDF")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    render_pdf(Path(args.input), Path(args.output))
    print(Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
