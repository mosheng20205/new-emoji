# API 索引

本索引从 `src/new_emoji.def` 生成，用于快速确认当前 DLL 导出名称。说明列可逐步补充，组件级说明请查看 [组件文档](components/README.md)。

| 导出 | 说明 |
|---|---|
| `EU_CreateWindow` | |
| `EU_CreateWindowDark` | |
| `EU_DestroyWindow` | |
| `EU_ShowWindow` | |
| `EU_SetWindowTitle` | |
| `EU_SetWindowBounds` | |
| `EU_GetWindowBounds` | |
| `EU_CreatePanel` | |
| `EU_CreateButton` | |
| `EU_CreateEditBox` | |
| `EU_CreateInfoBox` | |
| `EU_CreateText` | |
| `EU_CreateLink` | |
| `EU_CreateIcon` | |
| `EU_CreateSpace` | |
| `EU_CreateContainer` | |
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
| `EU_CreateEmpty` | |
| `EU_CreateSkeleton` | |
| `EU_CreateDescriptions` | |
| `EU_CreateTable` | 创建表格；兼容旧基础表格协议，高级能力通过 `EU_SetTableColumnsEx` / `EU_SetTableRowsEx` 补齐 |
| `EU_CreateCard` | |
| `EU_CreateCollapse` | |
| `EU_CreateTimeline` | 创建 Timeline 时间线，支持中文和 emoji 项目 |
| `EU_CreateStatistic` | |
| `EU_CreateKpiCard` | |
| `EU_CreateTrend` | |
| `EU_CreateStatusDot` | |
| `EU_CreateGauge` | |
| `EU_CreateRingProgress` | |
| `EU_CreateBulletProgress` | |
| `EU_CreateLineChart` | |
| `EU_CreateBarChart` | |
| `EU_CreateDonutChart` | |
| `EU_CreateDivider` | |
| `EU_CreateCalendar` | |
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
| `EU_SetDividerOptions` | |
| `EU_GetDividerOptions` | |
| `EU_SetDividerSpacing` | |
| `EU_GetDividerSpacing` | |
| `EU_SetButtonEmoji` | |
| `EU_SetButtonVariant` | |
| `EU_GetButtonState` | |
| `EU_SetButtonOptions` | |
| `EU_GetButtonOptions` | |
| `EU_SetEditBoxText` | |
| `EU_SetEditBoxOptions` | |
| `EU_GetEditBoxOptions` | |
| `EU_GetEditBoxState` | |
| `EU_GetEditBoxText` | |
| `EU_SetEditBoxTextCallback` | |
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
| `EU_SetAvatarShape` | |
| `EU_SetAvatarSource` | |
| `EU_SetAvatarFit` | |
| `EU_GetAvatarImageStatus` | |
| `EU_GetAvatarOptions` | |
| `EU_SetEmptyDescription` | |
| `EU_SetEmptyOptions` | |
| `EU_SetEmptyActionClicked` | |
| `EU_GetEmptyActionClicked` | |
| `EU_SetEmptyActionCallback` | |
| `EU_SetSkeletonRows` | |
| `EU_SetSkeletonAnimated` | |
| `EU_SetSkeletonLoading` | |
| `EU_SetSkeletonOptions` | |
| `EU_GetSkeletonLoading` | |
| `EU_GetSkeletonOptions` | |
| `EU_SetDescriptionsItems` | |
| `EU_SetDescriptionsColumns` | |
| `EU_SetDescriptionsBordered` | |
| `EU_SetDescriptionsOptions` | |
| `EU_GetDescriptionsItemCount` | |
| `EU_SetDescriptionsAdvancedOptions` | |
| `EU_GetDescriptionsOptions` | |
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
| `EU_SetCardBody` | |
| `EU_SetCardFooter` | |
| `EU_SetCardActions` | |
| `EU_GetCardAction` | |
| `EU_ResetCardAction` | |
| `EU_SetCardShadow` | |
| `EU_SetCardOptions` | |
| `EU_GetCardOptions` | |
| `EU_SetCollapseItems` | |
| `EU_SetCollapseActive` | |
| `EU_GetCollapseActive` | |
| `EU_GetCollapseItemCount` | |
| `EU_SetCollapseOptions` | |
| `EU_SetCollapseAdvancedOptions` | |
| `EU_GetCollapseOptions` | |
| `EU_SetTimelineItems` | 设置 Timeline 项目，支持类型、图标、颜色、尺寸、时间位置和卡片字段 |
| `EU_SetTimelineOptions` | 设置 Timeline 基础选项：位置和显示时间 |
| `EU_GetTimelineItemCount` | 读取 Timeline 项目数量 |
| `EU_GetTimelineOptions` | 读取 Timeline 基础选项 |
| `EU_SetTimelineAdvancedOptions` | 设置 Timeline 高级选项：位置、显示时间、倒序和默认时间位置 |
| `EU_GetTimelineAdvancedOptions` | 读取 Timeline 高级选项 |
| `EU_SetStatisticValue` | |
| `EU_SetStatisticFormat` | |
| `EU_SetStatisticOptions` | |
| `EU_GetStatisticOptions` | |
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
| `EU_SetCalendarDate` | |
| `EU_SetCalendarRange` | |
| `EU_SetCalendarOptions` | |
| `EU_CalendarMoveMonth` | |
| `EU_GetCalendarValue` | |
| `EU_GetCalendarRange` | |
| `EU_GetCalendarOptions` | |
| `EU_SetCalendarSelectionRange` | |
| `EU_GetCalendarSelectionRange` | |
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
| `EU_SetTabsOptions` | |
| `EU_SetTabsEditable` | 设置可编辑标签页模式 |
| `EU_SetTabsContentVisible` | 设置标签页是否绘制内容区 |
| `EU_AddTabsItem` | |
| `EU_CloseTabsItem` | |
| `EU_SetTabsScroll` | |
| `EU_TabsScroll` | |
| `EU_GetTabsActive` | |
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
| `EU_SetPaginationPageSizeOptions` | |
| `EU_SetPaginationJumpPage` | |
| `EU_TriggerPaginationJump` | |
| `EU_NextPaginationPageSize` | |
| `EU_GetPaginationCurrent` | |
| `EU_GetPaginationPageCount` | |
| `EU_GetPaginationState` | |
| `EU_GetPaginationFullState` | |
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
| `EU_SetLoadingOptions` | |
| `EU_GetLoadingActive` | |
| `EU_GetLoadingOptions` | |
| `EU_SetLoadingTarget` | |
| `EU_GetLoadingText` | |
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
