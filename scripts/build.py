#!/usr/bin/env python3
"""Build the bilingual static portfolio from Markdown files.

The Chinese site is generated at the repository root. The English site is
mirrored under /en/. Only the Python standard library is required.
"""
from __future__ import annotations

import ast
import html
import json
import re
import shutil
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
CONTENT_DIR = ROOT / "content"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required configuration file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


SITE_CONFIG: dict[str, Any] = load_json(DATA_DIR / "site.json")
LANGUAGES: dict[str, dict[str, Any]] = load_json(DATA_DIR / "i18n.json")
SUPPORTED_LANGUAGES = tuple(LANGUAGES.keys())



def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        try:
            return ast.literal_eval(value)
        except Exception:
            inner = value[1:-1].strip()
            return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def site_for_language(lang: str) -> dict[str, Any]:
    identity = dict(SITE_CONFIG["identity"][lang])
    contact = SITE_CONFIG.get("contact", {})
    resumes = SITE_CONFIG.get("resumes", {})
    social_links = SITE_CONFIG.get("social", [])
    social_by_key = {item.get("key", ""): item.get("url", "") for item in social_links}
    assets = SITE_CONFIG.get("assets", {})
    identity.update(
        {
            "site_url": SITE_CONFIG.get("site_url", "").rstrip("/"),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "resume": resumes.get(lang, ""),
            "resume_zh": resumes.get("zh", ""),
            "resume_en": resumes.get("en", ""),
            "social_links": social_links,
            "linkedin": social_by_key.get("linkedin", ""),
            "github": social_by_key.get("github", ""),
            "favicon": assets.get("favicon", "/assets/images/avatar-monogram.svg"),
            "avatar": assets.get("avatar", "/assets/images/avatar-monogram.svg"),
            "default_og": assets.get("default_og", "/assets/images/decaran-cover.webp"),
            "copyright_start": SITE_CONFIG.get("copyright_start", datetime.now().year),
            "homepage": SITE_CONFIG.get("homepage", {}).get(lang, {}),
        }
    )
    return identity


def nested_value(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def expand_variables(text: str, context: dict[str, Any], source: Path) -> str:
    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        try:
            return str(nested_value(context, key))
        except KeyError as exc:
            raise ValueError(f"Unknown variable '{{{{{key}}}}}' in {source.relative_to(ROOT)}") from exc

    return pattern.sub(replace, text)


def read_md(path: Path, context: dict[str, Any] | None = None) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if context:
        text = expand_variables(text, context, path)
    meta: dict[str, Any] = {}
    body = text
    if text.startswith("---\n"):
        _, fm, body = text.split("---", 2)
        for raw in fm.strip().splitlines():
            if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
                continue
            key, value = raw.split(":", 1)
            meta[key.strip()] = parse_scalar(value)
    return meta, body.strip()


def slugify(text: str, fallback: str) -> str:
    ascii_text = text.lower()
    ascii_text = re.sub(r"[^a-z0-9\s-]", "", ascii_text)
    ascii_text = re.sub(r"[\s-]+", "-", ascii_text).strip("-")
    return ascii_text or fallback


def inline(text: str) -> str:
    """Render a deliberately small and predictable Markdown inline subset."""
    tokens: list[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens)-1}@@"

    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = html.escape(text, quote=False)

    image_re = re.compile(r"!\[([^\]]*)\]\(([^\s\)]+)(?:\s+&quot;([^&]*)&quot;)?\)")
    text = image_re.sub(
        lambda m: stash(
            f'<img class="inline-image" src="{html.escape(m.group(2), quote=True)}" '
            f'alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'
        ),
        text,
    )

    link_re = re.compile(r"\[([^\]]+)\]\(([^\s\)]+)(?:\s+&quot;([^&]*)&quot;)?\)")

    def link_sub(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        ext = url.startswith("http://") or url.startswith("https://")
        attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
        return stash(f'<a href="{html.escape(url, quote=True)}"{attrs}>{label}</a>')

    text = link_re.sub(link_sub, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = text.replace("\n", "<br>")
    for i, token in enumerate(tokens):
        text = text.replace(f"@@TOKEN{i}@@", token)
    return text


@dataclass
class Rendered:
    html: str
    toc: list[tuple[str, str]]


def parse_image_line(line: str) -> tuple[str, str] | None:
    m = re.fullmatch(r"!\[([^\]]*)\]\(([^\s\)]+)(?:\s+\"[^\"]*\")?\)", line.strip())
    if not m:
        return None
    return m.group(1), m.group(2)


def render_directive(name: str, attrs: str, lines: list[str], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    clean = [ln.strip() for ln in lines if ln.strip()]
    if name == "lead":
        return f'<div class="article-lead">{inline(" ".join(clean))}</div>'

    if name in {"capabilities", "metrics", "timeline", "links", "steps", "archive"}:
        items: list[list[str]] = []
        for line in clean:
            if line.startswith("-"):
                items.append([x.strip() for x in line[1:].strip().split("|")])

        if name == "capabilities":
            cards = [
                f'<article class="capability-card"><h3>{inline(p[0] if p else "")}</h3>'
                f'<p>{inline(p[1] if len(p) > 1 else "")}</p></article>'
                for p in items
            ]
            return '<div class="capability-grid">' + "".join(cards) + "</div>"

        if name == "metrics":
            cards = []
            for p in items:
                value = p[0] if p else ""
                label = p[1] if len(p) > 1 else ""
                note = p[2] if len(p) > 2 else ""
                cards.append(
                    f'<div class="metric"><strong>{inline(value)}</strong><span>{inline(label)}</span>'
                    f'<small>{inline(note)}</small></div>'
                )
            return '<div class="metrics-grid">' + "".join(cards) + "</div>"

        if name == "timeline":
            cards = []
            for p in items:
                date = p[0] if p else ""
                org = p[1] if len(p) > 1 else ""
                body = p[2] if len(p) > 2 else ""
                cards.append(
                    f'<div class="timeline-item"><time>{inline(date)}</time><div><h3>{inline(org)}</h3>'
                    f'<p>{inline(body)}</p></div></div>'
                )
            return '<div class="timeline">' + "".join(cards) + "</div>"

        if name == "links":
            cards = []
            for p in items:
                label = p[0] if p else ""
                url = p[1] if len(p) > 1 else "#"
                desc = p[2] if len(p) > 2 else ""
                ext = url.startswith("http://") or url.startswith("https://")
                attrs2 = ' target="_blank" rel="noopener noreferrer"' if ext else ""
                cards.append(
                    f'<a class="resource-link" href="{html.escape(url, quote=True)}"{attrs2}>'
                    f'<span><strong>{inline(label)}</strong><small>{inline(desc)}</small></span>'
                    '<span class="resource-arrow" aria-hidden="true">↗</span></a>'
                )
            return '<div class="resource-list">' + "".join(cards) + "</div>"

        if name == "steps":
            cards = []
            for idx, p in enumerate(items, 1):
                title = p[0] if p else ""
                body = p[1] if len(p) > 1 else ""
                cards.append(
                    f'<div class="step"><span>{idx:02d}</span><div><h3>{inline(title)}</h3>'
                    f'<p>{inline(body)}</p></div></div>'
                )
            return '<div class="steps">' + "".join(cards) + "</div>"

        if name == "archive":
            cards = []
            for p in items:
                title = p[0] if p else ""
                tool = p[1] if len(p) > 1 else ""
                body = p[2] if len(p) > 2 else ""
                image = p[3] if len(p) > 3 else ""
                media = (
                    f'<img src="{html.escape(image, quote=True)}" alt="" loading="lazy">'
                    if image
                    else '<div class="archive-placeholder" aria-hidden="true">LD</div>'
                )
                cards.append(
                    f'<article class="archive-card"><div class="archive-media">{media}</div>'
                    f'<div class="archive-copy"><span>{inline(tool)}</span><h3>{inline(title)}</h3>'
                    f'<p>{inline(body)}</p></div></article>'
                )
            return '<div class="archive-grid">' + "".join(cards) + "</div>"

    if name == "gallery":
        m = re.search(r"cols=(\d+)", attrs)
        cols = max(1, min(3, int(m.group(1)))) if m else 2
        figures = []
        for line in clean:
            parsed = parse_image_line(line)
            if not parsed:
                continue
            caption, src = parsed
            figures.append(
                f'<figure class="gallery-item"><button class="image-button" type="button" '
                f'data-lightbox-src="{html.escape(src, quote=True)}" '
                f'data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" '
                f'loading="lazy" decoding="async"></button><figcaption>{inline(caption)}</figcaption></figure>'
            )
        return f'<div class="gallery gallery-{cols}">' + "".join(figures) + "</div>"

    if name == "callout":
        title_match = re.search(r'title="([^"]+)"', attrs)
        title = title_match.group(1) if title_match else labels["design_note"]
        return f'<aside class="callout"><span>{inline(title)}</span><p>{inline(" ".join(clean))}</p></aside>'

    if name == "video":
        def attr(key: str, fallback: str = "") -> str:
            match = re.search(rf'{re.escape(key)}="([^"]*)"', attrs)
            return match.group(1).strip() if match else fallback

        platform = attr("platform", "YouTube")
        video_id = attr("id")
        title = attr("title", "Video")
        normalized = platform.lower()
        if video_id and normalized == "youtube":
            src = f"https://www.youtube-nocookie.com/embed/{html.escape(video_id, quote=True)}"
        elif video_id and normalized == "bilibili":
            src = f"https://player.bilibili.com/player.html?bvid={html.escape(video_id, quote=True)}&page=1&high_quality=1"
        else:
            src = ""
        if src:
            return (
                '<div class="video-embed">'
                f'<iframe src="{src}" title="{html.escape(title, quote=True)}" '
                'loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                'gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
                f'<p><strong>{inline(title)}</strong><span>{inline(platform)}</span></p></div>'
            )
        placeholder = "Bilibili 视频接口已预留" if lang == "zh" and normalized == "bilibili" else "YouTube video slot reserved"
        return (
            '<div class="video-placeholder" role="note">'
            f'<span>{inline(platform)}</span><strong>{inline(title)}</strong><p>{inline(placeholder)}</p></div>'
        )

    return ""


def render_markdown(body: str, lang: str) -> Rendered:
    labels = LANGUAGES[lang]["labels"]
    lines = body.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    section_count = 0
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            joined = "\n".join(x.rstrip() for x in paragraph)
            joined = re.sub(r"  \n", "\n", joined).replace("\n", " ")
            out.append(f"<p>{inline(joined)}</p>")
            paragraph = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if stripped.startswith(":::") and stripped != ":::":
            flush_paragraph()
            opening = stripped[3:].strip()
            name, _, attrs = opening.partition(" ")
            inner: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                inner.append(lines[i])
                i += 1
            out.append(render_directive(name, attrs, inner, lang))
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            section_count += 1
            title = stripped[3:].strip()
            sid = slugify(title, f"section-{section_count}")
            toc.append((sid, title))
            out.append(
                f'<h2 id="{sid}">{inline(title)}<a class="heading-anchor" href="#{sid}" '
                f'aria-label="{html.escape(labels["section_link"], quote=True)}">#</a></h2>'
            )
            i += 1
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            title = stripped[4:].strip()
            sid = slugify(title, f"subsection-{section_count}-{i}")
            out.append(f'<h3 id="{sid}">{inline(title)}</h3>')
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines):
            separator = lines[i + 1].strip()
            separator_cells = [cell.strip() for cell in separator.strip("|").split("|")]
            if separator.startswith("|") and separator_cells and all(
                re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells
            ):
                flush_paragraph()

                def table_cells(line: str) -> list[str]:
                    return [cell.strip() for cell in line.strip().strip("|").split("|")]

                header_cells = table_cells(stripped)
                rows: list[list[str]] = []
                i += 2
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append(table_cells(lines[i]))
                    i += 1
                thead = "".join(f"<th scope=\"col\">{inline(cell)}</th>" for cell in header_cells)
                tbody = "".join(
                    "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
                    for row in rows
                )
                out.append(
                    '<div class="data-table-wrap"><table class="data-table"><thead><tr>'
                    + thead
                    + "</tr></thead><tbody>"
                    + tbody
                    + "</tbody></table></div>"
                )
                continue

        if stripped == "---":
            flush_paragraph()
            out.append("<hr>")
            i += 1
            continue

        image = parse_image_line(stripped)
        if image:
            flush_paragraph()
            caption, src = image
            out.append(
                f'<figure class="feature-figure"><button class="image-button" type="button" '
                f'data-lightbox-src="{html.escape(src, quote=True)}" '
                f'data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" '
                f'loading="lazy" decoding="async"></button><figcaption>{inline(caption)}</figcaption></figure>'
            )
            i += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            quote = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f'<blockquote>{inline(" ".join(quote))}</blockquote>')
            continue

        if re.match(r"^-\s+", stripped):
            flush_paragraph()
            items = []
            while i < len(lines) and re.match(r"^-\s+", lines[i].strip()):
                items.append(re.sub(r"^-\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue

        paragraph.append(raw)
        i += 1

    flush_paragraph()
    return Rendered("\n".join(out), toc)


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def portfolio_name(site: dict[str, Any], lang: str, level_design: bool = False) -> str:
    cfg = LANGUAGES[lang]
    label = cfg["level_design_portfolio_label"] if level_design else cfg["portfolio_label"]
    joiner = "" if lang == "zh" else " "
    return f"{site.get('name', '')}{joiner}{label}"


def page_title(title: str, site: dict[str, Any], lang: str, level_design: bool = False) -> str:
    return f"{title}{LANGUAGES[lang]['title_separator']}{portfolio_name(site, lang, level_design)}"


def route(lang: str, path: str) -> str:
    if path.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return path
    if path.startswith("/assets/"):
        return path
    clean = "/" + path.lstrip("/")
    prefix = LANGUAGES[lang]["prefix"]
    if clean == "/":
        return f"{prefix}/" if prefix else "/"
    return f"{prefix}{clean}"


def output_path(lang: str, route_path: str) -> Path:
    prefix = str(LANGUAGES[lang].get("prefix", "")).strip("/")
    base_dir = ROOT / prefix if prefix else ROOT
    if route_path == "/":
        return base_dir / "index.html"
    return base_dir / route_path.strip("/") / "index.html"


def project_url(project: dict[str, Any], lang: str) -> str:
    return route(lang, f"/projects/{project['slug']}/")


def tag_list(tags: list[str] | str) -> str:
    if isinstance(tags, str):
        tags = [x.strip() for x in tags.split(",") if x.strip()]
    return "".join(f"<span>{esc(tag)}</span>" for tag in tags)


def project_card(project: dict[str, Any], lang: str, index: int = 0) -> str:
    labels = LANGUAGES[lang]["labels"]
    url = project_url(project, lang)
    tags = tag_list(project.get("tags", []))
    return f'''
    <article class="project-card reveal" style="--delay:{min(index, 5) * 70}ms">
      <a class="project-card-media" href="{url}" aria-label="{esc(labels['view_project'])} {esc(project['title'])}">
        <img src="{esc(project.get('cover'))}" alt="{esc(project['title'])} {esc(labels['project_cover'])}" loading="lazy" decoding="async">
        <span class="project-index">{index + 1:02d}</span>
      </a>
      <div class="project-card-copy">
        <div class="project-card-kicker">{esc(project.get('kicker'))}</div>
        <h3><a href="{url}">{esc(project['title'])}</a></h3>
        <p>{esc(project.get('summary'))}</p>
        <div class="tag-list">{tags}</div>
        <div class="project-card-meta"><span>{esc(project.get('role'))}</span><span>{esc(project.get('card_note'))}</span></div>
      </div>
    </article>'''


def nav(active: str, site: dict[str, Any], lang: str, route_path: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    links = [
        (labels["home"], route(lang, "/"), "home"),
        (labels["work"], route(lang, "/work/"), "work"),
        (labels["about"], route(lang, "/about/"), "about"),
        (labels["archive"], route(lang, "/archive/"), "archive"),
    ]
    navlinks = "".join(
        f'<a href="{url}" class="{"active" if active == key else ""}"'
        f'{" aria-current=\"page\"" if active == key else ""}>{esc(label)}</a>'
        for label, url, key in links
    )
    zh_url = route("zh", route_path)
    en_url = route("en", route_path)
    language_links = []
    for code, url in (("zh", zh_url), ("en", en_url)):
        current = ' class="active" aria-current="page"' if lang == code else ""
        language_links.append(
            f'<a href="{url}" data-language-link="{code}" lang="{esc(LANGUAGES[code]["html_lang"])}"{current}>'
            f'{esc(LANGUAGES[code]["switch_label"])}</a>'
        )
    language_switch = f'''
    <div class="language-switch" role="group" aria-label="{esc(labels['language'])}">
      {language_links[0]}
      <span aria-hidden="true">/</span>
      {language_links[1]}
    </div>'''
    return f'''
<a class="skip-link" href="#main-content">{esc(labels['skip'])}</a>
<header class="site-header" id="siteHeader">
  <a class="brand" href="{route(lang, '/')}" aria-label="{esc(labels['back_home'])}"><strong>{esc(site.get('brand'))}</strong><span>{esc(site.get('short_role'))}</span></a>
  <nav class="desktop-nav" aria-label="{esc(labels['main_nav'])}">{navlinks}</nav>
  <div class="header-actions">
    {language_switch}
    <a class="header-resume" href="{esc(site.get('resume'))}" target="_blank" rel="noopener noreferrer">{esc(labels['resume'])}</a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobileNav" aria-label="{esc(labels['menu'])}"><span></span><span></span></button>
  </div>
</header>
<nav class="mobile-nav" id="mobileNav" aria-label="{esc(labels['mobile_nav'])}">
  {navlinks}
  <a href="mailto:{esc(site.get('email'))}">{esc(labels['contact'])}</a>
  <div class="mobile-language">{language_switch}</div>
</nav>'''

def footer(site: dict[str, Any], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    social_links = "".join(
        f'<a href="{esc(item.get("url"))}" target="_blank" rel="me noopener noreferrer">{esc(item.get("label"))}</a>'
        for item in site.get("social_links", [])
        if item.get("url")
    )
    start = int(site.get("copyright_start", datetime.now().year))
    year = datetime.now().year
    years = str(year) if start == year else f"{start}–{year}"
    return f'''
<footer class="site-footer">
  <div><strong>{esc(site.get('name'))}</strong><span>{esc(site.get('footer_role'))}</span></div>
  <div class="footer-links">
    <a href="mailto:{esc(site.get('email'))}">{esc(site.get('email'))}</a>
    {social_links}
  </div>
  <small>© {years} {esc(site.get('name'))}. {esc(labels['built'])}</small>
</footer>
<div class="lightbox" id="lightbox" aria-hidden="true" role="dialog" aria-modal="true" aria-label="{esc(labels['image_preview'])}">
  <button class="lightbox-close" type="button" aria-label="{esc(labels['close_preview'])}">×</button>
  <img src="" alt="">
  <p></p>
</div>'''

def base(
    page_title_text: str,
    description: str,
    active: str,
    content: str,
    site: dict[str, Any],
    lang: str,
    route_path: str,
    image: str = "",
    body_class: str = "",
) -> str:
    cfg = LANGUAGES[lang]
    canonical_base = site.get("site_url", "").rstrip("/")
    current_url = canonical_base + route(lang, route_path)
    zh_url = canonical_base + route("zh", route_path)
    en_url = canonical_base + route("en", route_path)
    image = image or site.get("default_og", "")
    image_url = image if str(image).startswith(("http://", "https://")) else canonical_base + str(image)
    body_classes = " ".join(x for x in [body_class, f"lang-{lang}"] if x)
    alternate_locale = LANGUAGES["en" if lang == "zh" else "zh"]["og_locale"]
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site.get("name"),
        "alternateName": site.get("alternate_name"),
        "url": canonical_base + route(lang, "/"),
        "image": canonical_base + site.get("avatar", ""),
        "jobTitle": site.get("role"),
        "email": f"mailto:{site.get('email')}" if site.get("email") else "",
        "sameAs": [item.get("url") for item in site.get("social_links", []) if item.get("url")],
    }
    json_ld = json.dumps(structured_data, ensure_ascii=False, separators=(",", ":"))
    return f'''<!doctype html>
<html lang="{esc(cfg['html_lang'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#111314">
  <meta name="color-scheme" content="light">
  <meta name="author" content="{esc(site.get('name'))}">
  <meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(portfolio_name(site, lang))}">
  <meta property="og:locale" content="{esc(cfg['og_locale'])}">
  <meta property="og:locale:alternate" content="{esc(alternate_locale)}">
  <meta property="og:title" content="{esc(page_title_text)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(current_url)}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(page_title_text)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <link rel="canonical" href="{esc(current_url)}">
  <link rel="alternate" hreflang="zh-CN" href="{esc(zh_url)}">
  <link rel="alternate" hreflang="en" href="{esc(en_url)}">
  <link rel="alternate" hreflang="x-default" href="{esc(zh_url)}">
  <title>{esc(page_title_text)}</title>
  <link rel="icon" href="{esc(site.get('favicon'))}" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script type="application/ld+json">{json_ld}</script>
  <script defer src="/assets/js/main.js"></script>
</head>
<body class="{esc(body_classes)}" data-lang="{esc(lang)}" data-page-route="{esc(route_path)}">
<div class="scroll-progress" id="scrollProgress"></div>
{nav(active, site, lang, route_path)}
{content}
{footer(site, lang)}
</body>
</html>'''

def home_page(meta: dict[str, Any], rendered: Rendered, projects: list[dict[str, Any]], site: dict[str, Any], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    featured = [p for p in projects if p.get("featured")]
    cards = "".join(project_card(p, lang, i) for i, p in enumerate(featured))
    home_data = site.get("homepage", {})
    profile_html = "".join(
        f'<div><span>{esc(item.get("label"))}</span><strong>{"<br>".join(esc(line) for line in item.get("lines", []))}</strong></div>'
        for item in home_data.get("profile", [])
    )
    experience_html = "".join(
        f'<article class="experience-item reveal" style="--delay:{i * 70}ms"><span>{esc(item.get("date"))}</span>'
        f'<h3>{esc(item.get("organization"))}</h3><p>{esc(item.get("description"))}</p></article>'
        for i, item in enumerate(home_data.get("experience", []))
    )
    content = f'''
<main id="main-content">
  <section class="home-hero">
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-main reveal">
      <div class="eyebrow">{esc(meta.get('kicker'))}</div>
      <h1>{esc(meta.get('headline'))}</h1>
      <p>{esc(meta.get('intro'))}</p>
      <div class="hero-actions">
        <a class="button button-primary" href="{route(lang, '/work/')}">{esc(labels['view_selected'])} <span>↗</span></a>
        <a class="button button-secondary" href="{esc(site.get('resume'))}" target="_blank" rel="noopener noreferrer">{esc(labels['download_resume'])}</a>
      </div>
    </div>
    <aside class="hero-profile reveal" style="--delay:120ms">
      <img src="{esc(site.get('avatar'))}" alt="{esc(site.get('name'))} monogram">
      {profile_html}
    </aside>
    <div class="hero-number" aria-hidden="true">LD</div>
  </section>

  <section class="section-shell featured-section" id="featured-work">
    <div class="section-heading reveal"><div><span>{esc(labels['selected_eyebrow'])}</span><h2>{esc(labels['selected_work'])}</h2></div><p>{esc(labels['selected_desc'])}</p></div>
    <div class="project-grid">{cards}</div>
    <div class="section-action"><a href="{route(lang, '/work/')}">{esc(labels['view_all'])} <span>↗</span></a></div>
  </section>

  <section class="design-section">
    <div class="section-shell design-layout">
      <div class="design-title reveal"><span>{esc(labels['approach_eyebrow'])}</span><h2>{labels['approach_title']}</h2></div>
      <div class="article-body home-article reveal" style="--delay:80ms">{rendered.html}</div>
    </div>
  </section>

  <section class="section-shell experience-section">
    <div class="section-heading reveal"><div><span>{esc(labels['experience_eyebrow'])}</span><h2>{esc(labels['experience_title'])}</h2></div><p>{esc(labels['experience_desc'])}</p></div>
    <div class="experience-grid">{experience_html}</div>
  </section>

  <section class="contact-band">
    <div class="section-shell contact-inner reveal">
      <div><span>{esc(labels['open_to'])}</span><h2>{esc(labels['open_opportunities'])}</h2></div>
      <div class="contact-actions"><a href="mailto:{esc(site.get('email'))}" class="button button-light">{esc(labels['send_email'])}</a><button class="copy-email" type="button" data-email="{esc(site.get('email'))}" data-copied-label="{esc(labels['copied'])}">{esc(labels['copy_email'])}</button></div>
    </div>
  </section>
</main>'''
    return base(meta.get("title", portfolio_name(site, lang, True)), site.get("description", ""), "home", content, site, lang, "/", body_class="home-page")

def work_page(projects: list[dict[str, Any]], site: dict[str, Any], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    cards = "".join(project_card(p, lang, i) for i, p in enumerate(projects))
    title = page_title(labels["work"], site, lang, level_design=True)
    content = f'''
<main id="main-content">
  <header class="page-hero section-shell">
    <div class="eyebrow">{esc(labels['work_eyebrow'])}</div>
    <h1>{esc(labels['work_title'])}</h1>
    <p>{esc(labels['work_desc'])}</p>
  </header>
  <section class="section-shell work-list"><div class="project-grid">{cards}</div></section>
</main>'''
    return base(title, site.get("description", ""), "work", content, site, lang, "/work/", body_class="work-page")


def project_page(project: dict[str, Any], rendered: Rendered, projects: list[dict[str, Any]], site: dict[str, Any], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    tags = tag_list(project.get("tags", []))
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    idx = projects.index(project)
    prev_project = projects[idx - 1] if idx > 0 else projects[-1]
    next_project = projects[(idx + 1) % len(projects)]
    route_path = f"/projects/{project['slug']}/"
    project_page_title = page_title(str(project["title"]), site, lang)
    content = f'''
<main class="project-main" id="main-content">
  <header class="project-hero">
    <div class="project-hero-copy section-shell">
      <div class="project-breadcrumb"><a href="{route(lang, '/work/')}">{esc(labels['project'])}</a><span>/</span><span>{esc(project.get('engine'))}</span></div>
      <div class="eyebrow">{esc(project.get('kicker'))}</div>
      <h1>{esc(project.get('title'))}</h1>
      <p class="project-subtitle">{esc(project.get('subtitle'))}</p>
      <p class="project-summary">{esc(project.get('summary'))}</p>
      <div class="tag-list tag-list-large">{tags}</div>
    </div>
    <div class="project-hero-media">
      <img src="{esc(project.get('hero') or project.get('cover'))}" alt="{esc(project.get('title'))} {esc(labels['hero_alt'])}" decoding="async">
    </div>
    <div class="project-specs section-shell">
      <div><span>{esc(labels['role'])}</span><strong>{esc(project.get('role'))}</strong></div>
      <div><span>{esc(labels['engine'])}</span><strong>{esc(project.get('engine'))}</strong></div>
      <div><span>{esc(labels['team'])}</span><strong>{esc(project.get('team'))}</strong></div>
      <div><span>{esc(labels['period'])}</span><strong>{esc(project.get('period'))}</strong></div>
      <div><span>{esc(labels['status'])}</span><strong>{esc(project.get('status'))}</strong></div>
    </div>
  </header>

  <div class="project-content section-shell">
    <aside class="project-toc"><span>{esc(labels['toc'])}</span>{toc}<a class="toc-back" href="#siteHeader">{esc(labels['back_top'])}</a></aside>
    <article class="article-body project-article">{rendered.html}</article>
  </div>

  <nav class="project-pagination section-shell" aria-label="{esc(labels['project_switch'])}">
    <a href="{project_url(prev_project, lang)}"><span>{esc(labels['previous'])}</span><strong>← {esc(prev_project['title'])}</strong></a>
    <a href="{project_url(next_project, lang)}"><span>{esc(labels['next'])}</span><strong>{esc(next_project['title'])} →</strong></a>
  </nav>
</main>'''
    return base(project_page_title, project.get("summary", ""), "work", content, site, lang, route_path, project.get("cover", ""), "project-page")


def standard_page(meta: dict[str, Any], rendered: Rendered, site: dict[str, Any], active: str, lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    route_path = f"/{active}/"
    content = f'''
<main id="main-content">
  <header class="page-hero section-shell">
    <div class="eyebrow">{esc(meta.get('kicker'))}</div>
    <h1>{esc(meta.get('title'))}</h1>
    <p>{esc(meta.get('summary'))}</p>
  </header>
  <div class="standard-content section-shell">
    <aside class="project-toc"><span>{esc(labels['toc'])}</span>{toc}<a class="toc-back" href="#siteHeader">{esc(labels['back_top'])}</a></aside>
    <article class="article-body standard-article">{rendered.html}</article>
  </div>
</main>'''
    return base(page_title(str(meta.get("title", "")), site, lang), meta.get("summary", site.get("description", "")), active, content, site, lang, route_path, body_class=f"{active}-page")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def validate_sources() -> None:
    errors: list[str] = []
    required_identity = {"name", "brand", "role", "short_role", "description", "footer_role"}
    for lang in SUPPORTED_LANGUAGES:
        missing = required_identity - set(SITE_CONFIG.get("identity", {}).get(lang, {}))
        if missing:
            errors.append(f"data/site.json identity.{lang} is missing: {', '.join(sorted(missing))}")
        for page in ("home", "about", "archive"):
            path = CONTENT_DIR / "pages" / f"{page}.{lang}.md"
            if not path.exists():
                errors.append(f"Missing localized page: {path.relative_to(ROOT)}")

    project_root = CONTENT_DIR / "projects"
    project_dirs = [p for p in project_root.iterdir() if p.is_dir() and not p.name.startswith("_")]
    seen_slugs: set[str] = set()
    seen_orders: set[int] = set()
    if not project_dirs:
        errors.append("No project source folders found in content/projects/.")
    for project_dir in project_dirs:
        shared_path = project_dir / "project.json"
        if not shared_path.exists():
            errors.append(f"Missing {shared_path.relative_to(ROOT)}")
            continue
        shared = load_json(shared_path)
        slug = str(shared.get("slug", ""))
        order = shared.get("order")
        if not slug:
            errors.append(f"Missing slug in {shared_path.relative_to(ROOT)}")
        elif slug != project_dir.name:
            errors.append(f"Project folder '{project_dir.name}' must match slug '{slug}'.")
        elif slug in seen_slugs:
            errors.append(f"Duplicate project slug: {slug}")
        seen_slugs.add(slug)
        if not isinstance(order, int):
            errors.append(f"Project order must be an integer in {shared_path.relative_to(ROOT)}")
        elif order in seen_orders:
            errors.append(f"Duplicate project order: {order}")
        else:
            seen_orders.add(order)
        for lang in SUPPORTED_LANGUAGES:
            localized = project_dir / f"{lang}.md"
            if not localized.exists():
                errors.append(f"Missing localized project file: {localized.relative_to(ROOT)}")
        for key in ("cover", "hero"):
            asset = str(shared.get(key, ""))
            if asset.startswith("/assets/") and not (ROOT / asset.lstrip("/")).exists():
                errors.append(f"Missing project {key} asset for {slug}: {asset}")

    if errors:
        raise SystemExit("Source validation failed:\n- " + "\n- ".join(errors))


def load_language(lang: str) -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any], str, dict[str, Any], str, list[tuple[dict[str, Any], str]]]:
    site = site_for_language(lang)
    context = {"site": site}
    pages_dir = CONTENT_DIR / "pages"
    home_meta, home_body = read_md(pages_dir / f"home.{lang}.md", context)
    about_meta, about_body = read_md(pages_dir / f"about.{lang}.md", context)
    archive_meta, archive_body = read_md(pages_dir / f"archive.{lang}.md", context)
    project_records: list[tuple[dict[str, Any], str]] = []
    project_dirs = sorted(p for p in (CONTENT_DIR / "projects").iterdir() if p.is_dir() and not p.name.startswith("_"))
    for project_dir in project_dirs:
        shared = load_json(project_dir / "project.json")
        localized, body = read_md(project_dir / f"{lang}.md", context)
        project_records.append(({**shared, **localized}, body))
    project_records.sort(key=lambda record: int(record[0].get("order", 999)))
    return site, home_meta, home_body, about_meta, about_body, archive_meta, archive_body, project_records


def clean_generated() -> None:
    for directory in ("en", "about", "archive", "work", "projects", "404"):
        target = ROOT / directory
        if target.exists():
            shutil.rmtree(target)
    for filename in ("index.html", "404.html", "sitemap.xml", "robots.txt"):
        target = ROOT / filename
        if target.exists():
            target.unlink()


def main() -> None:
    validate_sources()
    clean_generated()
    localized_sites: dict[str, dict[str, Any]] = {}
    route_paths: list[str] = []

    for lang in SUPPORTED_LANGUAGES:
        site, home_meta, home_body, about_meta, about_body, archive_meta, archive_body, project_records = load_language(lang)
        projects = [record[0] for record in project_records]
        localized_sites[lang] = site

        write(output_path(lang, "/"), home_page(home_meta, render_markdown(home_body, lang), projects, site, lang))
        write(output_path(lang, "/work/"), work_page(projects, site, lang))
        write(output_path(lang, "/about/"), standard_page(about_meta, render_markdown(about_body, lang), site, "about", lang))
        write(output_path(lang, "/archive/"), standard_page(archive_meta, render_markdown(archive_body, lang), site, "archive", lang))

        for meta, body in project_records:
            path = f"/projects/{meta['slug']}/"
            write(output_path(lang, path), project_page(meta, render_markdown(body, lang), projects, site, lang))

        if not route_paths:
            route_paths = ["/", "/work/", "/about/", "/archive/"] + [f"/projects/{p['slug']}/" for p in projects]

    for lang in SUPPORTED_LANGUAGES:
        site = localized_sites[lang]
        labels = LANGUAGES[lang]["labels"]
        home_url = route(lang, "/")
        not_found = f'''<main class="not-found" id="main-content"><div><span>404</span><h1>{esc(labels['not_found_title'])}</h1><p>{esc(labels['not_found_desc'])}</p><a class="button button-primary" href="{home_url}">{esc(labels['return_home'])}</a></div></main>'''
        page = base(page_title(labels["page_not_found"], site, lang), labels["page_not_found"], "", not_found, site, lang, "/404/")
        write(output_path(lang, "/404/"), page)
        if lang == SITE_CONFIG.get("default_language", "zh"):
            write(ROOT / "404.html", page)

    site_url = str(SITE_CONFIG.get("site_url", "")).rstrip("/")
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for path in route_paths:
        alternates = {lang: site_url + route(lang, path) for lang in SUPPORTED_LANGUAGES}
        for lang in SUPPORTED_LANGUAGES:
            sitemap_lines.append("  <url>")
            sitemap_lines.append(f"    <loc>{esc(alternates[lang])}</loc>")
            for alt_lang in SUPPORTED_LANGUAGES:
                hreflang = "zh-CN" if alt_lang == "zh" else "en"
                sitemap_lines.append(f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{esc(alternates[alt_lang])}" />')
            sitemap_lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{esc(alternates["zh"])}" />')
            sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap_lines) + "\n")
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n")
    total = len(route_paths) * len(SUPPORTED_LANGUAGES)
    print(f"Built {total} localized pages from paired bilingual sources.")


if __name__ == "__main__":
    main()
