"""
视频处理服务
"""
import os
import uuid
import httpx
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from supabase import Client
from app.config import settings
from app.utils.ffmpeg_helper import FFmpegHelper
from app.utils.validators import validate_video_file, validate_video_size, validate_trim_range


class VideoService:
    """视频处理服务类"""
    
    def __init__(self, db: Client):
        self.db = db
        self.upload_dir = settings.upload_dir
        
        # 确保上传目录存在
        os.makedirs(os.path.join(self.upload_dir, "original"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "processed"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "thumbnails"), exist_ok=True)
    
    async def sync_cloud_video(
        self,
        file_id: str,
        user_id: str,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None
    ) -> dict:
        """
        从微信云存储同步视频并处理
        """
        # 1. 微信云托管内部接口换取下载链接
        # 微信云托管内部可以通过该地址获取文件下载链接，无需额外鉴权
        try:
            async with httpx.AsyncClient() as client:
                # 微信云托管内部 API
                cloud_api_url = "http://api.weixin.qq.com/tcb/batchdownloadfile"
                payload = {
                    "env": "cloud1-1grfk67f82062cc1",
                    "file_list": [
                        {
                            "fileid": file_id,
                            "max_age": 7200
                        }
                    ]
                }
                response = await client.post(cloud_api_url, json=payload)
                res_data = response.json()
                
                if res_data.get("errcode") == 0 and res_data.get("file_list"):
                    download_url = res_data["file_list"][0]["download_url"]
                else:
                    raise Exception(f"获取下载链接失败: {res_data.get('errmsg')}")

                # 2. 下载文件到本地 original 目录
                unique_id = str(uuid.uuid4())
                stored_filename = f"{unique_id}.mp4"
                original_path = os.path.join(self.upload_dir, "original", stored_filename)
                
                async with client.stream("GET", download_url) as r:
                    with open(original_path, "wb") as f:
                        async for chunk in r.aiter_bytes():
                            f.write(chunk)
                
                # 3. 后续处理（复用现有逻辑）
                # 获取视频时长
                video_info = FFmpegHelper.get_video_info(original_path)
                duration = video_info['duration']
                
                # 处理视频
                processed_filename = f"{unique_id}_processed.mp4"
                processed_path = os.path.join(self.upload_dir, "processed", processed_filename)
                
                _, processed_info = FFmpegHelper.process_video(
                    input_path=original_path,
                    output_path=processed_path,
                    trim_start=trim_start,
                    trim_end=trim_end,
                    compress=True
                )
                
                # 生成缩略图
                thumbnail_filename = f"{unique_id}_thumb.jpg"
                thumbnail_path = os.path.join(self.upload_dir, "thumbnails", thumbnail_filename)
                FFmpegHelper.generate_thumbnail(processed_path, thumbnail_path)
                
                # 保存数据库
                video_data = {
                    "user_id": user_id,
                    "original_filename": f"cloud_{unique_id[:8]}.mp4",
                    "stored_filename": processed_filename,
                    "file_path": processed_path,
                    "file_size": os.path.getsize(processed_path),
                    "duration": processed_info['duration'],
                    "thumbnail_path": thumbnail_path,
                    "trim_start": trim_start or 0.0,
                    "trim_end": trim_end,
                }
                
                db_res = self.db.table("videos").insert(video_data).execute()
                video_record = db_res.data[0]
                
                return {
                    "id": video_record["id"],
                    "original_filename": video_record["original_filename"],
                    "file_path": video_record["file_path"],
                    "duration": video_record["duration"],
                    "file_size": video_record["file_size"],
                    "thumbnail_path": video_record["thumbnail_path"],
                    "uploaded_at": video_record["uploaded_at"]
                }
        except Exception as e:
            print(f"云存储视频同步失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"从云存储同步视频失败: {str(e)}"
            )

    async def upload_video(
        self,
        file: UploadFile,
        user_id: str,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None
    ) -> dict:
        """
        上传并处理视频
        
        Args:
            file: 上传的视频文件
            user_id: 用户ID
            trim_start: 裁剪起始时间
            trim_end: 裁剪结束时间
        
        Returns:
            视频信息字典
        """
        # 1. 验证文件
        validate_video_file(file)
        
        # 2. 生成唯一文件名
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        unique_id = str(uuid.uuid4())
        original_filename = file.filename
        stored_filename = f"{unique_id}.{file_ext}"
        
        # 3. 保存原始文件
        original_path = os.path.join(self.upload_dir, "original", stored_filename)
        
        try:
            # 流式保存文件，防止内存溢出
            file_size = 0
            CHUNK_SIZE = 1024 * 1024  # 1MB chunks
            
            with open(original_path, "wb") as f:
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    f.write(chunk)
                    
                    # 检查文件大小是否超过限制
                    if file_size > settings.max_video_size_bytes:
                        f.close()
                        os.remove(original_path)
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"视频文件过大 (超过 {settings.max_video_size_mb}MB)"
                        )
            
            # 指针回到文件开头(如果后续还需要读取，但这里都是用路径处理了，所以不需要seek)
            # await file.seek(0)
            
            # 4. 获取视频信息
            try:
                video_info = FFmpegHelper.get_video_info(original_path)
                duration = video_info['duration']
            except Exception as e:
                # 清理已保存的文件
                if os.path.exists(original_path):
                    os.remove(original_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的视频文件: {str(e)}"
                )
            
            # 5. 验证裁剪范围
            if trim_start is not None or trim_end is not None:
                trim_start, trim_end = validate_trim_range(trim_start, trim_end, duration)
            
            # 6. 处理视频（裁剪 + 压缩）
            processed_filename = f"{unique_id}_processed.mp4"
            processed_path = os.path.join(self.upload_dir, "processed", processed_filename)
            
            try:
                _, processed_info = FFmpegHelper.process_video(
                    input_path=original_path,
                    output_path=processed_path,
                    trim_start=trim_start,
                    trim_end=trim_end,
                    compress=True,
                    crf=28
                )
                
                # 更新时长为处理后的时长
                duration = processed_info['duration']
            
            except Exception as e:
                # 清理文件
                if os.path.exists(original_path):
                    os.remove(original_path)
                if os.path.exists(processed_path):
                    os.remove(processed_path)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"视频处理失败: {str(e)}"
                )
            
            # 7. 生成缩略图
            thumbnail_filename = f"{unique_id}_thumb.jpg"
            thumbnail_path = os.path.join(self.upload_dir, "thumbnails", thumbnail_filename)
            
            try:
                FFmpegHelper.generate_thumbnail(processed_path, thumbnail_path)
            except Exception as e:
                # 缩略图生成失败不影响主流程
                print(f"Warning: 缩略图生成失败: {str(e)}")
                thumbnail_path = None
            
            # 8. 保存到数据库
            video_data = {
                "user_id": user_id,
                "original_filename": original_filename,
                "stored_filename": processed_filename,
                "file_path": processed_path,
                "file_size": os.path.getsize(processed_path),
                "duration": duration,
                "thumbnail_path": thumbnail_path,
                "trim_start": trim_start or 0.0,
                "trim_end": trim_end,
            }
            
            try:
                response = self.db.table("videos").insert(video_data).execute()
                if not response.data:
                    raise Exception("数据库插入失败")
                
                video_record = response.data[0]
                
                # 清理原始文件（可选，如果不需要保留）
                # os.remove(original_path)
                
                # 构建缩略图 URL（如果存在）
                thumbnail_url = None
                if video_record.get("thumbnail_path"):
                    # 将本地路径转换为可访问的 URL
                    # 例如: ./uploads/thumbnails/xxx.jpg -> /uploads/thumbnails/xxx.jpg
                    thumbnail_path = video_record["thumbnail_path"]
                    if thumbnail_path.startswith("./"):
                        thumbnail_path = thumbnail_path[2:]
                    elif not thumbnail_path.startswith("/"):
                        thumbnail_path = "/" + thumbnail_path
                    # 移除 uploads 前缀（因为静态文件挂载在 /uploads）
                    if thumbnail_path.startswith("/uploads/"):
                        thumbnail_url = thumbnail_path
                    else:
                        thumbnail_url = f"/uploads/{thumbnail_path}"
                
                return {
                    "id": video_record["id"],
                    "original_filename": video_record["original_filename"],
                    "file_path": video_record["file_path"],
                    "duration": video_record["duration"],
                    "file_size": video_record["file_size"],
                    "thumbnail_path": thumbnail_url,  # 返回 URL 而不是本地路径
                    "uploaded_at": video_record["uploaded_at"]
                }
            
            except Exception as e:
                # 数据库操作失败，清理文件
                if os.path.exists(original_path):
                    os.remove(original_path)
                if os.path.exists(processed_path):
                    os.remove(processed_path)
                if thumbnail_path and os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"保存视频信息失败: {str(e)}"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            # 清理可能的文件
            if os.path.exists(original_path):
                try:
                    os.remove(original_path)
                except:
                    pass
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"上传视频失败: {str(e)}"
            )
    
    async def get_video(self, video_id: str, user_id: str) -> dict:
        """
        获取视频信息
        
        Args:
            video_id: 视频ID
            user_id: 用户ID
        
        Returns:
            视频信息字典
        """
        try:
            response = self.db.table("videos").select("*").eq("id", video_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="视频不存在"
                )
            
            return response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取视频信息失败: {str(e)}"
            )
