#!/usr/bin/env python3
"""
AppGraveyard 🪦 - Cross Platform Version
Find the apps you buried but never use.
"""

import sys
import os
import tkinter as tk

# 检测操作系统并导入相应的扫描器
if sys.platform.startswith('win'):
    from cross_platform_scanner import AppScanner
elif sys.platform.startswith('darwin'):
    from cross_platform_scanner import AppScanner
elif sys.platform.startswith('linux'):
    from cross_platform_scanner import AppScanner
else:
    print(f"Unsupported platform: {sys.platform}")
    sys.exit(1)

from scoring import AppScorer
from ui_fixed import AppGraveyardUI

def main():
    """主函数"""
    platform_name = {
        'win32': 'Windows',
        'darwin': 'macOS', 
        'linux': 'Linux'
    }.get(sys.platform, sys.platform)
    
    print(f"AppGraveyard 🪦 - 正在扫描 {platform_name} 上已安装的程序...")
    
    try:
        # 扫描已安装的程序
        scanner = AppScanner()
        apps = scanner.scan_installed_programs()
        print(f"找到 {len(apps)} 个已安装的程序")
        
        # 调试：打印前几个程序的详细信息
        for i, app in enumerate(apps[:3]):
            print(f"  {i+1}. {app.get('name', 'Unknown')}")
            print(f"     安装位置: {app.get('install_location', 'N/A')}")
            print(f"     大小: {app.get('size', 0)} bytes")
            if sys.platform.startswith('win'):
                print(f"     卸载字符串: {app.get('uninstall_string', 'N/A')[:50]}...")
        
        # 获取最后访问时间并计算分数
        scorer = AppScorer()
        enhanced_apps = []
        
        for app in apps:
            # 获取最后访问时间
            last_access = scanner.get_last_access_time(app)
            app['last_access_time'] = last_access
            
            # 计算分数和状态
            score_info = scorer.calculate_score(app)
            app.update(score_info)
            
            enhanced_apps.append(app)
        
        print(f"处理完成，准备显示界面...")
        
        # 启动UI
        ui = AppGraveyardUI(enhanced_apps)
        ui.run()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        # 如果GUI失败，显示错误对话框
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        tk.messagebox.showerror("AppGraveyard 错误", f"发生错误:\n{e}\n\n请查看控制台获取详细错误信息。")
        root.destroy()

if __name__ == "__main__":
    main()