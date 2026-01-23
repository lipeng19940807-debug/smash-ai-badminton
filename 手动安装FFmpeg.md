# FFmpeg 手动安装指南

由于自动安装遇到网络问题，请按照以下步骤手动安装 FFmpeg。

## 方法 1：使用 Homebrew（推荐）

### 步骤 1：安装 Homebrew

在终端（Terminal）中运行以下命令：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**注意：**
- 安装过程中会要求输入您的 Mac 管理员密码
- 安装完成后，按照提示将 Homebrew 添加到 PATH

### 步骤 2：配置 Homebrew PATH

安装完成后，根据您的 Mac 类型运行以下命令之一：

**Apple Silicon Mac (M1/M2/M3)：**
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel Mac：**
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

### 步骤 3：安装 FFmpeg

```bash
brew install ffmpeg
```

### 步骤 4：验证安装

```bash
ffmpeg -version
ffprobe -version
```

如果两个命令都能显示版本信息，说明安装成功！

---

## 方法 2：直接下载预编译二进制文件（如果 Homebrew 无法使用）

### 步骤 1：访问 FFmpeg 官网

访问：https://evermeet.cx/ffmpeg/ （macOS 预编译版本）

### 步骤 2：下载文件

下载以下三个文件：
- `ffmpeg` - 主程序
- `ffprobe` - 视频信息工具
- `ffplay`（可选）- 视频播放器

### 步骤 3：安装到系统

1. 打开终端
2. 创建目录（如果不存在）：
```bash
sudo mkdir -p /usr/local/bin
```

3. 将下载的文件移动到系统目录：
```bash
sudo mv ~/Downloads/ffmpeg /usr/local/bin/
sudo mv ~/Downloads/ffprobe /usr/local/bin/
sudo chmod +x /usr/local/bin/ffmpeg
sudo chmod +x /usr/local/bin/ffprobe
```

4. 验证安装：
```bash
ffmpeg -version
ffprobe -version
```

---

## 方法 3：使用 MacPorts（如果已安装 MacPorts）

```bash
sudo port install ffmpeg
```

---

## 验证安装

无论使用哪种方法，安装完成后请运行：

```bash
ffmpeg -version
ffprobe -version
```

如果两个命令都能正常显示版本信息，说明安装成功！

---

## 如果遇到问题

### 问题 1：`command not found: brew`

**解决方法：** 确保已正确配置 PATH，运行：
```bash
eval "$(/opt/homebrew/bin/brew shellenv)"  # Apple Silicon
# 或
eval "$(/usr/local/bin/brew shellenv)"     # Intel
```

### 问题 2：网络连接超时

**解决方法：**
- 检查网络连接
- 尝试使用 VPN 或代理
- 使用方法 2 直接下载预编译文件

### 问题 3：权限问题

**解决方法：** 确保您有管理员权限，某些操作需要 `sudo`

---

## 安装完成后

安装完成后，重启后端服务：

```bash
cd backend
python3 run.py
```

然后就可以正常使用视频上传功能了！
