#!/usr/bin/env python3
"""
Video Recorder - 视频录制器
使用 agent-browser 自动录制视频
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil
import logging


class VideoRecorder:
    """视频录制器"""
    
    def __init__(self, url: str, output_file: Path, logger: Optional[logging.Logger] = None):
        """
        初始化视频录制器
        
        Args:
            url: 要录制的网页 URL
            output_file: 输出视频文件路径
            logger: 日志记录器
        """
        self.url = url
        self.output_file = Path(output_file)
        self.logger = logger or logging.getLogger(__name__)
        self.agent_browser = self._find_agent_browser()
        
    def _find_agent_browser(self) -> str:
        """查找 agent-browser 可执行文件"""
        possible_paths = [
            shutil.which('agent-browser'),
            Path.home() / '.local' / 'bin' / 'agent-browser',
            '/usr/local/bin/agent-browser',
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return str(path)
                
        raise FileNotFoundError("未找到 agent-browser，请运行: pipx install agent-browser")
    
    def _run_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """运行 agent-browser 命令"""
        cmd = [self.agent_browser] + args
        self.logger.debug(f"运行命令: {' '.join(cmd)}")
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    
    def open_browser(self) -> bool:
        """打开浏览器"""
        try:
            self.logger.info(f"打开浏览器: {self.url}")
            result = self._run_command(['open', self.url])
            time.sleep(3)  # 等待页面加载
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"打开浏览器失败: {e.stderr}")
            return False
    
    def start_recording(self) -> bool:
        """开始录制"""
        try:
            self.logger.info(f"开始录制: {self.output_file}")
            result = self._run_command(['record', 'start', str(self.output_file)])
            time.sleep(2)  # 等待录制开始
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"开始录制失败: {e.stderr}")
            return False
    
    def stop_recording(self) -> bool:
        """停止录制"""
        try:
            self.logger.info("停止录制")
            result = self._run_command(['record', 'stop'])
            time.sleep(2)  # 等待录制停止
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"停止录制失败: {e.stderr}")
            return False
    
    def close_browser(self) -> bool:
        """关闭浏览器"""
        try:
            self.logger.info("关闭浏览器")
            result = self._run_command(['close'])
            time.sleep(1)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"关闭浏览器失败: {e.stderr}")
            return False
    
    def scroll(self, direction: str = 'down', distance: int = 300) -> bool:
        """滚动页面"""
        try:
            self.logger.debug(f"滚动页面: {direction} {distance}px")
            if direction == 'down':
                result = self._run_command(['scroll', 'down', str(distance)])
            elif direction == 'up':
                result = self._run_command(['scroll', 'up', str(distance)])
            else:
                result = self._run_command(['scroll', direction])
            time.sleep(1)  # 等待滚动完成
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"滚动页面失败: {e.stderr}")
            return False
    
    def scroll_to_top(self) -> bool:
        """滚动到页面顶部"""
        try:
            self.logger.debug("滚动到页面顶部")
            result = self._run_command(['scroll', 'to', 'top'])
            time.sleep(1)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"滚动到顶部失败: {e.stderr}")
            return False
    
    def screenshot(self, output_file: Path) -> bool:
        """截图"""
        try:
            self.logger.debug(f"截图: {output_file}")
            result = self._run_command(['screenshot', str(output_file)])
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"截图失败: {e.stderr}")
            return False
    
    def auto_record(self, durations: List[float], actions: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        自动录制视频
        
        Args:
            durations: 每个场景的时长列表（秒）
            actions: 每个场景的操作列表（可选）
        
        Returns:
            是否成功
        """
        self.logger.info("开始自动录制流程")
        
        # 1. 打开浏览器
        if not self.open_browser():
            self.logger.error("打开浏览器失败")
            return False
        
        # 2. 开始录制
        if not self.start_recording():
            self.logger.error("开始录制失败")
            self.close_browser()
            return False
        
        # 3. 执行场景录制
        try:
            for i, duration in enumerate(durations):
                scene_num = i + 1
                self.logger.info(f"录制场景 {scene_num}/{len(durations)} ({duration:.1f}秒)")
                
                # 执行操作（如果有）
                if actions and i < len(actions):
                    action = actions[i]
                    self._execute_action(action)
                
                # 等待指定时长
                time.sleep(duration)
                
                # 执行场景结束后的操作（如果有）
                if actions and i < len(actions):
                    action = actions[i]
                    if 'post_action' in action:
                        self._execute_action(action['post_action'])
        
        except Exception as e:
            self.logger.error(f"录制过程出错: {e}")
            self.stop_recording()
            self.close_browser()
            return False
        
        # 4. 停止录制
        if not self.stop_recording():
            self.logger.error("停止录制失败")
            self.close_browser()
            return False
        
        # 5. 关闭浏览器
        if not self.close_browser():
            self.logger.warning("关闭浏览器失败，但录制已完成")
        
        self.logger.info("自动录制完成")
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """执行单个操作"""
        action_type = action.get('type')
        
        if action_type == 'scroll':
            direction = action.get('direction', 'down')
            distance = action.get('distance', 300)
            return self.scroll(direction, distance)
        
        elif action_type == 'scroll_to_top':
            return self.scroll_to_top()
        
        elif action_type == 'screenshot':
            output_file = action.get('output_file')
            if output_file:
                return self.screenshot(Path(output_file))
        
        elif action_type == 'wait':
            duration = action.get('duration', 1)
            time.sleep(duration)
            return True
        
        else:
            self.logger.warning(f"未知操作类型: {action_type}")
            return False
    
    def record_with_config(self, config: Dict[str, Any]) -> bool:
        """
        根据配置录制视频
        
        Args:
            config: 录制配置
        
        Returns:
            是否成功
        """
        scenes = config.get('scenes', [])
        durations = [scene.get('duration', 10) for scene in scenes]
        actions = [scene.get('action', {}) for scene in scenes]
        
        return self.auto_record(durations, actions)


class VideoRecorderError(Exception):
    """视频录制器错误"""
    pass
