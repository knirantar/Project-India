from __future__ import annotations

from pathlib import Path
import re

from project_india import paths
from project_india.topics import TOPIC_FOLDERS, create_topic, slugify


def _read_section(markdown: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in markdown:
        return "TBD."
    after = markdown.split(marker, 1)[1]
    next_heading = after.find("\n## ")
    section = after if next_heading == -1 else after[:next_heading]
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return "\n".join(lines) if lines else "TBD."


def _bullets(text: str, limit: int = 5) -> list[str]:
    bullets = []
    for line in text.splitlines():
        clean = line.strip().lstrip("-").strip()
        if clean and clean != "TBD.":
            bullets.append(clean)
    if not bullets and text.strip() and text.strip() != "TBD.":
        bullets = [text.strip()]
    return bullets[:limit] or ["TBD."]


def _topic_path(slug: str, category: str) -> Path:
    return TOPIC_FOLDERS[category] / f"{slug}.md"


def _load_or_create_topic(title: str, slug: str, category: str) -> Path:
    path = _topic_path(slug, category)
    if not path.exists():
        create_topic(title, slug=slug, category=category)
    return path


def _outline_path(slug: str) -> Path:
    return paths.PRESENTATIONS / f"{slug}-outline.md"


def _outline_slides(markdown: str) -> list[tuple[str, list[str]]]:
    outline = _read_section(markdown, "Slide Outline")
    if outline == "TBD.":
        return []

    slides: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_bullets: list[str] = []

    for line in outline.splitlines():
        stripped = line.strip()
        match = re.match(r"^\d+\.\s+(.*)", stripped)
        if match:
            if current_title:
                slides.append((current_title, current_bullets[:5] or ["TBD."]))
            current_title = match.group(1).strip()
            current_bullets = []
            continue

        if current_title and stripped.startswith("-"):
            current_bullets.append(stripped.lstrip("-").strip())
        elif current_title and stripped:
            current_bullets.append(stripped)

    if current_title:
        slides.append((current_title, current_bullets[:5] or ["TBD."]))

    return slides[:12]


def build_presentation(
    title: str,
    slug: str | None = None,
    category: str = "sectors",
    output_path: Path | None = None,
) -> Path:
    topic_slug = slugify(slug or title)
    topic_path = _load_or_create_topic(title, topic_slug, category)
    markdown = topic_path.read_text(encoding="utf-8")
    outline_path = _outline_path(topic_slug)
    outline_markdown = outline_path.read_text(encoding="utf-8") if outline_path.exists() else ""

    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches, Pt
    except ImportError as error:
        raise SystemExit(
            "python-pptx is required. Install with: python3 -m pip install -e '.[presentation]'"
        ) from error

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    ink = RGBColor(21, 21, 21)
    muted = RGBColor(103, 98, 90)
    saffron = RGBColor(217, 119, 6)
    paper = RGBColor(247, 241, 231)

    def add_slide(kicker: str, claim: str, bullets: list[str]) -> None:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = paper

        marker = slide.shapes.add_shape(1, Inches(0.65), Inches(0.55), Inches(0.18), Inches(0.18))
        marker.fill.solid()
        marker.fill.fore_color.rgb = saffron
        marker.line.fill.background()

        kicker_box = slide.shapes.add_textbox(Inches(0.95), Inches(0.48), Inches(2.2), Inches(0.3))
        kicker_tf = kicker_box.text_frame
        kicker_tf.text = kicker.upper()
        kicker_run = kicker_tf.paragraphs[0].runs[0]
        kicker_run.font.size = Pt(9)
        kicker_run.font.bold = True
        kicker_run.font.color.rgb = muted

        title_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.02), Inches(11.3), Inches(1.0))
        title_tf = title_box.text_frame
        title_tf.word_wrap = True
        title_tf.text = claim
        title_run = title_tf.paragraphs[0].runs[0]
        title_run.font.size = Pt(27)
        title_run.font.bold = True
        title_run.font.color.rgb = ink

        body_box = slide.shapes.add_textbox(Inches(1.05), Inches(2.45), Inches(10.7), Inches(3.5))
        body_tf = body_box.text_frame
        body_tf.word_wrap = True
        body_tf.clear()
        for index, item in enumerate(bullets):
            para = body_tf.paragraphs[0] if index == 0 else body_tf.add_paragraph()
            para.text = item
            para.level = 0
            para.space_after = Pt(10)
            para.font.size = Pt(18)
            para.font.color.rgb = ink

        footer = slide.shapes.add_textbox(Inches(0.65), Inches(6.95), Inches(11.7), Inches(0.22))
        footer_tf = footer.text_frame
        footer_tf.text = "Project India | generated presentation draft | verify time-sensitive claims"
        footer_para = footer_tf.paragraphs[0]
        footer_para.alignment = PP_ALIGN.LEFT
        footer_run = footer_para.runs[0]
        footer_run.font.size = Pt(8)
        footer_run.font.color.rgb = muted

    researched_slides = _outline_slides(outline_markdown)

    if researched_slides:
        core_message = _read_section(outline_markdown, "Core Message")
        add_slide("Topic", title, _bullets(core_message, 3))
        for index, (claim, bullets) in enumerate(researched_slides, start=1):
            add_slide(f"Slide {index}", claim, bullets)
    else:
        add_slide("Topic", title, [_read_section(markdown, "One-Line Summary")])
        add_slide("Why it matters", "This topic matters because it changes the strategic picture.", _bullets(_read_section(markdown, "Why This Matters"), 4))
        add_slide("Current state", "The current state gives us the baseline for analysis.", _bullets(_read_section(markdown, "Current State"), 5))
        add_slide("Context", "Historical context prevents shallow conclusions.", _bullets(_read_section(markdown, "Historical Context"), 5))
        add_slide("Actors", "The key actors define incentives and constraints.", _bullets(_read_section(markdown, "Key Actors and Institutions"), 6))
        add_slide("Data", "The next analytical layer is data and indicators.", _bullets(_read_section(markdown, "Data and Indicators"), 6))
        add_slide("Opportunities", "The opportunity set is where strategy becomes concrete.", _bullets(_read_section(markdown, "Opportunities"), 5))
        add_slide("Risks", "The risks show where the story can break.", _bullets(_read_section(markdown, "Risks"), 5))
        add_slide("Watch next", "The follow-up agenda should drive the next research cycle.", _bullets(_read_section(markdown, "Open Questions"), 6))

    output = Path(output_path) if output_path else paths.PRESENTATIONS / f"{topic_slug}-generated-deck.pptx"
    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output)
    return output
