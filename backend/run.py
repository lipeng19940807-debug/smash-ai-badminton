#!/usr/bin/env python3
"""
启动脚本
运行 FastAPI 应用
"""
import uvicorn
from app.config import settings


import os

if __name__ == "__main__":
    # 微信云托管环境会自动注入 PORT 环境变量，默认为 80
    # 我们优先使用环境变量，如果没有则使用 settings 里的默认值 (现在已改为 80)
    port = int(os.environ.get("PORT", settings.port))
    
    # 在生产环境下关闭 reload，除非明确指定 DEBUG=true
    is_debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    print(f"Starting server on {settings.host}:{port} (debug: {is_debug})")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        reload=is_debug,
        log_level="info"
    )
