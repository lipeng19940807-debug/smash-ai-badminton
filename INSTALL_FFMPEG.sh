#!/bin/bash
# FFmpeg 安装脚本
# 使用方法：在终端中运行：bash INSTALL_FFMPEG.sh

echo "=========================================="
echo "开始安装 FFmpeg"
echo "=========================================="

# 检查是否已安装 Homebrew
if ! command -v brew &> /dev/null; then
    echo "检测到 Homebrew 未安装，开始安装 Homebrew..."
    echo "注意：安装过程中可能需要输入您的管理员密码"
    echo ""
    
    # 安装 Homebrew
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 将 Homebrew 添加到 PATH（根据安装位置）
    if [ -f "/opt/homebrew/bin/brew" ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f "/usr/local/bin/brew" ]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew 已安装"
fi

# 检查 Homebrew 是否可用
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew 安装失败或未正确配置 PATH"
    echo "请手动运行以下命令："
    echo '  eval "$(/opt/homebrew/bin/brew shellenv)"  # Apple Silicon Mac'
    echo '  或'
    echo '  eval "$(/usr/local/bin/brew shellenv)"     # Intel Mac'
    exit 1
fi

echo ""
echo "开始安装 FFmpeg..."
brew install ffmpeg

echo ""
echo "验证安装..."
if command -v ffmpeg &> /dev/null && command -v ffprobe &> /dev/null; then
    echo "✅ FFmpeg 安装成功！"
    echo ""
    echo "版本信息："
    ffmpeg -version | head -1
    ffprobe -version | head -1
else
    echo "❌ FFmpeg 安装失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "安装完成！现在可以正常使用视频上传功能了"
echo "=========================================="
