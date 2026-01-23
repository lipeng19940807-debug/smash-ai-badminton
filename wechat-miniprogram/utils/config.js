// 配置文件
// 根据环境切换不同的 BASE_URL

// 开发环境配置
const DEV_CONFIG = {
    BASE_URL: 'http://192.168.31.54:8000/api', // 开发环境局域网地址，请根据实际情况修改
    // 如果后端运行在本地，可以使用：
    // BASE_URL: 'http://localhost:8000/api',
    // 或者使用本机IP地址（在微信开发者工具中需要勾选"不校验合法域名"）
};

// 生产环境配置
const PROD_CONFIG = {
    BASE_URL: 'https://your-domain.com/api', // 生产环境域名，请替换为实际域名
};

// 当前环境（可以通过编译时切换，或根据域名判断）
// 开发环境：development
// 生产环境：production
const ENV = 'development'; // 或 'production'

// 导出配置
const config = ENV === 'production' ? PROD_CONFIG : DEV_CONFIG;

module.exports = config;
