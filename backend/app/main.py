"""
FastAPI 主应用
羽毛球杀球分析后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.config import settings
from app.routers import auth, video, analysis, history


# 创建 FastAPI 应用
app = FastAPI(
    title="羽毛球杀球分析 API",
    description="使用 AI 分析羽毛球杀球视频，提供速度估算和技术建议",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(history.router, prefix="/api")


# 挂载静态文件（上传的视频和缩略图）
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """API 根路径，返回服务信息"""
    return {
        "service": "羽毛球杀球分析 API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "badminton-smash-analysis-api"
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"服务器内部错误: {str(exc)}",
            "type": type(exc).__name__
        }
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    # 确保上传目录存在
    os.makedirs(os.path.join(settings.upload_dir, "original"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "processed"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "thumbnails"), exist_ok=True)
    
    print("=" * 60)
    print("🏸 羽毛球杀球分析 API 启动成功！")
    print(f"📝 API 文档: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 健康检查: http://{settings.host}:{settings.port}/health")
    print("=" * 60)


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    from app.database import Database
    Database.close()
    print("\n👋 应用已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
