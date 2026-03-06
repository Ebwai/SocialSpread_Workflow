# 测试计划 (testplan.md)

## 1. 测试范围
- **微信公众号发布流程**：测试图片素材上传、文章素材上传（待开发）。
- **豆包AI内容生成流程**：测试文章改写、摘要生成、封面生成。
- **文件上传功能**：测试豆包Web端文件上传。
- **交互自愈机制**：验证 Selector 失效时的自动重录与恢复能力。

## 2. 自动化测试用例

### 2.1 微信公众号流程 (`tests/test_wechat_mp_workflow.py`)
- **Case 1: `test_get_access_token`**
    - 目标：验证获取Access Token是否成功。
    - 预期：返回非空Token。
    - 状态：[✓] 已实现，但受限于IP白名单。
- **Case 2: `test_upload_image`**
    - 目标：上传临时图片素材。
    - 预期：返回Media ID和URL。
    - 状态：[✓] 已实现，但受限于IP白名单。
- **Case 3: `test_upload_permanent_material_full`**
    - 目标：上传永久图片素材。
    - 预期：返回Media ID。
    - 状态：[✓] 已实现，但受限于IP白名单。

### 2.2 豆包AI流程 (`test_social_media_automatic_publish.py`)
- **Case 4: `generate_rewritten_content_with_doubao`**
    - 目标：验证文章改写功能。
    - 预期：成功上传Markdown文件，输入提示词，获取改写后的Markdown文件。
    - 状态：[✓] 已修复上传逻辑，并接入 InteractionManager。
- **Case 5: `generate_summary_with_doubao`**
    - 目标：验证摘要生成功能。
    - 预期：成功生成摘要。
    - 状态：[✓] 已接入 InteractionManager。

### 2.3 交互自愈验证 (手动触发)
- **Case 6: 模拟 Selector 失效**
    - 步骤：
        1. 手动修改 `test_social_media_automatic_publish.py` 中的 `default_selector` 为无效值。
        2. 运行脚本。
        3. 观察控制台是否提示“启动交互录制器”。
        4. 在弹出浏览器中操作正确元素。
        5. 验证 `atom_storage.json` 是否更新，且流程继续执行。
    - 状态：[✓] 机制已实现，待手动验证。

## 3. 手动验证清单
- **IP白名单配置**：
    - 登录微信公众平台后台 -> 开发 -> 基本配置 -> IP白名单。
    - 将测试机器IP添加到白名单。
- **豆包Web端登录**：
    - 确保Playwright启动的浏览器已登录豆包账号（或通过Cookies注入）。

## 4. 状态追踪
- [✓] 创建微信公众号自动化测试用例。
- [✓] 修复豆包上传功能测试用例。
- [✓] 验证交互自愈机制（代码实现完成）。
- [?] 验证IP白名单配置。
