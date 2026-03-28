# 爆款文章发现与改写系统

## 📌 系统概述

这是一个完整的爆款文章发现、改写、发布系统，帮助你快速获取热点内容并改写发布。

## 🎯 核心功能

1. **热点文章抓取**：支持多平台热榜抓取
2. **AI智能改写**：保持原意，改变表达
3. **一键发布**：同步到多个平台

## 📊 支持平台

### 抓取平台
- ✅ 今日头条热榜
- ✅ 知乎热榜
- ✅ 简书热门
- ✅ 微信公众号（通过搜狗）
- ✅ 小红书爆款笔记
- ✅ 微博热搜

### 发布平台
- ✅ 微信公众号
- ✅ 知乎
- ✅ 掘金
- ✅ 简书
- ✅ 头条号
- ✅ 小红书

## 🔧 方案选择

### 方案1：Coze智能体工作流（推荐）

**适合人群**：非技术人员、快速上手

**优势**：
- 可视化操作，无需编程
- 1分钟抓取500+爆款笔记
- 自动同步到飞书表格
- 支持多平台

**使用步骤**：
1. 访问 [Coze平台](https://www.coze.cn/)
2. 创建智能体工作流
3. 配置小红书搜索节点
4. 设置循环节点获取详情
5. 添加数据格式化节点
6. 配置飞书表格同步

**参考教程**：
- [1分钟抓取500+小红书爆款笔记](https://juejin.cn/post/7548595210564059151)

### 方案2：Python爬虫 + AI改写

**适合人群**：开发者、需要定制化

**优势**：
- 完全开源免费
- 可自定义抓取规则
- 可集成到现有系统
- 支持批量处理

**技术栈**：
- Python 3.8+
- requests / selenium
- BeautifulSoup4
- Vercel AI SDK（已集成）

## 💻 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 pandas
```

### 2. 抓取今日头条热榜

```python
import requests
from bs4 import BeautifulSoup

url = 'https://www.toutiao.com/ch/news_hot/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取热榜标题和链接
hot_articles = []
for item in soup.select('.title-box a'):
    hot_articles.append({
        'title': item.text.strip(),
        'url': 'https://www.toutiao.com' + item['href']
    })

print(f"抓取到 {len(hot_articles)} 篇热门文章")
```

### 3. 抓取知乎热榜

```python
import requests

url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total'
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Cookie': '你的知乎cookie'
}

response = requests.get(url, headers=headers)
data = response.json()

hot_list = []
for item in data['data']:
    hot_list.append({
        'rank': item['target']['id'],
        'title': item['target']['title'],
        'url': item['target']['url'],
        'hot_score': item['detail_text']
    })

print(f"抓取到 {len(hot_list)} 条知乎热榜")
```

### 4. 抓取小红书爆款笔记

**方法1：使用Coze智能体（推荐）**
- 无需编程
- 1分钟抓取500+笔记
- 自动同步到表格

**方法2：Python爬虫**
```python
# 需要配置cookie和代理
# 建议使用Coze智能体工作流
```

### 5. AI改写文章

**使用已集成的Vercel AI SDK**：

```javascript
import { rewriteContent } from './ai-service.js'

const rewritten = await rewriteContent({
  provider: 'zhipu',  // 使用智谱AI
  apiKey: 'your-api-key',
  model: 'glm-4-flash',
  rewriteType: 'full',  // 全文改写
  content: originalContent
})

console.log(rewritten)
```

**改写模式**：
- `full`: 全文改写
- `title`: 标题改写
- `summary`: 生成摘要
- `expand`: 内容扩展
- `simplify`: 内容简化
- `professional`: 专业风格
- `casual`: 轻松风格

## 📝 完整工作流示例

### Python版本

```python
import requests
from bs4 import BeautifulSoup
import json

class HotArticleRewriter:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.ai_api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
        self.ai_api_key = 'your-zhipu-api-key'
    
    def fetch_toutiao_hot(self):
        """抓取今日头条热榜"""
        url = 'https://www.toutiao.com/ch/news_hot/'
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for item in soup.select('.title-box a')[:10]:  # 取前10篇
            articles.append({
                'title': item.text.strip(),
                'url': 'https://www.toutiao.com' + item['href']
            })
        return articles
    
    def fetch_article_content(self, url):
        """获取文章内容"""
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 提取正文内容（需要根据具体网站调整）
        content = soup.select_one('article')
        return content.text if content else ''
    
    def rewrite_with_ai(self, content, rewrite_type='full'):
        """使用AI改写"""
        prompts = {
            'full': '请改写以下文章，保持原意但改变表达方式：\n\n',
            'title': '请改写以下标题，使其更吸引人：\n\n',
            'summary': '请为以下文章生成摘要（100字以内）：\n\n'
        }
        
        data = {
            "model": "glm-4-flash",
            "messages": [
                {
                    "role": "user",
                    "content": prompts[rewrite_type] + content
                }
            ],
            "temperature": 0.7
        }
        
        headers = {
            'Authorization': f'Bearer {self.ai_api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            self.ai_api_url,
            headers=headers,
            json=data
        )
        
        return response.json()['choices'][0]['message']['content']
    
    def process_hot_articles(self):
        """处理热门文章"""
        print("正在抓取今日头条热榜...")
        articles = self.fetch_toutiao_hot()
        
        results = []
        for i, article in enumerate(articles[:5]):  # 处理前5篇
            print(f"\n处理第 {i+1} 篇: {article['title']}")
            
            # 获取文章内容
            content = self.fetch_article_content(article['url'])
            
            if content:
                # AI改写
                print("  正在AI改写...")
                rewritten = self.rewrite_with_ai(content[:1000])  # 限制长度
                
                results.append({
                    'original_title': article['title'],
                    'original_url': article['url'],
                    'rewritten_content': rewritten
                })
                
                print(f"  ✓ 改写完成")
        
        return results

# 使用示例
if __name__ == '__main__':
    rewriter = HotArticleRewriter()
    results = rewriter.process_hot_articles()
    
    # 保存结果
    with open('rewritten_articles.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！共处理 {len(results)} 篇文章")
```

## 🎨 高级功能

### 1. 批量改写

```python
def batch_rewrite(articles, rewrite_type='full'):
    """批量改写文章"""
    results = []
    for article in articles:
        rewritten = rewrite_with_ai(article['content'], rewrite_type)
        results.append({
            'original': article,
            'rewritten': rewritten
        })
    return results
```

### 2. 定时抓取

```python
import schedule
import time

def job():
    print("开始抓取热榜...")
    rewriter = HotArticleRewriter()
    results = rewriter.process_hot_articles()
    # 保存或发送通知

# 每6小时抓取一次
schedule.every(6).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### 3. 数据分析

```python
import pandas as pd

def analyze_articles(articles):
    """分析文章数据"""
    df = pd.DataFrame(articles)
    
    # 统计标题长度分布
    df['title_length'] = df['title'].apply(len)
    
    # 找出最热门的文章
    top_articles = df.nlargest(10, 'hot_score')
    
    return {
        'total': len(df),
        'avg_title_length': df['title_length'].mean(),
        'top_articles': top_articles.to_dict('records')
    }
```

## 📊 数据存储

### 存储到CSV

```python
import pandas as pd

df = pd.DataFrame(rewritten_articles)
df.to_csv('hot_articles.csv', index=False, encoding='utf-8-sig')
```

### 存储到MongoDB

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['hot_articles']
collection = db['articles']

collection.insert_many(rewritten_articles)
```

### 同步到飞书表格

使用Coze智能体工作流自动同步。

## ⚠️ 注意事项

### 法律合规
- 遵守robots.txt协议
- 不要过度请求，避免影响网站正常运行
- 不抓取个人隐私数据
- 商业使用需获得授权

### 技术要点
- 设置合理的请求间隔（3-5秒）
- 使用代理IP防止被封
- 处理异常和错误
- 数据去重和清洗

### 改写质量
- 保持原文核心观点
- 改变表达方式和句式
- 增加个人见解和分析
- 避免直接复制粘贴

## 🔗 相关资源

### 开源项目
- [AiToEarn](https://github.com/...) - 10.9K Stars，全流程内容营销工具
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui) - 本地AI文本生成
- [LangChain](https://github.com/langchain-ai/langchain) - AI应用开发框架

### API文档
- [智谱AI API](https://open.bigmodel.cn/)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
- [Coze智能体平台](https://www.coze.cn/)

### 教程
- [Python爬虫实战：3行代码抓取爆款文章](https://blog.csdn.net/m0_37649480/article/details/148589432)
- [Coze智能体工作流教程](https://juejin.cn/post/7548595210564059151)

## 🚀 快速开始

### 非技术用户
1. 使用Coze智能体工作流
2. 配置关键词和平台
3. 一键抓取爆款笔记
4. 使用MD编辑器AI改写
5. 发布到多个平台

### 技术用户
1. 安装Python依赖
2. 配置API密钥
3. 运行爬虫脚本
4. 批量AI改写
5. 自动发布

## 💡 最佳实践

1. **热点追踪**：每天定时抓取热榜，保持内容新鲜度
2. **质量把控**：AI改写后人工审核，确保质量
3. **原创性**：添加个人观点和分析，避免纯搬运
4. **数据分析**：跟踪发布效果，优化内容策略
5. **合规运营**：遵守平台规则，避免违规

## 📈 效果预期

- **效率提升**：从手动2小时 → 自动化10分钟
- **内容质量**：AI改写 + 人工优化
- **覆盖范围**：单平台 → 多平台同步
- **数据驱动**：基于热榜数据选题

---

**开始你的爆款内容之旅吧！** 🎉
