"""
QuickDelete v12 — 极速删除 (无完成弹窗)
"""
import sys, os, time, json, uuid, tempfile, subprocess, ctypes

CREATE_NO_WINDOW = 0x08000000
MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6
QUEUE_DIR = os.path.join(tempfile.gettempdir(), 'QDQueue')

def msg(text, icon=0x10):
    ctypes.windll.user32.MessageBoxW(0, text, "极速删除", icon)

def confirm(text):
    return ctypes.windll.user32.MessageBoxW(0, text, "极速删除", MB_YESNO | MB_ICONWARNING) == IDYES

def show_progress(text):
    safe = text.replace('"', '\\"')
    ps = f'''
    Add-Type -AssemblyName PresentationFramework
    $w=New-Object Windows.Window
    $w.Title="极速删除";$w.Width=380;$w.Height=110
    $w.WindowStartupLocation="CenterScreen"
    $w.Topmost=$true;$w.WindowStyle="ToolWindow"
    $w.ResizeMode="NoResize"
    $s=New-Object Windows.Controls.StackPanel;$s.Margin="15"
    $t=New-Object Windows.Controls.TextBlock
    $t.Text="{safe}";$t.FontSize=15
    $t.HorizontalAlignment="Center";$t.VerticalAlignment="Center"
    $t.TextWrapping="WrapWithOverflow"
    $s.Children.Add($t);$w.Content=$s
    $w.Show()|Out-Null
    Start-Sleep -Seconds 9999
    '''
    return subprocess.Popen(
        ['powershell', '-NoProfile', '-Command', ps],
        shell=False, creationflags=CREATE_NO_WINDOW
    )

def delete_single(path):
    cmd = f'Remove-Item -LiteralPath "{path}" -Force -Recurse -ErrorAction Stop'
    p = subprocess.Popen(['powershell', '-NoProfile', '-Command', cmd],
                         shell=False, creationflags=CREATE_NO_WINDOW)
    p.wait(timeout=300)
    return not os.path.exists(path)

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(1)
    path = args[0].strip('"')
    if not os.path.exists(path):
        sys.exit(1)

    os.makedirs(QUEUE_DIR, exist_ok=True)
    my_id = uuid.uuid4().hex[:12]
    entry = {'id': my_id, 'path': path, 'ts': time.time()}
    with open(os.path.join(QUEUE_DIR, f'{my_id}.json'), 'w') as f:
        json.dump(entry, f)

    time.sleep(0.3 + (hash(path) & 0xFF) / 1000.0)

    all_entries = []
    if os.path.isdir(QUEUE_DIR):
        for fn in sorted(os.listdir(QUEUE_DIR)):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(QUEUE_DIR, fn)) as f:
                        d = json.load(f)
                        if os.path.exists(d['path']):
                            all_entries.append(d)
                except:
                    pass

    if not all_entries:
        sys.exit(1)

    my_ts = entry['ts']
    if my_ts < max(e['ts'] for e in all_entries) - 0.15:
        sys.exit(0)

    # leader: 清理队列
    if os.path.isdir(QUEUE_DIR):
        for f in os.listdir(QUEUE_DIR):
            try: os.remove(os.path.join(QUEUE_DIR, f))
            except: pass
        try: os.rmdir(QUEUE_DIR)
        except: pass

    valid_paths = [e['path'] for e in sorted(all_entries, key=lambda x: x['ts'])]
    names = [os.path.basename(p) or p for p in valid_paths]

    if len(names) == 1:
        tip = f"确定要永久删除「{names[0]}」吗？\n\n此操作不可恢复！"
    elif len(names) <= 8:
        tip = f"确定要永久删除以下 {len(names)} 项吗？\n\n" + "\n".join(f"  • {n}" for n in names) + "\n\n此操作不可恢复！"
    else:
        tip = f"确定要永久删除以下 {len(names)} 项吗？\n\n" + "\n".join(f"  • {n}" for n in names[:8]) + f"\n  ……等 {len(names)} 项\n\n此操作不可恢复！"

    if not confirm(tip):
        sys.exit(0)

    progress = show_progress(f"正在删除 {len(valid_paths)} 项…\n请稍候")
    for p in valid_paths:
        try: delete_single(p)
        except: pass

    try:
        progress.kill()
        progress.wait(timeout=3)
    except:
        pass

    # 不弹完成窗，直接退出
    sys.exit(0)

if __name__ == '__main__':
    main()
