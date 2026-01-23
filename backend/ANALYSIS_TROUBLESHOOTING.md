# 分析功能故障排查指南

## 问题：上传视频后分析失败（500错误）

### 可能的原因和解决方法

#### 1. Gemini API 配置问题

**检查项：**
- 确认 `.env` 文件中已配置 `GEMINI_API_KEY`
- 确认 API key 有效且未过期

**解决方法：**
```bash
# 检查配置
cd backend
grep GEMINI_API_KEY .env

# 如果未配置，添加：
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

#### 2. 视频文件路径问题

**检查项：**
- 视频文件是否成功上传到服务器
- 文件路径是否正确

**解决方法：**
- 检查 `backend/uploads/processed/` 目录
- 确认文件权限正确

#### 3. Gemini API 配额限制

**检查项：**
- API 使用量是否超限
- 是否有足够的配额

**解决方法：**
- 访问 Google Cloud Console 检查配额
- 等待配额重置或升级计划

#### 4. 网络连接问题

**检查项：**
- 服务器是否能访问 Gemini API
- 防火墙设置

**解决方法：**
```bash
# 测试网络连接
curl https://generativelanguage.googleapis.com
```

### 查看详细错误日志

**方法1：查看后端日志**
```bash
tail -f /tmp/backend_new.log
```

**方法2：查看实时错误**
在微信开发者工具的 Network 标签中查看响应详情

### 常见错误信息

1. **"Gemini API 密钥配置错误"**
   - 解决：检查 `.env` 文件中的 `GEMINI_API_KEY`

2. **"视频文件不存在"**
   - 解决：检查视频上传是否成功

3. **"AI 返回结果解析失败"**
   - 解决：可能是 Gemini API 返回格式异常，检查日志

4. **"Gemini API 配额已用完"**
   - 解决：等待配额重置或升级 API 计划

### 测试分析接口

使用 curl 测试：
```bash
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"video_id": "your_video_id"}'
```

### 联系支持

如果问题仍然存在，请提供：
1. 后端日志（`/tmp/backend_new.log`）
2. 错误响应详情
3. 视频文件信息
