# 双语内容编辑指南

## 1. 页面内容成对维护

普通页面位于：

```text
content/pages/home.zh.md
content/pages/home.en.md
content/pages/about.zh.md
content/pages/about.en.md
content/pages/archive.zh.md
content/pages/archive.en.md
```

项目位于同一个文件夹内：

```text
content/projects/decaran/
  project.json
  zh.md
  en.md
```

这样打开一个项目文件夹，就能同时看到共享设置与两种语言内容。

## 2. 项目共享设置 `project.json`

```json
{
  "slug": "decaran",
  "cover": "/assets/images/decaran-cover.webp",
  "hero": "/assets/images/decaran-overview.webp",
  "featured": true,
  "order": 1
}
```

- `slug`：决定网址，必须与文件夹名一致。
- `cover`：首页与项目列表卡片封面。
- `hero`：项目详情页顶部主视觉。
- `featured`：是否显示在首页精选项目中。
- `order`：显示顺序，数字越小越靠前，不能重复。

这些信息两种语言共用，只写一次。

## 3. 本地化项目信息 `zh.md` / `en.md`

```md
---
layout: project
title: 项目名称
subtitle: 项目类型与一句话定位
kicker: LEVEL DESIGN / ENGINE
summary: 一句话说明体验目标、个人职责和结果。
engine: Unreal Engine 5
role: 关卡设计
team: 4 人团队
period: 8 周 · Scrum
status: 完成
tags: [关卡设计, 战斗设计, 玩家引导]
card_note: 首页卡片底部的补充信息
---
```

英文文件使用相同字段，但内容应按海外游戏行业表达重新组织，而不是机械逐字翻译。

## 4. 全站信息与变量

全站信息集中在：

```text
data/site.json
```

Markdown 中可以引用以下变量：

```md
{{site.name}}
{{site.email}}
{{site.phone}}
{{site.resume}}
{{site.resume_zh}}
{{site.resume_en}}
{{site.linkedin}}
{{site.github}}
```

例如：

```md
:::links
- 下载中文简历 | {{site.resume_zh}} | PDF · 中文
- LinkedIn | {{site.linkedin}} | 职业经历与联系
:::
```

变量不存在时，构建会直接报错，避免生成带有错误占位符的网页。

## 5. 普通 Markdown

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

二级标题会自动生成左侧目录和锚点。

## 6. 指标卡片

```md
:::metrics
- 18 分钟 | 完整体验时长 | 从任务发布到最终选择
- 300 小时 | 独立开发投入 | 设计、搭建、脚本与测试
:::
```

格式为：`数值 | 标题 | 补充说明`。

## 7. 重点说明

```md
:::callout title="我的职责"
关卡流程、白盒、战斗遭遇、脚本实现与测试迭代。
:::
```

## 8. 图片画廊

```md
:::gallery cols=2
![第一张图片说明](/assets/images/image-01.webp)
![第二张图片说明](/assets/images/image-02.webp)
:::
```

`cols` 可使用 `1`、`2` 或 `3`。图片可以点击放大。

## 9. 设计步骤

```md
:::steps
- 入口识别 | 让玩家在高速移动中提前发现路线入口。
- 路线预告 | 镜头展示下一段道路与目标位置。
:::
```

## 10. 能力卡片

```md
:::capabilities
- 空间设计 | 使用路线结构和空间层级建立清晰流程。
- 原型实现 | 在引擎中独立制作可测试版本。
:::
```

## 11. 时间线

```md
:::timeline
- 2025—2027 | SMU Guildhall | Level Design Track
- 2024 | 网易雷火 | 系统策划实习
:::
```

## 12. 文档与外部链接

```md
:::links
- 完整演示 | https://youtu.be/example | YouTube
- 设计文档 | /assets/docs/example.pdf | PDF
:::
```

## 13. 项目表格

时间线与测试迭代支持标准 Markdown 表格：

```md
| 阶段 | 时间 | 工作内容 |
|---|---|---|
| Whitebox | 2026.06.08 | 完成白盒搭建。 |
```

在手机上表格会自动允许横向滚动，不会挤压正文。

## 14. 视频接口

中文项目页使用 Bilibili 的 BV 号：

```md
:::video platform="Bilibili" id="BVxxxxxxxxxx" title="项目宣传片"
:::
```

英文项目页使用 YouTube 视频网址中 `v=` 或 `youtu.be/` 后面的 ID：

```md
:::video platform="YouTube" id="dQw4w9WgXcQ" title="Project Trailer"
:::
```

暂时没有视频时将 `id` 留空，页面会显示已预留的视频位；以后只需补上 ID 并重新构建。

## 15. 项目归档卡片

用于 `archive.zh.md` 与 `archive.en.md`：

```md
:::archive
- 项目名称 | 工具或类型 | 一句话介绍。 | /assets/images/cover.webp
- 没有图片的项目 | Prototype | 会自动使用文字占位图。 |
:::
```

## 16. 新建项目

推荐使用脚本：

```bash
python scripts/new_project.py project-slug --order 5
```

`slug` 只能使用小写字母、数字和连字符。

## 17. 构建与质量检查

```bash
python scripts/build.py
python scripts/check.py
```

检查内容包括：

- 中文和英文源文件是否齐全。
- 项目 `slug` 与文件夹是否一致。
- 项目排序是否重复。
- 封面和主视觉是否存在。
- 站内链接、资源和章节锚点是否有效。
- 图片是否有 `alt`。
- canonical、hreflang 和双语项目页面是否齐全。
- 中文顶部品牌是否仍被英文硬编码覆盖。

## 内容写作建议

每个完整项目优先回答：

1. 你要解决什么玩家体验问题？
2. 你个人具体负责什么？
3. 为什么选择这种空间、机制或流程结构？
4. 测试发现了什么问题，你如何调整？
5. 最终完成了什么，下一步会改进什么？
