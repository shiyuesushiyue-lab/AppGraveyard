import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import subprocess
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
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建说明标签
        desc_label = ttk.Label(
            main_frame, 
            text="这些是你很久没用但占用大量空间的应用程序",
            font=("Arial", 12)
        )
        desc_label.pack(pady=(0, 10))
        
        # 创建树形视图
        columns = ("name", "size", "days", "status", "action")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        self.tree.heading("name", text="程序名")
        self.tree.heading("size", text="大小")
        self.tree.heading("days", text="上次使用")
        self.tree.heading("status", text="状态")
        self.tree.heading("action", text="操作")
        
        # 设置列宽
        self.tree.column("name", width=250, minwidth=150)
        self.tree.column("size", width=100, minwidth=80, anchor="center")
        self.tree.column("days", width=100, minwidth=80, anchor="center")
        self.tree.column("status", width=120, minwidth=100, anchor="center")
        self.tree.column("action", width=100, minwidth=80, anchor="center")
        
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
        
        # 创建底部按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        refresh_btn = ttk.Button(button_frame, text="重新扫描", command=self.refresh_scan)
        refresh_btn.pack(side=tk.LEFT)
        
        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT)
    
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
            
            if days != 'N/A':
                days_str = f"{days}天前"
            else:
                days_str = "未知"
            
            self.tree.insert("", "end", values=(name, size_str, days_str, status, "卸载"))
    
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
        
        if target_app and target_app.get('uninstall_string'):
            self.open_uninstall(target_app)
        else:
            messagebox.showinfo("信息", f"无法找到 {app_name} 的卸载程序")
    
    def open_uninstall(self, app: Dict):
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
        except Exception as e:
            messagebox.showerror("错误", f"无法启动卸载程序: {e}")
    
    def refresh_scan(self):
        """重新扫描（这里需要重新实现完整的扫描逻辑）"""
        messagebox.showinfo("提示", "重新扫描功能将在完整版本中实现")
    
    def run(self):
        """运行UI"""
        self.root.mainloop()