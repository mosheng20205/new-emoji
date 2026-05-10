using NewEmoji;

class Program
{
    static void Main()
    {
        var win = EmojiWindow.Create("✅ new_emoji C# 示例", 860, 560);
        var root = win.CreateContainer(0, 0, 820, 500);

        root.AddText("欢迎使用 new_emoji C# 界面库 🚀", 32, 32, 420, 40);
        var input = root.AddInput("", "请输入一段中文或 emoji 😊", 32, 88, 320, 42);
        input.TextChanged += (_, e) => win.SetTitle($"✅ 输入中：{e.Text}");

        root.AddButton("✅", "确认操作", 32, 152, 160, 42)
            .Clicked += (_, _) => win.ShowMessage("操作成功 🎉", EmojiMessageType.Success, closable: true);

        win.Show();
        EmojiApplication.Run();
    }
}
