# 抖音视频文字提取工作流 - 部署指南

## 🚀 快速部署

### 1. 安装技能
```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/douyin-asr-workflow

# 安装依赖
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# 安装Python依赖
pip3 install -r requirements.txt

# 安装Whisper技能
openclaw skill install openai-whisper
```

### 2. 测试功能
```bash
# 测试基本功能
python3 scripts/test_workflow.py

# 测试自动响应
python3 scripts/auto_responder.py "https://v.douyin.com/MnqFZFeXX9w/" --test
```

### 3. 集成到OpenClaw

#### 方法A：自动集成（推荐）
将技能目录链接到OpenClaw插件目录：
```bash
ln -sf ~/.openclaw/workspace/skills/douyin-asr-workflow \
       ~/.openclaw/plugins/douyin-asr-workflow
```

#### 方法B：手动配置
编辑OpenClaw配置文件 `~/.openclaw/config.yaml`：
```yaml
plugins:
  douyin-asr-workflow:
    enabled: true
    path: ~/.openclaw/workspace/skills/douyin-asr-workflow/integration
    config: ~/.openclaw/workspace/skills/douyin-asr-workflow/integration/config.json
```

### 4. 重启OpenClaw
```bash
openclaw restart
```

## 📋 功能验证

### 测试消息
发送以下消息测试自动响应：

1. **抖音链接**：
   ```
   https://v.douyin.com/MnqFZFeXX9w/
   ```

2. **带说明的链接**：
   ```
   帮我提取这个抖音视频的文字：https://v.douyin.com/MnqFZFeXX9w/
   ```

3. **使用命令**：
   ```
   /douyin https://v.douyin.com/MnqFZFeXX9w/
   ```

### 预期响应
```
🎬 检测到抖音链接，正在启动文字提取工作流...

⏳ 处理中...
✅ 文字提取完成！

📝 提取结果：
（视频文字内容）

📊 统计：XXX字符，XXX词
⏱️ 耗时：XX.XX秒
```

## ⚙️ 配置说明

### 核心配置
编辑 `integration/config.json`：

```json
{
  "enabled": true,
  "auto_trigger": true,
  "require_confirmation": false,
  "model": "base",
  "timeout": 300
}
```

### 用户管理
```json
{
  "allowed_users": [],      # 空数组 = 所有用户
  "excluded_users": []      # 排除的用户
}
```

### 性能限制
```json
{
  "limits": {
    "max_video_size_mb": 100,
    "max_daily_requests": 50,
    "max_concurrent": 3
  }
}
```

## 🔧 高级配置

### 自定义触发器
编辑 `scripts/auto_responder.py`：

```python
# 添加新的触发模式
self.douyin_patterns = [
    r'https://v\.douyin\.com/[^\s<>"\']+',
    # 添加更多模式...
]

# 添加新的触发关键词
self.trigger_keywords = [
    "抖音视频转文字",
    # 添加更多关键词...
]
```

### 自定义响应格式
编辑 `integration/config.json`：

```json
{
  "output": {
    "format": "markdown",
    "include_video_info": true,
    "include_transcription": true,
    "truncate_length": 1000
  }
}
```

## 🐳 Docker部署

### Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 安装yt-dlp和whisper
RUN pip3 install yt-dlp openai-whisper

# 复制技能文件
COPY . /app
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV WHISPER_MODEL=base

# 启动命令
CMD ["python3", "scripts/douyin_asr_workflow.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  douyin-workflow:
    build: .
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./cache:/root/.cache
    environment:
      - WHISPER_MODEL=base
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

## 📊 监控和维护

### 日志文件
- `logs/douyin_workflow.log` - 工作流日志
- `logs/auto_responder.log` - 自动响应日志
- `logs/errors.log` - 错误日志

### 监控命令
```bash
# 查看实时日志
tail -f logs/douyin_workflow.log

# 查看处理统计
grep -c "处理完成" logs/douyin_workflow.log

# 查看错误统计
grep -c "错误" logs/errors.log
```

### 定期维护
```bash
# 清理临时文件
find /tmp -name "douyin_*" -mtime +1 -delete

# 清理日志文件
find logs -name "*.log" -mtime +7 -delete

# 更新依赖
pip3 install --upgrade -r requirements.txt
```

## 🔒 安全配置

### 访问控制
```json
{
  "allowed_users": ["user1", "user2"],
  "excluded_users": ["spam_user"]
}
```

### 速率限制
```json
{
  "rate_limits": {
    "per_user_per_day": 10,
    "per_ip_per_hour": 20
  }
}
```

### 内容过滤
```json
{
  "content_filters": {
    "block_keywords": ["暴力", "色情", "政治"],
    "max_video_duration": 300
  }
}
```

## 🚨 故障排除

### 常见问题

1. **不自动响应**
   ```bash
   # 检查配置
   cat integration/config.json | grep -A2 -B2 "auto_trigger"
   
   # 检查日志
   tail -f logs/auto_responder.log
   ```

2. **处理失败**
   ```bash
   # 检查依赖
   python3 scripts/test_workflow.py
   
   # 检查网络
   curl -I https://v.douyin.com/
   
   # 检查磁盘空间
   df -h
   ```

3. **性能问题**
   ```bash
   # 查看资源使用
   top -p $(pgrep -f douyin)
   
   # 调整配置
   # 减小视频质量：修改 scripts/douyin_asr_workflow.py 中的 yt-dlp 参数
   # 使用更小的模型：修改 config.json 中的 model 为 "tiny"
   ```

### 调试模式
```bash
# 启用调试
export DOUYIN_DEBUG=true
export LOG_LEVEL=DEBUG

# 运行测试
python3 scripts/douyin_asr_workflow.py "https://v.douyin.com/test/" --verbose
```

## 📈 性能优化

### 硬件要求
- **CPU**: 2+ 核心
- **内存**: 2+ GB
- **磁盘**: 10+ GB（Whisper模型缓存）
- **网络**: 稳定连接

### 优化建议
1. **使用SSD** - 加快模型加载
2. **增加内存** - 减少磁盘交换
3. **使用CDN** - 加速视频下载
4. **批量处理** - 提高吞吐量

### 基准测试
```bash
# 测试处理速度
time python3 scripts/douyin_asr_workflow.py "测试链接"

# 测试并发能力
./scripts/benchmark.py
```

## 🔄 更新升级

### 版本升级
```bash
# 备份配置
cp -r integration/config.json integration/config.json.backup

# 更新代码
git pull origin main

# 更新依赖
pip3 install --upgrade -r requirements.txt

# 重启服务
openclaw restart
```

### 数据迁移
```bash
# 备份数据
tar -czf douyin_backup_$(date +%Y%m%d).tar.gz logs/ cache/

# 恢复数据
tar -xzf douyin_backup_YYYYMMDD.tar.gz
```

## 📚 相关文档

- [SKILL.md](./SKILL.md) - 技能主文档
- [README.md](./README.md) - 使用说明
- [OPENCLAW_INTEGRATION.md](./OPENCLAW_INTEGRATION.md) - OpenClaw集成指南
- [TRIGGER.md](./TRIGGER.md) - 触发器配置

## 🆘 获取帮助

### 问题反馈
1. 查看日志文件
2. 检查配置参数
3. 测试基本功能
4. 联系技术支持

### 社区支持
- OpenClaw Discord 社区
- GitHub Issues
- 技术文档

## 🎯 部署检查清单

- [ ] 安装所有依赖
- [ ] 测试基本功能
- [ ] 配置自动响应
- [ ] 设置访问控制
- [ ] 配置监控日志
- [ ] 测试实际消息
- [ ] 验证安全设置
- [ ] 备份配置数据

## ✅ 部署完成

当所有检查项完成时，抖音视频文字提取工作流已成功集成到OpenClaw，可以自动响应抖音链接并提取文字内容！

**部署状态**: ✅ 完成
**集成方式**: OpenClaw自动响应
**磁盘优化**: 使用base模型（74MB）
**功能验证**: 测试通过