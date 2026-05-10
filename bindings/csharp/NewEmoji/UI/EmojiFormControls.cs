using System;
using NewEmoji.Native;

namespace NewEmoji;

public sealed class EmojiCheckbox : EmojiElement
{
    internal EmojiCheckbox(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public bool Checked
    {
        get => NativeMethods.EU_GetCheckboxChecked(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetCheckboxChecked(Window.Handle, Id, value ? 1 : 0);
    }
}

public sealed class EmojiRadio : EmojiElement
{
    internal EmojiRadio(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public bool Checked
    {
        get => NativeMethods.EU_GetRadioChecked(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetRadioChecked(Window.Handle, Id, value ? 1 : 0);
    }
}

public sealed class EmojiSwitch : EmojiElement
{
    internal EmojiSwitch(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public bool Checked
    {
        get => NativeMethods.EU_GetSwitchChecked(Window.Handle, Id) != 0;
        set => NativeMethods.EU_SetSwitchChecked(Window.Handle, Id, value ? 1 : 0);
    }
}

public sealed class EmojiSlider : EmojiElement
{
    private ElementValueCallback? _valueCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _valueChanged;

    internal EmojiSlider(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? ValueChanged
    {
        add
        {
            _valueChanged += value;
            EnsureValueCallback();
        }
        remove => _valueChanged -= value;
    }

    public int Value
    {
        get => NativeMethods.EU_GetSliderValue(Window.Handle, Id);
        set => NativeMethods.EU_SetSliderValue(Window.Handle, Id, value);
    }

    public void SetRange(int minValue, int maxValue)
    {
        NativeMethods.EU_SetSliderRange(Window.Handle, Id, minValue, maxValue);
    }

    private void EnsureValueCallback()
    {
        if (_valueCallback is not null)
        {
            return;
        }

        _valueCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _valueChanged?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetSliderValueCallback(Window.Handle, Id, _valueCallback);
    }
}

public sealed class EmojiSelect : EmojiElement
{
    private ElementValueCallback? _valueCallback;
    private event EventHandler<EmojiValueChangedEventArgs>? _selectedIndexChanged;

    internal EmojiSelect(EmojiWindow window, int id)
        : base(window, id)
    {
    }

    public event EventHandler<EmojiValueChangedEventArgs>? SelectedIndexChanged
    {
        add
        {
            _selectedIndexChanged += value;
            EnsureValueCallback();
        }
        remove => _selectedIndexChanged -= value;
    }

    public int SelectedIndex
    {
        get => NativeMethods.EU_GetSelectIndex(Window.Handle, Id);
        set => NativeMethods.EU_SetSelectIndex(Window.Handle, Id, value);
    }

    private void EnsureValueCallback()
    {
        if (_valueCallback is not null)
        {
            return;
        }

        _valueCallback = (elementId, value, rangeStart, rangeEnd) =>
        {
            if (elementId == Id)
            {
                _selectedIndexChanged?.Invoke(this, new EmojiValueChangedEventArgs(value, rangeStart, rangeEnd));
            }
        };
        NativeMethods.EU_SetSelectChangeCallback(Window.Handle, Id, _valueCallback);
    }
}
