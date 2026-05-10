using System;

namespace NewEmoji;

public readonly struct EmojiRect
{
    public EmojiRect(int x, int y, int width, int height)
    {
        X = x;
        Y = y;
        Width = width;
        Height = height;
    }

    public int X { get; }
    public int Y { get; }
    public int Width { get; }
    public int Height { get; }
}

public enum EmojiMessageType
{
    Info = 0,
    Success = 1,
    Warning = 2,
    Error = 3,
}

public enum EmojiWindowFrameFlags
{
    Default = 0x0000,
    Borderless = 0x0001,
    CustomCaption = 0x0002,
    CustomButtons = 0x0004,
    Resizable = 0x0008,
    Rounded = 0x0010,
    HideTitleBar = 0x0020,
    BrowserShell = Borderless | CustomCaption | CustomButtons | Resizable | Rounded | HideTitleBar,
}

public sealed class EmojiResizeEventArgs : EventArgs
{
    public EmojiResizeEventArgs(int width, int height)
    {
        Width = width;
        Height = height;
    }

    public int Width { get; }
    public int Height { get; }
}

public sealed class EmojiTextChangedEventArgs : EventArgs
{
    public EmojiTextChangedEventArgs(string text)
    {
        Text = text;
    }

    public string Text { get; }
}

public sealed class EmojiValueChangedEventArgs : EventArgs
{
    public EmojiValueChangedEventArgs(int value, int rangeStart, int rangeEnd)
    {
        Value = value;
        RangeStart = rangeStart;
        RangeEnd = rangeEnd;
    }

    public int Value { get; }
    public int RangeStart { get; }
    public int RangeEnd { get; }
}

public sealed class EmojiTableCellEventArgs : EventArgs
{
    public EmojiTableCellEventArgs(int row, int column, int action, int value)
    {
        Row = row;
        Column = column;
        Action = action;
        Value = value;
    }

    public int Row { get; }
    public int Column { get; }
    public int Action { get; }
    public int Value { get; }
}

public sealed class EmojiTableCellEditEventArgs : EventArgs
{
    public EmojiTableCellEditEventArgs(int row, int column, int action, string text)
    {
        Row = row;
        Column = column;
        Action = action;
        Text = text;
    }

    public int Row { get; }
    public int Column { get; }
    public int Action { get; }
    public string Text { get; }
}

public sealed class EmojiTableEditState
{
    public bool Enabled { get; set; }
    public int EditingRow { get; set; }
    public int EditingColumn { get; set; }
}

public sealed class EmojiTableOptions
{
    public bool Striped { get; set; }
    public bool Bordered { get; set; }
    public int RowHeight { get; set; }
    public int HeaderHeight { get; set; }
    public bool Selectable { get; set; }
    public int SortColumn { get; set; }
    public bool SortDescending { get; set; }
    public int ScrollRow { get; set; }
    public int ColumnWidth { get; set; }
}

public sealed class EmojiTabsState
{
    public int ActiveIndex { get; set; }
    public int ItemCount { get; set; }
    public int TabType { get; set; }
}

public sealed class EmojiDialogOptions
{
    public bool Open { get; set; }
    public bool Modal { get; set; }
    public bool Closable { get; set; }
    public bool CloseOnMask { get; set; }
    public bool Draggable { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
}

public sealed class EmojiCardOptions
{
    public bool Shadow { get; set; }
    public bool Hoverable { get; set; }
    public int ActionCount { get; set; }
}

public sealed class EmojiDrawerOptions
{
    public int Placement { get; set; }
    public bool Open { get; set; }
    public bool Modal { get; set; }
    public bool Closable { get; set; }
    public bool CloseOnMask { get; set; }
    public int Size { get; set; }
}

public sealed class EmojiDrawerAdvancedOptions
{
    public bool ShowHeader { get; set; }
    public bool ShowClose { get; set; }
    public bool CloseOnEscape { get; set; }
    public int ContentPadding { get; set; }
    public int FooterHeight { get; set; }
    public int SizeMode { get; set; }
    public int SizeValue { get; set; }
    public int ContentParentId { get; set; }
    public int FooterParentId { get; set; }
    public bool ClosePending { get; set; }
}

public sealed class EmojiNotificationOptions
{
    public int Type { get; set; }
    public bool Closable { get; set; }
    public int DurationMs { get; set; }
    public bool Closed { get; set; }
}

public sealed class EmojiNotificationState
{
    public int Type { get; set; }
    public bool Closable { get; set; }
    public int DurationMs { get; set; }
    public bool Closed { get; set; }
    public int CloseHover { get; set; }
    public int CloseDown { get; set; }
    public int CloseCount { get; set; }
    public int LastAction { get; set; }
    public int TimerElapsedMs { get; set; }
    public bool TimerRunning { get; set; }
    public int StackIndex { get; set; }
    public int StackGap { get; set; }
    public int Placement { get; set; }
    public int Offset { get; set; }
    public bool Rich { get; set; }
}
