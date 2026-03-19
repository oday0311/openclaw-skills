# OpenClaw 集成指南

## 概述

本文档说明如何将抖音视频文字提取工作流集成到OpenClaw系统中，实现自动响应抖音链接的功能。

## 集成方式

### 方式1：作为技能插件（推荐）

将本技能注册为OpenClaw插件，自动处理包含抖音链接的消息。

### 方式2：作为独立服务

通过API或Webhook与OpenClaw集成。

### 方式3：作为命令行工具

通过OpenClaw的命令系统调用。

## 快速集成

### 步骤1：安装依赖

```bash
cd ~/.openclaw/workspace/skills/douyin-asr-workflow
./scripts/install_dependencies.sh
pip3 install -r requirements.txt
openclaw skill install openai-whisper
```

### 步骤2：配置OpenClaw

编辑OpenClaw配置文件 `~/.openclaw/config.yaml`：

```yaml
skills:
  douyin-asr-workflow:
    enabled: true
    auto_trigger: true
    config_path: ~/.openclaw/workspace/skills/douyin-asr-workflow/integration/config.json
```

### 步骤3：重启OpenClaw

```bash
openclaw restart
```

## 自动响应配置

### 触发条件

当用户消息满足以下任一条件时，自动触发工作流：

1. **包含抖音链接**：
   - `https://v.douyin.com/`
   - `https://www.douyin.com/video/`

2. **包含关键词**：
   - "抖音视频转文字"
   - "提取抖音文字"
   - "抖音字幕"

3. **使用命令**：
   - `/douyin <链接>`
   - `/抖音转文字 <链接>`

### 响应流程

```
用户消息 → 检测抖音链接 → 启动工作流 → 返回结果
```

## 消息处理示例

### 用户输入
```
帮我提取这个抖音视频的文字：https://v.douyin.com/MnqFZFeXX9w/
```

### 自动响应
```
🎬 检测到抖音链接，正在启动文字提取工作流...

⏳ 处理中...
✅ 下载视频完成
✅ 提取音频完成
✅ 语音转文字完成

📝 提取结果：
俄罗斯油轮马上抵达中国，突然在南海掉头把油送往印度...

📊 统计：856字符，156词
⏱️ 耗时：45.23秒
```

## 配置选项

### 基本配置
```yaml
# config.json
{
  "enabled": true,                    # 启用/禁用
  "auto_trigger": true,               # 自动触发
  "require_confirmation": false,      # 需要用户确认
  "max_duration": 300,                # 最大视频时长（秒）
  "model": "base"                     # Whisper模型
}
```

### 用户管理
```yaml
{
  "allowed_users": [],                # 允许的用户列表（空=所有）
  "excluded_users": []                # 排除的用户列表
}
```

### 限制设置
```yaml
{
  "limits": {
    "max_video_size_mb": 100,         # 最大视频大小
    "max_daily_requests": 50,         # 每日最大请求数
    "max_concurrent": 3               # 最大并发数
  }
}
```

## API 接口

### 直接调用工作流
```bash
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/xxxx/" --verbose
```

### 通过自动响应器
```python
from scripts.auto_responder import DouyinAutoResponder

responder = DouyinAutoResponder()
result = await responder.process_message("抖音链接")
```

### 通过OpenClaw插件
```python
from integration.openclaw_integration import DouyinPlugin

plugin = DouyinPlugin()
response = await plugin.handle_message(message_event)
```

## 测试集成

### 测试脚本
```bash
# 测试自动响应
python3 scripts/auto_responder.py "https://v.douyin.com/MnqFZFeXX9w/" --test

# 测试完整集成
python3 integration/openclaw_integration.py
```

### 测试用例
```python
test_messages = [
    "https://v.douyin.com/MnqFZFeXX9w/",
    "抖音视频转文字 https://v.douyin.com/xxxx/",
    "/douyin https://v.douyin.com/yyyy/",
    "不要处理这个抖音链接"
]
```

## 监控和日志

### 日志文件
- `logs/douyin_workflow.log` - 工作流日志
- `logs/auto_responder.log` - 自动响应器日志
- `logs/errors.log` - 错误日志

### 监控指标
- 触发次数
- 处理成功率
- 平均处理时间
- 资源使用情况

## 故障排除

### 常见问题

1. **不自动响应**
   - 检查 `auto_trigger` 配置
   - 检查消息是否匹配触发模式
   - 查看日志文件

2. **处理失败**
   - 检查网络连接
   - 检查磁盘空间
   - 查看错误日志

3. **性能问题**
   - 调整视频质量设置
   - 使用更小的Whisper模型
   - 增加超时时间

### 调试模式
```bash
# 启用详细日志
export DOUYIN_DEBUG=true

# 查看实时日志
tail -f logs/douyin_workflow.log
```

## 高级配置

### 自定义触发器
编辑 `scripts/auto_responder.py` 中的模式匹配规则。

### 自定义响应格式
修改 `integration/config.json` 中的输出配置。

### 添加新命令
在 `integration/openclaw_integration.py` 中添加新的命令处理器。

## 安全考虑

### 用户权限
- 限制敏感操作
- 记录用户活动
- 实现速率限制

### 资源保护
- 限制视频大小
- 限制并发处理
- 定期清理临时文件

### 隐私保护
- 本地处理音频
- 不存储用户数据
- 自动清理临时文件

## 扩展开发

### 添加新功能
1. 批量处理
2. 字幕生成
3. 翻译功能
4. 情感分析

### 集成其他平台
1. B站视频
2. YouTube视频
3. 微信视频号

## 性能优化

### 缓存策略
- 缓存视频信息
- 缓存识别结果
- 模型预加载

### 并行处理
- 多视频并行处理
- 异步任务队列
- 负载均衡

## 部署建议

### 生产环境
- 使用Docker容器
- 配置监控告警
- 定期备份配置

### 开发环境
- 使用虚拟环境
- 启用调试日志
- 配置测试数据

## 更新维护

### 版本升级
1. 备份配置和数据
2. 更新代码和依赖
3. 测试新功能
4. 部署到生产

### 日常维护
1. 监控日志文件
2. 清理临时文件
3. 更新依赖包
4. 优化配置参数