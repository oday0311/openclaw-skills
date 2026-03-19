#!/usr/bin/env python3
"""
抖音视频文字提取工作流
从抖音视频分享链接到文字内容的完整处理流程
"""

import os
import sys
import json
import subprocess
import tempfile
import time
import re
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import argparse

class DouyinASRWorkflow:
    """抖音视频文字提取工作流"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.temp_dir = tempfile.gettempdir()
        self.results = {
            "input_url": "",
            "video_info": {},
            "audio_path": "",
            "transcription": "",
            "steps": [],
            "errors": [],
            "start_time": None,
            "end_time": None
        }
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        
        if self.verbose:
            print(log_msg)
        
        self.results["steps"].append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
    
    def validate_douyin_url(self, url: str) -> bool:
        """验证抖音分享链接格式"""
        patterns = [
            r'^https://v\.douyin\.com/',
            r'^https://www\.douyin\.com/video/',
            r'^https://www\.iesdouyin\.com/share/video/'
        ]
        
        for pattern in patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def get_video_info(self, share_link: str) -> Optional[Dict]:
        """使用agent-reach获取抖音视频信息"""
        self.log(f"获取抖音视频信息: {share_link}")
        
        try:
            # 使用mcporter调用douyin工具
            cmd = [
                "mcporter", "call",
                f'douyin.parse_douyin_video_info(share_link: "{share_link}")'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log(f"获取视频信息失败: {result.stderr}", "ERROR")
                return None
            
            # 解析JSON输出
            try:
                video_info = json.loads(result.stdout)
                self.log(f"视频信息获取成功: {video_info.get('title', '未知标题')}")
                return video_info
            except json.JSONDecodeError:
                self.log(f"JSON解析失败: {result.stdout}", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("获取视频信息超时", "ERROR")
            return None
        except Exception as e:
            self.log(f"获取视频信息异常: {str(e)}", "ERROR")
            return None
    
    def download_video(self, video_url: str, video_id: str) -> Optional[str]:
        """下载抖音视频"""
        self.log(f"下载视频: {video_url}")
        
        output_template = f"{self.temp_dir}/douyin_{video_id}.%(ext)s"
        
        try:
            # 使用yt-dlp下载视频（选择720p或以下以节省带宽）
            cmd = [
                "yt-dlp",
                "-f", "best[height<=720]",
                "-o", output_template,
                video_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                self.log(f"视频下载失败: {result.stderr}", "ERROR")
                return None
            
            # 查找下载的文件
            video_path = None
            for ext in ["mp4", "flv", "webm", "mkv"]:
                test_path = f"{self.temp_dir}/douyin_{video_id}.{ext}"
                if os.path.exists(test_path):
                    video_path = test_path
                    break
            
            if video_path:
                self.log(f"视频下载完成: {video_path}")
                return video_path
            else:
                self.log("无法找到下载的视频文件", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("视频下载超时", "ERROR")
            return None
        except Exception as e:
            self.log(f"视频下载异常: {str(e)}", "ERROR")
            return None
    
    def extract_audio(self, video_path: str, video_id: str) -> Optional[str]:
        """从视频中提取音频"""
        self.log(f"从视频提取音频: {video_path}")
        
        audio_path = f"{self.temp_dir}/douyin_{video_id}.wav"
        
        try:
            # 使用ffmpeg提取音频并转换为ASR友好的格式
            # 16kHz采样率，单声道，PCM 16位
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # 禁用视频流
                "-acodec", "pcm_s16le",
                "-ar", "16000",  # 16kHz采样率
                "-ac", "1",  # 单声道
                "-y",  # 覆盖输出文件
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180  # 3分钟超时
            )
            
            if result.returncode != 0:
                self.log(f"音频提取失败: {result.stderr}", "ERROR")
                return None
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                self.log(f"音频提取完成: {audio_path} ({os.path.getsize(audio_path)} bytes)")
                return audio_path
            else:
                self.log("音频文件创建失败", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("音频提取超时", "ERROR")
            return None
        except Exception as e:
            self.log(f"音频提取异常: {str(e)}", "ERROR")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """使用本地Whisper转写音频"""
        self.log(f"开始语音转文字: {audio_path}")
        
        try:
            # 检查whisper命令是否可用
            if not shutil.which("whisper"):
                self.log("whisper命令未找到，请安装openai-whisper技能", "ERROR")
                return None
            
            # 准备输出文件路径
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            output_dir = self.temp_dir
            output_txt = os.path.join(output_dir, f"{base_name}.txt")
            
            # 使用whisper进行识别
            # 使用base模型节省磁盘空间，平衡速度和准确度
            # 输出格式为txt，语言自动检测
            whisper_cmd = [
                "whisper",
                audio_path,
                "--model", "base",
                "--output_format", "txt",
                "--output_dir", output_dir,
                "--fp16", "False"  # 避免FP16精度问题
            ]
            
            self.log("正在调用本地Whisper进行识别...")
            self.log(f"命令: {' '.join(whisper_cmd)}")
            
            transcribe_result = subprocess.run(
                whisper_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时，Whisper可能较慢
            )
            
            if transcribe_result.returncode != 0:
                self.log(f"Whisper识别失败: {transcribe_result.stderr}", "ERROR")
                return None
            
            # 检查输出文件
            if os.path.exists(output_txt):
                with open(output_txt, 'r', encoding='utf-8') as f:
                    transcription = f.read().strip()
                
                if transcription:
                    self.log(f"Whisper识别完成，文字长度: {len(transcription)} 字符")
                    
                    # 清理Whisper生成的其他文件
                    for ext in ['.txt', '.vtt', '.srt', '.json']:
                        other_file = os.path.join(output_dir, f"{base_name}{ext}")
                        if os.path.exists(other_file) and other_file != output_txt:
                            try:
                                os.remove(other_file)
                                self.log(f"清理临时文件: {other_file}")
                            except:
                                pass
                    
                    return transcription
                else:
                    self.log("Whisper识别返回空结果", "WARNING")
                    return ""
            else:
                self.log(f"Whisper输出文件未找到: {output_txt}", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("Whisper识别超时", "ERROR")
            return None
        except Exception as e:
            self.log(f"Whisper识别异常: {str(e)}", "ERROR")
            return None
    
    def cleanup(self, video_path: Optional[str], audio_path: Optional[str]):
        """清理临时文件"""
        files_to_clean = []
        if video_path and os.path.exists(video_path):
            files_to_clean.append(video_path)
        if audio_path and os.path.exists(audio_path):
            files_to_clean.append(audio_path)
        
        for file_path in files_to_clean:
            try:
                os.remove(file_path)
                self.log(f"清理临时文件: {file_path}")
            except Exception as e:
                self.log(f"清理文件失败 {file_path}: {str(e)}", "WARNING")
    
    def run(self, douyin_url: str) -> Dict:
        """执行完整工作流"""
        self.results["start_time"] = time.time()
        self.results["input_url"] = douyin_url
        
        self.log("=" * 60)
        self.log("开始抖音视频文字提取工作流")
        self.log("=" * 60)
        
        # 步骤1: 验证链接
        self.log("步骤1: 验证抖音分享链接")
        if not self.validate_douyin_url(douyin_url):
            error_msg = f"无效的抖音分享链接: {douyin_url}"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            return self.results
        
        self.log("链接验证通过")
        
        # 步骤2: 获取视频信息
        self.log("\n步骤2: 获取抖音视频信息")
        video_info = self.get_video_info(douyin_url)
        if not video_info:
            error_msg = "无法获取视频信息"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            return self.results
        
        self.results["video_info"] = video_info
        
        # 提取视频ID和URL
        video_id = video_info.get("video_id", "unknown")
        video_url = video_info.get("video_url")
        
        if not video_url:
            error_msg = "视频信息中缺少视频URL"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            return self.results
        
        # 步骤3: 下载视频
        self.log("\n步骤3: 下载抖音视频")
        video_path = self.download_video(video_url, video_id)
        if not video_path:
            error_msg = "视频下载失败"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            return self.results
        
        # 步骤4: 提取音频
        self.log("\n步骤4: 从视频提取音频")
        audio_path = self.extract_audio(video_path, video_id)
        if not audio_path:
            error_msg = "音频提取失败"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            self.cleanup(video_path, None)
            return self.results
        
        self.results["audio_path"] = audio_path
        
        # 步骤5: 语音转文字
        self.log("\n步骤5: 语音转文字")
        transcription = self.transcribe_audio(audio_path)
        if transcription is None:  # None表示失败，空字符串表示成功但无内容
            error_msg = "语音转文字失败"
            self.log(error_msg, "ERROR")
            self.results["errors"].append(error_msg)
            self.cleanup(video_path, audio_path)
            return self.results
        
        self.results["transcription"] = transcription
        
        # 步骤6: 清理临时文件
        self.log("\n步骤6: 清理临时文件")
        self.cleanup(video_path, audio_path)
        
        # 完成
        self.results["end_time"] = time.time()
        duration = self.results["end_time"] - self.results["start_time"]
        
        self.log("=" * 60)
        self.log(f"工作流完成！总耗时: {duration:.2f} 秒")
        self.log("=" * 60)
        
        return self.results
    
    def generate_report(self) -> str:
        """生成过程汇报"""
        report = []
        
        # 标题
        report.append("# 抖音视频文字提取工作流报告")
        report.append("")
        
        # 基本信息
        report.append("## 基本信息")
        report.append(f"- **输入链接**: {self.results['input_url']}")
        report.append(f"- **开始时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.results.get('start_time', 0)))}")
        
        if self.results.get('end_time'):
            duration = self.results['end_time'] - self.results['start_time']
            report.append(f"- **总耗时**: {duration:.2f} 秒")
        
        report.append("")
        
        # 视频信息
        if self.results.get('video_info'):
            video_info = self.results['video_info']
            report.append("## 视频信息")
            report.append(f"- **标题**: {video_info.get('title', '未知')}")
            report.append(f"- **作者**: {video_info.get('author', '未知')}")
            report.append(f"- **视频ID**: {video_info.get('video_id', '未知')}")
            report.append(f"- **时长**: {video_info.get('duration', '未知')} 秒")
            report.append("")
        
        # 处理步骤
        report.append("## 处理步骤")
        for step in self.results.get('steps', []):
            level_emoji = {
                "INFO": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌"
            }.get(step['level'], "ℹ️")
            
            report.append(f"{level_emoji} **{step['timestamp']}** [{step['level']}] {step['message']}")
        report.append("")
        
        # 错误信息
        if self.results.get('errors'):
            report.append("## 错误信息")
            for error in self.results['errors']:
                report.append(f"- ❌ {error}")
            report.append("")
        
        # 转录结果
        if self.results.get('transcription') is not None:
            report.append("## 文字转录结果")
            report.append("```")
            report.append(self.results['transcription'])
            report.append("```")
            report.append("")
            
            # 统计信息
            char_count = len(self.results['transcription'])
            word_count = len(self.results['transcription'].split())
            report.append(f"**统计**: {char_count} 字符, {word_count} 词")
        
        return "\n".join(report)

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="抖音视频文字提取工作流")
    parser.add_argument("url", help="抖音视频分享链接")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--output", "-o", help="输出报告文件路径")
    
    args = parser.parse_args()
    
    # 创建工作流实例
    workflow = DouyinASRWorkflow(verbose=args.verbose)
    
    # 执行工作流
    results = workflow.run(args.url)
    
    # 生成报告
    report = workflow.generate_report()
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)
    
    # 返回退出码
    if results.get('errors'):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()