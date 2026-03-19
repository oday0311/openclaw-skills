# 抖音视频文字提取工作流 - 快速开始

## 1. 安装技能

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/douyin-asr-workflow

# 安装依赖
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# 安装Python依赖
pip3 install -r requirements.txt
```

## 2. 安装Whisper技能

```bash
# 安装openai-whisper技能
openclaw skill install openai-whisper
```

## 3. 测试安装

```bash
# 运行测试脚本
python3 scripts/test_workflow.py
```

## 4. 基本使用

```bash
# 处理抖音视频
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/"

# 显示详细过程
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/" --verbose

# 保存报告到文件
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/" --output result.md
```

## 5. 在OpenClaw中使用

当用户发送抖音链接时，会自动触发此工作流：

```
用户: 帮我提取这个抖音视频的文字：https://v.douyin.com/xxxxxxx/

卡卡西AI助手: 好的，我来处理这个抖音视频。启动文字提取工作流...
```

## 6. 自定义配置

### 修改Whisper模型（不推荐，当前使用base模型节省磁盘）

编辑 `scripts/douyin_asr_workflow.py`，找到以下行：

```python
whisper_cmd = [
    "whisper",
    audio_path,
    "--model", "base",  # 当前使用base模型，可修改为：tiny, small, medium, large
    # ...
]
```

### 修改音频格式

```python
# 修改音频采样率（默认16000Hz）
cmd = [
    "ffmpeg",
    "-i", video_path,
    "-vn",
    "-acodec", "pcm_s16le",
    "-ar", "16000",  # 修改这里
    "-ac", "1",
    "-y",
    audio_path
]
```

## 7. 故障排除

### 常见问题

1. **"whisper命令未找到"**
   ```bash
   # 确保已安装openai-whisper技能
   openclaw skill install openai-whisper
   ```

2. **模型下载缓慢**
   ```bash
   # 使用较小的模型
   # 修改脚本中的 --model 参数为 "tiny" 或 "base"
   ```

3. **视频下载失败**
   ```bash
   # 检查网络连接
   # 尝试使用代理
   export http_proxy="http://your-proxy:port"
   ```

4. **内存不足**
   ```bash
   # 当前已使用base模型（内存需求较低）
   # 如果仍然内存不足，可改为tiny模型
   ```

## 8. 性能提示

- **第一次运行较慢**: Whisper需要下载base模型文件（约74MB）
- **使用SSD**: 模型加载速度更快
- **批量处理**: 可以编写脚本批量处理多个视频
- **缓存结果**: 相同视频ID可以跳过重复处理

## 9. 输出示例

工作流会生成详细的报告，包括：

- 视频信息（标题、作者、时长）
- 处理步骤日志
- 完整的文字转录
- 错误信息（如果有）

## 10. 下一步

- 查看完整文档: `README.md`
- 查看使用示例: `examples/example_usage.md`
- 查看脚本源码: `scripts/douyin_asr_workflow.py`