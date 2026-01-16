import { Component, ChangeDetectionStrategy, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';

@Component({
  selector: 'app-analysis',
  standalone: true,
  template: `
    <div class="relative flex min-h-screen w-full flex-col bg-background-dark text-white max-w-[480px] mx-auto shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="flex items-center bg-background-dark p-4 pb-2 justify-between z-20">
        <div (click)="cancel()" class="text-white flex size-12 shrink-0 items-center justify-start cursor-pointer hover:text-red-400 transition-colors">
          <span class="material-symbols-outlined">close</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight tracking-tight flex-1 text-center pr-12">
          {{ error() ? '分析失败' : 'AI 正在分析...' }}
        </h2>
      </div>

      <!-- Error State -->
      @if (error()) {
        <div class="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <span class="material-symbols-outlined text-red-500 text-6xl mb-4">error_outline</span>
          <p class="text-white text-lg font-bold mb-2">无法完成分析</p>
          <p class="text-slate-400 text-sm mb-6">{{ error() }}</p>
          <button (click)="retry()" class="px-6 py-3 bg-primary text-background-dark font-bold rounded-xl hover:bg-[#149cc9]">
            重试
          </button>
        </div>
      } @else {
        <!-- Main Visual -->
        <div class="px-4 relative z-10">
          <div class="flex items-center justify-center gap-2 py-2 mb-2">
            <div class="size-2 rounded-full bg-primary animate-pulse"></div>
            <h4 class="text-primary text-sm font-bold leading-normal tracking-wide animate-pulse">正在追踪球路</h4>
          </div>
          
          <div class="relative flex items-center justify-center bg-slate-800 bg-cover bg-center aspect-[3/4] rounded-xl overflow-hidden border border-white/10 shadow-2xl" 
               style="background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://lh3.googleusercontent.com/aida-public/AB6AXuCnsKm8dqjJd3o8-ZQrV7YPG5e4_GWEPFLaBAVDFMeH5e0xC_1XykV3d8kqy2Kqg-Ywmqy7KX80WUgQxrpM69RnESeOtW0Ybu1wwGsngKiyNDkqr4DWCZp1xH05YwgUuWH_HkEunqJqX4Ft6N46IUis3VsCHiRfh21odk7l-u3mhpW52P0v5Vtfk5gBBwgWJDSOvI4j-G9HOOvNg38MKd4lKHPEDOHed0y9rBZOD8Y31Jv995N5wNSVz0MP0bF8fU2lzkgUs2WEcMdH');">
            
            <!-- Scanning Line -->
            <div class="absolute top-0 w-full h-[2px] bg-primary/80 shadow-[0_0_15px_#19baf0] animate-[scan_2s_ease-in-out_infinite]"></div>
            
            <!-- Skeleton Nodes -->
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 30%; left: 50%;"></div>
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 20%; left: 65%;"></div>
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 10%; left: 75%;"></div>
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 60%; left: 48%;"></div>
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 85%; left: 40%;"></div>
            <div class="absolute w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#19baf0]" style="top: 85%; left: 55%;"></div>
            
            <!-- Lines -->
            <svg class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
               <line x1="50" y1="30" x2="65" y2="20" stroke="#19baf0" stroke-width="0.5" stroke-opacity="0.8" />
               <line x1="65" y1="20" x2="75" y2="10" stroke="#19baf0" stroke-width="0.5" stroke-opacity="0.8" />
               <line x1="50" y1="30" x2="48" y2="60" stroke="#19baf0" stroke-width="0.5" stroke-opacity="0.8" />
               <line x1="48" y1="60" x2="40" y2="85" stroke="#19baf0" stroke-width="0.5" stroke-opacity="0.8" />
               <line x1="48" y1="60" x2="55" y2="85" stroke="#19baf0" stroke-width="0.5" stroke-opacity="0.8" />
            </svg>
  
            <!-- Badges -->
            <div class="absolute bottom-4 left-4 flex flex-col gap-2">
              <div class="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/20 flex items-center gap-2 w-fit animate-pulse">
                <span class="material-symbols-outlined text-[14px] text-primary">accessibility_new</span>
                <span class="text-[10px] font-bold tracking-widest uppercase">骨架提取中</span>
              </div>
               <div class="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/20 flex items-center gap-2 w-fit">
                <span class="material-symbols-outlined text-[14px] text-primary">graphic_eq</span>
                <span class="text-[10px] font-bold tracking-widest uppercase">声学事件检测</span>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Progress Section -->
        <div class="flex flex-col gap-3 p-6 mt-2">
          <div class="flex gap-6 justify-between items-end">
            <div class="flex flex-col">
              <p class="text-slate-400 text-xs font-bold uppercase tracking-widest">分析状态</p>
              <p class="text-white text-xl font-bold leading-normal">正在进行 AI 分析...</p>
            </div>
            <div class="flex flex-col items-end">
              <p class="text-primary text-2xl font-black leading-normal">Processing</p>
            </div>
          </div>
          <div class="rounded-full bg-slate-800 overflow-hidden">
            <div class="h-2.5 rounded-full bg-primary w-full animate-[width_2s_ease-in-out_infinite]"></div>
          </div>
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[18px]">settings_motion_mode</span>
            <p class="text-slate-400 text-sm font-medium leading-normal italic">正在计算拍头速度...</p>
          </div>
        </div>
      }

      <!-- Footer Action -->
      <div class="fixed bottom-0 left-0 right-0 p-6 bg-slate-900/50 backdrop-blur-xl border-t border-white/5 max-w-[480px] mx-auto z-30">
        <button (click)="cancel()" class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-xl transition-all border border-white/10 flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-[20px]">stop_circle</span>
          取消分析
        </button>
      </div>

      <style>
        @keyframes scan {
          0% { top: 0%; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
      </style>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AnalysisComponent implements OnInit {
  router = inject(Router);
  smashService = inject(SmashService);
  error = signal<string | null>(null);

  ngOnInit() {
    this.startAnalysis();
  }

  async startAnalysis() {
    try {
      this.error.set(null);
      await this.smashService.analyzeSmash();
      this.router.navigate(['/report']);
    } catch (e: any) {
      console.error(e);
      this.error.set(e.message || 'Unknown Error');
    }
  }

  retry() {
    this.startAnalysis();
  }

  cancel() {
    this.router.navigate(['/upload']);
  }
}