#!/usr/bin/env python3
"""Validate generated portfolio pages and local references using stdlib only."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []
        self.canonicals = 0
        self.alternates: set[str] = set()
        self.html_lang = ""
        self.images = 0
        self.images_with_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = data.get("lang", "")
        element_id = data.get("id")
        if element_id:
            self.ids.add(element_id)
        for attr in ("href", "src"):
            value = data.get(attr)
            if value:
                self.refs.append((attr, value))
        if tag == "link" and data.get("rel") == "canonical":
            self.canonicals += 1
        if tag == "link" and data.get("rel") == "alternate" and data.get("hreflang"):
            self.alternates.add(data["hreflang"])
        if tag == "img":
            self.images += 1
            if "alt" in data:
                self.images_with_alt += 1


def html_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)


def target_for_path(url_path: str) -> Path:
    clean = unquote(url_path).lstrip("/")
    target = ROOT / clean
    if not clean or url_path.endswith("/"):
        return target / "index.html"
    if target.is_dir():
        return target / "index.html"
    return target


def is_external(ref: str) -> bool:
    parsed = urlsplit(ref)
    return parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"} or ref.startswith("//")


def main() -> int:
    errors: list[str] = []
    pages = html_files()
    parsed_pages: dict[Path, PageParser] = {}
    total_refs = 0

    if not pages:
        errors.append("No generated HTML pages found. Run scripts/build.py first.")

    for page in pages:
        text = page.read_text(encoding="utf-8")
        if "{{" in text or "}}" in text:
            errors.append(f"Unresolved template variable in {page.relative_to(ROOT)}")
        parser = PageParser()
        parser.feed(text)
        parsed_pages[page.resolve()] = parser
        if parser.canonicals != 1:
            errors.append(f"{page.relative_to(ROOT)} has {parser.canonicals} canonical links; expected 1")
        if not {"zh-CN", "en", "x-default"}.issubset(parser.alternates):
            errors.append(f"Missing hreflang alternates in {page.relative_to(ROOT)}")
        if parser.images != parser.images_with_alt:
            errors.append(f"Image without alt attribute in {page.relative_to(ROOT)}")

    for page in pages:
        parser = parsed_pages[page.resolve()]
        for attr, ref in parser.refs:
            if is_external(ref):
                continue
            parsed = urlsplit(ref)
            path_part = parsed.path
            fragment = parsed.fragment
            if not path_part:
                target = page
            elif path_part.startswith("/"):
                target = target_for_path(path_part)
            else:
                target = (page.parent / path_part).resolve()
                if path_part.endswith("/"):
                    target = target / "index.html"
            total_refs += 1
            if not target.exists():
                errors.append(f"Broken local {attr} in {page.relative_to(ROOT)}: {ref}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_parser = parsed_pages.get(target.resolve())
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    parsed_pages[target.resolve()] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(f"Missing anchor #{fragment} in {target.relative_to(ROOT)} (linked from {page.relative_to(ROOT)})")

    config = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
    zh_brand = config["identity"]["zh"]["brand"]
    en_brand = config["identity"]["en"]["brand"]
    zh_home = (ROOT / "index.html").read_text(encoding="utf-8")
    en_home = (ROOT / "en" / "index.html").read_text(encoding="utf-8")
    if f"<strong>{zh_brand}</strong>" not in zh_home:
        errors.append("Chinese header brand does not match data/site.json")
    if f"<strong>{en_brand}</strong>" not in en_home:
        errors.append("English header brand does not match data/site.json")
    if re.search(r'<body[^>]*data-lang="zh"[\s\S]*?<a class="brand"[^>]*><strong>(?:MA ZIXIAO|ZIXIAO MA)</strong>', zh_home):
        errors.append("Chinese homepage still contains a hard-coded English brand")

    project_dirs = sorted(p.name for p in (ROOT / "content" / "projects").iterdir() if p.is_dir() and not p.name.startswith("_"))
    for slug in project_dirs:
        for path in (ROOT / "projects" / slug / "index.html", ROOT / "en" / "projects" / slug / "index.html"):
            if not path.exists():
                errors.append(f"Missing generated bilingual project page: {path.relative_to(ROOT)}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Checked {len(pages)} HTML files and {total_refs} local references: all valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
