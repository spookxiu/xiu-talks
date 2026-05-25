#!/usr/bin/env python3
"""
热点话题深度挖掘工具
流程：Tavily获取热点 → Bing搜索相关文章 → 抓取正文 → 清洗提取
"""

import argparse
import json
import re
import sys
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import quote

# 导入 Tavily 搜索
sys.path.insert(0, '/Users/xiutianyu/.openclaw/workspace/skills/openclaw-tavily-search/scripts')
from tavily_search import tavily_search


def bing_search(query: str, max_results: int = 5, retries: int = 2) -> List[Dict]:
    """Bing 搜索，返回结果列表（带重试机制）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    url = f'https://www.bing.com/search?q={quote(query)}'
    
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8')
                
                results = []
                items = re.findall(r'<li[^>]*class=\"[^\"]*b_algo[^\"]*\"[^>]*>(.*?)</li>', html, re.DOTALL)
                
                for item in items[:max_results]:
                    # 提取标题和链接
                    link_match = re.search(r'<a[^>]*href=\"([^\"]*)\"[^>]*>(.*?)</a>', item, re.DOTALL)
                    if link_match:
                        url = link_match.group(1)
                        title = re.sub(r'<[^>]+>', '', link_match.group(2)).strip()
                        
                        # 提取摘要
                        desc_match = re.search(r'<p[^>]*>(.*?)</p>', item, re.DOTALL)
                        desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip() if desc_match else ''
                        
                        if title and url.startswith('http'):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': desc
                            })
                
                return results
        except Exception as e:
            if attempt < retries:
                print(f"  Bing 搜索重试 ({attempt + 1}/{retries})...", file=sys.stderr)
                import time
                time.sleep(2)
            else:
                print(f"Bing 搜索失败: {e}", file=sys.stderr)
                return []


def fetch_article(url: str, retries: int = 1) -> Optional[str]:
    """抓取文章正文（带重试机制）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as resp:
                data = resp.read()
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    return data.decode('gbk', errors='ignore')
        except Exception as e:
            if attempt < retries:
                print(f"    重试 ({attempt + 1}/{retries})...", file=sys.stderr)
                import time
                time.sleep(1)
            else:
                print(f"    抓取失败: {e}", file=sys.stderr)
                return None


def extract_content(html: str) -> str:
    """从 HTML 中提取正文内容"""
    # 移除 script 和 style
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # 尝试找 article 或 main 标签
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if article_match:
        content = article_match.group(1)
    else:
        # 找 p 标签内容
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        content = ' '.join(paragraphs)
    
    # 清理 HTML 标签
    content = re.sub(r'<[^>]+>', '', content)
    
    # 清理多余空白
    content = re.sub(r'\s+', ' ', content).strip()
    
    # 限制长度
    return content[:2000] if len(content) > 2000 else content


def clean_text(text: str) -> str:
    """清洗文本，提取有用信息"""
    # 移除常见的无关内容
    noise_patterns = [
        r'Copyright ©.*?Reserved',
        r'版权所有.*?保留',
        r'免责声明.*?(?=\n|$)',
        r'相关推荐.*?(?=\n|$)',
        r'热门文章.*?(?=\n|$)',
        r'上一篇.*?(?=\n|$)',
        r'下一篇.*?(?=\n|$)',
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # 移除过短的句子（可能是导航、按钮文字等）
    lines = text.split('\n')
    useful_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 20 and len(line) < 500:  # 保留中等长度的句子
            useful_lines.append(line)
    
    return '\n'.join(useful_lines[:10])  # 最多保留10行


def estimate_tokens(text: str) -> int:
    """估算 token 数量"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + english_words * 1.3 + other_chars * 0.5)


def search_with_fallback(query: str, max_results: int = 3) -> List[Dict]:
    """搜索文章，优先使用 Tavily，失败时回退到 Bing"""
    # 先尝试 Tavily
    try:
        print("  尝试 Tavily 搜索...")
        result = tavily_search(query, max_results=max_results, include_answer=False, search_depth="basic")
        if result and result.get('results'):
            # 转换格式为统一格式
            return [{
                'title': r['title'],
                'url': r['url'],
                'snippet': r.get('content', '')[:200]
            } for r in result['results'][:max_results]]
    except Exception as e:
        print(f"  Tavily 失败: {e}")
    
    # 回退到 Bing
    print("  回退到 Bing 搜索...")
    return bing_search(query, max_results=max_results)


def main():
    parser = argparse.ArgumentParser(description='热点话题深度挖掘')
    parser.add_argument('--topic', '-t', help='指定话题（不指定则自动获取）')
    parser.add_argument('--max-articles', '-n', type=int, default=3, help='抓取文章数量（默认3）')
    parser.add_argument('--bing-only', action='store_true', help='强制使用 Bing 搜索（跳过 Tavily）')
    args = parser.parse_args()
    
    # 步骤1: 获取话题
    if args.topic:
        topic = args.topic
        print(f"使用指定话题: {topic}\n")
    else:
        print("步骤1: 获取今日热点...")
        result = tavily_search("今日热点新闻", max_results=3, include_answer=False, search_depth="basic")
        if result and result.get('results'):
            topic = result['results'][0]['title']
            print(f"热点话题: {topic}\n")
        else:
            print("获取热点失败")
            return
    
    # 步骤2: 搜索相关文章（带 fallback）
    print(f"步骤2: 搜索 '{topic}'...")
    if args.bing_only:
        search_results = bing_search(topic, max_results=args.max_articles)
    else:
        search_results = search_with_fallback(topic, max_results=args.max_articles)
    print(f"找到 {len(search_results)} 篇文章\n")
    
    # 步骤3: 抓取并清洗文章（带去重）
    print("步骤3: 抓取文章内容...")
    articles = []
    seen_content_hashes = set()
    
    def content_hash(text: str) -> str:
        """生成内容指纹用于去重"""
        # 取前100个字符的简化版本作为指纹
        simplified = re.sub(r'[^\u4e00-\u9fff]', '', text[:100])
        return simplified[:20]
    
    for i, result in enumerate(search_results, 1):
        print(f"  抓取 [{i}/{len(search_results)}] {result['title'][:40]}...")
        html = fetch_article(result['url'])
        if html:
            content = extract_content(html)
            cleaned = clean_text(content)
            if cleaned:
                # 去重检查
                content_id = content_hash(cleaned)
                if content_id in seen_content_hashes:
                    print(f"    跳过重复内容")
                    continue
                seen_content_hashes.add(content_id)
                
                articles.append({
                    'title': result['title'],
                    'url': result['url'],
                    'content': cleaned
                })
    
    # 步骤4: 整理输出
    print(f"\n步骤4: 整理内容（成功抓取 {len(articles)} 篇）\n")
    
    output = f"# {topic}\n\n"
    for i, article in enumerate(articles, 1):
        output += f"## 来源 {i}: {article['title']}\n"
        output += f"链接: {article['url']}\n\n"
        output += f"{article['content']}\n\n"
        output += "---\n\n"
    
    tokens = estimate_tokens(output)
    print(f"（约 {tokens} tokens）\n")
    print(output)


if __name__ == '__main__':
    main()
