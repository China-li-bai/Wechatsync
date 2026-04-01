#!/usr/bin/env node

const publishers = {
  'juejin.cn': {
    name: '掘金',
    selectors: {
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn, button[class*="confirm"]',
      successIndicator: '/post/'
    }
  },
  'zhuanlan.zhihu.com': {
    name: '知乎',
    selectors: {
      publishButton: '.PublishPanel-publishButton, button[class*="Publish"]',
      confirmButton: '.Modal-confirmButton, button[class*="confirm"]',
      successIndicator: '/p/'
    }
  },
  'jianshu.com': {
    name: '简书',
    selectors: {
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn',
      successIndicator: '/p/'
    }
  },
  'mp.weixin.qq.com': {
    name: '微信公众号',
    selectors: {
      publishButton: '#js_submit, .weui-desktop-btn_primary',
      confirmButton: '.weui-desktop-dialog__btn_primary',
      successIndicator: 'mp.weixin.qq.com'
    }
  },
  'mp.toutiao.com': {
    name: '头条号',
    selectors: {
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn',
      successIndicator: 'profile_v4'
    }
  }
}

async function publish(draftUrl) {
  const url = new URL(draftUrl)
  const hostname = url.hostname
  
  const config = publishers[hostname]
  if (!config) {
    throw new Error(`不支持的平台: ${hostname}`)
  }
  
  console.log(`开始自动发布到 ${config.name}...`)
  
  const { exec } = require('child_process')
  const { promisify } = require('util')
  const execAsync = promisify(exec)
  
  try {
    await execAsync(`agent-browser open "${draftUrl}"`)
    console.log('✓ 打开草稿页面')
    
    await sleep(3000)
    
    const snapshot = await execAsync('agent-browser snapshot -i')
    console.log('✓ 获取页面快照')
    
    const publishMatch = snapshot.stdout.match(/(@e\d+).*${config.selectors.publishButton}/)
    if (!publishMatch) {
      throw new Error('未找到发布按钮')
    }
    
    await execAsync(`agent-browser click ${publishMatch[1]}`)
    console.log('✓ 点击发布按钮')
    
    await sleep(1000)
    
    if (config.selectors.confirmButton) {
      const confirmSnapshot = await execAsync('agent-browser snapshot -i')
      const confirmMatch = confirmSnapshot.stdout.match(/(@e\d+).*${config.selectors.confirmButton}/)
      
      if (confirmMatch) {
        await execAsync(`agent-browser click ${confirmMatch[1]}`)
        console.log('✓ 确认发布')
      }
    }
    
    await sleep(2000)
    
    const currentUrl = await execAsync('agent-browser url')
    if (currentUrl.stdout.includes(config.selectors.successIndicator)) {
      console.log('✓ 发布成功!')
      console.log(`文章链接: ${currentUrl.stdout.trim()}`)
      
      await execAsync('agent-browser close')
      return {
        success: true,
        url: currentUrl.stdout.trim()
      }
    } else {
      throw new Error('发布可能未成功，请检查页面')
    }
  } catch (error) {
    console.error('✗ 发布失败:', error.message)
    await execAsync('agent-browser close')
    throw error
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

if (require.main === module) {
  const draftUrl = process.argv[2]
  if (!draftUrl) {
    console.error('用法: node auto-publish.js <草稿链接>')
    process.exit(1)
  }
  
  publish(draftUrl)
    .then(result => {
      console.log('\n发布结果:', result)
      process.exit(0)
    })
    .catch(error => {
      console.error('\n发布失败:', error.message)
      process.exit(1)
    })
}

module.exports = { publish, publishers }
