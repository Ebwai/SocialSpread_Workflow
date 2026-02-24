# -*- coding: utf-8 -*-
"""
豆包AI图片生成模块
提供完整的豆包AI图片生成功能，包括提示词生成和图片下载
"""

import os
import time
import pyperclip
from typing import List, Optional, Tuple
from playwright.sync_api import Page, BrowserContext


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
    
    def generate_prompt_from_markdown(self, markdown_file: str) -> Optional[str]:
        """
        从Markdown文件生成文生图提示词
        
        Args:
            markdown_file: Markdown文件路径
            
        Returns:
            生成的提示词，失败时返回None
        """
        try:
            print("🤖 开始生成文生图提示词...")
            
            # 上传Markdown文件
            self._upload_markdown_file(markdown_file)
            
            # 发送提示词生成请求
            prompt_text = self._get_prompt_generation_text()
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

            # 切换到图片生成技能
            self._switch_to_image_generation_skill()

            # 在聊天输入框中输入提示词，不发送
            self._fill_prompt_only(prompt)
            
            # 设置图片比例
            self._set_image_aspect_ratio(aspect_ratio)

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
    
    def generate_images_from_markdown(self, markdown_file: str, aspect_ratio: str = "16:9") -> Tuple[Optional[str], List[str]]:
        """
        从Markdown文件生成图片（完整流程）
        
        Args:
            markdown_file: Markdown文件路径
            aspect_ratio: 图片比例，默认为"16:9"
            
        Returns:
            (提示词, 图片文件路径列表)
        """
        try:
            print("🚀 开始完整的图片生成流程...")
            
            # 选择豆包AI的模式为思考模式
            self.select_ai_mode("思考")

            # 步骤1：生成提示词
            prompt = self.generate_prompt_from_markdown(markdown_file)
            if not prompt:
                return None, []
            
            self._exit_prompt_generation_view()

            # 步骤2：生成图片
            image_files = self.generate_images_with_prompt(prompt, aspect_ratio)
            
            return prompt, image_files
            
        except Exception as e:
            print(f"❌ 完整流程执行失败: {e}")
            return None, []
    
    def _upload_markdown_file(self, markdown_file: str) -> None:
        """上传Markdown文件"""
        print("📤 上传Markdown文件...")
        
        try:
            upload_button = self.page.locator("button[data-dbx-name='button']", has=self.page.locator("svg path[d^='M17.3977']"))
            if upload_button.count() > 0:
                upload_button.first.click()
            else:
                self.page.get_by_test_id("upload_file_button").click()
        except Exception as e:
            print(f"⚠️  点击上传按钮失败，尝试旧选择器: {e}")
            self.page.get_by_test_id("upload_file_button").click()
        self.page.wait_for_timeout(1000)
        
        with self.page.expect_file_chooser() as page_upload_file:
            try:
                self.page.get_by_test_id("upload_file_panel_upload_item").click()
            except Exception:
                self.page.get_by_text("上传文件或图片").click()
        page_upload_file = page_upload_file.value
        page_upload_file.set_files(markdown_file)
        self.page.wait_for_timeout(1000)
        
        print("✅ Markdown文件上传成功")
    
    def _get_prompt_generation_text(self) -> str:
        """获取提示词生成请求文本"""
        return """You are an expert in text-to-image prompt engineering.

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
   - the image must not include any other text, code snippets, logos, or watermarks
6. Output only the final prompt in English. Do not include explanations. """

    def _fill_chat_input(self, text: str, step_label: str) -> None:
        print(f"✍️  准备输入: {step_label}")
        input_locator = self.page.get_by_test_id("chat_input_input")
        input_locator.wait_for(state="visible", timeout=60000)
        for _ in range(10):
            if input_locator.is_enabled():
                break
            self.page.wait_for_timeout(500)
        try:
            input_locator.click(timeout=10000)
        except Exception as e:
            print(f"⚠️  点击输入框失败: {e}")
        self.page.wait_for_timeout(200)
        input_locator.fill(text)
        self.page.wait_for_timeout(500)
        try:
            current_value = input_locator.input_value()
            if not current_value:
                input_locator.type(text, delay=20)
                self.page.wait_for_timeout(500)
                current_value = input_locator.input_value()
            if not current_value:
                print("⚠️  输入框未接收到文本")
        except Exception as e:
            print(f"⚠️  输入校验失败: {e}")
    
    def _send_prompt_request(self, prompt_text: str) -> None:
        """发送提示词生成请求"""
        print("💬 发送提示词生成请求...")
        self._fill_chat_input(prompt_text, "提示词")
        
        # 发送消息
        self.page.get_by_test_id("chat_input_send_button").click()
        print("✅ 提示词生成请求发送成功")
        
        # 等待AI回复
        print("⏳ 等待AI回复（10秒）...")
        self.page.wait_for_timeout(10000)
    
    def _fill_prompt_only(self, prompt_text: str) -> None:
        """仅在聊天输入框中输入提示词，不发送"""
        print("💬 在聊天输入框中输入提示词...")
        self._fill_chat_input(prompt_text, "提示词")
        
        print("✅ 提示词输入完成")

    def _get_ai_response(self) -> Optional[str]:
        """获取AI回复内容"""
        try:
            print("📋 获取AI回复内容...")
            
            # 点击复制按钮
            # 等待复制按钮出现，超时时间为2分钟
            try:
                copy_button = self.page.get_by_test_id("message_action_copy")
                copy_button.wait_for(timeout=120000)  # 等待2分钟
                copy_button.click()
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
                print(f"⚠️  等待复制按钮超时或点击失败: {e}")
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
        print("🎯 切换到图片生成技能...")
        try:
            self._fill_chat_input("/图像生成", "切换图像生成")
            input_locator = self.page.get_by_test_id("chat_input_input")
            input_locator.press("Enter")
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"⚠️  输入切换指令失败: {e}")
        try:
            self.page.get_by_test_id("image-creation-chat-input-picture-ration-button").wait_for(state="visible", timeout=60000)
            print("✅ 图片生成技能切换成功")
        except Exception as e:
            print(f"❌ 图片生成技能切换失败: {e}")
            raise
    
    def _set_image_aspect_ratio(self, aspect_ratio: str) -> None:
        """设置图片比例"""
        print(f"📐 设置图片比例为 {aspect_ratio}...")
        
        ratio_button = self.page.get_by_test_id("image-creation-chat-input-picture-ration-button")
        ratio_button.wait_for(state="visible", timeout=60000)
        ratio_button.scroll_into_view_if_needed()
        ratio_button.click()
        self.page.wait_for_timeout(500)
        
        # 选择比例
        if aspect_ratio == "16:9":
            self.page.get_by_text("16:9 桌面壁纸，风景").click()
        elif aspect_ratio == "9:16":
            self.page.get_by_text("9:16 手机壁纸，人像").click()
        elif aspect_ratio == "4:3":
            self.page.get_by_text("4:3 文章配图，插画").click()
        else:
            self.page.get_by_text("16:9 桌面壁纸，风景").click()
        
        self.page.wait_for_timeout(1000)
        print(f"✅ 图片比例 {aspect_ratio} 设置成功")
    
    def _send_image_generation_request(self, prompt: str) -> None:
        """发送图片生成请求"""
        print("🎨 发送图片生成请求...")
        print("正在点击发送按钮")
        # self.page.get_by_test_id("chat_input_input").locator("div").nth(1).click()
        self.page.wait_for_timeout(500)
        
        # 输入提示词
        # 这里也可以不用输入提示词，因为之前回答中已经包含了提示词，只需设置图片比例即可。
        # self.page.get_by_test_id("chat_input_input").fill(prompt)
        # self.page.wait_for_timeout(1000)
        
        # 发送请求
        self.page.get_by_test_id("chat_input_send_button").click()
        print("✅ 图片生成请求发送成功")
    
    def _wait_for_image_generation(self) -> None:
        """等待图片生成完成"""
        print("⏳ 等待图片生成完成...")
        print("这可能需要几十秒时间，请耐心等待...")
        print("等待50秒")
        self.page.wait_for_timeout(50000)

    def _download_generated_images(self) -> List[str]:
        """下载生成的图片"""
        print("📥 开始下载生成的图片...")
        
        try:
            print("⬇️ 向下滚动以显示下载入口...")
            try:
                self.page.locator("body").click()
                last_height = self.page.evaluate("() => document.body.scrollHeight")
                for _ in range(12):
                    self.page.mouse.wheel(0, 2400)
                    self.page.wait_for_timeout(300)
                for _ in range(4):
                    self.page.keyboard.press("PageDown")
                    self.page.wait_for_timeout(300)
                self.page.keyboard.press("End")
                self.page.wait_for_timeout(800)
                current_height = self.page.evaluate("() => document.body.scrollHeight")
                if current_height == last_height:
                    self.page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                    self.page.wait_for_timeout(800)
            except Exception as e:
                print(f"⚠️  滚动页面失败: {e}")
            print("等待下载入口出现，超时时间为1分钟")
            more_buttons = self.page.get_by_test_id("message_action_more")
            more_buttons.wait_for(state="visible", timeout=60000)
            print("下载入口出现")
            
            # 设置下载事件监听器
            downloads = []
            
            def handle_download(download):
                downloads.append(download)
                print(f"📥 检测到下载: {download.suggested_filename}")
            
            self.page.on("download", handle_download)
            
            print("🖱️  打开下载菜单...")
            more_buttons.last.click()
            self.page.wait_for_timeout(500)
            download_menu_items = self.page.get_by_test_id("message_action_download_dropdown")
            if download_menu_items.count() == 0:
                print("⚠️  未找到下载菜单项")
                return []
            download_menu_items.first.click()
            self.page.wait_for_timeout(500)
            try:
                download_confirm_button = self.page.get_by_role("button", name="下载")
                download_confirm_button.wait_for(state="visible", timeout=10000)
                download_confirm_button.click()
            except Exception as e:
                print(f"⚠️  点击下载确认按钮失败: {e}")
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
        
        try:
            print(f"🔄 正在选择豆包AI的'{mode}'模式...")
            
            # 方法1：通过文本内容定位指定模式按钮
            try:
                mode_button = self.page.get_by_text(mode, exact=True)
                if mode_button.count() > 0:
                    mode_button.click()
                    self.page.wait_for_timeout(1000)
                    print(f"✅ 通过文本定位成功选择'{mode}'模式")
                    return True
            except Exception as e1:
                print(f"⚠️  方法1失败: {e1}")
            
            # 方法2：通过CSS类名和文本内容定位
            try:
                mode_button = self.page.locator(f"span.button-mE6AaR:has-text('{mode}')")
                if mode_button.count() > 0:
                    mode_button.click()
                    self.page.wait_for_timeout(1000)
                    print(f"✅ 通过CSS类名和文本内容定位成功选择'{mode}'模式")
                    return True
            except Exception as e2:
                print(f"⚠️  方法2失败: {e2}")
            
            # 方法3：通过包含指定文本的span元素定位
            try:
                mode_button = self.page.locator(f"span:has-text('{mode}')")
                if mode_button.count() > 0:
                    # 过滤出具有button-mE6AaR类的元素
                    for i in range(mode_button.count()):
                        element = mode_button.nth(i)
                        if "button-mE6AaR" in element.get_attribute("class", ""):
                            element.click()
                            self.page.wait_for_timeout(1000)
                            print(f"✅ 通过span元素定位成功选择'{mode}'模式")
                            return True
            except Exception as e3:
                print(f"⚠️  方法3失败: {e3}")
            
            # 方法4：通过tabindex属性定位（查找所有可点击的按钮）
            try:
                all_buttons = self.page.locator("span[tabindex='0']")
                if all_buttons.count() > 0:
                    for i in range(all_buttons.count()):
                        button = all_buttons.nth(i)
                        button_text = button.text_content()
                        if button_text == mode:
                            button.click()
                            self.page.wait_for_timeout(1000)
                            print(f"✅ 通过tabindex属性定位成功选择'{mode}'模式")
                            return True
            except Exception as e4:
                print(f"⚠️  方法4失败: {e4}")
            
            # 方法5：兜底方案 - 查找所有包含指定文本的元素
            try:
                all_mode_elements = self.page.locator(f"*:has-text('{mode}')")
                if all_mode_elements.count() > 0:
                    # 遍历所有包含指定文本的元素，找到可点击的按钮
                    for i in range(all_mode_elements.count()):
                        element = all_mode_elements.nth(i)
                        element_class = element.get_attribute("class", "")
                        if "button-mE6AaR" in element_class or "button" in element_class:
                            element.click()
                            self.page.wait_for_timeout(1000)
                            print(f"✅ 通过兜底方案成功选择'{mode}'模式")
                            return True
            except Exception as e5:
                print(f"⚠️  方法5失败: {e5}")
            
            print(f"❌ 所有方法都无法找到'{mode}'模式按钮")
            return False
            
        except Exception as e:
            print(f"❌ 选择'{mode}'模式时出错: {e}")
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
