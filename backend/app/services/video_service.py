"""
视频处理服务
"""
import os
import uuid
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
            # 保存文件
            contents = await file.read()
            file_size = len(contents)
            
            # 验证文件大小
            validate_video_size(file_size)
            
            with open(original_path, "wb") as f:
                f.write(contents)
            
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
                
                return {
                    "id": video_record["id"],
                    "original_filename": video_record["original_filename"],
                    "file_path": video_record["file_path"],
                    "duration": video_record["duration"],
                    "file_size": video_record["file_size"],
                    "thumbnail_path": video_record.get("thumbnail_path"),
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
