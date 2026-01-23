// pages/report/report.js
Page({
    data: {
        result: null,
        loading: true
    },

    onLoad(options) {
        // 先设置 loading 状态
        this.setData({
            loading: true,
            result: null
        });
        
        // 使用 nextTick 确保渲染层准备好
        wx.nextTick(() => {
            this.loadAnalysisResult();
        });
    },

    onShow() {
        // 页面显示时也检查数据
        if (!this.data.result && !this.data.loading) {
            this.loadAnalysisResult();
        }
    },

    loadAnalysisResult() {
        const result = wx.getStorageSync('analysisResult');
        if (result) {
            // 确保数据结构正确
            const formattedResult = {
                speed: Number(result.speed) || 0,
                level: String(result.level || '初级'),
                score: Number(result.score) || 0,
                technique: {
                    power: Number(result.technique?.power || result.technique_power || 0),
                    angle: Number(result.technique?.angle || result.technique_angle || 0),
                    coordination: Number(result.technique?.coordination || result.technique_coordination || 0)
                },
                rank: Number(result.rank) || 0,
                rankPosition: Number(result.rank_position || result.rankPosition || 0),
                suggestions: Array.isArray(result.suggestions) ? result.suggestions.map(item => ({
                    title: String(item.title || '建议'),
                    desc: String(item.desc || ''),
                    icon: String(item.icon || '💡'),
                    highlight: String(item.highlight || '')
                })) : []
            };
            
            // 确保数值在合理范围内
            formattedResult.technique.power = Math.min(100, Math.max(0, formattedResult.technique.power));
            formattedResult.technique.angle = Math.min(100, Math.max(0, formattedResult.technique.angle));
            formattedResult.technique.coordination = Math.min(100, Math.max(0, formattedResult.technique.coordination));
            
            console.log('格式化后的结果:', formattedResult);
            
            // 先设置 loading 为 false，再设置数据
            this.setData({
                loading: false
            }, () => {
                // 使用 nextTick 确保渲染层准备好
                wx.nextTick(() => {
                    this.setData({
                        result: formattedResult
                    }, () => {
                        console.log('数据设置完成');
                    });
                });
            });
        } else {
            this.setData({
                loading: false
            });
            wx.showToast({
                title: '没有分析结果',
                icon: 'none'
            });
            setTimeout(() => {
                wx.navigateBack();
            }, 1500);
        }
    },

    handleBack() {
        wx.navigateBack();
    },

    // 分享功能
    handleShare() {
        wx.showShareMenu({
            withShareTicket: true,
            menus: ['shareAppMessage', 'shareTimeline']
        });
    },

    // 格式化建议
    formatSuggestions(suggestions) {
        if (!suggestions || !Array.isArray(suggestions)) {
            return [];
        }
        // 图标映射：将 Material Design 图标名转换为 emoji
        const iconMap = {
            'mdi-motion': '🏃',
            'mdi-badminton': '🏸',
            'mdi-arm-flex': '💪',
            'directions_run': '🏃',
            'flight': '✈️',
            'fitness_center': '💪',
            'motion': '🏃',
            'badminton': '🏸',
            'arm-flex': '💪'
        };
        
        return suggestions.map(item => {
            let icon = item.icon || '💡';
            // 如果是 Material Design 图标名，转换为 emoji
            if (icon.startsWith('mdi-') || icon.includes('_') || icon.includes('-')) {
                const key = icon.toLowerCase().replace(/-/g, '_');
                icon = iconMap[icon] || iconMap[key] || '💡';
            }
            // 确保图标是 emoji，不是文本
            if (icon.length > 2 && !/[\u{1F300}-\u{1F9FF}]/u.test(icon)) {
                // 如果不是 emoji，使用默认图标
                icon = '💡';
            }
            return {
                title: item.title || '建议',
                desc: item.desc || '',
                icon: icon.substring(0, 2),  // 只取前2个字符（一个emoji）
                highlight: item.highlight || ''
            };
        });
    }
})
