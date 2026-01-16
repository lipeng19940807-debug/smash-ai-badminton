# 羽毛球杀球分析 - 后端 API

使用 FastAPI + Supabase + Gemini AI 构建的羽毛球杀球视频分析后端服务。

## 功能特性

- ✅ **用户认证**: JWT Token 认证，支持注册和登录
- ✅ **视频上传**: 支持多种格式，自动压缩和裁剪
- ✅ **AI 分析**: 使用 Gemini 2.0 Flash 分析杀球速度和技术
- ✅ **历史记录**: 保存和查询分析历史
- ✅ **缩略图**: 自动生成视频缩略图

## 技术栈

- **Web框架**: FastAPI 0.115+
- **数据库**: Supabase (PostgreSQL)
- **视频处理**: FFmpeg
- **AI服务**: Google Gemini 2.0 Flash API
- **认证**: JWT (python-jose)
- **密码加密**: Bcrypt (passlib)

## 快速开始

### 1. 环境要求

- Python 3.8+
- FFmpeg (视频处理)
- Supabase 账号和项目

### 2. 安装 FFmpeg

**Mac:**
```bash
brew install ffmpeg
```

**Windows:**
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)，添加到系统 PATH

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入真实配置
# - SUPABASE_URL: 你的 Supabase 项目 URL
# - SUPABASE_KEY: Supabase Anon Key
# - GEMINI_API_KEY: Google Gemini API Key
# - SECRET_KEY: JWT 密钥（使用 openssl rand -hex 32 生成）
```

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

> **注意**: 脚本会输出 SQL 语句，你需要在 Supabase Dashboard 的 SQL Editor 中手动执行这些语句以创建表。

### 6. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:8000` 启动

### 7. 访问 API 文档

打开浏览器访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

### 视频相关

- `POST /api/video/upload` - 上传视频
- `GET /api/video/{video_id}` - 获取视频信息

### 分析相关

- `POST /api/analysis/start` - 开始分析视频
- `GET /api/analysis/{analysis_id}` - 获取分析结果

### 历史记录

- `GET /api/history` - 获取历史记录列表
- `GET /api/history/{analysis_id}/detail` - 获取历史记录详情

## 项目结构

```
backend/
├── app/
│   ├── main.py                # FastAPI 应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── dependencies.py        # 依赖注入
│   ├── models/                # 数据模型
│   ├── schemas/               # API 响应模式
│   ├── services/              # 业务逻辑
│   ├── routers/               # API 路由
│   └── utils/                 # 工具函数
├── scripts/                   # 脚本
├── uploads/                   # 上传文件存储
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量示例
└── run.py                     # 启动脚本
```

## 开发说明

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black app/
```

### 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| SUPABASE_URL | Supabase 项目 URL | https://xxxxx.supabase.co |
| SUPABASE_KEY | Supabase Anon Key | eyJhbGciOiJ... |
| GEMINI_API_KEY | Gemini API Key | AIzaSy... |
| SECRET_KEY | JWT 密钥 | 随机32字节十六进制字符串 |
| HOST | 服务器地址 | 0.0.0.0 |
| PORT | 服务器端口 | 8000 |
| MAX_VIDEO_SIZE_MB | 最大视频大小(MB) | 50 |
| MAX_VIDEO_DURATION_SECONDS | 最大视频时长(秒) | 10 |

## 常见问题

### 1. FFmpeg 找不到

**错误**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**解决**: 确保 FFmpeg 已正确安装并添加到系统 PATH

### 2. Supabase 连接失败

**错误**: `Database connection failed`

**解决**: 检查 `.env` 文件中的 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确

### 3. Gemini API 调用失败

**错误**: `Gemini API call failed`

**解决**:
- 检查 `GEMINI_API_KEY` 是否正确
- 确认 API Key 有足够的配额
- 检查网络连接

### 4. CORS 错误

**错误**: `Access-Control-Allow-Origin`

**解决**: 在 `.env` 中添加前端地址到 `ALLOWED_ORIGINS`

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发者。
