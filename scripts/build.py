#!/usr/bin/env python3
"""Build the bilingual static portfolio from Markdown files.

The builder intentionally uses only Python's standard library so the site can
be rebuilt on Windows, macOS, or Linux without installing packages.
"""
from __future__ import annotations

import ast
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ZH_CONTENT = ROOT / "content"
EN_CONTENT = ROOT / "content" / "en"

LANGS = {
    "zh": {
        "html_lang": "zh-CN",
        "prefix": "",
        "labels": {
            "home": "首页",
            "personal": "个人项目",
            "team": "团队项目",
            "other": "其他项目",
            "about": "关于",
            "resume": "简历 PDF",
            "contact": "联系方式",
            "current": "当前身份",
            "experience": "经历",
            "tools": "工具",
            "selected": "精选项目",
            "all_projects": "查看全部项目",
            "view_project": "查看项目",
            "contents": "目录",
            "back_top": "回到顶部 ↑",
            "project": "项目",
            "role": "职责",
            "tool": "工具",
            "team_label": "团队",
            "period": "周期",
            "status": "状态",
            "previous": "上一个项目",
            "next": "下一个项目",
            "copy": "复制邮箱",
            "copied": "已复制",
            "send_email": "发送邮件",
            "not_found_title": "这个空间还没有被搭建。",
            "not_found_body": "返回首页继续查看项目。",
            "back_home": "返回首页",
            "individual_note": "独立完成的任务、FPS 与机制关卡，重点展示从概念到可玩实现的完整能力。",
            "team_note": "在跨职能团队中负责核心关卡与玩法模块，强调协作、落地和测试迭代。",
            "other_note": "研究、多人地图、桌游与快速原型，补充展示设计广度与持续探索。",
            "work_title": "项目与设计案例",
            "work_intro": "按个人项目、团队项目与其他项目组织，让招聘者快速确认我的独立制作能力、团队经验与设计广度。",
            "other_cta": "查看完整项目归档",
        },
    },
    "en": {
        "html_lang": "en",
        "prefix": "en",
        "labels": {
            "home": "Home",
            "personal": "Personal",
            "team": "Team",
            "other": "Other Work",
            "about": "About",
            "resume": "Resume PDF",
            "contact": "Contact",
            "current": "Current",
            "experience": "Experience",
            "tools": "Tools",
            "selected": "Selected Work",
            "all_projects": "View All Projects",
            "view_project": "View Case Study",
            "contents": "Contents",
            "back_top": "Back to top ↑",
            "project": "Work",
            "role": "Role",
            "tool": "Tools",
            "team_label": "Team",
            "period": "Duration",
            "status": "Status",
            "previous": "Previous Project",
            "next": "Next Project",
            "copy": "Copy Email",
            "copied": "Copied",
            "send_email": "Email Me",
            "not_found_title": "This space has not been built yet.",
            "not_found_body": "Return home to continue exploring the portfolio.",
            "back_home": "Back Home",
            "individual_note": "Solo quest, FPS, and mechanics-driven levels that demonstrate an end-to-end process from concept to playable implementation.",
            "team_note": "Core levels and gameplay features created within cross-functional teams, emphasizing collaboration, execution, and playtest iteration.",
            "other_note": "Research, multiplayer maps, tabletop design, and rapid prototypes that demonstrate range and continued exploration.",
            "work_title": "Projects & Case Studies",
            "work_intro": "Organized into personal, team, and other work so recruiters can quickly assess my independent execution, collaboration experience, and design range.",
            "other_cta": "View Complete Archive",
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
    """Render a deliberately small, predictable Markdown inline subset."""
    tokens: list[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens)-1}@@"

    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = html.escape(text, quote=False)

    image_re = re.compile(r"!\[([^\]]*)\]\(([^\s\)]+)(?:\s+&quot;([^&]*)&quot;)?\)")
    text = image_re.sub(
        lambda m: stash(
            f'<img class="inline-image" src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'
        ),
        text,
    )

    link_re = re.compile(r"\[([^\]]+)\]\(([^\s\)]+)(?:\s+&quot;([^&]*)&quot;)?\)")

    def link_sub(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        external = url.startswith("http://") or url.startswith("https://")
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
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
    match = re.fullmatch(r"!\[([^\]]*)\]\(([^\s\)]+)(?:\s+\"[^\"]*\")?\)", line.strip())
    return (match.group(1), match.group(2)) if match else None


def render_directive(name: str, attrs: str, lines: list[str], lang: str) -> str:
    clean = [line.strip() for line in lines if line.strip()]
    if name == "lead":
        return f'<div class="article-lead glass-panel">{inline(" ".join(clean))}</div>'

    if name in {"capabilities", "metrics", "timeline", "links", "steps", "archive"}:
        items: list[list[str]] = []
        for line in clean:
            if line.startswith("-"):
                items.append([x.strip() for x in line[1:].strip().split("|")])

        if name == "capabilities":
            cards = [
                f'<article class="capability-card glass-panel"><h3>{inline(p[0] if p else "")}</h3><p>{inline(p[1] if len(p) > 1 else "")}</p></article>'
                for p in items
            ]
            return '<div class="capability-grid">' + "".join(cards) + "</div>"

        if name == "metrics":
            cards = []
            for p in items:
                cards.append(
                    f'<div class="metric glass-panel"><strong>{inline(p[0] if p else "")}</strong>'
                    f'<span>{inline(p[1] if len(p) > 1 else "")}</span>'
                    f'<small>{inline(p[2] if len(p) > 2 else "")}</small></div>'
                )
            return '<div class="metrics-grid">' + "".join(cards) + "</div>"

        if name == "timeline":
            cards = []
            for p in items:
                cards.append(
                    f'<div class="timeline-item glass-panel"><time>{inline(p[0] if p else "")}</time>'
                    f'<div><h3>{inline(p[1] if len(p) > 1 else "")}</h3>'
                    f'<p>{inline(p[2] if len(p) > 2 else "")}</p></div></div>'
                )
            return '<div class="timeline">' + "".join(cards) + "</div>"

        if name == "links":
            cards = []
            for p in items:
                label = p[0] if p else ""
                url = p[1] if len(p) > 1 else "#"
                desc = p[2] if len(p) > 2 else ""
                external = url.startswith("http://") or url.startswith("https://")
                attrs2 = ' target="_blank" rel="noopener noreferrer"' if external else ""
                cards.append(
                    f'<a class="resource-link glass-panel" href="{html.escape(url, quote=True)}"{attrs2}>'
                    f'<span><strong>{inline(label)}</strong><small>{inline(desc)}</small></span>'
                    '<span class="resource-arrow" aria-hidden="true">↗</span></a>'
                )
            return '<div class="resource-list">' + "".join(cards) + "</div>"

        if name == "steps":
            cards = []
            for index, p in enumerate(items, 1):
                cards.append(
                    f'<div class="step glass-panel"><span>{index:02d}</span><div>'
                    f'<h3>{inline(p[0] if p else "")}</h3>'
                    f'<p>{inline(p[1] if len(p) > 1 else "")}</p></div></div>'
                )
            return '<div class="steps">' + "".join(cards) + "</div>"

        if name == "archive":
            return archive_cards_html(items)

    if name == "gallery":
        match = re.search(r"cols=(\d+)", attrs)
        cols = max(1, min(3, int(match.group(1)))) if match else 2
        figures = []
        for line in clean:
            parsed = parse_image_line(line)
            if not parsed:
                continue
            caption, src = parsed
            figures.append(
                f'<figure class="gallery-item glass-panel"><button class="image-button" type="button" '
                f'data-lightbox-src="{html.escape(src, quote=True)}" data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" loading="lazy"></button>'
                f'<figcaption>{inline(caption)}</figcaption></figure>'
            )
        return f'<div class="gallery gallery-{cols}">' + "".join(figures) + "</div>"

    if name == "callout":
        title_match = re.search(r'title="([^"]+)"', attrs)
        title = title_match.group(1) if title_match else ("设计说明" if lang == "zh" else "Design Note")
        return f'<aside class="callout glass-panel"><span>{inline(title)}</span><p>{inline(" ".join(clean))}</p></aside>'

    return ""


def render_markdown(body: str, lang: str) -> Rendered:
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
            anchor_label = "链接到本节" if lang == "zh" else "Link to this section"
            out.append(f'<h2 id="{sid}">{inline(title)}<a class="heading-anchor" href="#{sid}" aria-label="{anchor_label}">#</a></h2>')
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
                f'<figure class="feature-figure glass-panel"><button class="image-button" type="button" '
                f'data-lightbox-src="{html.escape(src, quote=True)}" data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" loading="lazy"></button>'
                f'<figcaption>{inline(caption)}</figcaption></figure>'
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
            out.append(f'<blockquote class="glass-panel">{inline(" ".join(quote))}</blockquote>')
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


def extract_archive_items(body: str) -> list[list[str]]:
    items: list[list[str]] = []
    in_archive = False
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith(":::archive"):
            in_archive = True
            continue
        if in_archive and line == ":::":
            in_archive = False
            continue
        if in_archive and line.startswith("-"):
            items.append([x.strip() for x in line[1:].strip().split("|")])
    return items


def archive_cards_html(items: list[list[str]], limit: int | None = None) -> str:
    cards = []
    for p in items[:limit] if limit else items:
        title = p[0] if p else ""
        tool = p[1] if len(p) > 1 else ""
        body = p[2] if len(p) > 2 else ""
        image = p[3] if len(p) > 3 else ""
        media = (
            f'<img src="{html.escape(image, quote=True)}" alt="" loading="lazy">'
            if image
            else '<div class="archive-placeholder" aria-hidden="true"><span>LD</span></div>'
        )
        cards.append(
            f'<article class="archive-card glass-panel"><div class="archive-media">{media}</div>'
            f'<div class="archive-copy"><span>{inline(tool)}</span><h3>{inline(title)}</h3><p>{inline(body)}</p></div></article>'
        )
    return '<div class="archive-grid">' + "".join(cards) + "</div>"


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def tag_list(tags: list[str] | str) -> str:
    if isinstance(tags, str):
        tags = [x.strip() for x in tags.split(",") if x.strip()]
    return "".join(f"<span>{esc(tag)}</span>" for tag in tags)


def lang_path(route: str, lang: str) -> str:
    route = route if route.startswith("/") else "/" + route
    if lang == "en":
        return "/en/" if route == "/" else "/en" + route
    return route


def project_url(project: dict[str, Any], lang: str) -> str:
    return lang_path(f"/projects/{project['slug']}/", lang)


def project_card(project: dict[str, Any], index: int, lang: str) -> str:
    labels = LANGS[lang]["labels"]
    tags = tag_list(project.get("tags", []))
    return f'''
    <article class="project-card glass-panel reveal" style="--delay:{min(index, 5) * 70}ms">
      <a class="project-card-media" href="{project_url(project, lang)}" aria-label="{esc(labels['view_project'])}: {esc(project['title'])}">
        <img src="{esc(project.get('cover'))}" alt="{esc(project['title'])}">
        <span class="project-index">{index + 1:02d}</span>
        <span class="project-view">{esc(labels['view_project'])} <b>↗</b></span>
      </a>
      <div class="project-card-copy">
        <div class="project-card-kicker">{esc(project.get('kicker'))}</div>
        <h3><a href="{project_url(project, lang)}">{esc(project['title'])}</a></h3>
        <p>{esc(project.get('summary'))}</p>
        <div class="tag-list">{tags}</div>
        <div class="project-card-meta"><span>{esc(project.get('role'))}</span><span>{esc(project.get('card_note'))}</span></div>
      </div>
    </article>'''


def category_section(title: str, eyebrow: str, note: str, projects: list[dict[str, Any]], lang: str, section_id: str) -> str:
    cards = "".join(project_card(project, index, lang) for index, project in enumerate(projects))
    return f'''
<section class="section-shell project-category" id="{section_id}">
  <div class="section-heading reveal">
    <div><span>{esc(eyebrow)}</span><h2>{esc(title)}</h2></div>
    <p>{esc(note)}</p>
  </div>
  <div class="project-grid">{cards}</div>
</section>'''


def nav(active: str, site: dict[str, Any], lang: str, route: str) -> str:
    labels = LANGS[lang]["labels"]
    opposite = "en" if lang == "zh" else "zh"
    links = [
        (labels["home"], lang_path("/", lang), "home"),
        (labels["personal"], lang_path("/work/#personal-projects", lang), "personal"),
        (labels["team"], lang_path("/work/#team-projects", lang), "team"),
        (labels["other"], lang_path("/work/#other-projects", lang), "archive"),
        (labels["about"], lang_path("/about/", lang), "about"),
    ]
    navlinks = "".join(
        f'<a href="{url}" class="{"active" if active == key else ""}">{esc(label)}</a>'
        for label, url, key in links
    )
    resume = site.get("resume_cn") if lang == "zh" else site.get("resume_en")
    alt_url = lang_path(route, opposite)
    return f'''
<header class="site-header glass-panel" id="siteHeader">
  <a class="brand" href="{lang_path('/', lang)}" aria-label="{esc(labels['home'])}">
    <span class="brand-mark">MZ</span><span class="brand-copy"><strong>MA ZIXIAO</strong><small>{esc(site.get('short_role'))}</small></span>
  </a>
  <nav class="desktop-nav" aria-label="Main navigation">{navlinks}</nav>
  <div class="header-actions">
    <a class="contact-chip email-chip" href="mailto:{esc(site.get('email'))}" title="{esc(site.get('email'))}"><span>✉</span><b>{esc(site.get('email'))}</b></a>
    <a class="contact-chip phone-chip" href="tel:{esc(site.get('phone_link'))}" title="{esc(site.get('phone'))}"><span>☎</span><b>{esc(site.get('phone'))}</b></a>
    <div class="language-switch" aria-label="Language">
      <a href="{lang_path(route, 'zh')}" class="{'active' if lang == 'zh' else ''}" lang="zh-CN">中</a>
      <a href="{lang_path(route, 'en')}" class="{'active' if lang == 'en' else ''}" lang="en">EN</a>
    </div>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobileNav"><span></span><span></span></button>
  </div>
</header>
<nav class="mobile-nav glass-panel" id="mobileNav" aria-label="Mobile navigation">
  <div class="mobile-nav-links">{navlinks}</div>
  <div class="mobile-contact">
    <a href="mailto:{esc(site.get('email'))}">{esc(site.get('email'))}</a>
    <a href="tel:{esc(site.get('phone_link'))}">{esc(site.get('phone'))}</a>
    <a href="{esc(resume)}" target="_blank">{esc(labels['resume'])}</a>
    <a href="{esc(alt_url)}">{'English' if lang == 'zh' else '中文'}</a>
  </div>
</nav>'''


def footer(site: dict[str, Any], lang: str) -> str:
    role_line = "关卡设计 / 游戏设计 / 原型实现" if lang == "zh" else "Level Design / Game Design / Prototyping"
    built = "由 Markdown 构建并部署于 GitHub Pages" if lang == "zh" else "Built from Markdown for GitHub Pages"
    return f'''
<footer class="site-footer section-shell glass-panel">
  <div><strong>{esc(site.get('name'))}</strong><span>{role_line}</span></div>
  <div class="footer-links">
    <a href="mailto:{esc(site.get('email'))}">{esc(site.get('email'))}</a>
    <a href="{esc(site.get('linkedin'))}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
    <a href="{esc(site.get('github'))}" target="_blank" rel="noopener noreferrer">GitHub</a>
  </div>
  <small>© 2026 Ma Zixiao · {built}</small>
</footer>
<div class="lightbox" id="lightbox" aria-hidden="true" role="dialog" aria-label="Image preview">
  <button class="lightbox-close glass-panel" type="button" aria-label="Close">×</button><img src="" alt=""><p></p>
</div>'''


def base(
    page_title: str,
    description: str,
    active: str,
    content: str,
    site: dict[str, Any],
    lang: str,
    route: str,
    image: str = "/assets/images/decaran-cover.webp",
    body_class: str = "",
) -> str:
    canonical_base = site.get("site_url", "").rstrip("/")
    canonical = canonical_base + lang_path(route, lang)
    opposite = "en" if lang == "zh" else "zh"
    return f'''<!doctype html>
<html lang="{LANGS[lang]['html_lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#eaf0ff">
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="alternate" hreflang="zh-CN" href="{esc(canonical_base + lang_path(route, 'zh'))}">
  <link rel="alternate" hreflang="en" href="{esc(canonical_base + lang_path(route, 'en'))}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{esc(canonical_base + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <title>{esc(page_title)}</title>
  <link rel="icon" href="/assets/images/avatar-monogram.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script defer src="/assets/js/main.js"></script>
</head>
<body class="{esc(body_class)}" data-lang="{lang}" data-copy-label="{esc(LANGS[lang]['labels']['copied'])}">
<div class="ambient ambient-one" aria-hidden="true"></div><div class="ambient ambient-two" aria-hidden="true"></div><div class="ambient ambient-three" aria-hidden="true"></div>
<div class="noise" aria-hidden="true"></div>
<div class="scroll-progress" id="scrollProgress"></div>
{nav(active, site, lang, route)}
{content}
{footer(site, lang)}
</body>
</html>'''


def home_page(
    meta: dict[str, Any],
    rendered: Rendered,
    projects: list[dict[str, Any]],
    archive_items: list[list[str]],
    site: dict[str, Any],
    lang: str,
) -> str:
    labels = LANGS[lang]["labels"]
    personal = [p for p in projects if p.get("category") == "personal"]
    team = [p for p in projects if p.get("category") == "team"]
    resume = site.get("resume_cn") if lang == "zh" else site.get("resume_en")
    role_current = "SMU Guildhall\nLevel Design M.I.T." if lang == "zh" else "SMU Guildhall\nLevel Design M.I.T."
    exp = "网易雷火\n系统策划实习" if lang == "zh" else "NetEase Leihuo\nSystem Design Intern"
    profile_alt = "马子潇个人照片" if lang == "zh" else "Portrait of Zixiao Ma"
    category_intro = "PROJECT INDEX / 项目分类" if lang == "zh" else "PROJECT INDEX / CATEGORIES"
    category_title = "三类项目，快速了解我的能力结构。" if lang == "zh" else "Three categories, one clear view of my design practice."
    category_cards = f'''
      <a class="category-card glass-panel" href="{lang_path('/work/#personal-projects', lang)}"><span>01</span><h3>{labels['personal']}</h3><p>{labels['individual_note']}</p><b>{len(personal):02d} ↗</b></a>
      <a class="category-card glass-panel" href="{lang_path('/work/#team-projects', lang)}"><span>02</span><h3>{labels['team']}</h3><p>{labels['team_note']}</p><b>{len(team):02d} ↗</b></a>
      <a class="category-card glass-panel" href="{lang_path('/work/#other-projects', lang)}"><span>03</span><h3>{labels['other']}</h3><p>{labels['other_note']}</p><b>{len(archive_items):02d} ↗</b></a>
    '''
    experience_heading = "设计与制作经验" if lang == "zh" else "Education & Experience"
    experience_note = "从独立任务关卡，到 42 人团队项目，再到大型在线游戏实习。" if lang == "zh" else "From solo quest levels and a 42-person team project to live-service game development at NetEase."
    open_heading = "寻找关卡设计、游戏设计相关实习与校招机会。" if lang == "zh" else "Open to level design and game design internship and graduate opportunities."
    content = f'''
<main>
  <section class="home-hero section-shell">
    <div class="hero-main glass-panel reveal">
      <div class="hero-copy">
        <div class="eyebrow">{esc(meta.get('kicker'))}</div>
        <h1>{esc(meta.get('headline'))}</h1>
        <p>{esc(meta.get('intro'))}</p>
        <div class="hero-actions">
          <a class="button button-primary" href="{lang_path('/work/', lang)}">{esc(labels['selected'])} <span>↗</span></a>
          <a class="button button-secondary" href="{esc(resume)}" target="_blank">{esc(labels['resume'])}</a>
        </div>
      </div>
      <aside class="hero-profile">
        <div class="portrait-shell"><img src="{esc(site.get('profile_image'))}" alt="{profile_alt}"></div>
        <div class="profile-name"><strong>{esc(site.get('name'))}</strong><span>{esc(site.get('role'))}</span></div>
        <div class="profile-facts">
          <div><span>{labels['current']}</span><strong>{role_current.replace(chr(10), '<br>')}</strong></div>
          <div><span>{labels['experience']}</span><strong>{exp.replace(chr(10), '<br>')}</strong></div>
          <div><span>{labels['tools']}</span><strong>UE5 · Unity · CK<br>Hammer · Radiant</strong></div>
        </div>
      </aside>
    </div>
  </section>

  <section class="section-shell category-section">
    <div class="section-heading reveal"><div><span>{category_intro}</span><h2>{category_title}</h2></div><p>{esc(labels['work_intro'])}</p></div>
    <div class="category-grid">{category_cards}</div>
  </section>

  {category_section(labels['personal'], '01 / PERSONAL PROJECTS', labels['individual_note'], personal, lang, 'personal-projects')}
  {category_section(labels['team'], '02 / TEAM PROJECTS', labels['team_note'], team, lang, 'team-projects')}

  <section class="section-shell project-category" id="other-projects">
    <div class="section-heading reveal"><div><span>03 / OTHER WORK</span><h2>{esc(labels['other'])}</h2></div><p>{esc(labels['other_note'])}</p></div>
    {archive_cards_html(archive_items, limit=3)}
    <div class="section-action"><a class="glass-link" href="{lang_path('/archive/', lang)}">{esc(labels['other_cta'])} <span>↗</span></a></div>
  </section>

  <section class="section-shell design-section glass-panel">
    <div class="design-layout">
      <div class="design-title reveal"><span>04 / APPROACH</span><h2>{esc(meta.get('approach_title'))}</h2></div>
      <div class="article-body home-article reveal" style="--delay:80ms">{rendered.html}</div>
    </div>
  </section>

  <section class="section-shell experience-section">
    <div class="section-heading reveal"><div><span>05 / EXPERIENCE</span><h2>{experience_heading}</h2></div><p>{experience_note}</p></div>
    <div class="experience-grid">
      <article class="experience-item glass-panel reveal"><span>2025—2027</span><h3>SMU Guildhall</h3><p>Digital Game Development · Level Design Track</p></article>
      <article class="experience-item glass-panel reveal" style="--delay:70ms"><span>2024</span><h3>{'网易雷火' if lang == 'zh' else 'NetEase Leihuo'}</h3><p>{'《天谕》手游海外版本 · 系统策划实习' if lang == 'zh' else 'Revelation Mobile Global · System Design Intern'}</p></article>
      <article class="experience-item glass-panel reveal" style="--delay:140ms"><span>2021—2025</span><h3>{'浙江理工大学' if lang == 'zh' else 'Zhejiang Sci-Tech University'}</h3><p>{'计算机科学与技术 · 全英班' if lang == 'zh' else 'B.Eng. Computer Science and Technology'}</p></article>
    </div>
  </section>

  <section class="section-shell contact-band glass-panel">
    <div class="contact-inner reveal"><div><span>OPEN TO OPPORTUNITIES</span><h2>{open_heading}</h2></div>
    <div class="contact-actions"><a href="mailto:{esc(site.get('email'))}" class="button button-primary">{labels['send_email']}</a><button class="copy-email button button-secondary" type="button" data-email="{esc(site.get('email'))}">{labels['copy']}</button></div></div>
  </section>
</main>'''
    return base(meta.get("title", "Portfolio"), site.get("description", ""), "home", content, site, lang, "/", body_class="home-page")


def work_page(projects: list[dict[str, Any]], archive_items: list[list[str]], site: dict[str, Any], lang: str) -> str:
    labels = LANGS[lang]["labels"]
    personal = [p for p in projects if p.get("category") == "personal"]
    team = [p for p in projects if p.get("category") == "team"]
    content = f'''
<main>
  <header class="page-hero section-shell glass-panel reveal">
    <div class="eyebrow">WORK / CASE STUDIES</div><h1>{labels['work_title']}</h1><p>{labels['work_intro']}</p>
    <div class="page-tabs"><a href="#personal-projects">{labels['personal']} <b>{len(personal):02d}</b></a><a href="#team-projects">{labels['team']} <b>{len(team):02d}</b></a><a href="#other-projects">{labels['other']} <b>{len(archive_items):02d}</b></a></div>
  </header>
  {category_section(labels['personal'], '01 / PERSONAL PROJECTS', labels['individual_note'], personal, lang, 'personal-projects')}
  {category_section(labels['team'], '02 / TEAM PROJECTS', labels['team_note'], team, lang, 'team-projects')}
  <section class="section-shell project-category" id="other-projects"><div class="section-heading reveal"><div><span>03 / OTHER WORK</span><h2>{labels['other']}</h2></div><p>{labels['other_note']}</p></div>{archive_cards_html(archive_items)}</section>
</main>'''
    title = "项目｜马子潇关卡设计作品集" if lang == "zh" else "Work | Zixiao Ma Level Design Portfolio"
    return base(title, site.get("description", ""), "work", content, site, lang, "/work/", body_class="work-page")


def project_page(project: dict[str, Any], rendered: Rendered, projects: list[dict[str, Any]], site: dict[str, Any], lang: str) -> str:
    labels = LANGS[lang]["labels"]
    tags = tag_list(project.get("tags", []))
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    index = projects.index(project)
    previous = projects[index - 1] if index > 0 else projects[-1]
    next_project = projects[(index + 1) % len(projects)]
    route = f"/projects/{project['slug']}/"
    content = f'''
<main class="project-main">
  <header class="project-hero section-shell glass-panel reveal">
    <div class="project-hero-copy">
      <div class="project-breadcrumb"><a href="{lang_path('/work/', lang)}">{labels['project']}</a><span>/</span><span>{esc(project.get('engine'))}</span></div>
      <div class="eyebrow">{esc(project.get('kicker'))}</div><h1>{esc(project.get('title'))}</h1>
      <p class="project-subtitle">{esc(project.get('subtitle'))}</p><p class="project-summary">{esc(project.get('summary'))}</p>
      <div class="tag-list tag-list-large">{tags}</div>
    </div>
    <div class="project-hero-media"><img src="{esc(project.get('hero') or project.get('cover'))}" alt="{esc(project.get('title'))}"></div>
    <div class="project-specs">
      <div><span>{labels['role']}</span><strong>{esc(project.get('role'))}</strong></div><div><span>{labels['tool']}</span><strong>{esc(project.get('engine'))}</strong></div>
      <div><span>{labels['team_label']}</span><strong>{esc(project.get('team'))}</strong></div><div><span>{labels['period']}</span><strong>{esc(project.get('period'))}</strong></div><div><span>{labels['status']}</span><strong>{esc(project.get('status'))}</strong></div>
    </div>
  </header>
  <div class="project-content section-shell">
    <aside class="project-toc glass-panel"><span>{labels['contents']}</span>{toc}<a class="toc-back" href="#siteHeader">{labels['back_top']}</a></aside>
    <article class="article-body project-article glass-panel">{rendered.html}</article>
  </div>
  <nav class="project-pagination section-shell" aria-label="Project navigation">
    <a class="glass-panel" href="{project_url(previous, lang)}"><span>{labels['previous']}</span><strong>← {esc(previous['title'])}</strong></a>
    <a class="glass-panel" href="{project_url(next_project, lang)}"><span>{labels['next']}</span><strong>{esc(next_project['title'])} →</strong></a>
  </nav>
</main>'''
    title = f"{project['title']}｜马子潇作品集" if lang == "zh" else f"{project['title']} | Zixiao Ma Portfolio"
    return base(title, project.get("summary", ""), "work", content, site, lang, route, project.get("cover", ""), "project-page")


def standard_page(meta: dict[str, Any], rendered: Rendered, site: dict[str, Any], active: str, lang: str, route: str) -> str:
    labels = LANGS[lang]["labels"]
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    content = f'''
<main>
  <header class="page-hero section-shell glass-panel reveal"><div class="eyebrow">{esc(meta.get('kicker'))}</div><h1>{esc(meta.get('title'))}</h1><p>{esc(meta.get('summary'))}</p></header>
  <div class="standard-content section-shell"><aside class="project-toc glass-panel"><span>{labels['contents']}</span>{toc}<a class="toc-back" href="#siteHeader">{labels['back_top']}</a></aside><article class="article-body standard-article glass-panel">{rendered.html}</article></div>
</main>'''
    title = f"{meta.get('title')}｜马子潇作品集" if lang == "zh" else f"{meta.get('title')} | Zixiao Ma Portfolio"
    return base(title, meta.get("summary", site.get("description", "")), active, content, site, lang, route, body_class=f"{active}-page")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def build_language(content_dir: Path, lang: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    site, _ = read_md(content_dir / "site.md")
    home_meta, home_body = read_md(content_dir / "home.md")
    about_meta, about_body = read_md(content_dir / "about.md")
    archive_meta, archive_body = read_md(content_dir / "archive.md")

    records: list[tuple[dict[str, Any], str]] = []
    for path in sorted((content_dir / "projects").glob("*.md")):
        records.append(read_md(path))
    records.sort(key=lambda item: int(item[0].get("order", 999)))
    projects = [item[0] for item in records]
    archive_items = extract_archive_items(archive_body)

    output_root = ROOT if lang == "zh" else ROOT / "en"
    write(output_root / "index.html", home_page(home_meta, render_markdown(home_body, lang), projects, archive_items, site, lang))
    write(output_root / "work" / "index.html", work_page(projects, archive_items, site, lang))
    write(output_root / "about" / "index.html", standard_page(about_meta, render_markdown(about_body, lang), site, "about", lang, "/about/"))
    write(output_root / "archive" / "index.html", standard_page(archive_meta, render_markdown(archive_body, lang), site, "archive", lang, "/archive/"))
    for meta, body in records:
        write(output_root / "projects" / meta["slug"] / "index.html", project_page(meta, render_markdown(body, lang), projects, site, lang))

    labels = LANGS[lang]["labels"]
    not_found = f'<main class="not-found section-shell"><div class="glass-panel"><span>404</span><h1>{labels["not_found_title"]}</h1><p>{labels["not_found_body"]}</p><a class="button button-primary" href="{lang_path("/", lang)}">{labels["back_home"]}</a></div></main>'
    write(output_root / "404.html", base("404", labels["not_found_body"], "", not_found, site, lang, "/404.html"))

    urls = [lang_path("/", lang), lang_path("/work/", lang), lang_path("/about/", lang), lang_path("/archive/", lang)]
    urls.extend(project_url(project, lang) for project in projects)
    return site, projects, urls


def main() -> None:
    zh_site, zh_projects, zh_urls = build_language(ZH_CONTENT, "zh")
    en_site, en_projects, en_urls = build_language(EN_CONTENT, "en")
    all_urls = zh_urls + en_urls
    base_url = zh_site.get("site_url", "").rstrip("/")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f"  <url><loc>{base_url}{url}</loc></url>" for url in all_urls
    ) + "\n</urlset>\n"
    write(ROOT / "sitemap.xml", sitemap)
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")
    print(f"Built {len(zh_projects)} Chinese and {len(en_projects)} English project pages in {ROOT}")


if __name__ == "__main__":
    main()
