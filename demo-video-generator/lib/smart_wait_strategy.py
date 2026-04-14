#!/usr/bin/env python3
"""
智能等待策略 v1.0.0
基于Playwright的智能等待和页面状态检测

参考项目:
- Playwright Auto-waiting: https://playwright.io/

技术要点:
- 多策略等待
- 页面加载状态检测
- 网络空闲检测
- 元素就绪检测
- 自定义JavaScript检查
"""

import time
import logging
from typing import Optional, Callable, Dict, Any
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


class SmartWaitStrategy:
    """智能等待策略"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化智能等待策略
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def wait_for_page_ready(self, page: Page, timeout: int = 30000) -> bool:
        """
        等待页面完全加载
        
        策略:
        1. 等待网络空闲
        2. 等待DOM内容加载
        3. 等待页面就绪状态
        4. 检查未完成的请求
        
        Args:
            page: Playwright页面对象
            timeout: 超时时间（毫秒）
        
        Returns:
            是否成功
        """
        self.logger.debug("开始智能等待页面加载...")
        
        try:
            # 策略1: 等待网络空闲
            self._wait_for_network_idle(page, timeout)
            
            # 策略2: 等待DOM内容加载
            page.wait_for_load_state('domcontentloaded', timeout=timeout)
            self.logger.debug("DOM内容加载完成")
            
            # 策略3: 等待页面就绪状态
            page.wait_for_load_state('load', timeout=timeout)
            self.logger.debug("页面加载完成")
            
            # 策略4: 自定义JavaScript检查
            is_ready = self._check_page_ready_with_js(page)
            
            if is_ready:
                self.logger.info("✅ 页面完全加载就绪")
                return True
            else:
                self.logger.warning("⚠️  页面可能未完全加载")
                return True  # 仍然返回True，因为已经等待了足够时间
            
        except PlaywrightTimeoutError:
            self.logger.warning("⚠️  页面加载超时，继续执行")
            return True
        except Exception as e:
            self.logger.error(f"页面加载等待异常: {e}")
            return False
    
    def _wait_for_network_idle(self, page: Page, timeout: int):
        """
        等待网络空闲
        
        Args:
            page: Playwright页面对象
            timeout: 超时时间（毫秒）
        """
        try:
            page.wait_for_load_state('networkidle', timeout=timeout)
            self.logger.debug("网络空闲")
        except PlaywrightTimeoutError:
            self.logger.debug("网络空闲超时，继续执行")
    
    def _check_page_ready_with_js(self, page: Page) -> bool:
        """
        使用JavaScript检查页面就绪状态
        
        Args:
            page: Playwright页面对象
        
        Returns:
            是否就绪
        """
        try:
            is_ready = page.evaluate("""
                () => {
                    // 检查文档就绪状态
                    if (document.readyState !== 'complete') {
                        return false;
                    }
                    
                    // 检查未完成的资源请求
                    const pendingResources = window.performance.getEntriesByType('resource')
                        .filter(r => !r.responseEnd).length;
                    
                    if (pendingResources > 0) {
                        return false;
                    }
                    
                    // 检查未完成的XHR请求
                    const pendingXHR = window.performance.getEntriesByType('resource')
                        .filter(r => r.initiatorType === 'xmlhttprequest' && !r.responseEnd).length;
                    
                    if (pendingXHR > 0) {
                        return false;
                    }
                    
                    return true;
                }
            """)
            
            return is_ready
            
        except Exception as e:
            self.logger.warning(f"JavaScript检查失败: {e}")
            return True
    
    def wait_for_element(self, page: Page, selector: str, 
                        state: str = 'visible', timeout: int = 10000) -> bool:
        """
        等待元素出现
        
        Args:
            page: Playwright页面对象
            selector: CSS选择器
            state: 等待状态
            timeout: 超时时间（毫秒）
        
        Returns:
            是否成功
        """
        try:
            page.wait_for_selector(selector, state=state, timeout=timeout)
            self.logger.debug(f"元素就绪: {selector}")
            return True
        except PlaywrightTimeoutError:
            self.logger.warning(f"元素等待超时: {selector}")
            return False
    
    def smart_scroll(self, page: Page, distance: int = 300, 
                    smooth: bool = True) -> bool:
        """
        智能滚动
        
        Args:
            page: Playwright页面对象
            distance: 滚动距离（像素）
            smooth: 是否平滑滚动
        
        Returns:
            是否到达底部
        """
        try:
            behavior = 'smooth' if smooth else 'auto'
            
            page.evaluate(f"""
                window.scrollBy({{
                    top: {distance},
                    behavior: '{behavior}'
                }});
            """)
            
            # 等待滚动完成
            time.sleep(0.5 if smooth else 0.1)
            
            # 检查是否到达底部
            at_bottom = page.evaluate("""
                () => {
                    return (window.innerHeight + window.scrollY) >= 
                           document.body.offsetHeight - 100;
                }
            """)
            
            if at_bottom:
                self.logger.debug("已到达页面底部")
            
            return at_bottom
            
        except Exception as e:
            self.logger.error(f"滚动失败: {e}")
            return False
    
    def smart_click(self, page: Page, selector: str, 
                   wait_after: int = 1000) -> bool:
        """
        智能点击
        
        Args:
            page: Playwright页面对象
            selector: CSS选择器
            wait_after: 点击后等待时间（毫秒）
        
        Returns:
            是否成功
        """
        try:
            # 等待元素可见
            page.wait_for_selector(selector, state='visible', timeout=10000)
            
            # 等待元素可点击
            page.wait_for_selector(selector, state='enabled', timeout=5000)
            
            # 点击
            page.click(selector)
            
            self.logger.debug(f"点击元素: {selector}")
            
            # 等待响应
            time.sleep(wait_after / 1000)
            
            # 等待网络空闲
            self._wait_for_network_idle(page, timeout=5000)
            
            return True
            
        except PlaywrightTimeoutError:
            self.logger.warning(f"点击元素超时: {selector}")
            return False
        except Exception as e:
            self.logger.error(f"点击失败: {e}")
            return False
    
    def wait_for_navigation(self, page: Page, timeout: int = 30000) -> bool:
        """
        等待页面导航完成
        
        Args:
            page: Playwright页面对象
            timeout: 超时时间（毫秒）
        
        Returns:
            是否成功
        """
        try:
            page.wait_for_load_state('load', timeout=timeout)
            self.logger.debug("页面导航完成")
            return True
        except PlaywrightTimeoutError:
            self.logger.warning("页面导航超时")
            return False
    
    def wait_for_condition(self, page: Page, condition: Callable[[], bool],
                          timeout: int = 30000, poll_interval: int = 500) -> bool:
        """
        等待自定义条件
        
        Args:
            page: Playwright页面对象
            condition: 条件函数
            timeout: 超时时间（毫秒）
            poll_interval: 轮询间隔（毫秒）
        
        Returns:
            是否成功
        """
        start_time = time.time()
        
        while True:
            try:
                if condition():
                    self.logger.debug("条件满足")
                    return True
                
                elapsed = (time.time() - start_time) * 1000
                
                if elapsed >= timeout:
                    self.logger.warning("条件等待超时")
                    return False
                
                time.sleep(poll_interval / 1000)
                
            except Exception as e:
                self.logger.error(f"条件检查失败: {e}")
                return False
    
    def adaptive_wait(self, page: Page, action_type: str, 
                     params: Optional[Dict[str, Any]] = None) -> bool:
        """
        自适应等待
        
        根据动作类型自动选择合适的等待策略
        
        Args:
            page: Playwright页面对象
            action_type: 动作类型
            params: 动作参数
        
        Returns:
            是否成功
        """
        params = params or {}
        
        if action_type == 'navigate':
            return self.wait_for_page_ready(page)
        
        elif action_type == 'scroll':
            distance = params.get('distance', 300)
            smooth = params.get('smooth', True)
            return self.smart_scroll(page, distance, smooth)
        
        elif action_type == 'click':
            selector = params.get('selector')
            if not selector:
                self.logger.error("点击动作缺少selector参数")
                return False
            
            wait_after = params.get('wait_after', 1000)
            return self.smart_click(page, selector, wait_after)
        
        elif action_type == 'wait_for_element':
            selector = params.get('selector')
            if not selector:
                self.logger.error("等待元素动作缺少selector参数")
                return False
            
            state = params.get('state', 'visible')
            timeout = params.get('timeout', 10000)
            return self.wait_for_element(page, selector, state, timeout)
        
        else:
            self.logger.warning(f"未知动作类型: {action_type}")
            return False


class RecordingController:
    """录制控制器 - 集成智能等待"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化录制控制器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.wait_strategy = SmartWaitStrategy(self.logger)
    
    def execute_scene(self, page: Page, scene: Dict[str, Any], duration: float):
        """
        执行场景动作
        
        Args:
            page: Playwright页面对象
            scene: 场景配置
            duration: 场景时长（秒）
        """
        action = scene.get('action', 'screenshot')
        
        self.logger.info(f"执行场景: {scene.get('name', 'unnamed')}")
        
        if action == 'scroll':
            distance = scene.get('scroll_distance', 300)
            self.wait_strategy.smart_scroll(page, distance)
        
        elif action == 'interact':
            selector = scene.get('selector')
            if selector:
                self.wait_strategy.smart_click(page, selector)
        
        elif action == 'scroll_to_top':
            page.evaluate("window.scrollTo(0, 0);")
            time.sleep(0.5)
        
        # 等待场景时长
        time.sleep(duration)


if __name__ == "__main__":
    # 测试代码
    from playwright.sync_api import sync_playwright
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== 智能等待策略测试 ===\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 测试页面加载等待
        print("测试1: 页面加载等待")
        page.goto('https://example.com')
        
        wait_strategy = SmartWaitStrategy()
        success = wait_strategy.wait_for_page_ready(page)
        
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 测试智能滚动
        print("\n测试2: 智能滚动")
        at_bottom = wait_strategy.smart_scroll(page, distance=300)
        print(f"结果: {'到达底部' if at_bottom else '未到底部'}")
        
        browser.close()
    
    print("\n✅ 测试完成")
