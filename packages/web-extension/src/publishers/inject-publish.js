(function() {
  const publishers = {
    'juejin.cn': {
      name: '掘金',
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn, button[class*="confirm"]',
      successUrl: '/post/'
    },
    'zhuanlan.zhihu.com': {
      name: '知乎',
      publishButton: '.PublishPanel-publishButton, button[class*="Publish"]',
      confirmButton: '.Modal-confirmButton, button[class*="confirm"]',
      successUrl: '/p/'
    },
    'jianshu.com': {
      name: '简书',
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn',
      successUrl: '/p/'
    },
    'mp.weixin.qq.com': {
      name: '微信公众号',
      publishButton: '#js_submit, .weui-desktop-btn_primary',
      confirmButton: '.weui-desktop-dialog__btn_primary',
      successUrl: 'mp.weixin.qq.com'
    },
    'mp.toutiao.com': {
      name: '头条号',
      publishButton: '.publish-btn, button[class*="publish"]',
      confirmButton: '.confirm-btn',
      successUrl: 'profile_v4'
    }
  }

  function getPublisherConfig() {
    const hostname = window.location.hostname
    return publishers[hostname]
  }

  function injectPublishButton() {
    const config = getPublisherConfig()
    if (!config) return

    const existingBtn = document.getElementById('syncer-auto-publish')
    if (existingBtn) return

    const btn = document.createElement('button')
    btn.id = 'syncer-auto-publish'
    btn.innerHTML = '🚀 一键发布'
    btn.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 99999;
      padding: 12px 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: bold;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
      transition: all 0.3s ease;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    `

    btn.onmouseenter = () => {
      btn.style.transform = 'translateY(-2px)'
      btn.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)'
    }

    btn.onmouseleave = () => {
      btn.style.transform = 'translateY(0)'
      btn.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
    }

    btn.onclick = async () => {
      btn.disabled = true
      btn.innerHTML = '⏳ 发布中...'
      btn.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'

      try {
        await autoPublish(config)
        btn.innerHTML = '✅ 发布成功'
        btn.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'

        setTimeout(() => {
          btn.remove()
        }, 2000)
      } catch (e) {
        btn.innerHTML = '❌ 发布失败'
        btn.style.background = 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)'
        console.error('autoPublish error', e)

        setTimeout(() => {
          btn.disabled = false
          btn.innerHTML = '🚀 一键发布'
          btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }, 2000)
      }
    }

    document.body.appendChild(btn)
    console.log(`[WechatSync] 已注入"一键发布"按钮 - ${config.name}`)
  }

  async function autoPublish(config) {
    const publishBtn = document.querySelector(config.publishButton)
    if (!publishBtn) {
      throw new Error('未找到发布按钮')
    }

    publishBtn.click()
    console.log('[WechatSync] 点击发布按钮')

    await sleep(1000)

    if (config.confirmButton) {
      const confirmBtn = document.querySelector(config.confirmButton)
      if (confirmBtn) {
        confirmBtn.click()
        console.log('[WechatSync] 确认发布')
      }
    }

    await sleep(2000)

    if (!window.location.href.includes(config.successUrl)) {
      throw new Error('发布可能未成功，请检查页面')
    }

    console.log('[WechatSync] 发布成功:', window.location.href)
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(injectPublishButton, 1000)
    })
  } else {
    setTimeout(injectPublishButton, 1000)
  }
})()
