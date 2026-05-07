# IconButton 工具栏图标按钮

`IconButton` 用于 Chrome 顶部工具栏的纯图标按钮。默认背景可完全透明，hover、press、checked 时显示半透明圆形、圆角矩形或胶囊背景。

## 创建

```text
EU_CreateIconButton(hwnd, parent_id, icon_bytes, icon_len, tooltip_bytes, tooltip_len, x, y, w, h)
```

图标参数优先使用 emoji / Unicode 文本，例如 `←`、`↻`、`📥`、`⋮`。

## API

```text
EU_SetIconButtonIcon
EU_SetIconButtonTooltip
EU_SetIconButtonBadge
EU_SetIconButtonChecked
EU_GetIconButtonChecked
EU_SetIconButtonDropdown
EU_SetIconButtonColors
EU_SetIconButtonShape
EU_SetIconButtonPadding
EU_SetIconButtonIconSize
EU_GetIconButtonState
```

`normal_bg = 0x00000000` 表示透明默认态。`shape`：`0=圆角矩形`，`1=圆形`，`2=胶囊`。

## Dropdown / Popup

`EU_SetIconButtonDropdown(hwnd, button_id, popup_id)` 可绑定 `Popover`、`Menu` 或 `Dropdown`。绑定后点击 `IconButton` 会自动切换 popup 打开状态；打开当前按钮 popup 时，同窗口内其他已打开 popup 会自动关闭。点击打开 popup 后，该按钮 tooltip 会暂停显示，直到鼠标离开按钮后恢复。

建议配合通用 Popup API 使用：

```text
EU_SetPopupAnchorElement
EU_SetPopupPlacement
EU_SetPopupOpen / EU_GetPopupOpen
EU_SetPopupDismissBehavior
```

内部兼容通用 `EU_SetElementPopup(hwnd, button_id, popup_id, 0)` 机制，因此工具栏按钮左键弹层和普通组件右键弹层共享同一套打开/关闭规则。
