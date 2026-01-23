// app.js
const { request } = require('./utils/request');

App({
    onLaunch() {
        // 初始化云开发
        if (!wx.cloud) {
            console.error('请使用 2.2.3 或以上的基础库以使用云能力');
        } else {
            wx.cloud.init({
                env: 'cloud1-1grfk67f82062cc1',
                traceUser: true,
            });
        }

        // 检查是否有 token
        const token = wx.getStorageSync('token');
        if (!token) {
            // 无 token，不自动登录，让用户手动登录
            console.log('未检测到登录信息，请手动登录');
        } else {
            // 有 token，尝试获取用户信息验证 token 是否有效
            this.checkToken().catch(err => {
                console.log('Token 验证失败，需要重新登录', err);
            });
        }
    },

    // 检查 token 是否有效
    async checkToken() {
        try {
            // 在云托管环境下，如果 header 中有 X-WX-OPENID，后端会自动返回/创建用户
            const data = await request('/auth/profile', { silent: true });
            if (data && data.id) {
                this.globalData.userInfo = {
                    id: data.id,
                    username: data.username,
                    nickname: data.nickname,
                    avatar_url: data.avatar_url,
                    points: data.points || 0
                };
                wx.setStorageSync('userInfo', this.globalData.userInfo);
                // 如果后端返回了新的 token（用于非云托管环境下的后续调用），可以保存
                if (data.token) {
                    wx.setStorageSync('token', data.token);
                }
                return true;
            }
            return false;
        } catch (error) {
            console.log('Token 验证失败或用户未登录', error);
            return false;
        }
    },

    async login() {
        // 在云开发/云托管环境下，我们可以通过 profile 接口直接实现静默登录
        const success = await this.checkToken();
        if (success) return this.globalData.userInfo;

        // 如果静默登录失败，再走原有的微信登录流程
        return new Promise((resolve, reject) => {
            wx.login({
                success: async (res) => {
                    if (res.code) {
                        try {
                            const data = await request('/auth/wechat', {
                                method: 'POST',
                                data: { code: res.code },
                                silent: true
                            });
                            wx.setStorageSync('token', data.access_token);
                            wx.setStorageSync('userInfo', data.user);
                            this.globalData.userInfo = data.user;
                            resolve(data);
                        } catch (error) {
                            reject(error);
                        }
                    } else {
                        reject(res.errMsg);
                    }
                },
                fail: (err) => reject(err)
            });
        });
    },

    globalData: {
        userInfo: null
    }
})
