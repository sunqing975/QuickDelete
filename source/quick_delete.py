"""
QuickDelete v18 — tkinter 进度窗 + 先弹窗后协调
"""
import sys, os, time, json, uuid, tempfile, subprocess, ctypes, threading, tkinter as tk

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

    name = os.path.basename(path) or path

    # ---- 先弹确认（立即响应） ----
    if not confirm(f"确定要永久删除「{name}」吗？\n\n此操作不可恢复！"):
        sys.exit(0)

    # ---- 再协调多实例 ----
    os.makedirs(QUEUE_DIR, exist_ok=True)
    my_id = uuid.uuid4().hex[:12]
    entry = {'id': my_id, 'path': path, 'ts': time.time()}
    with open(os.path.join(QUEUE_DIR, f'{my_id}.json'), 'w') as f:
        json.dump(entry, f)

    time.sleep(0.08 + (hash(path) & 0x3F) / 1000.0)

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

    # 不是 leader 就退出（leader 会处理队列中所有路径）
    if not all_entries or entry['ts'] < max(e['ts'] for e in all_entries) - 0.15:
        sys.exit(0)

    # ---- leader: 收集所有路径 ----
    if os.path.isdir(QUEUE_DIR):
        for f in os.listdir(QUEUE_DIR):
            try: os.remove(os.path.join(QUEUE_DIR, f))
            except: pass
        try: os.rmdir(QUEUE_DIR)
        except: pass

    valid_paths = [e['path'] for e in sorted(all_entries, key=lambda x: x['ts'])]

    if not valid_paths:
        sys.exit(0)

    # ---- 进度窗 ----
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.configure(bg='#ccc')
    root.geometry('302x62')
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'+{(sw-302)//2}+{(sh-62)//2}')
    inner = tk.Frame(root, bg='white', bd=0)
    inner.pack(padx=1, pady=1, fill='both', expand=True)
    tk.Label(inner, text=f"⏳ 正在删除 {len(valid_paths)} 项…",
             font=("Microsoft YaHei", 13, "bold"), bg='white', fg='#333'
             ).pack(expand=True, fill='both')

    t0 = time.time()
    done = [False]

    def do_delete():
        for p in valid_paths:
            try: delete_single(p)
            except: pass
        done[0] = True

    threading.Thread(target=do_delete, daemon=True).start()

    def poll():
        while not done[0]:
            root.update()
            time.sleep(0.03)
        elapse = time.time() - t0
        if elapse < MIN_DELAY:
            time.sleep(MIN_DELAY - elapse)
        root.destroy()

    threading.Thread(target=poll, daemon=True).start()

    # 等 tkinter 窗口显示 + 删除完成
    root.mainloop()
    sys.exit(0)

if __name__ == '__main__':
    main()
