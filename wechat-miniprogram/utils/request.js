// 开发环境配置
// 注意：在微信开发者工具中，需要勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
// 路径：工具栏 -> 详情 -> 本地设置 -> 不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书

// 导入配置
const config = require('./config');
const BASE_URL = config.BASE_URL;

/**
 * 通用请求工具类
 * 支持微信云托管调用和普通 HTTPS 调用
 */
const request = (url, options = {}) => {
    return new Promise((resolve, reject) => {
        // 获取 Token
        const token = wx.getStorageSync('token');

        // 如果配置了使用云托管，则优先使用云托管
        // 这里可以根据配置决定是使用 wx.cloud.callContainer 还是 wx.request
        const useCloud = true; // 后续可以改为动态配置

        if (useCloud && wx.cloud) {
            wx.cloud.callContainer({
                config: {
                    env: 'cloud1-1grfk67f82062cc1',
                },
                path: `/api${url}`, // 微信云托管会自动转发到容器内部
                header: {
                    'X-WX-SERVICE': 'smashai-backend', // 替换为你的云托管服务名
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...options.header
                },
                method: options.method || 'GET',
                data: options.data || {},
                success: (res) => {
                    // 云托管返回的 res.data 才是真实的业务响应
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else if (res.statusCode === 401) {
                        handleAuthError(options.silent);
                        reject(res);
                    } else {
                        handleGeneralError(res, options.silent);
                        reject(res);
                    }
                },
                fail: (err) => {
                    handleNetworkError(err, options.silent);
                    reject(err);
                }
            });
        } else {
            // 原有的 wx.request 逻辑作为兜底
            wx.request({
                url: `${BASE_URL}${url}`,
                method: options.method || 'GET',
                data: options.data || {},
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...options.header
                },
                success: (res) => {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else if (res.statusCode === 401) {
                        handleAuthError(options.silent);
                        reject(res);
                    } else {
                        handleGeneralError(res, options.silent);
                        reject(res);
                    }
                },
                fail: (err) => {
                    handleNetworkError(err, options.silent);
                    reject(err);
                }
            });
        }
    });
};

/**
 * 处理身份验证错误
 */
function handleAuthError(silent) {
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    if (!silent) {
        wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
        });
    }
    wx.reLaunch({
        url: '/pages/login/login',
    });
}

/**
 * 处理通用业务错误
 */
function handleGeneralError(res, silent) {
    let errorMsg = `请求失败 (${res.statusCode})`;
    if (res.data) {
        if (res.data.detail) {
            errorMsg = res.data.detail;
        } else if (res.data.message) {
            errorMsg = res.data.message;
        } else if (typeof res.data === 'string') {
            errorMsg = res.data;
        }
    }
    
    if (!silent) {
        wx.showToast({
            title: errorMsg.length > 50 ? errorMsg.substring(0, 50) + '...' : errorMsg,
            icon: 'none',
            duration: 3000
        });
    }
}

/**
 * 处理网络错误
 */
function handleNetworkError(err, silent) {
    console.error('网络请求失败:', err);
    let errorMsg = '网络连接失败';
    
    if (err.errMsg) {
        if (err.errMsg.includes('ERR_CONNECTION_REFUSED') || err.errMsg.includes('fail')) {
            errorMsg = '无法连接到服务器，请检查后端服务是否已启动';
        } else if (err.errMsg.includes('timeout')) {
            errorMsg = '请求超时，请检查网络连接';
        }
    }
    
    if (!silent) {
        wx.showModal({
            title: '网络错误',
            content: errorMsg,
            showCancel: false,
            confirmText: '知道了'
        });
    }
}

module.exports = {
    request,
    BASE_URL
};
