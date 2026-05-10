using NewEmoji;

class BlankWindow
{
    static void Main()
    {
        var win = EmojiWindow.Create("✅ C# 空白窗口", 860, 560);
        var root = win.CreateContainer(0, 0, 820, 500);

        root.AddText("欢迎使用 new_emoji 🚀", 32, 32, 460, 40);
        root.AddButton("✅", "确认操作", 32, 96, 160, 42)
            .Clicked += (_, _) => win.ShowMessage("操作成功 🎉", EmojiMessageType.Success);

        win.Show();
        EmojiApplication.Run();
    }
}
