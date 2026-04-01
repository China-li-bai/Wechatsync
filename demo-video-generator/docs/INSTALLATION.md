# Demo Video Generator - 安装指南

## 📋 系统要求

- Python 3.8+
- ffmpeg (视频处理)
- edge-tts (语音生成)
- agent-browser (浏览器自动化)

---

## 🚀 快速安装

### 方法1: 使用 pipx（推荐）

```bash
# 安装核心依赖
pipx install PyYAML
pipx install tqdm

# 安装系统工具
pipx install edge-tts
npm install -g agent-browser

# 安装 ffmpeg (macOS)
brew install ffmpeg
```

---

### 方法2: 使用虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装系统工具
pip install edge-tts
npm install -g agent-browser

# 安装 ffmpeg (macOS)
brew install ffmpeg
```

---

### 方法3: 使用 --break-system-packages

```bash
# 安装依赖（不推荐，可能破坏系统环境）
pip3 install --break-system-packages PyYAML tqdm
```

---

## ✅ 验证安装

```bash
# 验证 Python 依赖
python3 -c "import yaml; print('✅ PyYAML')"
python3 -c "import tqdm; print('✅ tqdm')"

# 验证系统工具
edge-tts --version
agent-browser --version
ffmpeg -version
```

---

## 🔧 常见问题

### 问题1: externally-managed-environment

**错误信息**:
```
error: externally-managed-environment
```

**解决方案**:
使用虚拟环境或 pipx 安装

---

### 问题2: ModuleNotFoundError: No module named 'yaml'

**解决方案**:
```bash
pipx install PyYAML
# 或
pip3 install --break-system-packages PyYAML
```

---

### 问题3: edge-tts not found

**解决方案**:
```bash
pipx install edge-tts
```

---

### 问题4: agent-browser not found

**解决方案**:
```bash
npm install -g agent-browser
```

---

### 问题5: ffmpeg not found

**解决方案**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

---

## 📦 完整依赖列表

### Python 依赖

```
PyYAML>=6.0          # YAML 配置文件解析
tqdm>=4.65.0         # 进度条（可选）
```

### 系统工具

```
edge-tts            # 语音生成
agent-browser       # 浏览器自动化
ffmpeg              # 视频处理
```

---

## 🎯 下一步

安装完成后，请查看:

- [快速开始指南](QUICK-START.md)
- [配置详解](CONFIGURATION.md)
- [测试指南](TESTING.md)

---

**安装指南版本**: v1.1.0  
**最后更新**: 2026-03-30
