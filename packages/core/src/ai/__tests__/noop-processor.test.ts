/**
 * 验证 NoopAIProcessor 实现
 */

import { NoopAIProcessor } from '../index'
import type { RewriteStyle } from '../index'

async function testNoopAIProcessor() {
  const processor = new NoopAIProcessor()
  
  // 测试 rewriteArticle 方法
  const article = {
    title: '测试标题',
    content: '<p>测试内容</p>',
    cover: 'https://example.com/cover.jpg'
  }
  
  const options = {
    style: 'professional' as RewriteStyle,
    preserveStructure: true
  }
  
  console.log('测试 NoopAIProcessor.rewriteArticle...')
  const result = await processor.rewriteArticle(article, options)
  
  console.log('结果:', result)
  
  // 验证结果
  if (result.title !== article.title) {
    throw new Error('标题不匹配')
  }
  
  if (result.content !== article.content) {
    throw new Error('内容不匹配')
  }
  
  if (result.cover !== article.cover) {
    throw new Error('封面不匹配')
  }
  
  if (result.originalTitle !== article.title) {
    throw new Error('原标题不匹配')
  }
  
  if (result.originalContent !== article.content) {
    throw new Error('原内容不匹配')
  }
  
  if (result.style !== options.style) {
    throw new Error('风格不匹配')
  }
  
  if (!result.timestamp) {
    throw new Error('缺少时间戳')
  }
  
  console.log('✅ 所有测试通过！')
}

testNoopAIProcessor().catch(console.error)
