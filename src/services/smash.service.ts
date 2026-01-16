import { Injectable, signal } from '@angular/core';
import { GoogleGenAI, Type } from '@google/genai';

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
  // Mock User State
  userName = signal<string>('陈一鸣 (Alex)');
  userAvatar = signal<string>('https://lh3.googleusercontent.com/aida-public/AB6AXuDvhR5OpWHMhPEIU8BrF44ZKAdNIpKgP1sjdfsv67TC96WqFRTPqETFoDCTbeUAtVZO8ASEUzW2V81nwZVqABXQu9bHpTBZSUaPuT0rX7IecY8BP-qHSEuqDsiJ4CJ2CH1i8-_j9xMdlB1MJba78Aw6sHJghdeC01UKye-39DQmu0kcZrdkvCDHimwwpRsXNi7btCPyjhyLih10Q8y2T3BuiO0YZHg110pO6hI9y4_nhrK046RwNpXIjznEKGdAvU0UJiQVeAX2MeMZ');

  // Mock History Data
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
    },
    {
      id: '2',
      date: '2023年10月22日',
      speed: 365,
      count: 18,
      score: 8.5,
      tags: ['发挥稳定'],
      thumbnail: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBdVeISZ9mc68vSZGi1u6BGA3ZF6mhBPzWeXH9HHY67XpT_CPcyQo9YKmTNeOaIDKMwbkHrRnyTzGVJ07x8_rOBt1scB6RG2ODyTnkPApH0i7-ER7jKGgXBqVSr7jasv3do2KOpbPQ2k7ajUqfxNFXSV7jq5eWphOxex1NaikZQBvs10vuZ3r0Ygv9CV-qYEiMocrotq3dRrIPjTG4mQ0cPJkZPBstaDyiRdkBqS8dllluV6TEIyc4AJIpK-GtLO6SDL5aH1xG9cLEM',
      title: '技巧恢复训练'
    },
    {
      id: '3',
      date: '2023年10月18日',
      speed: 342,
      count: 56,
      score: 7.9,
      tags: [],
      thumbnail: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB6L9Oxrz-vqLXmByrRUuSBTKproszPQa5U2l0X-6UtCxGRCBffYacDMtiRaYL52dSskhF6n2VDaStpP4MgqWF7WbBgZwuRTZcR5mO2ShOywMt4GeVYgZYYt2VAThCo7I-EP8abznfiUxrc8XUE6MpuV6KbfcHsM78gRlAMM-RZrILfBzOzC2bCXou4t1UmBHixEkZGhat8U1p9IdSycREX5ncV12OcY6dQkLy1r8AYPMN3ly4ihr6im-yAIThlPpu2dkyXpmB9qMUo',
      title: '高强度多球'
    },
    {
      id: '4',
      date: '2023年10月15日',
      speed: 355,
      count: 30,
      score: 8.8,
      tags: ['新纪录'],
      thumbnail: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBxSFBR2La-a460iDZnAjM43TGeff4rQVz1jLdmiIb4sidAQsH1f-EikcXfsvmKNHQ7ov_zYeOFoq-fHoj-dK_GLp7ELEV3c8c_6cRcTD0e8wUmK4Q2bsZcUBkSw4T9LEh7TbQJjRwwhW165fqaKup5qCM1MU4Jv36VB88nE86KMT5HA0jmI3UnV1KLgt1OypUL6zh8pxZQ0GNayBLVdk1blhI-RBQcB7Tb_JLAlGeaG9_ahOi1WE9bdMgUQuTzYOLbonELjemKpJ3E',
      title: '友谊赛实战'
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

  constructor() {}

  async analyzeSmash(): Promise<void> {
    const file = this.uploadedFile();
    if (!file) throw new Error('No video file selected');

    const apiKey = process.env['API_KEY'];
    if (!apiKey) throw new Error('API Key not found');

    const ai = new GoogleGenAI({ apiKey });

    // Convert File to Base64
    const base64Data = await this.fileToGenerativePart(file);

    // Prompt updated to be scientifically rigorous and robust
    const prompt = `
      你是一位世界顶级的羽毛球科研专家和运动生物力学分析师。请对上传的视频进行极高精度的量化分析，结果必须严谨且经得住推敲。
      
      请执行以下思维过程（Thinking Process）来确保准确性（如果是 Thinking Mode）：
      1. **视觉测距与物理建模**：
         - 仔细观察视频中的环境参照物（标准羽毛球场长13.40米，宽6.10米，网高1.55米）。
         - 估算羽毛球从击球点（Impact Point）到落地点（Landing Point）的飞行距离。
         - 计算飞行时间（Time of Flight），从而推算平均速度和初速度。
      2. **动作生物力学诊断**：
         - 逐帧分析 "鞭打动作" (Whip Effect)：检查力量是否从蹬地 -> 转髋 -> 展胸 -> 大臂 -> 小臂 -> 手腕 -> 手指 顺畅传递。
         - 观察击球点高度：是否在人体中轴线的前上方最高点（Sweet Spot）。
      3. **数据合理性校验**：
         - 业余初级：< 150 km/h
         - 业余中高级：150 - 250 km/h
         - 职业级：> 250 km/h
         - 请根据视频中选手的动作流畅度和爆发力，给出符合物理常识的速度估算，**严禁产生幻觉或给出不切实际的数值**。
      
      最后，请输出一份结构化的 JSON 报告。所有文本必须使用**简体中文**。
    `;

    const schema = {
      type: Type.OBJECT,
      properties: {
        speed: { type: Type.INTEGER, description: "Calculated smash speed in km/h based on physics" },
        rank: { type: Type.INTEGER, description: "Percentile rank (0-100)" },
        rankPosition: { type: Type.INTEGER, description: "Top X percent (e.g. 5 for top 5%)" },
        level: { type: Type.STRING, description: "Skill level (e.g., '职业级', '精英级', '进阶级', '入门级')" },
        technique: {
          type: Type.OBJECT,
          properties: {
            power: { type: Type.INTEGER, description: "Explosive power score 0-100 based on kinetic chain" },
            angle: { type: Type.INTEGER, description: "Smash angle score 0-100" },
            coordination: { type: Type.INTEGER, description: "Body coordination score 0-100" },
          },
          required: ["power", "angle", "coordination"]
        },
        score: { type: Type.NUMBER, description: "Overall scientific score out of 10.0" },
        suggestions: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING, description: "Technical suggestion title" },
              desc: { type: Type.STRING, description: "Detailed biomechanical correction advice" },
              icon: { type: Type.STRING, description: "Material symbol name" },
              highlight: { type: Type.STRING, description: "Key data point highlight (e.g. '15°', '0.2s')" }
            },
            required: ["title", "desc", "icon", "highlight"]
          }
        }
      },
      required: ["speed", "level", "technique", "score", "suggestions"]
    };

    try {
      // First attempt: With Thinking Config (high accuracy)
      console.log('Attempting analysis with Thinking Config...');
      await this.generateWithConfig(ai, base64Data, file.type, prompt, schema, true);
    } catch (error: any) {
      // Check for 503 Overloaded or similar resource errors
      const isOverloaded = error.message?.includes('503') || error.message?.includes('overloaded') || error.status === 503;
      
      if (isOverloaded) {
        console.warn('Model overloaded with Thinking Config. Retrying with standard config...');
        // Fallback: Standard Flash (No Thinking, lower latency/resource usage)
        try {
          await this.generateWithConfig(ai, base64Data, file.type, prompt, schema, false);
        } catch (fallbackError) {
          console.error('Fallback analysis failed', fallbackError);
          throw fallbackError; // Throw the original or new error depending on what you want to show
        }
      } else {
        console.error('Gemini Analysis Failed', error);
        throw error;
      }
    }
  }

  private async generateWithConfig(ai: GoogleGenAI, base64Data: string, mimeType: string, prompt: string, schema: any, useThinking: boolean) {
    const config: any = {
      responseMimeType: 'application/json',
      responseSchema: schema,
    };

    if (useThinking) {
      // Thinking mode requires reserving tokens for the thinking process
      config.maxOutputTokens = 4000;
      config.thinkingConfig = { thinkingBudget: 2000 };
    }

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: {
        parts: [
          { inlineData: { mimeType: mimeType, data: base64Data } },
          { text: prompt }
        ]
      },
      config: config
    });

    if (response.text) {
      const result = JSON.parse(response.text) as AnalysisResult;
      this.currentResult.set(result);
    } else {
      throw new Error('AI returned empty response');
    }
  }

  private fileToGenerativePart(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        // Remove the Data URL prefix (e.g., "data:video/mp4;base64,")
        const base64Data = result.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}