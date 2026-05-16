# QuickDelete 🗑️⚡

Windows 右键菜单「极速删除」—— 跳过回收站，直接永久删除文件/文件夹。

## 特点

- ⚡ **极速** — 几十万小文件秒删，不走回收站
- 🪟 **无窗口闪烁** — 静默后台运行
- 🌏 **中文路径友好** — 完美支持中文、空格、特殊字符
- ✅ **确认弹窗** — 防误删，点「是」才删
- 🆓 **免费开源** — 一个 Python 脚本编译而成

## 安装方法

### 方法一：快速安装（推荐）

1. 下载 `QuickDelete.exe` 和 `极速删除.reg`
2. 把 `QuickDelete.exe` 放到 `C:\Program Files\QuickDelete\` 目录下
3. 双击 `极速删除.reg` 导入注册表
4. 右键任意文件或文件夹 → 即可看到「极速删除」

### 方法二：自己编译

需要 Python 3.10+ 和 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name QuickDelete source/quick_delete.py
```

## 使用方法

1. 选中文件或文件夹
2. 鼠标右键 → **极速删除**
3. 弹窗确认 → 点「是」直接永久删除

> ⚠️ **注意：删除后不可恢复！不会进入回收站！**

## 卸载方法

1. 删除 `C:\Program Files\QuickDelete\` 目录
2. 双击 `卸载.reg` 清除右键菜单
3. 或者手动运行：
   ```cmd
   reg delete HKCR\*\shell\QuickDelete /f
   reg delete HKCR\Directory\shell\QuickDelete /f
   reg delete HKCR\Directory\Background\shell\QuickDelete /f
   ```

## 原理

右键菜单通过注册表注册，选中路径作为参数传给 `QuickDelete.exe`。
程序调用 PowerShell `Remove-Item -Force -Recurse` 跳过回收站直接删除。

对比普通删除：

| 步骤 | 普通 Delete | 极速删除 |
|:----:|:-----------:|:--------:|
| 复制到回收站 | ✅ 每个文件复制一次 | ❌ 不复制 |
| 杀毒扫描 | ✅ 扫描每个文件 | ❌ 跳过 |
| 文件管理器 UI | ✅ 渲染进度条 | ❌ 无 |
| 实际耗时 | 几分钟~几十分钟 | 秒级 |

## 截图

*(欢迎提交 screenshot PR!)*

## 许可

MIT License
