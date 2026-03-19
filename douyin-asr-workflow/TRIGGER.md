# 抖音视频文字提取工作流 - 触发器配置

## 自动触发规则

当用户消息包含以下模式时，自动触发此工作流：

### 1. 抖音链接模式
- `https://v.douyin.com/`
- `https://www.douyin.com/video/`
- `https://www.iesdouyin.com/share/video/`

### 2. 关键词模式
- "抖音视频转文字"
- "提取抖音文字"
- "抖音字幕"
- "抖音内容转文字"

### 3. 命令模式
- "/douyin 链接"
- "/抖音转文字 链接"

## 响应流程

1. **检测到抖音链接** → 自动启动工作流
2. **显示处理状态** → 实时更新进度
3. **返回结果** → 提供文字内容和详细报告

## 集成配置

### 方法1：修改SKILL.md（推荐）
在SKILL.md中添加触发器配置：

```yaml
metadata:
  openclaw:
    triggers:
      patterns:
        - "https://v\\.douyin\\.com/"
        - "抖音视频转文字"
      commands:
        - "/douyin"
        - "/抖音转文字"
```

### 方法2：创建触发器脚本
创建 `scripts/trigger_handler.py` 处理自动触发。

### 方法3：使用OpenClaw事件系统
监听消息事件，检测抖音链接。

## 示例交互

### 用户输入
```
用户: 帮我提取这个抖音视频的文字：https://v.douyin.com/MnqFZFeXX9w/
```

### 自动响应
```
卡卡西AI助手: 检测到抖音链接，正在启动文字提取工作流...

[处理中] 获取视频信息...
[处理中] 下载视频...
[处理中] 提取音频...
[处理中] 语音转文字...
[完成] 文字提取完成！

📝 提取结果:
俄罗斯油轮马上抵达中国，突然在南海掉头把油送往印度...
（完整文字内容）

📊 统计: 856字符，156词
⏱️ 耗时: 45.23秒
```

## 实现步骤

### 1. 创建触发器处理器
```python
# scripts/trigger_handler.py
import re

def should_trigger(message):
    """检查是否应该触发工作流"""
    patterns = [
        r'https://v\.douyin\.com/',
        r'抖音视频转文字',
        r'提取抖音文字'
    ]
    
    for pattern in patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    
    return False

def extract_douyin_url(message):
    """从消息中提取抖音链接"""
    patterns = [
        r'https://v\.douyin\.com/[^\s]+',
        r'https://www\.douyin\.com/video/[^\s]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(0)
    
    return None
```

### 2. 集成到主消息处理
在OpenClaw的消息处理流程中调用触发器。

### 3. 异步处理
使用异步任务处理长时工作流，避免阻塞主线程。

## 配置说明

### 环境变量
```bash
# 启用自动触发
export DOUYIN_AUTO_TRIGGER=true

# 设置处理超时（秒）
export DOUYIN_TIMEOUT=300

# 设置最大视频长度（秒）
export DOUYIN_MAX_DURATION=300
```

### 配置文件
创建 `config/trigger.yaml`：
```yaml
douyin:
  auto_trigger: true
  patterns:
    - "https://v.douyin.com/"
    - "抖音"
  exclude_patterns:
    - "不要处理"
    - "跳过"
  max_duration: 300
  model: "base"
```

## 高级功能

### 1. 批量处理
支持多个抖音链接同时处理。

### 2. 进度回调
实时向用户发送处理进度。

### 3. 结果缓存
避免重复处理相同视频。

### 4. 错误恢复
处理失败时提供重试选项。

## 测试触发器

### 测试脚本
```python
# scripts/test_trigger.py
from trigger_handler import should_trigger, extract_douyin_url

test_messages = [
    "https://v.douyin.com/MnqFZFeXX9w/",
    "帮我提取抖音文字：https://v.douyin.com/xxxx/",
    "抖音视频转文字",
    "这个视频不错：https://v.douyin.com/yyyy/"
]

for msg in test_messages:
    if should_trigger(msg):
        url = extract_douyin_url(msg)
        print(f"触发: {msg}")
        print(f"提取链接: {url}")
```

## 部署说明

### 1. 本地部署
将触发器脚本添加到OpenClaw的插件目录。

### 2. 云部署
配置Webhook接收消息，触发工作流。

### 3. Docker部署
创建包含所有依赖的Docker镜像。

## 注意事项

1. **用户确认**：首次触发前可询问用户确认
2. **资源限制**：限制并发处理数量
3. **错误处理**：友好的错误提示
4. **隐私保护**：明确说明数据处理方式

## 监控和日志

### 日志文件
- `logs/trigger.log` - 触发器日志
- `logs/workflow.log` - 工作流日志
- `logs/errors.log` - 错误日志

### 监控指标
- 触发次数
- 处理成功率
- 平均处理时间
- 错误类型统计