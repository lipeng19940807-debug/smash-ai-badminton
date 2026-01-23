// pages/index/index.js
const { request, BASE_URL } = require('../../utils/request');
const app = getApp();

Page({
    data: {
        isAnalyzing: false,
        statusText: '等待上传',
        userInfo: null,
        isLoggedIn: false,
        // 历史记录数据
        recentRecords: [],
        // 统计数据
        stats: {
            totalSmash: 0,
            maxSpeed: 0,
            avgScore: 0
        },
        // Hero卡片数据
        heroData: {
            bestSpeed: 0,
            rank: 0,
            level: '初级'
        }
    },

    onLoad() {
        this.checkLoginStatus();
        this.loadUserData();
    },

    onShow() {
        // 页面显示时检查登录状态
        this.checkLoginStatus();
        if (this.data.isLoggedIn) {
            this.loadUserData();
        }
    },

    // 检查登录状态
    checkLoginStatus() {
        const token = wx.getStorageSync('token');
        const userInfo = wx.getStorageSync('userInfo') || app.globalData.userInfo;
        
        if (token && userInfo) {
            this.setData({
                isLoggedIn: true,
                userInfo: userInfo
            });
            app.globalData.userInfo = userInfo;
        } else {
            this.setData({
                isLoggedIn: false,
                userInfo: null
            });
        }
    },

    // 加载用户数据
    async loadUserData() {
        if (!this.data.isLoggedIn) return;

        try {
            // 加载历史记录（使用 silent 模式，避免频繁弹窗）
            const historyRes = await request('/history', {
                method: 'GET',
                data: {
                    page: 1,
                    page_size: 10,
                    sort_by: 'analyzed_at',
                    order: 'desc'
                },
                silent: true  // 静默模式，不显示错误提示
            });

            if (historyRes && historyRes.items) {
                // 处理历史记录
                const { BASE_URL } = require('../../utils/request');
                const records = historyRes.items.map(item => {
                    // 构建完整的缩略图 URL
                    let thumbnailUrl = '';
                    if (item.thumbnail_url) {
                        // 如果已经是完整 URL，直接使用；否则拼接 BASE_URL
                        if (item.thumbnail_url.startsWith('http')) {
                            thumbnailUrl = item.thumbnail_url;
                        } else {
                            // 移除 BASE_URL 中的 /api 后缀，然后拼接
                            const baseUrl = BASE_URL.replace('/api', '');
                            thumbnailUrl = baseUrl + (item.thumbnail_url.startsWith('/') ? item.thumbnail_url : '/' + item.thumbnail_url);
                        }
                    }
                    
                    return {
                        id: item.id,
                        speed: item.speed,
                        score: item.score,
                        level: item.level,
                        thumbnail: thumbnailUrl,
                        date: this.formatDate(item.analyzed_at),
                        title: this.getRecordTitle(item),
                        count: 1 // 每次分析算一次杀球
                    };
                });

                // 计算统计数据
                const stats = {
                    totalSmash: historyRes.total || 0,
                    maxSpeed: records.length > 0 ? Math.max(...records.map(r => r.speed)) : 0,
                    avgScore: records.length > 0 
                        ? (records.reduce((sum, r) => sum + r.score, 0) / records.length).toFixed(1)
                        : 0
                };

                // Hero数据
                const heroData = {
                    bestSpeed: stats.maxSpeed,
                    rank: records.length > 0 ? Math.floor(Math.random() * 500) + 1 : 0,
                    level: this.getLevel(stats.maxSpeed)
                };

                this.setData({
                    recentRecords: records.slice(0, 6),
                    stats: stats,
                    heroData: heroData
                });
            }
        } catch (error) {
            console.error('加载用户数据失败', error);
            // 静默失败，不影响页面显示
            // 如果是连接重置错误，可能是后端重启，稍后会自动重试
            if (error.errMsg && error.errMsg.includes('reset')) {
                console.log('连接重置，可能是后端服务重启，将在下次 onShow 时重试');
            }
        }
    },

    // 格式化日期
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${year}年${month}月${day}日`;
    },

    // 获取记录标题
    getRecordTitle(item) {
        const titles = ['早间专项练习', '训练建议', '技术提升', '杀球分析'];
        const index = parseInt(item.id.slice(-1)) % titles.length;
        return titles[index] || `杀球分析 - ${item.speed}km/h`;
    },

    // 获取等级
    getLevel(speed) {
        if (speed >= 300) return '职业级';
        if (speed >= 250) return '精英级';
        if (speed >= 200) return '高级';
        if (speed >= 150) return '中级';
        return '初级';
    },

    // 手动登录 - 跳转到登录页面
    // 跳转到个人中心
    goToProfile() {
        wx.navigateTo({
            url: '/pages/profile/profile'
        });
    },

    handleLogin() {
        wx.navigateTo({
            url: '/pages/login/login'
        });
    },

    // 选择视频
    handleChooseVideo() {
        // 检查登录状态
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showModal({
                title: '需要登录',
                content: '上传视频需要先登录，是否前往登录？',
                success: (res) => {
                    if (res.confirm) {
                        wx.navigateTo({
                            url: '/pages/login/login'
                        });
                    }
                }
            });
            return;
        }

        wx.chooseMedia({
            count: 1,
            mediaType: ['video'],
            sourceType: ['album', 'camera'],
            maxDuration: 60,
            camera: 'back',
            success: (res) => {
                const tempFilePath = res.tempFiles[0].tempFilePath;
                // 优先使用云存储上传
                this.uploadToCloud(tempFilePath);
            },
            fail: (err) => {
                console.error('选择视频失败', err);
                wx.showToast({
                    title: '选择视频失败',
                    icon: 'none'
                });
            }
        });
    },

    // 使用微信云存储上传视频
    uploadToCloud(filePath) {
        this.setData({ isAnalyzing: true, statusText: '正在安全上传...' });
        
        // 生成云端路径
        const cloudPath = `videos/${Date.now()}-${Math.floor(Math.random() * 1000)}.mp4`;

        wx.cloud.uploadFile({
            cloudPath: cloudPath,
            filePath: filePath,
            success: res => {
                console.log('云存储上传成功', res.fileID);
                // 上传成功后，将 fileID 发送给后端
                this.notifyBackend(res.fileID);
            },
            fail: err => {
                console.error('云存储上传失败', err);
                this.handleError('安全上传失败，请重试');
            }
        });
    },

    // 通知后端处理云存储中的视频
    async notifyBackend(fileID) {
        this.setData({ statusText: '正在同步数据...' });
        try {
            const data = await request('/video/cloud-upload', {
                method: 'POST',
                data: { file_id: fileID }
            });
            this.startAnalysis(data.id);
        } catch (e) {
            console.error('同步失败', e);
            this.handleError('数据同步失败');
        }
    },

    // 原有的 uploadVideo 逻辑可以保留作为备份，或者直接删除
    uploadVideo(filePath) {
        // ... 原有逻辑 ...
    },

    // 开始分析
    async startAnalysis(videoId) {
        this.setData({ statusText: 'AI 正在分析动作 (约15秒)...' });

        try {
            const result = await request('/analysis/start', {
                method: 'POST',
                data: { video_id: videoId }
            });

            this.setData({ isAnalyzing: false });

            // 确保数据格式正确
            const formattedResult = {
                ...result,
                rank_position: result.rank_position || result.rankPosition || 0,
                rankPosition: result.rank_position || result.rankPosition || 0
            };
            
            // 保存结果并跳转
            wx.setStorageSync('analysisResult', formattedResult);
            
            // 使用延迟确保数据已保存
            setTimeout(() => {
                wx.navigateTo({
                    url: '/pages/report/report',
                    success: () => {
                        console.log('跳转到报告页面成功');
                    },
                    fail: (err) => {
                        console.error('跳转失败', err);
                        wx.showToast({
                            title: '页面跳转失败',
                            icon: 'none'
                        });
                    }
                });
            }, 100);

        } catch (error) {
            console.error('分析失败', error);
            let errorMsg = '分析失败';
            
            // 提取错误信息
            if (error.data) {
                if (error.data.detail) {
                    errorMsg = error.data.detail;
                } else if (error.data.message) {
                    errorMsg = error.data.message;
                } else if (typeof error.data === 'string') {
                    errorMsg = error.data;
                }
            } else if (error.detail) {
                errorMsg = error.detail;
            } else if (error.errMsg) {
                errorMsg = error.errMsg;
            } else if (error.message) {
                errorMsg = error.message;
            }
            
            // 限制错误信息长度
            if (errorMsg.length > 200) {
                errorMsg = errorMsg.substring(0, 200) + '...';
            }
            
            this.setData({ isAnalyzing: false });
            this.handleError(errorMsg);
        }
    },

    // 错误处理
    handleError(msg) {
        this.setData({ isAnalyzing: false, statusText: msg });
        wx.showToast({ title: msg, icon: 'none', duration: 3000 });
    },

    // 查看历史记录详情
    viewRecordDetail(e) {
        const recordId = e.currentTarget.dataset.id;
        // 可以跳转到详情页或报告页
        wx.showToast({
            title: '功能开发中',
            icon: 'none'
        });
    },

    // 切换到个人中心
    switchToProfile() {
        wx.showToast({
            title: '功能开发中',
            icon: 'none'
        });
    },

    // 图片加载错误处理
    handleImageError(e) {
        const type = e.currentTarget.dataset.type;
        console.log(`图片加载失败 (${type})`, e.detail);
        // 静默处理，不显示错误提示
    }
})
