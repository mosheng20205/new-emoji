using System;
using System.Windows.Forms;
using NewEmoji;

namespace NewEmojiNet48Example
{
    internal static class Program
    {
        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            var win = EmojiWindow.Create("✅ new_emoji .NET 4.8 示例", 900, 600);
            win.Closing += (_, _) => Application.ExitThread();

            var root = win.CreateContainer(0, 0, 860, 540);
            root.AddText("欢迎使用 WinForms .NET Framework 4.8 封装 🚀", 32, 32, 520, 40);

            var input = root.AddInput("", "请输入中文或 emoji 😊", 32, 88, 340, 42);
            input.TextChanged += (_, e) => win.SetTitle($"✅ .NET 4.8 输入：{e.Text}");

            root.AddButton("✅", "确认操作", 32, 152, 160, 42)
                .Clicked += (_, _) => win.ShowMessage("WinForms .NET 4.8 调用成功 🎉", EmojiMessageType.Success, closable: true);

            win.Show();
            Application.Run();
        }
    }
}
