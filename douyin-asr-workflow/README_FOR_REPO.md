# 抖音视频文字提取工作流 Skill

## 概述

这是一个完整的抖音视频处理工作流，将抖音视频分享链接转换为文字内容。技能使用本地Whisper进行语音识别，无需API密钥，特别优化了小磁盘环境。

## 功能特性

- 🎯 **全自动处理**：从抖音链接到文字内容，一键完成
- 🔒 **本地处理**：使用Whisper base模型（74MB），无需API密钥
- 💾 **磁盘友好**：base模型比medium模型小90%+
- 🤖 **智能集成**：自动响应OpenClaw中的抖音链接
- 📊 **详细报告**：完整的过程日志和结果统计

## 快速开始

### 安装
```bash
# 1. 复制技能到OpenClaw技能目录
cp -r douyin-asr-workflow ~/.openclaw/workspace/skills/

# 2. 安装依赖
cd ~/.openclaw/workspace/skills/douyin-asr-workflow
./scripts/install_dependencies.sh
pip3 install -r requirements.txt

# 3. 安装Whisper技能
openclaw skill install openai-whisper
```

### 使用
```bash
# 直接运行
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxxxxx/"

# 在OpenClaw中自动响应
# 发送抖音链接即可自动触发
```

## 文件结构

```
douyin-asr-workflow/
├── SKILL.md                    # 技能主文档
├── README.md                   # 详细使用说明
├── DEPLOYMENT.md               # 部署指南
├── OPENCLAW_INTEGRATION.md     # OpenClaw集成指南
├── FINAL_SUMMARY.md            # 项目总结
├── scripts/
│   ├── douyin_asr_workflow.py  # 主工作流脚本
│   ├── auto_responder.py       # 自动响应器
│   ├── test_workflow.py        # 测试脚本
│   └── install_dependencies.sh # 依赖安装脚本
├── integration/
│   ├── openclaw_integration.py # OpenClaw集成模块
│   └── config.json             # 配置文件
├── examples/                   # 使用示例
└── docs/                       # 技术文档
```

## 技术栈

- **Python 3.7+** - 主编程语言
- **OpenAI Whisper** - 本地语音识别
- **yt-dlp** - 视频下载
- **ffmpeg** - 音频提取
- **agent-reach** - 抖音链接解析

## 性能指标

- **模型大小**: 74MB (Whisper base模型)
- **处理时间**: 1分钟视频约30-60秒
- **内存占用**: 200-500MB
- **磁盘占用**: 临时文件自动清理

## 使用场景

1. **内容创作** - 提取抖音视频文字作为素材
2. **学习研究** - 转录教育类视频内容
3. **信息整理** - 批量处理多个抖音视频
4. **无障碍访问** - 为听障用户提供文字内容

## 配置选项

编辑 `integration/config.json`：
```json
{
  "enabled": true,
  "auto_trigger": true,
  "model": "base",
  "timeout": 300
}
```

## 许可证

MIT License

## 作者

卡卡西AI助手

## 贡献

欢迎提交Issue和Pull Request改进这个工作流。

## 相关链接

- [OpenClaw文档](https://docs.openclaw.ai)
- [Whisper GitHub](https://github.com/openai/whisper)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)