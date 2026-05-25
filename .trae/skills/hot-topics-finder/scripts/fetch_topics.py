#!/usr/bin/env python3
"""
热点话题获取脚本 - 智能版
优先级：微博热搜(本地) → Tavily搜索 → retry
"""

import argparse
import json
import sys
import re
import os
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 超时配置（秒）
TIMEOUT_CONFIG = {
    "connect": 5,
    "read": 10,
    "total": 15
}

# Tavily API 配置
TAVILY_SCRIPT = os.path.expanduser("~/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py")


def fetch_weibo_hot() -> List[Dict]:
    """获取微博热搜"""
    url = 'https://weibo.com/ajax/side/hotSearch'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://weibo.com/',
    }
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=TIMEOUT_CONFIG["total"]) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'data' in data and 'realtime' in data['data']:
                hot_list = data['data']['realtime']
                topics = []
                for item in hot_list[:15]:
                    note = item.get('note', '').strip()
                    num = item.get('num', 0)
                    if note:
                        topics.append({
                            "title": note,
                            "summary": f"热度: {num}",
                            "source": "微博热搜"
                        })
                return topics
    except Exception as e:
        print(f"微博热搜获取失败: {e}", file=sys.stderr)
    
    return []


def fetch_tavily_topics(max_retries: int = 2) -> List[Dict]:
    """使用 Tavily 获取热门话题"""
    import subprocess
    
    queries = [
        "今日热点新闻 微博热搜 社交媒体热议",
        "今天热门话题 网络热议事件"
    ]
    
    for attempt in range(max_retries):
        for query in queries:
            try:
                cmd = [
                    "python3", TAVILY_SCRIPT,
                    "--query", query,
                    "--max-results", "10",
                    "--format", "json"
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        if isinstance(data, list) and len(data) > 0:
                            topics = []
                            for item in data[:10]:
                                title = item.get('title', '').strip()
                                snippet = item.get('snippet', '')[:80]
                                if title:
                                    topics.append({
                                        "title": title,
                                        "summary": snippet + "..." if snippet else "",
                                        "source": "Tavily搜索"
                                    })
                            if topics:
                                return topics
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                print(f"Tavily 查询失败 ({query}): {e}", file=sys.stderr)
                continue
    
    return []


def fetch_all_topics(limit: int = 10) -> List[Dict]:
    """
    获取热点话题
    优先级：微博热搜 → Tavily → 重试
    """
    all_topics = []
    seen_titles = set()
    
    # 1. 先尝试微博热搜（免费，本地）
    print("正在获取 微博热搜...", file=sys.stderr)
    weibo_topics = fetch_weibo_hot()
    for topic in weibo_topics:
        title = topic.get("title", "").strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            all_topics.append(topic)
    
    if len(all_topics) >= limit:
        return all_topics[:limit]
    
    # 2. 微博失败或不够，用 Tavily
    print("微博数据不足，尝试 Tavily 搜索...", file=sys.stderr)
    tavily_topics = fetch_tavily_topics(max_retries=2)
    for topic in tavily_topics:
        title = topic.get("title", "").strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            all_topics.append(topic)
    
    return all_topics[:limit]


def estimate_tokens(text: str) -> int:
    """估算 token 数量"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + english_words * 1.3 + other_chars * 0.5)


def format_output(topics: List[Dict]) -> str:
    """格式化输出，用于用户选择"""
    lines = ["## 今日热点话题\n"]
    lines.append("请回复数字选择要深入挖掘的话题（如：1,3,5）：\n")
    
    for i, topic in enumerate(topics, 1):
        lines.append(f"**{i}. {topic['title']}**")
        if topic.get('summary'):
            lines.append(f"   {topic['summary']}")
        lines.append(f"   *来源：{topic['source']}*")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="获取实时热点话题")
    parser.add_argument("--limit", "-l", type=int, default=10, help="返回数量（默认10）")
    parser.add_argument("--json", "-j", action="store_true", help="输出JSON格式")
    args = parser.parse_args()
    
    topics = fetch_all_topics(args.limit)
    
    if not topics:
        print("❌ 未能获取到任何热点话题", file=sys.stderr)
        sys.exit(1)
    
    if args.json:
        print(json.dumps(topics, ensure_ascii=False, indent=2))
    else:
        output = format_output(topics)
        tokens = estimate_tokens(output)
        print(f"# 今日热点话题 (约 {tokens} tokens)\n")
        print(output)


if __name__ == "__main__":
    main()
