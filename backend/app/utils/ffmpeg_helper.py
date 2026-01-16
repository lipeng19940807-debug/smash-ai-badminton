"""
FFmpeg 视频处理工具
"""
import os
import ffmpeg
from typing import Tuple, Optional
from app.config import settings


class FFmpegHelper:
    """FFmpeg 视频处理辅助类"""
    
    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """
        获取视频元数据
        
        Args:
            file_path: 视频文件路径
        
        Returns:
            包含视频信息的字典(duration, width, height, codec等)
        """
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if video_stream is None:
                raise ValueError("未找到视频流")
            
            duration = float(probe['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            codec = video_stream['codec_name']
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'codec': codec,
                'bit_rate': int(probe['format'].get('bit_rate', 0))
            }
        
        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")
    
    @staticmethod
    def trim_video(
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float
    ) -> None:
        """
        裁剪视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
        """
        try:
            duration = end_time - start_time
            
            (
                ffmpeg
                .input(input_path, ss=start_time, t=duration)
                .output(
                    output_path,
                    codec='copy',  # 使用复制模式，速度快
                    avoid_negative_ts='make_zero'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"裁剪视频失败: {error_message}")
    
    @staticmethod
    def compress_video(
        input_path: str,
        output_path: str,
        target_size_mb: Optional[float] = None,
        crf: int = 28
    ) -> None:
        """
        压缩视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            target_size_mb: 目标文件大小（MB），如果指定则忽略 crf
            crf: 质量参数（18-28，数值越大文件越小，质量越低）
        """
        try:
            # 获取视频信息
            info = FFmpegHelper.get_video_info(input_path)
            duration = info['duration']
            
            # 如果指定了目标大小，计算比特率
            if target_size_mb:
                target_size_bytes = target_size_mb * 1024 * 1024
                # 预留 10% 给音频
                video_bitrate = int((target_size_bytes * 8 * 0.9) / duration)
                
                (
                    ffmpeg
                    .input(input_path)
                    .output(
                        output_path,
                        video_bitrate=video_bitrate,
                        audio_bitrate='128k',
                        vcodec='libx264',
                        acodec='aac'
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
            else:
                # 使用 CRF 模式压缩
                (
                    ffmpeg
                    .input(input_path)
                    .output(
                        output_path,
                        vcodec='libx264',
                        crf=crf,
                        preset='medium',
                        acodec='aac',
                        audio_bitrate='128k'
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
        
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"压缩视频失败: {error_message}")
    
    @staticmethod
    def generate_thumbnail(
        video_path: str,
        thumbnail_path: str,
        time_offset: Optional[float] = None
    ) -> None:
        """
        生成视频缩略图
        
        Args:
            video_path: 视频文件路径
            thumbnail_path: 缩略图保存路径
            time_offset: 截取时间点（秒），如果为None则取视频中间帧
        """
        try:
            # 如果未指定时间点，取视频中间帧
            if time_offset is None:
                info = FFmpegHelper.get_video_info(video_path)
                time_offset = info['duration'] / 2
            
            (
                ffmpeg
                .input(video_path, ss=time_offset)
                .filter('scale', 320, -1)  # 宽度320px，高度自适应
                .output(thumbnail_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"生成缩略图失败: {error_message}")
    
    @staticmethod
    def process_video(
        input_path: str,
        output_path: str,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None,
        compress: bool = True,
        crf: int = 28
    ) -> Tuple[str, dict]:
        """
        处理视频（裁剪 + 压缩）
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            trim_start: 裁剪起始时间
            trim_end: 裁剪结束时间
            compress: 是否压缩
            crf: 压缩质量参数
        
        Returns:
            (处理后视频路径, 视频信息)
        """
        try:
            # 获取原始视频信息
            original_info = FFmpegHelper.get_video_info(input_path)
            
            # 如果需要裁剪
            if trim_start is not None and trim_end is not None:
                temp_trimmed = output_path + ".trimmed.mp4"
                FFmpegHelper.trim_video(input_path, temp_trimmed, trim_start, trim_end)
                process_input = temp_trimmed
            else:
                process_input = input_path
            
            # 如果需要压缩
            if compress:
                FFmpegHelper.compress_video(process_input, output_path, crf=crf)
            else:
                # 如果不压缩但裁剪了，重命名临时文件
                if process_input != input_path:
                    os.rename(process_input, output_path)
                else:
                    # 复制原文件
                    import shutil
                    shutil.copy2(input_path, output_path)
            
            # 清理临时文件
            if trim_start is not None and trim_end is not None and os.path.exists(temp_trimmed):
                try:
                    os.remove(temp_trimmed)
                except:
                    pass
            
            # 获取处理后的视频信息
            processed_info = FFmpegHelper.get_video_info(output_path)
            
            return output_path, processed_info
        
        except Exception as e:
            # 清理可能的临时文件
            if trim_start is not None and trim_end is not None:
                temp_file = output_path + ".trimmed.mp4"
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            raise Exception(f"处理视频失败: {str(e)}")
