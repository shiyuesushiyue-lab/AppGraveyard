# AppGraveyard 🪦

Find the apps you buried but never use.

## 功能

- 扫描 Windows 已安装程序
- 估算上次使用时间  
- 按"垃圾程度"排序
- 一键跳转卸载

## 使用

```bash
AppGraveyard.exe
```

## 项目定位

AppGraveyard 是一个 Windows 小工具，
它会扫描你电脑里安装的软件，
并告诉你：哪些你很久没用、但却占着大量空间。

用户只需点一下，就能看到：
- 体积最大的程序
- 多久没打开过  
- 是否安全卸载
- 并可一键跳转到系统卸载

## 用户真实痛点

- C 盘爆了，但不知道该删谁
- 控制面板列表太长，看不懂
- 不敢乱删，怕系统坏

AppGraveyard = 可解释的"卸载建议"

## 核心功能（MVP）

### 扫描已安装程序
从 Windows 注册表获取：
- 程序名
- 安装路径  
- 安装大小（估算）
- 安装日期（若有）

### 最近使用时间估计
优先级：
1. 可执行文件 LastAccessTime
2. 文件夹最近访问
3. 注册表字段 InstallDate 作为 fallback

### 评分规则（是否"坟墓"）
```
score = w1 * size_gb + w2 * days_since_last_use
```
默认：
- w1 = 2
- w2 = 0.01

标记为：
- 🟢 安全卸载
- 🟡 可考虑  
- 🔴 可能仍需要

### 界面（极简）
| 列 | 内容 |
|---|---|
| 程序名 | name |
| 大小 | size (MB/GB) |
| 上次使用 | days |
| 状态 | 安全/警告 |
| 操作 | 打开卸载页 |

## 技术实现

### 语言
Python 3.10+

### 依赖
```
psutil
pywin32
tkinter (内置)
```

### 打包
```bash
pip install pyinstaller
pyinstaller --onefile appgraveyard.py
```

生成：
```
dist/AppGraveyard.exe
```

## 目录结构
```
appgraveyard/
  appgraveyard.py
  scanner.py
  scoring.py
  ui.py
  requirements.txt
  README.md
```

## 开源协议
MIT License

## 后续扩展（不在 MVP）
- 自动生成"释放空间统计"
- 扫描模型缓存 / pip / conda
- 语言切换
- 黑名单（永不标记）