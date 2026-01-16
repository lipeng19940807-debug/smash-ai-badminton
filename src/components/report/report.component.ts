import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';

@Component({
  selector: 'app-report',
  standalone: true,
  template: `
    <div class="relative flex min-h-screen w-full flex-col max-w-md mx-auto bg-background-dark text-white selection:bg-primary/30">
      <header class="flex items-center p-4 justify-between sticky top-0 z-30 bg-background-dark/80 backdrop-blur-md border-b border-white/5">
        <div (click)="goDashboard()" class="text-primary flex size-12 shrink-0 items-center cursor-pointer hover:bg-white/5 rounded-full justify-center -ml-2">
          <span class="material-symbols-outlined text-2xl">arrow_back_ios</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight flex-1 text-center">杀球性能报告</h2>
        <div class="flex w-12 items-center justify-end">
          <button class="flex size-10 items-center justify-center rounded-full text-primary hover:bg-primary/10 transition-colors">
            <span class="material-symbols-outlined">info</span>
          </button>
        </div>
      </header>

      <main class="flex-1 px-4 pb-48">
        <!-- Speed Hero -->
        <section class="flex flex-col items-center justify-center pt-8 pb-10">
          <p class="text-primary text-sm font-bold tracking-widest mb-2 uppercase">杀球速度</p>
          <div class="flex items-baseline relative">
            <h1 class="text-white tracking-tighter text-8xl font-black italic drop-shadow-[0_0_30px_rgba(25,186,240,0.5)]">
              {{ result.speed }}
            </h1>
            <span class="text-2xl ml-2 font-bold text-white/90">km/h</span>
          </div>
          <div class="mt-6 flex items-center gap-2 px-6 py-2 bg-primary/10 rounded-full border border-primary/20 animate-pulse-fast">
            <span class="material-symbols-outlined text-primary text-sm">trending_up</span>
            <span class="text-primary text-xs font-bold">刷新个人最佳记录</span>
          </div>
        </section>

        <!-- Technical Bar Chart Card -->
        <section class="mb-6">
          <div class="bg-slate-900/40 rounded-3xl p-6 border border-slate-800/60 shadow-lg relative overflow-hidden">
            <!-- Decorative border glow -->
            <div class="absolute inset-0 border-2 border-primary/20 rounded-3xl pointer-events-none"></div>
            
            <h3 class="text-white text-lg font-bold mb-6 flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">bar_chart</span>
              技术维度评分
            </h3>
            
            <!-- Bar Chart Display -->
            <div class="grid grid-cols-3 gap-4 h-56 px-2">
              
              <!-- Bar 1: Power -->
              <div class="flex flex-col items-center h-full justify-end group w-full">
                <span class="text-white font-black mb-3 text-2xl font-display tracking-tight">{{ result.technique.power }}</span>
                <!-- Track -->
                <div class="w-full max-w-[50px] bg-slate-800/50 rounded-2xl relative overflow-hidden h-32 border border-white/5 shadow-inner flex flex-col justify-end">
                   <!-- Bar -->
                   <div class="w-full bg-gradient-to-t from-blue-600 to-primary rounded-2xl transition-all duration-1000 ease-out shadow-[0_0_20px_rgba(25,186,240,0.4)] relative min-h-[4px]" 
                        [style.height.%]="result.technique.power">
                        <div class="absolute top-0 left-0 right-0 h-[2px] bg-white/60"></div>
                   </div>
                </div>
                <p class="text-slate-400 text-xs font-bold mt-3 uppercase tracking-wider">发力</p>
              </div>
              
              <!-- Bar 2: Angle -->
              <div class="flex flex-col items-center h-full justify-end group w-full">
                <span class="text-white font-black mb-3 text-2xl font-display tracking-tight">{{ result.technique.angle }}</span>
                <div class="w-full max-w-[50px] bg-slate-800/50 rounded-2xl relative overflow-hidden h-32 border border-white/5 shadow-inner flex flex-col justify-end">
                   <div class="w-full bg-gradient-to-t from-purple-600 to-purple-400 rounded-2xl transition-all duration-1000 ease-out delay-100 shadow-[0_0_20px_rgba(192,132,252,0.4)] relative min-h-[4px]" 
                        [style.height.%]="result.technique.angle">
                        <div class="absolute top-0 left-0 right-0 h-[2px] bg-white/60"></div>
                   </div>
                </div>
                <p class="text-slate-400 text-xs font-bold mt-3 uppercase tracking-wider">角度</p>
              </div>
              
              <!-- Bar 3: Coordination -->
              <div class="flex flex-col items-center h-full justify-end group w-full">
                <span class="text-white font-black mb-3 text-2xl font-display tracking-tight">{{ result.technique.coordination }}</span>
                <div class="w-full max-w-[50px] bg-slate-800/50 rounded-2xl relative overflow-hidden h-32 border border-white/5 shadow-inner flex flex-col justify-end">
                   <div class="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-2xl transition-all duration-1000 ease-out delay-200 shadow-[0_0_20px_rgba(52,211,153,0.4)] relative min-h-[4px]" 
                        [style.height.%]="result.technique.coordination">
                        <div class="absolute top-0 left-0 right-0 h-[2px] bg-white/60"></div>
                   </div>
                </div>
                <p class="text-slate-400 text-xs font-bold mt-3 uppercase tracking-wider">协调性</p>
              </div>
              
            </div>

            <div class="flex items-center justify-between pt-6 border-t border-white/5 mt-6">
              <span class="text-slate-400 text-sm font-medium">动作综合评分：</span>
              <div class="flex items-baseline gap-2">
                <span class="text-primary text-4xl font-black italic">{{ result.score }}</span>
                <span class="text-primary/60 text-xs font-bold bg-primary/10 px-2 py-1 rounded">/ 10.0</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Suggestions -->
        <section class="mb-6">
          <h3 class="text-white text-lg font-bold px-1 mb-4">专业建议</h3>
          <div class="relative overflow-hidden bg-slate-900/40 border border-slate-800/60 rounded-3xl p-5">
            <div class="flex gap-4 relative z-10">
              <div class="flex flex-col gap-6 flex-1">
                @for (item of result.suggestions; track item.title) {
                  <div class="flex items-start gap-3">
                    <div class="bg-primary/20 p-2.5 rounded-xl flex items-center justify-center shrink-0">
                      <span class="material-symbols-outlined text-primary text-base font-bold">{{ item.icon }}</span>
                    </div>
                    <div>
                      <p class="text-white text-sm font-bold">{{ item.title }}</p>
                      <p class="text-slate-400 text-xs mt-1.5 leading-relaxed">
                        {{ item.desc }}
                      </p>
                    </div>
                  </div>
                }
              </div>
              <!-- Skeleton visual decoration -->
              <div class="w-24 flex-shrink-0 relative overflow-hidden rounded-xl bg-slate-950 border border-slate-800 self-stretch">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBtmFRen954ALCkYN1xe1wQ0zUs5MVgp_4q2mttdAMvP6w-7JSo3XRT5YbZHXX-u6UJ1qvYC3ylQx6qQw1awYdMixCnCSFu4eFgH6WwmLb8PFnmlOosc8eir0j5-0cE4LqqVbj_14ZLefoKYVo_arageZw_D8pk1unzacXYxFQPnnfyn9JwaMr1RhC4tB4REcJBwHkppx_pLra4GOIFka2O4s64COt5ceC-nrjY1PAtvQSHxsJlC2NZZzsa11N2R_rDDsNmpShTIddQ" class="w-full h-full object-cover opacity-60 mix-blend-screen" alt="Skeleton Analysis">
              </div>
            </div>
          </div>
        </section>

        <!-- Ranking -->
        <section class="mb-6">
          <div class="bg-slate-900/40 rounded-3xl p-5 flex items-center justify-between border border-slate-800/60">
            <div class="flex items-center gap-4">
              <div class="size-11 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20">
                <span class="material-symbols-outlined text-yellow-500 text-2xl">trophy</span>
              </div>
              <div>
                <p class="text-white text-sm font-bold">全球排名</p>
                <p class="text-slate-500 text-xs mt-0.5">业余联赛 (Lvl 5)</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-primary text-2xl font-black italic">前 {{ result.rankPosition }}%</p>
              <p class="text-slate-500 text-[10px] uppercase font-bold tracking-wider mt-0.5">地区: 亚洲</p>
            </div>
          </div>
        </section>
      </main>

      <!-- Footer -->
      <footer class="fixed bottom-0 left-0 right-0 bg-background-dark/95 backdrop-blur-2xl p-6 pb-10 z-40 max-w-md mx-auto border-t border-white/5">
        <div class="space-y-6">
          <button (click)="share()" class="w-full bg-primary text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 shadow-[0_4px_20px_rgba(25,186,240,0.3)] transition-transform active:scale-[0.98] hover:bg-[#149cc9]">
            <span class="material-symbols-outlined font-bold">share</span>
            <span class="text-lg">分享战报</span>
          </button>
          
          <div class="flex items-center justify-between px-2">
            <p class="text-slate-400 text-xs font-medium">快速分享到</p>
            <div class="flex gap-4">
              <button class="size-11 rounded-full bg-slate-800/80 flex items-center justify-center border border-slate-700/50 hover:bg-slate-700 transition-colors">
                <span class="material-symbols-outlined text-white/90 text-xl">chat</span>
              </button>
              <button class="size-11 rounded-full bg-slate-800/80 flex items-center justify-center border border-slate-700/50 hover:bg-slate-700 transition-colors">
                 <span class="material-symbols-outlined text-white/90 text-xl">camera_indoor</span>
              </button>
              <button class="size-11 rounded-full bg-slate-800/80 flex items-center justify-center border border-slate-700/50 hover:bg-slate-700 transition-colors">
                 <span class="material-symbols-outlined text-white/90 text-xl">download</span>
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ReportComponent {
  smashService = inject(SmashService);
  router = inject(Router);
  
  result = this.smashService.currentResult();

  goDashboard() {
    this.router.navigate(['/dashboard']);
  }

  share() {
    this.router.navigate(['/share']);
  }
}