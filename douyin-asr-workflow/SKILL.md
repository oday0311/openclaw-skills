---
name: douyin-asr-workflow
description: >
  抖音视频文字提取工作流。从抖音视频分享链接开始，自动获取视频内容，提取音频文件，
  然后通过本地Whisper将音频转换为文字，最后提供完整的过程汇报。
  
  **当以下情况时使用此 Skill**：
  (1) 用户提供抖音视频分享链接需要提取文字内容
  (2) 需要完整的抖音视频处理工作流（获取→提取音频→转文字）
  (3) 用户需要过程汇报和结果验证
  (4) 用户提到"抖音视频转文字"、"抖音字幕提取"、"视频内容转录"
  (5) 希望使用本地语音识别，无需API密钥
metadata:
  openclaw:
    category: workflow
    dependencies:
      - agent-reach
      - openai-whisper
    platforms:
      - douyin
---

# 抖音视频文字提取工作流 Skill

这是一个端到端的抖音视频处理工作流，将抖音视频分享链接转换为文字内容。

## 工作流程

1. **输入验证** - 验证抖音分享链接格式
2. **视频获取** - 使用agent-reach获取抖音视频信息
3. **音频提取** - 使用ffmpeg从视频中提取音频
4. **语音转文字** - 使用腾讯云ASR将音频转换为文字
5. **结果汇报** - 提供完整的过程日志和最终结果

## 前置要求

确保以下技能已安装并配置：
- `agent-reach` - 用于抖音视频获取
- `openai-whisper` - 用于本地语音转文字
- `ffmpeg` - 用于音频提取（会自动安装）

## 核心执行流

### 1. 抖音视频信息获取

```bash
# 使用agent-reach的douyin工具解析视频信息
mcporter call 'douyin.parse_douyin_video_info(share_link: "抖音分享链接")'
```

### 2. 视频下载和音频提取

```bash
# 下载视频（使用yt-dlp）
yt-dlp -f "best[height<=720]" -o "/tmp/douyin_%(id)s.%(ext)s" "视频URL"

# 提取音频为WAV格式（适合ASR处理）
ffmpeg -i "/tmp/douyin_视频ID.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "/tmp/douyin_视频ID.wav"
```

### 3. 音频转文字

```bash
# 使用本地Whisper进行语音识别（使用base模型节省磁盘空间）
whisper "/tmp/douyin_视频ID.wav" --model base --output_format txt --output_dir /tmp
```

### 4. 清理临时文件

```bash
# 清理下载的视频和音频文件
rm -f "/tmp/douyin_视频ID.mp4" "/tmp/douyin_视频ID.wav"
```

## 完整示例脚本

参考 `scripts/douyin_asr_workflow.py` 获取完整的实现。

## 错误处理

- **链接无效**：检查抖音分享链接格式（应以 `https://v.douyin.com/` 开头）
- **视频无法访问**：可能需要处理地区限制或登录要求
- **音频提取失败**：检查ffmpeg安装和视频格式
- **Whisper识别失败**：检查Whisper安装和音频质量

## 输出格式

工作流会生成以下输出：

1. **过程日志**：每个步骤的执行状态和结果
2. **视频信息**：视频标题、作者、时长等元数据
3. **文字内容**：完整的转录文字
4. **时间戳**：处理开始和结束时间

## 性能优化

- 对于长视频（>2分钟），建议分段处理
- 可以缓存已处理的视频ID避免重复处理
- 支持批量处理多个抖音链接