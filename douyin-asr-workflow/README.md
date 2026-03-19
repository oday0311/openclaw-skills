# 抖音视频文字提取工作流

一个端到端的抖音视频处理工作流，将抖音视频分享链接转换为文字内容。

## 功能特点

- 🎯 **全自动处理**: 从抖音链接到文字内容，一键完成
- 🔄 **完整工作流**: 视频获取 → 音频提取 → 语音转文字 → 结果汇报
- 📊 **详细日志**: 每个步骤都有详细的状态记录
- 🧹 **自动清理**: 处理完成后自动清理临时文件
- 📝 **多种输出**: 支持控制台输出和文件报告

## 工作流程

1. **输入验证** - 验证抖音分享链接格式
2. **视频获取** - 使用agent-reach获取抖音视频信息
3. **音频提取** - 使用ffmpeg从视频中提取音频
4. **语音转文字** - 使用腾讯云ASR将音频转换为文字
5. **结果汇报** - 提供完整的过程日志和最终结果

## 安装

### 前置要求

- Python 3.7+
- pip3
- ffmpeg
- yt-dlp
- mcporter (@mcporter/cli)
- openai-whisper技能

### 快速安装

```bash
# 1. 进入技能目录
cd ~/.openclaw/workspace/skills/douyin-asr-workflow

# 2. 安装依赖
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# 3. 安装Python依赖
pip3 install -r requirements.txt
```

### 依赖说明

- **agent-reach**: 用于抖音视频信息获取
- **openai-whisper**: 用于本地语音转文字（无需API密钥）
- **ffmpeg**: 用于音频提取
- **yt-dlp**: 用于视频下载
- **mcporter**: agent-reach的命令行工具

## 使用方法

### 基本用法

```bash
# 处理单个抖音视频
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/"

# 显示详细日志
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/" --verbose

# 保存报告到文件
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/" --output report.md
```

### 在OpenClaw中使用

当用户提供抖音分享链接时，此技能会自动触发：

```
用户: 帮我提取这个抖音视频的文字内容：https://v.douyin.com/xxxxxxx/

卡卡西AI助手: 好的，我来帮你处理这个抖音视频。让我启动抖音视频文字提取工作流...
```

## 配置

### Whisper模型配置

本工作流固定使用`base`模型以节省磁盘空间。base模型提供良好的平衡：
- 模型大小：约74MB（tiny: 39MB, small: 244MB, medium: 769MB, large: 1550MB）
- 准确度：适合大多数日常使用
- 速度：相对较快

如果你需要更改模型，可以修改 `scripts/douyin_asr_workflow.py` 中的模型参数：

```python
whisper_cmd = [
    "whisper",
    audio_path,
    "--model", "base",  # 修改这里：tiny, base, small, medium, large
    # ...
]
```

模型文件默认下载到 `~/.cache/whisper/` 目录。

### 代理设置（如果需要）

如果网络访问需要代理：

```bash
# 设置HTTP代理
export http_proxy="http://proxy-server:port"
export https_proxy="http://proxy-server:port"

# 对于yt-dlp
export YT_DLP_PROXY="http://proxy-server:port"
```

## 输出示例

### 控制台输出

```
[2024-01-15 10:30:00] [INFO] 开始抖音视频文字提取工作流
[2024-01-15 10:30:05] [INFO] 视频信息获取成功: 教你如何快速学习Python编程
[2024-01-15 10:30:45] [INFO] 工作流完成！总耗时: 45.23 秒
```

### 报告文件内容

报告文件包含：
- 基本信息（链接、时间、耗时）
- 视频信息（标题、作者、时长）
- 详细处理步骤
- 错误信息（如果有）
- 完整的文字转录结果

## 错误处理

工作流会处理以下常见错误：

- ❌ **无效链接**: 检查抖音分享链接格式
- ❌ **视频无法访问**: 视频可能已被删除或设为私密
- ❌ **网络超时**: 检查网络连接和代理设置
- ❌ **音频提取失败**: 检查ffmpeg安装和视频格式
- ❌ **Whisper识别失败**: 检查Whisper安装和音频质量

## 高级功能

### 批量处理

可以编写脚本批量处理多个抖音链接：

```python
#!/usr/bin/env python3
import subprocess

urls = [
    "https://v.douyin.com/url1/",
    "https://v.douyin.com/url2/",
    "https://v.douyin.com/url3/"
]

for url in urls:
    subprocess.run([
        "python3", "scripts/douyin_asr_workflow.py",
        url,
        "--output", f"report_{url.split('/')[-2]}.md"
    ])
```

### 自定义配置

可以通过修改脚本来自定义行为：

- 调整视频下载质量
- 修改音频采样率
- 更改ASR识别引擎
- 调整超时时间

## 性能优化

- **缓存机制**: 可以添加视频ID缓存避免重复处理
- **并行处理**: 对于批量任务可以使用多线程
- **分段处理**: 对于长视频可以分段处理提高识别准确率
- **结果存储**: 可以将结果保存到数据库或文件中

## 限制和注意事项

1. **网络依赖**: 需要稳定的网络连接
2. **API限制**: 腾讯云ASR有调用频率限制
3. **视频长度**: 建议处理5分钟以内的视频
4. **音频质量**: 背景噪音可能影响识别准确率
5. **版权问题**: 仅用于个人学习和研究

## 故障排除

### 常见问题

1. **"命令未找到"错误**
   - 检查所有依赖是否已安装
   - 运行 `./scripts/install_dependencies.sh`

2. **视频下载失败**
   - 检查网络连接
   - 尝试使用代理
   - 检查视频是否可公开访问

3. **Whisper识别失败**
   - 检查Whisper是否安装正确
   - 检查音频文件格式
   - 查看详细的错误日志
   - 检查磁盘空间（模型文件较大）

### 获取帮助

- 查看详细日志: 使用 `--verbose` 参数
- 检查依赖: 运行 `./scripts/install_dependencies.sh`
- 查看示例: 参考 `examples/` 目录

## 贡献

欢迎提交Issue和Pull Request来改进这个工作流。

## 许可证

MIT License