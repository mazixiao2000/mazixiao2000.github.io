# 本次重构说明

## 路径迁移

旧结构：

```text
content/site.md
content/home.md
content/projects/decaran.md
content_en/home.md
content_en/projects/decaran.md
```

新结构：

```text
data/site.json
content/pages/home.zh.md
content/pages/home.en.md
content/projects/decaran/project.json
content/projects/decaran/zh.md
content/projects/decaran/en.md
```

## 顶部姓名 bug

旧生成器在 HTML 模板中直接写死：

```html
<strong>MA ZIXIAO</strong>
```

新生成器读取：

```text
data/site.json → identity.zh.brand / identity.en.brand
```

因此中文页面重新构建后仍会保持“马子潇”，不会再次被模板覆盖。
