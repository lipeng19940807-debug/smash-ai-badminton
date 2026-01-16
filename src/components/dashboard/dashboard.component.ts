import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  template: `
    <div class="min-h-screen pb-24 bg-background-light dark:bg-background-dark">
      <!-- Top Navigation / Header -->
      <div class="sticky top-0 z-40 flex items-center bg-background-dark/80 backdrop-blur-md p-4 pb-2 justify-between border-b border-white/5">
        <div class="flex items-center gap-3">
          <div class="flex size-10 shrink-0 items-center overflow-hidden rounded-full border-2 border-primary">
            <img [src]="smashService.userAvatar()" class="w-full h-full object-cover" alt="Avatar">
          </div>
          <div>
            <p class="text-[10px] text-slate-400 font-medium uppercase tracking-wider">欢迎回来</p>
            <h2 class="text-white text-base font-bold leading-tight">{{ smashService.userName() }}</h2>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button class="flex size-10 cursor-pointer items-center justify-center rounded-full bg-slate-800 text-white hover:bg-slate-700 transition-colors">
            <span class="material-symbols-outlined text-[24px]">notifications</span>
          </button>
          <button class="flex size-10 cursor-pointer items-center justify-center rounded-full bg-slate-800 text-white hover:bg-slate-700 transition-colors">
            <span class="material-symbols-outlined text-[24px]">settings</span>
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      @if (currentTab() === 'home') {
        <!-- HOME TAB CONTENT -->
        <div class="animate-fade-in">
          <!-- Hero Card -->
          <div class="p-4">
            <div class="bg-cover bg-center flex flex-col items-stretch justify-end rounded-2xl pt-[120px] shadow-2xl overflow-hidden relative group" 
                 style="background-image: linear-gradient(0deg, rgba(10, 18, 22, 0.98) 0%, rgba(10, 18, 22, 0.3) 100%), url('https://lh3.googleusercontent.com/aida-public/AB6AXuDaq4ydYnwmn-wUgoqjzr2qjsNVgx-qy3aKjCj5G30OjOXflbZhZEujpZa0XlYEjBAOTqT6Nv93UiYcitaJrVp3UQwr-Sxm0yroGpmAeCzyPxiZ4cgbJ_Uxw5ctSxjBEUYv_dKMjNm2ET3XFbw3o3w45S8uOR8kUyVCtPwFHVZ6rdFGSfjQ0JwBcZzWoPmk60luteD8q_cNVwFYwQOnkaXweAXmDYyFMQVQukUaU5uIKbjRCihbKyh4Pr2ZK8SDqegYcqavSeJqzGRW');">
              <div class="absolute top-4 right-4 bg-primary/20 backdrop-blur-md border border-primary/30 rounded-full px-3 py-1">
                <p class="text-primary text-[10px] font-black uppercase tracking-[0.1em]">精英级选手</p>
              </div>
              <div class="flex w-full items-end justify-between gap-4 p-6">
                <div class="flex flex-1 flex-col">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-slate-400 text-sm font-medium">全国排名:</span>
                    <span class="text-primary font-bold text-sm">第 452 名</span>
                  </div>
                  <div class="flex items-baseline gap-1">
                    <p class="text-white tracking-tighter text-5xl font-black leading-tight">392</p>
                    <p class="text-xl font-bold text-slate-400">km/h</p>
                  </div>
                  <p class="text-slate-300 text-sm font-medium tracking-wide">个人最佳杀球时速</p>
                </div>
                <button (click)="switchTab('profile')" class="flex min-w-[90px] items-center justify-center rounded-xl h-10 px-4 bg-white/10 backdrop-blur-md border border-white/10 text-white text-xs font-bold hover:bg-white/20 transition-all">
                  详细数据
                </button>
              </div>
            </div>
          </div>

          <!-- Action Button -->
          <div class="px-4 py-2">
            <button (click)="startAnalysis()" class="flex w-full items-center justify-center rounded-2xl h-16 px-5 bg-primary text-background-dark gap-3 text-lg font-black tracking-wide shadow-[0_0_20px_rgba(25,186,240,0.4)] active:scale-[0.98] transition-all hover:bg-[#149cc9]">
              <span class="material-symbols-outlined text-[30px] fill-1">videocam</span>
              <span>开始分析杀球</span>
            </button>
          </div>

          <!-- AI Insight -->
          <div class="px-4 py-4">
            <div class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-4 flex items-center gap-4">
              <div class="size-12 rounded-full bg-primary/10 flex items-center justify-center shrink-0 border border-primary/20">
                <span class="material-symbols-outlined text-primary text-[28px]">psychology</span>
              </div>
              <div>
                <p class="text-[10px] font-black text-primary uppercase tracking-widest mb-0.5">AI 智能建议</p>
                <p class="text-sm text-slate-300 leading-snug">你在上一场训练中的手腕爆发力提升了 <span class="text-primary font-bold">12%</span>。请继续保持这个挥拍节奏！</p>
              </div>
            </div>
          </div>

          <!-- Recent Records Section -->
          <div class="flex items-center justify-between px-5 pt-4">
            <h2 class="text-white text-xl font-black leading-tight tracking-tight">最近记录</h2>
            <button (click)="switchTab('profile')" class="text-primary text-sm font-bold flex items-center gap-0.5 hover:underline">
              查看全部 <span class="material-symbols-outlined text-sm">chevron_right</span>
            </button>
          </div>

          <!-- Horizontal Scroll / Grid for Home -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4">
            @for (record of recentRecords(); track record.id) {
              <div class="flex flex-col gap-3 pb-3 bg-slate-900/40 rounded-2xl overflow-hidden border border-slate-800/50 p-2.5 hover:bg-slate-800/60 transition-colors cursor-pointer">
                <div class="relative w-full bg-center bg-no-repeat aspect-video bg-cover rounded-xl overflow-hidden group" 
                     [style.background-image]="'url(' + record.thumbnail + ')'">
                  <div class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors"></div>
                  <div class="absolute bottom-2 left-2 bg-black/70 backdrop-blur-md rounded-lg px-2.5 py-1 text-[11px] text-white font-black flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px] text-primary">bolt</span> {{ record.speed }} km/h
                  </div>
                </div>
                <div class="px-1.5 pb-1">
                  <div class="flex justify-between items-start mb-1.5">
                    <p class="text-white text-base font-bold">{{ record.title }}</p>
                    @if (record.tags.length > 0) {
                       <span class="text-[10px] px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 border border-green-500/20 font-black uppercase tracking-tighter">{{ record.tags[0] }}</span>
                    }
                  </div>
                  <div class="flex items-center justify-between">
                    <p class="text-slate-400 text-[11px] font-medium">{{ record.date }}</p>
                    <p class="text-slate-400 text-[11px] font-medium">{{ record.count }} 次杀球</p>
                  </div>
                </div>
              </div>
            }
          </div>
        </div>
      } @else if (currentTab() === 'profile') {
        <!-- PROFILE TAB CONTENT -->
        <div class="animate-fade-in p-4">
          
          <!-- User Profile Header -->
          <div class="flex flex-col items-center justify-center pt-4 pb-8">
            <div class="size-24 rounded-full border-4 border-primary p-1 mb-4">
               <img [src]="smashService.userAvatar()" class="w-full h-full rounded-full object-cover bg-slate-800" alt="Profile">
            </div>
            <h1 class="text-2xl font-black text-white mb-1">{{ smashService.userName() }}</h1>
            <div class="flex items-center gap-2">
               <span class="text-xs font-bold text-background-dark bg-primary px-2 py-0.5 rounded">Lv. 5</span>
               <span class="text-slate-400 text-sm">上海市羽毛球业余联赛</span>
            </div>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-3 gap-3 mb-8">
             <div class="bg-slate-800/50 rounded-2xl p-3 flex flex-col items-center justify-center border border-white/5">
                <span class="text-primary text-xl font-black">146</span>
                <span class="text-slate-400 text-[10px] uppercase font-bold tracking-wider mt-1">总杀球数</span>
             </div>
             <div class="bg-slate-800/50 rounded-2xl p-3 flex flex-col items-center justify-center border border-white/5">
                <span class="text-white text-xl font-black">392</span>
                <span class="text-slate-400 text-[10px] uppercase font-bold tracking-wider mt-1">最高时速</span>
             </div>
             <div class="bg-slate-800/50 rounded-2xl p-3 flex flex-col items-center justify-center border border-white/5">
                <span class="text-green-400 text-xl font-black">8.9</span>
                <span class="text-slate-400 text-[10px] uppercase font-bold tracking-wider mt-1">平均评分</span>
             </div>
          </div>

          <!-- Full History List -->
          <h3 class="text-white text-lg font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">history</span>
            杀球记录档案
          </h3>

          <div class="flex flex-col gap-4 pb-12">
            @for (record of smashService.smashHistory(); track record.id) {
              <div class="flex gap-4 bg-slate-900/40 border border-slate-800/60 p-3 rounded-2xl">
                 <div class="w-24 aspect-[4/3] bg-slate-800 rounded-lg bg-cover bg-center shrink-0 relative"
                      [style.background-image]="'url(' + record.thumbnail + ')'">
                      <div class="absolute bottom-1 right-1 bg-black/70 px-1.5 py-0.5 rounded text-[10px] font-bold text-white">
                        {{ record.score }}
                      </div>
                 </div>
                 <div class="flex-1 flex flex-col justify-center">
                    <div class="flex justify-between items-start">
                       <h4 class="text-white font-bold text-sm line-clamp-1">{{ record.title }}</h4>
                       <span class="text-primary font-black text-sm italic">{{ record.speed }} <span class="text-[10px] font-normal not-italic text-slate-400">km/h</span></span>
                    </div>
                    <p class="text-slate-500 text-xs mt-1">{{ record.date }}</p>
                    <div class="flex gap-2 mt-2">
                       @for(tag of record.tags; track tag) {
                          <span class="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">{{ tag }}</span>
                       }
                    </div>
                 </div>
              </div>
            }
          </div>
        </div>
      }

      <!-- Bottom Navigation Bar -->
      <div class="fixed bottom-0 left-0 right-0 bg-background-dark/95 backdrop-blur-2xl border-t border-slate-800/60 px-8 py-3 pb-8 flex justify-between items-center z-50">
        
        <!-- Home Tab -->
        <div (click)="switchTab('home')" 
             class="flex flex-col items-center gap-1.5 cursor-pointer transition-colors"
             [class]="currentTab() === 'home' ? 'text-primary' : 'text-slate-500 hover:text-slate-300'">
          <span class="material-symbols-outlined text-[28px]" [class.fill-1]="currentTab() === 'home'">home</span>
          <span class="text-[10px] font-black">首页</span>
        </div>

        <!-- Leaderboard (Placeholder) -->
        <div class="flex flex-col items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors cursor-pointer opacity-50">
          <span class="material-symbols-outlined text-[28px]">leaderboard</span>
          <span class="text-[10px] font-black">排行榜</span>
        </div>

        <!-- Profile Tab -->
        <div (click)="switchTab('profile')"
             class="flex flex-col items-center gap-1.5 cursor-pointer transition-colors"
             [class]="currentTab() === 'profile' ? 'text-primary' : 'text-slate-500 hover:text-slate-300'">
          <span class="material-symbols-outlined text-[28px]" [class.fill-1]="currentTab() === 'profile'">person</span>
          <span class="text-[10px] font-black">个人中心</span>
        </div>
        
      </div>
    </div>
  `,
  styles: [`
    .animate-fade-in {
      animation: fadeIn 0.3s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent {
  smashService = inject(SmashService);
  router = inject(Router);

  currentTab = signal<'home' | 'profile'>('home');
  recentRecords = signal(this.smashService.smashHistory().slice(0, 2));

  startAnalysis() {
    this.router.navigate(['/upload']);
  }

  switchTab(tab: 'home' | 'profile') {
    this.currentTab.set(tab);
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}