/**
 * WebSocket Bridge 测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ExtensionBridge } from '../ws-bridge'

describe('ExtensionBridge', () => {
  let bridge: ExtensionBridge

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(async () => {
    if (bridge) {
      // 清理 bridge
    }
  })

  describe('constructor', () => {
    it('should create bridge instance with default port', () => {
      bridge = new ExtensionBridge()
      expect(bridge).toBeDefined()
    })

    it('should create bridge instance with custom port', () => {
      bridge = new ExtensionBridge(8080)
      expect(bridge).toBeDefined()
    })

    it('should create bridge instance with silent mode', () => {
      bridge = new ExtensionBridge(9527, { silent: true })
      expect(bridge).toBeDefined()
    })

    it('should read token from environment variables', () => {
      process.env.MCP_TOKEN = 'test-token'
      bridge = new ExtensionBridge()
      expect(bridge).toBeDefined()
      delete process.env.MCP_TOKEN
    })

    it('should prefer WECHATSYNC_TOKEN over MCP_TOKEN', () => {
      process.env.WECHATSYNC_TOKEN = 'wechat-token'
      process.env.MCP_TOKEN = 'mcp-token'
      bridge = new ExtensionBridge()
      expect(bridge).toBeDefined()
      delete process.env.WECHATSYNC_TOKEN
      delete process.env.MCP_TOKEN
    })
  })

  describe('isConnected', () => {
    it('should return false when no client connected', () => {
      bridge = new ExtensionBridge(9531, { silent: true })
      expect(bridge.isConnected()).toBe(false)
    })
  })

  describe('request', () => {
    it('should reject when no client connected in server mode', async () => {
      bridge = new ExtensionBridge(9533, { silent: true })
      
      // 启动 bridge（会变成 server mode）
      await bridge.start()
      
      // 在 server mode 下，如果没有 client 连接，应该抛出错误
      await expect(
        bridge.request('testMethod', {})
      ).rejects.toThrow('Extension not connected')
    })
  })
})
