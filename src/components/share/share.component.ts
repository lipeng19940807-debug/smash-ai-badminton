import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';

@Component({
  selector: 'app-share',
  standalone: true,
  template: `
    <div class="min-h-screen bg-background-dark font-display text-white antialiased flex flex-col">
      <!-- TopAppBar -->
      <div class="flex items-center bg-transparent p-4 pb-2 justify-between z-10">
        <div (click)="close()" class="text-white flex size-12 shrink-0 items-center justify-start cursor-pointer hover:opacity-80">
          <span class="material-symbols-outlined text-2xl">close</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight tracking-[-0.015em] flex-1 text-center">分享战报</h2>
        <div class="flex w-12 items-center justify-end">
          <button class="flex items-center justify-center rounded-lg h-12 text-white hover:opacity-80">
            <span class="material-symbols-outlined">more_horiz</span>
          </button>
        </div>
      </div>

      <main class="flex-1 flex flex-col items-center justify-center p-4">
        <!-- Shareable War Report Card -->
        <div class="w-full max-w-sm rounded-xl overflow-hidden shadow-2xl relative bg-gradient-to-br from-[#192d34] to-[#111e22] border border-primary/20">
          <!-- Card Header Image -->
          <div class="relative h-56 w-full">
            <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuCMmryFURWmPoJtgyTjGtjMMjXLmHefQkRcTgy0b67txsERK7sc5Ew7Cl_a-qbBhS91PWZpOw2AnfJUihzHIb9ZGEtKD7BTUZvtDBpWsJoRJTD2YNiEGSDhkpieMp1lXQJD4XkDmlm3ZBmb43PWc1O57xJVQw4-UZpUxg6TkMbqKAO6FQTw_STTqk8ulFxJy6b_TSjV58Na-8S7wskg3w-ufGyQwfOeT7Xvl3crOZ8LIc1bqZo8ZzvmMFSeIN6Zwy52p6NE9FgBn2UD')"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-[#111e22] to-transparent"></div>
            <div class="absolute top-4 left-4 flex items-center gap-2">
              <div class="bg-primary px-3 py-1 rounded-full flex items-center gap-1 shadow-lg shadow-primary/20">
                <span class="material-symbols-outlined text-xs !text-[#101d22] font-bold">bolt</span>
                <span class="text-xs font-bold text-[#101d22] uppercase tracking-wider italic">AI Smash Analysis</span>
              </div>
            </div>
          </div>

          <!-- Card Body -->
          <div class="p-6 pt-2 flex flex-col items-center text-center -mt-8 relative z-10">
            <p class="text-primary/80 text-sm font-medium tracking-[0.2em] mb-1 uppercase">Smash War Report</p>
            <h1 class="text-6xl font-bold text-white mb-2 italic tracking-tighter drop-shadow-lg">
              {{ result.speed }} <span class="text-xl not-italic font-normal text-primary/60">km/h</span>
            </h1>

            <div class="flex gap-6 my-6 w-full justify-center">
              <div class="flex flex-col">
                <span class="text-primary font-bold text-lg">#{{ result.rank }}</span>
                <span class="text-[#91bcca] text-[10px] uppercase font-medium">城市排名</span>
              </div>
              <div class="h-8 w-[1px] bg-white/10 self-center"></div>
              <div class="flex flex-col">
                <span class="text-white font-bold text-lg">98%</span>
                <span class="text-[#91bcca] text-[10px] uppercase font-medium">超越球友</span>
              </div>
              <div class="h-8 w-[1px] bg-white/10 self-center"></div>
              <div class="flex flex-col">
                <span class="text-white font-bold text-lg">{{ result.level }}</span>
                <span class="text-[#91bcca] text-[10px] uppercase font-medium">爆发等级</span>
              </div>
            </div>

            <div class="w-full bg-white/5 rounded-lg p-3 flex items-center justify-between mb-6 border border-white/5 backdrop-blur-sm">
              <div class="flex items-center gap-3">
                <div class="size-10 rounded-full border-2 border-primary overflow-hidden">
                  <img [src]="smashService.userAvatar()" class="w-full h-full object-cover" alt="Avatar">
                </div>
                <div class="text-left">
                  <p class="text-white text-sm font-bold">{{ smashService.userName() }}</p>
                  <p class="text-[#91bcca] text-xs">2023年10月24日 · 上海</p>
                </div>
              </div>
              <div class="bg-white p-1 rounded-sm">
                <div class="size-10 bg-white flex items-center justify-center">
                  <span class="material-symbols-outlined text-[#111e22] !text-4xl">qr_code_2</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- MetaText -->
        <div class="mt-8 mb-4">
          <p class="text-[#91bcca] text-sm font-normal leading-normal text-center">分享荣耀时刻至</p>
        </div>

        <!-- ActionsBar -->
        <div class="w-full">
          <div class="gap-2 px-4 grid grid-cols-4 max-w-md mx-auto">
            <!-- WeChat -->
            <button class="flex flex-col items-center gap-2 py-2.5 text-center cursor-pointer group hover:bg-white/5 rounded-xl transition-colors">
              <div class="rounded-full bg-white/5 group-hover:bg-green-500 p-4 transition-colors duration-300">
                <span class="material-symbols-outlined text-white">chat</span>
              </div>
              <p class="text-white text-xs font-medium">微信</p>
            </button>
            <!-- Moments -->
            <button class="flex flex-col items-center gap-2 py-2.5 text-center cursor-pointer group hover:bg-white/5 rounded-xl transition-colors">
              <div class="rounded-full bg-white/5 group-hover:bg-green-600 p-4 transition-colors duration-300">
                <span class="material-symbols-outlined text-white">camera_indoor</span>
              </div>
              <p class="text-white text-xs font-medium">朋友圈</p>
            </button>
            <!-- Douyin -->
            <button class="flex flex-col items-center gap-2 py-2.5 text-center cursor-pointer group hover:bg-white/5 rounded-xl transition-colors">
              <div class="rounded-full bg-white/5 group-hover:bg-black p-4 transition-colors duration-300">
                <span class="material-symbols-outlined text-white">music_video</span>
              </div>
              <p class="text-white text-xs font-medium">抖音</p>
            </button>
            <!-- XHS -->
            <button class="flex flex-col items-center gap-2 py-2.5 text-center cursor-pointer group hover:bg-white/5 rounded-xl transition-colors">
              <div class="rounded-full bg-white/5 group-hover:bg-red-500 p-4 transition-colors duration-300">
                <span class="material-symbols-outlined text-white">book</span>
              </div>
              <p class="text-white text-xs font-medium">小红书</p>
            </button>
          </div>
        </div>

        <!-- SingleButton -->
        <div class="w-full flex px-4 py-8 justify-center">
          <button class="flex min-w-[200px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-14 px-8 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 gap-2 transition-all active:scale-95">
            <span class="material-symbols-outlined">download</span>
            <span class="truncate font-bold tracking-wide">保存图片</span>
          </button>
        </div>
      </main>
      
      <div class="h-8 bg-transparent"></div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ShareComponent {
  smashService = inject(SmashService);
  router = inject(Router);
  
  result = this.smashService.currentResult();

  close() {
    this.router.navigate(['/dashboard']);
  }
}