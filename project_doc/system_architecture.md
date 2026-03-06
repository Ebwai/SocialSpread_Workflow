# 系统架构说明书

## 1. 架构概览
- **前端交互**：Playwright（自动化控制豆包Web端、小红书创作中心）
- **交互管理**：`InteractionManager`（负责原子交互的执行、失败捕获、录制更新）
- **API集成**：
    - `wechat_mp_sdk`：用于微信公众号API交互（上传素材、发布文章）。
    - 外部AI服务：豆包Web端（通过Playwright）。
- **流程控制**：Python（pytest作为测试运行器，组织任务流程）。
- **工具库**：
    - `markdown_cleaner_sdk`：文本预处理。
    - `word_counter_sdk`：字数统计。

## 2. 核心模块列表

### 2.1 交互管理器 (`interaction_manager/`)
- **功能**：管理所有 Playwright UI 交互，提供自愈能力。
- **核心组件**：
    - `core.py`: 实现 `InteractionManager` 类。
    - `atom_storage.json`: 存储所有交互原子的最新 Selector 和元数据。
- **核心逻辑**：
    - `perform_interaction`: 执行原子交互。
    - `_launch_recorder`: 启动 Codegen 录制新交互。
    - `precondition`: 保证录制上下文的钩子函数。

### 2.2 豆包AI生成器 (`doubao_ai_image_generator.py`)
- **功能**：与豆包Web端交互，生成文章改写、摘要和封面图。
- **输入**：`browser_context`（Playwright Context）、Markdown文件路径、提示词。
- **输出**：改写后的Markdown文件、生成的封面图片文件。
- **核心逻辑**：
    - `open_doubao_chat_page`：打开豆包聊天界面。
    - `click_doubao_upload_button`：(已接入 InteractionManager) 点击上传按钮。

### 2.3 微信公众号SDK (`wechat_mp_sdk/wechat_mp_sdk.py`)
- **功能**：封装微信公众号API。
- **输入**：`app_id`、`app_secret`。
- **输出**：Access Token、Media ID、Article Draft ID。
- **核心逻辑**：
    - `get_access_token`：获取API令牌。
    - `upload_permanent_material`：上传永久素材（图片）。
    - `upload_image`：上传临时素材（图片）。

### 2.4 主流程脚本 (`test_social_media_automatic_publish.py`)
- **功能**：集成各模块，执行完整的自动化发布流程。
- **输入**：命令行参数（`--url`、`--markdown-file` 等）。
- **输出**：发布状态日志、生成的草稿链接。
- **测试**：基于 `pytest` 框架，提供 `--title`, `--url`, `--markdown-file` 等参数运行。

### 2.5 测试配置 (`conftest.py`)
- **功能**：提供pytest fixtures，配置浏览器环境，加载 `.env` 变量。
- **输入**：无。
- **输出**：浏览器上下文、测试数据目录。

## 3. 技术选型理由
- **Playwright**：比Selenium更快、更稳定，支持Headless模式，适合Web自动化。
- **InteractionManager**：自研的轻量级 RPA 框架，解决 UI 自动化维护成本高的问题，通过“运行时录制”替代“开发时硬编码”。
- **Pytest**：强大的测试框架，支持参数化测试，易于集成CI/CD。
- **Python-dotenv**：方便管理环境变量，避免硬编码敏感信息。
- **WeChat Official Account API**：直接调用API比Web自动化更稳定，减少维护成本。

## 4. 状态追踪
- [✓] 移除钉钉相关模块。
- [✓] 更新 `doubao_ai_image_generator.py` 以支持 robust 上传。
- [✓] 创建 `tests/test_wechat_mp_workflow.py` 验证微信公众号API。
- [✓] 实现 `InteractionManager` 并集成到主流程。
