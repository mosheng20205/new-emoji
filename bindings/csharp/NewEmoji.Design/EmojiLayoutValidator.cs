using System;
using System.Collections.Generic;

namespace NewEmoji.Design;

public sealed class EmojiLayoutValidator
{
    private static readonly HashSet<string> SupportedTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        "Container",
        "Panel",
        "Text",
        "Button",
        "Input",
        "EditBox",
        "Table",
        "Card",
        "Tabs",
        "Dialog",
        "Drawer",
        "Notification",
    };

    public IReadOnlyList<string> Validate(EmojiLayoutDocument document)
    {
        var errors = new List<string>();
        if (document.SchemaVersion != 1)
        {
            errors.Add("schemaVersion 必须为 1。");
        }

        if (document.Window.Width <= 0 || document.Window.Height <= 0)
        {
            errors.Add("窗口宽高必须大于 0。");
        }

        ValidateElement(document.Root, "root", document.Root.Bounds, errors);

        var rootRight = document.Root.Bounds.X + document.Root.Bounds.Width;
        var rootBottom = document.Root.Bounds.Y + document.Root.Bounds.Height;
        if (document.Window.Width < rootRight + 20 || document.Window.Height < rootBottom + 20)
        {
            errors.Add("窗口首次尺寸必须覆盖根容器，并保留至少 20px 逻辑余量。");
        }

        return errors;
    }

    private static void ValidateElement(EmojiElementDesign element, string path, EmojiBounds parentBounds, List<string> errors)
    {
        if (!SupportedTypes.Contains(element.Type))
        {
            errors.Add($"{path}: 暂不支持组件类型 {element.Type}。");
        }

        if (string.IsNullOrWhiteSpace(element.Name))
        {
            errors.Add($"{path}: name 不能为空。");
        }

        if (element.Bounds.Width <= 0 || element.Bounds.Height <= 0)
        {
            errors.Add($"{path}: width/height 必须大于 0。");
        }

        foreach (var child in element.Children)
        {
            ValidateElement(child, $"{path}.{child.Name}", element.Bounds, errors);
        }
    }
}
