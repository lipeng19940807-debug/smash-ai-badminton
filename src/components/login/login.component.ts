import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';

@Component({
  selector: 'app-login',
  standalone: true,
  template: `
    <div class="relative flex min-h-screen w-full flex-col overflow-x-hidden max-w-md mx-auto">
      <div class="flex items-center p-4 pb-2 justify-between">
        <div class="text-white flex size-12 shrink-0 items-center cursor-pointer">
          <span class="material-symbols-outlined text-white text-2xl">arrow_back_ios_new</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight flex-1 text-center pr-12 font-display">SmashAI</h2>
      </div>

      <div class="@container">
        <div class="px-4 py-3">
          <div class="w-full bg-center bg-no-repeat bg-cover flex flex-col justify-center items-center overflow-hidden bg-background-dark rounded-xl min-h-[180px] relative" 
               style="background-image: linear-gradient(to bottom, rgba(16, 29, 34, 0.4), rgba(16, 29, 34, 1)), url('https://lh3.googleusercontent.com/aida-public/AB6AXuBJPCPXO7tkSsvN6SQtfnKNWjMinrEujFwMx5_SQsT7jcoHx5YoCv3i_rs9f5MiGisEvB65PCB2lq0_KB1zARDjeNa14R0ad9w9Ti7GaFs0ZMsISq35Q8v-8m4bHC5SdYkFzWwsZBLLWvlzh_stEKQVPT6IKQs4u9Z3c-gRFjmCYgkgRNsS0pm74GirYnI__1vZUJexFCou8hVsK8Pt5LgVNKafhAy5cpTVLqWl2WjqhOnmxoK69E7qLXFyVOTbwrLGJuotaBQDIHjn');">
            <div class="bg-primary/20 p-4 rounded-full mb-2 backdrop-blur-sm border border-primary/10">
              <span class="material-symbols-outlined text-primary text-5xl">bolt</span>
            </div>
          </div>
        </div>
      </div>

      <h1 class="text-white tracking-tight text-[32px] font-bold leading-tight px-6 text-center pb-2 pt-4 font-display">
        提升你的扣杀
      </h1>
      <p class="text-slate-400 text-center px-8 pb-6 text-sm">利用 AI 技术追踪羽毛球球速与挥拍技巧</p>

      <div class="flex px-6 py-3">
        <div class="flex h-12 flex-1 items-center justify-center rounded-full bg-[#192d34] p-1 border border-[#325a67]/30">
          <button (click)="setMode('signup')" 
            class="flex-1 h-full rounded-full text-sm font-semibold transition-all duration-300"
            [class]="mode() === 'signup' ? 'bg-primary shadow-lg text-white' : 'text-slate-400 hover:text-white'">
            注册
          </button>
          <button (click)="setMode('login')"
             class="flex-1 h-full rounded-full text-sm font-semibold transition-all duration-300"
            [class]="mode() === 'login' ? 'bg-primary shadow-lg text-white' : 'text-slate-400 hover:text-white'">
            登录
          </button>
        </div>
      </div>

      <div class="flex flex-col gap-4 px-6 pt-4">
        <label class="flex flex-col gap-2">
          <span class="text-white text-sm font-medium px-1">用户昵称</span>
          <div class="relative">
            <input 
              [value]="smashService.userName()"
              (input)="onNameChange($event)"
              class="w-full rounded-full text-white bg-[#192d34] border border-[#325a67] focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none h-14 pl-6 pr-12 text-base transition-all placeholder:text-slate-500" 
              placeholder="起一个响亮的名字" 
              type="text" />
            <span class="material-symbols-outlined absolute right-5 top-4 text-slate-500">person</span>
          </div>
        </label>

        <label class="flex flex-col gap-2">
          <span class="text-white text-sm font-medium px-1">电子邮箱</span>
          <div class="relative">
            <input class="w-full rounded-full text-white bg-[#192d34] border border-[#325a67] focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none h-14 pl-6 pr-12 text-base transition-all placeholder:text-slate-500" placeholder="example@email.com" type="email" />
            <span class="material-symbols-outlined absolute right-5 top-4 text-slate-500">mail</span>
          </div>
        </label>

        <label class="flex flex-col gap-2">
          <span class="text-white text-sm font-medium px-1">密码</span>
          <div class="relative">
            <input class="w-full rounded-full text-white bg-[#192d34] border border-[#325a67] focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none h-14 pl-6 pr-12 text-base transition-all placeholder:text-slate-500" placeholder="••••••••" type="password" />
            <span class="material-symbols-outlined absolute right-5 top-4 text-slate-500">visibility_off</span>
          </div>
        </label>
      </div>

      <div class="px-6 pt-8 pb-4 mt-auto">
        <button (click)="goDashboard()" class="w-full bg-primary hover:bg-[#149cc9] text-white font-bold py-4 rounded-full text-lg shadow-[0_8px_20px_rgba(25,186,240,0.3)] active:scale-[0.98] transition-all flex items-center justify-center gap-2">
          <span>立即开启挑战</span>
          <span class="material-symbols-outlined">sports_tennis</span>
        </button>
      </div>
      <div class="h-6"></div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class LoginComponent {
  router = inject(Router);
  smashService = inject(SmashService);
  mode = signal<'login' | 'signup'>('signup');

  setMode(m: 'login' | 'signup') {
    this.mode.set(m);
  }

  onNameChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.smashService.userName.set(input.value);
  }

  goDashboard() {
    this.router.navigate(['/dashboard']);
  }
}