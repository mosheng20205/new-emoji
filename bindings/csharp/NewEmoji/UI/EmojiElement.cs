using System;
using System.Runtime.InteropServices;
using NewEmoji.Native;

namespace NewEmoji;

public class EmojiElement
{
    private ElementClickCallback? _clickCallback;
    private event EventHandler? _clicked;

    internal EmojiElement(EmojiWindow window, int id)
    {
        Window = window ?? throw new ArgumentNullException(nameof(window));
        Id = EmojiWindow.EnsureElementId(id, "Element");
    }

    public EmojiWindow Window { get; }

    public int Id { get; }

    public event EventHandler? Clicked
    {
        add
        {
            _clicked += value;
            EnsureClickCallback();
        }
        remove => _clicked -= value;
    }

    public virtual string Text
    {
        get => NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetElementText(Window.Handle, Id, buffer, size));
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetElementText(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public EmojiRect Bounds
    {
        get => GetBounds();
        set => SetBounds(value.X, value.Y, value.Width, value.Height);
    }

    public bool Visible
    {
        get => NativeMethods.EU_GetElementVisible(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetElementVisible(Window.Handle, Id, value ? 1 : 0);
    }

    public bool Enabled
    {
        get => NativeMethods.EU_GetElementEnabled(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetElementEnabled(Window.Handle, Id, value ? 1 : 0);
    }

    internal static EmojiElement Wrap(EmojiWindow window, int id, string? componentName)
    {
        var ensuredId = EmojiWindow.EnsureElementId(id, componentName ?? "Element");
        return componentName switch
        {
            "Button" => new EmojiButton(window, ensuredId),
            "Container" => new EmojiContainer(window, ensuredId),
            "Panel" => new EmojiPanel(window, ensuredId),
            "Text" => new EmojiText(window, ensuredId),
            "Input" => new EmojiInput(window, ensuredId),
            "Select" => new EmojiSelect(window, ensuredId),
            "Checkbox" => new EmojiCheckbox(window, ensuredId),
            "Radio" => new EmojiRadio(window, ensuredId),
            "Switch" => new EmojiSwitch(window, ensuredId),
            "Slider" => new EmojiSlider(window, ensuredId),
            "EditBox" => new EmojiEditBox(window, ensuredId),
            "Table" => new EmojiTable(window, ensuredId),
            "Tabs" => new EmojiTabs(window, ensuredId),
            "Dialog" => new EmojiDialog(window, ensuredId),
            "Card" => new EmojiCard(window, ensuredId),
            "Drawer" => new EmojiDrawer(window, ensuredId),
            "Notification" => new EmojiNotification(window, ensuredId),
            _ => new EmojiElement(window, ensuredId),
        };
    }

    public void SetText(string text)
    {
        Text = text;
    }

    public void SetBounds(int x, int y, int width, int height)
    {
        NativeMethods.EU_SetElementBounds(Window.Handle, Id, x, y, width, height);
    }

    public EmojiRect GetBounds()
    {
        var x = Marshal.AllocHGlobal(sizeof(int));
        var y = Marshal.AllocHGlobal(sizeof(int));
        var width = Marshal.AllocHGlobal(sizeof(int));
        var height = Marshal.AllocHGlobal(sizeof(int));
        try
        {
            var ok = NativeMethods.EU_GetElementBounds(Window.Handle, Id, x, y, width, height);
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

    public void SetColor(uint background, uint foreground)
    {
        NativeMethods.EU_SetElementColor(Window.Handle, Id, background, foreground);
    }

    public void SetFont(string fontName, float size)
    {
        var bytes = NativeUtf8.GetBytes(fontName);
        NativeMethods.EU_SetElementFont(Window.Handle, Id, bytes, bytes.Length, size);
    }

    public void Focus()
    {
        NativeMethods.EU_SetElementFocus(Window.Handle, Id);
    }

    public void Invalidate()
    {
        NativeMethods.EU_InvalidateElement(Window.Handle, Id);
    }

    public EmojiContainer AddContainer(int x, int y, int width, int height)
    {
        var id = NativeMethods.EU_CreateContainer(Window.Handle, Id, x, y, width, height);
        return new EmojiContainer(Window, EmojiWindow.EnsureElementId(id, "Container"));
    }

    public EmojiPanel AddPanel(int x, int y, int width, int height)
    {
        var id = NativeMethods.EU_CreatePanel(Window.Handle, Id, x, y, width, height);
        return new EmojiPanel(Window, EmojiWindow.EnsureElementId(id, "Panel"));
    }

    public EmojiText AddText(string text, int x, int y, int width, int height)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateText(Window.Handle, Id, bytes, bytes.Length, x, y, width, height);
        return new EmojiText(Window, EmojiWindow.EnsureElementId(id, "Text"));
    }

    public EmojiButton AddButton(string emoji, string text, int x, int y, int width, int height)
    {
        var emojiBytes = NativeUtf8.GetBytes(emoji);
        var textBytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateButton(Window.Handle, Id, emojiBytes, emojiBytes.Length, textBytes, textBytes.Length, x, y, width, height);
        return new EmojiButton(Window, EmojiWindow.EnsureElementId(id, "Button"));
    }

    public EmojiInput AddInput(
        string text,
        string placeholder,
        int x,
        int y,
        int width,
        int height,
        string prefix = "",
        string suffix = "",
        bool clearable = true)
    {
        var textBytes = NativeUtf8.GetBytes(text);
        var placeholderBytes = NativeUtf8.GetBytes(placeholder);
        var prefixBytes = NativeUtf8.GetBytes(prefix);
        var suffixBytes = NativeUtf8.GetBytes(suffix);
        var id = NativeMethods.EU_CreateInput(
            Window.Handle,
            Id,
            textBytes,
            textBytes.Length,
            placeholderBytes,
            placeholderBytes.Length,
            prefixBytes,
            prefixBytes.Length,
            suffixBytes,
            suffixBytes.Length,
            clearable ? 1 : 0,
            x,
            y,
            width,
            height);
        return new EmojiInput(Window, EmojiWindow.EnsureElementId(id, "Input"));
    }

    public EmojiEditBox AddEditBox(int x, int y, int width, int height, string text = "")
    {
        var id = NativeMethods.EU_CreateEditBox(Window.Handle, Id, x, y, width, height);
        var editBox = new EmojiEditBox(Window, EmojiWindow.EnsureElementId(id, "EditBox"));
        if (!string.IsNullOrEmpty(text))
        {
            editBox.Text = text;
        }

        return editBox;
    }

    public EmojiCheckbox AddCheckbox(string text, bool isChecked, int x, int y, int width, int height)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateCheckbox(Window.Handle, Id, bytes, bytes.Length, isChecked ? 1 : 0, x, y, width, height);
        return new EmojiCheckbox(Window, EmojiWindow.EnsureElementId(id, "Checkbox"));
    }

    public EmojiRadio AddRadio(string text, bool isChecked, int x, int y, int width, int height)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateRadio(Window.Handle, Id, bytes, bytes.Length, isChecked ? 1 : 0, x, y, width, height);
        return new EmojiRadio(Window, EmojiWindow.EnsureElementId(id, "Radio"));
    }

    public EmojiSwitch AddSwitch(string text, bool isChecked, int x, int y, int width, int height)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateSwitch(Window.Handle, Id, bytes, bytes.Length, isChecked ? 1 : 0, x, y, width, height);
        return new EmojiSwitch(Window, EmojiWindow.EnsureElementId(id, "Switch"));
    }

    public EmojiSlider AddSlider(string text, int minValue, int maxValue, int value, int x, int y, int width, int height)
    {
        var bytes = NativeUtf8.GetBytes(text);
        var id = NativeMethods.EU_CreateSlider(Window.Handle, Id, bytes, bytes.Length, minValue, maxValue, value, x, y, width, height);
        return new EmojiSlider(Window, EmojiWindow.EnsureElementId(id, "Slider"));
    }

    public EmojiSelect AddSelect(string text, string options, int selectedIndex, int x, int y, int width, int height)
    {
        var textBytes = NativeUtf8.GetBytes(text);
        var optionBytes = NativeUtf8.GetBytes(options);
        var id = NativeMethods.EU_CreateSelect(Window.Handle, Id, textBytes, textBytes.Length, optionBytes, optionBytes.Length, selectedIndex, x, y, width, height);
        return new EmojiSelect(Window, EmojiWindow.EnsureElementId(id, "Select"));
    }

    public EmojiTable AddTable(string columns, string rows, int x, int y, int width, int height, bool striped = true, bool bordered = true)
    {
        var columnBytes = NativeUtf8.GetBytes(columns);
        var rowBytes = NativeUtf8.GetBytes(rows);
        var id = NativeMethods.EU_CreateTable(Window.Handle, Id, columnBytes, columnBytes.Length, rowBytes, rowBytes.Length, striped ? 1 : 0, bordered ? 1 : 0, x, y, width, height);
        return new EmojiTable(Window, EmojiWindow.EnsureElementId(id, "Table"));
    }

    public EmojiTabs AddTabs(string items, int activeIndex, int tabType, int x, int y, int width, int height)
    {
        var itemBytes = NativeUtf8.GetBytes(items);
        var id = NativeMethods.EU_CreateTabs(Window.Handle, Id, itemBytes, itemBytes.Length, activeIndex, tabType, x, y, width, height);
        return new EmojiTabs(Window, EmojiWindow.EnsureElementId(id, "Tabs"));
    }

    public EmojiCard AddCard(string title, string body, bool shadow, int x, int y, int width, int height)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var bodyBytes = NativeUtf8.GetBytes(body);
        var id = NativeMethods.EU_CreateCard(Window.Handle, Id, titleBytes, titleBytes.Length, bodyBytes, bodyBytes.Length, shadow ? 1 : 0, x, y, width, height);
        return new EmojiCard(Window, EmojiWindow.EnsureElementId(id, "Card"));
    }

    public EmojiNotification AddNotification(string title, string body, EmojiMessageType type, bool closable, int x, int y, int width, int height)
    {
        var titleBytes = NativeUtf8.GetBytes(title);
        var bodyBytes = NativeUtf8.GetBytes(body);
        var id = NativeMethods.EU_CreateNotification(Window.Handle, Id, titleBytes, titleBytes.Length, bodyBytes, bodyBytes.Length, (int)type, closable ? 1 : 0, x, y, width, height);
        return new EmojiNotification(Window, EmojiWindow.EnsureElementId(id, "Notification"));
    }

    private void EnsureClickCallback()
    {
        if (_clickCallback is not null)
        {
            return;
        }

        _clickCallback = elementId =>
        {
            if (elementId == Id)
            {
                _clicked?.Invoke(this, EventArgs.Empty);
            }
        };
        NativeMethods.EU_SetElementClickCallback(Window.Handle, Id, _clickCallback);
    }
}
