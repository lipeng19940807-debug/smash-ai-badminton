// pages/login/login.js
const app = getApp();
const { request } = require('../../utils/request');

Page({
    data: {
        authMode: 'login', // 默认显示登录模式
        formData: {
            username: '', // 登录用
            nickname: '', // 注册用
            email: '',
            password: ''
        },
        showPassword: false,
        loginError: ''
    },

    onLoad() {
        // 检查是否已登录
        const token = wx.getStorageSync('token');
        if (token) {
            // 已登录，直接跳转
            wx.reLaunch({ url: '/pages/index/index' });
        }
    },

    // 切换登录/注册模式
    switchAuthMode(e) {
        const mode = e.currentTarget.dataset.mode;
        this.setData({
            authMode: mode,
            loginError: '',
            formData: {
                username: '',
                nickname: '',
                email: '',
                password: ''
            },
            showPassword: false
        });
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

    // 输入处理
    onUsernameInput(e) {
        this.setData({
            'formData.username': e.detail.value
        });
    },

    onNicknameInput(e) {
        this.setData({
            'formData.nickname': e.detail.value
        });
    },

    onEmailInput(e) {
        this.setData({
            'formData.email': e.detail.value
        });
    },

    onPasswordInput(e) {
        this.setData({
            'formData.password': e.detail.value
        });
    },

    // 切换密码显示
    togglePassword() {
        this.setData({
            showPassword: !this.data.showPassword
        });
    },

    // 微信一键登录
    async handleWeChatLogin() {
        this.setData({ loginError: '' });
        wx.showLoading({ title: '登录中...' });
        
        try {
            await app.login();
            wx.hideLoading();
            wx.showToast({
                title: '登录成功',
                icon: 'success'
            });
            setTimeout(() => {
                wx.reLaunch({ url: '/pages/index/index' });
            }, 500);
        } catch (err) {
            wx.hideLoading();
            console.error('微信登录失败', err);
            
            let errorMsg = '微信登录失败';
            if (err.errMsg) {
                if (err.errMsg.includes('ERR_CONNECTION_REFUSED') || err.errMsg.includes('fail')) {
                    errorMsg = '无法连接到服务器\n\n请检查：\n1. 后端服务是否已启动\n2. IP地址是否正确\n3. 是否勾选了"不校验合法域名"';
                } else {
                    errorMsg = err.errMsg;
                }
            } else if (err.detail) {
                errorMsg = err.detail;
            }
            
            this.setData({ loginError: errorMsg });
            wx.showModal({
                title: '登录失败',
                content: errorMsg,
                showCancel: false,
                confirmText: '知道了'
            });
        }
    },

    // 提交表单
    async handleSubmit() {
        const { authMode, formData } = this.data;

        // 验证表单
        if (authMode === 'register') {
            // 注册验证
            if (!formData.nickname || formData.nickname.trim().length < 3) {
                wx.showToast({
                    title: '昵称至少3个字符',
                    icon: 'none'
                });
                return;
            }

            if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
                wx.showToast({
                    title: '邮箱格式不正确',
                    icon: 'none'
                });
                return;
            }

            if (!formData.password || formData.password.length < 6) {
                wx.showToast({
                    title: '密码至少6位',
                    icon: 'none'
                });
                return;
            }
        } else {
            // 登录验证
            if (!formData.username || formData.username.trim() === '') {
                wx.showToast({
                    title: '请输入用户名',
                    icon: 'none'
                });
                return;
            }

            if (!formData.password || formData.password.trim() === '') {
                wx.showToast({
                    title: '请输入密码',
                    icon: 'none'
                });
                return;
            }
        }

        this.setData({ loginError: '' });
        wx.showLoading({ title: authMode === 'register' ? '注册中...' : '登录中...' });

        try {
            if (authMode === 'register') {
                // 注册逻辑
                const result = await request('/auth/register', {
                    method: 'POST',
                    data: {
                        username: formData.nickname.trim(),
                        password: formData.password,
                        email: formData.email.trim() || undefined,
                        nickname: formData.nickname.trim()
                    }
                });

                wx.hideLoading();
                wx.showToast({
                    title: '注册成功',
                    icon: 'success'
                });

                // 保存token并跳转
                wx.setStorageSync('token', result.token);
                wx.setStorageSync('userInfo', {
                    id: result.id,
                    username: result.username,
                    nickname: result.nickname
                });

                setTimeout(() => {
                    wx.reLaunch({ url: '/pages/index/index' });
                }, 1000);
            } else {
                // 账号密码登录逻辑
                const result = await request('/auth/login', {
                    method: 'POST',
                    data: {
                        username: formData.username.trim(),
                        password: formData.password
                    }
                });

                wx.hideLoading();
                wx.showToast({
                    title: '登录成功',
                    icon: 'success'
                });

                // 保存token和用户信息
                wx.setStorageSync('token', result.access_token);
                wx.setStorageSync('userInfo', result.user);
                app.globalData.userInfo = result.user;

                setTimeout(() => {
                    wx.reLaunch({ url: '/pages/index/index' });
                }, 500);
            }
        } catch (err) {
            wx.hideLoading();
            console.error('操作失败', err);
            
            let errorMsg = authMode === 'register' ? '注册失败' : '登录失败';
            
            // 处理不同类型的错误
            if (err.errMsg) {
                // 网络错误
                if (err.errMsg.includes('ERR_CONNECTION_REFUSED') || err.errMsg.includes('fail')) {
                    errorMsg = '无法连接到服务器\n\n请检查：\n1. 后端服务是否已启动\n2. IP地址是否正确\n3. 是否勾选了"不校验合法域名"';
                } else if (err.errMsg === 'request:ok') {
                    // request:ok 表示请求已发送，但可能返回了错误状态码
                    // 需要从 err.data 中提取错误信息
                    if (err.data) {
                        if (err.data.detail) {
                            errorMsg = err.data.detail;
                        } else if (err.data.message) {
                            errorMsg = err.data.message;
                        } else if (typeof err.data === 'string') {
                            errorMsg = err.data;
                        }
                    }
                    if (errorMsg === (authMode === 'register' ? '注册失败' : '登录失败')) {
                        errorMsg = '服务器返回错误，请稍后重试';
                    }
                } else {
                    errorMsg = err.errMsg;
                }
            } else if (err.detail) {
                // 直接错误详情
                errorMsg = err.detail;
            } else if (err.data) {
                // 响应数据中的错误
                if (err.data.detail) {
                    errorMsg = err.data.detail;
                } else if (err.data.message) {
                    errorMsg = err.data.message;
                } else if (typeof err.data === 'string') {
                    errorMsg = err.data;
                }
            } else if (err.message) {
                errorMsg = err.message;
            }
            
            // 限制错误信息长度
            if (errorMsg.length > 200) {
                errorMsg = errorMsg.substring(0, 200) + '...';
            }
            
            this.setData({ loginError: errorMsg });
            
            wx.showModal({
                title: authMode === 'register' ? '注册失败' : '登录失败',
                content: errorMsg,
                showCancel: false,
                confirmText: '知道了'
            });
        }
    }
})
