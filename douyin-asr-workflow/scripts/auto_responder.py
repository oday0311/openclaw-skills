#!/usr/bin/env python3
"""
抖音视频文字提取工作流 - 自动响应器
集成到OpenClaw，自动检测并处理抖音链接
"""

import os
import re
import sys
import json
import asyncio
import subprocess
from typing import Optional, Dict, List
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("douyin_auto_responder")

class DouyinAutoResponder:
    """抖音自动响应器"""
    
    def __init__(self):
        self.workflow_script = os.path.join(
            os.path.dirname(__file__),
            "douyin_asr_workflow.py"
        )
        
        # 抖音链接模式
        self.douyin_patterns = [
            r'https://v\.douyin\.com/[^\s<>"\']+',
            r'https://www\.douyin\.com/video/[^\s<>"\']+',
            r'https://www\.iesdouyin\.com/share/video/[^\s<>"\']+'
        ]
        
        # 触发关键词
        self.trigger_keywords = [
            "抖音视频转文字",
            "提取抖音文字",
            "抖音字幕",
            "抖音内容转文字",
            "douyin转文字",
            "抖音转录"
        ]
        
        # 排除关键词（当用户明确表示不要处理时）
        self.exclude_keywords = [
            "不要处理",
            "跳过",
            "不用",
            "别处理"
        ]
    
    def should_respond(self, message: str) -> bool:
        """检查是否应该响应此消息"""
        message_lower = message.lower()
        
        # 检查排除关键词
        for keyword in self.exclude_keywords:
            if keyword in message_lower:
                logger.info(f"消息包含排除关键词: {keyword}")
                return False
        
        # 检查抖音链接
        for pattern in self.douyin_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.info(f"检测到抖音链接模式: {pattern}")
                return True
        
        # 检查触发关键词
        for keyword in self.trigger_keywords:
            if keyword in message_lower:
                logger.info(f"检测到触发关键词: {keyword}")
                return True
        
        return False
    
    def extract_douyin_url(self, message: str) -> Optional[str]:
        """从消息中提取抖音链接"""
        for pattern in self.douyin_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                url = match.group(0)
                # 清理URL（移除可能的标点符号）
                url = url.strip('.,;:!?\'"()[]{}<>')
                logger.info(f"提取到抖音链接: {url}")
                return url
        
        return None
    
    def extract_command_args(self, message: str) -> Dict:
        """从消息中提取命令参数"""
        args = {
            "url": None,
            "verbose": False,
            "output": None
        }
        
        # 提取URL
        args["url"] = self.extract_douyin_url(message)
        
        # 检查详细模式
        if "详细" in message or "verbose" in message.lower():
            args["verbose"] = True
        
        # 检查输出文件
        output_match = re.search(r'输出[到\s]+([^\s]+)', message)
        if output_match:
            args["output"] = output_match.group(1)
        
        return args
    
    async def process_message(self, message: str) -> Dict:
        """处理消息并返回响应"""
        logger.info(f"处理消息: {message[:100]}...")
        
        if not self.should_respond(message):
            return {
                "should_respond": False,
                "reason": "不匹配触发条件"
            }
        
        # 提取参数
        args = self.extract_command_args(message)
        
        if not args["url"]:
            return {
                "should_respond": True,
                "response": "检测到抖音相关请求，但未找到有效的抖音链接。请提供抖音视频分享链接。",
                "action": "ask_for_url"
            }
        
        # 启动工作流
        return await self.start_workflow(args)
    
    async def start_workflow(self, args: Dict) -> Dict:
        """启动工作流处理"""
        url = args["url"]
        
        logger.info(f"启动工作流处理: {url}")
        
        # 构建命令
        cmd = [sys.executable, self.workflow_script, url]
        
        if args.get("verbose"):
            cmd.append("--verbose")
        
        if args.get("output"):
            cmd.extend(["--output", args["output"]])
        
        try:
            # 执行工作流
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 发送初始响应
            initial_response = {
                "should_respond": True,
                "response": f"检测到抖音链接，正在启动文字提取工作流...\n链接: {url}",
                "action": "workflow_started",
                "workflow": {
                    "url": url,
                    "status": "processing",
                    "pid": process.pid
                }
            }
            
            # 等待处理完成
            stdout, stderr = await process.wait()
            
            if process.returncode == 0:
                # 读取输出文件或使用stdout
                output_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
                
                # 提取关键信息
                result = self.parse_workflow_output(output_text)
                
                return {
                    "should_respond": True,
                    "response": self.format_success_response(result),
                    "action": "workflow_completed",
                    "workflow": {
                        "url": url,
                        "status": "completed",
                        "result": result
                    }
                }
            else:
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "未知错误"
                logger.error(f"工作流失败: {error_msg}")
                
                return {
                    "should_respond": True,
                    "response": f"抖音视频处理失败:\n错误: {error_msg[:200]}",
                    "action": "workflow_failed",
                    "workflow": {
                        "url": url,
                        "status": "failed",
                        "error": error_msg
                    }
                }
                
        except Exception as e:
            logger.error(f"工作流异常: {str(e)}")
            return {
                "should_respond": True,
                "response": f"处理抖音视频时发生异常: {str(e)}",
                "action": "workflow_error",
                "workflow": {
                    "url": url,
                    "status": "error",
                    "error": str(e)
                }
            }
    
    def parse_workflow_output(self, output: str) -> Dict:
        """解析工作流输出"""
        result = {
            "transcription": "",
            "video_info": {},
            "duration": 0,
            "char_count": 0,
            "word_count": 0
        }
        
        # 尝试提取转录文字
        # 查找转录结果部分
        transcription_match = re.search(
            r'文字转录结果\s*```\s*(.*?)\s*```',
            output,
            re.DOTALL
        )
        
        if transcription_match:
            result["transcription"] = transcription_match.group(1).strip()
            result["char_count"] = len(result["transcription"])
            result["word_count"] = len(result["transcription"].split())
        
        # 提取视频信息
        title_match = re.search(r'标题[:：]\s*(.+)', output)
        if title_match:
            result["video_info"]["title"] = title_match.group(1).strip()
        
        author_match = re.search(r'作者[:：]\s*(.+)', output)
        if author_match:
            result["video_info"]["author"] = author_match.group(1).strip()
        
        duration_match = re.search(r'总耗时[:：]\s*([\d.]+)\s*秒', output)
        if duration_match:
            result["duration"] = float(duration_match.group(1))
        
        return result
    
    def format_success_response(self, result: Dict) -> str:
        """格式化成功响应"""
        response = "✅ 抖音视频文字提取完成！\n\n"
        
        if result.get("video_info", {}).get("title"):
            response += f"📺 **视频标题**: {result['video_info']['title']}\n"
        
        if result.get("video_info", {}).get("author"):
            response += f"👤 **视频作者**: {result['video_info']['author']}\n"
        
        if result.get("duration"):
            response += f"⏱️ **处理耗时**: {result['duration']:.2f}秒\n"
        
        response += f"📝 **文字长度**: {result.get('char_count', 0)} 字符, {result.get('word_count', 0)} 词\n\n"
        
        transcription = result.get("transcription", "")
        if transcription:
            # 截断长文本
            if len(transcription) > 1000:
                response += "**文字内容（前1000字符）**:\n"
                response += transcription[:1000] + "...\n"
                response += f"\n（完整内容共 {len(transcription)} 字符）"
            else:
                response += "**文字内容**:\n"
                response += transcription
        
        return response
    
    def format_quick_response(self, url: str) -> str:
        """格式化快速响应（用于立即反馈）"""
        return f"🎬 检测到抖音链接，正在处理...\n链接: {url}\n\n请稍候，文字提取工作流已启动。"

# 命令行接口
async def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="抖音自动响应器测试")
    parser.add_argument("message", help="用户消息")
    parser.add_argument("--test", action="store_true", help="测试模式")
    
    args = parser.parse_args()
    
    responder = DouyinAutoResponder()
    
    if args.test:
        # 测试模式
        print("测试消息:", args.message)
        print("应该响应:", responder.should_respond(args.message))
        print("提取链接:", responder.extract_douyin_url(args.message))
        print("命令参数:", responder.extract_command_args(args.message))
    else:
        # 处理消息
        result = await responder.process_message(args.message)
        
        print("处理结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())