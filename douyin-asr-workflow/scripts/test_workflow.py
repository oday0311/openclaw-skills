#!/usr/bin/env python3
"""
抖音视频文字提取工作流测试脚本
用于测试工作流的各个组件
"""

import os
import sys
import subprocess
import tempfile

def test_dependencies():
    """测试依赖是否安装"""
    print("测试依赖安装状态...")
    
    dependencies = {
        "python3": "Python 3解释器",
        "pip3": "Python包管理器",
        "ffmpeg": "音频/视频处理工具",
        "yt-dlp": "视频下载工具",
        "whisper": "语音识别工具",
        "mcporter": "agent-reach命令行工具"
    }
    
    all_ok = True
    for cmd, desc in dependencies.items():
        try:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {desc} ({cmd}) - 已安装")
            else:
                print(f"❌ {desc} ({cmd}) - 未安装")
                all_ok = False
        except Exception as e:
            print(f"❌ {desc} ({cmd}) - 检查失败: {str(e)}")
            all_ok = False
    
    return all_ok

def test_whisper():
    """测试Whisper是否正常工作"""
    print("\n测试Whisper...")
    
    # 创建一个测试音频文件（静音1秒）
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        test_audio = f.name
    
    try:
        # 使用ffmpeg创建1秒的静音WAV文件
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "anullsrc=r=16000:cl=mono",
            "-t", "1",
            "-acodec", "pcm_s16le",
            test_audio,
            "-y"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 创建测试音频失败: {result.stderr}")
            return False
        
        # 测试Whisper
        print("测试Whisper识别（静音音频，应该返回空结果）...")
        whisper_cmd = [
            "whisper",
            test_audio,
            "--model", "base",  # 使用base模型测试
            "--output_format", "txt",
            "--fp16", "False"
        ]
        
        result = subprocess.run(
            whisper_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Whisper测试通过")
            return True
        else:
            print(f"❌ Whisper测试失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Whisper测试超时")
        return False
    except Exception as e:
        print(f"❌ Whisper测试异常: {str(e)}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_audio):
            os.remove(test_audio)

def test_ffmpeg():
    """测试ffmpeg是否正常工作"""
    print("\n测试ffmpeg...")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 提取版本信息
            lines = result.stdout.split('\n')
            if lines:
                version_line = lines[0]
                print(f"✅ ffmpeg测试通过 - {version_line}")
            return True
        else:
            print(f"❌ ffmpeg测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ffmpeg测试异常: {str(e)}")
        return False

def test_yt_dlp():
    """测试yt-dlp是否正常工作"""
    print("\n测试yt-dlp...")
    
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ yt-dlp测试通过 - 版本: {version}")
            return True
        else:
            print(f"❌ yt-dlp测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ yt-dlp测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("抖音视频文字提取工作流 - 依赖测试")
    print("=" * 60)
    
    # 测试所有依赖
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ 部分依赖未安装，请先安装缺失的依赖")
        print("运行以下命令安装依赖:")
        print("  ./scripts/install_dependencies.sh")
        sys.exit(1)
    
    # 测试各个组件
    tests = [
        ("ffmpeg", test_ffmpeg),
        ("yt-dlp", test_yt_dlp),
        ("whisper", test_whisper)
    ]
    
    all_tests_passed = True
    for name, test_func in tests:
        if not test_func():
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ 所有测试通过！工作流可以正常运行。")
        print("\n使用示例:")
        print("  python3 douyin_asr_workflow.py \"https://v.douyin.com/xxxxxxx/\" --verbose")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()