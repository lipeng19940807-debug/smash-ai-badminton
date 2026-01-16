# 前端集成说明

## 已创建的文件

### 核心服务
- `src/services/backend-api.service.ts` ✅ - 后端 API 封装
- `src/interceptors/auth.interceptor.ts` ✅ - JWT 拦截器
- `src/guards/auth.guard.ts` ✅ - 路由守卫

### 组件
- `src/components/register/register.component.ts` ✅ - 注册组件

## 需要修改的现有文件

### 1. app.component.ts - 添加 HTTP 拦截器

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ]
};
```

### 2. app.routes.ts - 添加路由和守卫

```typescript
import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { 
    path: 'login', 
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  { 
    path: 'register', 
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  { 
    path: 'dashboard', 
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]  // 需要登录
  },
  { 
    path: 'upload', 
    loadComponent: () => import('./components/upload/upload.component').then(m => m.UploadComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'analysis', 
    loadComponent: () => import('./components/analysis/analysis.component').then(m => m.AnalysisComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'report', 
    loadComponent: () => import('./components/report/report.component').then(m => m.ReportComponent),
    canActivate: [AuthGuard]
  },
  { 
    path: 'share', 
    loadComponent: () => import('./components/share/share.component').then(m => m.ShareComponent),
    canActivate: [AuthGuard]
  },
];
```

### 3. smash.service.ts - 改用后端 API

需要修改以下方法：
- `analyzeSmash()` - 改为调用后端上传视频并分析
- `uploadedFile` 和 `uploadedVideoUrl` - 改为通过后端上传

### 4. upload.component.ts - 使用后端上传

```typescript
import { BackendApiService } from '../../services/backend-api.service';

// 注入服务
backendApi = inject(BackendApiService);

async onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const file = input.files[0];
    
    // 上传到后端
    this.backendApi.uploadVideo(file, this.trimStart(), this.trimEnd()).subscribe({
      next: (response) => {
        // 保存视频 ID
        this.uploadedVideoId = response.id;
        this.uploadedVideoUrl.set(URL.createObjectURL(file));
      },
      error: (error) => {
        console.error('上传失败', error);
      }
    });
  }
}
```

### 5. analysis.component.ts - 调用后端分析

```typescript
import { BackendApiService } from '../../services/backend-api.service';

backendApi = inject(BackendApiService);

async start Analysis() {
  try {
    const result = await this.backendApi.startAnalysis(this.videoId).toPromise();
    this.smashService.currentResult.set(result);
    this.router.navigate(['/report']);
  } catch (e) {
    this.error.set(e.message);
  }
}
```

## 部署到 Vercel

1. 在项目根目录创建 `vercel.json`:

```json
{
  "version": 2,
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

2. 部署:

```bash
npm install -g vercel
vercel --prod
```

## 环境变量

创建 `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend.com/api'
};
```

## 中国大陆用户

请参阅 `china_deployment.md` 了解完整的国内部署方案。
