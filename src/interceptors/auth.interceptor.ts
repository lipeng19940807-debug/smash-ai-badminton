import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { BackendApiService } from '../services/backend-api.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

    constructor(
        private backendApi: BackendApiService,
        private router: Router
    ) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // 获取 Token
        const token = this.backendApi.getToken();

        // 如果有 Token 且请求是发往后端 API，则添加 Authorization Header
        if (token && request.url.includes('/api/')) {
            request = request.clone({
                setHeaders: {
                    Authorization: `Bearer ${token}`
                }
            });
        }

        // 处理响应错误
        return next.handle(request).pipe(
            catchError((error: HttpErrorResponse) => {
                if (error.status === 401) {
                    // Token 无效或过期，跳转到登录页
                    this.backendApi.logout();
                    this.router.navigate(['/login']);
                }
                return throwError(() => error);
            })
        );
    }
}
