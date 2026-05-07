# Omnibox 地址栏

`Omnibox` 是 Chrome 外壳专用地址栏组件，包含安全状态、搜索/网址输入、前缀 chip、右侧动作图标和建议列表。

## 创建

```text
EU_CreateOmnibox(hwnd, parent_id, value_bytes, value_len, placeholder_bytes, placeholder_len, x, y, w, h)
```

## API

```text
EU_SetOmniboxValue
EU_GetOmniboxValue
EU_SetOmniboxPlaceholder
EU_SetOmniboxSecurityState
EU_SetOmniboxPrefixChip
EU_SetOmniboxActionIcons
EU_SetOmniboxSuggestionItems
EU_SetOmniboxSuggestionOpen
EU_SetOmniboxSuggestionSelected
EU_GetOmniboxSuggestionState
EU_SetOmniboxCommitCallback
EU_SetOmniboxIconButtonCallback
```

`security_state`：`0=普通`，`1=安全`，`2=不安全`，`3=警告`，`4=本地文件`，`5=搜索`。

建议项协议：每行一项，字段使用 Tab 分隔：`类型<TAB>图标<TAB>主文本<TAB>副文本<TAB>补全文本`。
