import pytest
import os
import shutil
import glob
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_screen_viewport(default_width=1920, default_height=1080):
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        if width and height:
            print(f"🖥️ 检测到屏幕分辨率: {width}x{height}")
            return {"width": int(width), "height": int(height)}
    except Exception as e:
        print(f"⚠️ 获取屏幕分辨率失败: {e}")
    print(f"🖥️ 使用默认视口分辨率: {default_width}x{default_height}")
    return {"width": default_width, "height": default_height}

def get_screen_size():
    viewport = get_screen_viewport()
    return viewport["width"], viewport["height"]

def pytest_addoption(parser):
    parser.addoption("--title", type=str, 
                     help='文章标题（必填）')
    parser.addoption("--author", type=str, default='tornadoami', help='作者名称')
    parser.addoption("--summary", type=str, 
                     help='文章摘要（可选，如不指定则使用豆包AI自动生成）')
    parser.addoption("--url", type=str, 
                     help='原文链接（必填）')
    parser.addoption("--markdown-file", type=str, 
                     help='Markdown文件路径（必填）')
    parser.addoption("--user-data-dir", type=str, 
                     default='D:/tornadofiles/scripts_脚本/github_projects/playwright-automation/chromium-browser-data',
                     help='浏览器用户数据目录')
    parser.addoption("--platforms", type=str, 
                     default='all',
                     help='指定要发布到的平台，用逗号分隔，如：wechat,zhihu,csdn,51cto,cnblogs 或 all 表示所有平台')
    parser.addoption("--cover-image", type=str, 
                     help='文章封面图片路径（可选，如不指定则使用Gemini自动生成）')
    # 新增话题标签参数
    parser.addoption("--tags", type=str, 
                     default='AI,人工智能,大模型,LLM,机器学习,深度学习,开源,技术分享,自动化,agent',
                     help='话题标签，用逗号分隔，如：AI,人工智能,大模型,LLM')
    # 新增浏览器数据备份控制参数
    parser.addoption("--backup-browser-data", type=str, 
                     default='true',
                     help='是否备份浏览器数据，可选值：true/false，默认为true')
    # 新增短标题参数
    parser.addoption("--short-title", type=str, 
                     help='短标题（可选，用于图文平台，如不指定则自动生成）')
    parser.addoption("--rewrite-platform-content", type=str,
                     default='false',
                     help='是否按平台风格改写正文，可选值：true/false，默认为false')
    parser.addoption("--rewrite-special-prompt", type=str,
                     help='正文改写特殊提示词（可选）')
    parser.addoption("--image-special-prompt", type=str,
                     help='封面图生成特殊提示词（可选）')

def cleanup_old_backups(max_backups=3):
    """清理旧的备份目录，只保留最近的指定数量的备份"""
    backup_pattern = "chromium-browser-data_backup_*"
    backup_dirs = glob.glob(backup_pattern)
    
    if len(backup_dirs) <= max_backups:
        print(f"📁 当前备份数量: {len(backup_dirs)}，无需清理")
        return
    
    # 按修改时间排序，最新的在前面
    backup_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 删除超出数量限制的旧备份
    dirs_to_delete = backup_dirs[max_backups:]
    
    for backup_dir in dirs_to_delete:
        try:
            shutil.rmtree(backup_dir)
            print(f"🗑️  已删除旧备份: {backup_dir}")
        except Exception as e:
            print(f"❌ 删除备份失败 {backup_dir}: {e}")
    
    print(f"✅ 备份清理完成，保留最近 {max_backups} 个备份")

def backup_browser_data():
    """备份chromium-browser-data目录"""
    source_dir = "chromium-browser-data"
    if os.path.exists(source_dir):
        # 先清理旧备份
        cleanup_old_backups(max_backups=3)
        
        # 创建带时间戳的备份目录名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"chromium-browser-data_backup_{timestamp}"
        
        try:
            # 复制目录
            shutil.copytree(source_dir, backup_dir)
            print(f"✅ 浏览器数据目录备份成功: {backup_dir}")
            
            # 备份完成后再次清理，确保不超过限制
            cleanup_old_backups(max_backups=3)
            
            return backup_dir
        except Exception as e:
            print(f"❌ 浏览器数据目录备份失败: {e}")
            return None
    else:
        print("⚠️  chromium-browser-data 目录不存在，跳过备份")
        return None

@pytest.fixture(scope="session", autouse=True)
def backup_browser_data_fixture(request):
    """自动执行的备份fixture"""
    # 获取备份控制参数
    backup_enabled = request.config.getoption("--backup-browser-data").lower() in ['true', '1', 'yes', 'on']
    
    if backup_enabled:
        print("🔄 开始备份浏览器数据目录...")
        backup_path = backup_browser_data()
        yield backup_path
        print(f"📦 浏览器数据备份完成: {backup_path}")
    else:
        print("⏭️  跳过浏览器数据备份（用户设置 --backup-browser-data=false）")
        yield None

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    screen_width, screen_height = get_screen_size()
    return {
        "geolocation": {"latitude": 22.558033372050147, "longitude": 113.46251764183725}, 
        "locale": "zh-CN", 
        "permissions": ["geolocation"], 
        "timezone_id": "Asia/Shanghai", 
        "viewport": None,
        "screen": {"width": screen_width, "height": screen_height}
    }
