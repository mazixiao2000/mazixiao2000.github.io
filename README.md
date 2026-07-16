# 马子潇个人作品集网站 / Zixiao Ma Portfolio

这是一个部署于 GitHub Pages 的中英文双语静态个人作品集网站。

This is a bilingual Chinese–English portfolio website designed for deployment on GitHub Pages.

## 内容维护 / Content Editing

每个页面使用两份 Markdown：

- `content.md`：中文内容
- `content_en.md`：English content

详细语法与操作步骤见：[CONTENT_GUIDE.md](CONTENT_GUIDE.md)

## 在线更新 / GitHub Pages

修改 Markdown、图片或 PDF 后，通过 GitHub Desktop 提交并推送即可。网页顶部的语言滑块会读取对应语言内容。

After editing Markdown, images, or PDFs, commit and push with GitHub Desktop. The language switch in the header loads the matching language files.

## 本地预览 / Local Preview

修改任意 Markdown 文件后，运行：

```text
build-content.bat
```

或：

```bash
python scripts/build_content.py
```

脚本会重新生成同时包含中英文内容的 `content.generated.js`。
