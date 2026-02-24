# 🚀 SocialSpread Workflow (社交媒体全自动分发系统)

## 📝 简介 (Introduction)
SocialSpread Workflow 是一个基于 Python 的全自动化社交媒体内容分发系统。它旨在解决内容创作者在多平台发布时的痛点：繁琐的排版调整、不同平台的风格适配以及重复的上传操作。

通过结合 Playwright 自动化技术和 AI 大模型（如豆包 AI），本系统能够将一篇 Markdown 格式的原始文章，自动改写为适配微信公众号、小红书、钉钉等不同平台风格的内容，并自动完成发布或推送到草稿箱。

## 🎯 适用人群与场景
**适用人群**：
- 技术博客作者、自媒体运营者
- 需要维护企业技术博客的开发者
- 希望通过自动化节省分发时间的个人开发者

**使用场景**：
- **一次编写，多处运行**：写好一篇 Markdown 技术文章，自动分发到公众号（适配排版）、小红书（生成长图文风格）、钉钉（内部同步）。
- **AI 风格化重写**：针对小红书需要更活泼、带 Emoji 的风格，针对公众号需要更正式的排版，系统自动根据预设 Prompt 进行改写。
- **自动化发布**：对于提供 API 的平台（如钉钉、微信公众号）直接调用接口；对于无 API 的平台（如小红书），使用浏览器自动化模拟人工操作。

## ✨ 核心特性 (Features)
- **🤖 多模态自动化引擎**：
  - **API 集成**：原生支持微信公众号（草稿箱）、钉钉（工作通知/群机器人）接口。
  - **RPA 模拟**：内置 Playwright 脚本，支持小红书网页版的全自动登录（需扫码）、内容填写、标签选择和发布。
  
- **🧠 AI 智能改写**：
  - 集成 LLM（如豆包），根据不同平台的受众画像，自动调整文章语气、结构和排版。
  - 支持自定义 Prompt，让你的文章在小红书“种草”，在公众号“沉稳”。

- **🔌 插件化架构**：
  - 基于 Pytest 的运行框架，通过简单的命令行参数即可控制发布平台、是否改写等行为。
  - 易于扩展新的平台模块。

- **🛡️ 隐私与安全**：
  - 所有敏感配置（AppID, Secret）通过环境变量管理，支持 `.env` 文件，确保密钥不泄露。

## 🚀 极简部署指南 (How to Use)

### 阶段一：环境准备
确保你的电脑已安装 Python 3.8+ 和 Chrome 浏览器。

1.  **克隆项目并安装依赖**：
    ```bash
    # 推荐使用 uv 管理依赖，或者直接 pip
    pip install -r requirements.txt
    # 安装 Playwright 浏览器驱动
    playwright install chromium
    ```

2.  **配置环境变量**：
    - 复制 `.env.example` 为 `.env`。
    - 填入你的微信公众号 `WECHAT_APP_ID`, `WECHAT_APP_SECRET`。
    - 填入钉钉 `DINGTALK_APP_KEY`, `DINGTALK_APP_SECRET`。
    - 根据需要调整 AI 提示词配置。

### 阶段二：运行发布
使用 `pytest` 命令启动自动化流程。

**示例 1：发布到所有平台**
```bash
pytest -s test_social_media_automatic_publish.py --title="我的新文章" --platforms="all"
```

**示例 2：仅发布到小红书并开启 AI 改写**
```bash
pytest -s test_social_media_automatic_publish.py --title="我的新文章" --platforms="xiaohongshu" --rewrite-platform-content="true"
```

**示例 3：指定 Markdown 文件路径**
```bash
pytest -s test_social_media_automatic_publish.py --title="深度学习入门" --markdown-file="./articles/deep_learning.md"
```

## ✅ 已完成的特性 (Completed)
- [x] **微信公众号集成**：支持上传图文素材到草稿箱，支持封面上传。
- [x] **钉钉集成**：支持发送 Markdown 消息到工作通知。
- [x] **小红书自动化**：
    - [x] 自动登录检测
    - [x] 标题与正文填写
    - [x] 智能字数检测与内容截断/分段
    - [x] 自动点击“一键排版”
- [x] **AI 改写模块**：基于环境变量配置的 Prompt 进行多平台内容适配。

## 🚧 待办事项 (To-Do List)
- [ ] **多账号管理**：支持配置多个小红书或公众号账号。
- [ ] **更多平台支持**：计划接入知乎、CSDN、掘金等技术社区。
- [ ] **数据分析看板**：统计各平台阅读量与互动数据。
- [ ] **GUI 界面**：开发桌面端控制面板，降低命令行使用门槛。
