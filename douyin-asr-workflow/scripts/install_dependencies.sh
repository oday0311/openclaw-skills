#!/bin/bash
# 抖音视频文字提取工作流依赖安装脚本

set -e

echo "安装抖音视频文字提取工作流依赖..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要Python3"
    exit 1
fi

# 检查pip3
if ! command -v pip3 &> /dev/null; then
    echo "错误: 需要pip3"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r ../requirements.txt

# 检查并安装yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "安装yt-dlp..."
    pip3 install yt-dlp
else
    echo "yt-dlp 已安装"
fi

# 检查并安装ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "安装ffmpeg..."
    
    # 根据系统类型安装ffmpeg
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        else
            echo "警告: 无法自动安装ffmpeg，请手动安装"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "警告: 需要Homebrew来安装ffmpeg，请先安装Homebrew或手动安装ffmpeg"
        fi
    else
        echo "警告: 不支持的系统类型，请手动安装ffmpeg"
    fi
else
    echo "ffmpeg 已安装"
fi

# 检查并安装mcporter（agent-reach的一部分）
if ! command -v mcporter &> /dev/null; then
    echo "安装mcporter..."
    
    # 尝试通过npm安装
    if command -v npm &> /dev/null; then
        npm install -g @mcporter/cli
    else
        echo "警告: 需要Node.js/npm来安装mcporter"
        echo "请先安装Node.js，然后运行: npm install -g @mcporter/cli"
    fi
else
    echo "mcporter 已安装"
fi

# 检查agent-reach技能
echo "检查agent-reach技能..."
AGENT_REACH_DIR="$HOME/.openclaw/workspace/skills/agent-reach"
if [ ! -d "$AGENT_REACH_DIR" ]; then
    echo "警告: agent-reach技能未找到"
    echo "请确保agent-reach技能已安装"
else
    echo "agent-reach技能已安装"
fi

# 检查腾讯云ASR技能
echo "检查腾讯云ASR技能..."
TENCENT_ASR_DIR="$HOME/.openclaw/workspace/skills/tencentcloud-asr"
if [ ! -d "$TENCENT_ASR_DIR" ]; then
    echo "警告: 腾讯云ASR技能未找到"
    echo "请确保tencentcloud-asr技能已安装"
fi

echo ""
echo "依赖安装完成！"
echo ""
echo "使用说明:"
echo "1. 确保已安装openai-whisper技能: openclaw skill install openai-whisper"
echo "2. 运行工作流: python3 douyin_asr_workflow.py <抖音分享链接>"
echo "3. 查看详细日志: python3 douyin_asr_workflow.py <链接> --verbose"
echo "4. 保存报告: python3 douyin_asr_workflow.py <链接> --output report.md"
echo ""
echo "注意:"
echo "- Whisper第一次运行时会下载base模型（约74MB）"
echo "- 工作流固定使用base模型以节省磁盘空间"
echo "- 如需更改模型，请编辑脚本中的 --model 参数"