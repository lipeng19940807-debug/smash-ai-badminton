"""
AI 分析服务
调用 Gemini API 分析视频
"""
import base64
import time
import json
from typing import Optional
from fastapi import HTTPException, status
from supabase import Client
import google.generativeai as genai
from app.config import settings


class AnalysisService:
    """AI 分析服务类"""
    
    def __init__(self, db: Client):
        self.db = db
        # 配置 Gemini API
        genai.configure(api_key=settings.gemini_api_key)
    
    async def analyze_video(self, video_id: str, user_id: str) -> dict:
        """
        分析视频并返回结果
        
        Args:
            video_id: 视频ID
            user_id: 用户ID
        
        Returns:
            分析结果字典
        """
        start_time = time.time()
        
        # 1. 获取视频信息
        try:
            video_response = self.db.table("videos").select("*").eq("id", video_id).eq("user_id", user_id).execute()
            
            if not video_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="视频不存在"
                )
            
            video = video_response.data[0]
            video_path = video["file_path"]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取视频信息失败: {str(e)}"
            )
        
        # 2. 上传视频文件到 Gemini
        try:
            video_file = genai.upload_file(path=video_path)
            print(f"上传视频文件: {video_file.uri}")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"上传视频到 Gemini 失败: {str(e)}"
            )
        
        # 3. 构建 Prompt
        prompt = """
你是一位世界顶级的羽毛球科研专家和运动生物力学分析师。请对上传的视频进行极高精度的量化分析，结果必须严谨且经得住推敲。

请执行以下思维过程来确保准确性：
1. **视觉测距与物理建模**：
   - 仔细观察视频中的环境参照物（标准羽毛球场长13.40米，宽6.10米，网高1.55米）。
   - 估算羽毛球从击球点到落地点的飞行距离。
   - 计算飞行时间，从而推算平均速度和初速度。
2. **动作生物力学诊断**：
   - 逐帧分析"鞭打动作"：检查力量是否从蹬地 -> 转髋 -> 展胸 -> 大臂 -> 小臂 -> 手腕 -> 手指顺畅传递。
   - 观察击球点高度：是否在人体中轴线的前上方最高点。
3. **数据合理性校验**：
   - 业余初级：< 150 km/h
   - 业余中高级：150 - 250 km/h
   - 职业级：> 250 km/h
   - 请根据视频中选手的动作流畅度和爆发力，给出符合物理常识的速度估算。

请以 JSON 格式返回分析结果，包含以下字段（所有文本使用简体中文）：
{
  "speed": 整数(km/h),
  "rank": 百分位排名(0-100),
  "rank_position": 前X%,
  "level": "技术等级",
  "technique": {
    "power": 发力评分(0-100),
    "angle": 角度评分(0-100),
    "coordination": 协调性评分(0-100)
  },
  "score": 综合评分(0-10),
  "suggestions": [
    {
      "title": "建议标题",
      "desc": "详细建议",
      "icon": "Material图标名",
      "highlight": "关键数据"
    }
  ]
}
"""
        
        # 4. 调用 Gemini API
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                [video_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            # 解析结果
            result = json.loads(response.text)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI 分析失败: {str(e)}"
            )
        finally:
            # 清理上传的文件
            try:
                genai.delete_file(video_file.name)
            except:
                pass
        
        # 5. 保存分析结果到数据库
        analysis_duration = time.time() - start_time
        
        analysis_data = {
            "user_id": user_id,
            "video_id": video_id,
            "speed": result["speed"],
            "level": result["level"],
            "score": result["score"],
            "technique_power": result["technique"]["power"],
            "technique_angle": result["technique"]["angle"],
            "technique_coordination": result["technique"]["coordination"],
            "rank": result.get("rank"),
            "rank_position": result.get("rank_position"),
            "suggestions": result["suggestions"],
            "analysis_duration": analysis_duration
        }
        
        try:
            db_response = self.db.table("analyses").insert(analysis_data).execute()
            if not db_response.data:
                raise Exception("数据库插入失败")
            
            analysis_record = db_response.data[0]
            
            return {
                "id": analysis_record["id"],
                "video_id": video_id,
                "speed": analysis_record["speed"],
                "level": analysis_record["level"],
                "score": analysis_record["score"],
                "technique": {
                    "power": analysis_record["technique_power"],
                    "angle": analysis_record["technique_angle"],
                    "coordination": analysis_record["technique_coordination"]
                },
                "rank": analysis_record.get("rank"),
                "rank_position": analysis_record.get("rank_position"),
                "suggestions": analysis_record["suggestions"],
                "analyzed_at": analysis_record["analyzed_at"]
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"保存分析结果失败: {str(e)}"
            )
    
    async def get_analysis(self, analysis_id: str, user_id: str) -> dict:
        """
        获取分析结果
        
        Args:
            analysis_id: 分析ID
            user_id: 用户ID
        
        Returns:
            分析结果字典
        """
        try:
            response = self.db.table("analyses").select("*").eq("id", analysis_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="分析记录不存在"
                )
            
            record = response.data[0]
            
            return {
                "id": record["id"],
                "video_id": record["video_id"],
                "speed": record["speed"],
                "level": record["level"],
                "score": record["score"],
                "technique": {
                    "power": record["technique_power"],
                    "angle": record["technique_angle"],
                    "coordination": record["technique_coordination"]
                },
                "rank": record.get("rank"),
                "rank_position": record.get("rank_position"),
                "suggestions": record["suggestions"],
                "analyzed_at": record["analyzed_at"]
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取分析结果失败: {str(e)}"
            )
