#!/usr/bin/env python3
"""
AppGraveyard CLI - 命令行版本用于测试
"""

import sys
import os
from cross_platform_scanner import CrossPlatformScanner
from scoring import AppScorer

def main():
    """主函数 - 命令行版本"""
    print("AppGraveyard 🪦 - 正在扫描已安装的程序...")
    
    try:
        # 扫描已安装的程序
        scanner = CrossPlatformScanner()
        apps = scanner.scan_installed_programs()
        print(f"找到 {len(apps)} 个已安装的程序")
        
        if not apps:
            print("没有找到任何应用程序。这可能是因为:")
            print("- 在Windows上运行但缺少winreg模块")
            print("- 在Linux/Mac上但没有找到可执行文件")
            return
        
        # 获取最后访问时间并计算分数
        scorer = AppScorer()
        enhanced_apps = []
        
        for app in apps[:20]:  # 限制显示数量
            # 获取最后访问时间
            last_access = scanner.get_last_access_time(app)
            app['last_access_time'] = last_access
            
            # 计算分数和状态
            score_info = scorer.calculate_score(app)
            app.update(score_info)
            
            enhanced_apps.append(app)
        
        print(f"\n处理完成，显示前 {len(enhanced_apps)} 个应用:")
        print("-" * 80)
        print(f"{'程序名':<30} {'大小':<10} {'上次使用':<15} {'状态':<15}")
        print("-" * 80)
        
        # 按分数排序（高分在前）
        sorted_apps = sorted(enhanced_apps, key=lambda x: x.get('score', 0), reverse=True)
        
        for app in sorted_apps:
            name = app.get('name', 'Unknown')[:29]
            size_bytes = app.get('size', 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024**2:
                size_str = f"{size_bytes//1024}KB"
            elif size_bytes < 1024**3:
                size_str = f"{size_bytes//(1024**2)}MB"
            else:
                size_str = f"{size_bytes//(1024**3)}GB"
            
            days = app.get('days_since_last_use', 'N/A')
            if days != 'N/A':
                days_str = f"{days}天前"
            else:
                days_str = "未知"
            
            status = app.get('status', '未知')
            print(f"{name:<30} {size_str:<10} {days_str:<15} {status:<15}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()