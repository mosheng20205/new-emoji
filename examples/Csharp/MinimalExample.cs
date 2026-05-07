using System;
using System.Runtime.InteropServices;
using System.Text;

class Program
{
    [DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
    static extern IntPtr EU_CreateWindow(byte[] title, int titleLen, int x, int y, int w, int h, uint titlebarColor);

    [DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
    static extern int EU_CreateContainer(IntPtr hwnd, int parentId, int x, int y, int w, int h);

    [DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
    static extern int EU_CreateText(IntPtr hwnd, int parentId, byte[] text, int textLen, int x, int y, int w, int h);

    [DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
    static extern int EU_CreateButton(IntPtr hwnd, int parentId, byte[] emoji, int emojiLen, byte[] text, int textLen, int x, int y, int w, int h);

    [DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
    static extern void EU_ShowWindow(IntPtr hwnd, int visible);

    [DllImport("user32.dll")] static extern int GetMessageW(out MSG msg, IntPtr hwnd, uint min, uint max);
    [DllImport("user32.dll")] static extern bool TranslateMessage(ref MSG msg);
    [DllImport("user32.dll")] static extern IntPtr DispatchMessageW(ref MSG msg);

    [StructLayout(LayoutKind.Sequential)]
    struct MSG { public IntPtr hwnd; public uint message; public UIntPtr wParam; public IntPtr lParam; public uint time; public int ptX; public int ptY; }

    static byte[] U8(string text) => Encoding.UTF8.GetBytes(text);

    static void Main()
    {
        byte[] title = U8("✨ new_emoji 示例");
        IntPtr hwnd = EU_CreateWindow(title, title.Length, 240, 120, 820, 560, 0xFF2D7DFF);
        int root = EU_CreateContainer(hwnd, 0, 0, 0, 780, 500);

        byte[] hello = U8("你好，new_emoji 🚀");
        EU_CreateText(hwnd, root, hello, hello.Length, 32, 32, 360, 40);

        byte[] emoji = U8("✅");
        byte[] button = U8("确认操作");
        EU_CreateButton(hwnd, root, emoji, emoji.Length, button, button.Length, 32, 96, 160, 42);

        EU_ShowWindow(hwnd, 1);
        while (GetMessageW(out MSG msg, IntPtr.Zero, 0, 0) > 0)
        {
            TranslateMessage(ref msg);
            DispatchMessageW(ref msg);
        }
    }
}
