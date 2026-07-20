# 双语 Markdown 内容编辑指南

## 1. 中英文文件必须成对维护

中文内容放在 `content/`，英文内容放在 `content_en/`。两边目录结构保持一致：

```text
content/projects/decaran.md
content_en/projects/decaran.md
```

两个版本必须使用相同的：

- 文件名
- `slug`
- `order`
- 图片与文档路径

文字、标签、职责、摘要等内容分别使用对应语言。

## 2. 项目基础信息

每个项目文件开头的 `---` 区域是项目元数据：

```md
---
layout: project
slug: project-name
title: 项目名称
subtitle: 项目副标题
kicker: LEVEL DESIGN / ENGINE
summary: 一句话说明项目的体验目标和你的贡献。
cover: /assets/images/project-cover.webp
hero: /assets/images/project-hero.webp
engine: Unreal Engine 5
role: 关卡设计师
team: 4 人团队
period: 8 周
status: 完成
featured: true
order: 1
tags: [关卡设计, 战斗设计, 玩家引导]
card_note: 首页卡片底部的补充信息
---
```

- `featured: true`：显示在首页。
- `order`：数字越小，显示越靠前。
- `slug`：决定网址，例如 `slug: fling` 对应 `/projects/fling/` 和 `/en/projects/fling/`。
- 图片和文档建议使用英文文件名，不使用空格。

## 3. 普通 Markdown

支持：

```md
## 二级标题
### 三级标题

普通段落，支持 **粗体**、*斜体*、`代码` 和 [链接](https://example.com)。

- 无序列表
- 无序列表

1. 有序列表
2. 有序列表

![图片说明](/assets/images/example.webp)
```

二级标题会自动生成左侧目录。

## 4. 指标卡片

```md
:::metrics
- 18 分钟 | 完整体验时长 | 从任务发布到最终选择
- 300 小时 | 独立开发投入 | 设计、搭建、脚本与测试
:::
```

格式为：`数值 | 标题 | 补充说明`。

## 5. 重点说明

```md
:::callout title="我的职责"
关卡流程、白盒、战斗遭遇、脚本实现与测试迭代。
:::
```

英文页面直接使用英文标题：

```md
:::callout title="My Responsibilities"
Quest flow, blockout, encounters, scripting, playtesting, and iteration.
:::
```

## 6. 图片画廊

```md
:::gallery cols=2
![第一张图片说明](/assets/images/image-01.webp)
![第二张图片说明](/assets/images/image-02.webp)
:::
```

`cols` 可以使用 `1`、`2` 或 `3`。图片可以点击放大。

## 7. 设计步骤

```md
:::steps
- 入口识别 | 让玩家在高速移动中提前发现路线入口。
- 路线预告 | 镜头展示下一段道路与目标位置。
:::
```

## 8. 能力卡片

```md
:::capabilities
- 空间设计 | 使用路线结构和空间层级建立清晰流程。
- 原型实现 | 在引擎中独立制作可测试版本。
:::
```

## 9. 时间线

```md
:::timeline
- 2025—2027 | SMU Guildhall | Level Design Track
- 2024 | 网易雷火 | 系统策划实习
:::
```

## 10. 文档与外部链接

```md
:::links
- 完整演示 | https://youtu.be/example | YouTube
- 设计文档 | /assets/docs/example.pdf | PDF
:::
```

## 11. 项目归档卡片

用于 `content/archive.md` 与 `content_en/archive.md`：

```md
:::archive
- 项目名称 | 工具或类型 | 一句话介绍。 | /assets/images/cover.webp
- 没有图片的项目 | Prototype | 会自动使用文字占位图。 |
:::
```

## 12. 构建与检查

修改完成后运行：

```bash
python scripts/build.py
```

脚本会同时生成中文根目录页面与 `/en/` 英文页面，并更新 `sitemap.xml`。

## 内容写作建议

每个完整项目优先回答五个问题：

1. 你要解决什么玩家体验问题？
2. 你个人具体负责什么？
3. 为什么选择这种空间、机制或流程结构？
4. 测试发现了什么问题，你如何调整？
5. 最终完成了什么，下一步会改进什么？

英文版本不要逐字直译中文，而应优先使用海外游戏行业常见表达，并保持职责边界清晰。
