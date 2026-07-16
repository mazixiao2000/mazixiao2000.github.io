# 中英文网站内容更新指南

本网站使用中英文双语 Markdown 内容。网页外观、布局和交互由 `index.html` 控制；日常更新只需要编辑各页面目录中的 Markdown 文件。

## 1. 中英文内容文件

每个页面包含两份内容：

```text
project1/content.md       中文
project1/content_en.md    English

project2/content.md
project2/content_en.md

project3/content.md
project3/content_en.md

project4/content.md
project4/content_en.md

moreprojects/content.md
moreprojects/content_en.md

aboutme/content.md
aboutme/content_en.md
```

顶部栏右侧的语言滑块会在两份内容之间切换。访客选择的语言会保存在浏览器中。

更新中文内容时编辑 `content.md`；更新英文内容时编辑 `content_en.md`。建议两份文件保持相同的章节、图片和链接顺序。

## 2. 页面基本信息

每个 Markdown 文件顶部都有由 `---` 包围的元数据：

```md
---
title: 页面大标题
tab_title: 左侧选项卡标题
tag: 页面副标题
type: 项目类型
role: 负责模块
time: 项目周期
caption: 页面底部说明
hero: images/hero.jpg
hero_caption: Hero 图片题注
hero_width: 68%
---
```

英文文件中填写对应英文内容：

```md
---
title: About Me
tab_title: About Me
tag: Resume & Design Experience
type: Personal Profile
role: Level Designer / Game Designer
time: Portfolio
caption: ▲ English footer caption
hero: images/hero.jpg
hero_caption: English hero caption
hero_width: 68%
---
```

- `hero` 可以省略；省略后该页面不显示 Hero 图。
- Hero 图固定显示在页面大标题下方。
- `hero_width` 可以省略，默认铺满内容宽度。
- 中文和英文页面可以引用同一张图片和同一份 PDF。

## 3. 添加标题和正文

```md
## 项目概述

这里写正文。不同段落之间保留一个空行。
```

英文文件示例：

```md
## Project Overview

Write the English project description here.
```

## 4. 添加图片和题注

```md
![图片题注](images/combat-space.jpg)
```

英文版应翻译方括号内的题注，但图片路径保持不变：

```md
![Combat-space layout and cover placement](images/combat-space.jpg)
```

建议图片使用英文小写文件名，例如：

```text
hero.jpg
level-overview.jpg
combat-space.jpg
boss-fight.jpg
```

## 5. 添加 YouTube 内嵌播放器

```md
@[youtube](lieJnrhMxWs "《底卡伦：变人》完整游戏演示")
```

英文版：

```md
@[youtube](lieJnrhMxWs "Decaran: Become Human — Full Gameplay Walkthrough")
```

也可以填写完整 YouTube 链接。部署到 GitHub Pages 后会直接显示内嵌播放器。直接双击本地 `index.html` 时，YouTube 可能因来源验证而无法播放。

## 6. 添加 PDF 或简历按钮

单个按钮：

```md
[📄 查看 LDD](pdfs/example.pdf)
```

英文按钮：

```md
[📄 View LDD](pdfs/example.pdf)
```

两个按钮并排：

```md
[📄 中文简历](../resume.pdf) [📄 English Resume](../resume_en.pdf)
```

链接放在哪段文字下面，按钮就会显示在哪段文字下面。

## 7. 更新与预览

### 上传 GitHub Pages

修改 Markdown、图片或 PDF 后，通过 GitHub Desktop 提交并推送。线上网站会读取当前语言对应的 Markdown 文件，不需要修改 `index.html`。

### 本地双击预览

直接双击 `index.html` 时，网站使用 `content.generated.js` 作为本地备用内容。每次修改任意 `content.md` 或 `content_en.md` 后，运行：

```text
build-content.bat
```

也可以在终端运行：

```bash
python scripts/build_content.py
```

## 8. 不应手动修改的文件

```text
content.generated.js
```

该文件由构建脚本自动生成，并同时包含中文和英文内容。
