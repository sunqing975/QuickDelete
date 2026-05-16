"""
QuickDelete v17 — tkinter 主线程进度窗
"""
import sys, os, time, json, uuid, tempfile, subprocess, ctypes, tkinter as tk

CREATE_NO_WINDOW = 0x08000000
MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6
QUEUE_DIR = os.path.join(tempfile.gettempdir(), 'QDQueue')
MIN_DELAY = 1.2

def confirm(text):
    return ctypes.windll.user32.MessageBoxW(0, text, "极速删除", MB_YESNO | MB_ICONWARNING) == IDYES

def delete_single(path):
    cmd = f'Remove-Item -LiteralPath "{path}" -Force -Recurse -ErrorAction Stop'
    p = subprocess.Popen(['powershell', '-NoProfile', '-Command', cmd],
                         shell=False, creationflags=CREATE_NO_WINDOW)
    p.wait(timeout=300)

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
    if not all_entries or entry['ts'] < max(e['ts'] for e in all_entries) - 0.15:
        sys.exit(1)

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

    # ---- 进度窗（主线程 tkinter） ----
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.configure(bg='white')
    root.geometry('300x60')
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'+{(sw-300)//2}+{(sh-60)//2}')
    tk.Label(root, text=f"⏳ 正在删除 {len(valid_paths)} 项…",
             font=("Microsoft YaHei", 13, "bold"), bg='white', fg='#333'
             ).pack(expand=True, fill='both')

    t0 = time.time()
    result = []

    def do_delete():
        for p in valid_paths:
            try: delete_single(p)
            except: pass
        result.append(True)

    threading.Thread(target=do_delete, daemon=True).start()

    def check_done():
        if result:
            elapse = time.time() - t0
            if elapse >= MIN_DELAY:
                root.destroy()
                return
            root.after(int((MIN_DELAY - elapse) * 1000), root.destroy)
        else:
            root.after(50, check_done)

    root.after(50, check_done)
    root.mainloop()

    sys.exit(0)

if __name__ == '__main__':
    main()
