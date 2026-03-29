#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版爆款文章抓取系统
使用RSS和公开API获取热门文章
"""

import requests
import json
import time
import random
from typing import List, Dict
import os

class SimpleArticleCrawler:
    """简化版文章爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_hackernews_top(self, limit=10) -> List[Dict]:
        """
        获取Hacker News热门文章
        使用官方API，稳定可靠
        """
        print("正在获取Hacker News热门文章...")
        
        try:
            # 获取热门文章ID列表
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()[:limit]
            articles = []
            
            # 获取每篇文章的详细信息
            for story_id in story_ids:
                try:
                    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    story_response = self.session.get(story_url, timeout=10)
                    story_data = story_response.json()
                    
                    if story_data:
                        articles.append({
                            'platform': 'Hacker News',
                            'title': story_data.get('title', ''),
                            'url': story_data.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                            'score': story_data.get('score', 0),
                            'by': story_data.get('by', ''),
                            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(story_data.get('time', 0))),
                            'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    time.sleep(0.1)  # 避免请求过快
                    
                except Exception as e:
                    print(f"获取文章 {story_id} 失败: {str(e)}")
                    continue
            
            print(f"✓ 成功获取 {len(articles)} 篇Hacker News热门文章")
            return articles
            
        except Exception as e:
            print(f"✗ 获取Hacker News失败: {str(e)}")
            return []
    
    def fetch_reddit_programming(self, limit=10) -> List[Dict]:
        """
        获取Reddit编程板块热门文章
        使用官方JSON API
        """
        print("正在获取Reddit编程热门文章...")
        
        try:
            url = 'https://www.reddit.com/r/programming/hot.json'
            headers = self.headers.copy()
            headers['Accept'] = 'application/json'
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for post in data['data']['children'][:limit]:
                post_data = post['data']
                
                articles.append({
                    'platform': 'Reddit',
                    'title': post_data.get('title', ''),
                    'url': post_data.get('url', ''),
                    'score': post_data.get('score', 0),
                    'author': post_data.get('author', ''),
                    'subreddit': post_data.get('subreddit', ''),
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            print(f"✓ 成功获取 {len(articles)} 篇Reddit热门文章")
            return articles
            
        except Exception as e:
            print(f"✗ 获取Reddit失败: {str(e)}")
            return []
    
    def fetch_dev_to_articles(self, limit=10) -> List[Dict]:
        """
        获取dev.to热门文章
        使用官方API
        """
        print("正在获取dev.to热门文章...")
        
        try:
            url = f'https://dev.to/api/articles?per_page={limit}&top=7'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            articles_data = response.json()
            articles = []
            
            for article in articles_data:
                articles.append({
                    'platform': 'dev.to',
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'description': article.get('description', ''),
                    'author': article.get('user', {}).get('name', ''),
                    'tags': article.get('tag_list', []),
                    'positive_reactions_count': article.get('positive_reactions_count', 0),
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            print(f"✓ 成功获取 {len(articles)} 篇dev.to热门文章")
            return articles
            
        except Exception as e:
            print(f"✗ 获取dev.to失败: {str(e)}")
            return []
    
    def fetch_github_trending(self, limit=10) -> List[Dict]:
        """
        获取GitHub Trending
        使用非官方API
        """
        print("正在获取GitHub Trending...")
        
        try:
            url = 'https://api.gitterapp.com/repositories?language=&since=daily'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            repos_data = response.json()
            articles = []
            
            for repo in repos_data[:limit]:
                articles.append({
                    'platform': 'GitHub',
                    'title': repo.get('name', ''),
                    'url': repo.get('url', ''),
                    'description': repo.get('description', ''),
                    'author': repo.get('author', ''),
                    'stars': repo.get('stars', 0),
                    'language': repo.get('language', ''),
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            print(f"✓ 成功获取 {len(articles)} 个GitHub热门项目")
            return articles
            
        except Exception as e:
            print(f"✗ 获取GitHub Trending失败: {str(e)}")
            return []
    
    def fetch_article_content(self, url: str) -> str:
        """
        获取文章正文内容（简化版）
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 简单提取文本内容
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text(separator='\n', strip=True)
            
            # 清理多余空行
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = '\n'.join(lines)
            
            return content
            
        except Exception as e:
            print(f"✗ 获取文章内容失败: {str(e)}")
            return ""
    
    def crawl_all(self, limit=5) -> List[Dict]:
        """
        抓取所有平台的热门内容
        """
        all_articles = []
        
        # Hacker News
        articles = self.fetch_hackernews_top(limit)
        all_articles.extend(articles)
        time.sleep(1)
        
        # Reddit
        articles = self.fetch_reddit_programming(limit)
        all_articles.extend(articles)
        time.sleep(1)
        
        # dev.to
        articles = self.fetch_dev_to_articles(limit)
        all_articles.extend(articles)
        time.sleep(1)
        
        # GitHub
        articles = self.fetch_github_trending(limit)
        all_articles.extend(articles)
        
        return all_articles
    
    def save_to_json(self, articles: List[Dict], filename: str = 'hot_articles.json'):
        """保存文章到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已保存 {len(articles)} 篇文章到 {filename}")


class ArticleRewriter:
    """文章改写器（使用智谱AI）"""
    
    def __init__(self, api_key: str):
        self.api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
        self.api_key = api_key
        
        self.prompts = {
            'full': '请改写以下文章，保持原意但改变表达方式，使其更加流畅自然：\n\n',
            'anti_detection': '''请将以下内容进行深度改写，要求：
1. 改变论证顺序，打破高概率路径
2. 插入低频语义噪声（具体数据、地域特色、时间细节）
3. 频繁交替使用主动/被动语态
4. 将陈述句改为反问、设问
5. 增加句子的复杂度和变化
6. 模仿人类写作的跳跃性思维
7. 避免使用AI常用的高频词汇组合

原文如下：
'''
        }
    
    def rewrite(self, content: str, rewrite_type: str = 'anti_detection', model: str = 'glm-4-flash') -> str:
        """使用AI改写文章"""
        if not content:
            return ""
        
        prompt = self.prompts.get(rewrite_type, self.prompts['full'])
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt + content
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            rewritten = result['choices'][0]['message']['content']
            
            return rewritten
            
        except Exception as e:
            print(f"✗ AI改写失败: {str(e)}")
            return ""


def main():
    """主函数"""
    print("=" * 60)
    print("爆款文章抓取与改写系统")
    print("=" * 60)
    
    # 初始化爬虫
    crawler = SimpleArticleCrawler()
    
    # 抓取热门文章
    print("\n开始抓取热门文章...")
    articles = crawler.crawl_all(limit=3)
    
    if not articles:
        print("✗ 没有抓取到任何文章")
        return
    
    # 保存原始文章
    crawler.save_to_json(articles, 'original_hot_articles.json')
    
    # 显示抓取结果
    print("\n" + "=" * 60)
    print("抓取结果预览：")
    print("=" * 60)
    
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. [{article['platform']}] {article['title']}")
        print(f"   URL: {article['url']}")
        if 'score' in article:
            print(f"   评分: {article['score']}")
    
    # 询问是否获取文章内容
    print("\n" + "=" * 60)
    choice = input("是否获取文章详细内容并改写？(y/n): ").strip().lower()
    
    if choice == 'y':
        # 配置智谱AI
        api_key = 'fc866212e0d64350b837a486e5faf08a.7ZdotggpaC5add3D'
        rewriter = ArticleRewriter(api_key)
        
        print("\n开始获取文章内容并改写...")
        
        rewritten_articles = []
        
        for i, article in enumerate(articles[:3], 1):  # 只处理前3篇
            print(f"\n[{i}/{min(3, len(articles))}] 处理: {article['title']}")
            
            # 获取文章内容
            print("  → 获取文章内容...")
            content = crawler.fetch_article_content(article['url'])
            
            if content:
                article['original_content'] = content[:2000]  # 限制长度
                
                # AI改写
                print("  → AI改写中...")
                rewritten = rewriter.rewrite(content[:2000], 'anti_detection')
                
                if rewritten:
                    article['rewritten_content'] = rewritten
                    rewritten_articles.append(article)
                    print("  ✓ 改写完成")
                else:
                    print("  ✗ 改写失败")
            else:
                print("  ✗ 获取内容失败")
            
            time.sleep(2)  # 避免请求过快
        
        # 保存改写结果
        if rewritten_articles:
            crawler.save_to_json(rewritten_articles, 'rewritten_articles.json')
            
            print("\n" + "=" * 60)
            print("改写完成！")
            print("=" * 60)
            print(f"原始文章: original_hot_articles.json")
            print(f"改写文章: rewritten_articles.json")
            
            # 显示改写示例
            if rewritten_articles:
                print("\n改写示例：")
                print("-" * 60)
                sample = rewritten_articles[0]
                print(f"标题: {sample['title']}")
                print(f"\n原文片段:\n{sample.get('original_content', '')[:300]}...")
                print(f"\n改写后:\n{sample.get('rewritten_content', '')[:300]}...")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
