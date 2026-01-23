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
    port = int(os.environ.get("PORT", settings.port))
    # 在生产环境下关闭 reload
    is_debug = os.environ.get("DEBUG", "true").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=is_debug,
        log_level="info"
    )
