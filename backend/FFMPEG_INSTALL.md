# FFmpeg 安装指南

## 问题说明

如果遇到以下错误：
```
无效的视频文件:获取视频信息失败: [Errno 2] No such file or directory: 'ffprobe'
```

这说明系统未安装 FFmpeg 或 FFmpeg 不在 PATH 环境变量中。

## 安装方法

### macOS

#### 方法1：使用 Homebrew（推荐）

1. 如果未安装 Homebrew，先安装：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. 安装 FFmpeg：
```bash
brew install ffmpeg
```

3. 验证安装：
```bash
ffmpeg -version
ffprobe -version
```

#### 方法2：使用 MacPorts

```bash
sudo port install ffmpeg
```

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Windows

1. 访问 https://ffmpeg.org/download.html
2. 下载 Windows 版本
3. 解压到某个目录（如 `C:\ffmpeg`）
4. 将 `C:\ffmpeg\bin` 添加到系统 PATH 环境变量
5. 重启终端或命令行窗口
6. 验证：`ffmpeg -version`

### 验证安装

安装完成后，在终端运行：

```bash
ffmpeg -version
ffprobe -version
```

如果两个命令都能正常显示版本信息，说明安装成功。

## 常见问题

### 1. 安装后仍然报错

**原因：** FFmpeg 可能不在 PATH 中

**解决方法：**
- macOS/Linux: 检查 `which ffmpeg` 和 `which ffprobe`
- 如果返回空，需要将 FFmpeg 的 bin 目录添加到 PATH

### 2. macOS 上 Homebrew 安装失败

**解决方法：**
- 确保 Xcode Command Line Tools 已安装：`xcode-select --install`
- 或者使用 MacPorts 安装

### 3. 权限问题

如果遇到权限错误，可能需要使用 `sudo` 安装（Linux）或输入管理员密码（macOS）。

## 测试视频处理

安装完成后，可以测试后端是否能正常处理视频：

```bash
# 在项目根目录
cd backend
python3 -c "from app.utils.ffmpeg_helper import FFmpegHelper; print('FFmpeg 检查通过')"
```

如果输出 "FFmpeg 检查通过"，说明配置正确。
