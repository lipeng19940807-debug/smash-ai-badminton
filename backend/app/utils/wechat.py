import os
import httpx
from fastapi import HTTPException, status

async def get_wechat_openid(code: str) -> str:
    """
    通过 code 获取微信 openid
    """
    app_id = os.getenv("WECHAT_APP_ID")
    secret = os.getenv("WECHAT_APP_SECRET")
    
    if not app_id or not secret:
        # 开发环境下如果未配置，为了方便测试，可以允许特定 mock code
        if code.startswith("mock_") or os.getenv("ENVIRONMENT") != "production":
            return f"openid_{code or 'dev_user'}"
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="微信小程序配置缺失 (WECHAT_APP_ID, WECHAT_APP_SECRET)，请在 backend/.env 文件中配置"
        )
        
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={secret}&js_code={code}&grant_type=authorization_code"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"连接微信服务器失败: {str(e)}"
            )
        
    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {data.get('errmsg')}"
        )
        
    return data["openid"]
