#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 获取热门文章并改写
"""

import requests
import json
import time

def test_hackernews():
    """测试Hacker News API"""
    print("=" * 60)
    print("测试Hacker News API")
    print("=" * 60)
    
    try:
        # 获取热门文章ID
        url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        response = requests.get(url, timeout=10)
        story_ids = response.json()[:5]
        
        print(f"✓ 获取到 {len(story_ids)} 个热门文章ID")
        
        articles = []
        for story_id in story_ids:
            story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
            story_response = requests.get(story_url, timeout=10)
            story_data = story_response.json()
            
            if story_data:
                articles.append({
                    'title': story_data.get('title', ''),
                    'url': story_data.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                    'score': story_data.get('score', 0)
                })
            
            time.sleep(0.1)
        
        print("\n热门文章：")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']} (评分: {article['score']})")
            print(f"   URL: {article['url']}")
        
        return articles
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return []


def test_dev_to():
    """测试dev.to API"""
    print("\n" + "=" * 60)
    print("测试dev.to API")
    print("=" * 60)
    
    try:
        url = 'https://dev.to/api/articles?per_page=5&top=7'
        response = requests.get(url, timeout=10)
        articles_data = response.json()
        
        print(f"✓ 获取到 {len(articles_data)} 篇热门文章")
        
        print("\n热门文章：")
        for i, article in enumerate(articles_data, 1):
            print(f"{i}. {article['title']}")
            print(f"   作者: {article['user']['name']}")
            print(f"   反应数: {article['positive_reactions_count']}")
            print(f"   URL: {article['url']}")
        
        return articles_data
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return []


def test_reddit():
    """测试Reddit API"""
    print("\n" + "=" * 60)
    print("测试Reddit API")
    print("=" * 60)
    
    try:
        url = 'https://www.reddit.com/r/programming/hot.json'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        posts = data['data']['children'][:5]
        print(f"✓ 获取到 {len(posts)} 篇热门帖子")
        
        print("\n热门帖子：")
        for i, post in enumerate(posts, 1):
            post_data = post['data']
            print(f"{i}. {post_data['title']}")
            print(f"   评分: {post_data['score']}")
            print(f"   URL: {post_data['url']}")
        
        return posts
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return []


def test_zhipu_ai():
    """测试智谱AI改写"""
    print("\n" + "=" * 60)
    print("测试智谱AI改写")
    print("=" * 60)
    
    api_key = 'fc866212e0d64350b837a486e5faf08a.7ZdotggpaC5add3D'
    api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    
    test_text = """
    Python是一种广泛使用的编程语言，具有简单易学、功能强大的特点。
    它被广泛应用于Web开发、数据科学、人工智能等领域。
    Python的语法简洁明了，非常适合初学者学习。
    """
    
    prompt = f"""请将以下内容进行深度改写，要求：
1. 改变论证顺序，打破高概率路径
2. 插入低频语义噪声（具体数据、地域特色、时间细节）
3. 频繁交替使用主动/被动语态
4. 将陈述句改为反问、设问
5. 增加句子的复杂度和变化

原文如下：
{test_text}
"""
    
    data = {
        "model": "glm-4-flash",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("正在调用智谱AI...")
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if 'choices' in result:
            rewritten = result['choices'][0]['message']['content']
            
            print("\n原文：")
            print(test_text.strip())
            print("\n改写后：")
            print(rewritten)
            
            return rewritten
        else:
            print(f"✗ API返回错误: {result}")
            return None
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return None


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("开始测试各个API")
    print("=" * 60)
    
    # 测试Hacker News
    hn_articles = test_hackernews()
    
    # 测试dev.to
    dev_articles = test_dev_to()
    
    # 测试Reddit
    reddit_posts = test_reddit()
    
    # 测试智谱AI
    ai_result = test_zhipu_ai()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✓ Hacker News: {len(hn_articles)} 篇文章")
    print(f"✓ dev.to: {len(dev_articles)} 篇文章")
    print(f"✓ Reddit: {len(reddit_posts)} 篇帖子")
    print(f"✓ 智谱AI: {'成功' if ai_result else '失败'}")
    
    print("\n所有测试完成！")


if __name__ == '__main__':
    main()
