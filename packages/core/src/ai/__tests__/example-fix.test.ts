/**
 * 验证示例文件的修复
 */

import { ArticleRewriter } from '../rewriter'

async function testExample() {
  // 测试正确的构造函数调用
  console.log('测试 ArticleRewriter 构造函数...')
  
  const rewriter = new ArticleRewriter({
    provider: 'openai',
    apiKey: 'test-api-key',
    model: 'gpt-4-turbo-preview'
  })
  
  console.log('✅ ArticleRewriter 构造函数调用成功！')
  console.log('Provider:', rewriter)
  
  // 验证实例创建成功
  if (!rewriter) {
    throw new Error('ArticleRewriter 实例创建失败')
  }
  
  console.log('✅ 所有测试通过！')
}

testExample().catch(console.error)
