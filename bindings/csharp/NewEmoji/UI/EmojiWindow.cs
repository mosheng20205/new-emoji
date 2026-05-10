using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using NewEmoji.Native;

namespace NewEmoji;

public sealed class EmojiWindow : IDisposable
{
    private WindowResizeCallback? _resizeCallback;
    private WindowCloseCallback? _closeCallback;
    private readonly List<Delegate> _callbackRoots = new();
    private bool _disposed;

    private EmojiWindow(IntPtr handle)
    {
        Handle = handle == IntPtr.Zero ? throw new InvalidOperationException("EU_CreateWindow 返回了空 HWND。") : handle;
    }

    public IntPtr Handle { get; }

    public event EventHandler<EmojiResizeEventArgs>? Resized
    {
        add
        {
            _resized += value;
            EnsureResizeCallback();
        }
        remove => _resized -= value;
    }

    public event EventHandler? Closing
    {
        add
        {
            _closing += value;
            EnsureCloseCallback();
        }
        remove => _closing -= value;
    }

    private event EventHandler<EmojiResizeEventArgs>? _resized;
    private event EventHandler? _closing;

    public static EmojiWindow Create(
        string title,
        int width,
        int height,
        int x = 240,
        int y = 120,
        uint titlebarColor = 0xFF2D7DFF)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        return new EmojiWindow(NativeMethods.EU_CreateWindow(titleBytes, titleBytes.Length, x, y, width, height, titlebarColor));
    }

    public static EmojiWindow CreateDark(
        string title,
        int width,
        int height,
        int x = 240,
        int y = 120,
        uint titlebarColor = 0xFF1F2937)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        return new EmojiWindow(NativeMethods.EU_CreateWindowDark(titleBytes, titleBytes.Length, x, y, width, height, titlebarColor));
    }

    public static EmojiWindow CreateEx(
        string title,
        int width,
        int height,
        EmojiWindowFrameFlags frameFlags,
        int x = 240,
        int y = 120,
        uint titlebarColor = 0xFF2D7DFF)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        return new EmojiWindow(NativeMethods.EU_CreateWindowEx(titleBytes, titleBytes.Length, x, y, width, height, titlebarColor, (int)frameFlags));
    }

    public EmojiContainer CreateContainer(int x, int y, int width, int height, int parentId = 0)
    {
        var id = NativeMethods.EU_CreateContainer(Handle, parentId, x, y, width, height);
        return new EmojiContainer(this, EnsureElementId(id, "Container"));
    }

    public EmojiPanel CreatePanel(int x, int y, int width, int height, int parentId = 0)
    {
        var id = NativeMethods.EU_CreatePanel(Handle, parentId, x, y, width, height);
        return new EmojiPanel(this, EnsureElementId(id, "Panel"));
    }

    public EmojiElement WrapElement(int elementId)
    {
        return EmojiElement.Wrap(this, elementId, null);
    }

    public void Show(bool visible = true)
    {
        NativeMethods.EU_ShowWindow(Handle, visible ? 1 : 0);
    }

    public void Close()
    {
        Dispose();
    }

    public void SetTitle(string title)
    {
        var bytes = NativeUtf8.GetBytes(title);
        NativeMethods.EU_SetWindowTitle(Handle, bytes, bytes.Length);
    }

    public int SetIcon(string path)
    {
        var bytes = NativeUtf8.GetBytes(path);
        return NativeMethods.EU_SetWindowIcon(Handle, bytes, bytes.Length);
    }

    public int SetIconBytes(byte[] iconBytes)
    {
        if (iconBytes is null)
        {
            throw new ArgumentNullException(nameof(iconBytes));
        }

        return NativeMethods.EU_SetWindowIconFromBytes(Handle, iconBytes, iconBytes.Length);
    }

    public void SetBounds(int x, int y, int width, int height)
    {
        NativeMethods.EU_SetWindowBounds(Handle, x, y, width, height);
    }

    public EmojiRect GetBounds()
    {
        var x = Marshal.AllocHGlobal(sizeof(int));
        var y = Marshal.AllocHGlobal(sizeof(int));
        var width = Marshal.AllocHGlobal(sizeof(int));
        var height = Marshal.AllocHGlobal(sizeof(int));
        try
        {
            var ok = NativeMethods.EU_GetWindowBounds(Handle, x, y, width, height);
            if (ok == 0)
            {
                return default;
            }

            return new EmojiRect(Marshal.ReadInt32(x), Marshal.ReadInt32(y), Marshal.ReadInt32(width), Marshal.ReadInt32(height));
        }
        finally
        {
            Marshal.FreeHGlobal(x);
            Marshal.FreeHGlobal(y);
            Marshal.FreeHGlobal(width);
            Marshal.FreeHGlobal(height);
        }
    }

    public void SetRoundedCorners(bool enabled, int radius)
    {
        NativeMethods.EU_SetWindowRoundedCorners(Handle, enabled ? 1 : 0, radius);
    }

    public EmojiElement ShowMessage(
        string text,
        EmojiMessageType type = EmojiMessageType.Info,
        bool closable = false,
        bool center = false,
        bool rich = false,
        int durationMs = 3000,
        int offset = 20)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_ShowMessage(Handle, bytes, bytes.Length, (int)type, closable ? 1 : 0, center ? 1 : 0, rich ? 1 : 0, durationMs, offset);
        return EmojiElement.Wrap(this, id, "Message");
    }

    public EmojiDialog CreateDialog(string title, string body, bool modal = true, bool closable = true, int width = 420, int height = 240)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var bodyBytes = NativeUtf8.GetBytes(body);
        var id = NativeMethods.EU_CreateDialog(Handle, titleBytes, titleBytes.Length, bodyBytes, bodyBytes.Length, modal ? 1 : 0, closable ? 1 : 0, width, height);
        return new EmojiDialog(this, EnsureElementId(id, "Dialog"));
    }

    public EmojiNotification ShowNotification(
        string title,
        string body,
        EmojiMessageType type = EmojiMessageType.Info,
        bool closable = true,
        int durationMs = 4500,
        int placement = 1,
        int offset = 20,
        bool rich = false,
        int width = 360,
        int height = 110)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var bodyBytes = NativeUtf8.GetBytes(body);
        var id = NativeMethods.EU_ShowNotification(Handle, titleBytes, titleBytes.Length, bodyBytes, bodyBytes.Length, (int)type, closable ? 1 : 0, durationMs, placement, offset, rich ? 1 : 0, width, height);
        return new EmojiNotification(this, EnsureElementId(id, "Notification"));
    }

    public EmojiDrawer CreateDrawer(string title, string body, int placement = 1, bool modal = true, bool closable = true, int size = 320)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var bodyBytes = NativeUtf8.GetBytes(body);
        var id = NativeMethods.EU_CreateDrawer(Handle, titleBytes, titleBytes.Length, bodyBytes, bodyBytes.Length, placement, modal ? 1 : 0, closable ? 1 : 0, size);
        return new EmojiDrawer(this, EnsureElementId(id, "Drawer"));
    }

    public EmojiElement ShowMessageBox(
        string title,
        string text,
        string confirm = "确定 ✅",
        string cancel = "取消",
        EmojiMessageType type = EmojiMessageType.Info,
        bool showCancel = false,
        bool center = false,
        bool rich = false,
        bool distinguishCancelAndClose = false,
        Action<int, string>? result = null)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var textBytes = NativeUtf8.GetBytes(text);
        var confirmBytes = NativeUtf8.GetBytes(confirm);
        var cancelBytes = NativeUtf8.GetBytes(cancel);
        MessageBoxExCallback callback = (_, action, valueUtf8, valueLen) =>
        {
            result?.Invoke(action, NativeUtf8.FromPointer(valueUtf8, valueLen));
        };
        _callbackRoots.Add(callback);
        var id = NativeMethods.EU_ShowMessageBoxEx(
            Handle,
            titleBytes,
            titleBytes.Length,
            textBytes,
            textBytes.Length,
            confirmBytes,
            confirmBytes.Length,
            cancelBytes,
            cancelBytes.Length,
            (int)type,
            showCancel ? 1 : 0,
            center ? 1 : 0,
            rich ? 1 : 0,
            distinguishCancelAndClose ? 1 : 0,
            callback);
        return EmojiElement.Wrap(this, id, "MessageBox");
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        NativeMethods.EU_DestroyWindow(Handle);
        GC.SuppressFinalize(this);
    }

    internal static int EnsureElementId(int id, string componentName)
    {
        if (id == 0)
        {
            throw new InvalidOperationException($"创建 {componentName} 组件失败。");
        }

        return id;
    }

    private void EnsureResizeCallback()
    {
        if (_resizeCallback is not null)
        {
            return;
        }

        _resizeCallback = (_, width, height) => _resized?.Invoke(this, new EmojiResizeEventArgs(width, height));
        NativeMethods.EU_SetWindowResizeCallback(Handle, _resizeCallback);
    }

    private void EnsureCloseCallback()
    {
        if (_closeCallback is not null)
        {
            return;
        }

        _closeCallback = _ => _closing?.Invoke(this, EventArgs.Empty);
        NativeMethods.EU_SetWindowCloseCallback(Handle, _closeCallback);
    }
}
