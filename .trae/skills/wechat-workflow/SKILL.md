---
name: "wechat-workflow"
description: "一键完成公众号文章全流程：创建目录、生成封面、摘要标题、撰写正文、转成HTML。Invoke when user says '写篇文章', '一键生成', or wants complete WeChat article creation workflow."
---

# 公众号文章工作流

一键完成从创建到发布的完整公众号文章流程。

## 功能

串联以下 Skill，完成全流程：
1. **article-manager** - 创建文章目录结构
2. **cover-prompt-generator** - 生成封面图描述
3. **metadata-generator** - 生成摘要和标题推荐
4. **wechat-formatter** - 转换为 HTML 格式

## 工作流程

```
用户输入主题 → 创建目录 → 生成封面 → 生成摘要/标题 → 撰写正文 → 转成HTML → 完成
```

## 使用场景

- 用户说"写篇文章" → 执行完整工作流
- 用户说"一键生成" → 执行完整工作流
- 用户说"帮我写篇公众号" → 执行完整工作流

## 执行步骤

### Step 1: 创建文章目录
使用 **article-manager** 创建：
```bash
mkdir -p content/YYYYMMDD/文章标题
touch content/YYYYMMDD/文章标题/article.md
```

### Step 2: 生成封面图描述
使用 **cover-prompt-generator** 生成封面描述。

### Step 3: 生成摘要和标题
使用 **metadata-generator** 生成：
- 34字以内摘要
- A/B/C 三版标题

### Step 4: 撰写正文
根据用户提供的观点或主题，撰写正文内容。

### Step 5: 生成完整 article.md
组合以上所有内容，生成完整的 article.md：

```markdown
# 文章标题

## 封面图描述
...

## 摘要
...

## 标题推荐
...

---

## 正文
...
```

### Step 6: 转换为 HTML
使用 **wechat-formatter** 生成 article-wechat.html。

## 输出文件

- `content/YYYYMMDD/标题/article.md` - 完整文章
- `content/YYYYMMDD/标题/article-wechat.html` - 公众号格式

## 也可以单独使用

工作流中的每个步骤都可以单独调用：
- 只要封面 → 调用 cover-prompt-generator
- 只要标题 → 调用 metadata-generator
- 只要转HTML → 调用 wechat-formatter
