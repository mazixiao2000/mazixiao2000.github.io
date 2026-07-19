# 马子潇｜双语关卡设计作品集

面向米哈游、鹰角等中国游戏公司关卡设计 / 游戏设计岗位制作的静态作品集网站。整体采用 Apple / visionOS 风格毛玻璃界面，并使用 **Markdown 内容 + Python 静态生成** 架构，无前端框架依赖，可直接部署到 GitHub Pages。

## 核心特性

- 中文默认站点，英文站点位于 `/en/`
- 顶栏可切换中英文，并显示邮箱与电话
- 项目按“个人项目 / 团队项目 / 其他项目”分类
- 首页和关于页面展示个人照片
- 原生 CSS `backdrop-filter` 毛玻璃效果，并提供不支持浏览器的回退样式
- 桌面端、平板与手机端响应式布局
- 图片灯箱、项目目录、滚动进度和轻量进入动画
- Markdown 修改后可一键重新生成全部中英文页面

## 文件结构

```text
content/                 中文 Markdown 内容
content/en/              英文 Markdown 内容
content/projects/        中文完整项目
content/en/projects/     英文完整项目
assets/images/           项目图片与个人照片
assets/docs/             中英文简历与项目文档
assets/css/styles.css    全站毛玻璃视觉样式
assets/js/main.js        菜单、目录、灯箱等交互
scripts/build.py         双语静态网站生成器
en/                      自动生成的英文网站
```

## 部署到 GitHub Pages

1. 解压压缩包。
2. 将 `mazixiao-portfolio` 文件夹**里面的全部内容**复制到 `mazixiao2000.github.io` 仓库根目录。
3. 不要只上传外层文件夹，否则网址会多一层目录。
4. 保留 `CNAME` 文件，以继续使用 `mazixiao.com`。
5. 使用 GitHub Desktop Commit 并 Push。

生成后的 HTML 已包含在压缩包中，首次部署不需要运行构建命令。

## 修改内容

中文内容：

- `content/site.md`
- `content/home.md`
- `content/about.md`
- `content/projects/*.md`
- `content/archive.md`

英文内容位于对应的 `content/en/` 路径。

修改 Markdown 后重新生成：

- Windows：双击 `build-content.bat`
- macOS / Linux：运行 `./build-content.sh`

构建脚本只使用 Python 标准库，建议 Python 3.10 或更高版本。

## 替换个人照片

当前照片文件：

```text
assets/images/profile-zixiao.webp
```

使用同名图片直接替换即可，建议竖版、清晰、正面或半身照，宽度至少 800 px。替换图片不需要重新运行构建脚本。

## 本地预览

在网站目录打开终端：

```bash
python -m http.server 8000
```

浏览器访问：

```text
http://localhost:8000
```

不要直接双击 `index.html`，否则部分绝对路径资源可能无法正常加载。
