#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化爆款文章抓取与改写流程
无需交互，全自动运行
"""

import requests
import json
import time
import os
from datetime import datetime

class AutoArticleProcessor:
    """自动化文章处理器"""
    
    def __init__(self, zhipu_api_key):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.zhipu_api_key = zhipu_api_key
        self.zhipu_api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
        
        # 创建输出目录
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def fetch_hackernews(self, limit=5):
        """获取Hacker News热门文章"""
        print("📥 正在获取Hacker News热门文章...")
        
        try:
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = self.session.get(url, timeout=10)
            story_ids = response.json()[:limit]
            
            articles = []
            for story_id in story_ids:
                story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                story_response = self.session.get(story_url, timeout=10)
                story_data = story_response.json()
                
                if story_data:
                    articles.append({
                        'platform': 'Hacker News',
                        'title': story_data.get('title', ''),
                        'url': story_data.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                        'score': story_data.get('score', 0),
                        'by': story_data.get('by', '')
                    })
                
                time.sleep(0.1)
            
            print(f"✓ 成功获取 {len(articles)} 篇Hacker News文章")
            return articles
            
        except Exception as e:
            print(f"✗ 获取Hacker News失败: {str(e)}")
            return []
    
    def fetch_dev_to(self, limit=5):
        """获取dev.to热门文章"""
        print("📥 正在获取dev.to热门文章...")
        
        try:
            url = f'https://dev.to/api/articles?per_page={limit}&top=7'
            response = self.session.get(url, timeout=10)
            articles_data = response.json()
            
            articles = []
            for article in articles_data:
                articles.append({
                    'platform': 'dev.to',
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'description': article.get('description', ''),
                    'author': article.get('user', {}).get('name', ''),
                    'reactions': article.get('positive_reactions_count', 0)
                })
            
            print(f"✓ 成功获取 {len(articles)} 篇dev.to文章")
            return articles
            
        except Exception as e:
            print(f"✗ 获取dev.to失败: {str(e)}")
            return []
    
    def fetch_article_content(self, url):
        """获取文章内容"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text(separator='\n', strip=True)
            
            # 清理多余空行
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = '\n'.join(lines)
            
            # 限制长度
            return content[:3000] if len(content) > 3000 else content
            
        except Exception as e:
            print(f"  ✗ 获取内容失败: {str(e)}")
            return ""
    
    def rewrite_with_zhipu(self, content, mode='anti_detection'):
        """使用智谱AI改写"""
        if not content:
            return ""
        
        prompts = {
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
        
        prompt = prompts.get(mode, prompts['anti_detection'])
        
        data = {
            "model": "glm-4-flash",
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
            'Authorization': f'Bearer {self.zhipu_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                self.zhipu_api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            result = response.json()
            
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            else:
                print(f"  ✗ AI返回错误: {result.get('error', 'Unknown error')}")
                return ""
                
        except Exception as e:
            print(f"  ✗ AI改写失败: {str(e)}")
            return ""
    
    def process_articles(self, articles, max_process=3):
        """处理文章：获取内容并改写"""
        processed = []
        
        for i, article in enumerate(articles[:max_process], 1):
            print(f"\n📝 [{i}/{min(max_process, len(articles))}] 处理: {article['title'][:50]}...")
            
            # 获取文章内容
            print("  → 获取文章内容...")
            content = self.fetch_article_content(article['url'])
            
            if content:
                article['original_content'] = content
                
                # AI改写
                print("  → AI改写中...")
                rewritten = self.rewrite_with_zhipu(content)
                
                if rewritten:
                    article['rewritten_content'] = rewritten
                    processed.append(article)
                    print("  ✓ 改写完成")
                else:
                    print("  ✗ 改写失败")
            else:
                print("  ✗ 获取内容失败")
            
            time.sleep(2)  # 避免请求过快
        
        return processed
    
    def save_results(self, original_articles, processed_articles):
        """保存结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存原始文章
        original_file = os.path.join(self.output_dir, f'original_{timestamp}.json')
        with open(original_file, 'w', encoding='utf-8') as f:
            json.dump(original_articles, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 原始文章已保存: {original_file}")
        
        # 保存改写文章
        if processed_articles:
            processed_file = os.path.join(self.output_dir, f'rewritten_{timestamp}.json')
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_articles, f, ensure_ascii=False, indent=2)
            print(f"✓ 改写文章已保存: {processed_file}")
            
            # 生成Markdown报告
            self.generate_report(processed_articles, timestamp)
    
    def generate_report(self, articles, timestamp):
        """生成Markdown报告"""
        report_file = os.path.join(self.output_dir, f'report_{timestamp}.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 爆款文章改写报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"## {i}. {article['title']}\n\n")
                f.write(f"**平台**: {article['platform']}\n\n")
                f.write(f"**原文链接**: {article['url']}\n\n")
                
                if 'score' in article:
                    f.write(f"**评分**: {article['score']}\n\n")
                elif 'reactions' in article:
                    f.write(f"**反应数**: {article['reactions']}\n\n")
                
                f.write("### 原文片段\n\n")
                f.write("```\n")
                f.write(article.get('original_content', '')[:500] + "...\n")
                f.write("```\n\n")
                
                f.write("### 改写后内容\n\n")
                f.write(article.get('rewritten_content', ''))
                f.write("\n\n---\n\n")
        
        print(f"✓ Markdown报告已生成: {report_file}")
    
    def run(self):
        """运行完整流程"""
        print("=" * 70)
        print("🚀 自动化爆款文章抓取与改写系统")
        print("=" * 70)
        
        # 1. 抓取文章
        print("\n📊 第一步：抓取热门文章")
        print("-" * 70)
        
        all_articles = []
        
        # Hacker News
        hn_articles = self.fetch_hackernews(limit=3)
        all_articles.extend(hn_articles)
        time.sleep(1)
        
        # dev.to
        dev_articles = self.fetch_dev_to(limit=3)
        all_articles.extend(dev_articles)
        
        if not all_articles:
            print("\n❌ 没有抓取到任何文章，程序退出")
            return
        
        print(f"\n✓ 共抓取 {len(all_articles)} 篇文章")
        
        # 2. 处理文章
        print("\n📊 第二步：获取内容并改写")
        print("-" * 70)
        
        processed_articles = self.process_articles(all_articles, max_process=3)
        
        if not processed_articles:
            print("\n❌ 没有成功改写任何文章")
        
        # 3. 保存结果
        print("\n📊 第三步：保存结果")
        print("-" * 70)
        
        self.save_results(all_articles, processed_articles)
        
        # 4. 完成
        print("\n" + "=" * 70)
        print("✅ 完成！")
        print("=" * 70)
        print(f"✓ 原始文章: {len(all_articles)} 篇")
        print(f"✓ 改写文章: {len(processed_articles)} 篇")
        print(f"✓ 输出目录: {self.output_dir}/")
        print("=" * 70)


def main():
    # 智谱AI API密钥
    ZHIPU_API_KEY = 'fc866212e0d64350b837a486e5faf08a.7ZdotggpaC5add3D'
    
    # 创建处理器
    processor = AutoArticleProcessor(ZHIPU_API_KEY)
    
    # 运行
    processor.run()


if __name__ == '__main__':
    main()
