using System.Collections.Generic;
using System.Runtime.Serialization;

namespace NewEmoji.Design;

[DataContract]
public sealed class EmojiLayoutDocument
{
    [DataMember(Name = "schemaVersion", Order = 1)]
    public int SchemaVersion { get; set; } = 1;

    [DataMember(Name = "window", Order = 2)]
    public EmojiWindowDesign Window { get; set; } = new();

    [DataMember(Name = "root", Order = 3)]
    public EmojiElementDesign Root { get; set; } = EmojiElementDesign.CreateRoot();

    public static EmojiLayoutDocument CreateDefault()
    {
        var document = new EmojiLayoutDocument();
        document.Root.Children.Add(new EmojiElementDesign
        {
            Type = "Text",
            Name = "titleText",
            Text = "欢迎使用 new_emoji 设计器 🚀",
            Bounds = new EmojiBounds(32, 32, 420, 40),
        });
        document.Root.Children.Add(new EmojiElementDesign
        {
            Type = "Button",
            Name = "confirmButton",
            Text = "确认操作",
            Emoji = "✅",
            Bounds = new EmojiBounds(32, 96, 160, 42),
            Events = new Dictionary<string, string> { ["Clicked"] = "OnConfirmClicked" },
        });
        document.Root.Children.Add(new EmojiElementDesign
        {
            Type = "Input",
            Name = "nameInput",
            Text = "",
            Properties = new Dictionary<string, string> { ["placeholder"] = "请输入中文或 emoji 😊" },
            Bounds = new EmojiBounds(32, 156, 320, 42),
        });
        return document;
    }
}

[DataContract]
public sealed class EmojiWindowDesign
{
    [DataMember(Name = "title", Order = 1)]
    public string Title { get; set; } = "✅ 设计器示例";

    [DataMember(Name = "width", Order = 2)]
    public int Width { get; set; } = 900;

    [DataMember(Name = "height", Order = 3)]
    public int Height { get; set; } = 600;

    [DataMember(Name = "titlebarColor", Order = 4)]
    public string TitlebarColor { get; set; } = "#FF2D7DFF";
}

[DataContract]
public sealed class EmojiElementDesign
{
    [DataMember(Name = "type", Order = 1)]
    public string Type { get; set; } = "Panel";

    [DataMember(Name = "name", Order = 2)]
    public string Name { get; set; } = "element";

    [DataMember(Name = "bounds", Order = 3)]
    public EmojiBounds Bounds { get; set; } = new();

    [DataMember(Name = "text", Order = 4, EmitDefaultValue = false)]
    public string Text { get; set; } = "";

    [DataMember(Name = "emoji", Order = 5, EmitDefaultValue = false)]
    public string Emoji { get; set; } = "";

    [DataMember(Name = "visible", Order = 6, EmitDefaultValue = false)]
    public bool Visible { get; set; } = true;

    [DataMember(Name = "enabled", Order = 7, EmitDefaultValue = false)]
    public bool Enabled { get; set; } = true;

    [DataMember(Name = "properties", Order = 8, EmitDefaultValue = false)]
    public Dictionary<string, string> Properties { get; set; } = new();

    [DataMember(Name = "events", Order = 9, EmitDefaultValue = false)]
    public Dictionary<string, string> Events { get; set; } = new();

    [DataMember(Name = "children", Order = 10, EmitDefaultValue = false)]
    public List<EmojiElementDesign> Children { get; set; } = new();

    [OnDeserializing]
    private void OnDeserializing(StreamingContext context)
    {
        Type = "Panel";
        Name = "element";
        Bounds = new EmojiBounds();
        Text = "";
        Emoji = "";
        Visible = true;
        Enabled = true;
        Properties = new Dictionary<string, string>();
        Events = new Dictionary<string, string>();
        Children = new List<EmojiElementDesign>();
    }

    public static EmojiElementDesign CreateRoot()
    {
        return new EmojiElementDesign
        {
            Type = "Container",
            Name = "root",
            Bounds = new EmojiBounds(0, 0, 860, 540),
        };
    }
}

[DataContract]
public sealed class EmojiBounds
{
    public EmojiBounds()
    {
    }

    public EmojiBounds(int x, int y, int width, int height)
    {
        X = x;
        Y = y;
        Width = width;
        Height = height;
    }

    [DataMember(Name = "x", Order = 1)]
    public int X { get; set; }

    [DataMember(Name = "y", Order = 2)]
    public int Y { get; set; }

    [DataMember(Name = "width", Order = 3)]
    public int Width { get; set; } = 120;

    [DataMember(Name = "height", Order = 4)]
    public int Height { get; set; } = 40;
}
