# API 索引

本索引从 `src/new_emoji.def` 生成，用于快速确认当前 DLL 导出名称。说明列可逐步补充，组件级说明请查看 [组件文档](components/README.md)。

| 导出 | 说明 |
|---|---|
| `EU_CreateWindow` | |
| `EU_CreateWindowDark` | |
| `EU_DestroyWindow` | |
| `EU_ShowWindow` | |
| `EU_RunMessageLoop` | 运行 Win32 消息循环，适用于无宿主窗体的 DLL 窗口程序 |
| `EU_SetWindowTitle` | |
| `EU_SetWindowBounds` | |
| `EU_GetWindowBounds` | |
| `EU_CreatePanel` | |
| `EU_CreateButton` | |
| `EU_CreateEditBox` | 保留兼容的底层编辑内核；新表单输入推荐 `EU_CreateInput` |
| `EU_CreateInfoBox` | |
| `EU_CreateText` | |
| `EU_CreateLink` | |
| `EU_CreateIcon` | |
| `EU_CreateSpace` | |
| `EU_CreateContainer` | 创建 Container 容器；默认兼容旧绝对定位，流式布局通过 `EU_SetContainerLayout` 开启 |
| `EU_CreateHeader` | 创建 Container 顶栏区域 |
| `EU_CreateAside` | 创建 Container 侧边栏区域 |
| `EU_CreateMain` | 创建 Container 主要区域 |
| `EU_CreateFooter` | 创建 Container 底栏区域 |
| `EU_CreateLayout` | |
| `EU_CreateBorder` | |
| `EU_CreateCheckbox` | 创建独立复选框，支持普通/边框/尺寸样式 |
| `EU_CreateCheckboxGroup` | 创建原生复选框组，支持普通/按钮/边框样式、min/max |
| `EU_CreateRadio` | |
| `EU_CreateRadioGroup` | 创建原生单选组，支持普通/按钮/边框样式 |
| `EU_CreateSwitch` | |
| `EU_CreateSlider` | |
| `EU_CreateInputNumber` | |
| `EU_CreateInput` | 创建 Input 输入框 |
| `EU_CreateInputGroup` | 创建 InputGroup 组合输入 |
| `EU_CreateInputTag` | |
| `EU_CreateSelect` | |
| `EU_CreateSelectV2` | |
| `EU_CreateRate` | |
| `EU_CreateColorPicker` | |
| `EU_CreateTag` | |
| `EU_CreateBadge` | 创建徽标，支持数值、文本、dot、角标位置、独立模式和语义类型 |
| `EU_CreateProgress` | |
| `EU_CreateAvatar` | |
| `EU_CreateEmpty` | 创建空状态，支持描述、emoji 图标、图片、尺寸、内置操作按钮和子按钮插槽 |
| `EU_CreateSkeleton` | |
| `EU_CreateDescriptions` | |
| `EU_CreateTable` | 创建表格；兼容旧基础表格协议，高级能力通过 `EU_SetTableColumnsEx` / `EU_SetTableRowsEx` 补齐 |
| `EU_CreateCard` | 创建 Card 卡片，支持标题、正文、阴影和子元素插槽 |
| `EU_CreateCollapse` | 创建 Collapse 折叠面板，支持多展开、手风琴、中文 emoji 标题和旧项目格式 |
| `EU_CreateTimeline` | 创建 Timeline 时间线，支持中文和 emoji 项目 |
| `EU_CreateStatistic` | 创建统计数值组件 |
| `EU_CreateKpiCard` | |
| `EU_CreateTrend` | |
| `EU_CreateStatusDot` | |
| `EU_CreateGauge` | |
| `EU_CreateRingProgress` | |
| `EU_CreateBulletProgress` | |
| `EU_CreateLineChart` | |
| `EU_CreateBarChart` | |
| `EU_CreateDonutChart` | |
| `EU_CreateDivider` | 创建 Divider 分割线，支持横向/纵向与文本位置 |
| `EU_CreateCalendar` | 创建 Calendar 日历，支持基础绑定、可选范围、显示范围、自定义单元格和状态样式 |
| `EU_CreateTree` | |
| `EU_CreateTreeSelect` | |
| `EU_CreateTransfer` | |
| `EU_CreateAutocomplete` | 创建 Autocomplete 自动补全 |
| `EU_CreateMentions` | |
| `EU_CreateCascader` | |
| `EU_CreateDatePicker` | |
| `EU_CreateTimePicker` | |
| `EU_CreateDateTimePicker` | |
| `EU_CreateTimeSelect` | |
| `EU_CreateDropdown` | |
| `EU_CreateMenu` | |
| `EU_CreateAnchor` | |
| `EU_CreateBacktop` | |
| `EU_CreateSegmented` | |
| `EU_CreatePageHeader` | |
| `EU_CreateAffix` | |
| `EU_CreateWatermark` | |
| `EU_CreateTour` | |
| `EU_CreateImage` | |
| `EU_CreateCarousel` | |
| `EU_CreateUpload` | |
| `EU_CreateInfiniteScroll` | |
| `EU_CreateBreadcrumb` | |
| `EU_CreateTabs` | |
| `EU_CreatePagination` | |
| `EU_CreateSteps` | |
| `EU_CreateAlert` | |
| `EU_CreateAlertEx` | 创建高级警告提示，支持图标、居中、描述换行和自定义关闭文字 |
| `EU_CreateResult` | |
| `EU_CreateNotification` | |
| `EU_CreateLoading` | |
| `EU_CreateDialog` | |
| `EU_SetDialogAdvancedOptions` | 设置 Dialog 百分比宽度、居中和 slot 布局 |
| `EU_GetDialogAdvancedOptions` | 读取 Dialog 高级选项、slot ID 和 before-close 待确认状态 |
| `EU_GetDialogContentParent` | 获取 Dialog 内容 slot 容器 ID |
| `EU_GetDialogFooterParent` | 获取 Dialog 页脚 slot 容器 ID |
| `EU_SetDialogBeforeCloseCallback` | 设置 Dialog 关闭前拦截回调 |
| `EU_ConfirmDialogClose` | before-close 拦截后确认继续或取消关闭 |
| `EU_CreateDrawer` | 创建窗口级 Drawer 抽屉 |
| `EU_SetDrawerAdvancedOptions` | 设置 Drawer 标题栏、关闭按钮、ESC、padding、footer 和像素/百分比尺寸 |
| `EU_GetDrawerAdvancedOptions` | 读取 Drawer 高级选项、slot ID 和 before-close pending 状态 |
| `EU_GetDrawerContentParent` | 获取 Drawer 内容 slot 容器 ID |
| `EU_GetDrawerFooterParent` | 获取 Drawer 页脚 slot 容器 ID |
| `EU_SetDrawerBeforeCloseCallback` | 设置 Drawer 关闭前拦截回调 |
| `EU_ConfirmDrawerClose` | before-close 拦截后确认继续或取消关闭 |
| `EU_CreateTooltip` | |
| `EU_SetTooltipAdvancedOptions` | 设置 Tooltip 12 方位、明暗主题、disabled、箭头和 offset |
| `EU_GetTooltipAdvancedOptions` | 读取 Tooltip 高级选项 |
| `EU_CreatePopover` | |
| `EU_SetPopoverAdvancedOptions` | 设置 Popover 12 方位和弹层尺寸 |
| `EU_SetPopoverBehavior` | 设置 Popover hover/click/focus/manual 行为 |
| `EU_GetPopoverBehavior` | 读取 Popover 行为选项 |
| `EU_GetPopoverContentParent` | 获取 Popover 内容 slot 容器 ID |
| `EU_CreatePopconfirm` | |
| `EU_SetPopconfirmAdvancedOptions` | 设置 Popconfirm 12 方位、触发、外部关闭、箭头和 offset |
| `EU_SetPopconfirmIcon` | 设置 Popconfirm 图标文本/emoji、颜色和显示状态 |
| `EU_GetPopconfirmIcon` | 读取 Popconfirm 图标文本/emoji、颜色和显示状态 |
| `EU_ShowMessage` | 显示服务式 Message 消息提示 |
| `EU_ShowNotification` | 显示服务式 Notification 通知 |
| `EU_ShowMessageBox` | |
| `EU_ShowConfirmBox` | |
| `EU_ShowMessageBoxEx` | 显示扩展 MessageBox |
| `EU_ShowPromptBox` | 显示 Prompt 输入消息框 |
| `EU_SetElementText` | |
| `EU_GetElementText` | |
| `EU_SetElementBounds` | |
| `EU_GetElementBounds` | |
| `EU_SetElementVisible` | |
| `EU_GetElementVisible` | |
| `EU_SetElementEnabled` | |
| `EU_GetElementEnabled` | |
| `EU_SetElementColor` | |
| `EU_SetElementFont` | |
| `EU_SetTextOptions` | |
| `EU_GetTextOptions` | |
| `EU_SetLinkOptions` | |
| `EU_GetLinkOptions` | |
| `EU_SetLinkContent` | |
| `EU_GetLinkContent` | |
| `EU_SetLinkVisited` | |
| `EU_GetLinkVisited` | |
| `EU_SetIconOptions` | |
| `EU_GetIconOptions` | |
| `EU_SetPanelStyle` | |
| `EU_GetPanelStyle` | |
| `EU_SetPanelLayout` | |
| `EU_GetPanelLayout` | |
| `EU_SetContainerLayout` | 设置 Container 流式布局：0自动、1横向、2纵向 |
| `EU_GetContainerLayout` | 读取 Container 流式布局、间距和实际方向 |
| `EU_SetContainerRegionTextOptions` | 设置 Header/Aside/Main/Footer 区域文本对齐 |
| `EU_GetContainerRegionTextOptions` | 读取 Header/Aside/Main/Footer 区域文本对齐和角色 |
| `EU_SetLayoutOptions` | |
| `EU_GetLayoutOptions` | |
| `EU_SetLayoutChildWeight` | |
| `EU_GetLayoutChildWeight` | |
| `EU_SetBorderOptions` | |
| `EU_GetBorderOptions` | |
| `EU_SetBorderDashed` | |
| `EU_GetBorderDashed` | |
| `EU_SetInfoBoxText` | |
| `EU_SetInfoBoxOptions` | |
| `EU_SetInfoBoxClosed` | |
| `EU_GetInfoBoxClosed` | |
| `EU_GetInfoBoxPreferredHeight` | |
| `EU_SetSpaceSize` | |
| `EU_GetSpaceSize` | |
| `EU_SetDividerOptions` | 设置 Divider 方向、文本位置、颜色、线宽、兼容虚线和文本 |
| `EU_GetDividerOptions` | 读回 Divider 方向、文本位置、颜色、线宽和兼容虚线状态 |
| `EU_SetDividerSpacing` | 设置 Divider 线条外边距和文本间隙 |
| `EU_GetDividerSpacing` | 读回 Divider 线条外边距和文本间隙 |
| `EU_SetDividerLineStyle` | 设置 Divider 线型：0实线 1虚线 2点线 3双线 |
| `EU_GetDividerLineStyle` | 读回 Divider 线型 |
| `EU_SetDividerContent` | 设置 Divider 图标/emoji 与文本内容 |
| `EU_GetDividerContent` | 读回 Divider 图标/emoji 与文本内容 |
| `EU_SetButtonEmoji` | |
| `EU_SetButtonVariant` | |
| `EU_GetButtonState` | |
| `EU_SetButtonOptions` | |
| `EU_GetButtonOptions` | |
| `EU_SetEditBoxText` | 设置兼容编辑内核文本 |
| `EU_SetEditBoxOptions` | 设置兼容编辑内核只读、密码、多行、焦点色和占位文本 |
| `EU_GetEditBoxOptions` | 读取兼容编辑内核选项 |
| `EU_GetEditBoxState` | 读取兼容编辑内核光标、选区和文本长度 |
| `EU_GetEditBoxText` | 读取兼容编辑内核文本 |
| `EU_SetEditBoxTextCallback` | 设置兼容编辑内核文本变化回调 |
| `EU_SetElementFocus` | |
| `EU_SetCheckboxChecked` | |
| `EU_GetCheckboxChecked` | |
| `EU_SetCheckboxIndeterminate` | |
| `EU_GetCheckboxIndeterminate` | |
| `EU_SetCheckboxOptions` | 设置独立复选框 border/size |
| `EU_GetCheckboxOptions` | 读取独立复选框 border/size |
| `EU_SetCheckboxGroupItems` | 设置原生复选框组项目 |
| `EU_SetCheckboxGroupValue` | 设置原生复选框组选中值列表 |
| `EU_GetCheckboxGroupValue` | 读取原生复选框组选中值列表 |
| `EU_SetCheckboxGroupOptions` | 设置原生复选框组禁用、样式、尺寸和 min/max |
| `EU_GetCheckboxGroupOptions` | 读取原生复选框组禁用、样式、尺寸和 min/max |
| `EU_GetCheckboxGroupState` | 读取原生复选框组完整状态 |
| `EU_SetCheckboxGroupChangeCallback` | 设置原生复选框组变更回调 |
| `EU_SetRadioChecked` | |
| `EU_GetRadioChecked` | |
| `EU_SetRadioGroup` | |
| `EU_GetRadioGroup` | |
| `EU_SetRadioValue` | 设置独立单选框业务值 |
| `EU_GetRadioValue` | 读取独立单选框业务值 |
| `EU_SetRadioOptions` | 设置独立单选框 border/size |
| `EU_GetRadioOptions` | 读取独立单选框 border/size |
| `EU_SetRadioGroupItems` | 设置原生单选组项目 |
| `EU_SetRadioGroupValue` | 设置原生单选组选中值 |
| `EU_GetRadioGroupValue` | 读取原生单选组选中值 |
| `EU_GetRadioGroupSelectedIndex` | 读取原生单选组选中索引 |
| `EU_SetRadioGroupOptions` | 设置原生单选组禁用、样式和尺寸 |
| `EU_GetRadioGroupOptions` | 读取原生单选组禁用、样式和尺寸 |
| `EU_GetRadioGroupState` | 读取原生单选组完整状态 |
| `EU_SetRadioGroupChangeCallback` | 设置原生单选组变更回调 |
| `EU_SetSwitchChecked` | |
| `EU_GetSwitchChecked` | |
| `EU_SetSwitchLoading` | |
| `EU_GetSwitchLoading` | |
| `EU_SetSwitchTexts` | |
| `EU_GetSwitchOptions` | |
| `EU_SetSliderRange` | |
| `EU_SetSliderValue` | |
| `EU_GetSliderValue` | |
| `EU_SetSliderOptions` | |
| `EU_GetSliderStep` | |
| `EU_GetSliderOptions` | |
| `EU_SetSliderRangeValue` | |
| `EU_GetSliderRangeValue` | |
| `EU_SetSliderRangeMode` | |
| `EU_GetSliderRangeMode` | |
| `EU_SetSliderValueCallback` | |
| `EU_SetInputNumberRange` | |
| `EU_SetInputNumberStep` | |
| `EU_SetInputNumberValue` | |
| `EU_GetInputNumberValue` | |
| `EU_GetInputNumberCanStep` | |
| `EU_GetInputNumberOptions` | |
| `EU_SetInputNumberPrecision` | |
| `EU_GetInputNumberPrecision` | |
| `EU_SetInputNumberText` | |
| `EU_GetInputNumberText` | |
| `EU_GetInputNumberState` | |
| `EU_SetInputNumberValueCallback` | |
| `EU_SetInputValue` | |
| `EU_GetInputValue` | |
| `EU_SetInputPlaceholder` | |
| `EU_SetInputAffixes` | |
| `EU_SetInputIcons` | 设置 Input 前后图标 |
| `EU_GetInputIcons` | 读取 Input 前后图标 |
| `EU_SetInputClearable` | |
| `EU_SetInputOptions` | |
| `EU_SetInputVisualOptions` | 设置 Input 尺寸、密码显隐、字数统计与 autosize |
| `EU_GetInputVisualOptions` | 读取 Input 视觉选项 |
| `EU_SetInputSelection` | 设置 Input 文本选区 |
| `EU_GetInputSelection` | 读取 Input 文本选区 |
| `EU_SetInputContextMenuEnabled` | 设置 Input 右键菜单是否启用 |
| `EU_GetInputContextMenuEnabled` | 读取 Input 右键菜单是否启用 |
| `EU_GetInputState` | |
| `EU_SetInputMaxLength` | |
| `EU_GetInputMaxLength` | |
| `EU_SetInputTextCallback` | |
| `EU_SetInputGroupValue` | 设置 InputGroup 内部输入值 |
| `EU_GetInputGroupValue` | 读取 InputGroup 内部输入值 |
| `EU_SetInputGroupOptions` | 设置 InputGroup 尺寸与输入行为选项 |
| `EU_GetInputGroupOptions` | 读取 InputGroup 尺寸与输入行为选项 |
| `EU_SetInputGroupTextAddon` | 设置 InputGroup 文本附加项 |
| `EU_SetInputGroupButtonAddon` | 设置 InputGroup 按钮附加项 |
| `EU_SetInputGroupSelectAddon` | 设置 InputGroup 选择附加项 |
| `EU_ClearInputGroupAddon` | 清空 InputGroup 附加项 |
| `EU_GetInputGroupInputElementId` | 读取 InputGroup 内部 Input 元素 ID |
| `EU_GetInputGroupAddonElementId` | 读取 InputGroup 某侧附加项元素 ID |
| `EU_SetInputTagTags` | |
| `EU_SetInputTagPlaceholder` | |
| `EU_SetInputTagOptions` | |
| `EU_GetInputTagCount` | |
| `EU_GetInputTagOptions` | |
| `EU_AddInputTagItem` | |
| `EU_RemoveInputTagItem` | |
| `EU_SetInputTagInputValue` | |
| `EU_GetInputTagInputValue` | |
| `EU_GetInputTagItem` | |
| `EU_SetInputTagChangeCallback` | |
| `EU_SetSelectOptions` | |
| `EU_SetSelectIndex` | |
| `EU_GetSelectIndex` | |
| `EU_SetSelectOpen` | |
| `EU_GetSelectOpen` | |
| `EU_SetSelectSearch` | |
| `EU_SetSelectOptionDisabled` | |
| `EU_SetSelectOptionAlignment` | |
| `EU_GetSelectOptionAlignment` | |
| `EU_SetSelectValueAlignment` | |
| `EU_GetSelectValueAlignment` | |
| `EU_GetSelectOptionCount` | |
| `EU_GetSelectMatchedCount` | |
| `EU_GetSelectOptionDisabled` | |
| `EU_SetSelectMultiple` | |
| `EU_GetSelectMultiple` | |
| `EU_SetSelectSelectedIndices` | |
| `EU_GetSelectSelectedCount` | |
| `EU_GetSelectSelectedAt` | |
| `EU_SetSelectChangeCallback` | |
| `EU_SetSelectV2Options` | |
| `EU_SetSelectV2Index` | |
| `EU_SetSelectV2VisibleCount` | |
| `EU_GetSelectV2Index` | |
| `EU_GetSelectV2VisibleCount` | |
| `EU_SetSelectV2Open` | |
| `EU_GetSelectV2Open` | |
| `EU_SetSelectV2Search` | |
| `EU_SetSelectV2OptionDisabled` | |
| `EU_SetSelectV2OptionAlignment` | |
| `EU_GetSelectV2OptionAlignment` | |
| `EU_SetSelectV2ValueAlignment` | |
| `EU_GetSelectV2ValueAlignment` | |
| `EU_GetSelectV2OptionCount` | |
| `EU_GetSelectV2MatchedCount` | |
| `EU_GetSelectV2OptionDisabled` | |
| `EU_SetSelectV2ScrollIndex` | |
| `EU_GetSelectV2ScrollIndex` | |
| `EU_SetSelectV2ChangeCallback` | |
| `EU_SetRateValue` | |
| `EU_GetRateValue` | |
| `EU_SetRateMax` | |
| `EU_GetRateMax` | |
| `EU_SetRateValueX2` | |
| `EU_GetRateValueX2` | |
| `EU_SetRateOptions` | |
| `EU_GetRateOptions` | |
| `EU_SetRateTexts` | |
| `EU_SetRateColors` | |
| `EU_GetRateColors` | |
| `EU_SetRateIcons` | |
| `EU_GetRateIcons` | |
| `EU_SetRateTextItems` | |
| `EU_SetRateDisplayOptions` | |
| `EU_GetRateDisplayOptions` | |
| `EU_SetRateChangeCallback` | |
| `EU_SetColorPickerColor` | |
| `EU_GetColorPickerColor` | |
| `EU_SetColorPickerAlpha` | |
| `EU_GetColorPickerAlpha` | |
| `EU_SetColorPickerHex` | |
| `EU_GetColorPickerHex` | |
| `EU_SetColorPickerOpen` | |
| `EU_GetColorPickerOpen` | |
| `EU_SetColorPickerPalette` | |
| `EU_GetColorPickerPaletteCount` | |
| `EU_SetColorPickerOptions` | 设置 ColorPicker 透明度开关、尺寸和可清空状态 |
| `EU_GetColorPickerOptions` | 读取 ColorPicker 透明度开关、尺寸和可清空状态 |
| `EU_ClearColorPicker` | 清空 ColorPicker，进入无默认值/空值态 |
| `EU_GetColorPickerHasValue` | 读取 ColorPicker 是否有当前颜色值 |
| `EU_SetColorPickerChangeCallback` | |
| `EU_SetTagType` | |
| `EU_SetTagEffect` | |
| `EU_SetTagClosable` | |
| `EU_SetTagClosed` | |
| `EU_GetTagClosed` | |
| `EU_GetTagOptions` | |
| `EU_SetTagSize` | |
| `EU_SetTagThemeColor` | |
| `EU_GetTagVisualOptions` | |
| `EU_SetTagCloseCallback` | |
| `EU_SetBadgeValue` | |
| `EU_SetBadgeMax` | |
| `EU_SetBadgeType` | |
| `EU_SetBadgeDot` | |
| `EU_SetBadgeOptions` | |
| `EU_GetBadgeHidden` | |
| `EU_GetBadgeOptions` | |
| `EU_GetBadgeType` | |
| `EU_SetBadgeLayoutOptions` | |
| `EU_GetBadgeLayoutOptions` | |
| `EU_SetProgressPercentage` | |
| `EU_GetProgressPercentage` | |
| `EU_SetProgressStatus` | |
| `EU_GetProgressStatus` | |
| `EU_SetProgressShowText` | |
| `EU_SetProgressOptions` | |
| `EU_GetProgressOptions` | |
| `EU_SetProgressFormatOptions` | |
| `EU_GetProgressFormatOptions` | |
| `EU_SetProgressTextInside` | |
| `EU_GetProgressTextInside` | |
| `EU_SetProgressColors` | |
| `EU_GetProgressColors` | |
| `EU_SetProgressColorStops` | |
| `EU_GetProgressColorStopCount` | |
| `EU_GetProgressColorStop` | |
| `EU_SetProgressCompleteText` | |
| `EU_GetProgressCompleteText` | |
| `EU_SetProgressTextTemplate` | |
| `EU_GetProgressTextTemplate` | |
| `EU_SetAvatarShape` | |
| `EU_SetAvatarSource` | |
| `EU_SetAvatarFallbackSource` | |
| `EU_SetAvatarIcon` | |
| `EU_SetAvatarErrorText` | |
| `EU_SetAvatarFit` | |
| `EU_GetAvatarImageStatus` | |
| `EU_GetAvatarOptions` | |
| `EU_SetEmptyDescription` | 设置空状态描述文字 |
| `EU_SetEmptyOptions` | 设置空状态 emoji 图标和内置操作按钮文字 |
| `EU_SetEmptyActionClicked` | 设置内置操作按钮点击状态 |
| `EU_GetEmptyActionClicked` | 读取内置操作按钮点击状态 |
| `EU_SetEmptyActionCallback` | 设置内置操作按钮回调 |
| `EU_SetEmptyImage` | 设置空状态图片，支持本地路径、HTTP 和 HTTPS |
| `EU_SetEmptyImageSize` | 设置空状态图片尺寸，0 为自适应 |
| `EU_GetEmptyImageStatus` | 读取图片状态：0 默认图标/无图片，1 已加载，2 加载失败，3 加载中 |
| `EU_GetEmptyImageSize` | 读取图片逻辑尺寸 |
| `EU_SetSkeletonRows` | |
| `EU_SetSkeletonAnimated` | |
| `EU_SetSkeletonLoading` | |
| `EU_SetSkeletonOptions` | |
| `EU_GetSkeletonLoading` | |
| `EU_GetSkeletonOptions` | |
| `EU_SetDescriptionsItems` | |
| `EU_SetDescriptionsColumns` | |
| `EU_SetDescriptionsBordered` | |
| `EU_SetDescriptionsLayout` | 设置方向、尺寸、列数和边框 |
| `EU_SetDescriptionsItemsEx` | 设置高级项目：跨列、图标、标签、对齐和逐项颜色 |
| `EU_SetDescriptionsOptions` | |
| `EU_GetDescriptionsItemCount` | |
| `EU_SetDescriptionsAdvancedOptions` | |
| `EU_SetDescriptionsColors` | 设置描述列表全局颜色 |
| `EU_SetDescriptionsExtra` | 设置右上角操作按钮 |
| `EU_GetDescriptionsOptions` | |
| `EU_GetDescriptionsFullState` | 读取方向、尺寸、列数、项目数和操作点击次数 |
| `EU_SetTableData` | 设置旧协议列/行数据 |
| `EU_SetTableStriped` | 设置斑马纹 |
| `EU_SetTableBordered` | 设置边框 |
| `EU_SetTableEmptyText` | 设置空状态文字 |
| `EU_SetTableSelectedRow` | 设置单选高亮行 |
| `EU_GetTableSelectedRow` | 读取当前选中行 |
| `EU_GetTableRowCount` | 读取表格行数 |
| `EU_GetTableColumnCount` | 读取表格列数 |
| `EU_SetTableOptions` | 设置基础表格选项：斑马纹、边框、行高、表头高、可选择 |
| `EU_SetTableSort` | 设置排序列和方向 |
| `EU_SetTableScrollRow` | 设置首个可见行 |
| `EU_SetTableColumnWidth` | 设置统一列宽 |
| `EU_GetTableOptions` | 读取基础表格选项 |
| `EU_SetTableColumnsEx` | 设置高级列配置：固定列、多级表头、排序、筛选、宽度、单元格类型 |
| `EU_SetTableRowsEx` | 设置高级行数据：树形、展开、懒加载、行样式和单元格类型 |
| `EU_SetTableCellEx` | 设置单元格类型、值和选项 |
| `EU_SetTableRowStyle` | 设置某一行的颜色、对齐、字体标志和字号 |
| `EU_SetTableCellStyle` | 设置某一单元格的颜色、对齐、字体标志和字号 |
| `EU_SetTableSelectionMode` | 设置无选择/单选/多选模式 |
| `EU_SetTableSelectedRows` | 设置多选行集合 |
| `EU_SetTableFilter` | 设置列筛选值 |
| `EU_ClearTableFilter` | 清除单列或全部筛选 |
| `EU_SetTableSearch` | 设置表头搜索文本 |
| `EU_SetTableSpan` | 设置行列合并 |
| `EU_ClearTableSpans` | 清除行列合并 |
| `EU_SetTableSummary` | 设置合计行文本 |
| `EU_SetTableRowExpanded` | 设置行展开状态 |
| `EU_SetTableTreeOptions` | 设置树形、缩进和懒加载模式 |
| `EU_SetTableViewportOptions` | 设置最大高度、固定表头、横向滚动和合计显示 |
| `EU_SetTableScroll` | 设置垂直/水平滚动位置；Table 内容溢出时会显示可拖拽滚动条 |
| `EU_SetTableCellClickCallback` | 设置任意单元格点击回调 |
| `EU_SetTableCellActionCallback` | 设置单元格按钮、开关、选择、展开等交互回调 |
| `EU_GetTableCellValue` | 读取单元格值 |
| `EU_GetTableFullState` | 读取高级表格摘要状态 |
| `EU_SetCardTitle` | 设置 Card 标题 |
| `EU_SetCardBody` | 设置 Card 正文 |
| `EU_SetCardFooter` | 设置 Card 页脚文字 |
| `EU_SetCardItems` | 设置 Card 正文列表项 |
| `EU_SetCardActions` | 设置 Card 页脚操作项 |
| `EU_GetCardItemCount` | 读取 Card 列表项数量 |
| `EU_GetCardAction` | 读取 Card 最近点击的操作索引 |
| `EU_ResetCardAction` | 重置 Card 操作索引 |
| `EU_SetCardShadow` | 设置 Card 阴影模式 |
| `EU_SetCardOptions` | 设置 Card 阴影和悬停选项 |
| `EU_SetCardStyle` | 设置 Card 背景、边框、圆角和外层 padding |
| `EU_GetCardStyle` | 读取 Card 背景、边框、圆角和外层 padding |
| `EU_SetCardBodyStyle` | 设置 Card 正文 padding、字号、列表间距、列表内边距和分割线 |
| `EU_GetCardBodyStyle` | 读取 Card 正文样式 |
| `EU_GetCardOptions` | 读取 Card 阴影、悬停和操作项数量 |
| `EU_SetCollapseItems` | 设置 Collapse 项目；兼容 `标题:正文` 和扩展字段 |
| `EU_SetCollapseItemsEx` | 设置 Collapse 扩展项目，字段为标题、正文、标题图标、右侧说明、禁用 |
| `EU_SetCollapseActive` | 设置单个激活项，兼容旧单展开调用 |
| `EU_GetCollapseActive` | 读取兼容单激活索引 |
| `EU_SetCollapseActiveItems` | 设置多个激活项，非手风琴模式可同时展开 |
| `EU_GetCollapseActiveItems` | 读取多个激活项索引列表 |
| `EU_GetCollapseItemCount` | 读取 Collapse 项目数量 |
| `EU_SetCollapseOptions` | 设置手风琴、再次点击折叠和禁用索引 |
| `EU_SetCollapseAdvancedOptions` | 设置手风琴、再次点击折叠、动画和禁用索引 |
| `EU_GetCollapseOptions` | 读取 Collapse 选项 |
| `EU_GetCollapseStateJson` | 读取 Collapse 完整状态 JSON |
| `EU_SetTimelineItems` | 设置 Timeline 项目，支持类型、图标、颜色、尺寸、时间位置和卡片字段 |
| `EU_SetTimelineOptions` | 设置 Timeline 基础选项：位置和显示时间 |
| `EU_GetTimelineItemCount` | 读取 Timeline 项目数量 |
| `EU_GetTimelineOptions` | 读取 Timeline 基础选项 |
| `EU_SetTimelineAdvancedOptions` | 设置 Timeline 高级选项：位置、显示时间、倒序和默认时间位置 |
| `EU_GetTimelineAdvancedOptions` | 读取 Timeline 高级选项 |
| `EU_SetStatisticValue` | 设置统计数值普通值 |
| `EU_SetStatisticFormat` | 设置统计数值标题、前缀和后缀 |
| `EU_SetStatisticOptions` | 设置统计数值精度与数字动画（兼容旧接口） |
| `EU_GetStatisticOptions` | 读回统计数值精度与动画选项 |
| `EU_SetStatisticNumberOptions` | 设置统计数值精度、动画、千分位和小数分隔符 |
| `EU_SetStatisticAffixOptions` | 设置统计数值前后缀、颜色和后缀可点击 |
| `EU_SetStatisticDisplayText` | 设置统计数值 formatter 风格自定义文本 |
| `EU_SetStatisticCountdown` | 设置统计数值倒计时目标时间和显示格式 |
| `EU_SetStatisticCountdownState` | 暂停或继续统计数值倒计时 |
| `EU_AddStatisticCountdownTime` | 增加或减少统计数值倒计时毫秒数 |
| `EU_SetStatisticFinishCallback` | 设置统计数值倒计时完成回调 |
| `EU_SetStatisticSuffixClickCallback` | 设置统计数值后缀点击回调 |
| `EU_GetStatisticFullState` | 读回统计数值完整状态 |
| `EU_SetKpiCardData` | |
| `EU_SetKpiCardOptions` | |
| `EU_GetKpiCardOptions` | |
| `EU_SetTrendData` | |
| `EU_SetTrendOptions` | |
| `EU_GetTrendDirection` | |
| `EU_GetTrendOptions` | |
| `EU_SetStatusDot` | |
| `EU_SetStatusDotOptions` | |
| `EU_GetStatusDotStatus` | |
| `EU_GetStatusDotOptions` | |
| `EU_SetGaugeValue` | |
| `EU_SetGaugeOptions` | |
| `EU_GetGaugeValue` | |
| `EU_GetGaugeStatus` | |
| `EU_GetGaugeOptions` | |
| `EU_SetRingProgressValue` | |
| `EU_SetRingProgressOptions` | |
| `EU_GetRingProgressValue` | |
| `EU_GetRingProgressStatus` | |
| `EU_GetRingProgressOptions` | |
| `EU_SetBulletProgressValue` | |
| `EU_SetBulletProgressOptions` | |
| `EU_GetBulletProgressValue` | |
| `EU_GetBulletProgressTarget` | |
| `EU_GetBulletProgressStatus` | |
| `EU_GetBulletProgressOptions` | |
| `EU_SetLineChartData` | |
| `EU_SetLineChartSeries` | |
| `EU_SetLineChartOptions` | |
| `EU_SetLineChartSelected` | |
| `EU_GetLineChartPointCount` | |
| `EU_GetLineChartSeriesCount` | |
| `EU_GetLineChartSelected` | |
| `EU_GetLineChartOptions` | |
| `EU_SetBarChartData` | |
| `EU_SetBarChartSeries` | |
| `EU_SetBarChartOptions` | |
| `EU_SetBarChartSelected` | |
| `EU_GetBarChartBarCount` | |
| `EU_GetBarChartSeriesCount` | |
| `EU_GetBarChartSelected` | |
| `EU_GetBarChartOptions` | |
| `EU_SetDonutChartData` | |
| `EU_SetDonutChartOptions` | |
| `EU_SetDonutChartAdvancedOptions` | |
| `EU_SetDonutChartActive` | |
| `EU_GetDonutChartSliceCount` | |
| `EU_GetDonutChartActive` | |
| `EU_GetDonutChartOptions` | |
| `EU_GetDonutChartAdvancedOptions` | |
| `EU_SetCalendarDate` | 设置当前年月和选中日 |
| `EU_SetCalendarRange` | 设置可选日期范围限制，0 表示不限制 |
| `EU_SetCalendarOptions` | 设置今天高亮日期和是否显示今天 |
| `EU_CalendarMoveMonth` | 按月份偏移切换日历 |
| `EU_GetCalendarValue` | 读取当前选中日期，格式 YYYYMMDD |
| `EU_GetCalendarRange` | 读取可选日期范围限制 |
| `EU_GetCalendarOptions` | 读取今天高亮和显示选项 |
| `EU_SetCalendarSelectionRange` | 设置区间选择读回值 |
| `EU_GetCalendarSelectionRange` | 读取区间选择起止日期和启用状态 |
| `EU_SetCalendarDisplayRange` | 设置显示范围，对应 Element UI Calendar 的 `range` |
| `EU_GetCalendarDisplayRange` | 读取显示范围，0/0 表示普通月视图 |
| `EU_SetCalendarCellItems` | 设置 dateCell 等价数据：label、extra、emoji、badge、颜色、禁用态 |
| `EU_GetCalendarCellItems` | 读取 dateCell 单元格数据 UTF-8 文本 |
| `EU_ClearCalendarCellItems` | 清空 dateCell 单元格数据 |
| `EU_SetCalendarVisualOptions` | 设置标题、星期栏、标签模式、相邻月份日期和单元格圆角 |
| `EU_GetCalendarVisualOptions` | 读取日历视觉选项 |
| `EU_SetCalendarStateColors` | 设置选中、区间、今天、悬停、禁用和相邻日期状态颜色 |
| `EU_GetCalendarStateColors` | 读取日历状态颜色 |
| `EU_SetCalendarSelectedMarker` | 设置选中日期角标，例如 `✔️` |
| `EU_SetCalendarChangeCallback` | 设置日期变化回调，返回当前选中值和区间起止值 |
| `EU_SetTreeItems` | |
| `EU_SetTreeSelected` | |
| `EU_GetTreeSelected` | |
| `EU_SetTreeOptions` | |
| `EU_GetTreeOptions` | |
| `EU_SetTreeItemExpanded` | |
| `EU_ToggleTreeItemExpanded` | |
| `EU_GetTreeItemExpanded` | |
| `EU_SetTreeItemChecked` | |
| `EU_GetTreeItemChecked` | |
| `EU_SetTreeItemLazy` | |
| `EU_GetTreeItemLazy` | |
| `EU_GetTreeVisibleCount` | |
| `EU_SetTreeDataJson` | 设置 Tree 嵌套 JSON 数据 |
| `EU_GetTreeDataJson` | 读取 Tree 嵌套 JSON 数据 |
| `EU_SetTreeOptionsJson` | 设置 Tree 高级 JSON 选项 |
| `EU_GetTreeStateJson` | 读取 Tree 状态 JSON |
| `EU_SetTreeCheckedKeysJson` | 按 key 设置 Tree 勾选节点 |
| `EU_GetTreeCheckedKeysJson` | 读取 Tree 勾选 key 数组 JSON |
| `EU_SetTreeExpandedKeysJson` | 按 key 设置 Tree 展开节点 |
| `EU_GetTreeExpandedKeysJson` | 读取 Tree 展开 key 数组 JSON |
| `EU_AppendTreeNodeJson` | 按 parentKey 追加 Tree 节点 JSON |
| `EU_UpdateTreeNodeJson` | 按 key 更新 Tree 节点 JSON |
| `EU_RemoveTreeNodeByKey` | 按 key 删除 Tree 节点及子树 |
| `EU_SetTreeNodeEventCallback` | 设置 Tree 节点事件回调 |
| `EU_SetTreeLazyLoadCallback` | 设置 Tree 懒加载回调 |
| `EU_SetTreeDragCallback` | 设置 Tree 拖拽完成回调 |
| `EU_SetTreeAllowDragCallback` | 设置 Tree 是否允许拖拽回调 |
| `EU_SetTreeAllowDropCallback` | 设置 Tree 是否允许放置回调 |
| `EU_SetTreeSelectItems` | |
| `EU_SetTreeSelectSelected` | |
| `EU_GetTreeSelectSelected` | |
| `EU_SetTreeSelectOpen` | |
| `EU_GetTreeSelectOpen` | |
| `EU_SetTreeSelectOptions` | |
| `EU_GetTreeSelectOptions` | |
| `EU_SetTreeSelectSearch` | |
| `EU_GetTreeSelectSearch` | |
| `EU_ClearTreeSelect` | |
| `EU_SetTreeSelectSelectedItems` | |
| `EU_GetTreeSelectSelectedCount` | |
| `EU_GetTreeSelectSelectedItem` | |
| `EU_SetTreeSelectItemExpanded` | |
| `EU_ToggleTreeSelectItemExpanded` | |
| `EU_GetTreeSelectItemExpanded` | |
| `EU_SetTreeSelectDataJson` | 设置 TreeSelect 嵌套 JSON 数据 |
| `EU_GetTreeSelectDataJson` | 读取 TreeSelect 嵌套 JSON 数据 |
| `EU_SetTreeSelectOptionsJson` | 设置 TreeSelect 高级 JSON 选项 |
| `EU_GetTreeSelectStateJson` | 读取 TreeSelect 状态 JSON |
| `EU_SetTreeSelectSelectedKeysJson` | 按 key 设置 TreeSelect 选中值 |
| `EU_GetTreeSelectSelectedKeysJson` | 读取 TreeSelect 选中 key 数组 JSON |
| `EU_SetTreeSelectExpandedKeysJson` | 按 key 设置 TreeSelect 展开节点 |
| `EU_GetTreeSelectExpandedKeysJson` | 读取 TreeSelect 展开 key 数组 JSON |
| `EU_AppendTreeSelectNodeJson` | 按 parentKey 追加 TreeSelect 节点 JSON |
| `EU_UpdateTreeSelectNodeJson` | 按 key 更新 TreeSelect 节点 JSON |
| `EU_RemoveTreeSelectNodeByKey` | 按 key 删除 TreeSelect 节点及子树 |
| `EU_SetTreeSelectNodeEventCallback` | 设置 TreeSelect 节点事件回调 |
| `EU_SetTreeSelectLazyLoadCallback` | 设置 TreeSelect 懒加载回调 |
| `EU_SetTreeSelectDragCallback` | 设置 TreeSelect 拖拽完成回调 |
| `EU_SetTreeSelectAllowDragCallback` | 设置 TreeSelect 是否允许拖拽回调 |
| `EU_SetTreeSelectAllowDropCallback` | 设置 TreeSelect 是否允许放置回调 |
| `EU_SetTransferItems` | |
| `EU_TransferMoveRight` | |
| `EU_TransferMoveLeft` | |
| `EU_TransferMoveAllRight` | |
| `EU_TransferMoveAllLeft` | |
| `EU_SetTransferSelected` | |
| `EU_GetTransferSelected` | |
| `EU_GetTransferCount` | |
| `EU_SetTransferFilters` | |
| `EU_GetTransferMatchedCount` | |
| `EU_SetTransferItemDisabled` | |
| `EU_GetTransferItemDisabled` | |
| `EU_GetTransferDisabledCount` | |
| `EU_SetTransferDataEx` | 设置 Transfer 结构化项目和目标值 |
| `EU_SetTransferOptions` | 设置 Transfer 筛选、多选、底部区、全选、统计和渲染模式 |
| `EU_GetTransferOptions` | 读回 Transfer 样式与行为选项 |
| `EU_SetTransferTitles` | 设置 Transfer 左右面板标题 |
| `EU_SetTransferButtonTexts` | 设置 Transfer 左右移动按钮文案 |
| `EU_SetTransferFormat` | 设置 Transfer 统计格式 |
| `EU_SetTransferItemTemplate` | 设置 Transfer 数据项字段模板 |
| `EU_SetTransferFooterTexts` | 设置 Transfer 左右底部操作区文案 |
| `EU_SetTransferFilterPlaceholder` | 设置 Transfer 筛选输入框占位文案 |
| `EU_SetTransferCheckedKeys` | 设置 Transfer 左右默认勾选键 |
| `EU_GetTransferCheckedCount` | 读回 Transfer 指定侧勾选数量 |
| `EU_GetTransferValueKeys` | 读回 Transfer 右侧目标值 |
| `EU_GetTransferText` | 读回 Transfer 标题、按钮、格式、模板、底部文案和筛选占位文案 |
| `EU_SetAutocompleteSuggestions` | |
| `EU_SetAutocompleteValue` | |
| `EU_SetAutocompletePlaceholder` | 设置自动补全占位文本 |
| `EU_GetAutocompletePlaceholder` | 读取自动补全占位文本 |
| `EU_SetAutocompleteIcons` | 设置自动补全前后图标 |
| `EU_GetAutocompleteIcons` | 读取自动补全前后图标 |
| `EU_SetAutocompleteBehaviorOptions` | 设置自动补全行为选项 |
| `EU_GetAutocompleteBehaviorOptions` | 读取自动补全行为选项 |
| `EU_SetAutocompleteOpen` | |
| `EU_SetAutocompleteSelected` | |
| `EU_SetAutocompleteAsyncState` | |
| `EU_SetAutocompleteEmptyText` | |
| `EU_GetAutocompleteValue` | |
| `EU_GetAutocompleteOpen` | |
| `EU_GetAutocompleteSelected` | |
| `EU_GetAutocompleteSuggestionCount` | |
| `EU_GetAutocompleteOptions` | |
| `EU_SetMentionsValue` | |
| `EU_SetMentionsSuggestions` | |
| `EU_SetMentionsOpen` | |
| `EU_SetMentionsSelected` | |
| `EU_SetMentionsOptions` | |
| `EU_SetMentionsFilter` | |
| `EU_InsertMentionsSelected` | |
| `EU_GetMentionsValue` | |
| `EU_GetMentionsOpen` | |
| `EU_GetMentionsSelected` | |
| `EU_GetMentionsSuggestionCount` | |
| `EU_GetMentionsOptions` | |
| `EU_SetCascaderOptions` | |
| `EU_SetCascaderValue` | |
| `EU_SetCascaderOpen` | |
| `EU_SetCascaderAdvancedOptions` | |
| `EU_SetCascaderSearch` | |
| `EU_GetCascaderOpen` | |
| `EU_GetCascaderOptionCount` | |
| `EU_GetCascaderSelectedDepth` | |
| `EU_GetCascaderLevelCount` | |
| `EU_GetCascaderAdvancedOptions` | |
| `EU_SetDatePickerDate` | |
| `EU_SetDatePickerRange` | |
| `EU_SetDatePickerOptions` | |
| `EU_SetDatePickerOpen` | |
| `EU_ClearDatePicker` | |
| `EU_DatePickerSelectToday` | |
| `EU_GetDatePickerOpen` | |
| `EU_GetDatePickerValue` | |
| `EU_DatePickerMoveMonth` | |
| `EU_GetDatePickerRange` | |
| `EU_GetDatePickerOptions` | |
| `EU_SetDatePickerSelectionRange` | |
| `EU_GetDatePickerSelectionRange` | |
| `EU_SetTimePickerTime` | |
| `EU_SetTimePickerRange` | |
| `EU_SetTimePickerOptions` | |
| `EU_SetTimePickerOpen` | |
| `EU_SetTimePickerScroll` | |
| `EU_GetTimePickerOpen` | |
| `EU_GetTimePickerValue` | |
| `EU_GetTimePickerRange` | |
| `EU_GetTimePickerOptions` | |
| `EU_GetTimePickerScroll` | |
| `EU_SetTimePickerArrowControl` | |
| `EU_GetTimePickerArrowControl` | |
| `EU_SetTimePickerRangeSelect` | |
| `EU_SetTimePickerStartPlaceholder` | |
| `EU_SetTimePickerEndPlaceholder` | |
| `EU_SetTimePickerRangeSeparator` | |
| `EU_GetTimePickerRangeValue` | |
| `EU_SetDateTimePickerDateTime` | |
| `EU_SetDateTimePickerRange` | |
| `EU_SetDateTimePickerOptions` | |
| `EU_SetDateTimePickerOpen` | |
| `EU_ClearDateTimePicker` | |
| `EU_DateTimePickerSelectToday` | |
| `EU_DateTimePickerSelectNow` | |
| `EU_SetDateTimePickerScroll` | |
| `EU_GetDateTimePickerOpen` | |
| `EU_GetDateTimePickerDateValue` | |
| `EU_GetDateTimePickerTimeValue` | |
| `EU_DateTimePickerMoveMonth` | |
| `EU_GetDateTimePickerRange` | |
| `EU_GetDateTimePickerOptions` | |
| `EU_GetDateTimePickerScroll` | |
| `EU_SetDateTimePickerShortcuts` | |
| `EU_SetDateTimePickerStartPlaceholder` | |
| `EU_SetDateTimePickerEndPlaceholder` | |
| `EU_SetDateTimePickerDefaultTime` | |
| `EU_SetDateTimePickerRangeDefaultTime` | |
| `EU_SetDateTimePickerRangeSeparator` | |
| `EU_SetDateTimePickerRangeSelect` | |
| `EU_GetDateTimePickerRangeValue` | |
| `EU_SetTimeSelectTime` | |
| `EU_SetTimeSelectRange` | |
| `EU_SetTimeSelectOptions` | |
| `EU_SetTimeSelectOpen` | |
| `EU_SetTimeSelectScroll` | |
| `EU_GetTimeSelectOpen` | |
| `EU_GetTimeSelectValue` | |
| `EU_GetTimeSelectRange` | |
| `EU_GetTimeSelectOptions` | |
| `EU_GetTimeSelectState` | |
| `EU_SetDropdownItems` | |
| `EU_SetDropdownSelected` | |
| `EU_GetDropdownSelected` | |
| `EU_SetDropdownOpen` | |
| `EU_GetDropdownOpen` | |
| `EU_GetDropdownItemCount` | |
| `EU_SetDropdownDisabled` | |
| `EU_GetDropdownState` | |
| `EU_SetDropdownOptions` | |
| `EU_GetDropdownOptions` | |
| `EU_SetDropdownItemMeta` | |
| `EU_GetDropdownItemMeta` | |
| `EU_SetDropdownCommandCallback` | |
| `EU_SetDropdownMainClickCallback` | |
| `EU_SetMenuItems` | |
| `EU_SetMenuActive` | |
| `EU_GetMenuActive` | |
| `EU_SetMenuOrientation` | |
| `EU_GetMenuOrientation` | |
| `EU_GetMenuItemCount` | |
| `EU_SetMenuExpanded` | |
| `EU_GetMenuState` | |
| `EU_GetMenuActivePath` | |
| `EU_SetMenuColors` | 设置 Menu/NavMenu 背景、文字、激活文字、悬停、禁用和边框色 |
| `EU_GetMenuColors` | 读取 Menu/NavMenu 自定义颜色 |
| `EU_SetMenuCollapsed` | 设置垂直菜单收起状态 |
| `EU_GetMenuCollapsed` | 读取垂直菜单收起状态 |
| `EU_SetMenuItemMeta` | 设置菜单项图标、分组、链接、目标和命令元数据 |
| `EU_GetMenuItemMeta` | 读取菜单项图标、分组、链接、目标和命令元数据 |
| `EU_SetMenuSelectCallback` | 设置菜单项选择回调 |
| `EU_SetAnchorItems` | |
| `EU_SetAnchorActive` | |
| `EU_GetAnchorActive` | |
| `EU_GetAnchorItemCount` | |
| `EU_SetAnchorTargets` | |
| `EU_SetAnchorOptions` | |
| `EU_SetAnchorScroll` | |
| `EU_GetAnchorState` | |
| `EU_SetBacktopState` | |
| `EU_GetBacktopVisible` | |
| `EU_GetBacktopState` | |
| `EU_SetBacktopOptions` | |
| `EU_SetBacktopScroll` | |
| `EU_TriggerBacktop` | |
| `EU_GetBacktopFullState` | |
| `EU_SetSegmentedItems` | |
| `EU_SetSegmentedActive` | |
| `EU_GetSegmentedActive` | |
| `EU_GetSegmentedItemCount` | |
| `EU_SetSegmentedDisabled` | |
| `EU_GetSegmentedState` | |
| `EU_SetPageHeaderText` | |
| `EU_SetPageHeaderBreadcrumbs` | |
| `EU_SetPageHeaderActions` | |
| `EU_GetPageHeaderAction` | |
| `EU_SetPageHeaderBackText` | |
| `EU_SetPageHeaderActiveAction` | |
| `EU_SetPageHeaderBreadcrumbActive` | |
| `EU_TriggerPageHeaderBack` | |
| `EU_ResetPageHeaderResult` | |
| `EU_GetPageHeaderState` | |
| `EU_SetAffixText` | |
| `EU_SetAffixState` | |
| `EU_GetAffixFixed` | |
| `EU_GetAffixState` | |
| `EU_SetAffixOptions` | |
| `EU_GetAffixOptions` | |
| `EU_SetWatermarkContent` | |
| `EU_SetWatermarkOptions` | |
| `EU_GetWatermarkOptions` | |
| `EU_SetWatermarkLayer` | |
| `EU_GetWatermarkFullOptions` | |
| `EU_SetTourSteps` | |
| `EU_SetTourActive` | |
| `EU_SetTourOpen` | |
| `EU_SetTourOptions` | |
| `EU_SetTourTargetElement` | |
| `EU_SetTourMaskBehavior` | |
| `EU_GetTourActive` | |
| `EU_GetTourOpen` | |
| `EU_GetTourStepCount` | |
| `EU_GetTourOptions` | |
| `EU_GetTourFullState` | |
| `EU_SetImageSource` | 设置图片来源和替代说明，支持本地路径、HTTP 和 HTTPS |
| `EU_SetImageFit` | 设置适配方式：contain、cover、fill、none、scale-down |
| `EU_SetImagePreview` | 打开或关闭图片预览层 |
| `EU_SetImagePreviewEnabled` | 设置是否允许点击打开预览 |
| `EU_SetImagePreviewTransform` | 设置预览缩放比例和偏移 |
| `EU_SetImageCacheEnabled` | 设置是否缓存已解码位图 |
| `EU_SetImageLazy` | 设置视口懒加载，未进入可见区时保持等待状态 |
| `EU_SetImagePlaceholder` | 设置占位图标、文字、前景色和背景色 |
| `EU_SetImageErrorContent` | 设置加载失败图标、文字、前景色和背景色 |
| `EU_SetImagePreviewList` | 设置预览图片列表和当前索引 |
| `EU_SetImagePreviewIndex` | 切换预览列表当前图片 |
| `EU_GetImageStatus` | 读取加载状态：占位、已加载、失败、加载中、懒加载等待 |
| `EU_GetImagePreviewOpen` | 读取预览层打开状态 |
| `EU_GetImageOptions` | 读取基础选项：fit、预览启用、预览打开、状态 |
| `EU_GetImageFullOptions` | 读取完整选项：基础选项、缓存、重载次数、位图尺寸 |
| `EU_GetImageAdvancedOptions` | 读取高级选项：lazy、预览列表、状态、缩放和偏移 |
| `EU_SetCarouselItems` | |
| `EU_SetCarouselActive` | |
| `EU_SetCarouselOptions` | |
| `EU_SetCarouselBehavior` | 设置走马灯触发方式、箭头模式、方向、普通/卡片类型和悬停暂停 |
| `EU_GetCarouselBehavior` | 读取走马灯触发方式、箭头模式、方向、普通/卡片类型和悬停暂停 |
| `EU_SetCarouselVisual` | 设置走马灯文字、背景、指示器颜色和卡片缩放比例 |
| `EU_GetCarouselVisual` | 读取走马灯文字、背景、指示器颜色和卡片缩放比例 |
| `EU_SetCarouselAutoplay` | |
| `EU_SetCarouselAnimation` | |
| `EU_CarouselAdvance` | |
| `EU_CarouselTick` | |
| `EU_GetCarouselActive` | |
| `EU_GetCarouselItemCount` | |
| `EU_GetCarouselOptions` | |
| `EU_GetCarouselFullState` | |
| `EU_SetUploadFiles` | |
| `EU_SetUploadFileItems` | |
| `EU_SetUploadOptions` | |
| `EU_SetUploadStyle` | |
| `EU_GetUploadStyle` | |
| `EU_SetUploadTexts` | |
| `EU_SetUploadConstraints` | |
| `EU_GetUploadConstraints` | |
| `EU_SetUploadPreviewOpen` | |
| `EU_GetUploadPreviewState` | |
| `EU_SetUploadSelectedFiles` | |
| `EU_SetUploadFileStatus` | |
| `EU_RemoveUploadFile` | |
| `EU_RetryUploadFile` | |
| `EU_ClearUploadFiles` | |
| `EU_OpenUploadFileDialog` | |
| `EU_StartUpload` | |
| `EU_GetUploadFileCount` | |
| `EU_GetUploadFileStatus` | |
| `EU_GetUploadSelectedFiles` | |
| `EU_GetUploadFileName` | |
| `EU_GetUploadFullState` | |
| `EU_SetUploadSelectCallback` | |
| `EU_SetUploadActionCallback` | |
| `EU_SetInfiniteScrollItems` | 设置无限滚动列表项目 |
| `EU_AppendInfiniteScrollItems` | 追加无限滚动列表项目 |
| `EU_ClearInfiniteScrollItems` | 清空无限滚动列表项目 |
| `EU_SetInfiniteScrollState` | 设置加载中、没有更多和禁用状态 |
| `EU_SetInfiniteScrollOptions` | 设置行高、间距、触底阈值、样式模式、指示条和索引 |
| `EU_SetInfiniteScrollTexts` | 设置加载中、没有更多和空状态文案 |
| `EU_SetInfiniteScrollScroll` | 设置垂直滚动位置 |
| `EU_GetInfiniteScrollFullState` | 读取项目数、滚动、内容高度、状态、触发次数和样式选项 |
| `EU_SetInfiniteScrollLoadCallback` | 设置触底加载回调 |
| `EU_SetBreadcrumbItems` | |
| `EU_SetBreadcrumbSeparator` | |
| `EU_SetBreadcrumbCurrent` | |
| `EU_TriggerBreadcrumbClick` | |
| `EU_GetBreadcrumbCurrent` | |
| `EU_GetBreadcrumbItemCount` | |
| `EU_GetBreadcrumbState` | |
| `EU_GetBreadcrumbItem` | |
| `EU_GetBreadcrumbFullState` | |
| `EU_SetBreadcrumbSelectCallback` | |
| `EU_SetTabsItems` | |
| `EU_SetTabsItemsEx` | 设置扩展标签页项目：标签、名称、内容、图标、禁用、可关闭 |
| `EU_SetTabsActive` | |
| `EU_SetTabsActiveName` | 按名称激活标签页 |
| `EU_SetTabsType` | |
| `EU_SetTabsPosition` | 设置标签页位置：上、右、下、左 |
| `EU_SetTabsHeaderAlign` | 设置标签页表头文字对齐：0左 1中 2右 |
| `EU_SetTabsOptions` | |
| `EU_SetTabsEditable` | 设置可编辑标签页模式 |
| `EU_SetTabsContentVisible` | 设置标签页是否绘制内容区 |
| `EU_AddTabsItem` | |
| `EU_CloseTabsItem` | |
| `EU_SetTabsScroll` | |
| `EU_TabsScroll` | |
| `EU_GetTabsActive` | |
| `EU_GetTabsHeaderAlign` | 读取标签页表头文字对齐方式 |
| `EU_GetTabsItemCount` | |
| `EU_GetTabsState` | |
| `EU_GetTabsItem` | |
| `EU_GetTabsActiveName` | 读取当前激活标签名称 |
| `EU_GetTabsItemContent` | 读取标签页内容文本 |
| `EU_GetTabsFullState` | |
| `EU_GetTabsFullStateEx` | 读取扩展完整状态，含位置、editable 和内容区状态 |
| `EU_SetTabsChangeCallback` | |
| `EU_SetTabsCloseCallback` | |
| `EU_SetTabsAddCallback` | |
| `EU_SetPagination` | |
| `EU_SetPaginationCurrent` | |
| `EU_SetPaginationPageSize` | |
| `EU_SetPaginationOptions` | |
| `EU_SetPaginationAdvancedOptions` | |
| `EU_SetPaginationPageSizeOptions` | |
| `EU_SetPaginationJumpPage` | |
| `EU_TriggerPaginationJump` | |
| `EU_NextPaginationPageSize` | |
| `EU_GetPaginationCurrent` | |
| `EU_GetPaginationPageCount` | |
| `EU_GetPaginationState` | |
| `EU_GetPaginationFullState` | |
| `EU_GetPaginationAdvancedOptions` | |
| `EU_SetPaginationChangeCallback` | |
| `EU_SetStepsItems` | |
| `EU_SetStepsDetailItems` | |
| `EU_SetStepsIconItems` | |
| `EU_SetStepsActive` | |
| `EU_SetStepsDirection` | |
| `EU_SetStepsOptions` | |
| `EU_GetStepsOptions` | |
| `EU_SetStepsStatuses` | |
| `EU_TriggerStepsClick` | |
| `EU_GetStepsActive` | |
| `EU_GetStepsItemCount` | |
| `EU_GetStepsState` | |
| `EU_GetStepsItem` | |
| `EU_GetStepsFullState` | |
| `EU_GetStepsVisualState` | |
| `EU_SetStepsChangeCallback` | |
| `EU_SetAlertDescription` | |
| `EU_SetAlertType` | |
| `EU_SetAlertEffect` | |
| `EU_SetAlertClosable` | |
| `EU_SetAlertAdvancedOptions` | 设置 Alert 显示图标、居中和描述换行 |
| `EU_GetAlertAdvancedOptions` | 读取 Alert 高级选项 |
| `EU_SetAlertCloseText` | 设置 Alert 自定义关闭文字 |
| `EU_GetAlertText` | 读取 Alert 标题、描述或关闭文字 |
| `EU_SetAlertClosed` | |
| `EU_TriggerAlertClose` | |
| `EU_GetAlertClosed` | |
| `EU_GetAlertOptions` | |
| `EU_GetAlertFullState` | |
| `EU_SetAlertCloseCallback` | |
| `EU_SetResultSubtitle` | |
| `EU_SetResultType` | |
| `EU_SetResultActions` | |
| `EU_GetResultAction` | |
| `EU_GetResultOptions` | |
| `EU_SetResultExtraContent` | |
| `EU_TriggerResultAction` | |
| `EU_GetResultText` | |
| `EU_GetResultActionText` | |
| `EU_GetResultFullState` | |
| `EU_SetResultActionCallback` | |
| `EU_SetMessageBoxBeforeClose` | 设置 MessageBox 确认按钮 loading 与延迟关闭 |
| `EU_SetMessageBoxInput` | 设置 Prompt 输入值、占位和校验 |
| `EU_GetMessageBoxInput` | 读取 Prompt 输入值 |
| `EU_GetMessageBoxFullState` | 读取 MessageBox 完整状态 |
| `EU_SetMessageText` | 更新 Message 文本 |
| `EU_SetMessageOptions` | 设置 Message 类型、关闭、居中、富文本、持续时间和偏移 |
| `EU_SetMessageClosed` | 设置 Message 关闭状态 |
| `EU_GetMessageOptions` | 读取 Message 基础选项 |
| `EU_GetMessageFullState` | 读取 Message 完整状态 |
| `EU_TriggerMessageClose` | 程序触发 Message 关闭 |
| `EU_SetMessageCloseCallback` | 设置 Message 关闭回调 |
| `EU_SetNotificationBody` | |
| `EU_SetNotificationType` | |
| `EU_SetNotificationClosable` | |
| `EU_SetNotificationOptions` | |
| `EU_SetNotificationClosed` | |
| `EU_GetNotificationClosed` | |
| `EU_GetNotificationOptions` | |
| `EU_SetNotificationPlacement` | 设置 Notification 四角位置和偏移 |
| `EU_SetNotificationRichMode` | 设置 Notification 轻量富文本模式 |
| `EU_SetNotificationStack` | |
| `EU_TriggerNotificationClose` | |
| `EU_GetNotificationText` | |
| `EU_GetNotificationFullState` | |
| `EU_GetNotificationFullStateEx` | 读取 Notification 扩展完整状态 |
| `EU_SetNotificationCloseCallback` | |
| `EU_SetLoadingActive` | |
| `EU_SetLoadingText` | 设置 Loading 加载文本 |
| `EU_SetLoadingOptions` | |
| `EU_SetLoadingStyle` | 设置 Loading 遮罩色、图标色、文字色、spinner 类型和锁定输入 |
| `EU_GetLoadingActive` | |
| `EU_GetLoadingOptions` | |
| `EU_SetLoadingTarget` | |
| `EU_GetLoadingText` | |
| `EU_GetLoadingStyle` | 读取 Loading 样式 |
| `EU_ShowLoading` | 服务式显示 Loading |
| `EU_CloseLoading` | 关闭服务式 Loading |
| `EU_GetLoadingFullState` | |
| `EU_SetDialogOpen` | |
| `EU_SetDialogTitle` | |
| `EU_SetDialogBody` | |
| `EU_SetDialogOptions` | |
| `EU_SetDialogAdvancedOptions` | 设置 Dialog 百分比宽度、居中和 slot 布局 |
| `EU_GetDialogAdvancedOptions` | 读取 Dialog 高级选项、slot ID 和 before-close 待确认状态 |
| `EU_GetDialogContentParent` | 获取 Dialog 内容 slot 容器 ID |
| `EU_GetDialogFooterParent` | 获取 Dialog 页脚 slot 容器 ID |
| `EU_SetDialogBeforeCloseCallback` | 设置 Dialog 关闭前拦截回调 |
| `EU_ConfirmDialogClose` | before-close 拦截后确认继续或取消关闭 |
| `EU_GetDialogOpen` | |
| `EU_GetDialogOptions` | |
| `EU_SetDialogButtons` | |
| `EU_TriggerDialogButton` | |
| `EU_GetDialogText` | |
| `EU_GetDialogButtonText` | |
| `EU_GetDialogFullState` | |

## Table 补充

| 导出 | 说明 |
|---|---|
| `EU_SetTableHeaderDragOptions` | 设置 Table 表头拖拽开关、列宽拖拽和表头高度拖拽参数 |
| `EU_ExportTableExcel` | 导出 Table 到 `.xlsx` |
| `EU_ImportTableExcel` | 从 `.xlsx` 导入 Table |
| `EU_SetDialogButtonCallback` | |
| `EU_SetDrawerOpen` | 设置 Drawer 打开状态 |
| `EU_SetDrawerTitle` | 设置 Drawer 标题 |
| `EU_SetDrawerBody` | 设置 Drawer 正文 fallback 文本 |
| `EU_SetDrawerPlacement` | 设置 Drawer 方向，0左 1右 2上 3下 |
| `EU_SetDrawerOptions` | 设置 Drawer 基础选项、遮罩关闭和像素尺寸 |
| `EU_SetDrawerAdvancedOptions` | 设置 Drawer 标题栏、关闭按钮、ESC、padding、footer 和像素/百分比尺寸 |
| `EU_GetDrawerAdvancedOptions` | 读取 Drawer 高级选项、slot ID 和 before-close pending 状态 |
| `EU_GetDrawerContentParent` | 获取 Drawer 内容 slot 容器 ID |
| `EU_GetDrawerFooterParent` | 获取 Drawer 页脚 slot 容器 ID |
| `EU_SetDrawerBeforeCloseCallback` | 设置 Drawer 关闭前拦截回调 |
| `EU_ConfirmDrawerClose` | before-close 拦截后确认继续或取消关闭 |
| `EU_GetDrawerOpen` | 读取 Drawer 打开状态 |
| `EU_GetDrawerOptions` | 读取 Drawer 基础选项 |
| `EU_SetDrawerAnimation` | 设置 Drawer 打开动画时长 |
| `EU_TriggerDrawerClose` | 程序触发 Drawer 关闭 |
| `EU_GetDrawerText` | 读取 Drawer 标题或正文 |
| `EU_GetDrawerFullState` | 读取 Drawer 完整基础状态 |
| `EU_SetDrawerCloseCallback` | 设置 Drawer 实际关闭后的回调 |
| `EU_SetTooltipContent` | |
| `EU_SetTooltipOpen` | |
| `EU_SetTooltipOptions` | |
| `EU_GetTooltipOpen` | |
| `EU_GetTooltipOptions` | |
| `EU_SetTooltipBehavior` | |
| `EU_SetTooltipAdvancedOptions` | 设置 Tooltip 12 方位、明暗主题、disabled、箭头和 offset |
| `EU_GetTooltipAdvancedOptions` | 读取 Tooltip 高级选项 |
| `EU_TriggerTooltip` | |
| `EU_GetTooltipText` | |
| `EU_GetTooltipFullState` | |
| `EU_SetPopoverOpen` | |
| `EU_SetPopoverContent` | |
| `EU_SetPopoverTitle` | |
| `EU_SetPopoverOptions` | |
| `EU_SetPopoverAdvancedOptions` | 设置 Popover 12 方位和弹层尺寸 |
| `EU_SetPopoverBehavior` | 设置 Popover hover/click/focus/manual 行为 |
| `EU_GetPopoverBehavior` | 读取 Popover 行为选项 |
| `EU_GetPopoverContentParent` | 获取 Popover 内容 slot 容器 ID |
| `EU_GetPopoverOpen` | |
| `EU_GetPopoverOptions` | |
| `EU_TriggerPopover` | |
| `EU_GetPopoverText` | |
| `EU_GetPopoverFullState` | |
| `EU_SetPopoverActionCallback` | |
| `EU_SetPopupAnchorElement` | 设置 Popover/Menu/Dropdown 通用弹层锚点元素 |
| `EU_SetPopupPlacement` | 设置 Popover/Menu/Dropdown 通用弹层 12 方位和偏移 |
| `EU_SetPopupOpen` | 打开或关闭 Popover/Menu/Dropdown 通用弹层 |
| `EU_GetPopupOpen` | 读取 Popover/Menu/Dropdown 通用弹层打开状态 |
| `EU_SetPopupDismissBehavior` | 设置 Popover/Menu/Dropdown 外部点击和 Esc 关闭策略 |
| `EU_SetElementPopup` | 绑定任意 Element 与 Popover/Menu/Dropdown，支持左键、右键、悬停、聚焦、手动触发 |
| `EU_ClearElementPopup` | 清除某个 Element 指定触发方式的弹层绑定 |
| `EU_GetElementPopup` | 读取某个 Element 指定触发方式绑定的 popup ID |
| `EU_SetPopconfirmOpen` | |
| `EU_SetPopconfirmOptions` | |
| `EU_SetPopconfirmAdvancedOptions` | 设置 Popconfirm 12 方位、触发、外部关闭、箭头和 offset |
| `EU_SetPopconfirmContent` | |
| `EU_SetPopconfirmButtons` | |
| `EU_SetPopconfirmIcon` | 设置 Popconfirm 图标文本/emoji、颜色和显示状态 |
| `EU_GetPopconfirmIcon` | 读取 Popconfirm 图标文本/emoji、颜色和显示状态 |
| `EU_ResetPopconfirmResult` | |
| `EU_GetPopconfirmOpen` | |
| `EU_GetPopconfirmResult` | |
| `EU_GetPopconfirmOptions` | |
| `EU_TriggerPopconfirmResult` | |
| `EU_GetPopconfirmText` | |
| `EU_GetPopconfirmFullState` | |
| `EU_SetPopconfirmResultCallback` | |
| `EU_SetElementClickCallback` | |
| `EU_SetElementKeyCallback` | |
| `EU_SetWindowResizeCallback` | |
| `EU_SetWindowCloseCallback` | |
| `EU_SetDarkMode` | |
| `EU_SetThemeMode` | |
| `EU_GetThemeMode` | |
| `EU_SetThemeColor` | |
| `EU_ResetTheme` | |
| `EU_InvalidateElement` | |

## Chrome 高仿外壳 API

### 新增组件

| 导出 | 说明 |
|---|---|
| `EU_CreateIconButton` | 创建透明默认态的工具栏图标按钮，支持 hover/press/checked、徽标、tooltip、dropdown。 |
| `EU_CreateOmnibox` | 创建 Chrome 风格地址栏，支持安全状态、前缀 chip、动作图标、建议列表和提交回调。 |
| `EU_CreateBrowserViewport` | 创建浏览内容占位区，提供空白页、加载中、截图占位、错误页和新标签页状态。 |

### 主要增强导出

`EU_SetTabsChromeMode`、`EU_GetTabsChromeMode`、`EU_SetTabsItemChromeState`、`EU_GetTabsItemChromeState`、`EU_SetMenuItemIcon`、`EU_SetMenuItemShortcut`、`EU_SetMenuItemChecked`、`EU_SetPopoverAnchorElement`、`EU_SetPopoverDismissBehavior`、`EU_SetPopupAnchorElement`、`EU_SetPopupPlacement`、`EU_SetPopupOpen`、`EU_GetPopupOpen`、`EU_SetPopupDismissBehavior`、`EU_SetElementPopup`、`EU_ClearElementPopup`、`EU_GetElementPopup`、`EU_SetWindowDragRegion`、`EU_SetContainerFlexLayout`、`EU_SetChromeThemePreset`、`EU_SetThemeToken`、`EU_GetThemeToken`、`EU_SetHighContrastMode`、`EU_SetIncognitoMode`。

易语言命令左侧可使用中文名，例如 `创建工具栏图标按钮`、`创建地址栏`、`创建浏览内容占位区`；右侧 DLL 入口名保持上述 `EU_` 导出名。

## Window Frame 通用窗口框架 API

| 导出 | 说明 |
|---|---|
| `EU_CreateWindowEx` | 创建扩展窗口，使用 `frame_flags` 开启无标题栏、自绘按钮、缩放边框等通用窗口外壳能力。 |
| `EU_GetWindowFrameFlags` | 读取窗口框架 flags。 |
| `EU_SetWindowFrameFlags` | 设置窗口框架 flags，v1 主要更新内部状态、布局和重绘。 |
| `EU_SetWindowResizeBorder` | 设置四边自定义缩放命中宽度。 |
| `EU_GetWindowResizeBorder` | 读取四边自定义缩放命中宽度。 |
| `EU_SetWindowNoDragRegion` | 设置非拖拽区域，避免按钮、地址栏、标签项被拖拽区覆盖。 |
| `EU_ClearWindowNoDragRegions` | 清空非拖拽区域。 |
| `EU_SetElementWindowCommand` | 将任意 Element 绑定为最小化、最大化/还原、关闭窗口按钮。 |
| `EU_GetElementWindowCommand` | 读取 Element 绑定的窗口命令。 |
