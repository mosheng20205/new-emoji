import ctypes
from ctypes import wintypes
import os
import tempfile
import time

import test_new_emoji as ui


g_hwnd = None
g_upload_id = 0
g_start_id = 0
g_retry_id = 0
g_clear_id = 0
g_selected_text = ""
g_action_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 上传完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.TextCallback
def on_select(element_id, data, length):
    global g_selected_text
    raw = ctypes.string_at(data, length) if data and length > 0 else b""
    g_selected_text = raw.decode("utf-8", errors="replace")
    print(f"[选择回调] 元素={element_id} 文件={g_selected_text}")


@ui.ValueCallback
def on_upload_action(element_id, action, index, value):
    g_action_events.append((action, index, value))
    print(f"[上传动作回调] 元素={element_id} 动作={action} 索引={index} 值={value}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_start_id:
        ui.start_upload(g_hwnd, g_upload_id, -1)
        print("[按钮] 开始上传：", ui.get_upload_full_state(g_hwnd, g_upload_id))
    elif element_id == g_retry_id:
        ui.retry_upload_file(g_hwnd, g_upload_id, 0)
        print("[按钮] 重试首项：", ui.get_upload_full_state(g_hwnd, g_upload_id))
    elif element_id == g_clear_id:
        ui.clear_upload_files(g_hwnd, g_upload_id)
        print("[按钮] 清空列表：", ui.get_upload_full_state(g_hwnd, g_upload_id))


def make_sample_files():
    folder = tempfile.mkdtemp(prefix="new_emoji_upload_")
    names = ["发布说明.txt", "封面素材.png", "演示数据.csv"]
    paths = []
    for name in names:
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"📤 上传组件验证文件：{name}\n")
        paths.append(path)
    return paths


def pump_messages(user32, msg, duration):
    start = time.time()
    running = True
    while running and time.time() - start < duration:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                running = False
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)
    return running


def main():
    global g_hwnd, g_upload_id, g_start_id, g_retry_id, g_clear_id

    sample_files = make_sample_files()
    hwnd = ui.create_window("📤 上传完整组件验证", 220, 80, 1000, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 620)

    ui.create_text(hwnd, content_id, "📤 Upload 上传完整封装", 28, 24, 430, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证真实文件选择入口、选择结果写入文件列表、选择/上传回调、重试/删除/清空和完整状态读回。",
        28, 72, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_upload_id = ui.create_upload(
        hwnd,
        content_id,
        "📤 点击可打开系统文件选择，也可由 API 写入待上传文件",
        "支持多选、自动上传、状态更新、失败重试和结果读回",
        [],
        46,
        145,
        760,
        310,
    )
    ui.set_upload_select_callback(hwnd, g_upload_id, on_select)
    ui.set_upload_action_callback(hwnd, g_upload_id, on_upload_action)
    ui.set_upload_options(hwnd, g_upload_id, multiple=True, auto_upload=False)

    g_start_id = ui.create_button(hwnd, content_id, "🚀", "开始上传", 46, 490, 130, 40)
    g_retry_id = ui.create_button(hwnd, content_id, "🔁", "重试首项", 196, 490, 130, 40)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空列表", 346, 490, 130, 40)
    for eid in (g_start_id, g_retry_id, g_clear_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    status_id = ui.create_text(hwnd, content_id, "✅ 控制台会输出选择、上传、重试、删除、清空的状态。", 46, 550, 760, 34)
    ui.set_text_options(hwnd, status_id, align=0, valign=0, wrap=False, ellipsis=False)

    initial = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[初始状态] ", initial)
    if not initial or initial["file_count"] != 0 or not initial["multiple"] or initial["auto_upload"]:
        raise RuntimeError("上传组件初始状态读回失败")

    ui.set_upload_selected_files(hwnd, g_upload_id, sample_files[:2])
    selected = ui.get_upload_full_state(hwnd, g_upload_id)
    selected_text = ui.get_upload_selected_files(hwnd, g_upload_id)
    print("[选择写入] ", selected, selected_text)
    if selected["file_count"] != 2 or selected["waiting_count"] != 2 or selected["last_action"] != 2:
        raise RuntimeError("上传选择结果写入失败")
    if sample_files[0] not in selected_text or "发布说明.txt" not in ui.get_upload_file_name(hwnd, g_upload_id, 0):
        raise RuntimeError("上传文件名或完整路径读回失败")
    if g_selected_text != selected_text:
        raise RuntimeError("上传选择回调未返回 UTF-8 文件列表")

    started = ui.start_upload(hwnd, g_upload_id, -1)
    uploading = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[开始上传] ", started, uploading)
    if started != 2 or uploading["uploading_count"] != 2 or uploading["upload_request_count"] != 2:
        raise RuntimeError("上传开始动作失败")

    ui.dll.EU_SetUploadFileStatus(hwnd, g_upload_id, 0, 1, 100)
    ui.dll.EU_SetUploadFileStatus(hwnd, g_upload_id, 1, 3, 45)
    mixed = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[状态更新] ", mixed)
    if mixed["success_count"] != 1 or mixed["failed_count"] != 1:
        raise RuntimeError("上传成功/失败状态读回失败")

    ui.retry_upload_file(hwnd, g_upload_id, 1)
    retried = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[失败重试] ", retried)
    if retried["retry_count"] != 1 or retried["uploading_count"] != 1:
        raise RuntimeError("上传重试状态失败")

    ui.remove_upload_file(hwnd, g_upload_id, 0)
    removed = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[删除文件] ", removed)
    if removed["file_count"] != 1 or removed["remove_count"] != 1:
        raise RuntimeError("上传删除状态失败")

    ui.set_upload_options(hwnd, g_upload_id, multiple=True, auto_upload=True)
    ui.set_upload_selected_files(hwnd, g_upload_id, sample_files)
    auto_state = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[自动上传选择] ", auto_state)
    if not auto_state["auto_upload"] or auto_state["file_count"] != 3 or auto_state["uploading_count"] != 3:
        raise RuntimeError("上传自动上传状态失败")
    if auto_state["upload_request_count"] < 6 or auto_state["last_action"] != 3:
        raise RuntimeError("上传自动上传回调/计数失败")

    ui.clear_upload_files(hwnd, g_upload_id)
    cleared = ui.get_upload_full_state(hwnd, g_upload_id)
    print("[清空文件] ", cleared)
    if cleared["file_count"] != 0 or cleared["last_action"] != 6:
        raise RuntimeError("上传清空状态失败")
    if not any(event[0] == 3 for event in g_action_events):
        raise RuntimeError("上传动作回调未触发")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("上传完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 60:
        running = pump_messages(user32, msg, 0.05)

    print("上传完整组件示例结束。")


if __name__ == "__main__":
    main()
