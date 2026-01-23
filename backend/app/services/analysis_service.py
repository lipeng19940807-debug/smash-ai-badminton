"""
AI 分析服务
调用 Gemini API 分析视频
"""
import base64
import time
import json
import re
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
        
        # 2. 检查视频文件是否存在
        import os
        if not os.path.exists(video_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"视频文件不存在: {video_path}"
            )
        
        # 3. 上传视频文件到 Gemini
        try:
            print(f"开始上传视频文件到 Gemini: {video_path}")
            video_file = genai.upload_file(path=video_path)
            print(f"视频文件上传成功: {video_file.uri}, 状态: {video_file.state}")
            
            # 等待文件处理完成（状态变为 ACTIVE）
            max_wait_time = 60  # 最多等待60秒
            wait_interval = 2   # 每2秒检查一次
            waited_time = 0
            
            while video_file.state.name != "ACTIVE" and waited_time < max_wait_time:
                print(f"等待文件处理完成，当前状态: {video_file.state.name}, 已等待: {waited_time}秒")
                time.sleep(wait_interval)
                waited_time += wait_interval
                # 重新获取文件状态
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name != "ACTIVE":
                raise Exception(f"文件处理超时，状态: {video_file.state.name}")
            
            print(f"文件已就绪，状态: {video_file.state.name}")
            
        except Exception as e:
            error_msg = str(e)
            # 提供更详细的错误信息
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = "Gemini API 密钥配置错误，请检查 .env 文件中的 GEMINI_API_KEY"
            elif "file" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = f"视频文件不存在或无法访问: {video_path}"
            elif "not in an ACTIVE state" in error_msg:
                error_msg = "视频文件处理未完成，请稍后重试"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"上传视频到 Gemini 失败: {error_msg}"
            )
        
        # 4. 构建 Prompt
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
        
        # 5. 调用 Gemini API
        try:
            print(f"开始调用 Gemini API，模型: gemini-2.0-flash-exp")
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print(f"模型创建成功，开始生成内容...")
            
            response = model.generate_content(
                [video_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            print(f"Gemini API 调用成功，响应类型: {type(response)}")
            
            # 解析结果
            if not hasattr(response, 'text') or not response.text:
                print(f"错误: AI 返回结果为空，response: {response}")
                raise Exception("AI 返回结果为空")
            
            print(f"AI 返回文本长度: {len(response.text)}")
            print(f"AI 返回文本前200字符: {response.text[:200]}")
            
            result = json.loads(response.text)
            print(f"JSON 解析成功，结果: {result}")
            
            # 验证结果格式
            if "speed" not in result:
                print(f"错误: 结果中缺少 speed 字段，完整结果: {result}")
                raise Exception("AI 返回结果格式不正确，缺少 speed 字段")
            
        except json.JSONDecodeError as e:
            error_detail = f"AI 返回结果解析失败: {str(e)}"
            if hasattr(response, 'text'):
                error_detail += f"。原始响应: {response.text[:500]}"
            print(f"JSON 解析错误: {error_detail}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"Gemini API 调用异常: {error_msg}")
            print(f"错误堆栈: {error_trace}")
            
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = "Gemini API 密钥配置错误，请检查 .env 文件中的 GEMINI_API_KEY"
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_msg = "Gemini API 配额已用完，请检查 API 使用限制"
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = "Gemini 模型不可用，请检查模型名称是否正确"
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI 分析失败: {error_msg}"
            )
        finally:
            # 清理上传的文件
            try:
                genai.delete_file(video_file.name)
            except:
                pass
        
        # 6. 扣除积分（每次分析消耗 10 积分）
        # 注意：如果数据库表没有积分字段，跳过积分扣除
        points_cost = 10
        points_deducted = False
        
        try:
            # 先检查数据库表是否有积分字段
            test_query = self.db.table("users").select("points").limit(1).execute()
            has_points_field = True
        except Exception:
            # 积分字段不存在，跳过积分扣除
            print("数据库表没有积分字段，跳过积分扣除")
            has_points_field = False
        
        if has_points_field:
            try:
                from app.services.points_service import PointsService
                points_service = PointsService(self.db)
                
                # 检查积分是否足够
                user_points = await points_service.get_user_points(user_id)
                if user_points.get("points", 0) < points_cost:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"积分不足，当前余额: {user_points.get('points', 0)}，需要: {points_cost}"
                    )
                
                # 扣除积分
                await points_service.adjust_points(
                    user_id=user_id,
                    points=-points_cost,
                    transaction_type="spend",
                    description="视频分析消耗",
                    related_type="analysis"
                )
                points_deducted = True
                print(f"成功扣除积分: {points_cost}，用户ID: {user_id}")
            except HTTPException:
                raise
            except Exception as e:
                print(f"扣除积分失败（可能积分系统未配置）: {str(e)}")
                # 积分扣除失败不影响分析结果保存，但记录错误
                points_deducted = False
        else:
            print("积分系统未启用，跳过积分扣除")
        
        # 7. 保存分析结果到数据库
        analysis_duration = time.time() - start_time
        
        # 处理 rank_position：如果是字符串（如"前25%"），提取数字部分
        rank_position = result.get("rank_position")
        if isinstance(rank_position, str):
            # 尝试从字符串中提取数字，例如 "前25%" -> 25
            match = re.search(r'\d+', rank_position)
            if match:
                rank_position = int(match.group())
            else:
                rank_position = None
        
        # 确保所有必需字段都存在
        analysis_data = {
            "user_id": user_id,
            "video_id": video_id,
            "speed": int(result["speed"]),
            "level": str(result["level"]),
            "score": float(result["score"]),
            "technique_power": int(result["technique"]["power"]),
            "technique_angle": int(result["technique"]["angle"]),
            "technique_coordination": int(result["technique"]["coordination"]),
            "rank": int(result.get("rank")) if result.get("rank") is not None else None,
            "rank_position": rank_position,  # 已经是处理后的整数或 None
            "suggestions": result["suggestions"],
            "analysis_duration": float(analysis_duration)
        }
        
        # 只有在积分字段存在且已扣除积分时才添加 points_cost
        # 注意：如果数据库表没有 points_cost 字段，Supabase 会自动忽略该字段
        # 但为了安全，我们只在确认积分系统已启用时才添加
        if has_points_field and points_deducted:
            try:
                # 尝试添加 points_cost 字段
                analysis_data["points_cost"] = points_cost
            except Exception:
                # 如果字段不存在，不添加（Supabase 会自动处理）
                pass
        
        try:
            print(f"准备保存分析结果到数据库")
            print(f"数据: user_id={user_id}, video_id={video_id}, speed={analysis_data['speed']}, level={analysis_data['level']}")
            db_response = self.db.table("analyses").insert(analysis_data).execute()
            if not db_response.data:
                print(f"数据库插入失败: 响应为空")
                raise Exception("数据库插入失败")
            
            analysis_record = db_response.data[0]
            print(f"分析结果保存成功: ID={analysis_record.get('id')}")
            
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
            import traceback
            error_trace = traceback.format_exc()
            print(f"保存分析结果到数据库失败: {str(e)}")
            print(f"错误堆栈: {error_trace}")
            print(f"尝试插入的数据: {analysis_data}")
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
