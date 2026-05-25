---
name: "article-manager"
description: "创建和管理文章目录结构。Invoke when user needs to create article directories, organize content files, or manage article structure."
---

# 文章目录管理

创建和管理文章目录结构，确保文章组织有序。

## 功能

- 创建日期目录和文章目录
- 生成 article.md 模板
- 管理文章文件结构

## 目录结构规范

```
content/
├── YYYYMMDD/                          # 日期目录
│   └── 文章标题/                       # 文章目录
│       ├── article.md                  # 完整文章
│       └── article-wechat.html         # 公众号格式
```

## 使用方法

### 创建新文章目录

```bash
mkdir -p content/YYYYMMDD/文章标题
touch content/YYYYMMDD/文章标题/article.md
```

### article.md 模板

```markdown
# 文章标题

## 封面图描述
[50-100字描述]
风格建议：[风格]
色调建议：[色调]
主体元素：[元素]
氛围：[情绪/氛围描述]

## 摘要
"[34字以内的一句话摘要]"

## 标题推荐
- A版：[信息明确型标题]
- B版：[悬念吸引型标题]
- C版：[情感共鸣型标题]

---

## 正文

### 01 小节标题
正文内容...
```

## 使用场景

- 用户说"创建文章" → 创建目录结构和模板
- 用户说"新建文章" → 创建目录结构和模板
- 用户说"整理文章" → 整理现有文章到新结构

## 文件命名规范

- **日期目录**: `YYYYMMDD` 格式
- **文章目录**: 简短清晰的中文标题
- **MD文件**: 固定命名 `article.md`
- **HTML文件**: 固定命名 `article-wechat.html`
