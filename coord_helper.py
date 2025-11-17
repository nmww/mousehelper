#!/usr/bin/env python3
"""
坐标获取助手 - 独立的坐标获取工具
通过文件通信与主程序交互
"""

import pyautogui
import time
import os
from pynput import mouse

def on_click(x, y, button, pressed):
    """鼠标点击事件处理"""
    if pressed and button == mouse.Button.left:
        # 保存坐标到文件
        try:
            with open("temp_coord.txt", "w") as f:
                f.write(f"{x},{y}")
            print(f"坐标已保存: ({x}, {y})")
            print("您可以关闭此窗口了")
            return False  # 停止监听器
        except Exception as e:
            print(f"保存坐标失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 坐标获取助手")
    print("=" * 50)
    print("请将鼠标移动到目标位置，然后点击鼠标左键")
    print("坐标将自动保存到临时文件")
    print("=" * 50)
    
    # 删除旧的临时文件
    try:
        if os.path.exists("temp_coord.txt"):
            os.remove("temp_coord.txt")
    except:
        pass
    
    # 启动鼠标监听器
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    print("监听器已启动，等待鼠标点击...")
    
    # 保持程序运行，直到用户点击
    try:
        listener.join()
    except KeyboardInterrupt:
        print("\n程序已退出")

if __name__ == "__main__":
    main()