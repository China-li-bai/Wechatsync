/**
 * AI 文章改写示例
 * 
 * 这个示例展示如何使用 AI 改写文章并同步到多个平台
 */

import { ArticleRewriter, type RewriteStyle } from './rewriter'

// 示例文章
const exampleArticle = {
  title: 'Ractor 下多线程 Ruby 程序指南',
  content: `
    <p>什么是 Ractor?</p>
    <p>Ractor 是 Ruby 3 新引入的特性。Ractor 顾名思义是 Ruby 和 Actor 的组合，
    它提供了一种在 Ruby 中实现真正并行执行的方式。</p>
    <p>在传统的 Ruby 程序中，由于 GIL (Global Interpreter Lock) 的存在，
    多线程并不能真正实现并行执行。而 Ractor 通过隔离内存空间，
    允许多个 Ractor 同时执行，从而实现真正的并行。</p>
  `,
  cover: 'https://example.com/cover.jpg'
}

async function demo() {
  // 1. 创建改写器
  const rewriter = new ArticleRewriter('openai', process.env.OPENAI_API_KEY!)
  
  // 2. 改写文章（专业风格）
  console.log('改写文章（专业风格）...')
  const professional = await rewriter.rewrite(exampleArticle, {
    style: 'professional',
    preserveStructure: true
  })
  console.log('改写结果:', professional)
  
  // 3. 改写文章（轻松风格）
  console.log('\n改写文章（轻松风格）...')
  const casual = await rewriter.rewrite(exampleArticle, {
    style: 'casual'
  })
  console.log('改写结果:', casual)
  
  // 4. 改写文章（创意风格）
  console.log('\n改写文章（创意风格）...')
  const creative = await rewriter.rewrite(exampleArticle, {
    style: 'creative'
  })
  console.log('改写结果:', creative)
  
  // 5. 改写文章（简洁风格）
  console.log('\n改写文章（简洁风格）...')
  const concise = await rewriter.rewrite(exampleArticle, {
    style: 'concise'
  })
  console.log('改写结果:', concise)
}

// 运行示例
if (require.main === module) {
  demo().catch(console.error)
}

export { demo }
