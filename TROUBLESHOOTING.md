# 故障排查指南

## 常见问题及解决方法

### 1. 网络连接错误 (ERR_CONNECTION_RESET / ERR_CONNECTION_REFUSED)

**症状：**
- 小程序显示"网络错误"
- 控制台显示 `ERR_CONNECTION_RESET` 或 `ERR_CONNECTION_REFUSED`

**解决方法：**

1. **检查后端服务是否运行**
   ```bash
   curl http://localhost:8000/health
   ```
   如果返回 `{"status":"healthy"}`，说明服务正常

2. **检查 IP 地址配置**
   - 确认本机 IP：`ifconfig | grep "inet "`
   - 确认小程序 `utils/config.js` 中的 `BASE_URL` 使用正确的 IP
   - 例如：`http://192.168.31.54:8000/api`

3. **微信开发者工具设置**
   - 打开微信开发者工具
   - 工具栏 -> 详情 -> 本地设置
   - ✅ 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"

4. **重启后端服务**
   ```bash
   cd backend
   python3 run.py
   ```

### 2. 分析接口 500 错误

**症状：**
- 上传视频后，分析失败
- 返回 500 Internal Server Error

**解决方法：**

1. **查看后端日志**
   ```bash
   tail -f /tmp/backend_new.log
   ```

2. **检查 Gemini API 配置**
   - 确认 `.env` 文件中有 `GEMINI_API_KEY`
   - 确认 API key 有效

3. **检查 FFmpeg 是否安装**
   ```bash
   ffmpeg -version
   ffprobe -version
   ```
   如果未安装，参考 `backend/FFMPEG_INSTALL.md`

### 3. 图片加载失败

**症状：**
- 缩略图显示失败
- 返回 500 错误

**解决方法：**

1. **检查静态文件服务**
   - 确认后端服务正常运行
   - 确认 `backend/uploads/thumbnails/` 目录存在
   - 确认文件权限正确

2. **检查 URL 路径**
   - 缩略图 URL 应该是：`http://192.168.31.54:8000/uploads/thumbnails/xxx.jpg`
   - 不是：`/pages/index/uploads/thumbnails/xxx.jpg`

### 4. 渲染失败

**症状：**
- 页面显示"渲染失败"
- 控制台显示渲染层错误

**解决方法：**

1. **清除缓存**
   - 微信开发者工具 -> 清除缓存 -> 清除所有缓存

2. **重新编译**
   - 点击"编译"按钮重新编译小程序

3. **检查数据格式**
   - 确认数据格式正确
   - 检查是否有 null 或 undefined 值

## 快速检查清单

- [ ] 后端服务运行中 (`curl http://localhost:8000/health`)
- [ ] IP 地址配置正确 (`utils/config.js`)
- [ ] 微信开发者工具勾选了"不校验合法域名"
- [ ] FFmpeg 已安装 (`ffmpeg -version`)
- [ ] Gemini API Key 已配置 (`.env` 文件)
- [ ] 网络连接正常

## 获取帮助

如果问题仍然存在，请提供：
1. 后端日志：`tail -50 /tmp/backend_new.log`
2. 小程序控制台错误信息
3. 具体的错误步骤
