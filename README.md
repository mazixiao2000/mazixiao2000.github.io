# 马子潇｜双语关卡设计作品集

面向中国与海外游戏公司关卡设计 / 游戏设计岗位的静态作品集网站。网站采用 **集中配置 + 成对双语 Markdown + Python 静态生成** 架构，不依赖前端框架，生成结果可直接部署到 GitHub Pages。

## 这版重构解决了什么

- 中文顶部品牌由配置读取，显示为 **马子潇**；英文显示为 **ZIXIAO MA**，不再写死在模板里。
- 姓名、邮箱、电话、简历、社交链接、头像与首页履历统一放在 `data/site.json`。
- 每个项目的中文和英文内容放在同一个文件夹中，避免两套目录逐渐不同步。
- `slug`、排序、封面、主视觉等共用信息只写一次。
- 每次构建前自动清理旧页面，删除项目后不会残留失效页面。
- 构建时检查双语文件、项目排序、资源路径；构建后检查站内链接、锚点、图片 alt、canonical 与 hreflang。
- 自动生成中英文 SEO 元数据、结构化数据和双语 Sitemap。

## 目录结构

```text
data/
  site.json                 # 姓名、联系方式、简历、社交链接、首页履历
  i18n.json                 # 导航与界面文案

content/
  pages/
    home.zh.md              # 中文首页正文
    home.en.md              # 英文首页正文
    about.zh.md / about.en.md
    archive.zh.md / archive.en.md
  projects/
    decaran/
      project.json          # 两种语言共用：slug、排序、封面、主视觉
      zh.md                 # 中文项目内容与本地化信息
      en.md                 # 英文项目内容与本地化信息

assets/
  images/                   # 图片
  docs/                     # 简历与项目文档
  css/styles.css
  js/main.js

scripts/
  build.py                  # 生成全部网页
  check.py                  # 检查生成结果
  new_project.py            # 创建新项目双语模板
```

生成后的中文页面位于根目录，英文镜像位于 `/en/`：

- `/projects/decaran/`
- `/en/projects/decaran/`

顶部“中 / EN”会切换到当前页面对应的另一语言版本，并保留当前章节锚点。

## 最常修改的文件

### 修改姓名、联系方式或简历

编辑：

```text
data/site.json
```

关键字段：

```json
{
  "identity": {
    "zh": {
      "name": "马子潇",
      "brand": "马子潇"
    },
    "en": {
      "name": "Zixiao Ma",
      "brand": "ZIXIAO MA"
    }
  },
  "contact": {
    "email": "mazixiao2000@outlook.com"
  },
  "resumes": {
    "zh": "/assets/docs/中文简历.pdf",
    "en": "/assets/docs/English_Resume.pdf"
  }
}
```

`name` 用于页面标题、页脚和结构化数据；`brand` 专门控制顶部品牌文字。

### 修改首页、关于与归档

编辑 `content/pages/` 下对应的 `.zh.md` 和 `.en.md`。

### 修改项目

进入对应项目文件夹：

```text
content/projects/hamsterballin/
```

- 修改 `project.json`：排序、封面、主视觉、是否在首页展示。
- 修改 `zh.md`：中文标题、摘要、职责、正文。
- 修改 `en.md`：英文标题、摘要、职责、正文。

## 新建项目

在网站根目录运行：

```bash
python scripts/new_project.py new-project --order 5
```

脚本会创建：

```text
content/projects/new-project/project.json
content/projects/new-project/zh.md
content/projects/new-project/en.md
```

随后放入封面图片、填写双语内容，再重新构建。

## 构建与检查

Windows：双击

```text
build-content.bat
```

macOS / Linux：

```bash
./build-content.sh
```

也可以分别运行：

```bash
python scripts/build.py
python scripts/check.py
```

仅使用 Python 标准库，建议 Python 3.10 或更高版本。

## 本地预览

不要直接双击 `index.html`。在网站根目录运行：

```bash
python -m http.server 8000
```

然后打开：

```text
中文：http://localhost:8000/
英文：http://localhost:8000/en/
```

## 部署到 GitHub Pages

1. 将本文件夹中的全部内容覆盖到 GitHub Pages 仓库根目录。
2. 保留 `CNAME`，继续使用 `www.mazixiao.com`。
3. 使用 GitHub Desktop Commit 并 Push。
4. 等待 GitHub Pages 完成部署。

压缩包已经包含生成后的 HTML，因此首次部署不要求本地安装 Python。
