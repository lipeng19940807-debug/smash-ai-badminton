# 修复总结

## 已修复的问题

### 1. ✅ FFmpeg/ffprobe 未安装导致的视频上传错误

**问题：** 上传视频时报错 `[Errno 2] No such file or directory: 'ffprobe'`

**修复：**
- 在 `backend/app/utils/ffmpeg_helper.py` 中添加了 `_check_ffmpeg_installed()` 方法
- 在所有 FFmpeg 操作前检查 FFmpeg 是否安装
- 提供清晰的错误提示和安装指南
- 创建了 `backend/FFMPEG_INSTALL.md` 安装文档

**下一步：** 需要安装 FFmpeg（参考 `backend/FFMPEG_INSTALL.md`）

### 2. ✅ 登录失败（500/401错误）

**问题：** 自动登录失败，导致页面报错

**修复：**
- 修改 `app.js` 中的 `onLaunch`，不再自动尝试登录
- 优化了 token 验证的错误处理
- 改进了登录页面的错误提示
- 确保所有 `showLoading` 都有对应的 `hideLoading`

### 3. ✅ 图片加载失败

**问题：** 静态资源 `/static/default-avatar.png` 加载失败（500错误）

**修复：**
- 移除了不存在的静态资源路径
- 添加了图片加载错误处理 `handleImageError`
- 当头像 URL 为空时，不显示图片（避免加载错误）

### 4. ✅ showLoading/hideLoading 不配对

**问题：** 控制台警告 `showLoading 与 hideLoading 必须配对使用`

**修复：**
- 检查了所有使用 `showLoading` 的地方
- 确保所有 `showLoading` 都有对应的 `hideLoading`
- 在错误处理中也添加了 `hideLoading`

## 需要手动操作的事项

### 1. 安装 FFmpeg（必需）

视频上传功能需要 FFmpeg。请按照 `backend/FFMPEG_INSTALL.md` 中的说明安装。

**macOS 快速安装：**
```bash
brew install ffmpeg
```

**验证安装：**
```bash
ffmpeg -version
ffprobe -version
```

### 2. 配置微信小程序（可选）

如果需要使用微信一键登录功能，需要在 `backend/.env` 文件中配置：
```
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

如果不配置，微信登录会失败，但可以使用账号密码登录。

## 测试步骤

1. **重启后端服务：**
   ```bash
   cd backend
   python3 run.py
   ```

2. **在微信开发者工具中重新编译小程序**

3. **测试登录：**
   - 点击"立即登录"
   - 注册新账号或使用已有账号登录

4. **测试视频上传（需要先安装 FFmpeg）：**
   - 登录后点击"开始分析杀球"
   - 选择视频文件
   - 如果 FFmpeg 未安装，会显示清晰的错误提示

## 已知问题

1. **FFmpeg 未安装** - 需要手动安装（见上方）
2. **微信登录配置** - 需要配置 AppID 和 AppSecret（可选）

## 后续优化建议

1. 添加视频预览功能
2. 优化错误提示的用户体验
3. 添加加载动画
4. 优化图片加载（使用占位图）
