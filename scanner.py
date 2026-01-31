import winreg
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import psutil

class AppScanner:
    """扫描Windows已安装程序的类"""
    
    def __init__(self):
        self.installed_apps = []
    
    def scan_installed_programs(self) -> List[Dict]:
        """扫描注册表中的已安装程序"""
        apps = []
        
        # 扫描机器级别的安装 (HKLM)
        try:
            hklm_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            apps.extend(self._scan_registry_key(hklm_key))
            winreg.CloseKey(hklm_key)
        except Exception as e:
            print(f"Error scanning HKLM: {e}")
        
        # 扫描用户级别的安装 (HKCU)
        try:
            hkcu_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            apps.extend(self._scan_registry_key(hkcu_key))
            winreg.CloseKey(hkcu_key)
        except Exception as e:
            print(f"Error scanning HKCU: {e}")
        
        # 过滤无效条目
        valid_apps = [app for app in apps if self._is_valid_app(app)]
        return valid_apps
    
    def _scan_registry_key(self, registry_key) -> List[Dict]:
        """扫描单个注册表键"""
        apps = []
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(registry_key, i)
                subkey_path = f"{registry_key.name}\\{subkey_name}"
                
                with winreg.OpenKey(registry_key, subkey_name) as subkey:
                    app_info = self._get_app_info_from_registry(subkey, subkey_path)
                    if app_info:
                        apps.append(app_info)
                i += 1
            except OSError:
                # 没有更多的子键了
                break
        return apps
    
    def _get_app_info_from_registry(self, subkey, subkey_path: str) -> Optional[Dict]:
        """从注册表子键获取应用信息"""
        try:
            app_info = {
                'name': '',
                'install_location': '',
                'size': 0,
                'install_date': None,
                'uninstall_string': '',
                'display_icon': '',
                'registry_path': subkey_path
            }
            
            # 获取基本信息
            try:
                app_info['name'] = winreg.QueryValueEx(subkey, "DisplayName")[0]
            except FileNotFoundError:
                return None
            
            # 获取安装位置
            try:
                app_info['install_location'] = winreg.QueryValueEx(subkey, "InstallLocation")[0]
            except FileNotFoundError:
                app_info['install_location'] = ''
            
            # 获取卸载字符串
            try:
                app_info['uninstall_string'] = winreg.QueryValueEx(subkey, "UninstallString")[0]
            except FileNotFoundError:
                app_info['uninstall_string'] = ''
            
            # 获取显示图标
            try:
                app_info['display_icon'] = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
            except FileNotFoundError:
                app_info['display_icon'] = ''
            
            # 获取安装日期
            try:
                install_date_str = winreg.QueryValueEx(subkey, "InstallDate")[0]
                if install_date_str and len(install_date_str) == 8:
                    # YYYYMMDD 格式
                    app_info['install_date'] = datetime.strptime(install_date_str, "%Y%m%d")
            except (FileNotFoundError, ValueError):
                app_info['install_date'] = None
            
            # 估算大小（如果注册表中有）
            try:
                estimated_size = winreg.QueryValueEx(subkey, "EstimatedSize")[0]
                # 注册表中的大小通常是以KB为单位
                app_info['size'] = estimated_size * 1024  # 转换为字节
            except FileNotFoundError:
                app_info['size'] = self._estimate_size_from_install_location(app_info['install_location'])
            
            return app_info
            
        except Exception as e:
            print(f"Error reading registry entry {subkey_path}: {e}")
            return None
    
    def _estimate_size_from_install_location(self, install_location: str) -> int:
        """根据安装位置估算程序大小"""
        if not install_location or not os.path.exists(install_location):
            return 0
        
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(install_location):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        except Exception as e:
            print(f"Error estimating size for {install_location}: {e}")
            return 0
    
    def _is_valid_app(self, app: Dict) -> bool:
        """检查应用是否有效（排除系统组件等）"""
        if not app.get('name'):
            return False
        
        # 排除一些常见的系统组件
        invalid_names = [
            'Microsoft Visual C++', 
            'Windows Driver Package',
            'Hotfix',
            'Update for',
            'Security Update',
            'Service Pack'
        ]
        
        app_name = app['name'].lower()
        for invalid in invalid_names:
            if invalid.lower() in app_name:
                return False
        
        # 必须有卸载字符串或者有效的安装位置
        if not app.get('uninstall_string') and not app.get('install_location'):
            return False
        
        return True
    
    def get_last_access_time(self, app: Dict) -> Optional[datetime]:
        """获取应用的最后访问时间"""
        # 优先级1: 检查可执行文件的最后访问时间
        executable_paths = self._find_executables(app)
        if executable_paths:
            latest_access = None
            for exe_path in executable_paths[:5]:  # 限制检查数量
                try:
                    access_time = os.path.getatime(exe_path)
                    access_dt = datetime.fromtimestamp(access_time)
                    if latest_access is None or access_dt > latest_access:
                        latest_access = access_dt
                except (OSError, FileNotFoundError):
                    continue
            if latest_access:
                return latest_access
        
        # 优先级2: 检查安装目录的最后修改时间
        install_location = app.get('install_location')
        if install_location and os.path.exists(install_location):
            try:
                mod_time = os.path.getmtime(install_location)
                return datetime.fromtimestamp(mod_time)
            except (OSError, FileNotFoundError):
                pass
        
        # 优先级3: 使用安装日期作为后备
        if app.get('install_date'):
            return app.get('install_date')
        
        return None
    
    def _find_executables(self, app: Dict) -> List[str]:
        """查找应用的可执行文件"""
        executables = []
        
        # 从显示图标路径获取
        if app.get('display_icon'):
            icon_path = app['display_icon']
            if os.path.exists(icon_path) and icon_path.lower().endswith('.exe'):
                executables.append(icon_path)
        
        # 从安装位置查找
        install_location = app.get('install_location')
        if install_location and os.path.exists(install_location):
            try:
                for root, dirs, files in os.walk(install_location):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            executables.append(os.path.join(root, file))
                            if len(executables) >= 10:  # 限制数量
                                break
                    if len(executables) >= 10:
                        break
            except Exception as e:
                print(f"Error finding executables in {install_location}: {e}")
        
        return executables