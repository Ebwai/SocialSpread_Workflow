import json
import os
import time
import subprocess
from pathlib import Path
from playwright.sync_api import Page, Locator

class InteractionManager:
    """
    交互管理器：负责读取原子交互定义、处理交互失败、启动录制并更新原子库。
    """
    
    def __init__(self, storage_path="interaction_atoms.json"):
        self.storage_path = Path(storage_path)
        self.atoms = self._load_atoms()
        
    def _load_atoms(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_atoms(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.atoms, f, indent=4, ensure_ascii=False)
            
    def get_locator_selector(self, interaction_id, default_selector):
        """获取交互的选择器，优先使用原子库中的记录"""
        return self.atoms.get(interaction_id, {}).get("selector", default_selector)

    def update_atom(self, interaction_id, selector, action_type="click"):
        """更新原子库"""
        self.atoms[interaction_id] = {
            "selector": selector,
            "action_type": action_type,
            "updated_at": time.time()
        }
        self._save_atoms()
        print(f"✅ 交互原子已更新: {interaction_id} -> {selector}")

    def perform_interaction(self, page: Page, interaction_id: str, default_selector: str, 
                          action_type="click", precondition=None, **kwargs):
        """
        执行交互动作。
        如果失败，触发重录流程（执行前置链 -> 录制 -> 更新 -> 重试）。
        
        Args:
            page: Playwright Page对象
            interaction_id: 交互ID (e.g. "doubao.summary.upload_btn")
            default_selector: 默认选择器
            action_type: 动作类型 (click, fill, hover, etc.)
            precondition: 失败时执行的前置动作链函数 (callable)
            **kwargs: 传递给动作的参数 (e.g. text for fill)
        """
        # 1. 获取当前选择器
        current_selector = self.get_locator_selector(interaction_id, default_selector)
        
        try:
            # 2. 尝试执行动作
            self._execute_action(page, current_selector, action_type, **kwargs)
            return True
        except Exception as e:
            print(f"❌ 交互失败 [{interaction_id}]: {e}")
            print(f"⚠️  当前选择器: {current_selector}")
            
            # 3. 失败处理逻辑
            if precondition:
                print("🔄 准备启动重录流程...")
                print("⏳ 5秒后开始执行前置动作链并录制新交互...")
                time.sleep(5)
                
                # 3.1 执行前置动作链
                try:
                    print("▶️  执行最小前置链...")
                    precondition(page)
                except Exception as pe:
                    print(f"❌ 前置链执行失败，无法继续重录: {pe}")
                    raise pe
                
                # 3.2 启动录制
                # 录制器启动前，确保页面状态已通过 precondition 准备好
                # 但 codegen 启动的是新窗口，所以需要确保 codegen 加载的状态包含了 precondition 执行后的效果
                # 实际上 precondition 已经在当前 page 执行过了，_launch_recorder 会保存这个状态
                new_selector = self._launch_recorder(page)
                
                if new_selector:
                    # 3.3 更新原子库
                    self.update_atom(interaction_id, new_selector, action_type)
                    
                    # 3.4 重试动作
                    print("🔄 使用新选择器重试...")
                    self._execute_action(page, new_selector, action_type, **kwargs)
                    return True
                else:
                    print("⚠️  未获取到新选择器，重录取消")
                    raise e
            else:
                print("⚠️  无前置动作链定义，无法自动重录")
                raise e

    def _execute_action(self, page: Page, selector: str, action_type: str, **kwargs):
        """执行具体的Playwright动作"""
        # 判断是否为 get_by_* 调用 (e.g. get_by_role("button", name="上传"))
        if selector.startswith("get_by_") or selector.startswith("locator("):
            # 这是一个 Python 代码片段，需要动态执行
            # 这里的 selector 是 page.xxx 的 xxx 部分
            # e.g. selector = 'get_by_role("button", name="上传")'
            try:
                # 动态执行 page 方法获取 locator
                locator = eval(f"page.{selector}", {"page": page})
            except Exception as e:
                print(f"⚠️  动态执行选择器失败: {selector}, 错误: {e}")
                raise e
        else:
            # 默认为 CSS/XPath 字符串
            locator = page.locator(selector)
        
        # 显式等待元素可见
        try:
            locator.first.wait_for(state="visible", timeout=5000)
        except:
            pass # 即使不可见也尝试操作，让Playwright报错

        if action_type == "click":
            locator.first.click()
        elif action_type == "fill":
            locator.first.fill(kwargs.get("text", ""))
        elif action_type == "hover":
            locator.first.hover()
        elif action_type == "upload":
            # 对于上传，通常是 set_input_files，但 locator 指向 input
            file_path = kwargs.get("file_path")
            if file_path:
                locator.first.set_input_files(file_path)
        elif action_type == "type":
            locator.first.type(kwargs.get("text", ""))
        elif action_type == "press":
            locator.first.press(kwargs.get("key", "Enter"))
        # 可以扩展更多动作...

    def _launch_recorder(self, page: Page, precondition=None):
        """
        启动录制流程：
        1. 保存当前状态 (Storage State)
        2. 启动 playwright codegen
        3. 解析输出获取 Locator
        """
        print("🎥 启动交互录制器...")
        print("👉 请在弹出的浏览器中操作目标元素（点击/输入等），然后关闭浏览器窗口")
        
        # 临时文件路径
        temp_state = "temp_auth.json"
        temp_script = "temp_recorded.py"
        
        # 保存当前页面状态（Cookies, LocalStorage）
        try:
            page.context.storage_state(path=temp_state)
        except Exception as e:
            print(f"⚠️  保存页面状态失败: {e}")
            
        # 构造 codegen 命令
        # 注意：我们需要让 codegen 加载这个状态，并且打开当前 URL
        current_url = page.url
        # 使用 subprocess.list2cmdline 处理参数转义
        cmd = [
            "playwright", "codegen",
            "--load-storage", temp_state,
            "--output", temp_script,
            "--target", "python",
            current_url
        ]
        
        try:
            # 阻塞运行 codegen，直到用户关闭窗口
            subprocess.run(cmd, check=True, shell=True)
            
            # 解析生成的脚本提取 Locator
            return self._extract_locator_from_script(temp_script)
        except Exception as e:
            print(f"❌ 录制过程出错: {e}")
            return None
        finally:
            # 清理临时文件
            if os.path.exists(temp_state):
                os.remove(temp_state)
            if os.path.exists(temp_script):
                os.remove(temp_script)

    def _extract_locator_from_script(self, script_path):
        """
        从 codegen 生成的 python 脚本中提取最后一行有效的 locator 操作
        支持 page.locator(...) 和 page.get_by_...(...)
        """
        if not os.path.exists(script_path):
            return None
            
        last_selector = None
        
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        import re
        # 匹配 page.xxx(...).action(...) 形式
        # 捕获 xxx(...) 部分，排除 page. 和 .action(...)
        # 示例: page.get_by_role("button", name="上传").click() -> get_by_role("button", name="上传")
        # 示例: page.locator("div > span").click() -> locator("div > span")
        
        # 简单策略：匹配行中 page. 开头，包含 click/fill/press/check/uncheck/select_option/set_input_files 等动作
        actions = ["click", "fill", "press", "check", "uncheck", "select_option", "hover", "type", "set_input_files"]
        action_pattern = "|".join(actions)
        
        # 正则：page\.(.+?)\.(?:action_pattern)
        # 非贪婪匹配中间部分
        pattern = re.compile(r'page\.(.+?)\.(?:' + action_pattern + r')')
        
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("page."):
                match = pattern.search(line)
                if match:
                    last_selector = match.group(1)
                    # 还需要验证括号是否匹配（简单检查）
                    if last_selector.count('(') == last_selector.count(')'):
                        break
            
        if last_selector:
            print(f"🎯 解析到新选择器: {last_selector}")
            return last_selector
        else:
            print("⚠️  未能从录制脚本中解析出有效的操作")
            return None
