import { Injectable, signal, inject } from '@angular/core';
import { BackendApiService, AnalysisResult as BackendAnalysisResult } from './backend-api.service';
import { firstValueFrom } from 'rxjs';

export interface AnalysisResult {
  speed: number;
  rank: number; // Percentage
  rankPosition: number;
  level: string;
  technique: {
    power: number;
    angle: number;
    coordination: number;
  };
  score: number;
  suggestions: { title: string; desc: string; icon: string; highlight: string }[];
}

export interface SmashRecord {
  id: string;
  date: string;
  speed: number;
  count: number;
  score: number;
  tags: string[];
  thumbnail: string;
  title: string;
}

@Injectable({
  providedIn: 'root'
})
export class SmashService {
  private backendApi = inject(BackendApiService);

  // Mock User State
  userName = signal<string>('陈一鸣 (Alex)');
  userAvatar = signal<string>('https://lh3.googleusercontent.com/aida-public/AB6AXuDvhR5OpWHMhPEIU8BrF44ZKAdNIpKgP1sjdfsv67TC96WqFRTPqETFoDCTbeUAtVZO8ASEUzW2V81nwZVqABXQu9bHpTBZSUaPuT0rX7IecY8BP-qHSEuqDsiJ4CJ2CH1i8-_j9xMdlB1MJba78Aw6sHJghdeC01UKye-39DQmu0kcZrdkvCDHimwwpRsXNi7btCPyjhyLih10Q8y2T3BuiO0YZHg110pO6hI9y4_nhrK046RwNpXIjznEKGdAvU0UJiQVeAX2MeMZ');

  // Mock History Data - TODO: Load from backend
  smashHistory = signal<SmashRecord[]>([
    {
      id: '1',
      date: '2023年10月24日',
      speed: 380,
      count: 42,
      score: 9.2,
      tags: ['表现提升'],
      thumbnail: 'https://lh3.googleusercontent.com/aida-public/AB6AXuA-1jQlGjaxUpLrc6gvjrsnfjRQJVNuNJXjm42MAWHl3j8W7ByFqKbvGp4hxh3PnhvsQWrpCeKSyTUNhsvT7A_hus__oVfsKylwhTQnSIQI65dt08oqMJTqQ9StF1a2Q_AekNc62qsdy_pebWLXTrFE33b_60QITqiZ7cjXj7EFkaHv7by4kltT2-xPCneUvrhLIq5c9c4YLg08gP2Nk5KfoRfRP7JZERGxMPltUEhC1QM4VN_pBYa_-lwk8rUrMrOSZuWd0MZkRJCb',
      title: '早间专项练习'
    }
  ]);

  // Video State
  uploadedFile = signal<File | null>(null);
  uploadedVideoUrl = signal<string | null>(null);
  trimStart = signal<number>(0);
  trimEnd = signal<number>(5);

  // Current Analysis State
  currentResult = signal<AnalysisResult>({
    speed: 0,
    rank: 0,
    rankPosition: 0,
    level: '-',
    technique: { power: 0, angle: 0, coordination: 0 },
    score: 0,
    suggestions: []
  });

  constructor() { }

  async analyzeSmash(): Promise<void> {
    const file = this.uploadedFile();
    if (!file) throw new Error('No video file selected');

    try {
      console.log('Starting analysis flow via Backend API...');

      // 1. Upload Video
      console.log('Uploading video...');
      const uploadResponse = await firstValueFrom(
        this.backendApi.uploadVideo(file, this.trimStart(), this.trimEnd())
      );
      console.log('Video uploaded, ID:', uploadResponse.id);

      // 2. Start Analysis
      console.log('Requesting analysis...');
      const analysisResult = await firstValueFrom(
        this.backendApi.startAnalysis(uploadResponse.id)
      );
      console.log('Analysis completed:', analysisResult);

      // 3. Map result to frontend model
      this.currentResult.set({
        speed: analysisResult.speed,
        rank: analysisResult.rank || 85, // Default fallback
        rankPosition: analysisResult.rank_position || 15,
        level: analysisResult.level,
        technique: analysisResult.technique,
        score: analysisResult.score,
        suggestions: analysisResult.suggestions
      });

    } catch (error) {
      console.error('Analysis failed:', error);
      throw error;
    }
  }
}