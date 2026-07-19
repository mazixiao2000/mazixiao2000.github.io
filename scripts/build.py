#!/usr/bin/env python3
"""Build the static portfolio from Markdown files.
Uses only the Python standard library so the site can be rebuilt anywhere.
"""
from __future__ import annotations

import ast
import html
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PROJECTS_DIR = CONTENT / "projects"


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

    # Protect code before escaping.
    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = html.escape(text, quote=False)

    # Images inside text (block images are handled separately).
    image_re = re.compile(r"!\[([^\]]*)\]\(([^\s\)]+)(?:\s+&quot;([^&]*)&quot;)?\)")
    text = image_re.sub(lambda m: stash(
        f'<img class="inline-image" src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'
    ), text)

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


def render_directive(name: str, attrs: str, lines: list[str]) -> str:
    clean = [ln.strip() for ln in lines if ln.strip()]
    if name == "lead":
        body = " ".join(clean)
        return f'<div class="article-lead">{inline(body)}</div>'

    if name in {"capabilities", "metrics", "timeline", "links", "steps", "archive"}:
        items = []
        for ln in clean:
            if not ln.startswith("-"):
                continue
            parts = [x.strip() for x in ln[1:].strip().split("|")]
            items.append(parts)

        if name == "capabilities":
            cards = []
            for p in items:
                title = p[0] if p else ""
                body = p[1] if len(p) > 1 else ""
                cards.append(f'<article class="capability-card"><h3>{inline(title)}</h3><p>{inline(body)}</p></article>')
            return '<div class="capability-grid">' + "".join(cards) + "</div>"

        if name == "metrics":
            cards = []
            for p in items:
                value = p[0] if p else ""
                label = p[1] if len(p) > 1 else ""
                note = p[2] if len(p) > 2 else ""
                cards.append(f'<div class="metric"><strong>{inline(value)}</strong><span>{inline(label)}</span><small>{inline(note)}</small></div>')
            return '<div class="metrics-grid">' + "".join(cards) + "</div>"

        if name == "timeline":
            cards = []
            for p in items:
                date = p[0] if p else ""
                org = p[1] if len(p) > 1 else ""
                body = p[2] if len(p) > 2 else ""
                cards.append(f'<div class="timeline-item"><time>{inline(date)}</time><div><h3>{inline(org)}</h3><p>{inline(body)}</p></div></div>')
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
                cards.append(f'<div class="step"><span>{idx:02d}</span><div><h3>{inline(title)}</h3><p>{inline(body)}</p></div></div>')
            return '<div class="steps">' + "".join(cards) + "</div>"

        if name == "archive":
            cards = []
            for p in items:
                title = p[0] if p else ""
                tool = p[1] if len(p) > 1 else ""
                body = p[2] if len(p) > 2 else ""
                image = p[3] if len(p) > 3 else ""
                media = f'<img src="{html.escape(image, quote=True)}" alt="" loading="lazy">' if image else '<div class="archive-placeholder" aria-hidden="true">LD</div>'
                cards.append(f'<article class="archive-card"><div class="archive-media">{media}</div><div class="archive-copy"><span>{inline(tool)}</span><h3>{inline(title)}</h3><p>{inline(body)}</p></div></article>')
            return '<div class="archive-grid">' + "".join(cards) + "</div>"

    if name == "gallery":
        m = re.search(r"cols=(\d+)", attrs)
        cols = max(1, min(3, int(m.group(1)))) if m else 2
        figs = []
        for ln in clean:
            parsed = parse_image_line(ln)
            if not parsed:
                continue
            caption, src = parsed
            figs.append(
                f'<figure class="gallery-item"><button class="image-button" type="button" data-lightbox-src="{html.escape(src, quote=True)}" data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" loading="lazy"></button>'
                f'<figcaption>{inline(caption)}</figcaption></figure>'
            )
        return f'<div class="gallery gallery-{cols}">' + "".join(figs) + "</div>"

    if name == "callout":
        tm = re.search(r'title="([^"]+)"', attrs)
        title = tm.group(1) if tm else "设计说明"
        body = " ".join(clean)
        return f'<aside class="callout"><span>{inline(title)}</span><p>{inline(body)}</p></aside>'

    return ""


def render_markdown(body: str) -> Rendered:
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
            joined = re.sub(r"  \n", "\n", joined)
            joined = joined.replace("\n", " ")
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
            out.append(render_directive(name, attrs, inner))
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
            out.append(f'<h2 id="{sid}">{inline(title)}<a class="heading-anchor" href="#{sid}" aria-label="链接到本节">#</a></h2>')
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

        img = parse_image_line(stripped)
        if img:
            flush_paragraph()
            caption, src = img
            out.append(
                f'<figure class="feature-figure"><button class="image-button" type="button" data-lightbox-src="{html.escape(src, quote=True)}" data-lightbox-alt="{html.escape(caption, quote=True)}">'
                f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" loading="lazy"></button>'
                f'<figcaption>{inline(caption)}</figcaption></figure>'
            )
            i += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            q = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("> "):
                q.append(lines[i].strip()[2:])
                i += 1
            out.append(f'<blockquote>{inline(" ".join(q))}</blockquote>')
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


def tag_list(tags: list[str] | str) -> str:
    if isinstance(tags, str):
        tags = [x.strip() for x in tags.split(",") if x.strip()]
    return "".join(f"<span>{esc(tag)}</span>" for tag in tags)


def project_url(p: dict[str, Any]) -> str:
    return f"/projects/{p['slug']}/"


def project_card(p: dict[str, Any], index: int = 0) -> str:
    tags = tag_list(p.get("tags", []))
    return f'''
    <article class="project-card reveal" style="--delay:{min(index, 5) * 70}ms">
      <a class="project-card-media" href="{project_url(p)}" aria-label="查看 {esc(p['title'])}">
        <img src="{esc(p.get('cover'))}" alt="{esc(p['title'])} 项目封面">
        <span class="project-index">{index + 1:02d}</span>
      </a>
      <div class="project-card-copy">
        <div class="project-card-kicker">{esc(p.get('kicker'))}</div>
        <h3><a href="{project_url(p)}">{esc(p['title'])}</a></h3>
        <p>{esc(p.get('summary'))}</p>
        <div class="tag-list">{tags}</div>
        <div class="project-card-meta"><span>{esc(p.get('role'))}</span><span>{esc(p.get('card_note'))}</span></div>
      </div>
    </article>'''


def nav(active: str, site: dict[str, Any]) -> str:
    links = [
        ("首页", "/", "home"),
        ("项目", "/work/", "work"),
        ("关于", "/about/", "about"),
        ("归档", "/archive/", "archive"),
    ]
    navlinks = "".join(f'<a href="{url}" class="{"active" if active == key else ""}">{label}</a>' for label, url, key in links)
    return f'''
<header class="site-header" id="siteHeader">
  <a class="brand" href="/" aria-label="返回首页"><strong>MA ZIXIAO</strong><span>{esc(site.get('short_role'))}</span></a>
  <nav class="desktop-nav" aria-label="主导航">{navlinks}</nav>
  <div class="header-actions">
    <a class="header-resume" href="{esc(site.get('resume_cn'))}" target="_blank">简历 PDF</a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobileNav"><span></span><span></span></button>
  </div>
</header>
<nav class="mobile-nav" id="mobileNav" aria-label="移动端导航">{navlinks}<a href="mailto:{esc(site.get('email'))}">联系我</a></nav>'''


def footer(site: dict[str, Any]) -> str:
    return f'''
<footer class="site-footer">
  <div><strong>{esc(site.get('name'))}</strong><span>关卡设计 / 游戏设计 / 原型实现</span></div>
  <div class="footer-links">
    <a href="mailto:{esc(site.get('email'))}">{esc(site.get('email'))}</a>
    <a href="{esc(site.get('linkedin'))}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
    <a href="{esc(site.get('github'))}" target="_blank" rel="noopener noreferrer">GitHub</a>
  </div>
  <small>© 2026 Ma Zixiao. Built from Markdown for GitHub Pages.</small>
</footer>
<div class="lightbox" id="lightbox" aria-hidden="true" role="dialog" aria-label="图片预览">
  <button class="lightbox-close" type="button" aria-label="关闭图片预览">×</button>
  <img src="" alt="">
  <p></p>
</div>'''


def base(page_title: str, description: str, active: str, content: str, site: dict[str, Any], image: str = "/assets/images/decaran-cover.webp", body_class: str = "") -> str:
    canonical = site.get("site_url", "").rstrip("/")
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#111314">
  <meta name="description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{esc(canonical + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <title>{esc(page_title)}</title>
  <link rel="icon" href="/assets/images/avatar-monogram.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script defer src="/assets/js/main.js"></script>
</head>
<body class="{esc(body_class)}">
<div class="scroll-progress" id="scrollProgress"></div>
{nav(active, site)}
{content}
{footer(site)}
</body>
</html>'''


def home_page(meta: dict[str, Any], rendered: Rendered, projects: list[dict[str, Any]], site: dict[str, Any]) -> str:
    featured = [p for p in projects if p.get("featured")]
    cards = "".join(project_card(p, i) for i, p in enumerate(featured))
    content = f'''
<main>
  <section class="home-hero">
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-main reveal">
      <div class="eyebrow">{esc(meta.get('kicker'))}</div>
      <h1>{esc(meta.get('headline'))}</h1>
      <p>{esc(meta.get('intro'))}</p>
      <div class="hero-actions">
        <a class="button button-primary" href="/work/">查看精选项目 <span>↗</span></a>
        <a class="button button-secondary" href="{esc(site.get('resume_cn'))}" target="_blank">下载中文简历</a>
      </div>
    </div>
    <aside class="hero-profile reveal" style="--delay:120ms">
      <img src="/assets/images/avatar-monogram.svg" alt="马子潇姓名缩写图形">
      <div><span>当前身份</span><strong>SMU Guildhall<br>Level Design M.I.T.</strong></div>
      <div><span>经历</span><strong>网易雷火<br>系统策划实习</strong></div>
      <div><span>工具</span><strong>UE5 · Unity · CK<br>Hammer · Radiant</strong></div>
    </aside>
    <div class="hero-number" aria-hidden="true">LD</div>
  </section>

  <section class="section-shell featured-section" id="featured-work">
    <div class="section-heading reveal"><div><span>01 / SELECTED WORK</span><h2>精选项目</h2></div><p>以完整 Case Study 展示我如何定义问题、组织空间、实现机制并通过测试迭代。</p></div>
    <div class="project-grid">{cards}</div>
    <div class="section-action"><a href="/work/">查看全部项目 <span>↗</span></a></div>
  </section>

  <section class="design-section">
    <div class="section-shell design-layout">
      <div class="design-title reveal"><span>02 / APPROACH</span><h2>关卡不是场景堆叠，<br>而是玩家决策的结构。</h2></div>
      <div class="article-body home-article reveal" style="--delay:80ms">{rendered.html}</div>
    </div>
  </section>

  <section class="section-shell experience-section">
    <div class="section-heading reveal"><div><span>03 / EXPERIENCE</span><h2>设计与制作经验</h2></div><p>从独立任务关卡，到 42 人团队项目，再到大型在线游戏实习。</p></div>
    <div class="experience-grid">
      <article class="experience-item reveal"><span>2025—2027</span><h3>SMU Guildhall</h3><p>Digital Game Development · Level Design Track</p></article>
      <article class="experience-item reveal" style="--delay:70ms"><span>2024</span><h3>网易雷火</h3><p>《天谕》手游海外版本 · 系统策划实习</p></article>
      <article class="experience-item reveal" style="--delay:140ms"><span>2021—2025</span><h3>浙江理工大学</h3><p>计算机科学与技术 · 全英班</p></article>
    </div>
  </section>

  <section class="contact-band">
    <div class="section-shell contact-inner reveal">
      <div><span>OPEN TO OPPORTUNITIES</span><h2>寻找关卡设计、游戏设计相关实习与校招机会。</h2></div>
      <div class="contact-actions"><a href="mailto:{esc(site.get('email'))}" class="button button-light">发送邮件</a><button class="copy-email" type="button" data-email="{esc(site.get('email'))}">复制邮箱</button></div>
    </div>
  </section>
</main>'''
    return base(meta.get("title", "作品集"), site.get("description", ""), "home", content, site, body_class="home-page")


def work_page(projects: list[dict[str, Any]], site: dict[str, Any]) -> str:
    cards = "".join(project_card(p, i) for i, p in enumerate(projects))
    content = f'''
<main>
  <header class="page-hero section-shell">
    <div class="eyebrow">WORK / CASE STUDIES</div>
    <h1>项目与设计案例</h1>
    <p>首页优先展示能够清楚说明设计目标、个人职责、制作过程和最终结果的完整项目。</p>
  </header>
  <section class="section-shell work-list"><div class="project-grid">{cards}</div></section>
</main>'''
    return base("项目｜马子潇关卡设计作品集", site.get("description", ""), "work", content, site, body_class="work-page")


def project_page(p: dict[str, Any], rendered: Rendered, projects: list[dict[str, Any]], site: dict[str, Any]) -> str:
    tags = tag_list(p.get("tags", []))
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    idx = projects.index(p)
    prev_p = projects[idx - 1] if idx > 0 else projects[-1]
    next_p = projects[(idx + 1) % len(projects)]
    content = f'''
<main class="project-main">
  <header class="project-hero">
    <div class="project-hero-copy section-shell">
      <div class="project-breadcrumb"><a href="/work/">项目</a><span>/</span><span>{esc(p.get('engine'))}</span></div>
      <div class="eyebrow">{esc(p.get('kicker'))}</div>
      <h1>{esc(p.get('title'))}</h1>
      <p class="project-subtitle">{esc(p.get('subtitle'))}</p>
      <p class="project-summary">{esc(p.get('summary'))}</p>
      <div class="tag-list tag-list-large">{tags}</div>
    </div>
    <div class="project-hero-media">
      <img src="{esc(p.get('hero') or p.get('cover'))}" alt="{esc(p.get('title'))} 项目主视觉">
    </div>
    <div class="project-specs section-shell">
      <div><span>职责</span><strong>{esc(p.get('role'))}</strong></div>
      <div><span>工具</span><strong>{esc(p.get('engine'))}</strong></div>
      <div><span>团队</span><strong>{esc(p.get('team'))}</strong></div>
      <div><span>周期</span><strong>{esc(p.get('period'))}</strong></div>
      <div><span>状态</span><strong>{esc(p.get('status'))}</strong></div>
    </div>
  </header>

  <div class="project-content section-shell">
    <aside class="project-toc"><span>目录</span>{toc}<a class="toc-back" href="#siteHeader">回到顶部 ↑</a></aside>
    <article class="article-body project-article">{rendered.html}</article>
  </div>

  <nav class="project-pagination section-shell" aria-label="项目切换">
    <a href="{project_url(prev_p)}"><span>上一个项目</span><strong>← {esc(prev_p['title'])}</strong></a>
    <a href="{project_url(next_p)}"><span>下一个项目</span><strong>{esc(next_p['title'])} →</strong></a>
  </nav>
</main>'''
    return base(f"{p['title']}｜马子潇作品集", p.get("summary", ""), "work", content, site, p.get("cover", ""), "project-page")


def standard_page(meta: dict[str, Any], rendered: Rendered, site: dict[str, Any], active: str) -> str:
    toc = "".join(f'<a href="#{esc(sid)}">{esc(title)}</a>' for sid, title in rendered.toc)
    content = f'''
<main>
  <header class="page-hero section-shell">
    <div class="eyebrow">{esc(meta.get('kicker'))}</div>
    <h1>{esc(meta.get('title'))}</h1>
    <p>{esc(meta.get('summary'))}</p>
  </header>
  <div class="standard-content section-shell">
    <aside class="project-toc"><span>目录</span>{toc}<a class="toc-back" href="#siteHeader">回到顶部 ↑</a></aside>
    <article class="article-body standard-article">{rendered.html}</article>
  </div>
</main>'''
    return base(f"{meta.get('title')}｜马子潇作品集", meta.get("summary", site.get("description", "")), active, content, site, body_class=f"{active}-page")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def main() -> None:
    site, _ = read_md(CONTENT / "site.md")
    home_meta, home_body = read_md(CONTENT / "home.md")
    about_meta, about_body = read_md(CONTENT / "about.md")
    archive_meta, archive_body = read_md(CONTENT / "archive.md")

    project_records: list[tuple[dict[str, Any], str]] = []
    for path in sorted(PROJECTS_DIR.glob("*.md")):
        meta, body = read_md(path)
        project_records.append((meta, body))
    project_records.sort(key=lambda x: int(x[0].get("order", 999)))
    projects = [x[0] for x in project_records]

    write(ROOT / "index.html", home_page(home_meta, render_markdown(home_body), projects, site))
    write(ROOT / "work" / "index.html", work_page(projects, site))
    write(ROOT / "about" / "index.html", standard_page(about_meta, render_markdown(about_body), site, "about"))
    write(ROOT / "archive" / "index.html", standard_page(archive_meta, render_markdown(archive_body), site, "archive"))

    for meta, body in project_records:
        write(ROOT / "projects" / meta["slug"] / "index.html", project_page(meta, render_markdown(body), projects, site))

    # GitHub Pages-friendly 404 with immediate home navigation.
    write(ROOT / "404.html", base("页面未找到｜马子潇作品集", "页面未找到", "", '<main class="not-found"><div><span>404</span><h1>这个空间还没有被搭建。</h1><p>返回首页继续查看项目。</p><a class="button button-primary" href="/">返回首页</a></div></main>', site))

    # Basic sitemap and robots.
    urls = ["/", "/work/", "/about/", "/archive/"] + [project_url(p) for p in projects]
    base_url = site.get("site_url", "").rstrip("/")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{base_url}{u}</loc></url>" for u in urls) + "\n</urlset>\n"
    write(ROOT / "sitemap.xml", sitemap)
    write(ROOT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")
    print(f"Built {len(projects)} project pages and core site pages in {ROOT}")


if __name__ == "__main__":
    main()
