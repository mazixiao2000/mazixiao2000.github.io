#!/usr/bin/env python3
"""Build the bilingual static portfolio from Markdown files.

The Chinese site is generated at the repository root. The English site is
mirrored under /en/. Only the Python standard library is required.
"""
from __future__ import annotations

import ast
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

LANGUAGES: dict[str, dict[str, Any]] = {
    "zh": {
        "content": ROOT / "content",
        "prefix": "",
        "html_lang": "zh-CN",
        "og_locale": "zh_CN",
        "labels": {
            "skip": "跳到主要内容",
            "home": "首页",
            "work": "项目",
            "about": "关于",
            "archive": "归档",
            "main_nav": "主导航",
            "mobile_nav": "移动端导航",
            "back_home": "返回首页",
            "resume": "简历 PDF",
            "contact": "联系我",
            "language": "语言切换",
            "menu": "打开导航菜单",
            "view_project": "查看",
            "project_cover": "项目封面",
            "view_selected": "查看精选项目",
            "download_resume": "下载中文简历",
            "current_identity": "当前身份",
            "experience": "经历",
            "tools": "工具",
            "selected_work": "精选项目",
            "selected_desc": "以完整 Case Study 展示我如何定义问题、组织空间、实现机制并通过测试迭代。",
            "view_all": "查看全部项目",
            "approach_title": "关卡不是场景堆叠，<br>而是玩家决策的结构。",
            "experience_title": "设计与制作经验",
            "experience_desc": "从独立任务关卡，到 42 人团队项目，再到大型在线游戏实习。",
            "open_opportunities": "寻找关卡设计、游戏设计相关实习与校招机会。",
            "send_email": "发送邮件",
            "copy_email": "复制邮箱",
            "copied": "已复制",
            "work_title": "项目与设计案例",
            "work_desc": "首页优先展示能够清楚说明设计目标、个人职责、制作过程和最终结果的完整项目。",
            "project": "项目",
            "role": "职责",
            "engine": "工具",
            "team": "团队",
            "period": "周期",
            "status": "状态",
            "toc": "目录",
            "back_top": "回到顶部 ↑",
            "previous": "上一个项目",
            "next": "下一个项目",
            "section_link": "链接到本节",
            "design_note": "设计说明",
            "image_preview": "图片预览",
            "close_preview": "关闭图片预览",
            "not_found_title": "这个空间还没有被搭建。",
            "not_found_desc": "返回首页继续查看项目。",
            "return_home": "返回首页",
            "footer_role": "关卡设计 / 游戏设计 / 原型实现",
            "built": "基于 Markdown 构建并部署于 GitHub Pages。",
            "project_switch": "项目切换",
            "hero_alt": "项目主视觉",
        },
    },
    "en": {
        "content": ROOT / "content_en",
        "prefix": "/en",
        "html_lang": "en",
        "og_locale": "en_US",
        "labels": {
            "skip": "Skip to main content",
            "home": "Home",
            "work": "Work",
            "about": "About",
            "archive": "Archive",
            "main_nav": "Primary navigation",
            "mobile_nav": "Mobile navigation",
            "back_home": "Back to homepage",
            "resume": "Resume PDF",
            "contact": "Contact",
            "language": "Language selector",
            "menu": "Open navigation menu",
            "view_project": "View",
            "project_cover": "project cover",
            "view_selected": "View Selected Work",
            "download_resume": "Download Resume",
            "current_identity": "Current",
            "experience": "Experience",
            "tools": "Tools",
            "selected_work": "Selected Work",
            "selected_desc": "Complete case studies showing how I define problems, structure spaces, implement mechanics, and iterate through playtesting.",
            "view_all": "View All Projects",
            "approach_title": "A level is not a collection of spaces.<br>It is a structure for player decisions.",
            "experience_title": "Design & Production Experience",
            "experience_desc": "From solo quest levels and small-team prototypes to a 42-person production and a live-service game internship.",
            "open_opportunities": "Open to level design and game design internships and graduate opportunities.",
            "send_email": "Send Email",
            "copy_email": "Copy Email",
            "copied": "Copied",
            "work_title": "Projects & Case Studies",
            "work_desc": "The primary portfolio focuses on projects that clearly communicate the design goal, personal ownership, development process, and final result.",
            "project": "Work",
            "role": "Role",
            "engine": "Tools",
            "team": "Team",
            "period": "Duration",
            "status": "Status",
            "toc": "Contents",
            "back_top": "Back to Top ↑",
            "previous": "Previous Project",
            "next": "Next Project",
            "section_link": "Link to this section",
            "design_note": "Design Note",
            "image_preview": "Image preview",
            "close_preview": "Close image preview",
            "not_found_title": "This space has not been built yet.",
            "not_found_desc": "Return home to continue exploring the portfolio.",
            "return_home": "Return Home",
            "footer_role": "Level Design / Game Design / Prototyping",
            "built": "Built from Markdown for GitHub Pages.",
            "project_switch": "Project navigation",
            "hero_alt": "project hero image",
        },
    },
}


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


def read_md(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
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
    base_dir = ROOT / "en" if lang == "en" else ROOT
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
        f'<a href="{url}" class="{"active" if active == key else ""}">{label}</a>'
        for label, url, key in links
    )
    zh_url = route("zh", route_path)
    en_url = route("en", route_path)
    resume = site.get("resume_en") if lang == "en" else site.get("resume_cn")
    language_switch = f'''
    <div class="language-switch" role="group" aria-label="{esc(labels['language'])}">
      <a href="{zh_url}" data-language-link="zh" lang="zh-CN" class="{'active' if lang == 'zh' else ''}" aria-current="{'true' if lang == 'zh' else 'false'}">中</a>
      <span aria-hidden="true">/</span>
      <a href="{en_url}" data-language-link="en" lang="en" class="{'active' if lang == 'en' else ''}" aria-current="{'true' if lang == 'en' else 'false'}">EN</a>
    </div>'''
    return f'''
<a class="skip-link" href="#main-content">{esc(labels['skip'])}</a>
<header class="site-header" id="siteHeader">
  <a class="brand" href="{route(lang, '/')}" aria-label="{esc(labels['back_home'])}"><strong>MA ZIXIAO</strong><span>{esc(site.get('short_role'))}</span></a>
  <nav class="desktop-nav" aria-label="{esc(labels['main_nav'])}">{navlinks}</nav>
  <div class="header-actions">
    {language_switch}
    <a class="header-resume" href="{esc(resume)}" target="_blank" rel="noopener noreferrer">{esc(labels['resume'])}</a>
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
    return f'''
<footer class="site-footer">
  <div><strong>{esc(site.get('name'))}</strong><span>{esc(labels['footer_role'])}</span></div>
  <div class="footer-links">
    <a href="mailto:{esc(site.get('email'))}">{esc(site.get('email'))}</a>
    <a href="{esc(site.get('linkedin'))}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
    <a href="{esc(site.get('github'))}" target="_blank" rel="noopener noreferrer">GitHub</a>
  </div>
  <small>© 2026 Ma Zixiao. {esc(labels['built'])}</small>
</footer>
<div class="lightbox" id="lightbox" aria-hidden="true" role="dialog" aria-modal="true" aria-label="{esc(labels['image_preview'])}">
  <button class="lightbox-close" type="button" aria-label="{esc(labels['close_preview'])}">×</button>
  <img src="" alt="">
  <p></p>
</div>'''


def base(
    page_title: str,
    description: str,
    active: str,
    content: str,
    site: dict[str, Any],
    lang: str,
    route_path: str,
    image: str = "/assets/images/decaran-cover.webp",
    body_class: str = "",
) -> str:
    cfg = LANGUAGES[lang]
    canonical_base = site.get("site_url", "").rstrip("/")
    current_url = canonical_base + route(lang, route_path)
    zh_url = canonical_base + route("zh", route_path)
    en_url = canonical_base + route("en", route_path)
    body_classes = " ".join(x for x in [body_class, f"lang-{lang}"] if x)
    return f'''<!doctype html>
<html lang="{esc(cfg['html_lang'])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#111314">
  <meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{esc(cfg['og_locale'])}">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(current_url)}">
  <meta property="og:image" content="{esc(canonical_base + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{esc(current_url)}">
  <link rel="alternate" hreflang="zh-CN" href="{esc(zh_url)}">
  <link rel="alternate" hreflang="en" href="{esc(en_url)}">
  <link rel="alternate" hreflang="x-default" href="{esc(zh_url)}">
  <title>{esc(page_title)}</title>
  <link rel="icon" href="/assets/images/avatar-monogram.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script defer src="/assets/js/main.js"></script>
</head>
<body class="{esc(body_classes)}" data-lang="{esc(lang)}">
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
    if lang == "zh":
        profile = [
            (labels["current_identity"], "SMU Guildhall<br>Level Design M.I.T."),
            (labels["experience"], "网易雷火<br>系统策划实习"),
            (labels["tools"], "UE5 · Unity · CK<br>Hammer · Radiant"),
        ]
        experience = [
            ("2025—2027", "SMU Guildhall", "Digital Game Development · Level Design Track"),
            ("2024", "网易雷火", "《天谕》手游海外版本 · 系统策划实习"),
            ("2021—2025", "浙江理工大学", "计算机科学与技术 · 全英班"),
        ]
    else:
        profile = [
            (labels["current_identity"], "SMU Guildhall<br>Level Design M.I.T."),
            (labels["experience"], "NetEase Games<br>Systems Design Intern"),
            (labels["tools"], "UE5 · Unity · CK<br>Hammer · Radiant"),
        ]
        experience = [
            ("2025—2027", "SMU Guildhall", "Digital Game Development · Level Design Track"),
            ("2024", "NetEase Games", "Revelation Mobile Overseas · Systems Design Internship"),
            ("2021—2025", "Zhejiang Sci-Tech University", "Computer Science and Technology · English-Taught Program"),
        ]
    profile_html = "".join(f"<div><span>{esc(a)}</span><strong>{b}</strong></div>" for a, b in profile)
    experience_html = "".join(
        f'<article class="experience-item reveal" style="--delay:{i * 70}ms"><span>{esc(date)}</span>'
        f'<h3>{esc(org)}</h3><p>{esc(desc)}</p></article>'
        for i, (date, org, desc) in enumerate(experience)
    )
    resume = site.get("resume_en") if lang == "en" else site.get("resume_cn")
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
        <a class="button button-secondary" href="{esc(resume)}" target="_blank" rel="noopener noreferrer">{esc(labels['download_resume'])}</a>
      </div>
    </div>
    <aside class="hero-profile reveal" style="--delay:120ms">
      <img src="/assets/images/avatar-monogram.svg" alt="MA monogram">
      {profile_html}
    </aside>
    <div class="hero-number" aria-hidden="true">LD</div>
  </section>

  <section class="section-shell featured-section" id="featured-work">
    <div class="section-heading reveal"><div><span>01 / SELECTED WORK</span><h2>{esc(labels['selected_work'])}</h2></div><p>{esc(labels['selected_desc'])}</p></div>
    <div class="project-grid">{cards}</div>
    <div class="section-action"><a href="{route(lang, '/work/')}">{esc(labels['view_all'])} <span>↗</span></a></div>
  </section>

  <section class="design-section">
    <div class="section-shell design-layout">
      <div class="design-title reveal"><span>02 / APPROACH</span><h2>{labels['approach_title']}</h2></div>
      <div class="article-body home-article reveal" style="--delay:80ms">{rendered.html}</div>
    </div>
  </section>

  <section class="section-shell experience-section">
    <div class="section-heading reveal"><div><span>03 / EXPERIENCE</span><h2>{esc(labels['experience_title'])}</h2></div><p>{esc(labels['experience_desc'])}</p></div>
    <div class="experience-grid">{experience_html}</div>
  </section>

  <section class="contact-band">
    <div class="section-shell contact-inner reveal">
      <div><span>OPEN TO OPPORTUNITIES</span><h2>{esc(labels['open_opportunities'])}</h2></div>
      <div class="contact-actions"><a href="mailto:{esc(site.get('email'))}" class="button button-light">{esc(labels['send_email'])}</a><button class="copy-email" type="button" data-email="{esc(site.get('email'))}" data-copied-label="{esc(labels['copied'])}">{esc(labels['copy_email'])}</button></div>
    </div>
  </section>
</main>'''
    return base(meta.get("title", "Portfolio"), site.get("description", ""), "home", content, site, lang, "/", body_class="home-page")


def work_page(projects: list[dict[str, Any]], site: dict[str, Any], lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    cards = "".join(project_card(p, lang, i) for i, p in enumerate(projects))
    title = "项目｜马子潇关卡设计作品集" if lang == "zh" else "Work | Zixiao Ma Level Design Portfolio"
    content = f'''
<main id="main-content">
  <header class="page-hero section-shell">
    <div class="eyebrow">WORK / CASE STUDIES</div>
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
    page_title = f"{project['title']}｜马子潇作品集" if lang == "zh" else f"{project['title']} | Zixiao Ma Portfolio"
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
    return base(page_title, project.get("summary", ""), "work", content, site, lang, route_path, project.get("cover", ""), "project-page")


def standard_page(meta: dict[str, Any], rendered: Rendered, site: dict[str, Any], active: str, lang: str) -> str:
    labels = LANGUAGES[lang]["labels"]
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    route_path = f"/{active}/"
    suffix = "马子潇作品集" if lang == "zh" else "Zixiao Ma Portfolio"
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
    return base(f"{meta.get('title')}｜{suffix}" if lang == "zh" else f"{meta.get('title')} | {suffix}", meta.get("summary", site.get("description", "")), active, content, site, lang, route_path, body_class=f"{active}-page")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def load_language(lang: str) -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any], str, dict[str, Any], str, list[tuple[dict[str, Any], str]]]:
    content_dir: Path = LANGUAGES[lang]["content"]
    site, _ = read_md(content_dir / "site.md")
    home_meta, home_body = read_md(content_dir / "home.md")
    about_meta, about_body = read_md(content_dir / "about.md")
    archive_meta, archive_body = read_md(content_dir / "archive.md")
    project_records: list[tuple[dict[str, Any], str]] = []
    for path in sorted((content_dir / "projects").glob("*.md")):
        project_records.append(read_md(path))
    project_records.sort(key=lambda record: int(record[0].get("order", 999)))
    return site, home_meta, home_body, about_meta, about_body, archive_meta, archive_body, project_records


def main() -> None:
    all_urls: list[str] = []
    site_url = ""

    for lang in ("zh", "en"):
        site, home_meta, home_body, about_meta, about_body, archive_meta, archive_body, project_records = load_language(lang)
        site_url = site.get("site_url", "").rstrip("/") or site_url
        projects = [record[0] for record in project_records]

        write(output_path(lang, "/"), home_page(home_meta, render_markdown(home_body, lang), projects, site, lang))
        write(output_path(lang, "/work/"), work_page(projects, site, lang))
        write(output_path(lang, "/about/"), standard_page(about_meta, render_markdown(about_body, lang), site, "about", lang))
        write(output_path(lang, "/archive/"), standard_page(archive_meta, render_markdown(archive_body, lang), site, "archive", lang))

        for meta, body in project_records:
            path = f"/projects/{meta['slug']}/"
            write(output_path(lang, path), project_page(meta, render_markdown(body, lang), projects, site, lang))

        routes = ["/", "/work/", "/about/", "/archive/"] + [f"/projects/{p['slug']}/" for p in projects]
        all_urls.extend(route(lang, item) for item in routes)

    zh_site, *_ = load_language("zh")
    en_site, *_ = load_language("en")
    zh_labels = LANGUAGES["zh"]["labels"]
    en_labels = LANGUAGES["en"]["labels"]
    zh_not_found = f'''<main class="not-found" id="main-content"><div><span>404</span><h1>{esc(zh_labels['not_found_title'])}</h1><p>{esc(zh_labels['not_found_desc'])}</p><a class="button button-primary" href="/">{esc(zh_labels['return_home'])}</a></div></main>'''
    en_not_found = f'''<main class="not-found" id="main-content"><div><span>404</span><h1>{esc(en_labels['not_found_title'])}</h1><p>{esc(en_labels['not_found_desc'])}</p><a class="button button-primary" href="/en/">{esc(en_labels['return_home'])}</a></div></main>'''
    zh_404 = base("页面未找到｜马子潇作品集", "页面未找到", "", zh_not_found, zh_site, "zh", "/404/")
    en_404 = base("Page Not Found | Zixiao Ma Portfolio", "Page not found", "", en_not_found, en_site, "en", "/404/")
    write(ROOT / "404.html", zh_404)
    write(output_path("zh", "/404/"), zh_404)
    write(output_path("en", "/404/"), en_404)

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(f"  <url><loc>{site_url}{url}</loc></url>" for url in all_urls)
    sitemap += "\n</urlset>\n"
    write(ROOT / "sitemap.xml", sitemap)
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n")
    print(f"Built {len(all_urls)} localized pages across Chinese and English.")


if __name__ == "__main__":
    main()
