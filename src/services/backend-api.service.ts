import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

import { environment } from '../environments/environment';

// API 基础 URL - 硬编码以确保生产环境正确
const API_BASE_URL = '/api';

// 认证相关接口
export interface RegisterRequest {
    username: string;
    password: string;
    email?: string;
    nickname?: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: {
        id: string;
        username: string;
        nickname?: string;
        avatar_url?: string;
    };
}

export interface UserProfile {
    id: string;
    username: string;
    email?: string;
    nickname?: string;
    avatar_url?: string;
    created_at: string;
}

// 视频相关接口
export interface VideoUploadResponse {
    id: string;
    original_filename: string;
    file_path: string;
    duration: number;
    file_size: number;
    thumbnail_path?: string;
    uploaded_at: string;
}

// 分析相关接口
export interface AnalysisRequest {
    video_id: string;
}

export interface AnalysisResult {
    id: string;
    video_id: string;
    speed: number;
    level: string;
    score: number;
    technique: {
        power: number;
        angle: number;
        coordination: number;
    };
    rank?: number;
    rank_position?: number;
    suggestions: Array<{
        title: string;
        desc: string;
        icon: string;
        highlight: string;
    }>;
    analyzed_at: string;
}

// 历史记录接口
export interface HistoryItem {
    id: string;
    video_id: string;
    speed: number;
    score: number;
    level: string;
    thumbnail_url?: string;
    analyzed_at: string;
}

export interface HistoryResponse {
    total: number;
    page: number;
    page_size: number;
    items: HistoryItem[];
}

@Injectable({
    providedIn: 'root'
})
export class BackendApiService {
    private apiUrl = API_BASE_URL;

    // 当前登录用户状态
    private currentUserSubject = new BehaviorSubject<UserProfile | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    // Token 存储
    private tokenKey = 'access_token';

    constructor(private http: HttpClient) {
        // 启动时检查是否有已保存的 token
        const token = this.getToken();
        if (token) {
            // 尝试获取用户信息
            this.getProfile().subscribe({
                next: (user) => this.currentUserSubject.next(user),
                error: () => this.logout() // Token 无效，清除
            });
        }
    }

    // ==================== 认证相关 ====================

    /**
     * 用户注册
     */
    register(data: RegisterRequest): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/auth/register`, data)
            .pipe(
                tap(response => {
                    this.saveToken(response.access_token);
                    this.currentUserSubject.next(response.user as UserProfile);
                })
            );
    }

    /**
     * 用户登录
     */
    login(data: LoginRequest): Observable<AuthResponse> {
        return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, data)
            .pipe(
                tap(response => {
                    this.saveToken(response.access_token);
                    this.currentUserSubject.next(response.user as UserProfile);
                })
            );
    }

    /**
     * 获取用户信息
     */
    getProfile(): Observable<UserProfile> {
        return this.http.get<UserProfile>(`${this.apiUrl}/auth/profile`);
    }

    /**
     * 登出
     */
    logout(): void {
        localStorage.removeItem(this.tokenKey);
        this.currentUserSubject.next(null);
    }

    /**
     * 检查是否已登录
     */
    isLoggedIn(): boolean {
        return !!this.getToken();
    }

    /**
     * 获取当前用户
     */
    getCurrentUser(): UserProfile | null {
        return this.currentUserSubject.value;
    }

    // ==================== 视频相关 ====================

    /**
     * 上传视频
     */
    uploadVideo(file: File, trimStart?: number, trimEnd?: number): Observable<VideoUploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        if (trimStart !== undefined) {
            formData.append('trim_start', trimStart.toString());
        }
        if (trimEnd !== undefined) {
            formData.append('trim_end', trimEnd.toString());
        }

        return this.http.post<VideoUploadResponse>(`${this.apiUrl}/video/upload`, formData);
    }

    /**
     * 获取视频信息
     */
    getVideo(videoId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/video/${videoId}`);
    }

    // ==================== 分析相关 ====================

    /**
     * 开始分析视频
     */
    startAnalysis(videoId: string): Observable<AnalysisResult> {
        return this.http.post<AnalysisResult>(`${this.apiUrl}/analysis/start`, {
            video_id: videoId
        });
    }

    /**
     * 获取分析结果
     */
    getAnalysis(analysisId: string): Observable<AnalysisResult> {
        return this.http.get<AnalysisResult>(`${this.apiUrl}/analysis/${analysisId}`);
    }

    // ==================== 历史记录相关 ====================

    /**
     * 获取历史记录列表
     */
    getHistory(params?: {
        page?: number;
        page_size?: number;
        sort_by?: string;
        order?: 'asc' | 'desc';
    }): Observable<HistoryResponse> {
        const queryParams = new URLSearchParams();
        if (params?.page) queryParams.set('page', params.page.toString());
        if (params?.page_size) queryParams.set('page_size', params.page_size.toString());
        if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
        if (params?.order) queryParams.set('order', params.order);

        const url = `${this.apiUrl}/history?${queryParams.toString()}`;
        return this.http.get<HistoryResponse>(url);
    }

    /**
     * 获取历史记录详情
     */
    getHistoryDetail(analysisId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/history/${analysisId}/detail`);
    }

    // ==================== Token 管理 ====================

    /**
     * 保存 Token
     */
    private saveToken(token: string): void {
        localStorage.setItem(this.tokenKey, token);
    }

    /**
     * 获取 Token
     */
    getToken(): string | null {
        return localStorage.getItem(this.tokenKey);
    }
}
