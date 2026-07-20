#!/usr/bin/env python3
"""Create paired Chinese and English Markdown files for a new project."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "content" / "projects"

ZH_TEMPLATE = """---
layout: project
title: 项目名称
subtitle: 项目类型与一句话定位
kicker: LEVEL DESIGN / ENGINE
summary: 一句话说明体验目标、你的职责和结果。
engine: Unreal Engine 5
role: 关卡设计
team: 单人项目
period: 8 周
status: 进行中
tags: [关卡设计, 玩家引导, 测试迭代]
card_note: 首页项目卡片补充说明
---

## 设计目标

说明你要解决的玩家体验问题。

## 我的职责

说明个人负责范围、制作过程与跨职能协作。

## 迭代与结果

说明测试发现、设计调整与最终成果。
"""

EN_TEMPLATE = """---
layout: project
title: Project Title
subtitle: Project type and one-line positioning
kicker: LEVEL DESIGN / ENGINE
summary: Summarize the experience goal, your ownership, and the outcome in one sentence.
engine: Unreal Engine 5
role: Level Design
team: Solo Project
period: 8 Weeks
status: In Progress
tags: [Level Design, Player Guidance, Playtesting]
card_note: Supplemental copy for the project card
---

## Design Goal

Explain the player-experience problem you set out to solve.

## Responsibilities

Clarify your ownership, implementation work, and cross-disciplinary collaboration.

## Iteration & Outcome

Describe playtest findings, design changes, and the final result.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Lowercase URL slug, for example: new-fps-level")
    parser.add_argument("--order", type=int, default=99, help="Display order; lower numbers appear first")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        parser.error("slug must use lowercase letters, numbers, and single hyphens")

    destination = PROJECT_ROOT / args.slug
    if destination.exists():
        parser.error(f"project already exists: {destination.relative_to(ROOT)}")

    destination.mkdir(parents=True)
    shared = {
        "slug": args.slug,
        "cover": f"/assets/images/{args.slug}-cover.webp",
        "hero": f"/assets/images/{args.slug}-hero.webp",
        "featured": False,
        "order": args.order,
    }
    (destination / "project.json").write_text(json.dumps(shared, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destination / "zh.md").write_text(ZH_TEMPLATE, encoding="utf-8")
    (destination / "en.md").write_text(EN_TEMPLATE, encoding="utf-8")
    print(f"Created {destination.relative_to(ROOT)} with paired bilingual content.")


if __name__ == "__main__":
    main()
