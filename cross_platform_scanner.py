import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Platform-specific imports
if sys.platform == "win32":
    import winreg
    import psutil
elif sys.platform == "darwin":  # macOS
    import plistlib
    import subprocess
else:  # Linux and others
    import subprocess

class AppScanner:
    """跨平台扫描已安装程序的类"""
    
    def __init__(self):
        self.installed_apps = []
    
    def scan_installed_programs(self) -> List[Dict]:
        """根据平台扫描已安装的程序"""
        if sys.platform == "win32":
            return self._scan_windows_programs()
        elif sys.platform == "darwin":
            return self._scan_macos_applications()
        else:
            return self._scan_linux_packages()
    
    def _scan_windows_programs(self) -> List[Dict]:
        """扫描Windows已安装程序"""
        apps = []
        
        # 扫描机器级别的安装 (HKLM) - 64位
        try:
            hklm_key_64 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                                    0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            apps.extend(self._scan_registry_key(hklm_key_64))
            winreg.CloseKey(hklm_key_64)
            print(f"从 HKLM 64位 找到 {len(apps)} 个程序")
        except Exception as e:
            print(f"Error scanning HKLM 64位: {e}")
        
        # 扫描机器级别的安装 (HKLM) - 32位
        try:
            hklm_key_32 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                                    0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
            apps_32 = self._scan_registry_key(hklm_key_32)
            apps.extend(apps_32)
            winreg.CloseKey(hklm_key_32)
            print(f"从 HKLM 32位 找到 {len(apps_32)} 个程序")
        except Exception as e:
            print(f"Error scanning HKLM 32位: {e}")
        
        # 扫描用户级别的安装 (HKCU)
        try:
            hkcu_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            apps_hkcu = self._scan_registry_key(hkcu_key)
            apps.extend(apps_hkcu)
            winreg.CloseKey(hkcu_key)
            print(f"从 HKCU 找到 {len(apps_hkcu)} 个程序")
        except Exception as e:
            print(f"Error scanning HKCU: {e}")
        
        # 去重（基于名称）
        unique_apps = {}
        for app in apps:
            if app.get('name') and app['name'] not in unique_apps:
                unique_apps[app['name']] = app
        
        apps_list = list(unique_apps.values())
        print(f"去重后总共有 {len(apps_list)} 个程序")
        
        # 过滤无效条目（但保留更多有效程序）
        valid_apps = [app for app in apps_list if self._is_valid_app(app)]
        print(f"过滤后剩下 {len(valid_apps)} 个有效程序")
        
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
            except Exception as e:
                print(f"Error enumerating key at index {i}: {e}")
                i += 1
                continue
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
                'publisher': '',
                'version': '',
                'registry_path': subkey_path,
                'platform': 'windows'
            }
            
            # 获取基本信息
            try:
                app_info['name'] = str(winreg.QueryValueEx(subkey, "DisplayName")[0])
            except FileNotFoundError:
                return None
            
            # 获取发布者
            try:
                app_info['publisher'] = str(winreg.QueryValueEx(subkey, "Publisher")[0])
            except FileNotFoundError:
                app_info['publisher'] = ''
            
            # 获取版本
            try:
                app_info['version'] = str(winreg.QueryValueEx(subkey, "DisplayVersion")[0])
            except FileNotFoundError:
                app_info['version'] = ''
            
            # 获取安装位置
            try:
                install_location = str(winreg.QueryValueEx(subkey, "InstallLocation")[0])
                if install_location and os.path.exists(install_location):
                    app_info['install_location'] = install_location
                else:
                    # 尝试从卸载字符串推断安装位置
                    try:
                        uninstall_str = str(winreg.QueryValueEx(subkey, "UninstallString")[0])
                        if uninstall_str and '"' in uninstall_str:
                            # 提取引号内的路径
                            start = uninstall_str.find('"')
                            end = uninstall_str.find('"', start + 1)
                            if start != -1 and end != -1:
                                exe_path = uninstall_str[start+1:end]
                                app_info['install_location'] = os.path.dirname(exe_path)
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                app_info['install_location'] = ''
            
            # 获取卸载字符串
            try:
                app_info['uninstall_string'] = str(winreg.QueryValueEx(subkey, "UninstallString")[0])
            except FileNotFoundError:
                # 尝试 QuietUninstallString
                try:
                    app_info['uninstall_string'] = str(winreg.QueryValueEx(subkey, "QuietUninstallString")[0])
                except FileNotFoundError:
                    app_info['uninstall_string'] = ''
            
            # 获取显示图标
            try:
                app_info['display_icon'] = str(winreg.QueryValueEx(subkey, "DisplayIcon")[0])
            except FileNotFoundError:
                app_info['display_icon'] = ''
            
            # 获取安装日期
            try:
                install_date_str = str(winreg.QueryValueEx(subkey, "InstallDate")[0])
                if install_date_str and len(install_date_str) == 8:
                    # YYYYMMDD 格式
                    app_info['install_date'] = datetime.strptime(install_date_str, "%Y%m%d")
            except (FileNotFoundError, ValueError):
                app_info['install_date'] = None
            
            # 获取大小
            try:
                estimated_size = int(winreg.QueryValueEx(subkey, "EstimatedSize")[0])
                # 注册表中的大小通常是以KB为单位
                app_info['size'] = estimated_size * 1024  # 转换为字节
            except (FileNotFoundError, ValueError):
                app_info['size'] = self._estimate_size_from_install_location(app_info['install_location'])
            
            return app_info
            
        except Exception as e:
            print(f"Error reading registry entry {subkey_path}: {e}")
            return None
    
    def _scan_macos_applications(self) -> List[Dict]:
        """扫描macOS应用程序"""
        apps = []
        applications_dirs = [
            "/Applications",
            os.path.expanduser("~/Applications")
        ]
        
        for app_dir in applications_dirs:
            if os.path.exists(app_dir):
                for item in os.listdir(app_dir):
                    if item.endswith(".app"):
                        app_path = os.path.join(app_dir, item)
                        app_info = self._get_macos_app_info(app_path)
                        if app_info:
                            apps.append(app_info)
        
        return apps
    
    def _get_macos_app_info(self, app_path: str) -> Optional[Dict]:
        """获取macOS应用信息"""
        try:
            app_name = os.path.basename(app_path).replace(".app", "")
            
            # 获取Info.plist信息
            plist_path = os.path.join(app_path, "Contents", "Info.plist")
            version = ""
            bundle_id = ""
            
            if os.path.exists(plist_path):
                try:
                    with open(plist_path, 'rb') as f:
                        plist_data = plistlib.load(f)
                        version = plist_data.get('CFBundleShortVersionString', '')
                        bundle_id = plist_data.get('CFBundleIdentifier', '')
                except Exception:
                    pass
            
            # 计算大小
            size = self._estimate_size_from_install_location(app_path)
            
            return {
                'name': app_name,
                'install_location': app_path,
                'size': size,
                'install_date': None,
                'uninstall_string': f"rm -rf '{app_path}'",
                'display_icon': '',
                'publisher': '',
                'version': version,
                'bundle_id': bundle_id,
                'platform': 'macos'
            }
        except Exception as e:
            print(f"Error reading macOS app {app_path}: {e}")
            return None
    
    def _scan_linux_packages(self) -> List[Dict]:
        """扫描Linux包管理器安装的程序"""
        apps = []
        
        # Try different package managers
        package_managers = [
            ("dpkg -l", self._parse_dpkg_output),
            ("rpm -qa --queryformat '%{NAME} %{VERSION} %{SIZE}\\n'", self._parse_rpm_output),
        ]
        
        for cmd, parser in package_managers:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    parsed_apps = parser(result.stdout)
                    apps.extend(parsed_apps)
                    break
            except Exception as e:
                print(f"Error running {cmd}: {e}")
                continue
        
        return apps
    
    def _parse_dpkg_output(self, output: str) -> List[Dict]:
        """解析dpkg输出"""
        apps = []
        lines = output.split('\n')
        for line in lines[5:]:  # Skip header
            if line.strip() and line.startswith('ii'):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    version = parts[2]
                    apps.append({
                        'name': name,
                        'install_location': '',
                        'size': 0,  # dpkg doesn't provide size easily
                        'install_date': None,
                        'uninstall_string': f"sudo apt remove {name}",
                        'display_icon': '',
                        'publisher': '',
                        'version': version,
                        'platform': 'linux'
                    })
        return apps
    
    def _parse_rpm_output(self, output: str) -> List[Dict]:
        """解析rpm输出"""
        apps = []
        lines = output.split('\n')
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    version = parts[1]
                    try:
                        size = int(parts[2])
                    except ValueError:
                        size = 0
                    apps.append({
                        'name': name,
                        'install_location': '',
                        'size': size,
                        'install_date': None,
                        'uninstall_string': f"sudo rpm -e {name}",
                        'display_icon': '',
                        'publisher': '',
                        'version': version,
                        'platform': 'linux'
                    })
        return apps
    
    def _estimate_size_from_install_location(self, install_location: str) -> int:
        """根据安装位置估算程序大小"""
        if not install_location or not os.path.exists(install_location):
            return 0
        
        try:
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(install_location):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                        # 限制文件数量以提高性能
                        if file_count > 1000:
                            break
                    except (OSError, FileNotFoundError):
                        continue
                if file_count > 1000:
                    break
            return total_size
        except Exception as e:
            print(f"Error estimating size for {install_location}: {e}")
            return 0
    
    def _is_valid_app(self, app: Dict) -> bool:
        """检查应用是否有效（排除系统组件等）"""
        if not app.get('name') or not app['name'].strip():
            return False
        
        app_name = app['name'].strip()
        
        # 排除一些常见的系统组件（但更宽松）
        system_components = [
            'Microsoft Visual C++',
            'Windows Driver Package',
            'Hotfix',
            'Update for Microsoft',
            'Security Update for Microsoft',
            'Service Pack',
            'Definition Update',
            'Language Pack',
            'Windows Setup',
            'Microsoft .NET Framework',
            'Microsoft ASP.NET',
            'Microsoft SQL Server',
            'Microsoft Silverlight',
            'Microsoft OneDrive',
            'Microsoft Edge',
            'Windows App Runtime'
        ]
        
        app_name_lower = app_name.lower()
        for component in system_components:
            if component.lower() in app_name_lower:
                return False
        
        # 必须有卸载字符串或者有效的安装位置
        has_uninstall = bool(app.get('uninstall_string') and app['uninstall_string'].strip())
        has_install_loc = bool(app.get('install_location') and app['install_location'].strip() and os.path.exists(app.get('install_location', '')))
        
        if not has_uninstall and not has_install_loc:
            return False
        
        # 排除非常小的程序（小于1KB）
        if app.get('size', 0) < 1024:
            return False
        
        return True
    
    def get_last_access_time(self, app: Dict) -> Optional[datetime]:
        """获取应用的最后访问时间"""
        # 优先级1: 检查可执行文件的最后访问时间
        executable_paths = self._find_executables(app)
        if executable_paths:
            latest_access = None
            for exe_path in executable_paths[:3]:  # 限制检查数量以提高性能
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
        
        # 优先级4: 如果都没有，返回很久以前的时间（表示很久没用）
        return datetime.now() - timedelta(days=365)
    
    def _find_executables(self, app: Dict) -> List[str]:
        """查找应用的可执行文件"""
        executables = []
        
        platform = app.get('platform', 'windows')
        
        if platform == 'windows':
            # Windows specific logic
            if app.get('display_icon'):
                icon_path = app['display_icon']
                if os.path.exists(icon_path) and icon_path.lower().endswith('.exe'):
                    executables.append(icon_path)
            
            if app.get('uninstall_string'):
                uninstall_str = app['uninstall_string']
                if '"' in uninstall_str:
                    start = uninstall_str.find('"')
                    end = uninstall_str.find('"', start + 1)
                    if start != -1 and end != -1:
                        exe_path = uninstall_str[start+1:end]
                        if os.path.exists(exe_path):
                            executables.append(exe_path)
            
            install_location = app.get('install_location')
            if install_location and os.path.exists(install_location):
                try:
                    main_exe_candidates = [
                        f"{app.get('name', '').replace(' ', '')}.exe",
                        "main.exe", "app.exe", "program.exe"
                    ]
                    
                    for candidate in main_exe_candidates:
                        exe_path = os.path.join(install_location, candidate)
                        if os.path.exists(exe_path):
                            executables.append(exe_path)
                            break
                    
                    if not executables:
                        for root, dirs, files in os.walk(install_location):
                            for file in files:
                                if file.lower().endswith('.exe'):
                                    executables.append(os.path.join(root, file))
                                    break
                            if executables:
                                break
                except Exception as e:
                    print(f"Error finding executables in {install_location}: {e}")
        
        elif platform == 'macos':
            # macOS: look for the main executable in Contents/MacOS
            install_location = app.get('install_location')
            if install_location and os.path.exists(install_location):
                macos_dir = os.path.join(install_location, "Contents", "MacOS")
                if os.path.exists(macos_dir):
                    for file in os.listdir(macos_dir):
                        exe_path = os.path.join(macos_dir, file)
                        if os.path.isfile(exe_path):
                            executables.append(exe_path)
                            break
        
        elif platform == 'linux':
            # Linux: this is more complex, but we can check common locations
            # For now, just return empty list as Linux apps are handled differently
            pass
        
        return executables