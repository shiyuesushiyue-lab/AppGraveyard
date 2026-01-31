#!/usr/bin/env python3
"""
AppGraveyard 🪦
Find the apps you buried but never use.
"""

import sys
import os
import tkinter as tk
from scanner import AppScanner
from scoring import AppScorer
from ui import AppGraveyardUI

def main():
    """主函数"""
    print("AppGraveyard 🪦 - 正在扫描已安装的程序...")
    
    try:
        # 扫描已安装的程序
        scanner = AppScanner()
        apps = scanner.scan_installed_programs()
        print(f"找到 {len(apps)} 个已安装的程序")
        
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
        # 如果GUI失败，显示错误对话框
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        tk.messagebox.showerror("AppGraveyard 错误", f"发生错误:\n{e}")
        root.destroy()

if __name__ == "__main__":
    main()