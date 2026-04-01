# Demo Video Generator - 测试和验证流程

## 🧪 测试策略

### 测试层次

```
┌─────────────────────────────────────┐
│         端到端测试 (E2E)             │
│   完整视频生成流程测试               │
├─────────────────────────────────────┤
│         集成测试                     │
│   模块间协作测试                     │
├─────────────────────────────────────┤
│         单元测试                     │
│   各模块功能测试                     │
├─────────────────────────────────────┤
│         配置验证                     │
│   配置文件格式验证                   │
└─────────────────────────────────────┘
```

---

## 📋 测试清单

### 1. 配置文件验证

#### 自动验证

```bash
# 验证配置文件格式
demo-gen validate config.yaml
```

#### 手动检查项

- [ ] 项目名称是否填写
- [ ] URL 是否有效
- [ ] 语音配置是否正确
- [ ] 场景数量是否合理（5-8个）
- [ ] 每个场景是否包含必需字段
- [ ] 文案长度是否适中（< 100字/场景）
- [ ] 字幕文本是否简短（< 30字）

---

### 2. 单元测试

#### 运行单元测试

```bash
# 运行所有单元测试
python tests/test_demo_video_generator.py

# 或使用 pytest（如果安装）
pytest tests/ -v
```

#### 测试覆盖

| 模块 | 测试项 | 状态 |
|------|--------|------|
| ConfigParser | 配置加载 | ✅ |
| ConfigParser | 字段验证 | ✅ |
| ConfigParser | 错误处理 | ✅ |
| SubtitleGenerator | SRT生成 | ✅ |
| SubtitleGenerator | 时间格式转换 | ✅ |
| VoiceoverGenerator | 语音生成 | ⚠️ 需要外部依赖 |
| VideoComposer | 视频合成 | ⚠️ 需要外部依赖 |

---

### 3. 集成测试

#### 测试场景

**场景1: 基础流程**

```bash
# 1. 创建测试项目
demo-gen init test-project
cd test-project

# 2. 使用基础配置
cp ../templates/basic.yaml config.yaml

# 3. 验证配置
demo-gen validate config.yaml

# 4. 生成语音（测试语音生成模块）
python -c "
from demo_video_generator import VoiceoverGenerator
from pathlib import Path

gen = VoiceoverGenerator({'language': 'zh-CN', 'voice_name': 'XiaoxiaoNeural'}, Path('.'))
duration = gen.generate('测试文案', Path('test.mp3'))
print(f'时长: {duration}s')
"

# 5. 生成字幕（测试字幕生成模块）
python -c "
from demo_video_generator import SubtitleGenerator
from pathlib import Path

gen = SubtitleGenerator({}, Path('.'))
gen.generate_srt([5.5, 3.2], ['第一句', '第二句'], Path('test.srt'))
print('字幕生成成功')
"
```

**预期结果**:
- ✅ 配置验证通过
- ✅ 语音文件生成成功
- ✅ 字幕文件生成成功

---

**场景2: 完整流程**

```bash
# 使用 PageAgent 示例配置
demo-gen generate templates/examples/pageagent.yaml
```

**预期结果**:
- ✅ 所有场景语音生成成功
- ✅ 语音文件合并成功
- ✅ 字幕文件生成成功
- ✅ 提示手动录制视频

---

### 4. 端到端测试

#### 完整视频生成测试

**步骤**:

1. **准备配置文件**
   ```bash
   cp templates/examples/pageagent.yaml test-config.yaml
   ```

2. **生成语音和字幕**
   ```bash
   demo-gen generate test-config.yaml
   ```

3. **手动录制视频**
   ```bash
   agent-browser open "https://alibaba.github.io/page-agent/"
   agent-browser record start output/recording.webm
   # 执行操作...
   agent-browser record stop
   ```

4. **合成最终视频**
   ```bash
   # 手动运行合成步骤（或等待自动合成）
   ffmpeg -y -i output/recording.webm -i output/voiceover.aac \
     -vf "subtitles=output/subtitles.srt" \
     -c:v libx264 -c:a aac \
     -shortest output/demo.mp4
   ```

5. **验证输出**
   ```bash
   # 检查文件是否存在
   ls -lh output/demo.mp4
   
   # 检查视频时长
   ffprobe -v error -show_entries format=duration output/demo.mp4
   
   # 播放视频验证
   open output/demo.mp4
   ```

**验证项**:

- [ ] 视频文件生成成功
- [ ] 视频时长符合预期
- [ ] 音频清晰无杂音
- [ ] 字幕与语音同步
- [ ] 字幕显示正常
- [ ] 视频质量符合要求

---

## 🔍 质量检查

### 1. 字幕同步检查

**自动检查**:

```python
import subprocess

def check_subtitle_sync(video_file, subtitle_file):
    """检查字幕同步"""
    # 获取视频时长
    video_duration = float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', video_file],
        capture_output=True, text=True
    ).stdout.strip())
    
    # 解析字幕文件，获取最后一条字幕的结束时间
    with open(subtitle_file, 'r') as f:
        lines = f.readlines()
        last_time = 0
        for line in lines:
            if '-->' in line:
                end_time = line.split('-->')[1].strip()
                # 转换为秒
                h, m, s = end_time.replace(',', ':').split(':')
                last_time = int(h)*3600 + int(m)*60 + float(s)
    
    # 检查差异
    diff = abs(video_duration - last_time)
    
    if diff < 1.0:
        print(f"✅ 字幕同步良好（差异: {diff:.2f}s）")
        return True
    else:
        print(f"❌ 字幕不同步（差异: {diff:.2f}s）")
        return False
```

**手动检查**:
- 播放视频，观察字幕是否与语音同步
- 检查字幕是否在语音开始时出现
- 检查字幕是否在语音结束时消失

---

### 2. 音频质量检查

**自动检查**:

```bash
# 检查音频质量
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels output/voiceover.aac
```

**预期输出**:
```
codec_name=aac
sample_rate=24000
channels=1
```

**手动检查**:
- 播放音频，检查是否清晰
- 检查是否有杂音或爆音
- 检查语速是否合适

---

### 3. 视频质量检查

**自动检查**:

```bash
# 检查视频质量
ffprobe -v error -show_entries stream=width,height,codec_name,r_frame_rate output/demo.mp4
```

**预期输出**:
```
width=1280
height=720
codec_name=h264
r_frame_rate=30/1
```

**手动检查**:
- 播放视频，检查画面是否清晰
- 检查是否有卡顿或跳帧
- 检查字幕是否清晰可读

---

### 4. 文件大小检查

**自动检查**:

```bash
# 检查文件大小
ls -lh output/demo.mp4
```

**预期**:
- 文件大小 < 5MB/分钟
- 例如：2分钟视频 < 10MB

---

## 📊 性能测试

### 1. 生成速度测试

**测试脚本**:

```bash
#!/bin/bash

# 测试语音生成速度
start_time=$(date +%s)

demo-gen generate config.yaml

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "生成耗时: ${duration}秒"
```

**预期**:
- 语音生成: < 30秒
- 字幕生成: < 5秒
- 总耗时: < 5分钟

---

### 2. 资源占用测试

**测试脚本**:

```bash
#!/bin/bash

# 监控资源占用
/usr/bin/time -v demo-gen generate config.yaml
```

**预期**:
- CPU: < 50%
- 内存: < 500MB
- 磁盘: < 100MB临时文件

---

## 🐛 故障排查

### 常见问题

#### 1. 字幕不同步

**症状**: 字幕与语音不匹配

**检查**:
```bash
# 检查语音时长
ffprobe -v error -show_entries format=duration output/voice-01.mp3

# 检查字幕时间轴
cat output/subtitles.srt
```

**解决**:
- 确保使用最新版本的脚本
- 重新生成语音和字幕

---

#### 2. 语音质量差

**症状**: 语音不清晰或有杂音

**检查**:
```bash
# 检查语音编码
ffprobe -v error -show_entries stream=codec_name,sample_rate output/voice-01.mp3
```

**解决**:
- 检查网络连接（Edge-TTS需要联网）
- 尝试其他语音

---

#### 3. 视频合成失败

**症状**: ffmpeg 报错

**检查**:
```bash
# 检查 ffmpeg 版本
ffmpeg -version

# 检查输入文件
ls -lh output/*.webm output/*.aac output/*.srt
```

**解决**:
- 更新 ffmpeg 到最新版本
- 检查文件路径是否正确

---

## ✅ 验收标准

### 功能验收

- [ ] 配置文件验证通过
- [ ] 语音生成成功
- [ ] 字幕生成成功
- [ ] 视频合成成功
- [ ] 字幕同步正确
- [ ] 音频质量良好
- [ ] 视频质量良好

### 性能验收

- [ ] 生成时间 < 5分钟
- [ ] 文件大小 < 5MB/分钟
- [ ] CPU占用 < 50%
- [ ] 内存占用 < 500MB

### 质量验收

- [ ] 字幕同步精度 < 100ms
- [ ] 语音质量 MOS > 4.0
- [ ] 视频分辨率 >= 720p
- [ ] 无明显卡顿或跳帧

---

## 📝 测试报告模板

```markdown
# Demo Video Generator 测试报告

## 测试环境

- 操作系统: macOS 12.0
- Python版本: 3.9.0
- ffmpeg版本: 5.0
- edge-tts版本: 6.1.0

## 测试结果

### 功能测试

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 配置验证 | ✅ 通过 | - |
| 语音生成 | ✅ 通过 | 时长准确 |
| 字幕生成 | ✅ 通过 | 同步精确 |
| 视频合成 | ✅ 通过 | 质量良好 |

### 性能测试

| 指标 | 目标 | 实际 | 结果 |
|------|------|------|------|
| 生成时间 | < 5分钟 | 3分20秒 | ✅ |
| 文件大小 | < 5MB/min | 3.2MB/min | ✅ |
| CPU占用 | < 50% | 35% | ✅ |
| 内存占用 | < 500MB | 280MB | ✅ |

### 质量测试

| 指标 | 目标 | 实际 | 结果 |
|------|------|------|------|
| 字幕同步 | < 100ms | 45ms | ✅ |
| 语音质量 | MOS > 4.0 | MOS 4.2 | ✅ |
| 视频分辨率 | >= 720p | 1080p | ✅ |

## 问题记录

无

## 结论

✅ 所有测试通过，产品可以发布
```

---

**文档版本**: 1.0  
**最后更新**: 2026-03-30
