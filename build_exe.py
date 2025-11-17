#!/usr/bin/env python3
"""
构建鼠标点击助手的exe可执行文件
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller安装完成")

def build_exe():
    """构建exe文件"""
    print("正在构建exe可执行文件...")
    
    # 创建dist目录（如果不存在）
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--name=鼠标点击助手",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 窗口程序，不显示控制台
        "--icon=NONE",  # 没有图标
        "--add-data=mousehelper.png;.",  # 包含图片文件
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=pynput.mouse._win32",
        "--clean",  # 清理临时文件
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ exe文件构建成功！")
        print("📁 可执行文件位置: dist/鼠标点击助手.exe")
        
        # 复制README和LICENSE到dist目录
        if os.path.exists("README.md"):
            shutil.copy2("README.md", "dist/")
        if os.path.exists("LICENSE"):
            shutil.copy2("LICENSE", "dist/")
        if os.path.exists("mousehelper.png"):
            shutil.copy2("mousehelper.png", "dist/")
            
        print("📄 相关文档已复制到dist目录")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    
    return True

def create_release_zip():
    """创建发布压缩包"""
    print("\n正在创建发布压缩包...")
    
    import zipfile
    import datetime
    
    # 获取当前日期
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    zip_filename = f"鼠标点击助手_v1.0_{current_date}.zip"
    
    # 创建zip文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加exe文件
        if os.path.exists("dist/鼠标点击助手.exe"):
            zipf.write("dist/鼠标点击助手.exe", "鼠标点击助手.exe")
        
        # 添加文档
        if os.path.exists("dist/README.md"):
            zipf.write("dist/README.md", "README.md")
        if os.path.exists("dist/LICENSE"):
            zipf.write("dist/LICENSE", "LICENSE")
        if os.path.exists("dist/mousehelper.png"):
            zipf.write("dist/mousehelper.png", "mousehelper.png")
    
    print(f"✅ 发布包创建成功: {zip_filename}")
    return zip_filename

def main():
    """主函数"""
    print("=" * 50)
    print("🐭 鼠标点击助手 - EXE构建工具")
    print("=" * 50)
    
    # 检查是否安装了PyInstaller
    try:
        import pyinstaller
    except ImportError:
        print("⚠️  未检测到PyInstaller，正在安装...")
        install_pyinstaller()
    
    # 构建exe
    if build_exe():
        # 创建发布包
        zip_file = create_release_zip()
        
        print("\n" + "=" * 50)
        print("🎉 构建完成！")
        print("📦 发布文件:")
        print(f"   - {zip_file}")
        print("\n📋 发布到GitHub的步骤:")
        print("1. 在GitHub创建新的Release")
        print("2. 上传上面的zip文件")
        print("3. 添加发布说明")
        print("4. 发布！")
        print("=" * 50)
    else:
        print("\n❌ 构建失败，请检查错误信息")

if __name__ == "__main__":
    main()