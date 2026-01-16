import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { BackendApiService } from '../services/backend-api.service';

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate {

    constructor(
        private backendApi: BackendApiService,
        private router: Router
    ) { }

    canActivate(): boolean {
        if (this.backendApi.isLoggedIn()) {
            return true;
        } else {
            // 未登录，重定向到登录页
            this.router.navigate(['/login']);
            return false;
        }
    }
}
