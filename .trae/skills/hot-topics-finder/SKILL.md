---
name: "hot-topics-finder"
description: "获取今日热点话题。Invoke when user asks for '今日热点', '热搜', '热门话题', or wants to know current trending topics."
---

# 热点话题获取

获取中文互联网实时热点话题。

## 功能

从百度热搜等平台抓取当前热门话题，返回结构化数据。

## 使用方法

运行脚本获取热点：

```bash
python3 .trae/skills/hot-topics-finder/scripts/fetch_topics.py --limit 10
```

### 参数

- `--limit`: 返回话题数量（默认5，最大20）
- `--category`: 分类（social/tech/entertainment/world）

## 输出格式

返回 Markdown 格式的话题列表：

```markdown
## 社会民生热点

1. **话题标题**
   - 来源：百度热搜 [链接]

2. **话题标题**
   - 来源：百度热搜 [链接]
```

## 使用场景

- 用户说"今日热点" → 获取热点话题列表
- 用户说"看看热搜" → 获取热点话题列表
- 用户说"有什么热门话题" → 获取热点话题列表

## 注意事项

- 脚本会尝试多个平台，如果某个平台失败会跳过
- 默认超时15秒，避免长时间等待
