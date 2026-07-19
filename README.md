# 马子潇｜关卡设计作品集

面向中国游戏公司关卡设计 / 游戏设计岗位制作的静态作品集网站。网站使用 **Markdown 内容 + Python 静态生成** 架构，不依赖前端框架，生成后的文件可以直接部署到 GitHub Pages。

## 网站结构

- `index.html`：首页
- `work/`：全部完整项目
- `projects/`：各项目 Case Study
- `about/`：个人经历、技能与简历
- `archive/`：其他项目与研究归档
- `content/`：所有可编辑 Markdown 内容
- `assets/images/`：网站图片
- `assets/docs/`：简历和项目文档
- `scripts/build.py`：将 Markdown 生成静态 HTML

## 部署到 GitHub Pages

1. 解压压缩包。
2. 将文件夹内的**全部内容**复制到你的 `mazixiao02.github.io` 仓库根目录。不要把外层文件夹作为二级目录上传。
3. 保留 `CNAME` 文件，以继续使用 `mazixiao.com`。
4. 使用 GitHub Desktop 提交并 Push。
5. 等待 GitHub Pages 自动更新。

生成好的 HTML 已经包含在压缩包中，因此首次部署不需要运行任何命令。

## 修改内容

主要编辑以下文件：

- `content/site.md`：姓名、邮箱、电话、社交链接、简历路径
- `content/home.md`：首页介绍与设计能力
- `content/about.md`：个人介绍、经历、工具
- `content/projects/*.md`：项目页面
- `content/archive.md`：其他项目归档

修改 Markdown 后，重新生成网页：

- Windows：双击 `build-content.bat`
- macOS / Linux：运行 `./build-content.sh`

脚本只使用 Python 标准库，建议使用 Python 3.10 或更高版本。

## 本地预览

不要直接双击 `index.html`。在网站目录打开终端并运行：

```bash
python -m http.server 8000
```

浏览器打开：

```text
http://localhost:8000
```

## 设计原则

首页只突出能够完整说明设计问题、职责、过程和结果的项目；信息不完整的作品放入归档，避免削弱招聘方的第一印象。项目页面以设计目标、个人贡献、空间与机制分析、迭代和文档为核心，而不是仅展示最终截图。
