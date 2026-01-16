#!/usr/bin/env python3
"""
启动脚本
运行 FastAPI 应用
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )
