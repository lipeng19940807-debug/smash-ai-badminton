#!/usr/bin/env python3
"""
配置向导脚本
帮助用户配置 Supabase 和 Gemini API
"""
import os
import sys

def colored(text, color_code):
    """输出彩色文本"""
    return f"\033[{color_code}m{text}\033[0m"

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(colored(text, "1;36"))  # 青色粗体
    print("=" * 60 + "\n")

def print_step(step_num, text):
    """打印步骤"""
    print(colored(f"步骤 {step_num}:", "1;33"), text)  # 黄色粗体

def print_success(text):
    """打印成功消息"""
    print(colored(f"✓ {text}", "1;32"))  # 绿色粗体

def print_error(text):
    """打印错误消息"""
    print(colored(f"✗ {text}", "1;31"))  # 红色粗体

def read_env_file():
    """读取 .env 文件"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        return {}
    
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def write_env_file(env_vars):
    """写入 .env 文件"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    with open(env_path, 'w') as f:
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
                else:
                    f.write(line)
            else:
                f.write(line)

def main():
    """主函数"""
    print_header("🏸 羽毛球杀球分析 - 配置向导")
    
    print("欢迎！此向导将帮助你配置后端服务。\n")
    
    # 读取现有配置
    env_vars = read_env_file()
    
    # 配置 Supabase
    print_step(1, "配置 Supabase 数据库")
    print("\n请访问: https://app.supabase.com")
    print("1. 创建或选择一个项目")
    print("2. 进入 Settings → API\n")
    
    supabase_url = input(colored("请输入 Project URL: ", "1;37")).strip()
    if supabase_url:
        env_vars['SUPABASE_URL'] = supabase_url
        print_success("Supabase URL 已保存")
    else:
        print_error("跳过 Supabase URL 配置")
    
    supabase_key = input(colored("请输入 anon / public Key: ", "1;37")).strip()
    if supabase_key:
        env_vars['SUPABASE_KEY'] = supabase_key
        print_success("Supabase Key 已保存")
    else:
        print_error("跳过 Supabase Key 配置")
    
    # 配置 Gemini API
    print("\n")
    print_step(2, "配置 Gemini API")
    print("\n如果你已有 Gemini API Key，请输入")
    print("如果没有，请访问: https://makersuite.google.com/app/apikey\n")
    
    gemini_key = input(colored("请输入 Gemini API Key (留空跳过): ", "1;37")).strip()
    if gemini_key:
        env_vars['GEMINI_API_KEY'] = gemini_key
        print_success("Gemini API Key 已保存")
    else:
        # 尝试从前端配置读取
        frontend_env = os.path.join(os.path.dirname(__file__), '..', '..', '.env.local')
        if os.path.exists(frontend_env):
            with open(frontend_env, 'r') as f:
                for line in f:
                    if 'GEMINI_API_KEY' in line and '=' in line:
                        _, value = line.split('=', 1)
                        value = value.strip()
                        if value and value != 'PLACEHOLDER_API_KEY':
                            use_frontend = input(colored(f"检测到前端配置的 API Key，是否使用？(y/n): ", "1;37")).strip().lower()
                            if use_frontend == 'y':
                                env_vars['GEMINI_API_KEY'] = value
                                print_success("使用前端的 Gemini API Key")
                            break
    
    # 写入配置
    write_env_file(env_vars)
    
    print("\n")
    print_header("✅ 配置完成")
    
    # 检查是否所有必需的配置都已填写
    required_keys = ['SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
    missing_keys = [k for k in required_keys if not env_vars.get(k) or env_vars[k].startswith('your-') or env_vars[k] == 'PLACEHOLDER_API_KEY']
    
    if missing_keys:
        print_error(f"以下配置尚未填写: {', '.join(missing_keys)}")
        print("\n你可以稍后手动编辑 backend/.env 文件")
    else:
        print_success("所有必需配置已完成！")
    
    print("\n下一步:")
    print("1. 在 Supabase Dashboard 的 SQL Editor 中执行数据库初始化脚本")
    print("   运行: python scripts/init_db.py")
    print("2. 启动后端服务:")
    print(colored("   python run.py", "1;32"))
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n配置已取消")
        sys.exit(0)
