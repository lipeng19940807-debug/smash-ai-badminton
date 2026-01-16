# 部署指南

## 快速部署步骤

### 1. 推送到 GitHub

```bash
# 在项目根目录执行

# 如果还没有 GitHub 仓库，先在 GitHub 网站创建一个新仓库
# 然后执行以下命令：

git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 2. 部署前端到 Vercel

#### 方法 1: 使用 Vercel Dashboard（推荐）

1. 访问 https://vercel.com
2. 点击 "Add New" → "Project"
3. 从 GitHub 导入你的仓库
4. Vercel 会自动检测到 Angular 项目
5. 点击 "Deploy"

#### 方法 2: 使用 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### 3. 配置环境变量（如果需要）

在 Vercel Dashboard 中设置：
- `API_URL`: 后端 API 地址（部署后端后设置）

### 注意事项

- ✅ Vercel 在国内可以访问
- ✅ 免费套餐足够个人项目使用
- ✅ 自动 HTTPS 证书
- ✅ 全球 CDN 加速

### 后端部署（稍后）

后端需要部署到支持 Python 的服务器：
- Railway.app
- Render.com
- 国内: 腾讯云、阿里云

详见 `china_deployment.md` 了解国内部署方案。
