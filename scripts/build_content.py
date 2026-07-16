#!/usr/bin/env python3
from __future__ import annotations

import json
import posixpath
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROJECT_IDS = ["project1", "project2", "project3", "project4", "moreprojects", "aboutme"]
LANGUAGES = {"zh": "content.md", "en": "content_en.md"}

FRONT_MATTER_RE = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$")
IMAGE_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")
YOUTUBE_RE = re.compile(r'^@\[youtube\]\((\S+?)(?:\s+["“](.*?)["”])?\)\s*$')
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LINKS_ONLY_RE = re.compile(r"^(?:\s*\[[^\]]+\]\([^)]+\)\s*)+$")


def parse_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    normalized = markdown.replace("\r\n", "\n")
    match = FRONT_MATTER_RE.match(normalized)
    if not match:
        raise ValueError("Missing Markdown front matter enclosed by ---")
    meta: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid metadata line: {raw_line}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"\'')
    return meta, match.group(2).strip()


def resolve_path(project_id: str, value: str) -> str:
    value = value.strip()
    if re.match(r"^(?:https?:|mailto:|data:|#)", value, re.I):
        return value
    return posixpath.normpath(posixpath.join(project_id, value))


def youtube_id(value: str) -> str:
    value = value.strip()
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
        r"youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/)([A-Za-z0-9_-]{6,})",
    ]
    for pattern in patterns:
        found = re.search(pattern, value)
        if found:
            return found.group(1)
    return value


def flush_paragraph(lines: list[str], blocks: list[dict[str, Any]], project_id: str) -> None:
    if not lines:
        return
    paragraph = "\n".join(lines).strip()
    lines.clear()
    if not paragraph:
        return

    if LINKS_ONLY_RE.fullmatch(paragraph):
        links = [
            {"label": label.strip(), "href": resolve_path(project_id, href.strip())}
            for label, href in LINK_RE.findall(paragraph)
        ]
        blocks.append({"kind": "buttons", "links": links})
        return

    blocks.append({"kind": "paragraph", "text": paragraph})


def parse_blocks(body: str, project_id: str, language: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    paragraph_lines: list[str] = []

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph(paragraph_lines, blocks, project_id)
            continue

        if stripped.startswith("## "):
            flush_paragraph(paragraph_lines, blocks, project_id)
            blocks.append({"kind": "heading", "text": stripped[3:].strip()})
            continue

        image_match = IMAGE_RE.fullmatch(stripped)
        if image_match:
            flush_paragraph(paragraph_lines, blocks, project_id)
            blocks.append({
                "kind": "image",
                "caption": image_match.group(1).strip(),
                "src": resolve_path(project_id, image_match.group(2).strip()),
            })
            continue

        youtube_match = YOUTUBE_RE.fullmatch(stripped)
        if youtube_match:
            flush_paragraph(paragraph_lines, blocks, project_id)
            blocks.append({
                "kind": "youtube",
                "id": youtube_id(youtube_match.group(1)),
                "caption": (youtube_match.group(2) or ("YouTube Video" if language == "en" else "YouTube 视频")).strip(),
            })
            continue

        paragraph_lines.append(line)

    flush_paragraph(paragraph_lines, blocks, project_id)
    return blocks


def validate_local_file(relative_path: str, source: Path) -> None:
    if re.match(r"^(?:https?:|mailto:|data:|#)", relative_path, re.I):
        return
    target = ROOT / relative_path
    if not target.is_file():
        raise FileNotFoundError(f"{source.relative_to(ROOT)} references a missing file: {relative_path}")


def parse_project(project_id: str, language: str, filename: str) -> tuple[dict[str, Any], dict[str, Any]]:
    source = ROOT / project_id / filename
    if not source.is_file():
        raise FileNotFoundError(f"Missing {project_id}/{filename}")

    meta, body = parse_front_matter(source.read_text(encoding="utf-8"))
    required = ["title", "tag", "type", "role", "time", "caption"]
    missing = [key for key in required if not meta.get(key)]
    if missing:
        raise ValueError(f"{source.relative_to(ROOT)} is missing metadata: {', '.join(missing)}")

    database = {
        "title": meta["title"],
        "tabTitle": meta.get("tab_title", meta["title"]),
        "tag": meta["tag"],
        "type": meta["type"],
        "role": meta["role"],
        "time": meta["time"],
        "caption": meta["caption"],
    }
    content: dict[str, Any] = {"blocks": parse_blocks(body, project_id, language)}

    if meta.get("hero"):
        hero_path = resolve_path(project_id, meta["hero"])
        validate_local_file(hero_path, source)
        content["hero"] = {
            "src": hero_path,
            "caption": meta.get("hero_caption", meta["title"]),
        }
        width = meta.get("hero_width", "").strip()
        if width:
            if not re.fullmatch(r"(?:100|[1-9]?\d)%|\d{2,4}px", width):
                raise ValueError(f"Invalid hero_width in {source.relative_to(ROOT)}: {width}")
            content["hero"]["width"] = width

    for block in content["blocks"]:
        if block["kind"] == "image":
            validate_local_file(block["src"], source)
        elif block["kind"] == "buttons":
            for link in block["links"]:
                validate_local_file(link["href"], source)

    return database, content


def main() -> int:
    payload: dict[str, dict[str, Any]] = {}

    try:
        for language, filename in LANGUAGES.items():
            database: dict[str, Any] = {}
            content: dict[str, Any] = {}
            for project_id in PROJECT_IDS:
                database[project_id], content[project_id] = parse_project(project_id, language, filename)
            payload[language] = {"database": database, "content": content}
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

    output = "// Generated by scripts/build_content.py. Do not edit manually.\n"
    output += "window.SITE_CONTENT_BY_LANGUAGE = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    output += "window.SITE_CONTENT = window.SITE_CONTENT_BY_LANGUAGE.zh;\n"
    (ROOT / "content.generated.js").write_text(output, encoding="utf-8")
    print("Generated bilingual content.generated.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
