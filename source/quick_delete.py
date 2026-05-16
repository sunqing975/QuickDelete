"""
QuickDelete v7 — 极速删除 (支持多选)
接收多个文件/文件夹路径，一次确认，批量删除
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


def delete_single(path):
    """删除单个文件或文件夹，返回 True=成功"""
    if os.path.isdir(path):
        cmd = f'Remove-Item -LiteralPath "{path}" -Force -Recurse -ErrorAction Stop'
    else:
        cmd = f'Remove-Item -LiteralPath "{path}" -Force -ErrorAction Stop'

    proc = subprocess.Popen(
        ['powershell', '-NoProfile', '-Command', cmd],
        shell=False,
        creationflags=CREATE_NO_WINDOW
    )
    proc.wait(timeout=60)
    return not os.path.exists(path)


def main():
    paths = sys.argv[1:]
    if not paths:
        sys.exit(1)

    # 过滤掉不存在的路径
    valid_paths = [p for p in paths if os.path.exists(p)]
    if not valid_paths:
        msgbox("选中的文件/文件夹不存在", "极速删除", 0x10)
        sys.exit(1)

    # 构建确认信息
    names = [os.path.basename(p) or p for p in valid_paths]
    if len(names) == 1:
        tip = f"确定要永久删除「{names[0]}」吗？\n\n此操作不可恢复！"
    elif len(names) <= 5:
        lines = "\n".join(f"  • {n}" for n in names)
        tip = f"确定要永久删除以下 {len(names)} 项吗？\n\n{lines}\n\n此操作不可恢复！"
    else:
        lines = "\n".join(f"  • {n}" for n in names[:5])
        tip = f"确定要永久删除以下 {len(names)} 项吗？\n\n{lines}\n  • ……等 {len(names)} 项\n\n此操作不可恢复！"

    if not confirm(tip):
        sys.exit(0)

    # 批量删除
    failed = []
    for path in valid_paths:
        try:
            if not delete_single(path):
                failed.append(path)
        except subprocess.TimeoutExpired:
            failed.append(f"{path} (超时)")
        except Exception as e:
            failed.append(f"{path} ({str(e)})")

    if failed:
        msgbox(f"以下项目删除失败:\n" + "\n".join(failed), "极速删除", 0x10)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
