# AppGraveyard 🪦

找出你埋葬但从未使用的应用程序，释放磁盘空间！

## 功能特点

- 🔍 **智能扫描**: 扫描 Windows 注册表中的已安装程序
- 📊 **智能评分**: 基于文件大小和使用频率计算"坟墓分数"
- 💾 **空间分析**: 显示每个应用占用的磁盘空间
- ⏰ **使用追踪**: 估算每个应用的最后使用时间
- 🎯 **状态分类**: 
  - 🟢 **安全卸载**: 大文件且很久没用
  - 🟡 **可考虑**: 中等大小或使用频率不确定
  - 🔴 **可能仍需要**: 小文件或最近使用过
- 🗑️ **一键卸载**: 双击即可启动卸载程序

## 安装

### 方法 1: 直接运行 (推荐)

1. 确保已安装 Python 3.7+
2. 安装依赖:
   ```bash
   pip install psutil
   ```
3. 运行程序:
   ```bash
   python appgraveyard.py
   ```

### 方法 2: 使用预编译的 EXE

从 [Releases](https://github.com/yourusername/appgraveyard/releases) 下载最新的 `.exe` 文件并直接运行。

## 构建 EXE

如果你想要自己构建 EXE 文件:

```bash
pip install pyinstaller psutil
pyinstaller --onefile --windowed --name AppGraveyard appgraveyard.py
```

## 工作原理

AppGraveyard 通过以下方式工作:

1. **注册表扫描**: 读取 `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` 和 `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`
2. **文件系统分析**: 检查安装目录的实际大小和文件访问时间
3. **智能评分**: 结合文件大小和使用频率计算卸载优先级
4. **用户友好界面**: 提供直观的 GUI 界面进行管理

## 故障排除

### 问题: 显示"找到 0 个程序"

**可能原因和解决方案:**

1. **权限不足**: 以管理员身份运行程序
2. **防病毒软件阻止**: 临时禁用防病毒软件或添加例外
3. **Windows 版本兼容性**: 确保使用 Windows 7 或更高版本
4. **注册表损坏**: 运行 `sfc /scannow` 修复系统文件

### 问题: 程序运行缓慢

- 第一次运行时会扫描所有安装目录，可能需要几分钟
- 后续运行会更快，因为会缓存部分信息

## 安全说明

- AppGraveyard **只读取**系统信息，不会修改任何文件
- 卸载操作会调用程序自带的卸载程序，与控制面板相同
- 建议在卸载前确认程序确实不再需要

## 许可证

MIT License - 详情见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！