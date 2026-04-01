#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爆款文章抓取与改写系统
支持：今日头条、知乎、简书、微信公众号等平台
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict

class HotArticleCrawler:
    """爆款文章爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_toutiao_hot(self, limit=10) -> List[Dict]:
        """
        抓取今日头条热榜
        
        Args:
            limit: 返回文章数量，默认10篇
        
        Returns:
            热门文章列表
        """
        print("正在抓取今日头条热榜...")
        
        url = 'https://www.toutiao.com/ch/news_hot/'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 提取热榜标题和链接
            items = soup.select('.title-box a')[:limit]
            
            for item in items:
                title = item.text.strip()
                url = 'https://www.toutiao.com' + item.get('href', '')
                
                if title and url:
                    articles.append({
                        'platform': '今日头条',
                        'title': title,
                        'url': url,
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            print(f"✓ 成功抓取 {len(articles)} 篇今日头条热榜文章")
            return articles
            
        except Exception as e:
            print(f"✗ 抓取今日头条失败: {str(e)}")
            return []
    
    def fetch_zhihu_hot(self, limit=10) -> List[Dict]:
        """
        抓取知乎热榜
        
        Args:
            limit: 返回文章数量，默认10篇
        
        Returns:
            热门文章列表
        """
        print("正在抓取知乎热榜...")
        
        url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total'
        
        try:
            # 注意：知乎可能需要cookie，请根据实际情况配置
            headers = self.headers.copy()
            headers['Cookie'] = 'your_zhihu_cookie_here'  # 替换为你的cookie
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('data', [])[:limit]:
                target = item.get('target', {})
                
                articles.append({
                    'platform': '知乎',
                    'title': target.get('title', ''),
                    'url': target.get('url', ''),
                    'hot_score': item.get('detail_text', ''),
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            print(f"✓ 成功抓取 {len(articles)} 条知乎热榜")
            return articles
            
        except Exception as e:
            print(f"✗ 抓取知乎失败: {str(e)}")
            return []
    
    def fetch_jianshu_hot(self, limit=10) -> List[Dict]:
        """
        抓取简书热门文章
        
        Args:
            limit: 返回文章数量，默认10篇
        
        Returns:
            热门文章列表
        """
        print("正在抓取简书热门文章...")
        
        url = 'https://www.jianshu.com'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 提取热门文章标题和链接
            items = soup.select('a.title')[:limit]
            
            for item in items:
                title = item.text.strip()
                url = 'https://www.jianshu.com' + item.get('href', '')
                
                if title and url:
                    articles.append({
                        'platform': '简书',
                        'title': title,
                        'url': url,
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            print(f"✓ 成功抓取 {len(articles)} 篇简书热门文章")
            return articles
            
        except Exception as e:
            print(f"✗ 抓取简书失败: {str(e)}")
            return []
    
    def fetch_weixin_articles(self, keyword='Python', limit=10) -> List[Dict]:
        """
        通过搜狗微信抓取公众号文章
        
        Args:
            keyword: 搜索关键词
            limit: 返回文章数量，默认10篇
        
        Returns:
            文章列表
        """
        print(f"正在搜索微信公众号文章（关键词：{keyword}）...")
        
        url = f'https://weixin.sogou.com/weixin?type=2&query={keyword}'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 提取文章标题和链接
            items = soup.select('.txt-box h3 a')[:limit]
            
            for item in items:
                title = item.text.strip()
                url = item.get('href', '')
                
                if title and url:
                    articles.append({
                        'platform': '微信公众号',
                        'title': title,
                        'url': url,
                        'keyword': keyword,
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            print(f"✓ 成功抓取 {len(articles)} 篇微信公众号文章")
            return articles
            
        except Exception as e:
            print(f"✗ 抓取微信公众号失败: {str(e)}")
            return []
    
    def fetch_article_content(self, url: str) -> str:
        """
        获取文章正文内容
        
        Args:
            url: 文章URL
        
        Returns:
            文章正文内容
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种选择器提取正文
            selectors = [
                'article',
                '.article-content',
                '.content',
                '#content',
                '.post-content',
                '.entry-content'
            ]
            
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    # 清理HTML标签
                    text = content.get_text(separator='\n', strip=True)
                    return text
            
            return ""
            
        except Exception as e:
            print(f"✗ 获取文章内容失败: {str(e)}")
            return ""
    
    def crawl_all_platforms(self, limit=5) -> List[Dict]:
        """
        抓取所有平台的热门文章
        
        Args:
            limit: 每个平台抓取的文章数量
        
        Returns:
            所有热门文章列表
        """
        all_articles = []
        
        # 抓取今日头条
        articles = self.fetch_toutiao_hot(limit)
        all_articles.extend(articles)
        time.sleep(random.uniform(1, 3))  # 随机延迟
        
        # 抓取知乎
        articles = self.fetch_zhihu_hot(limit)
        all_articles.extend(articles)
        time.sleep(random.uniform(1, 3))
        
        # 抓取简书
        articles = self.fetch_jianshu_hot(limit)
        all_articles.extend(articles)
        
        return all_articles
    
    def save_to_json(self, articles: List[Dict], filename: str = 'hot_articles.json'):
        """
        保存文章到JSON文件
        
        Args:
            articles: 文章列表
            filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已保存 {len(articles)} 篇文章到 {filename}")
    
    def save_to_csv(self, articles: List[Dict], filename: str = 'hot_articles.csv'):
        """
        保存文章到CSV文件
        
        Args:
            articles: 文章列表
            filename: 文件名
        """
        import pandas as pd
        
        df = pd.DataFrame(articles)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"✓ 已保存 {len(articles)} 篇文章到 {filename}")


class ArticleRewriter:
    """文章改写器（使用智谱AI）"""
    
    def __init__(self, api_key: str):
        """
        初始化改写器
        
        Args:
            api_key: 智谱AI的API密钥
        """
        self.api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
        self.api_key = api_key
        
        self.prompts = {
            'full': '请改写以下文章，保持原意但改变表达方式，使其更加流畅自然：\n\n',
            'title': '请改写以下文章标题，使其更加吸引人：\n\n',
            'summary': '请为以下文章生成一个简洁的摘要（100字以内）：\n\n',
            'expand': '请扩展以下文章内容，增加更多细节和例子：\n\n',
            'simplify': '请简化以下文章，使其更易理解：\n\n',
            'professional': '请将以下文章改写为更专业的技术文章风格：\n\n',
            'casual': '请将以下文章改写为更轻松的博客风格：\n\n'
        }
    
    def rewrite(self, content: str, rewrite_type: str = 'full', model: str = 'glm-4-flash') -> str:
        """
        使用AI改写文章
        
        Args:
            content: 原始内容
            rewrite_type: 改写类型
            model: AI模型
        
        Returns:
            改写后的内容
        """
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
            
            return rewritten.strip()
            
        except Exception as e:
            print(f"✗ AI改写失败: {str(e)}")
            return ""
    
    def batch_rewrite(self, articles: List[Dict], rewrite_type: str = 'title') -> List[Dict]:
        """
        批量改写文章标题
        
        Args:
            articles: 文章列表
            rewrite_type: 改写类型
        
        Returns:
            改写后的文章列表
        """
        rewritten_articles = []
        
        for i, article in enumerate(articles):
            print(f"正在改写第 {i+1}/{len(articles)} 篇: {article.get('title', '')[:30]}...")
            
            # 改写标题
            original_title = article.get('title', '')
            rewritten_title = self.rewrite(original_title, rewrite_type)
            
            # 创建新的文章对象
            new_article = article.copy()
            new_article['original_title'] = original_title
            new_article['rewritten_title'] = rewritten_title
            
            rewritten_articles.append(new_article)
            
            # 避免请求过快
            time.sleep(1)
        
        return rewritten_articles


def main():
    """主函数"""
    print("=" * 60)
    print("爆款文章抓取与改写系统")
    print("=" * 60)
    
    # 创建爬虫实例
    crawler = HotArticleCrawler()
    
    # 抓取所有平台的热门文章
    print("\n开始抓取热门文章...\n")
    articles = crawler.crawl_all_platforms(limit=5)
    
    if not articles:
        print("未抓取到任何文章")
        return
    
    # 保存原始文章
    print("\n保存原始文章...")
    crawler.save_to_json(articles, 'original_hot_articles.json')
    crawler.save_to_csv(articles, 'original_hot_articles.csv')
    
    # 改写文章（可选）
    print("\n" + "=" * 60)
    print("是否要使用AI改写文章标题？(y/n): ", end='')
    
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n请输入智谱AI的API密钥: ", end='')
        api_key = input().strip()
        
        if api_key:
            rewriter = ArticleRewriter(api_key)
            
            print("\n开始改写文章标题...\n")
            rewritten_articles = rewriter.batch_rewrite(articles, rewrite_type='title')
            
            # 保存改写后的文章
            print("\n保存改写后的文章...")
            crawler.save_to_json(rewritten_articles, 'rewritten_hot_articles.json')
            crawler.save_to_csv(rewritten_articles, 'rewritten_hot_articles.csv')
            
            print("\n改写完成！")
        else:
            print("未提供API密钥，跳过改写步骤")
    
    print("\n" + "=" * 60)
    print("所有任务完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
