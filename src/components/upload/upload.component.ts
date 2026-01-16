import { Component, ChangeDetectionStrategy, inject, ViewChild, ElementRef, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { SmashService } from '../../services/smash.service';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [DecimalPipe],
  template: `
    <div class="flex flex-col min-h-screen bg-background-dark text-white overflow-x-hidden max-w-[480px] mx-auto">
      <!-- Hidden Input -->
      <input #fileInput type="file" accept="video/*" class="hidden" (change)="onFileSelected($event)" />

      <!-- Nav -->
      <div class="flex items-center p-4 justify-between sticky top-0 z-50 bg-background-dark border-b border-white/10">
        <div (click)="goBack()" class="text-white flex size-10 shrink-0 items-center justify-center cursor-pointer hover:bg-white/5 rounded-full">
          <span class="material-symbols-outlined">arrow_back_ios</span>
        </div>
        <h2 class="text-white text-lg font-bold leading-tight flex-1 text-center">上传视频</h2>
        <div class="flex w-10 items-center justify-end">
          <button class="flex items-center justify-center rounded-lg h-10 text-white p-0 hover:bg-white/5">
            <span class="material-symbols-outlined">info</span>
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto pb-32">
        <div class="px-4 pt-6 pb-2">
          <h3 class="text-white text-2xl font-bold leading-tight">捕捉你的扣杀瞬间</h3>
          <p class="text-white/60 text-sm mt-1">AI 将自动截取并分析视频中的杀球动作，建议上传 5 秒内的清晰片段。</p>
        </div>

        <!-- Buttons -->
        <div class="grid grid-cols-2 gap-3 p-4">
          <div class="flex flex-col gap-3 pb-3">
            <button (click)="triggerUpload()" class="w-full bg-primary/10 border-2 border-primary/20 flex flex-col items-center justify-center aspect-square rounded-xl cursor-pointer hover:bg-primary/20 transition-colors">
              <span class="material-symbols-outlined text-primary text-4xl mb-2">videocam</span>
              <p class="text-white text-sm font-medium">拍摄视频</p>
            </button>
          </div>
          <div class="flex flex-col gap-3 pb-3">
            <button (click)="triggerUpload()" class="w-full bg-white/5 border-2 border-white/10 flex flex-col items-center justify-center aspect-square rounded-xl cursor-pointer hover:bg-white/10 transition-colors">
              <span class="material-symbols-outlined text-white text-4xl mb-2">photo_library</span>
              <p class="text-white text-sm font-medium">上传视频</p>
            </button>
          </div>
        </div>

        <!-- Player -->
        <div class="px-4">
          <div class="relative flex items-center justify-center bg-zinc-900 aspect-video rounded-xl overflow-hidden border border-white/10 group">
             @if (videoUrl()) {
               <video #videoPlayer 
                      [src]="videoUrl()" 
                      class="w-full h-full object-contain bg-black" 
                      controls 
                      playsinline
                      (loadedmetadata)="onMetadata($event)">
               </video>
             } @else {
               <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuBhEgNHHhjRbENKwGTGUNw-OhIiPEddh6jrlxrnwwiBVSFK1IPp20TKj36hwveqg_745Gbg6AnL1XoemWiTrsGQ2sV4e5V2B3FIxKklxJT-OhSYQIrEjqOARkrvpWlqv7Uz6SMfSjoDwOaN77q35sk1W7wYxlS7MbL6ugLiQtIf2CwNiAzWzXMgUnC3c2AIkSuEPsoRdIZ6scJR_5Yp1kt5Xh-Xh6F0nkQHxKb8PlRv4j3NjhOyqyNb-YCTAqaxsBsZ-ByivYFRUmNP');"></div>
               <div class="absolute inset-0 bg-black/40 group-hover:bg-black/50 transition-colors"></div>
               <button (click)="triggerUpload()" class="relative z-10 flex shrink-0 items-center justify-center rounded-full size-16 bg-black/60 text-white backdrop-blur-sm hover:scale-105 transition-transform">
                 <span class="material-symbols-outlined fill-1 text-4xl">play_arrow</span>
               </button>
               <div class="absolute top-3 right-3 bg-black/60 px-2 py-1 rounded text-[10px] font-bold tracking-widest uppercase">
                 演示视频
               </div>
             }
          </div>
        </div>
      </div>

      <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background-dark via-background-dark to-transparent pt-8 max-w-[480px] mx-auto z-50">
        <button (click)="start()" 
                [disabled]="!videoUrl()"
                [class.opacity-50]="!videoUrl()"
                class="w-full bg-primary text-background-dark font-bold text-lg h-14 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-primary/20 active:scale-95 transition-transform hover:bg-[#149cc9]">
          <span class="material-symbols-outlined fill-1">auto_awesome</span>
          开始 AI 分析
        </button>
        <div class="h-6"></div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UploadComponent {
  router = inject(Router);
  smashService = inject(SmashService);
  videoUrl = this.smashService.uploadedVideoUrl;

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  @ViewChild('videoPlayer') videoPlayer?: ElementRef<HTMLVideoElement>;

  videoDuration = signal(0);
  // Default trim range is handled by service, we just ensure file is loaded
  
  goBack() {
    this.router.navigate(['/dashboard']);
  }

  triggerUpload() {
    this.fileInput.nativeElement.click();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      const url = URL.createObjectURL(file);
      this.smashService.uploadedVideoUrl.set(url);
      this.smashService.uploadedFile.set(file); 
      
      // Default to start 0
      this.smashService.trimStart.set(0);
      // We will update end when metadata loads
    }
  }

  onMetadata(e: Event) {
    const v = e.target as HTMLVideoElement;
    this.videoDuration.set(v.duration);
    // Automatically set analyze range to first 5 seconds or full video if shorter
    this.smashService.trimEnd.set(Math.min(v.duration, 5));
  }

  start() {
    this.router.navigate(['/analysis']);
  }
}