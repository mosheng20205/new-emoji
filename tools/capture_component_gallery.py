import argparse
import ctypes
import importlib.util
import os
import pathlib
import subprocess
import sys
import time
import types
from ctypes import wintypes


ROOT = pathlib.Path(__file__).resolve().parents[1]
GALLERY = ROOT / "examples" / "python" / "component_gallery.py"
IMGS = ROOT / "imgs"


def _install_fake_ui():
    ui = types.ModuleType("new_emoji_ui")
    ui.MessageBoxCallback = lambda fn: fn
    ui.MenuSelectCallback = lambda fn: fn
    ui.ClickCallback = lambda fn: fn
    ui.dll = types.SimpleNamespace()

    def __getattr__(_name):
        def fn(*_args, **_kwargs):
            return 1
        return fn

    ui.__getattr__ = __getattr__
    sys.modules["new_emoji_ui"] = ui


def collect_components():
    _install_fake_ui()
    spec = importlib.util.spec_from_file_location("component_gallery_collect", GALLERY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    records = []

    def fake_make_page(_hwnd, _root, category_name, _intro, components, **_kwargs):
        mod.category_components[category_name] = [
            (name, emoji, summary) for name, emoji, summary, *_rest in components
        ]
        for name, _emoji, _summary, *_rest in components:
            records.append((category_name, name))

    def fake_add_component_detail(_hwnd, _root, category_name, name, emoji, summary, *_args, **_kwargs):
        mod.category_components.setdefault(category_name, []).append((name, emoji, summary))
        records.append((category_name, name))

    mod.make_page = fake_make_page
    mod.add_component_detail = fake_add_component_detail
    mod.build_pages(None, None)
    return records


def find_window_for_pid(pid):
    user32 = ctypes.windll.user32
    enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    found = []

    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        window_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid:
            found.append(hwnd)
        return True

    user32.EnumWindows(enum_proc(callback), 0)
    return found[0] if found else None


def print_window(hwnd, out_path):
    ps_out = str(out_path).replace("'", "''")
    ps = f"""
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class NativeShot {{
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT {{ public int Left; public int Top; public int Right; public int Bottom; }}
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr dpiContext);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern IntPtr GetWindowDC(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleDC(IntPtr hdc);
  [DllImport("gdi32.dll")] public static extern IntPtr CreateCompatibleBitmap(IntPtr hdc, int nWidth, int nHeight);
  [DllImport("gdi32.dll")] public static extern IntPtr SelectObject(IntPtr hdc, IntPtr hgdiobj);
  [DllImport("gdi32.dll")] public static extern bool DeleteObject(IntPtr hObject);
  [DllImport("gdi32.dll")] public static extern bool DeleteDC(IntPtr hdc);
}}
"@
$hwnd = [IntPtr]::new({int(hwnd)})
$out = '{ps_out}'
[void][NativeShot]::SetProcessDpiAwarenessContext([IntPtr]::new(-4))
$r = New-Object NativeShot+RECT
[void][NativeShot]::GetWindowRect($hwnd, [ref]$r)
$w = [Math]::Max(1, $r.Right - $r.Left)
$h = [Math]::Max(1, $r.Bottom - $r.Top)
$dpi = [NativeShot]::GetDpiForWindow($hwnd)
if ($dpi -gt 96 -and $w -le 2600) {{
  $scale = [double]$dpi / 96.0
  $w = [int][Math]::Ceiling($w * $scale)
  $h = [int][Math]::Ceiling($h * $scale)
}}
$src = [NativeShot]::GetWindowDC($hwnd)
$mem = [NativeShot]::CreateCompatibleDC($src)
$hbmp = [NativeShot]::CreateCompatibleBitmap($src, $w, $h)
$old = [NativeShot]::SelectObject($mem, $hbmp)
$ok = [NativeShot]::PrintWindow($hwnd, $mem, 2)
$img = [System.Drawing.Image]::FromHbitmap($hbmp)
$img.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$img.Dispose()
[void][NativeShot]::SelectObject($mem, $old)
[void][NativeShot]::DeleteObject($hbmp)
[void][NativeShot]::DeleteDC($mem)
[void][NativeShot]::ReleaseDC($hwnd, $src)
if (-not $ok) {{ exit 2 }}
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True,
        cwd=str(ROOT),
        timeout=60,
    )


def run_capture_child(category, component):
    sys.path.insert(0, str(ROOT / "examples" / "python"))
    os.environ["NEW_EMOJI_GALLERY_SECONDS"] = "120"
    os.environ["NEW_EMOJI_GALLERY_PAGE"] = category
    os.environ["NEW_EMOJI_GALLERY_COMPONENT"] = component
    import component_gallery as gallery

    gallery.main()


def capture_one(category, component, delay):
    IMGS.mkdir(exist_ok=True)
    out_path = IMGS / f"{component}.png"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, str(pathlib.Path(__file__).resolve()), "--child", category, component],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        hwnd = None
        for _ in range(120):
            hwnd = find_window_for_pid(proc.pid)
            if hwnd:
                break
            if proc.poll() is not None:
                raise RuntimeError("gallery process exited before creating a window")
            time.sleep(0.25)
        if not hwnd:
            raise RuntimeError("gallery window was not found")
        time.sleep(delay)
        print_window(hwnd, out_path)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", nargs=2, metavar=("CATEGORY", "COMPONENT"))
    parser.add_argument("--only")
    parser.add_argument("--delay", type=float, default=2.5)
    args = parser.parse_args()

    if args.child:
        run_capture_child(args.child[0], args.child[1])
        return

    for old in IMGS.glob("_screenshot_test_*.png"):
        old.unlink()

    records = collect_components()
    if args.only:
        records = [(cat, name) for cat, name in records if name == args.only]
    failures = []
    for index, (category, component) in enumerate(records, 1):
        try:
            out_path = capture_one(category, component, args.delay)
            print(f"[{index}/{len(records)}] saved {out_path.name}")
        except Exception as exc:
            failures.append((category, component, str(exc)))
            print(f"[{index}/{len(records)}] failed {category}/{component}: {exc}")
    if failures:
        print("FAILURES:")
        for category, component, error in failures:
            print(f"- {category}/{component}: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
