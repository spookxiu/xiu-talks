---
name: "wechat-formatter"
description: "将 Markdown 文章转换为微信公众号 HTML 格式。Invoke when user wants to convert article to HTML, says '转成HTML', '格式化', or needs WeChat-compatible formatting."
---

# 公众号格式转换器

将 Markdown 文章转换为可直接粘贴到公众号编辑器的 HTML 格式。

## 功能

- 提取正文内容（从 `## 正文` 开始）
- 转换为带样式的 HTML
- 优化排版以适应公众号编辑器

## 输出格式

生成 `article-wechat.html` 文件，包含：
- 完整的 HTML 结构
- 内联 CSS 样式
- 公众号优化的排版

## HTML 样式规范

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>文章标题</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    padding: 20px;
}
h2 {
    font-size: 18px;
    font-weight: bold;
    margin-top: 30px;
    border-left: 4px solid #07c160;
    padding-left: 12px;
}
p {
    margin-bottom: 16px;
    text-align: justify;
}
strong {
    font-weight: bold;
    color: #1a1a1a;
}
</style>
</head>
<body>
<!-- 正文内容 -->
</body>
</html>
```

## 转换规则

- 提取 `## 正文` 之后的内容
- `###` 转换为 `<h2>`
- `**文字**` 转换为 `<strong>`
- 段落转换为 `<p>`
- 列表转换为 `<ul>/<li>`
- 分隔线 `---` 转换为 `<hr>`

## 使用场景

- 用户说"转成HTML" → 转换文章为 HTML
- 用户说"格式化" → 转换文章为 HTML
- 用户说"生成公众号版本" → 转换文章为 HTML

## 使用方法

1. 读取 `content/YYYYMMDD/标题/article.md`
2. 提取正文部分
3. 应用 HTML 模板和样式
4. 保存为 `content/YYYYMMDD/标题/article-wechat.html`

## 注意事项

- HTML 文件只包含正文，不包含封面、摘要等元数据
- 样式已内联，可直接复制到公众号编辑器
- 标题使用 H2（##）格式，与公众号编辑器兼容
