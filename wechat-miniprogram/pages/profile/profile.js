// pages/profile/profile.js
const app = getApp();
const { request } = require('../../utils/request');

Page({
    data: {
        userInfo: null,
        stats: {
            points: 0,
            analyses_count: 0,
            best_speed: 0
        }
    },

    onLoad() {
        this.loadUserInfo();
        this.loadUserStats();
    },

    onShow() {
        // 每次显示页面时刷新数据
        this.loadUserInfo();
        this.loadUserStats();
    },

    // 加载用户信息
    loadUserInfo() {
        const userInfo = wx.getStorageSync('userInfo');
        if (userInfo) {
            this.setData({
                userInfo: userInfo
            });
        } else {
            // 如果没有用户信息，尝试从全局获取
            if (app.globalData.userInfo) {
                this.setData({
                    userInfo: app.globalData.userInfo
                });
            } else {
                // 尝试从服务器获取
                this.fetchUserProfile();
            }
        }
    },

    // 从服务器获取用户信息
    async fetchUserProfile() {
        try {
            const data = await request('/auth/profile', { silent: true });
            const userInfo = {
                id: data.id,
                username: data.username,
                nickname: data.nickname,
                email: data.email,
                avatar_url: data.avatar_url,
                points: data.points || 0
            };
            
            wx.setStorageSync('userInfo', userInfo);
            app.globalData.userInfo = userInfo;
            
            this.setData({
                userInfo: userInfo,
                'stats.points': data.points || 0
            });
        } catch (error) {
            console.error('获取用户信息失败:', error);
            // 如果获取失败，可能是未登录，跳转到登录页
            wx.reLaunch({
                url: '/pages/login/login'
            });
        }
    },

    // 加载用户统计数据
    async loadUserStats() {
        try {
            // 获取积分信息和用户信息
            const profileData = await request('/auth/profile', { silent: true });
            
            // 获取历史记录统计
            let analysesCount = 0;
            let bestSpeed = 0;
            
            try {
                const historyData = await request('/history?page=1&page_size=1', { silent: true });
                analysesCount = historyData.total || 0;
                
                // 如果有记录，获取最佳速度
                if (analysesCount > 0) {
                    const allHistory = await request('/history?page=1&page_size=100&sort_by=speed&order=desc', { silent: true });
                    if (allHistory.items && allHistory.items.length > 0) {
                        bestSpeed = allHistory.items[0].speed || 0;
                    }
                }
            } catch (historyError) {
                console.log('获取历史记录失败:', historyError);
                // 历史记录获取失败不影响页面显示
            }
            
            this.setData({
                stats: {
                    points: profileData.points || 0,
                    analyses_count: analysesCount,
                    best_speed: bestSpeed
                }
            });
        } catch (error) {
            console.error('加载统计数据失败:', error);
            // 静默失败，不影响页面显示
        }
    },

    // 返回
    handleBack() {
        const pages = getCurrentPages();
        if (pages.length > 1) {
            wx.navigateBack();
        } else {
            wx.reLaunch({ url: '/pages/index/index' });
        }
    },

    // 处理图片加载错误
    handleImageError(e) {
        console.log('头像加载失败', e);
    },

    // 跳转到历史记录
    goToHistory() {
        // 历史记录在首页显示，这里可以跳转回首页并滚动到记录区域
        wx.switchTab({
            url: '/pages/index/index'
        });
    },

    // 跳转到积分明细（暂时显示提示）
    goToPoints() {
        wx.showModal({
            title: '积分明细',
            content: '积分明细功能开发中，敬请期待！',
            showCancel: false,
            confirmText: '知道了'
        });
    },

    // 显示关于我们
    showAbout() {
        wx.showModal({
            title: '关于我们',
            content: '羽球速 SmashAI\n\n专业的羽毛球杀球速度分析工具，使用 AI 技术帮助您提升技术水平。',
            showCancel: false,
            confirmText: '知道了'
        });
    },

    // 显示使用帮助
    showHelp() {
        wx.showModal({
            title: '使用帮助',
            content: '1. 上传您的杀球视频\n2. 等待 AI 分析\n3. 查看详细报告和速度\n4. 获得专业建议\n\n每次分析消耗 10 积分',
            showCancel: false,
            confirmText: '知道了'
        });
    },

    // 登出
    handleLogout() {
        wx.showModal({
            title: '确认退出',
            content: '确定要退出登录吗？',
            success: (res) => {
                if (res.confirm) {
                    this.doLogout();
                }
            }
        });
    },

    // 执行登出
    doLogout() {
        wx.showLoading({
            title: '退出中...'
        });

        // 清除本地存储
        wx.removeStorageSync('token');
        wx.removeStorageSync('userInfo');
        app.globalData.userInfo = null;

        wx.hideLoading();
        wx.showToast({
            title: '已退出登录',
            icon: 'success'
        });

        // 跳转到登录页面
        setTimeout(() => {
            wx.reLaunch({
                url: '/pages/login/login'
            });
        }, 500);
    }
});
