#!/usr/bin/env python3
"""
OpenClaw集成模块
将抖音视频文字提取工作流集成到OpenClaw系统
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skill_dir))

from scripts.auto_responder import DouyinAutoResponder

class DouyinOpenClawIntegration:
    """OpenClaw集成类"""
    
    def __init__(self, config_path=None):
        self.responder = DouyinAutoResponder()
        self.config = self.load_config(config_path)
        
        # 集成状态
        self.enabled = self.config.get("enabled", True)
        self.auto_trigger = self.config.get("auto_trigger", True)
        self.require_confirmation = self.config.get("require_confirmation", False)
        
        print(f"抖音工作流集成初始化完成")
        print(f"  启用状态: {'✅ 已启用' if self.enabled else '❌ 已禁用'}")
        print(f"  自动触发: {'✅ 开启' if self.auto_trigger else '❌ 关闭'}")
        print(f"  需要确认: {'✅ 是' if self.require_confirmation else '❌ 否'}")
    
    def load_config(self, config_path=None):
        """加载配置文件"""
        default_config = {
            "enabled": True,
            "auto_trigger": True,
            "require_confirmation": False,
            "max_duration": 300,  # 最大视频时长（秒）
            "allowed_users": [],  # 空列表表示所有用户
            "excluded_users": [],
            "model": "base",
            "timeout": 300,
            "temp_dir": "/tmp/douyin_workflow"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                print(f"从 {config_path} 加载配置")
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        return default_config
    
    def should_process_message(self, message_data):
        """判断是否应该处理此消息"""
        if not self.enabled:
            return False
        
        # 提取消息内容
        message = message_data.get("text", "")
        user_id = message_data.get("user_id", "")
        
        # 检查用户权限
        if self.config["allowed_users"] and user_id not in self.config["allowed_users"]:
            return False
        
        if user_id in self.config["excluded_users"]:
            return False
        
        # 检查是否应该响应
        if self.auto_trigger:
            return self.responder.should_respond(message)
        
        return False
    
    async def handle_message(self, message_data):
        """处理消息"""
        if not self.should_process_message(message_data):
            return None
        
        message = message_data.get("text", "")
        user_id = message_data.get("user_id", "")
        chat_id = message_data.get("chat_id", "")
        
        print(f"处理来自用户 {user_id} 的消息")
        print(f"消息内容: {message[:100]}...")
        
        # 如果需要确认，先发送确认消息
        if self.require_confirmation:
            confirmation_response = {
                "type": "confirmation",
                "text": f"检测到抖音链接，是否开始文字提取？\n链接: {self.responder.extract_douyin_url(message)}",
                "options": ["开始处理", "取消"],
                "callback": "douyin_confirmation"
            }
            return confirmation_response
        
        # 直接处理
        result = await self.responder.process_message(message)
        
        if result.get("should_respond"):
            return {
                "type": "response",
                "text": result.get("response", "处理完成"),
                "metadata": result
            }
        
        return None
    
    async def handle_confirmation(self, confirmation_data):
        """处理用户确认"""
        user_choice = confirmation_data.get("choice")
        original_message = confirmation_data.get("original_message")
        
        if user_choice == "开始处理":
            # 处理原始消息
            result = await self.responder.process_message(original_message)
            
            if result.get("should_respond"):
                return {
                    "type": "response",
                    "text": result.get("response", "处理完成"),
                    "metadata": result
                }
        else:
            return {
                "type": "response",
                "text": "已取消抖音视频处理。"
            }
        
        return None

# OpenClaw插件接口
class DouyinPlugin:
    """OpenClaw插件类"""
    
    def __init__(self):
        self.integration = None
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            "config.json"
        )
    
    def initialize(self, openclaw_config):
        """初始化插件"""
        print("初始化抖音视频文字提取插件...")
        
        # 创建配置目录
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化集成
        self.integration = DouyinOpenClawIntegration(self.config_path)
        
        return {
            "name": "douyin-asr-workflow",
            "version": "1.0.0",
            "description": "抖音视频文字提取工作流",
            "author": "卡卡西AI助手",
            "handlers": {
                "message": self.handle_message,
                "confirmation": self.handle_confirmation
            }
        }
    
    async def handle_message(self, message_event):
        """处理消息事件"""
        if not self.integration:
            return None
        
        try:
            return await self.integration.handle_message(message_event)
        except Exception as e:
            print(f"处理消息时出错: {e}")
            return None
    
    async def handle_confirmation(self, confirmation_event):
        """处理确认事件"""
        if not self.integration:
            return None
        
        try:
            return await self.integration.handle_confirmation(confirmation_event)
        except Exception as e:
            print(f"处理确认时出错: {e}")
            return None
    
    def get_commands(self):
        """获取插件命令"""
        return {
            "douyin": {
                "description": "处理抖音视频链接",
                "usage": "/douyin <抖音链接> [--verbose] [--output 文件]",
                "handler": self.handle_douyin_command
            },
            "抖音转文字": {
                "description": "提取抖音视频文字",
                "usage": "/抖音转文字 <抖音链接>",
                "handler": self.handle_douyin_command
            }
        }
    
    async def handle_douyin_command(self, command_args, context):
        """处理抖音命令"""
        if not self.integration:
            return "插件未初始化"
        
        message = " ".join(command_args)
        message_data = {
            "text": message,
            "user_id": context.get("user_id", ""),
            "chat_id": context.get("chat_id", "")
        }
        
        result = await self.integration.handle_message(message_data)
        
        if result:
            return result.get("text", "命令处理完成")
        else:
            return "未检测到有效的抖音链接"

# 导出插件
plugin = DouyinPlugin()

# 测试函数
async def test_integration():
    """测试集成"""
    print("测试抖音工作流集成...")
    
    # 创建测试消息
    test_messages = [
        "https://v.douyin.com/MnqFZFeXX9w/",
        "帮我提取这个抖音视频的文字：https://v.douyin.com/MnqFZFeXX9w/",
        "抖音视频转文字",
        "这个视频不错：https://v.douyin.com/xxxx/",
        "不要处理这个抖音链接：https://v.douyin.com/yyyy/"
    ]
    
    integration = DouyinOpenClawIntegration()
    
    for msg in test_messages:
        print(f"\n测试消息: {msg}")
        should_process = integration.should_process_message({"text": msg})
        print(f"应该处理: {'✅ 是' if should_process else '❌ 否'}")
        
        if should_process:
            result = await integration.handle_message({"text": msg})
            if result:
                print(f"响应类型: {result.get('type')}")
                print(f"响应内容: {result.get('text', '')[:100]}...")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_integration())