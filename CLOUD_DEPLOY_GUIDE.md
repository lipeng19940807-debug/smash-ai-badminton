# 微信云开发集成说明 (Cloud Development Integration)

本项目已完成与微信云开发（WeChat Cloud Development）的深度打通。通过 **微信云托管 (Cloud Run)**，你可以实现免运维部署、自动伸缩，并利用云开发的原生认证与存储能力。

## 已完成的打通工作

### 1. 认证打通 (Authentication)
- **OpenID 自动识别**：后端已集成对微信云托管注入的 `X-WX-OPENID` 请求头的支持。
- **静默登录**：小程序端现支持静默登录，无需用户手动点击，即可通过云托管识别身份。

### 2. 存储打通 (Storage)
- **云存储直传**：小程序端改为直接上传视频到 **微信云存储**，大幅提升上传速度并减轻后端带宽压力。
- **后端自动同步**：后端新增 `/api/video/cloud-upload` 接口，利用微信内网 API 自动将云存储文件同步至处理引擎。

### 3. 部署打通 (Deployment)
- **Dockerfile**：已为后端添加生产级 Docker 配置，支持 FFmpeg 环境。
- **请求适配**：小程序端 `request.js` 已重构，支持通过 `wx.cloud.callContainer` 调用云托管服务。

## 如何部署到微信云托管

### 第一步：开启云托管
1. 登录 [微信对话开放平台/小程序管理后台](https://mp.weixin.qq.com/)。
2. 进入 **云开发** -> **云托管**。
3. 创建新环境（如环境 ID：`cloud1-1grfk67f82062cc1`）。

### 第二步：创建服务
1. 创建一个名为 `smashai-backend` 的服务。
2. 端口设置为 `80`。

### 第三步：发布代码
1. 将本项目代码推送到你关联的 Git 仓库（GitHub/GitLab/Gitee）。
2. 在云托管控制台选择 **发布** -> **代码库发布**。
3. 路径选择项目根目录，发布系统会自动识别 `backend/Dockerfile`。

### 第四步：环境变量配置
在云托管服务设置中，添加以下环境变量：
- `SUPABASE_URL`: 你的 Supabase URL
- `SUPABASE_KEY`: 你的 Supabase Service Role Key
- `GOOGLE_API_KEY`: 你的 Gemini API Key
- `DEBUG`: `false`

## 接口调用调整
- **小程序调用**：所有请求已自动适配为 `wx.cloud.callContainer`。
- **域名**：云托管部署后，无需配置“合法域名”，微信内网自动打通。

---
**注意**：目前数据库仍保留使用 Supabase (PostgreSQL)，以确保复杂的杀球数据统计和管理页面功能。微信云数据库 (NoSQL) 暂作为扩展能力支持。
