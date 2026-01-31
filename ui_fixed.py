import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import subprocess
import threading
from typing import List, Dict

class AppGraveyardUI:
    """AppGraveyard的用户界面"""
    
    def __init__(self, apps_data: List[Dict]):
        self.apps_data = apps_data
        self.root = tk.Tk()
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("AppGraveyard 🪦 - 找出你埋葬但从未使用的应用")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建说明标签
        desc_label = ttk.Label(
            main_frame, 
            text="这些是你很久没用但占用大量空间的应用程序",
            font=("Arial", 12, "bold")
        )
        desc_label.pack(pady=(0, 10))
        
        # 创建统计信息
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_apps = len(self.apps_data)
        large_apps = len([app for app in self.apps_data if app.get('size_gb', 0) > 1.0])
        old_apps = len([app for app in self.apps_data if app.get('days_since_last_use', 0) > 90])
        
        stats_text = f"总计: {total_apps} 个应用 | 大型应用 (>1GB): {large_apps} 个 | 长期未用 (>90天): {old_apps} 个"
        stats_label = ttk.Label(stats_frame, text=stats_text, font=("Arial", 10))
        stats_label.pack()
        
        # 创建树形视图
        columns = ("name", "size", "days", "status", "score")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        self.tree.heading("name", text="程序名")
        self.tree.heading("size", text="大小")
        self.tree.heading("days", text="上次使用")
        self.tree.heading("status", text="状态")
        self.tree.heading("score", text="分数")
        
        # 设置列宽
        self.tree.column("name", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80, anchor="center")
        self.tree.column("days", width=100, minwidth=80, anchor="center")
        self.tree.column("status", width=120, minwidth=100, anchor="center")
        self.tree.column("score", width=80, minwidth=60, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # 填充数据
        self.populate_tree()
        
        # 创建底部按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 左侧按钮
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(left_frame, text="重新扫描", command=self.refresh_scan)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_btn = ttk.Button(left_frame, text="导出报告", command=self.export_report)
        export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 右侧按钮
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        help_btn = ttk.Button(right_frame, text="帮助", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        exit_btn = ttk.Button(right_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
    
    def populate_tree(self):
        """填充树形视图数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 按分数排序（高分在前）
        sorted_apps = sorted(self.apps_data, key=lambda x: x.get('score', 0), reverse=True)
        
        for app in sorted_apps:
            name = app.get('name', 'Unknown')
            size_bytes = app.get('size', 0)
            size_str = self._format_size(size_bytes)
            days = app.get('days_since_last_use', 'N/A')
            status = app.get('status', '未知')
            score = app.get('score', 0)
            
            if days != 'N/A':
                days_str = f"{days}天前"
            else:
                days_str = "未知"
            
            score_str = f"{score:.1f}"
            
            self.tree.insert("", "end", values=(name, size_str, days_str, status, score_str))
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        elif size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes // 1024} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes // (1024 ** 2)} MB"
        else:
            return f"{size_bytes // (1024 ** 3)} GB"
    
    def on_double_click(self, event):
        """处理双击事件"""
        item = self.tree.selection()
        if not item:
            return
        
        item = item[0]
        values = self.tree.item(item, "values")
        app_name = values[0]
        
        # 找到对应的app数据
        target_app = None
        for app in self.apps_data:
            if app.get('name') == app_name:
                target_app = app
                break
        
        if target_app:
            self.show_app_details(target_app)
        else:
            messagebox.showinfo("信息", f"无法找到 {app_name} 的详细信息")
    
    def show_app_details(self, app: Dict):
        """显示应用详细信息"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"应用详情: {app.get('name', 'Unknown')}")
        details_window.geometry("500x400")
        details_window.minsize(400, 300)
        
        # 创建文本框显示详细信息
        text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 添加详细信息
        info_lines = []
        info_lines.append(f"应用名称: {app.get('name', 'N/A')}")
        info_lines.append(f"安装位置: {app.get('install_location', 'N/A')}")
        info_lines.append(f"大小: {self._format_size(app.get('size', 0))}")
        info_lines.append(f"安装日期: {app.get('install_date', 'N/A')}")
        info_lines.append(f"上次使用: {app.get('last_access_time', 'N/A')}")
        info_lines.append(f"距离上次使用: {app.get('days_since_last_use', 'N/A')} 天")
        info_lines.append(f"坟墓分数: {app.get('score', 0):.2f}")
        info_lines.append(f"状态: {app.get('status', 'N/A')}")
        info_lines.append(f"卸载命令: {app.get('uninstall_string', 'N/A')}")
        info_lines.append(f"注册表路径: {app.get('registry_path', 'N/A')}")
        
        text_widget.insert(tk.END, "\n".join(info_lines))
        text_widget.config(state=tk.DISABLED)
        
        # 添加按钮
        button_frame = ttk.Frame(details_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        if app.get('uninstall_string'):
            uninstall_btn = ttk.Button(button_frame, text="卸载此应用", 
                                     command=lambda: self.open_uninstall(app, details_window))
            uninstall_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        close_btn = ttk.Button(button_frame, text="关闭", command=details_window.destroy)
        close_btn.pack(side=tk.RIGHT)
    
    def open_uninstall(self, app: Dict, parent_window=None):
        """打开卸载程序"""
        uninstall_string = app.get('uninstall_string')
        if not uninstall_string:
            return
        
        try:
            # 尝试直接执行卸载命令
            if uninstall_string.startswith('"') and '"' in uninstall_string[1:]:
                # 处理带引号的路径
                subprocess.Popen(uninstall_string, shell=True)
            else:
                # 直接执行
                subprocess.Popen(uninstall_string, shell=True)
            
            if parent_window:
                parent_window.destroy()
                
        except Exception as e:
            messagebox.showerror("错误", f"无法启动卸载程序: {e}")
    
    def refresh_scan(self):
        """重新扫描（在后台线程中执行）"""
        def do_scan():
            try:
                progress_window = tk.Toplevel(self.root)
                progress_window.title("扫描中...")
                progress_window.geometry("300x100")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                label = ttk.Label(progress_window, text="正在重新扫描已安装的程序...")
                label.pack(pady=20)
                
                self.root.update()
                
                # 重新扫描已安装的程序
                from scanner_fixed import AppScanner
                from scoring import AppScorer
                
                scanner = AppScanner()
                apps = scanner.scan_installed_programs()
                
                scorer = AppScorer()
                enhanced_apps = []
                
                total_apps = len(apps)
                for i, app in enumerate(apps):
                    label.config(text=f"处理应用 {i+1}/{total_apps}: {app.get('name', 'Unknown')}")
                    self.root.update()
                    
                    last_access = scanner.get_last_access_time(app)
                    app['last_access_time'] = last_access
                    score_info = scorer.calculate_score(app)
                    app.update(score_info)
                    enhanced_apps.append(app)
                
                # 更新数据
                self.apps_data = enhanced_apps
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_after_scan(enhanced_apps, progress_window))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_scan_error(e, progress_window))
        
        # 在后台线程中执行扫描
        scan_thread = threading.Thread(target=do_scan, daemon=True)
        scan_thread.start()
    
    def update_after_scan(self, enhanced_apps, progress_window):
        """扫描完成后更新UI"""
        progress_window.destroy()
        
        # 清空并重新填充树形视图
        self.populate_tree()
        
        # 更新统计信息
        total_apps = len(enhanced_apps)
        large_apps = len([app for app in enhanced_apps if app.get('size_gb', 0) > 1.0])
        old_apps = len([app for app in enhanced_apps if app.get('days_since_last_use', 0) > 90])
        
        stats_text = f"总计: {total_apps} 个应用 | 大型应用 (>1GB): {large_apps} 个 | 长期未用 (>90天): {old_apps} 个"
        
        # 重新创建统计标签
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Label) and "总计:" in grandchild.cget("text"):
                                grandchild.config(text=stats_text)
                                break
        
        messagebox.showinfo("成功", f"重新扫描完成！找到 {len(enhanced_apps)} 个应用程序。")
    
    def handle_scan_error(self, error, progress_window):
        """处理扫描错误"""
        progress_window.destroy()
        messagebox.showerror("错误", f"重新扫描失败:\n{error}")
    
    def export_report(self):
        """导出报告"""
        if not self.apps_data:
            messagebox.showinfo("信息", "没有数据可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="保存报告"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("AppGraveyard 报告\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"总计应用数量: {len(self.apps_data)}\n\n")
                    
                    # 按分数排序
                    sorted_apps = sorted(self.apps_data, key=lambda x: x.get('score', 0), reverse=True)
                    
                    for app in sorted_apps:
                        f.write(f"应用名称: {app.get('name', 'N/A')}\n")
                        f.write(f"  大小: {self._format_size(app.get('size', 0))}\n")
                        f.write(f"  上次使用: {app.get('days_since_last_use', 'N/A')} 天前\n")
                        f.write(f"  状态: {app.get('status', 'N/A')}\n")
                        f.write(f"  分数: {app.get('score', 0):.2f}\n")
                        f.write("-" * 30 + "\n")
                
                messagebox.showinfo("成功", f"报告已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存报告失败:\n{e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
AppGraveyard 帮助

📊 状态说明:
• 🟢 安全卸载: 大型应用 (>1GB) 且长期未用 (>90天)
• 🟡 可考虑: 中等大小或中等使用频率的应用
• 🔴 可能仍需要: 小型应用 (<100MB) 或近期使用过 (<30天)

🖱️ 操作说明:
• 双击应用行查看详细信息
• 在详情窗口中点击"卸载此应用"启动卸载程序
• 点击"重新扫描"刷新应用列表
• 点击"导出报告"保存分析结果

💡 提示:
• 分数越高表示越适合卸载
• 卸载前请确认应用确实不再需要
• 某些系统应用可能无法正确识别
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        close_btn = ttk.Button(help_window, text="关闭", command=help_window.destroy)
        close_btn.pack(pady=(0, 10))
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

# 导入 datetime 用于报告功能
from datetime import datetime