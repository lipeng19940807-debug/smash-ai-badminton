import { Component, ChangeDetectionStrategy, signal, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { BackendApiService } from '../../services/backend-api.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [FormsModule],
    template: `
    <div class="flex flex-col min-h-screen bg-background-dark text-white overflow-x-hidden max-w-[480px] mx-auto">
      <!-- Header -->
      <div class="flex items-center p-4 justify-between sticky top-0 z-50 bg-background-dark border-b border-white/10">
        <div (click)="goBack()" class="text-white flex size-10 shrink-0 items-center justify-center cursor-pointer hover:bg-white/5 rounded-full">
          <span class="material-symbols-outlined">arrow_back_ios</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight flex-1 text-center">注册</h2>
        <div class="w-10"></div>
      </div>

      <div class="flex-1 flex flex-col justify-center px-6 py-12">
        <!-- Error Message -->
        @if (errorMessage()) {
          <div class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
            <p class="text-red-400 text-sm">{{ errorMessage() }}</p>
          </div>
        }

        <!-- Register Form -->
        <div class="space-y-6">
          <div>
            <label class="block text-white/60 text-sm mb-2">用户名</label>
            <input 
              type="text" 
              [(ngModel)]="username"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-primary"
              placeholder="请输入用户名（3-50字符）"
            />
          </div>

          <div>
            <label class="block text-white/60 text-sm mb-2">昵称（可选）</label>
            <input 
              type="text" 
              [(ngModel)]="nickname"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-primary"
              placeholder="请输入昵称"
            />
          </div>

          <div>
            <label class="block text-white/60 text-sm mb-2">密码</label>
            <input 
              type="password" 
              [(ngModel)]="password"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-primary"
              placeholder="请输入密码（至少6字符）"
            />
          </div>

          <div>
            <label class="block text-white/60 text-sm mb-2">确认密码</label>
            <input 
              type="password" 
              [(ngModel)]="confirmPassword"
              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-primary"
              placeholder="请再次输入密码"
            />
          </div>

          <button 
            (click)="onRegister()" 
            [disabled]="loading()"
            class="w-full bg-primary text-background-dark font-bold text-lg h-14 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-primary/20 hover:bg-[#149cc9] disabled:opacity-50"
          >
            @if (loading()) {
              <span class="material-symbols-outlined animate-spin">progress_activity</span>
              注册中...
            } @else {
              注册
            }
          </button>

          <div class="text-center">
            <span class="text-white/60 text-sm">已有账号？</span>
            <button (click)="goToLogin()" class="text-primary font-bold text-sm ml-2">立即登录</button>
          </div>
        </div>
      </div>
    </div>
  `,
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class RegisterComponent {
    router = inject(Router);
    backendApi = inject(BackendApiService);

    username = '';
    nickname = '';
    password = '';
    confirmPassword = '';
    loading = signal(false);
    errorMessage = signal<string | null>(null);

    goBack() {
        this.router.navigate(['/login']);
    }

    goToLogin() {
        this.router.navigate(['/login']);
    }

    onRegister() {
        this.errorMessage.set(null);

        // 验证
        if (!this.username || !this.password) {
            this.errorMessage.set('请填写用户名和密码');
            return;
        }

        if (this.username.length < 3) {
            this.errorMessage.set('用户名至少3个字符');
            return;
        }

        if (this.password.length < 6) {
            this.errorMessage.set('密码至少6个字符');
            return;
        }

        if (this.password !== this.confirmPassword) {
            this.errorMessage.set('两次输入的密码不一致');
            return;
        }

        this.loading.set(true);

        this.backendApi.register({
            username: this.username,
            password: this.password,
            nickname: this.nickname || undefined
        }).subscribe({
            next: () => {
                // 注册成功，自动登录并跳转
                this.router.navigate(['/dashboard']);
            },
            error: (error) => {
                this.loading.set(false);
                this.errorMessage.set(error.error?.detail || '注册失败，请重试');
            }
        });
    }
}
