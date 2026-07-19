# Markdown 内容编辑指南

## 1. 中英文内容对应关系

```text
content/home.md                 中文首页
content/en/home.md              英文首页
content/projects/decaran.md     中文项目页
content/en/projects/decaran.md  对应英文项目页
```

中英文项目必须使用相同的 `slug`，这样语言切换才能进入同一个项目。

## 2. 项目基础信息与分类

```md
---
layout: project
slug: project-name
title: 项目名称
subtitle: 项目副标题
kicker: LEVEL DESIGN / ENGINE
summary: 一句话说明体验目标和个人贡献。
cover: /assets/images/project-cover.webp
hero: /assets/images/project-hero.webp
engine: Unreal Engine 5
role: 关卡设计师
team: 4 人团队
period: 8 周
status: 完成
featured: true
category: personal
order: 1
tags: [关卡设计, 战斗设计, 玩家引导]
card_note: 卡片底部补充信息
---
```

分类字段：

- `category: personal`：个人项目
- `category: team`：团队项目
- 其他小型项目统一写在 `archive.md` 中

`order` 数字越小越靠前，`slug` 决定项目网址。

## 3. 首页与个人信息

- `site.md`：姓名、角色、邮箱、电话、简历、个人照片路径
- `home.md`：首页标题、介绍和设计取向
- `about.md`：经历、技能、工具和详细个人介绍

个人照片默认路径：

```md
profile_image: /assets/images/profile-zixiao.webp
```

## 4. 普通 Markdown

```md
## 二级标题
### 三级标题

普通段落支持 **粗体**、*斜体*、`代码` 和 [链接](https://example.com)。

- 无序列表

1. 有序列表

![图片说明](/assets/images/example.webp)
```

二级标题会自动生成项目页左侧目录。

## 5. 指标卡片

```md
:::metrics
- 18 分钟 | 完整体验时长 | 从任务发布到最终选择
- 300 小时 | 独立开发投入 | 设计、搭建、脚本与测试
:::
```

## 6. 重点说明

```md
:::callout title="我的职责"
关卡流程、白盒、战斗遭遇、脚本实现与测试迭代。
:::
```

## 7. 图片画廊

```md
:::gallery cols=2
![第一张图片说明](/assets/images/image-01.webp)
![第二张图片说明](/assets/images/image-02.webp)
:::
```

`cols` 支持 `1`、`2` 或 `3`，图片可点击放大。

## 8. 设计步骤与能力卡片

```md
:::steps
- 入口识别 | 让玩家提前发现路线入口。
- 路线预告 | 镜头展示下一段道路。
:::
```

```md
:::capabilities
- 空间设计 | 使用路线结构和空间层级建立清晰流程。
- 原型实现 | 在引擎中独立制作可测试版本。
:::
```

## 9. 时间线与资源链接

```md
:::timeline
- 2025—2027 | SMU Guildhall | Level Design Track
- 2024 | 网易雷火 | 系统策划实习
:::
```

```md
:::links
- 完整演示 | https://youtu.be/example | YouTube
- 设计文档 | /assets/docs/example.pdf | PDF
:::
```

## 10. 其他项目卡片

在中文和英文的 `archive.md` 中分别维护：

```md
:::archive
- 项目名称 | 工具或类型 | 一句话介绍。 | /assets/images/cover.webp
- 没有图片的项目 | Prototype | 自动使用 LD 占位图。 |
:::
```

## 项目写作检查

每个完整项目优先回答：设计问题是什么、个人具体负责什么、为何选择该空间或机制结构、测试发现了什么、最终完成了什么。
