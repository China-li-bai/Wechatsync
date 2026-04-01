# Demo Video Generator v2.0 - 核心功能深度解构

> 📅 创建时间: 2026-04-01  
> 🎯 目标: 深度解构 Web UI、批量生成、动画效果三大核心功能  
> 📊 技术栈: FastAPI + React + FFmpeg + Playwright

---

## 📋 目录

- [一、Web UI 界面功能解构](#一web-ui-界面功能解构)
- [二、批量生成功能解构](#二批量生成功能解构)
- [三、动画效果功能解构](#三动画效果功能解构)
- [四、技术选型对比](#四技术选型对比)
- [五、实施路线图](#五实施路线图)

---

## 一、Web UI 界面功能解构

### 1.1 功能概述

**目标**: 提供可视化界面，让用户无需编程即可配置和生成演示视频

**核心价值**:
- ✅ 降低使用门槛（非技术用户可用）
- ✅ 实时预览配置效果
- ✅ 可视化进度反馈
- ✅ 历史记录管理

---

### 1.2 技术架构设计

#### 1.2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Config Editor│  │ Progress UI  │  │ Video Preview│      │
│  │  (Monaco)    │  │  (Real-time) │  │   (Player)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ WebSocket (实时通信)
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  REST API    │  │  WebSocket   │  │ Task Queue   │      │
│  │  (CRUD)      │  │  (Progress)  │  │  (Celery)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                     Core Engine (Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Config Parser│  │ Video Gen    │  │  Playwright  │      │
│  │  (YAML)      │  │  (FFmpeg)    │  │  (Recording) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

#### 1.2.2 技术栈选型

| 层级 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| **Frontend** | React 18+ | 18.2.0 | 生态成熟，组件丰富 |
| | TypeScript | 5.0+ | 类型安全，开发体验好 |
| | Ant Design | 5.0+ | 企业级 UI 组件库 |
| | Monaco Editor | 0.45+ | 代码编辑器（配置编辑） |
| | Socket.io Client | 4.7+ | WebSocket 客户端 |
| **Backend** | FastAPI | 0.112+ | 高性能异步框架 |
| | Uvicorn | 0.30+ | ASGI 服务器 |
| | Celery | 5.3+ | 分布式任务队列 |
| | Redis | 7.0+ | 任务队列后端 + 缓存 |
| | Pydantic | 2.0+ | 数据验证 |
| **Core** | Playwright | 1.40+ | 浏览器自动化 |
| | FFmpeg | 6.0+ | 视频处理 |
| | edge-tts | 6.1+ | 语音合成 |

---

### 1.3 核心模块设计

#### 1.3.1 配置编辑器模块

**功能**: 可视化编辑 YAML 配置文件

**技术方案**:
```typescript
// frontend/src/components/ConfigEditor.tsx
import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Tabs, Card } from 'antd';
import MonacoEditor from '@monaco-editor/react';

interface SceneConfig {
  name: string;
  url: string;
  subtitle: string;
  voice: string;
  duration: number;
  actions?: Action[];
}

interface ProjectConfig {
  name: string;
  output_name: string;
  resolution: string;
  scenes: SceneConfig[];
}

const ConfigEditor: React.FC = () => {
  const [config, setConfig] = useState<ProjectConfig>({
    name: '',
    output_name: 'demo',
    resolution: '1920x1080',
    scenes: []
  });
  
  const [activeTab, setActiveTab] = useState<'visual' | 'yaml'>('visual');
  const [yamlContent, setYamlContent] = useState('');

  // Visual Editor -> YAML
  const convertToYaml = (config: ProjectConfig): string => {
    const yaml = `project:
  name: ${config.name}
  output_name: ${config.output_name}
  
video:
  resolution: ${config.resolution}

scenes:
${config.scenes.map((scene, index) => `
  - name: "${scene.name}"
    url: "${scene.url}"
    subtitle: "${scene.subtitle}"
    voice: "${scene.voice}"
    duration: ${scene.duration}
    actions:
${scene.actions?.map(action => `      - type: "${action.type}"`) || ''}
`).join('')}
`;
    return yaml;
  };

  // YAML -> Visual Editor
  const parseYaml = (yaml: string): ProjectConfig => {
    // 使用 js-yaml 解析
    const parsed = require('js-yaml').load(yaml);
    return {
      name: parsed.project?.name || '',
      output_name: parsed.project?.output_name || 'demo',
      resolution: parsed.video?.resolution || '1920x1080',
      scenes: parsed.scenes || []
    };
  };

  return (
    <Card>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="可视化编辑" key="visual">
          <Form layout="vertical">
            <Form.Item label="项目名称">
              <Input 
                value={config.name}
                onChange={(e) => setConfig({...config, name: e.target.value})}
              />
            </Form.Item>
            
            <Form.Item label="输出文件名">
              <Input 
                value={config.output_name}
                onChange={(e) => setConfig({...config, output_name: e.target.value})}
              />
            </Form.Item>
            
            <Form.Item label="分辨率">
              <Select 
                value={config.resolution}
                onChange={(value) => setConfig({...config, resolution: value})}
              >
                <Select.Option value="1920x1080">1920x1080 (横屏)</Select.Option>
                <Select.Option value="1080x1920">1080x1920 (竖屏)</Select.Option>
                <Select.Option value="1280x720">1280x720 (高清)</Select.Option>
              </Select>
            </Form.Item>
          </Form>
          
          {/* 场景列表 */}
          <SceneListEditor 
            scenes={config.scenes}
            onChange={(scenes) => setConfig({...config, scenes})}
          />
        </Tabs.TabPane>
        
        <Tabs.TabPane tab="YAML 编辑" key="yaml">
          <MonacoEditor
            height="600px"
            language="yaml"
            theme="vs-dark"
            value={yamlContent || convertToYaml(config)}
            onChange={(value) => {
              setYamlContent(value || '');
              try {
                const parsed = parseYaml(value || '');
                setConfig(parsed);
              } catch (e) {
                console.error('YAML 解析错误:', e);
              }
            }}
          />
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );
};

export default ConfigEditor;
```

---

#### 1.3.2 实时进度模块

**功能**: WebSocket 实时推送视频生成进度

**后端实现**:
```python
# backend/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
    
    async def broadcast_progress(self, task_id: str, progress: dict):
        if task_id in self.active_connections:
            message = json.dumps(progress)
            for connection in self.active_connections[task_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 可以接收客户端消息
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)

# 在视频生成过程中推送进度
async def generate_video_with_progress(task_id: str, config: dict):
    steps = [
        {"step": "语音生成", "progress": 0, "total": 100},
        {"step": "语音合并", "progress": 20, "total": 100},
        {"step": "字幕生成", "progress": 30, "total": 100},
        {"step": "视频录制", "progress": 40, "total": 100},
        {"step": "视频合成", "progress": 80, "total": 100},
        {"step": "完成", "progress": 100, "total": 100}
    ]
    
    for step in steps:
        # 推送进度
        await manager.broadcast_progress(task_id, {
            "type": "progress",
            "step": step["step"],
            "progress": step["progress"],
            "total": step["total"],
            "timestamp": datetime.now().isoformat()
        })
        
        # 执行实际任务
        if step["step"] == "语音生成":
            await generate_voice(config)
        elif step["step"] == "视频录制":
            await record_video(config)
        # ...
        
        await asyncio.sleep(0.5)  # 模拟处理时间
```

**前端实现**:
```typescript
// frontend/src/hooks/useProgress.ts
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface ProgressData {
  type: 'progress' | 'error' | 'complete';
  step: string;
  progress: number;
  total: number;
  timestamp: string;
  message?: string;
}

export const useProgress = (taskId: string | null) => {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const newSocket = io(`ws://localhost:8000`, {
      path: `/ws/${taskId}`,
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
    });

    newSocket.on('message', (data: string) => {
      const progressData: ProgressData = JSON.parse(data);
      setProgress(progressData);
    });

    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [taskId]);

  return { progress, socket };
};

// frontend/src/components/ProgressDisplay.tsx
import React from 'react';
import { Progress, Card, Steps, Alert } from 'antd';
import { useProgress } from '../hooks/useProgress';

const ProgressDisplay: React.FC<{ taskId: string }> = ({ taskId }) => {
  const { progress } = useProgress(taskId);

  if (!progress) {
    return <div>等待任务开始...</div>;
  }

  return (
    <Card>
      {progress.type === 'error' && (
        <Alert type="error" message={progress.message} />
      )}
      
      <Steps current={progress.progress === 100 ? 5 : -1}>
        <Steps.Step title="语音生成" />
        <Steps.Step title="语音合并" />
        <Steps.Step title="字幕生成" />
        <Steps.Step title="视频录制" />
        <Steps.Step title="视频合成" />
      </Steps>
      
      <Progress 
        percent={progress.progress} 
        status={progress.type === 'complete' ? 'success' : 'active'}
      />
      
      <div>
        <p>当前步骤: {progress.step}</p>
        <p>进度: {progress.progress}%</p>
        <p>时间: {progress.timestamp}</p>
      </div>
    </Card>
  );
};

export default ProgressDisplay;
```

---

#### 1.3.3 视频预览模块

**功能**: 在线预览生成的视频

**技术方案**:
```typescript
// frontend/src/components/VideoPreview.tsx
import React, { useRef, useEffect } from 'react';
import { Card, Button, Space } from 'antd';
import { PlayCircleOutlined, DownloadOutlined } from '@ant-design/icons';

interface VideoPreviewProps {
  videoUrl: string;
  subtitles?: string;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({ videoUrl, subtitles }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  const handlePlay = () => {
    videoRef.current?.play();
  };

  const handleDownload = () => {
    const a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'demo.mp4';
    a.click();
  };

  return (
    <Card 
      title="视频预览" 
      extra={
        <Space>
          <Button icon={<PlayCircleOutlined />} onClick={handlePlay}>
            播放
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleDownload}>
            下载
          </Button>
        </Space>
      }
    >
      <video 
        ref={videoRef}
        width="100%"
        controls
        style={{ maxHeight: '500px' }}
      >
        <source src={videoUrl} type="video/mp4" />
        {subtitles && (
          <track 
            kind="subtitles" 
            src={subtitles} 
            srcLang="zh" 
            label="中文字幕" 
          />
        )}
        您的浏览器不支持视频播放
      </video>
    </Card>
  );
};

export default VideoPreview;
```

**后端视频流服务**:
```python
# backend/api/video.py
from fastapi import APIRouter, StreamingResponse
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter()

@router.get("/video/{task_id}")
async def get_video(task_id: str):
    """获取生成的视频文件"""
    video_path = Path(f"output/{task_id}/demo.mp4")
    
    if not video_path.exists():
        return {"error": "Video not found"}
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{task_id}.mp4"
    )

@router.get("/video/stream/{task_id}")
async def stream_video(task_id: str):
    """流式传输视频（支持大文件）"""
    video_path = Path(f"output/{task_id}/demo.mp4")
    
    def iterfile():
        with open(video_path, "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(video_path.stat().st_size)
        }
    )
```

---

### 1.4 数据流设计

#### 1.4.1 配置提交流程

```
User Input (Config Editor)
         ↓
    Validate Config
         ↓
    POST /api/tasks
         ↓
    Create Task (Celery)
         ↓
    Return Task ID
         ↓
    WebSocket Connect
         ↓
    Real-time Progress
         ↓
    Video Complete
         ↓
    Preview & Download
```

---

#### 1.4.2 状态管理

```typescript
// frontend/src/store/taskStore.ts
import { create } from 'zustand';

interface TaskState {
  taskId: string | null;
  status: 'idle' | 'running' | 'completed' | 'error';
  config: any;
  progress: number;
  videoUrl: string | null;
  
  setTaskId: (id: string) => void;
  setStatus: (status: string) => void;
  setProgress: (progress: number) => void;
  setVideoUrl: (url: string) => void;
  reset: () => void;
}

export const useTaskStore = create<TaskState>((set) => ({
  taskId: null,
  status: 'idle',
  config: null,
  progress: 0,
  videoUrl: null,
  
  setTaskId: (id) => set({ taskId: id }),
  setStatus: (status) => set({ status: status as any }),
  setProgress: (progress) => set({ progress }),
  setVideoUrl: (url) => set({ videoUrl: url }),
  reset: () => set({
    taskId: null,
    status: 'idle',
    config: null,
    progress: 0,
    videoUrl: null
  })
}));
```

---

## 二、批量生成功能解构

### 2.1 功能概述

**目标**: 支持一次配置，批量生成多个版本的视频

**核心价值**:
- ✅ 提高效率（一次配置，多版本输出）
- ✅ A/B 测试（不同语音、字幕版本）
- ✅ 多语言支持（自动翻译 + 生成）

---

### 2.2 技术架构设计

#### 2.2.1 任务队列架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Task Queue System                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Task Producer│  │ Task Queue   │  │Task Consumer │      │
│  │  (FastAPI)   │→ │   (Redis)    │→ │   (Celery)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Task Manager │  │ Progress DB  │  │  Worker Pool │      │
│  │  (Monitor)   │  │   (Redis)    │  │  (Parallel)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

#### 2.2.2 批量任务配置

**YAML 配置扩展**:
```yaml
# config.yaml
project:
  name: "产品演示"
  output_name: "demo"

# 批量生成配置
batch:
  enabled: true
  count: 3  # 生成 3 个版本
  
  # 变体配置
  variations:
    # 版本1: 女声
    - name: "female_voice"
      voice: "XiaoxiaoNeural"
      subtitle_style: "bottom"
      
    # 版本2: 男声
    - name: "male_voice"
      voice: "YunxiNeural"
      subtitle_style: "top"
      
    # 版本3: 专业男声
    - name: "professional_voice"
      voice: "YunyangNeural"
      subtitle_style: "center"

scenes:
  - name: "开场"
    url: "https://example.com/intro"
    subtitle: "欢迎观看产品演示"
    duration: 5
    
  - name: "功能展示"
    url: "https://example.com/features"
    subtitle: "这是我们的核心功能"
    duration: 10
```

---

### 2.3 核心模块设计

#### 2.3.1 任务调度器

**Celery 任务定义**:
```python
# backend/tasks/video_tasks.py
from celery import Celery, group, chain, chord
from celery.result import AsyncResult
from typing import List, Dict
import asyncio

app = Celery('video_generator', broker='redis://localhost:6379/0')

@app.task(bind=True)
def generate_single_video(self, config: dict, variation: dict):
    """生成单个视频"""
    try:
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={'step': '初始化', 'progress': 0}
        )
        
        # 合并配置
        merged_config = {**config, **variation}
        
        # 生成视频
        from lib.demo_video_generator import DemoVideoGenerator
        generator = DemoVideoGenerator(merged_config)
        
        # 异步执行
        loop = asyncio.get_event_loop()
        output_file = loop.run_until_complete(generator.generate())
        
        return {
            'status': 'success',
            'output_file': str(output_file),
            'variation': variation['name']
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@app.task
def generate_batch_videos(config: dict, variations: List[dict]):
    """批量生成视频"""
    # 创建任务组
    job = group(
        generate_single_video.s(config, variation)
        for variation in variations
    )
    
    # 执行任务组
    result = job.apply_async()
    
    return {
        'batch_id': result.id,
        'task_count': len(variations)
    }

@app.task
def check_batch_status(batch_id: str):
    """检查批量任务状态"""
    result = AsyncResult(batch_id)
    
    if result.ready():
        # 所有任务完成
        results = result.get()
        return {
            'status': 'completed',
            'results': results
        }
    else:
        # 任务进行中
        completed = result.completed_count()
        total = len(result.children)
        
        return {
            'status': 'running',
            'completed': completed,
            'total': total,
            'progress': (completed / total) * 100
        }
```

---

#### 2.3.2 并发控制

**Worker 配置**:
```python
# backend/config/celeryconfig.py
from kombu import Queue

# Worker 配置
worker_concurrency = 4  # 并发数
worker_prefetch_multiplier = 1  # 预取任务数

# 任务队列
task_queues = (
    Queue('default', routing_key='task.default'),
    Queue('video', routing_key='task.video'),
    Queue('audio', routing_key='task.audio'),
)

# 任务路由
task_routes = {
    'tasks.video_tasks.generate_single_video': {
        'queue': 'video',
        'routing_key': 'task.video'
    },
    'tasks.audio_tasks.generate_voice': {
        'queue': 'audio',
        'routing_key': 'task.audio'
    },
}

# 任务结果后端
result_backend = 'redis://localhost:6379/1'
result_expires = 3600  # 结果保留 1 小时

# 任务限流
task_annotations = {
    'tasks.video_tasks.generate_single_video': {
        'rate_limit': '2/m'  # 每分钟最多 2 个任务
    }
}
```

---

#### 2.3.3 进度追踪

**Redis 进度存储**:
```python
# backend/utils/progress_tracker.py
import redis
import json
from datetime import datetime
from typing import Dict, List

class ProgressTracker:
    def __init__(self, redis_url: str = 'redis://localhost:6379/2'):
        self.redis = redis.from_url(redis_url)
    
    def init_batch(self, batch_id: str, task_ids: List[str]):
        """初始化批量任务进度"""
        progress_data = {
            'batch_id': batch_id,
            'total': len(task_ids),
            'completed': 0,
            'failed': 0,
            'tasks': {
                task_id: {
                    'status': 'pending',
                    'progress': 0,
                    'started_at': None,
                    'completed_at': None
                }
                for task_id in task_ids
            },
            'created_at': datetime.now().isoformat()
        }
        
        self.redis.setex(
            f'batch:{batch_id}',
            3600,  # 1 小时过期
            json.dumps(progress_data)
        )
    
    def update_task_progress(
        self, 
        batch_id: str, 
        task_id: str, 
        progress: int,
        status: str = 'running'
    ):
        """更新单个任务进度"""
        data = self.get_batch_progress(batch_id)
        
        if data:
            data['tasks'][task_id]['progress'] = progress
            data['tasks'][task_id]['status'] = status
            
            if status == 'running' and not data['tasks'][task_id]['started_at']:
                data['tasks'][task_id]['started_at'] = datetime.now().isoformat()
            
            if status in ['completed', 'failed']:
                data['tasks'][task_id]['completed_at'] = datetime.now().isoformat()
                
                if status == 'completed':
                    data['completed'] += 1
                else:
                    data['failed'] += 1
            
            self.redis.setex(
                f'batch:{batch_id}',
                3600,
                json.dumps(data)
            )
    
    def get_batch_progress(self, batch_id: str) -> Dict:
        """获取批量任务进度"""
        data = self.redis.get(f'batch:{batch_id}')
        return json.loads(data) if data else None
    
    def get_overall_progress(self, batch_id: str) -> Dict:
        """获取总体进度"""
        data = self.get_batch_progress(batch_id)
        
        if not data:
            return None
        
        total_progress = sum(
            task['progress'] 
            for task in data['tasks'].values()
        ) / data['total']
        
        return {
            'batch_id': batch_id,
            'total': data['total'],
            'completed': data['completed'],
            'failed': data['failed'],
            'progress': total_progress,
            'status': 'completed' if data['completed'] + data['failed'] == data['total'] else 'running'
        }
```

---

#### 2.3.4 结果管理

**批量结果聚合**:
```python
# backend/api/batch.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pathlib import Path
import shutil

router = APIRouter()

@router.post("/batch/create")
async def create_batch_task(config: dict):
    """创建批量任务"""
    from tasks.video_tasks import generate_batch_videos
    
    # 验证配置
    if not config.get('batch', {}).get('enabled'):
        raise HTTPException(400, "Batch mode not enabled")
    
    variations = config['batch']['variations']
    
    # 创建批量任务
    result = generate_batch_videos.delay(config, variations)
    
    return {
        'batch_id': result.id,
        'task_count': len(variations)
    }

@router.get("/batch/{batch_id}/status")
async def get_batch_status(batch_id: str):
    """获取批量任务状态"""
    from tasks.video_tasks import check_batch_status
    
    status = check_batch_status(batch_id)
    
    return status

@router.get("/batch/{batch_id}/results")
async def get_batch_results(batch_id: str):
    """获取批量任务结果"""
    from utils.progress_tracker import ProgressTracker
    
    tracker = ProgressTracker()
    progress = tracker.get_batch_progress(batch_id)
    
    if not progress:
        raise HTTPException(404, "Batch not found")
    
    # 收集所有生成的视频
    output_dir = Path(f"output/{batch_id}")
    videos = []
    
    for task_id, task_data in progress['tasks'].items():
        if task_data['status'] == 'completed':
            video_path = output_dir / task_id / "demo.mp4"
            if video_path.exists():
                videos.append({
                    'task_id': task_id,
                    'variation': task_data.get('variation'),
                    'video_url': f"/video/{batch_id}/{task_id}",
                    'thumbnail': f"/video/{batch_id}/{task_id}/thumbnail.jpg"
                })
    
    return {
        'batch_id': batch_id,
        'total': progress['total'],
        'completed': progress['completed'],
        'videos': videos
    }

@router.post("/batch/{batch_id}/download")
async def download_batch_results(batch_id: str):
    """打包下载所有结果"""
    output_dir = Path(f"output/{batch_id}")
    
    if not output_dir.exists():
        raise HTTPException(404, "Batch not found")
    
    # 创建 ZIP 文件
    zip_path = Path(f"output/{batch_id}.zip")
    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', output_dir)
    
    return {
        'download_url': f"/download/{batch_id}.zip"
    }
```

---

### 2.4 性能优化

#### 2.4.1 资源池化

```python
# backend/utils/resource_pool.py
from contextlib import contextmanager
from playwright.sync_api import sync_playwright
import threading

class BrowserPool:
    """浏览器实例池"""
    
    def __init__(self, max_size: int = 4):
        self.max_size = max_size
        self.pool = []
        self.lock = threading.Lock()
        self.playwright = sync_playwright().start()
    
    @contextmanager
    def get_browser(self):
        """获取浏览器实例"""
        browser = None
        
        with self.lock:
            if self.pool:
                browser = self.pool.pop()
            else:
                browser = self.playwright.chromium.launch()
        
        try:
            yield browser
        finally:
            with self.lock:
                if len(self.pool) < self.max_size:
                    self.pool.append(browser)
                else:
                    browser.close()
    
    def close_all(self):
        """关闭所有浏览器"""
        with self.lock:
            for browser in self.pool:
                browser.close()
            self.pool.clear()
            self.playwright.stop()

# 全局浏览器池
browser_pool = BrowserPool(max_size=4)
```

---

#### 2.4.2 缓存策略

```python
# backend/utils/cache.py
from functools import lru_cache
import hashlib
from pathlib import Path
import json

class VoiceCache:
    """语音缓存"""
    
    def __init__(self, cache_dir: Path = Path("cache/voice")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, text: str, voice: str) -> str:
        """生成缓存键"""
        content = f"{text}_{voice}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, voice: str) -> Path | None:
        """获取缓存的语音文件"""
        cache_key = self.get_cache_key(text, voice)
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        return cache_file if cache_file.exists() else None
    
    def set(self, text: str, voice: str, audio_file: Path):
        """缓存语音文件"""
        cache_key = self.get_cache_key(text, voice)
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        import shutil
        shutil.copy(audio_file, cache_file)
        
        return cache_file

# 全局缓存实例
voice_cache = VoiceCache()
```

---

## 三、动画效果功能解构

### 3.1 功能概述

**目标**: 为视频添加转场、特效、字幕动画等效果

**核心价值**:
- ✅ 提升视频专业度
- ✅ 增强视觉吸引力
- ✅ 更好的用户体验

---

### 3.2 动画类型设计

#### 3.2.1 转场效果

| 效果名称 | FFmpeg 滤镜 | 参数 | 适用场景 |
|---------|------------|------|---------|
| **淡入淡出** | `fade` | duration, color | 场景切换 |
| **滑动** | `slide` | direction, duration | 内容展示 |
| **缩放** | `zoompan` | zoom, duration | 重点突出 |
| **擦除** | `wipe` | direction, duration | 创意转场 |
| **旋转** | `rotate` | angle, duration | 动感效果 |

---

#### 3.2.2 字幕动画

| 效果名称 | 描述 | 参数 |
|---------|------|------|
| **淡入** | 字幕逐渐显示 | duration, delay |
| **打字机** | 逐字显示 | speed, cursor |
| **滚动** | 从下往上滚动 | speed, direction |
| **弹跳** | 弹跳进入 | bounce_height |
| **闪烁** | 闪烁效果 | frequency |

---

#### 3.2.3 特效

| 效果名称 | FFmpeg 滤镜 | 参数 |
|---------|------------|------|
| **模糊** | `boxblur` | radius, power |
| **锐化** | `unsharp` | luma, chroma |
| **色彩调整** | `eq` | brightness, contrast |
| **画中画** | `overlay` | position, opacity |
| **水印** | `overlay` | position, opacity |

---

### 3.3 技术实现

#### 3.3.1 FFmpeg 滤镜封装

```python
# lib/effects/ffmpeg_effects.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TransitionType(Enum):
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    WIPE = "wipe"
    ROTATE = "rotate"

@dataclass
class Transition:
    type: TransitionType
    duration: float
    params: Dict
    
    def to_ffmpeg_filter(self) -> str:
        """转换为 FFmpeg 滤镜"""
        if self.type == TransitionType.FADE:
            return f"fade=t=in:st=0:d={self.duration}:c={self.params.get('color', 'black')}"
        
        elif self.type == TransitionType.SLIDE:
            direction = self.params.get('direction', 'left')
            return f"slide=direction={direction}:duration={self.duration}"
        
        elif self.type == TransitionType.ZOOM:
            zoom = self.params.get('zoom', 1.5)
            return f"zoompan=z='min(zoom+0.0015,{zoom})':d={int(self.duration*25)}"
        
        elif self.type == TransitionType.WIPE:
            direction = self.params.get('direction', 'right')
            return f"wipe=direction={direction}:duration={self.duration}"
        
        elif self.type == TransitionType.ROTATE:
            angle = self.params.get('angle', 360)
            return f"rotate=angle={angle}*PI/180:duration={self.duration}"

class EffectsComposer:
    """特效合成器"""
    
    def __init__(self):
        self.filters: List[str] = []
    
    def add_transition(
        self, 
        transition: Transition,
        input_label: str,
        output_label: str
    ):
        """添加转场效果"""
        filter_str = transition.to_ffmpeg_filter()
        self.filters.append(f"[{input_label}]{filter_str}[{output_label}]")
        return self
    
    def add_subtitle_animation(
        self,
        text: str,
        style: str = "fade",
        duration: float = 1.0,
        position: str = "bottom",
        font_size: int = 24,
        font_color: str = "white"
    ):
        """添加字幕动画"""
        if style == "fade":
            filter_str = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=h-th-50:enable='between(t,0,{duration})':alpha='if(lt(t,{duration}),t/{duration},1)'"
        
        elif style == "typewriter":
            filter_str = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=h-th-50:enable='between(t,0,{duration})':textfile_reload=1"
        
        elif style == "scroll":
            filter_str = f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=h-th-50+h*t/{duration}:enable='between(t,0,{duration})'"
        
        self.filters.append(filter_str)
        return self
    
    def add_watermark(
        self,
        watermark_path: str,
        position: str = "top_right",
        opacity: float = 0.5
    ):
        """添加水印"""
        positions = {
            "top_left": "10:10",
            "top_right": "W-w-10:10",
            "bottom_left": "10:H-h-10",
            "bottom_right": "W-w-10:H-h-10",
            "center": "(W-w)/2:(H-h)/2"
        }
        
        x, y = positions.get(position, "W-w-10:10")
        
        filter_str = f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];[0:v][wm]overlay={x}:{y}"
        self.filters.append(filter_str)
        return self
    
    def add_blur(self, radius: int = 10):
        """添加模糊效果"""
        filter_str = f"boxblur={radius}:{radius}"
        self.filters.append(filter_str)
        return self
    
    def add_color_adjustment(
        self,
        brightness: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0
    ):
        """色彩调整"""
        filter_str = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
        self.filters.append(filter_str)
        return self
    
    def build_filter_complex(self) -> str:
        """构建滤镜链"""
        return ";".join(self.filters)

# 使用示例
composer = EffectsComposer()

# 添加转场
composer.add_transition(
    Transition(
        type=TransitionType.FADE,
        duration=1.0,
        params={"color": "black"}
    ),
    input_label="0:v",
    output_label="v1"
)

# 添加字幕动画
composer.add_subtitle_animation(
    text="欢迎观看产品演示",
    style="fade",
    duration=1.5,
    position="bottom"
)

# 添加水印
composer.add_watermark(
    watermark_path="logo.png",
    position="top_right",
    opacity=0.3
)

# 构建 FFmpeg 命令
filter_complex = composer.build_filter_complex()
```

---

#### 3.3.2 配置化动画

**YAML 配置扩展**:
```yaml
# config.yaml
project:
  name: "产品演示"
  output_name: "demo"

# 动画效果配置
effects:
  # 全局转场
  global_transition:
    type: "fade"
    duration: 0.5
    params:
      color: "black"
  
  # 水印
  watermark:
    enabled: true
    path: "assets/logo.png"
    position: "top_right"
    opacity: 0.3
  
  # 字幕动画
  subtitle_animation:
    enabled: true
    style: "fade"  # fade, typewriter, scroll
    duration: 1.0
    font_size: 24
    font_color: "white"
    position: "bottom"

scenes:
  - name: "开场"
    url: "https://example.com/intro"
    subtitle: "欢迎观看产品演示"
    duration: 5
    
    # 场景特定动画
    animations:
      - type: "zoom"
        duration: 2.0
        params:
          zoom: 1.2
      
      - type: "blur"
        params:
          radius: 5
          start: 3.0
          end: 5.0
```

---

#### 3.3.3 动画渲染器

```python
# lib/effects/animator.py
from typing import List, Dict
from pathlib import Path
import subprocess
from dataclasses import dataclass

@dataclass
class Animation:
    type: str
    duration: float
    params: Dict
    start_time: float = 0.0
    end_time: float = 0.0

class VideoAnimator:
    """视频动画渲染器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.effects = config.get('effects', {})
    
    def apply_effects(
        self, 
        input_video: Path, 
        output_video: Path,
        scenes: List[Dict]
    ):
        """应用所有动画效果"""
        composer = EffectsComposer()
        
        # 1. 添加全局转场
        if self.effects.get('global_transition'):
            transition = self.effects['global_transition']
            composer.add_transition(
                Transition(
                    type=TransitionType[transition['type'].upper()],
                    duration=transition['duration'],
                    params=transition.get('params', {})
                ),
                input_label="0:v",
                output_label="v1"
            )
        
        # 2. 添加水印
        if self.effects.get('watermark', {}).get('enabled'):
            wm = self.effects['watermark']
            composer.add_watermark(
                watermark_path=wm['path'],
                position=wm['position'],
                opacity=wm['opacity']
            )
        
        # 3. 添加字幕动画
        if self.effects.get('subtitle_animation', {}).get('enabled'):
            sub_anim = self.effects['subtitle_animation']
            for scene in scenes:
                if scene.get('subtitle'):
                    composer.add_subtitle_animation(
                        text=scene['subtitle'],
                        style=sub_anim['style'],
                        duration=sub_anim['duration'],
                        position=sub_anim['position'],
                        font_size=sub_anim['font_size'],
                        font_color=sub_anim['font_color']
                    )
        
        # 4. 添加场景特定动画
        for scene in scenes:
            if scene.get('animations'):
                for anim in scene['animations']:
                    if anim['type'] == 'zoom':
                        composer.filters.append(
                            f"zoompan=z='min(zoom+0.0015,{anim['params']['zoom']})':d={int(anim['duration']*25)}"
                        )
                    elif anim['type'] == 'blur':
                        radius = anim['params']['radius']
                        start = anim.get('start', 0)
                        end = anim.get('end', 0)
                        composer.filters.append(
                            f"boxblur={radius}:{radius}:enable='between(t,{start},{end})'"
                        )
        
        # 5. 构建 FFmpeg 命令
        filter_complex = composer.build_filter_complex()
        
        cmd = [
            'ffmpeg',
            '-i', str(input_video),
            '-i', self.effects['watermark']['path'],  # 水印输入
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',
            '-c:a', 'copy',
            '-y',
            str(output_video)
        ]
        
        # 执行命令
        subprocess.run(cmd, check=True)
        
        return output_video

# 集成到主流程
class DemoVideoGeneratorV2:
    def __init__(self, config: Dict):
        self.config = config
        self.animator = VideoAnimator(config)
    
    async def generate(self):
        """生成视频（带动画效果）"""
        # ... 原有流程 ...
        
        # 应用动画效果
        if self.config.get('effects'):
            animated_video = self.output_dir / "animated.mp4"
            self.animator.apply_effects(
                input_video=raw_video,
                output_video=animated_video,
                scenes=self.config['scenes']
            )
            return animated_video
        
        return raw_video
```

---

### 3.4 性能优化

#### 3.4.1 硬件加速

```python
# lib/effects/hardware_acceleration.py
import subprocess
from pathlib import Path

class HardwareAcceleratedEncoder:
    """硬件加速编码器"""
    
    @staticmethod
    def detect_gpu():
        """检测可用 GPU"""
        try:
            # NVIDIA GPU
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return 'nvidia'
        except:
            pass
        
        try:
            # AMD GPU
            result = subprocess.run(
                ['rocm-smi'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return 'amd'
        except:
            pass
        
        try:
            # Intel GPU
            result = subprocess.run(
                ['intel_gpu_top'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return 'intel'
        except:
            pass
        
        return 'cpu'
    
    def encode_with_gpu(
        self,
        input_video: Path,
        output_video: Path,
        gpu_type: str = 'auto'
    ):
        """使用 GPU 加速编码"""
        if gpu_type == 'auto':
            gpu_type = self.detect_gpu()
        
        if gpu_type == 'nvidia':
            codec = 'h264_nvenc'
            preset = 'p4'  # NVIDIA 专用预设
        elif gpu_type == 'amd':
            codec = 'h264_amf'
            preset = 'balanced'
        elif gpu_type == 'intel':
            codec = 'h264_qsv'
            preset = 'medium'
        else:
            codec = 'libx264'
            preset = 'medium'
        
        cmd = [
            'ffmpeg',
            '-i', str(input_video),
            '-c:v', codec,
            '-preset', preset,
            '-c:a', 'copy',
            '-y',
            str(output_video)
        ]
        
        subprocess.run(cmd, check=True)
        
        return output_video
```

---

#### 3.4.2 滤镜优化

```python
# lib/effects/filter_optimizer.py
from typing import List, Dict

class FilterOptimizer:
    """滤镜优化器"""
    
    @staticmethod
    def merge_filters(filters: List[str]) -> List[str]:
        """合并相同类型的滤镜"""
        merged = []
        filter_groups = {}
        
        for f in filters:
            # 提取滤镜类型
            filter_type = f.split('=')[0]
            
            if filter_type not in filter_groups:
                filter_groups[filter_type] = []
            
            filter_groups[filter_type].append(f)
        
        # 合并同类型滤镜
        for filter_type, group in filter_groups.items():
            if len(group) > 1:
                # 合并参数
                merged_filter = FilterOptimizer._merge_same_type(group)
                merged.append(merged_filter)
            else:
                merged.append(group[0])
        
        return merged
    
    @staticmethod
    def _merge_same_type(filters: List[str]) -> str:
        """合并同类型滤镜"""
        # 例如：合并多个 drawtext 滤镜
        if 'drawtext' in filters[0]:
            # 提取所有文本
            texts = []
            for f in filters:
                text = f.split("text='")[1].split("'")[0]
                texts.append(text)
            
            # 合并为一个滤镜
            return f"drawtext=text='{','.join(texts)}'"
        
        return filters[0]
    
    @staticmethod
    def optimize_filter_order(filters: List[str]) -> List[str]:
        """优化滤镜顺序"""
        # 根据滤镜类型排序，减少重编码
        priority = {
            'crop': 1,
            'scale': 2,
            'fps': 3,
            'setpts': 4,
            'drawtext': 5,
            'overlay': 6,
            'fade': 7,
            'boxblur': 8
        }
        
        return sorted(
            filters,
            key=lambda f: priority.get(f.split('=')[0], 99)
        )
```

---

## 四、技术选型对比

### 4.1 前端框架对比

| 框架 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **React 18+** | 生态成熟，组件丰富，TypeScript 支持好 | 学习曲线较陡 | ⭐⭐⭐⭐⭐ |
| **Vue 3+** | 易学易用，性能好 | 生态相对较小 | ⭐⭐⭐⭐ |
| **Svelte** | 编译时优化，性能最佳 | 生态不成熟 | ⭐⭐⭐ |

**推荐**: React 18+ + TypeScript + Ant Design

---

### 4.2 后端框架对比

| 框架 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **FastAPI** | 高性能，异步支持，自动文档 | 相对较新 | ⭐⭐⭐⭐⭐ |
| **Flask** | 成熟稳定，生态丰富 | 性能一般，无异步 | ⭐⭐⭐⭐ |
| **Django** | 功能全面，ORM 强大 | 过于重量级 | ⭐⭐⭐ |

**推荐**: FastAPI + Uvicorn + Celery

---

### 4.3 任务队列对比

| 系统 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **Celery** | 功能强大，生态成熟 | 配置复杂 | ⭐⭐⭐⭐⭐ |
| **RQ (Redis Queue)** | 简单易用 | 功能较少 | ⭐⭐⭐⭐ |
| **Dramatiq** | 性能好，代码简洁 | 生态较小 | ⭐⭐⭐⭐ |

**推荐**: Celery + Redis

---

### 4.4 浏览器自动化对比

| 工具 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **Playwright** | 跨浏览器，API 现代，内置录制 | 相对较新 | ⭐⭐⭐⭐⭐ |
| **Puppeteer** | Chrome 官方，生态成熟 | 仅支持 Chrome | ⭐⭐⭐⭐ |
| **Selenium** | 成熟稳定，支持多语言 | 性能差，API 陈旧 | ⭐⭐⭐ |

**推荐**: Playwright

---

## 五、实施路线图

### 5.1 Phase 1: Web UI 基础版（2-3 周）

**目标**: 实现基本的 Web 界面和 REST API

**任务清单**:
- [ ] 搭建 FastAPI 后端框架
- [ ] 实现配置 CRUD API
- [ ] 创建 React 前端项目
- [ ] 实现配置编辑器（Monaco Editor）
- [ ] 实现视频生成 API
- [ ] 添加视频预览功能

**交付物**:
- ✅ 可用的 Web 界面
- ✅ 基本的配置编辑功能
- ✅ 视频生成和预览

---

### 5.2 Phase 2: 实时进度 + 批量生成（2-3 周）

**目标**: 实现 WebSocket 实时进度和批量生成功能

**任务清单**:
- [ ] 集成 Celery 任务队列
- [ ] 实现 WebSocket 进度推送
- [ ] 实现批量任务管理
- [ ] 添加进度显示 UI
- [ ] 实现结果聚合和下载

**交付物**:
- ✅ 实时进度显示
- ✅ 批量生成功能
- ✅ 结果管理界面

---

### 5.3 Phase 3: 动画效果（2-3 周）

**目标**: 实现转场、字幕动画等特效

**任务清单**:
- [ ] 封装 FFmpeg 滤镜
- [ ] 实现转场效果
- [ ] 实现字幕动画
- [ ] 添加水印功能
- [ ] 配置化动画方案

**交付物**:
- ✅ 动画效果库
- ✅ 配置化动画
- ✅ 性能优化

---

### 5.4 Phase 4: 优化和测试（1-2 周）

**目标**: 性能优化和全面测试

**任务清单**:
- [ ] 硬件加速支持
- [ ] 缓存优化
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试

**交付物**:
- ✅ 性能优化报告
- ✅ 测试覆盖率 > 80%
- ✅ 文档完善

---

## 六、总结

### 6.1 核心技术栈

```
Frontend:  React 18+ + TypeScript + Ant Design + Monaco Editor
Backend:   FastAPI + Uvicorn + Celery + Redis
Core:      Playwright + FFmpeg + edge-tts
Storage:   Redis (任务队列) + Local File System (视频存储)
```

---

### 6.2 关键技术点

1. **Web UI**:
   - Monaco Editor 实现 YAML 编辑
   - WebSocket 实现实时进度
   - 流式视频传输

2. **批量生成**:
   - Celery 分布式任务队列
   - Redis 进度追踪
   - 资源池化优化

3. **动画效果**:
   - FFmpeg 滤镜封装
   - 配置化动画方案
   - 硬件加速支持

---

### 6.3 预期效果

**用户体验**:
- ✅ 无需编程即可使用
- ✅ 实时进度反馈
- ✅ 批量生成多版本
- ✅ 专业级动画效果

**性能提升**:
- ✅ 并发生成，效率提升 4x
- ✅ GPU 加速，编码速度提升 10x
- ✅ 缓存优化，重复生成速度提升 5x

---

**🎯 深度解构完成！三大核心功能的技术方案已详细设计，可按路线图逐步实施！** 🚀
