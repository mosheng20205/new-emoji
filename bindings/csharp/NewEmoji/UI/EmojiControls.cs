using System;
using System.Runtime.InteropServices;
using NewEmoji.Native;

namespace NewEmoji;

public sealed class EmojiContainer : EmojiElement
{
    internal EmojiContainer(EmojiWindow window, int id)
        : base(window, id)
    {
    }
}

public sealed class EmojiPanel : EmojiElement
{
    internal EmojiPanel(EmojiWindow window, int id)
        : base(window, id)
    {
    }
}

public sealed class EmojiText : EmojiElement
{
    internal EmojiText(EmojiWindow window, int id)
        : base(window, id)
    {
    }
}

public sealed class EmojiButton : EmojiElement
{
    internal EmojiButton(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public void SetEmoji(string emoji)
    {
        var bytes = NativeUtf8.GetBytes(emoji);
        NativeMethods.EU_SetButtonEmoji(Window.Handle, Id, bytes, bytes.Length);
    }
}

public sealed class EmojiInput : EmojiElement
{
    private ElementTextCallback? _textCallback;
    private event EventHandler<EmojiTextChangedEventArgs>? _textChanged;

    internal EmojiInput(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiTextChangedEventArgs>? TextChanged
    {
        add
        {
            _textChanged += value;
            EnsureTextCallback();
        }
        remove => _textChanged -= value;
    }

    public override string Text
    {
        get => NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetInputValue(Window.Handle, Id, buffer, size));
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetInputValue(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    private void EnsureTextCallback()
    {
        if (_textCallback is not null)
        {
            return;
        }

        _textCallback = (elementId, utf8, len) =>
        {
            if (elementId == Id)
            {
                _textChanged?.Invoke(this, new EmojiTextChangedEventArgs(NativeUtf8.FromPointer(utf8, len)));
            }
        };
        NativeMethods.EU_SetInputTextCallback(Window.Handle, Id, _textCallback);
    }
}

public sealed class EmojiEditBox : EmojiElement
{
    private ElementTextCallback? _textCallback;
    private event EventHandler<EmojiTextChangedEventArgs>? _textChanged;

    internal EmojiEditBox(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiTextChangedEventArgs>? TextChanged
    {
        add
        {
            _textChanged += value;
            EnsureTextCallback();
        }
        remove => _textChanged -= value;
    }

    public override string Text
    {
        get => NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetEditBoxText(Window.Handle, Id, buffer, size));
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetEditBoxText(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    private void EnsureTextCallback()
    {
        if (_textCallback is not null)
        {
            return;
        }

        _textCallback = (elementId, utf8, len) =>
        {
            if (elementId == Id)
            {
                _textChanged?.Invoke(this, new EmojiTextChangedEventArgs(NativeUtf8.FromPointer(utf8, len)));
            }
        };
        NativeMethods.EU_SetEditBoxTextCallback(Window.Handle, Id, _textCallback);
    }
}

public sealed class EmojiTable : EmojiElement
{
    private TableCellCallback? _cellClickCallback;
    private TableCellCallback? _cellActionCallback;
    private TableCellEditCallback? _cellEditCallback;
    private event EventHandler<EmojiTableCellEventArgs>? _cellClicked;
    private event EventHandler<EmojiTableCellEventArgs>? _cellAction;
    private event EventHandler<EmojiTableCellEditEventArgs>? _cellEdit;

    internal EmojiTable(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiTableCellEventArgs>? CellClicked
    {
        add
        {
            _cellClicked += value;
            EnsureCellClickCallback();
        }
        remove => _cellClicked -= value;
    }

    public event EventHandler<EmojiTableCellEventArgs>? CellAction
    {
        add
        {
            _cellAction += value;
            EnsureCellActionCallback();
        }
        remove => _cellAction -= value;
    }

    public event EventHandler<EmojiTableCellEditEventArgs>? CellEdit
    {
        add
        {
            _cellEdit += value;
            EnsureCellEditCallback();
        }
        remove => _cellEdit -= value;
    }

    public bool Striped
    {
        get => GetOptions().Striped;
        set => NativeMethods.EU_SetTableStriped(Window.Handle, Id, value ? 1 : 0);
    }

    public bool Bordered
    {
        get => GetOptions().Bordered;
        set => NativeMethods.EU_SetTableBordered(Window.Handle, Id, value ? 1 : 0);
    }

    public int SelectedRow
    {
        get => NativeMethods.EU_GetTableSelectedRow(Window.Handle, Id);
        set => NativeMethods.EU_SetTableSelectedRow(Window.Handle, Id, value);
    }

    public int RowCount => NativeMethods.EU_GetTableRowCount(Window.Handle, Id);

    public int ColumnCount => NativeMethods.EU_GetTableColumnCount(Window.Handle, Id);

    public string FullState => NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetTableFullState(Window.Handle, Id, buffer, size), 512);

    public bool DoubleClickEdit
    {
        get => GetDoubleClickEditState().Enabled;
        set => NativeMethods.EU_SetTableDoubleClickEdit(Window.Handle, Id, value ? 1 : 0);
    }

    public void SetData(string columns, string rows)
    {
        var columnBytes = NativeUtf8.GetBytes(columns);
        var rowBytes = NativeUtf8.GetBytes(rows);
        NativeMethods.EU_SetTableData(Window.Handle, Id, columnBytes, columnBytes.Length, rowBytes, rowBytes.Length);
    }

    public void SetColumns(string columns)
    {
        var bytes = NativeUtf8.GetBytes(columns);
        NativeMethods.EU_SetTableColumnsEx(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetRows(string rows)
    {
        var bytes = NativeUtf8.GetBytes(rows);
        NativeMethods.EU_SetTableRowsEx(Window.Handle, Id, bytes, bytes.Length);
    }

    public int AddRow(string row)
    {
        var bytes = NativeUtf8.GetBytes(row);
        return NativeMethods.EU_AddTableRow(Window.Handle, Id, bytes, bytes.Length);
    }

    public int InsertRow(int rowIndex, string row)
    {
        var bytes = NativeUtf8.GetBytes(row);
        return NativeMethods.EU_InsertTableRow(Window.Handle, Id, rowIndex, bytes, bytes.Length);
    }

    public int DeleteRow(int rowIndex)
    {
        return NativeMethods.EU_DeleteTableRow(Window.Handle, Id, rowIndex);
    }

    public int ClearRows()
    {
        return NativeMethods.EU_ClearTableRows(Window.Handle, Id);
    }

    public void SetEmptyText(string text)
    {
        var bytes = NativeUtf8.GetBytes(text);
        NativeMethods.EU_SetTableEmptyText(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetOptions(bool striped, bool bordered, int rowHeight, int headerHeight, bool selectable)
    {
        NativeMethods.EU_SetTableOptions(Window.Handle, Id, striped ? 1 : 0, bordered ? 1 : 0, rowHeight, headerHeight, selectable ? 1 : 0);
    }

    public EmojiTableOptions GetOptions()
    {
        using var values = IntBuffer.Create(9);
        var ok = NativeMethods.EU_GetTableOptions(
            Window.Handle,
            Id,
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[5],
            values[6],
            values[7],
            values[8]);
        if (ok == 0)
        {
            return new EmojiTableOptions();
        }

        return new EmojiTableOptions
        {
            Striped = values.Read(0) != 0,
            Bordered = values.Read(1) != 0,
            RowHeight = values.Read(2),
            HeaderHeight = values.Read(3),
            Selectable = values.Read(4) != 0,
            SortColumn = values.Read(5),
            SortDescending = values.Read(6) != 0,
            ScrollRow = values.Read(7),
            ColumnWidth = values.Read(8),
        };
    }

    public void SetSort(int columnIndex, bool descending)
    {
        NativeMethods.EU_SetTableSort(Window.Handle, Id, columnIndex, descending ? 1 : 0);
    }

    public void SetScrollRow(int scrollRow)
    {
        NativeMethods.EU_SetTableScrollRow(Window.Handle, Id, scrollRow);
    }

    public void SetColumnWidth(int columnWidth)
    {
        NativeMethods.EU_SetTableColumnWidth(Window.Handle, Id, columnWidth);
    }

    public void SetCell(int row, int column, int type, string value, string options = "")
    {
        var valueBytes = NativeUtf8.GetBytes(value);
        var optionBytes = NativeUtf8.GetBytes(options);
        NativeMethods.EU_SetTableCellEx(Window.Handle, Id, row, column, type, valueBytes, valueBytes.Length, optionBytes, optionBytes.Length);
    }

    public string GetCellValue(int row, int column)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetTableCellValue(Window.Handle, Id, row, column, buffer, size));
    }

    public void SetColumnDoubleClickEdit(int column, int editable)
    {
        NativeMethods.EU_SetTableColumnDoubleClickEdit(Window.Handle, Id, column, editable);
    }

    public void SetCellDoubleClickEdit(int row, int column, int editable)
    {
        NativeMethods.EU_SetTableCellDoubleClickEdit(Window.Handle, Id, row, column, editable);
    }

    public bool GetCellDoubleClickEditable(int row, int column)
    {
        return NativeMethods.EU_GetTableCellDoubleClickEditable(Window.Handle, Id, row, column) != 0;
    }

    public EmojiTableEditState GetDoubleClickEditState()
    {
        using var values = IntBuffer.Create(3);
        var ok = NativeMethods.EU_GetTableDoubleClickEditState(Window.Handle, Id, values[0], values[1], values[2]);
        if (ok == 0)
        {
            return new EmojiTableEditState { EditingRow = -1, EditingColumn = -1 };
        }

        return new EmojiTableEditState
        {
            Enabled = values.Read(0) != 0,
            EditingRow = values.Read(1),
            EditingColumn = values.Read(2),
        };
    }

    public void SetSelectedRows(string rows)
    {
        var bytes = NativeUtf8.GetBytes(rows);
        NativeMethods.EU_SetTableSelectedRows(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetFilter(int column, string value)
    {
        var bytes = NativeUtf8.GetBytes(value);
        NativeMethods.EU_SetTableFilter(Window.Handle, Id, column, bytes, bytes.Length);
    }

    public void ClearFilter(int column)
    {
        NativeMethods.EU_ClearTableFilter(Window.Handle, Id, column);
    }

    public void SetSearch(string value)
    {
        var bytes = NativeUtf8.GetBytes(value);
        NativeMethods.EU_SetTableSearch(Window.Handle, Id, bytes, bytes.Length);
    }

    private void EnsureCellClickCallback()
    {
        if (_cellClickCallback is not null)
        {
            return;
        }

        _cellClickCallback = (tableId, row, column, action, value) =>
        {
            if (tableId == Id)
            {
                _cellClicked?.Invoke(this, new EmojiTableCellEventArgs(row, column, action, value));
            }
        };
        NativeMethods.EU_SetTableCellClickCallback(Window.Handle, Id, _cellClickCallback);
    }

    private void EnsureCellActionCallback()
    {
        if (_cellActionCallback is not null)
        {
            return;
        }

        _cellActionCallback = (tableId, row, column, action, value) =>
        {
            if (tableId == Id)
            {
                _cellAction?.Invoke(this, new EmojiTableCellEventArgs(row, column, action, value));
            }
        };
        NativeMethods.EU_SetTableCellActionCallback(Window.Handle, Id, _cellActionCallback);
    }

    private void EnsureCellEditCallback()
    {
        if (_cellEditCallback is not null)
        {
            return;
        }

        _cellEditCallback = (tableId, row, column, action, utf8, len) =>
        {
            if (tableId == Id)
            {
                _cellEdit?.Invoke(this, new EmojiTableCellEditEventArgs(row, column, action, NativeUtf8.FromPointer(utf8, len)));
            }
        };
        NativeMethods.EU_SetTableCellEditCallback(Window.Handle, Id, _cellEditCallback);
    }
}

public sealed class EmojiTabs : EmojiElement
{
    private ElementValueCallback? _changeCallback;
    private ElementValueCallback? _closeCallback;
    private ElementValueCallback? _addCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _changed;
    private event EventHandler<EmojiValueChangedEventArgs>? _closed;
    private event EventHandler<EmojiValueChangedEventArgs>? _added;

    internal EmojiTabs(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? Changed
    {
        add
        {
            _changed += value;
            EnsureChangeCallback();
        }
        remove => _changed -= value;
    }

    public event EventHandler<EmojiValueChangedEventArgs>? Closed
    {
        add
        {
            _closed += value;
            EnsureCloseCallback();
        }
        remove => _closed -= value;
    }

    public event EventHandler<EmojiValueChangedEventArgs>? Added
    {
        add
        {
            _added += value;
            EnsureAddCallback();
        }
        remove => _added -= value;
    }

    public int ActiveIndex
    {
        get => NativeMethods.EU_GetTabsActive(Window.Handle, Id);
        set => NativeMethods.EU_SetTabsActive(Window.Handle, Id, value);
    }

    public string ActiveName
    {
        get => NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetTabsActiveName(Window.Handle, Id, buffer, size));
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetTabsActiveName(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public int ItemCount => NativeMethods.EU_GetTabsItemCount(Window.Handle, Id);

    public int HeaderAlign
    {
        get => NativeMethods.EU_GetTabsHeaderAlign(Window.Handle, Id);
        set => NativeMethods.EU_SetTabsHeaderAlign(Window.Handle, Id, value);
    }

    public EmojiTabsState State
    {
        get
        {
            using var values = IntBuffer.Create(3);
            var ok = NativeMethods.EU_GetTabsState(Window.Handle, Id, values[0], values[1], values[2]);
            if (ok == 0)
            {
                return new EmojiTabsState();
            }

            return new EmojiTabsState
            {
                ActiveIndex = values.Read(0),
                ItemCount = values.Read(1),
                TabType = values.Read(2),
            };
        }
    }

    public void SetItems(string items)
    {
        var bytes = NativeUtf8.GetBytes(items);
        NativeMethods.EU_SetTabsItems(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetItems(params string[] items)
    {
        SetItems(string.Join("\n", items ?? Array.Empty<string>()));
    }

    public void SetItemsEx(string items)
    {
        var bytes = NativeUtf8.GetBytes(items);
        NativeMethods.EU_SetTabsItemsEx(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetTabType(int tabType)
    {
        NativeMethods.EU_SetTabsType(Window.Handle, Id, tabType);
    }

    public void SetPosition(int tabPosition)
    {
        NativeMethods.EU_SetTabsPosition(Window.Handle, Id, tabPosition);
    }

    public void SetOptions(int tabType, bool closable, bool addable)
    {
        NativeMethods.EU_SetTabsOptions(Window.Handle, Id, tabType, closable ? 1 : 0, addable ? 1 : 0);
    }

    public void SetEditable(bool editable)
    {
        NativeMethods.EU_SetTabsEditable(Window.Handle, Id, editable ? 1 : 0);
    }

    public void SetContentVisible(bool visible)
    {
        NativeMethods.EU_SetTabsContentVisible(Window.Handle, Id, visible ? 1 : 0);
    }

    public void AddItem(string text)
    {
        var bytes = NativeUtf8.GetBytes(text);
        NativeMethods.EU_AddTabsItem(Window.Handle, Id, bytes, bytes.Length);
    }

    public void CloseItem(int itemIndex)
    {
        NativeMethods.EU_CloseTabsItem(Window.Handle, Id, itemIndex);
    }

    public string GetItem(int itemIndex)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetTabsItem(Window.Handle, Id, itemIndex, buffer, size));
    }

    public string GetItemContent(int itemIndex)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetTabsItemContent(Window.Handle, Id, itemIndex, buffer, size));
    }

    private void EnsureChangeCallback()
    {
        if (_changeCallback is not null)
        {
            return;
        }

        _changeCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _changed?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetTabsChangeCallback(Window.Handle, Id, _changeCallback);
    }

    private void EnsureCloseCallback()
    {
        if (_closeCallback is not null)
        {
            return;
        }

        _closeCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _closed?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetTabsCloseCallback(Window.Handle, Id, _closeCallback);
    }

    private void EnsureAddCallback()
    {
        if (_addCallback is not null)
        {
            return;
        }

        _addCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _added?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetTabsAddCallback(Window.Handle, Id, _addCallback);
    }
}

public sealed class EmojiDialog : EmojiElement
{
    private ElementValueCallback? _buttonCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _buttonClicked;

    internal EmojiDialog(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? ButtonClicked
    {
        add
        {
            _buttonClicked += value;
            EnsureButtonCallback();
        }
        remove => _buttonClicked -= value;
    }

    public bool Open
    {
        get => NativeMethods.EU_GetDialogOpen(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetDialogOpen(Window.Handle, Id, value ? 1 : 0);
    }

    public string Title
    {
        get => GetText(0);
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetDialogTitle(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public string Body
    {
        get => GetText(1);
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetDialogBody(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public EmojiDialogOptions Options
    {
        get
        {
            using var values = IntBuffer.Create(7);
            var ok = NativeMethods.EU_GetDialogOptions(Window.Handle, Id, values[0], values[1], values[2], values[3], values[4], values[5], values[6]);
            if (ok == 0)
            {
                return new EmojiDialogOptions();
            }

            return new EmojiDialogOptions
            {
                Open = values.Read(0) != 0,
                Modal = values.Read(1) != 0,
                Closable = values.Read(2) != 0,
                CloseOnMask = values.Read(3) != 0,
                Draggable = values.Read(4) != 0,
                Width = values.Read(5),
                Height = values.Read(6),
            };
        }
    }

    public string GetText(int textKind)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetDialogText(Window.Handle, Id, textKind, buffer, size));
    }

    public void SetOptions(bool open, bool modal, bool closable, bool closeOnMask, bool draggable, int width, int height)
    {
        NativeMethods.EU_SetDialogOptions(Window.Handle, Id, open ? 1 : 0, modal ? 1 : 0, closable ? 1 : 0, closeOnMask ? 1 : 0, draggable ? 1 : 0, width, height);
    }

    public void SetButtons(params string[] buttons)
    {
        SetButtons(string.Join("|", buttons ?? Array.Empty<string>()));
    }

    public void SetButtons(string buttons)
    {
        var bytes = NativeUtf8.GetBytes(buttons);
        NativeMethods.EU_SetDialogButtons(Window.Handle, Id, bytes, bytes.Length);
    }

    public void TriggerButton(int buttonIndex)
    {
        NativeMethods.EU_TriggerDialogButton(Window.Handle, Id, buttonIndex);
    }

    public string GetButtonText(int buttonIndex)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetDialogButtonText(Window.Handle, Id, buttonIndex, buffer, size));
    }

    public int ContentParentId => NativeMethods.EU_GetDialogContentParent(Window.Handle, Id);

    public int FooterParentId => NativeMethods.EU_GetDialogFooterParent(Window.Handle, Id);

    public void SetAdvancedOptions(int widthMode, int widthValue, bool center, bool footerCenter, int contentPadding, int footerHeight)
    {
        NativeMethods.EU_SetDialogAdvancedOptions(Window.Handle, Id, widthMode, widthValue, center ? 1 : 0, footerCenter ? 1 : 0, contentPadding, footerHeight);
    }

    private void EnsureButtonCallback()
    {
        if (_buttonCallback is not null)
        {
            return;
        }

        _buttonCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _buttonClicked?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetDialogButtonCallback(Window.Handle, Id, _buttonCallback);
    }
}

public sealed class EmojiCard : EmojiElement
{
    internal EmojiCard(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public string Title
    {
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetCardTitle(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public string Body
    {
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetCardBody(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public string Footer
    {
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetCardFooter(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public bool Shadow
    {
        set => NativeMethods.EU_SetCardShadow(Window.Handle, Id, value ? 1 : 0);
    }

    public int ItemCount => NativeMethods.EU_GetCardItemCount(Window.Handle, Id);

    public int LastAction => NativeMethods.EU_GetCardAction(Window.Handle, Id);

    public EmojiCardOptions Options
    {
        get
        {
            using var values = IntBuffer.Create(3);
            var ok = NativeMethods.EU_GetCardOptions(Window.Handle, Id, values[0], values[1], values[2]);
            if (ok == 0)
            {
                return new EmojiCardOptions();
            }

            return new EmojiCardOptions
            {
                Shadow = values.Read(0) != 0,
                Hoverable = values.Read(1) != 0,
                ActionCount = values.Read(2),
            };
        }
    }

    public void SetItems(string items)
    {
        var bytes = NativeUtf8.GetBytes(items);
        NativeMethods.EU_SetCardItems(Window.Handle, Id, bytes, bytes.Length);
    }

    public void SetActions(string actions)
    {
        var bytes = NativeUtf8.GetBytes(actions);
        NativeMethods.EU_SetCardActions(Window.Handle, Id, bytes, bytes.Length);
    }

    public void ResetAction()
    {
        NativeMethods.EU_ResetCardAction(Window.Handle, Id);
    }

    public void SetOptions(bool shadow, bool hoverable)
    {
        NativeMethods.EU_SetCardOptions(Window.Handle, Id, shadow ? 1 : 0, hoverable ? 1 : 0);
    }

    public void SetStyle(uint background, uint border, float borderWidth, float radius, int padding)
    {
        NativeMethods.EU_SetCardStyle(Window.Handle, Id, background, border, borderWidth, radius, padding);
    }

    public void SetBodyStyle(int padLeft, int padTop, int padRight, int padBottom, float fontSize, int itemGap, int itemPaddingY, bool divider)
    {
        NativeMethods.EU_SetCardBodyStyle(Window.Handle, Id, padLeft, padTop, padRight, padBottom, fontSize, itemGap, itemPaddingY, divider ? 1 : 0);
    }
}

public sealed class EmojiDrawer : EmojiElement
{
    private ElementValueCallback? _closeCallback;
    private ElementBeforeCloseCallback? _beforeCloseCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _closed;
    private Func<int, bool>? _beforeClose;

    internal EmojiDrawer(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? Closed
    {
        add
        {
            _closed += value;
            EnsureCloseCallback();
        }
        remove => _closed -= value;
    }

    public Func<int, bool>? BeforeClose
    {
        get => _beforeClose;
        set
        {
            _beforeClose = value;
            EnsureBeforeCloseCallback();
        }
    }

    public bool Open
    {
        get => NativeMethods.EU_GetDrawerOpen(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetDrawerOpen(Window.Handle, Id, value ? 1 : 0);
    }

    public string Title
    {
        get => GetText(0);
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetDrawerTitle(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public string Body
    {
        get => GetText(1);
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetDrawerBody(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public EmojiDrawerOptions Options
    {
        get
        {
            using var values = IntBuffer.Create(6);
            var ok = NativeMethods.EU_GetDrawerOptions(Window.Handle, Id, values[0], values[1], values[2], values[3], values[4], values[5]);
            if (ok == 0)
            {
                return new EmojiDrawerOptions();
            }

            return new EmojiDrawerOptions
            {
                Placement = values.Read(0),
                Open = values.Read(1) != 0,
                Modal = values.Read(2) != 0,
                Closable = values.Read(3) != 0,
                CloseOnMask = values.Read(4) != 0,
                Size = values.Read(5),
            };
        }
    }

    public EmojiDrawerAdvancedOptions AdvancedOptions
    {
        get
        {
            using var values = IntBuffer.Create(10);
            var ok = NativeMethods.EU_GetDrawerAdvancedOptions(
                Window.Handle,
                Id,
                values[0],
                values[1],
                values[2],
                values[3],
                values[4],
                values[5],
                values[6],
                values[7],
                values[8],
                values[9]);
            if (ok == 0)
            {
                return new EmojiDrawerAdvancedOptions();
            }

            return new EmojiDrawerAdvancedOptions
            {
                ShowHeader = values.Read(0) != 0,
                ShowClose = values.Read(1) != 0,
                CloseOnEscape = values.Read(2) != 0,
                ContentPadding = values.Read(3),
                FooterHeight = values.Read(4),
                SizeMode = values.Read(5),
                SizeValue = values.Read(6),
                ContentParentId = values.Read(7),
                FooterParentId = values.Read(8),
                ClosePending = values.Read(9) != 0,
            };
        }
    }

    public int ContentParentId => NativeMethods.EU_GetDrawerContentParent(Window.Handle, Id);

    public int FooterParentId => NativeMethods.EU_GetDrawerFooterParent(Window.Handle, Id);

    public string GetText(int textKind)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetDrawerText(Window.Handle, Id, textKind, buffer, size));
    }

    public void SetPlacement(int placement)
    {
        NativeMethods.EU_SetDrawerPlacement(Window.Handle, Id, placement);
    }

    public void SetOptions(int placement, bool open, bool modal, bool closable, bool closeOnMask, int size)
    {
        NativeMethods.EU_SetDrawerOptions(Window.Handle, Id, placement, open ? 1 : 0, modal ? 1 : 0, closable ? 1 : 0, closeOnMask ? 1 : 0, size);
    }

    public void SetAdvancedOptions(bool showHeader, bool showClose, bool closeOnEscape, int contentPadding, int footerHeight, int sizeMode, int sizeValue)
    {
        NativeMethods.EU_SetDrawerAdvancedOptions(Window.Handle, Id, showHeader ? 1 : 0, showClose ? 1 : 0, closeOnEscape ? 1 : 0, contentPadding, footerHeight, sizeMode, sizeValue);
    }

    public void SetAnimation(int durationMs)
    {
        NativeMethods.EU_SetDrawerAnimation(Window.Handle, Id, durationMs);
    }

    public void TriggerClose()
    {
        NativeMethods.EU_TriggerDrawerClose(Window.Handle, Id);
    }

    public void ConfirmClose(bool allow)
    {
        NativeMethods.EU_ConfirmDrawerClose(Window.Handle, Id, allow ? 1 : 0);
    }

    private void EnsureCloseCallback()
    {
        if (_closeCallback is not null)
        {
            return;
        }

        _closeCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _closed?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetDrawerCloseCallback(Window.Handle, Id, _closeCallback);
    }

    private void EnsureBeforeCloseCallback()
    {
        if (_beforeCloseCallback is not null)
        {
            return;
        }

        _beforeCloseCallback = (elementId, action) =>
        {
            if (elementId != Id)
            {
                return 1;
            }

            return _beforeClose?.Invoke(action) == false ? 0 : 1;
        };
        NativeMethods.EU_SetDrawerBeforeCloseCallback(Window.Handle, Id, _beforeCloseCallback);
    }
}

public sealed class EmojiNotification : EmojiElement
{
    private ElementValueCallback? _closeCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _closed;

    internal EmojiNotification(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? Closed
    {
        add
        {
            _closed += value;
            EnsureCloseCallback();
        }
        remove => _closed -= value;
    }

    public string Title => GetText(0);

    public string Body
    {
        get => GetText(1);
        set
        {
            var bytes = NativeUtf8.GetBytes(value);
            NativeMethods.EU_SetNotificationBody(Window.Handle, Id, bytes, bytes.Length);
        }
    }

    public int Type
    {
        get => Options.Type;
        set => NativeMethods.EU_SetNotificationType(Window.Handle, Id, value);
    }

    public bool Closable
    {
        get => Options.Closable;
        set => NativeMethods.EU_SetNotificationClosable(Window.Handle, Id, value ? 1 : 0);
    }

    public bool ClosedState
    {
        get => NativeMethods.EU_GetNotificationClosed(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetNotificationClosed(Window.Handle, Id, value ? 1 : 0);
    }

    public EmojiNotificationOptions Options
    {
        get
        {
            using var values = IntBuffer.Create(4);
            var ok = NativeMethods.EU_GetNotificationOptions(Window.Handle, Id, values[0], values[1], values[2], values[3]);
            if (ok == 0)
            {
                return new EmojiNotificationOptions();
            }

            return new EmojiNotificationOptions
            {
                Type = values.Read(0),
                Closable = values.Read(1) != 0,
                DurationMs = values.Read(2),
                Closed = values.Read(3) != 0,
            };
        }
    }

    public EmojiNotificationState State
    {
        get
        {
            using var values = IntBuffer.Create(15);
            var ok = NativeMethods.EU_GetNotificationFullStateEx(
                Window.Handle,
                Id,
                values[0],
                values[1],
                values[2],
                values[3],
                values[4],
                values[5],
                values[6],
                values[7],
                values[8],
                values[9],
                values[10],
                values[11],
                values[12],
                values[13],
                values[14]);
            if (ok == 0)
            {
                return new EmojiNotificationState();
            }

            return new EmojiNotificationState
            {
                Type = values.Read(0),
                Closable = values.Read(1) != 0,
                DurationMs = values.Read(2),
                Closed = values.Read(3) != 0,
                CloseHover = values.Read(4),
                CloseDown = values.Read(5),
                CloseCount = values.Read(6),
                LastAction = values.Read(7),
                TimerElapsedMs = values.Read(8),
                TimerRunning = values.Read(9) != 0,
                StackIndex = values.Read(10),
                StackGap = values.Read(11),
                Placement = values.Read(12),
                Offset = values.Read(13),
                Rich = values.Read(14) != 0,
            };
        }
    }

    public string GetText(int textKind)
    {
        return NativeUtf8.FromBuffer((buffer, size) => NativeMethods.EU_GetNotificationText(Window.Handle, Id, textKind, buffer, size));
    }

    public void SetPlacement(int placement, int offset)
    {
        NativeMethods.EU_SetNotificationPlacement(Window.Handle, Id, placement, offset);
    }

    public void SetRichMode(bool rich)
    {
        NativeMethods.EU_SetNotificationRichMode(Window.Handle, Id, rich ? 1 : 0);
    }

    public void SetOptions(EmojiMessageType type, bool closable, int durationMs)
    {
        NativeMethods.EU_SetNotificationOptions(Window.Handle, Id, (int)type, closable ? 1 : 0, durationMs);
    }

    public void SetStack(int stackIndex, int stackGap)
    {
        NativeMethods.EU_SetNotificationStack(Window.Handle, Id, stackIndex, stackGap);
    }

    public void TriggerClose()
    {
        NativeMethods.EU_TriggerNotificationClose(Window.Handle, Id);
    }

    private void EnsureCloseCallback()
    {
        if (_closeCallback is not null)
        {
            return;
        }

        _closeCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _closed?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetNotificationCloseCallback(Window.Handle, Id, _closeCallback);
    }
}

internal sealed class IntBuffer : IDisposable
{
    private readonly IntPtr[] _values;

    private IntBuffer(int count)
    {
        _values = new IntPtr[count];
        for (var i = 0; i < _values.Length; i++)
        {
            _values[i] = Marshal.AllocHGlobal(sizeof(int));
            Marshal.WriteInt32(_values[i], 0);
        }
    }

    public IntPtr this[int index] => _values[index];

    public static IntBuffer Create(int count)
    {
        return new IntBuffer(count);
    }

    public int Read(int index)
    {
        return Marshal.ReadInt32(_values[index]);
    }

    public void Dispose()
    {
        foreach (var value in _values)
        {
            if (value != IntPtr.Zero)
            {
                Marshal.FreeHGlobal(value);
            }
        }
    }
}
