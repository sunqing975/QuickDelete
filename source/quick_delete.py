"""
QuickDelete v6 — 极速删除 (带确认)
跳过回收站，直接永久删除文件/文件夹。
右键菜单调用，Windows 原生支持，无窗口闪烁。
"""
import sys
import os
import subprocess
import ctypes

CREATE_NO_WINDOW = 0x08000000
MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6


def msgbox(text, title="极速删除", icon=0x10):
    ctypes.windll.user32.MessageBoxW(0, text, title, icon)


def confirm(text, title="极速删除"):
    ret = ctypes.windll.user32.MessageBoxW(0, text, title, MB_YESNO | MB_ICONWARNING)
    return ret == IDYES


def quick_delete(path):
    if not os.path.exists(path):
        msgbox(f"路径不存在:\n{path}", "极速删除", 0x10)
        return 1

    is_dir = os.path.isdir(path)
    name = os.path.basename(path) or path

    if is_dir:
        tip = f"确定要永久删除文件夹「{name}」吗？\n\n此操作不可恢复！"
    else:
        tip = f"确定要永久删除文件「{name}」吗？\n\n此操作不可恢复！"

    if not confirm(tip):
        return 0

    try:
        ps_cmd = f'Remove-Item -LiteralPath "{path}" -Force -Recurse -ErrorAction Stop'
        proc = subprocess.Popen(
            ['powershell', '-NoProfile', '-Command', ps_cmd],
            shell=False,
            creationflags=CREATE_NO_WINDOW
        )
        proc.wait(timeout=60)

        if not os.path.exists(path):
            return 0
        else:
            msgbox(f"删除失败，可能权限不足或文件被占用:\n{path}", "极速删除", 0x10)
            return 1

    except subprocess.TimeoutExpired:
        msgbox(f"删除超时(>60s):\n{path}", "极速删除", 0x10)
        return 1
    except Exception as e:
        msgbox(f"错误:\n{str(e)}", "极速删除", 0x10)
        return 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    path = sys.argv[1].strip('"').strip("'")
    sys.exit(quick_delete(path))
