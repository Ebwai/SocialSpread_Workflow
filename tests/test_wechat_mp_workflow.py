import pytest
import os
import time
from pathlib import Path
from wechat_mp_sdk.wechat_mp_sdk import WeChatMPSDK

@pytest.fixture
def wechat_sdk():
    """初始化微信公众号SDK"""
    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        pytest.skip("未配置WECHAT_APP_ID或WECHAT_APP_SECRET，跳过微信公众号测试")
    
    return WeChatMPSDK(app_id=app_id, app_secret=app_secret)

@pytest.fixture
def test_image_path(tmp_path):
    """创建一个临时测试图片"""
    # 这里我们创建一个简单的文本文件作为伪造的图片，或者我们需要一个真实的图片
    # 微信API会检查文件格式。最好使用真实图片。
    # 我们尝试找一个项目中的图片，或者生成一个。
    
    # 尝试查找项目中的任意图片
    image_files = list(Path(".").rglob("*.png")) + list(Path(".").rglob("*.jpg"))
    if image_files:
        return str(image_files[0])
    
    # 如果没有，跳过测试
    pytest.skip("未找到测试图片，跳过上传测试")

def test_get_access_token(wechat_sdk):
    """测试获取Access Token"""
    token = wechat_sdk.get_access_token()
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    print(f"✅ 获取Access Token成功: {token[:10]}...")

def test_upload_image(wechat_sdk, test_image_path):
    """测试上传图片素材"""
    print(f"📤 正在测试上传图片: {test_image_path}")
    try:
        result = wechat_sdk.upload_image(test_image_path)
        assert result is not None
        assert "media_id" in result
        assert "url" in result
        print(f"✅ 图片上传成功，Media ID: {result['media_id']}")
        
        # 注意：永久素材通常需要手动删除，或者通过API删除
        # 这里我们记录下 media_id 以便后续清理（如果SDK支持删除）
        # SDK 目前似乎没有 del_material 方法，我们建议用户后续手动清理或扩展SDK
        
    except Exception as e:
        pytest.fail(f"❌ 上传图片失败: {e}")

def test_upload_permanent_material_full(wechat_sdk, test_image_path):
    """测试完整的永久素材上传流程"""
    try:
        result = wechat_sdk.upload_permanent_material(test_image_path, material_type='image')
        assert "media_id" in result
        print(f"✅ 永久素材上传成功: {result['media_id']}")
    except Exception as e:
        pytest.fail(f"❌ 永久素材上传失败: {e}")
