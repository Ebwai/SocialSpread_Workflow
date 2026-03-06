# -*- coding: utf-8 -*-
"""
豆包AI图片生成模块
提供完整的豆包AI图片生成功能，包括提示词生成和图片下载
"""

import os
import time
import sys
import shutil
import subprocess
import pyperclip
from typing import List, Optional, Tuple
from playwright.sync_api import Page, BrowserContext
from interaction_manager import InteractionManager

# 初始化交互管理器
interaction_manager = InteractionManager()

class DoubaoAIImageGenerator:
    """豆包AI图片生成器"""
    
    def __init__(self, page: Page, context: BrowserContext):
        """
        初始化豆包AI图片生成器
        
        Args:
            page: Playwright页面对象
            context: 浏览器上下文对象
        """
        self.page = page
        self.context = context
        self.downloads_dir = os.path.join(os.getcwd(), "test-results", "doubao_images")
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def generate_prompt_from_markdown(self, markdown_file: str, special_prompt: str = None) -> Optional[str]:
        """
        从Markdown文件生成文生图提示词
        
        Args:
            markdown_file: Markdown文件路径
            special_prompt: 特殊提示词（可选）
            
        Returns:
            生成的提示词，失败时返回None
        """
        try:
            print("🤖 开始生成文生图提示词...")
            
            # 上传Markdown文件
            self._upload_markdown_file(markdown_file)
            
            # 发送提示词生成请求
            prompt_text = self._get_prompt_generation_text(special_prompt)
            self._send_prompt_request(prompt_text)
            
            # 获取AI回复的提示词
            prompt_result = self._get_ai_response()
            
            if prompt_result:
                # 保存提示词到文件
                self._save_prompt_to_file(prompt_result, markdown_file)
                print(f"✅ 提示词生成成功: {prompt_result[:100]}...")
                return prompt_result
            else:
                print("❌ 提示词生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 生成提示词时出错: {e}")
            return None

    def generate_prompt_from_summary(self, summary_text: str, special_prompt: str = None) -> Optional[str]:
        """
        从摘要文本生成文生图提示词
        
        Args:
            summary_text: 文章摘要文本
            special_prompt: 特殊提示词（可选）
            
        Returns:
            生成的提示词，失败时返回None
        """
        try:
            print("🤖 开始根据摘要生成文生图提示词...")
            
            # 发送提示词生成请求
            prompt_request = self._get_prompt_generation_text_from_summary(summary_text, special_prompt)
            self._send_prompt_request(prompt_request)
            
            # 获取AI回复的提示词
            prompt_result = self._get_ai_response()
            
            if prompt_result:
                # 保存提示词到文件（这里没有markdown文件路径，暂时使用时间戳命名）
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                self._save_prompt_to_file(prompt_result, f"summary_prompt_{timestamp}.txt")
                print(f"✅ 提示词生成成功: {prompt_result[:100]}...")
                return prompt_result
            else:
                print("❌ 提示词生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 根据摘要生成提示词时出错: {e}")
            return None
    
    def generate_images_with_prompt(self, prompt: str, aspect_ratio: str = "16:9") -> List[str]:
        """
        使用提示词生成图片
        
        Args:
            prompt: 文生图提示词
            aspect_ratio: 图片比例，默认为"16:9"
            
        Returns:
            生成的图片文件路径列表
        """
        try:
            print("🎨 开始生成图片...")
            
            # 选择豆包AI的模式为思考模式
            # self.select_ai_mode("思考")

            # 切换到图片生成技能 (根据用户要求移除)
            # self._switch_to_image_generation_skill()

            # 在聊天输入框中输入提示词，不发送
            self._fill_prompt_only(prompt)
            
            # 发送图片生成请求
            self._send_image_generation_request(prompt)
            
            # 等待图片生成完成
            self._wait_for_image_generation()
            
            # 下载生成的图片
            downloaded_files = self._download_generated_images()
            
            if downloaded_files:
                print(f"✅ 图片生成成功，共下载 {len(downloaded_files)} 张图片")
                return downloaded_files
            else:
                print("❌ 图片生成失败")
                return []
                
        except Exception as e:
            print(f"❌ 生成图片时出错: {e}")
            return []
    
    def generate_images_from_markdown(self, markdown_file: str, aspect_ratio: str = "16:9", special_prompt: str = None) -> Tuple[Optional[str], List[str]]:
        """
        从Markdown文件生成图片（完整流程）
        
        Args:
            markdown_file: Markdown文件路径
            aspect_ratio: 图片比例，默认为"16:9"
            special_prompt: 特殊提示词（可选）
            
        Returns:
            (提示词, 图片文件路径列表)
        """
        try:
            print("🚀 开始完整的图片生成流程（基于Markdown文件）...")
            
            # 强制跳转到豆包聊天页面，确保环境纯净
            print("🔄 跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass
            
            # 步骤1：生成提示词
            # 不再选择思考模式，直接使用默认对话
            prompt = self.generate_prompt_from_markdown(markdown_file, special_prompt)
            if not prompt:
                return None, []
            
            # 不需要退出提示词生成界面，因为没有进入特殊模式
            # self._exit_prompt_generation_view()

            # 步骤2：生成图片
            image_files = self.generate_images_with_prompt(prompt, aspect_ratio)
            
            return prompt, image_files
            
        except Exception as e:
            print(f"❌ 完整流程执行失败: {e}")
            return None, []
    
    def generate_images_from_summary(self, summary_text: str, aspect_ratio: str = "16:9", special_prompt: str = None) -> Tuple[Optional[str], List[str]]:
        """
        从摘要文本生成图片（完整流程）
        
        Args:
            summary_text: 文章摘要
            aspect_ratio: 图片比例，默认为"16:9"
            special_prompt: 特殊提示词（可选）
            
        Returns:
            (提示词, 图片文件路径列表)
        """
        try:
            print("🚀 开始完整的图片生成流程（基于摘要）...")
            
            # 强制跳转到豆包聊天页面，确保环境纯净
            print("🔄 跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

            # 步骤1：生成提示词
            # 不再选择思考模式，直接使用默认对话
            prompt = self.generate_prompt_from_summary(summary_text, special_prompt)
            if not prompt:
                return None, []
            
            # 不需要退出提示词生成界面，因为没有进入特殊模式
            # self._exit_prompt_generation_view()

            # 步骤2：生成图片
            image_files = self.generate_images_with_prompt(prompt, aspect_ratio)
            
            return prompt, image_files
            
        except Exception as e:
            print(f"❌ 完整流程执行失败: {e}")
            return None, []

    def _upload_markdown_file(self, markdown_file: str) -> None:
        """上传Markdown文件"""
        print("📤 上传Markdown文件 (Managed)...")
        self._paste_file_to_chat_input(markdown_file)
        print("✅ Markdown文件上传成功")

    def _copy_file_to_clipboard(self, file_path: str) -> bool:
        if not file_path:
            print("⚠️ 未提供文件路径，跳过复制到剪贴板")
            return False
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
        if not sys.platform.startswith("win"):
            print("⚠️ 当前系统非Windows，跳过复制到剪贴板")
            return False
        shell_path = shutil.which("pwsh") or shutil.which("powershell")
        if not shell_path:
            print("❌ 未找到PowerShell，无法复制文件到剪贴板")
            return False
        safe_path = file_path.replace("'", "''")
        ps_command = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$files=New-Object System.Collections.Specialized.StringCollection; "
            f"$files.Add('{safe_path}'); "
            "[System.Windows.Forms.Clipboard]::SetFileDropList($files)"
        )
        result = subprocess.run(
            [shell_path, "-NoProfile", "-STA", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            error_output = (result.stderr or result.stdout or "").strip()
            print(f"❌ 复制文件到剪贴板失败: {error_output}")
            return False
        print("✅ 已复制文件到剪贴板")
        return True

    def _paste_file_to_chat_input(self, file_path: str) -> None:
        print("📋 复制本地文件并粘贴上传...")
        if not self._copy_file_to_clipboard(file_path):
            raise Exception("复制文件到剪贴板失败")
        def pre_click(page):
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                print("🔄 前置动作: 跳转到豆包聊天页面(强制重置)...")
                page.goto("https://www.doubao.com/chat/")
                try:
                    page.wait_for_load_state("networkidle")
                except:
                    pass
        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.chat.input_box_paste",
                default_selector="div[data-testid='chat_input_input'] div[contenteditable='true']",
                action_type="click",
                precondition=pre_click
            )
        except Exception:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.chat.input_box_paste_container",
                default_selector="div[data-testid='chat_input_input']",
                action_type="click",
                precondition=pre_click
            )
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("Control+V")
        self.page.wait_for_timeout(2000)
        print("✅ 文件已粘贴到输入框")

    def _click_upload_button(self) -> bool:
        # 强制检查页面状态，不依赖 InteractionManager
        if "doubao.com/chat" not in self.page.url or "create-image" in self.page.url:
            print("🔄 [强制检查] 检测到页面状态不正确，跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

        print("2️⃣ 点击文件上传按钮 (Managed)...")
        default_selector = "button[data-dbx-name='button']:has(svg path[d^='M17.3977'])"
        
        def precondition(page):
            # 严格检查：必须包含 doubao.com/chat 且 不能是 create-image
            # 因为 create-image 页面也有 doubao.com/chat 前缀，但 DOM 结构完全不同
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                print("🔄 前置动作: 跳转到豆包聊天页面(强制重置)...")
                page.goto("https://www.doubao.com/chat/")
                try:
                    page.wait_for_load_state("networkidle")
                except:
                    pass

        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.chat.upload_button",
                default_selector=default_selector,
                action_type="click",
                precondition=precondition
            )
            self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"❌ 上传按钮交互失败: {e}")
            return False

    def _select_upload_file_option(self):
        # 强制检查页面状态，不依赖 InteractionManager
        if "doubao.com/chat" not in self.page.url or "create-image" in self.page.url:
            print("🔄 [强制检查] 检测到页面状态不正确，跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

        print("3️⃣ 选择上传文件选项 (Managed)...")
        default_selector = "div[data-testid='upload_file_panel_upload_item']"
        
        def precondition(page):
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                print("🔄 前置动作: 跳转到豆包聊天页面(强制重置)...")
                page.goto("https://www.doubao.com/chat/")
            print("🔄 前置动作: 重新点击上传按钮...")
            self._click_upload_button()
            try:
                page.wait_for_selector(default_selector, timeout=5000)
            except:
                pass

        with self.page.expect_file_chooser() as page_upload_file:
            try:
                interaction_manager.perform_interaction(
                    self.page,
                    interaction_id="doubao.chat.upload_file_option",
                    default_selector=default_selector,
                    action_type="click",
                    precondition=precondition
                )
            except Exception as e:
                raise e
        return page_upload_file.value
    
    def _get_prompt_generation_text(self, special_prompt: str = None) -> str:
        """获取提示词生成请求文本"""
        base_prompt = """You are an expert in text-to-image prompt engineering.

I will provide you with a Markdown file as an input attachment.
This file contains an article written for publication on a WeChat Official Account.

Your task:
1. Read and analyze the Markdown file to understand the article’s content, theme, and **its filename** (prioritize identifying the filename).
2. Completely ignore any code blocks, command-line examples, or technical syntax within the file.
3. Summarize the main subject and mood of the article.
4. Generate **one single high-quality English prompt** for a text-to-image model (such as Doubao).
5. The image must be suitable as a **WeChat article cover**:
   - Aspect ratio: 16:9
   - Style: professional, clean, visually appealing
   - Subject should be clear and aligned with the article’s theme
   - the image must not include any other text, code snippets, logos, or watermarks"""

        if special_prompt:
            base_prompt += f"\n6. **Special Requirement**: {special_prompt}"
            base_prompt += "\n7. 输出一个符合要求的提示词。不要包含任何解释。 "
        else:
            base_prompt += "\n6. 输出一个符合要求的提示词。不要包含任何解释。 "
            
        return base_prompt

    def _get_prompt_generation_text_from_summary(self, summary_text: str, special_prompt: str = None) -> str:
        """获取基于摘要的提示词生成请求文本"""
        base_prompt = f"""你是一个专业的文本到图像提示词工程师。

我将提供你一个文章的摘要。

你的任务是根据摘要生成一段符合要求的提示词。

摘要:
{summary_text}
"""

        if special_prompt:
            base_prompt += f"\n4. **Special Requirement**: {special_prompt}"
            base_prompt += "\n5. Output only the final prompt in English. Do not include explanations. "
        else:
            base_prompt += "\n4. Output only the final prompt in English. Do not include explanations. "
            
        return base_prompt


    def _fill_chat_input(self, text: str, step_label: str) -> None:
        # 强制检查页面状态，不依赖 InteractionManager
        if "doubao.com/chat" not in self.page.url or "create-image" in self.page.url:
            print("🔄 [强制检查] 检测到页面状态不正确，跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

        print(f"✍️  准备输入: {step_label} (Managed)...")
        # 更新选择器以更精准地定位可编辑区域
        # 以前是 "div[data-testid='chat_input_input']"
        # 尝试定位 contenteditable 元素
        default_selector = "div[data-testid='chat_input_input'] div[contenteditable='true']"
        
        def get_visible_editor():
            editor = self.page.locator(default_selector)
            for i in range(editor.count()):
                el = editor.nth(i)
                try:
                    if el.is_visible():
                        return el
                except:
                    pass
            return None

        def get_visible_container():
            container = self.page.locator("div[data-testid='chat_input_input']")
            for i in range(container.count()):
                el = container.nth(i)
                try:
                    if el.is_visible():
                        return el
                except:
                    pass
            return None

        def read_visible_content():
            content = ""
            try:
                el = get_visible_editor()
                if el:
                    content = el.evaluate("el => el.innerText || el.textContent || ''")
            except:
                pass
            if not content or not content.strip():
                try:
                    el = get_visible_container()
                    if el:
                        content = el.evaluate("el => el.innerText || el.textContent || ''")
                except:
                    pass
            return content or ""

        def precondition(page):
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                print("🔄 前置动作: 跳转到豆包聊天页面(强制重置)...")
                page.goto("https://www.doubao.com/chat/")
                try:
                    page.wait_for_load_state("networkidle")
                except:
                    pass

        try:
            # 使用新ID以强制更新/使用新选择器
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.chat.input_box_v4",
                default_selector=default_selector,
                action_type="fill",
                text=text,
                precondition=precondition
            )
            
            try:
                self.page.wait_for_timeout(1000)
                
                try:
                    el = get_visible_editor()
                    if el:
                        el.click(timeout=2000)
                except:
                    print("⚠️  点击 contenteditable 失败，尝试点击父级输入框...")
                    try:
                        parent = get_visible_container()
                        if parent:
                            parent.click(timeout=2000)
                    except Exception as e:
                        print(f"⚠️  点击父级输入框也失败 (忽略): {e}")
                
                self.page.wait_for_timeout(500)
                
                content = read_visible_content()
                if not content or not content.strip():
                    print("⚠️  检测到输入框内容可能为空，跳过补输入，仅继续发送流程")
            except Exception as e:
                print(f"⚠️  验证输入内容时出错 (不影响流程): {e}")

        except Exception as e:
            print(f"❌ 输入框交互失败: {e}")
            raise e
    
    def _send_prompt_request(self, prompt_text: str) -> None:
        """发送提示词生成请求"""
        # 强制检查页面状态，不依赖 InteractionManager
        if "doubao.com/chat" not in self.page.url or "create-image" in self.page.url:
            print("🔄 [强制检查] 检测到页面状态不正确，跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

        print("💬 发送提示词生成请求 (Managed)...")
        self._fill_chat_input(prompt_text, "提示词")
        self._send_chat_message_with_validation("提示词生成请求")

        print("⏳ 等待AI回复（10秒）...")
        self.page.wait_for_timeout(10000)

    def _send_chat_message_with_validation(self, label: str) -> None:
        try:
            send_btn_selector = "button[data-testid='chat_input_send_button']"
            send_btn = self.page.locator(send_btn_selector)
            send_target = None
            for i in range(send_btn.count()):
                el = send_btn.nth(i)
                try:
                    if el.is_visible():
                        send_target = el
                        break
                except:
                    pass
            if send_target:
                send_target.click()
                self.page.wait_for_timeout(500)
            else:
                raise Exception("未找到可见的发送按钮")
            print(f"✅ {label}发送成功")
        except Exception as e:
            print(f"❌ 发送按钮点击失败: {e}")
            raise e

        def read_input_content():
            input_content = ""
            textarea = self.page.locator("textarea[data-testid='chat_input_input']")
            for i in range(textarea.count()):
                el = textarea.nth(i)
                try:
                    if el.is_visible():
                        input_content = el.evaluate("el => el.value || ''")
                        if input_content is not None:
                            return input_content
                except:
                    pass
            editor = self.page.locator("div[data-testid='chat_input_input'] div[contenteditable='true']")
            for i in range(editor.count()):
                el = editor.nth(i)
                try:
                    if el.is_visible():
                        input_content = el.evaluate("el => el.innerText || el.textContent || ''")
                        if input_content and input_content.strip():
                            return input_content
                except:
                    pass
            input_box = self.page.locator("div[data-testid='chat_input_input']")
            for i in range(input_box.count()):
                el = input_box.nth(i)
                try:
                    if el.is_visible():
                        input_content = el.evaluate("el => el.innerText || el.textContent || ''")
                        if input_content and input_content.strip():
                            return input_content
                except:
                    pass
            return input_content

        def is_send_button_disabled():
            try:
                send_btn = self.page.locator("button[data-testid='chat_input_send_button']")
                for i in range(send_btn.count()):
                    el = send_btn.nth(i)
                    try:
                        if el.is_visible():
                            try:
                                if el.is_disabled():
                                    return True
                            except:
                                pass
                            try:
                                aria_disabled = el.get_attribute("aria-disabled")
                                if aria_disabled == "true":
                                    return True
                            except:
                                pass
                            try:
                                disabled_attr = el.get_attribute("disabled")
                                if disabled_attr is not None:
                                    return True
                            except:
                                pass
                            break
                    except:
                        pass
            except:
                pass
            return False

        try:
            input_content = ""
            for _ in range(10):
                input_content = read_input_content()
                if not input_content or not input_content.strip():
                    break
                if is_send_button_disabled():
                    input_content = ""
                    break
                self.page.wait_for_timeout(500)
            if input_content and input_content.strip():
                print("⚠️  发送后输入框仍有内容，但检测到发送状态，继续流程")
        except Exception as e:
            print(f"❌ 发送结果校验失败: {e}")
            raise e
    
    def _fill_prompt_only(self, prompt_text: str) -> None:
        """仅在聊天输入框中输入提示词，不发送"""
        print("💬 在聊天输入框中输入提示词...")
        self._fill_chat_input(prompt_text, "提示词")
        
        print("✅ 提示词输入完成")

    def _get_ai_response(self) -> Optional[str]:
        """获取AI回复内容"""
        # 强制检查页面状态，不依赖 InteractionManager
        if "doubao.com/chat" not in self.page.url or "create-image" in self.page.url:
            print("🔄 [强制检查] 检测到页面状态不正确，跳转到豆包聊天页面...")
            self.page.goto("https://www.doubao.com/chat/")
            try:
                self.page.wait_for_load_state("networkidle")
            except:
                pass

        try:
            print("📋 获取AI回复内容 (Managed)...")
            
            # 点击复制按钮
            default_selector = "div[data-testid='receive_message']:last-of-type button[data-testid='message_action_copy']"
            
            def precondition(page):
                if "doubao.com/chat" not in page.url or "create-image" in page.url:
                    page.goto("https://www.doubao.com/chat/")
            
            # 等待复制按钮出现
            try:
                self.page.wait_for_selector("button[data-testid='message_action_copy']", timeout=120000)
            except:
                pass

            try:
                interaction_manager.perform_interaction(
                    self.page,
                    interaction_id="doubao.chat.copy_button_last",
                    default_selector=default_selector,
                    action_type="click",
                    precondition=precondition
                )
                self.page.wait_for_timeout(1000)
                
                # 从剪贴板读取内容
                prompt_result = pyperclip.paste().strip()
                
                if prompt_result:
                    print("✅ AI回复获取成功")
                    return prompt_result
                else:
                    print("⚠️  剪贴板内容为空")
                    return None
            except Exception as e:
                print(f"⚠️  复制按钮交互失败: {e}")
                return None
                
        except Exception as e:
            print(f"⚠️  获取AI回复时出错: {e}")
            return None
    
    def _save_prompt_to_file(self, prompt: str, markdown_file: str) -> None:
        """保存提示词到文件"""
        try:
            prompt_file = os.path.join(
                "test-results", 
                f"doubao_prompt_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt"
            )
            os.makedirs("test-results", exist_ok=True)
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            print(f"📁 提示词已保存到: {prompt_file}")
            
        except Exception as e:
            print(f"⚠️  保存提示词时出错: {e}")

    def _exit_prompt_generation_view(self) -> None:
        print("🔙 退出提示词生成界面...")
        closed = False
        try:
            text_button = self.page.get_by_text("编程", exact=True)
            if text_button.count() > 0:
                for i in range(text_button.count()):
                    candidate = text_button.nth(i)
                    if candidate.is_visible():
                        candidate.scroll_into_view_if_needed()
                        candidate.click()
                        closed = True
                        break
        except Exception as e:
            print(f"⚠️  关闭按钮点击失败: {e}")
        
        if not closed:
            try:
                fallback_text = self.page.get_by_text("编程")
                if fallback_text.count() > 0:
                    fallback_text.first.scroll_into_view_if_needed()
                    fallback_text.first.click()
                closed = True
            except Exception as e:
                print(f"⚠️  关闭图标点击失败: {e}")
        
        if closed:
            self.page.wait_for_timeout(500)
            print("✅ 已退出提示词生成界面")
        else:
            print("⚠️  未能退出提示词生成界面，继续尝试后续步骤")
    
    def _switch_to_image_generation_skill(self) -> None:
        """切换到图片生成技能"""
        print("🎯 切换到图片生成技能 (Managed)...")
        
        # 1. 输入切换指令
        self._fill_chat_input("/图像生成", "切换图像生成")
        
        # 2. 按下回车键
        default_selector = "div[data-testid='chat_input_input']"
        
        def precondition(page):
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                page.goto("https://www.doubao.com/chat/")
            # 确保输入框有内容
            try:
                page.locator(default_selector).fill("/图像生成")
            except:
                pass

        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.chat.input_enter",
                default_selector=default_selector,
                action_type="press",
                key="Enter",
                precondition=precondition
            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"⚠️  输入切换指令回车失败: {e}")
            
        # 3. 等待技能切换成功
        try:
            self.page.get_by_test_id("image-creation-chat-input-picture-ration-button").wait_for(state="visible", timeout=60000)
            print("✅ 图片生成技能切换成功")
        except Exception as e:
            print(f"❌ 图片生成技能切换失败: {e}")
            raise

    def _set_image_aspect_ratio(self, aspect_ratio: str) -> None:
        """设置图片比例"""
        print(f"📐 设置图片比例为 {aspect_ratio} (Managed)...")
        
        # 1. 点击比例按钮
        ratio_btn_selector = "[data-testid='image-creation-chat-input-picture-ration-button']"
        
        def precondition_ratio_menu(page):
            # 确保在图片生成模式
            try:
                if page.locator(ratio_btn_selector).count() == 0:
                    print("🔄 前置动作: 尝试切换到图片生成模式...")
                    page.locator("div[data-testid='chat_input_input']").fill("/图像生成")
                    page.locator("div[data-testid='chat_input_input']").press("Enter")
                    page.wait_for_timeout(2000)
            except:
                pass

        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id="doubao.image.ratio_button",
                default_selector=ratio_btn_selector,
                action_type="click",
                precondition=precondition_ratio_menu
            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"❌ 打开比例菜单失败: {e}")
            raise e
        
        # 2. 选择比例选项
        # 根据比例确定选项文本
        if aspect_ratio == "16:9":
            option_text = "16:9 桌面壁纸，风景"
        elif aspect_ratio == "9:16":
            option_text = "9:16 手机壁纸，人像"
        elif aspect_ratio == "4:3":
            option_text = "4:3 文章配图，插画"
        else:
            option_text = "16:9 桌面壁纸，风景"
            
        option_selector = f"text='{option_text}'"
        
        def precondition_option_select(page):
            # 确保菜单已打开
            precondition_ratio_menu(page)
            print("🔄 前置动作: 重新点击比例按钮...")
            page.locator(ratio_btn_selector).click()

        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id=f"doubao.image.ratio_option_{aspect_ratio.replace(':', '_')}",
                default_selector=option_selector,
                action_type="click",
                precondition=precondition_option_select
            )
            self.page.wait_for_timeout(1000)
            print(f"✅ 图片比例 {aspect_ratio} 设置成功")
        except Exception as e:
            print(f"❌ 选择比例选项失败: {e}")
            # 尝试备用点击
            try:
                self.page.get_by_text(option_text).click()
            except:
                pass

    def _send_image_generation_request(self, prompt: str) -> None:
        """发送图片生成请求"""
        print("🎨 发送图片生成请求 (Managed)...")
        self._send_chat_message_with_validation("图片生成请求")
    
    def _wait_for_image_generation(self) -> None:
        """等待图片生成完成"""
        print("⏳ 等待图片生成完成...")
        print("这可能需要几十秒时间，请耐心等待...")
        print("等待50秒")
        self.page.wait_for_timeout(50000)

    def _scroll_to_bottom(self, page=None):
        """滚动到底部以加载更多内容"""
        p = page or self.page
        print("⬇️ 滚动页面到底部...")
        try:
            p.locator("body").click()
            last_height = p.evaluate("() => document.body.scrollHeight")
            for _ in range(12):
                p.mouse.wheel(0, 2400)
                p.wait_for_timeout(300)
            for _ in range(4):
                p.keyboard.press("PageDown")
                p.wait_for_timeout(300)
            p.keyboard.press("End")
            p.wait_for_timeout(800)
            current_height = p.evaluate("() => document.body.scrollHeight")
            if current_height == last_height:
                p.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                p.wait_for_timeout(800)
        except Exception as e:
            print(f"⚠️  滚动页面失败: {e}")

    def _download_generated_images(self) -> List[str]:
        """下载生成的图片"""
        print("📥 开始下载生成的图片 (Managed)...")
        
        try:
            # 1. 滚动页面
            self._scroll_to_bottom()
            
            print("等待下载入口出现，超时时间为1分钟")
            # 2. 点击更多按钮
            more_btn_selector = "[data-testid='message_action_more']"
            
            def precondition_more_btn(page):
                self._scroll_to_bottom(page)
            
            try:
                # 确保至少有一个 more 按钮可见
                self.page.wait_for_selector(more_btn_selector, timeout=60000)
                
                # 我们通常需要点击最后一个
                # InteractionManager 默认操作 first，所以我们需要构造一个指向最后一个的选择器
                # 或者我们接受 InteractionManager 操作 first，但在 precondition 中我们尽量定位
                # 由于 CSS 选择器 :last-of-type 可能不准确，最好的方式是使用 locator.last
                # 但 InteractionManager 的 execute_action 默认是用 locator.first
                # 我们可以传递一个特殊的 index 参数给 execute_action? 不支持。
                # 我们可以构造一个 xpath 选择器指向最后一个
                last_more_selector = "xpath=(//*[@data-testid='message_action_more'])[last()]"
                
                interaction_manager.perform_interaction(
                    self.page,
                    interaction_id="doubao.image.more_button_last",
                    default_selector=last_more_selector,
                    action_type="click",
                    precondition=precondition_more_btn
                )
                self.page.wait_for_timeout(500)
            except Exception as e:
                print(f"❌ 点击更多按钮失败: {e}")
                # 尝试直接点击最后一个
                try:
                    self.page.get_by_test_id("message_action_more").last.click()
                except:
                    return []

            # 3. 点击下载菜单项
            download_item_selector = "[data-testid='message_action_download_dropdown']"
            
            def precondition_download_item(page):
                precondition_more_btn(page)
                # 点击最后一个更多按钮
                page.locator("xpath=(//*[@data-testid='message_action_more'])[last()]").click()

            # 设置下载事件监听器
            downloads = []
            def handle_download(download):
                downloads.append(download)
                print(f"📥 检测到下载: {download.suggested_filename}")
            
            self.page.on("download", handle_download)

            try:
                interaction_manager.perform_interaction(
                    self.page,
                    interaction_id="doubao.image.download_menu_item",
                    default_selector=download_item_selector,
                    action_type="click",
                    precondition=precondition_download_item
                )
                self.page.wait_for_timeout(500)
            except Exception as e:
                print(f"❌ 点击下载菜单项失败: {e}")
                return []

            # 4. 点击确认下载按钮
            confirm_btn_selector = "button:has-text('下载')"
            # 或者是 role=button, name='下载'
            
            def precondition_confirm_btn(page):
                precondition_download_item(page)
                page.locator(download_item_selector).click()

            try:
                # 可能会有多个下载按钮（历史消息的），我们需要确保是弹窗里的那个
                # 通常弹窗里的按钮是最后出现的，或者在特定容器里
                # 简单起见，使用 text='下载' 且可见的
                # 注意：这里可能会误点到其他的“下载”文字
                # 更好的选择器： div[class*='modal'] button:has-text('下载')
                # 但不确定 modal 的类名。
                # 尝试使用 role
                # default_selector = "button:has-text('下载')"
                
                interaction_manager.perform_interaction(
                    self.page,
                    interaction_id="doubao.image.download_confirm",
                    default_selector=confirm_btn_selector,
                    action_type="click",
                    precondition=precondition_confirm_btn
                )
            except Exception as e:
                print(f"⚠️  点击下载确认按钮失败: {e}")
                # 尝试直接点击
                try:
                    self.page.get_by_role("button", name="下载").click()
                except:
                    pass
            
            # 等待下载完成
            print("⏳ 等待下载完成...")
            self.page.wait_for_timeout(30000)  # 等待30秒
            
            # 处理下载的文件
            downloaded_files = []
            if downloads:
                print(f"📊 检测到 {len(downloads)} 个下载文件")
                
                for i, download in enumerate(downloads):
                    try:
                        # 生成文件名
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        original_name = download.suggested_filename or f"image_{i+1}.png"
                        name, ext = os.path.splitext(original_name)
                        filename = f"doubao_generated_image_{i+1}_{timestamp}{ext}"
                        file_path = os.path.join(self.downloads_dir, filename)
                        
                        download.save_as(file_path)
                        file_size = os.path.getsize(file_path)
                        
                        downloaded_files.append(file_path)
                        print(f"✅ 图片 {i+1} 下载成功: {filename}")
                        print(f"📊 文件大小: {file_size} 字节")
                        
                    except Exception as e:
                        print(f"⚠️  处理下载文件 {i+1} 时出错: {e}")
            else:
                print("⚠️  未检测到任何下载文件")
            
            return downloaded_files
            
        except Exception as e:
            print(f"⚠️  下载图片时出错: {e}")
            return []

    def select_ai_mode(self, mode: str) -> bool:
        """
        选择豆包AI的模式（极速、思考、超能）
        
        Args:
            mode: 要选择的模式，可选值：'极速', '思考', '超能'
        
        Returns:
            bool: 是否成功选择指定模式
        """
        # 验证输入参数
        valid_modes = ['极速', '思考', '超能']
        if mode not in valid_modes:
            print(f"❌ 无效的模式参数: {mode}")
            print(f"有效选项: {', '.join(valid_modes)}")
            return False
            
        print(f"🔄 正在选择豆包AI的'{mode}'模式 (Managed)...")
        
        # 定义默认选择器 - 优先尝试 tabindex=0 的 span，通常是可交互元素
        default_selector = f"span[tabindex='0']:has-text('{mode}')"
        
        def precondition(page):
            if "doubao.com/chat" not in page.url or "create-image" in page.url:
                print("🔄 前置动作: 跳转到豆包聊天页面(强制重置)...")
                page.goto("https://www.doubao.com/chat/")
                try:
                    page.wait_for_load_state("networkidle")
                except:
                    pass

        try:
            interaction_manager.perform_interaction(
                self.page,
                interaction_id=f"doubao.chat.mode_selection_{mode}",
                default_selector=default_selector,
                action_type="click",
                precondition=precondition
            )
            print(f"✅ 成功选择'{mode}'模式")
            return True
        except Exception as e:
            print(f"❌ 选择'{mode}'模式交互失败: {e}")
            # 尝试备用选择器 - 纯文本匹配
            try:
                print(f"⚠️  尝试备用选择器: text='{mode}'")
                self.page.click(f"text='{mode}'")
                print(f"✅ 通过备用选择器成功选择'{mode}'模式")
                return True
            except Exception as e2:
                print(f"❌ 备用选择器也失败: {e2}")
                return False

    def select_thinking_mode(self) -> bool:
        """
        选择豆包AI的"思考"模式（向后兼容方法）
        
        Returns:
            bool: 是否成功选择思考模式
        """
        return self.select_ai_mode("思考")


def create_doubao_generator(page: Page, context: BrowserContext) -> DoubaoAIImageGenerator:
    """
    创建豆包AI图片生成器实例
    
    Args:
        page: Playwright页面对象
        context: 浏览器上下文对象
        
    Returns:
        DoubaoAIImageGenerator实例
    """
    return DoubaoAIImageGenerator(page, context)
