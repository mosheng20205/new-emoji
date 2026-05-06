# 组件文档导航

计划内 88 个组件均已完成封装。每个组件都有单独文档，组件 API 变更时必须同步更新对应文档。

`Input` 是当前推荐的表单输入组件；`EditBox` 作为早期 MVP 的兼容编辑内核单独保留，不再放入基础布局分类。

## 🧱 基础/布局
`Button` 已补齐 Element 风格常用按钮样式，包括语义变体、朴素、圆角、圆形、加载中和尺寸选项。

| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Panel` | 面板 | `EU_CreatePanel` | 已完成 | [面板](./panel.md) |
| `Button` | 按钮 | `EU_CreateButton` | 已完成 | [按钮](./button.md) |
| `InfoBox` | 信息框 | `EU_CreateInfoBox` | 已完成 | [信息框](./info-box.md) |
| `Text` | 文本 | `EU_CreateText` | 已完成 | [文本](./text.md) |
| `Link` | 链接 | `EU_CreateLink` | 已完成 | [链接](./link.md) |
| `Icon` | 图标 | `EU_CreateIcon` | 已完成 | [图标](./icon.md) |
| `Space` | 间距 | `EU_CreateSpace` | 已完成 | [间距](./space.md) |
| `Container` | 容器套件 | `EU_CreateContainer` | 已完成，支持 Header/Aside/Main/Footer 流式布局套件 | [容器套件](./container.md) |
| `Header` | 顶栏 | `EU_CreateHeader` | 已完成 | [顶栏](./header.md) |
| `Aside` | 侧边栏 | `EU_CreateAside` | 已完成 | [侧边栏](./aside.md) |
| `Main` | 主要区域 | `EU_CreateMain` | 已完成 | [主要区域](./main.md) |
| `Footer` | 底栏 | `EU_CreateFooter` | 已完成 | [底栏](./footer.md) |
| `Layout` | 布局 | `EU_CreateLayout` | 已完成 | [布局](./layout.md) |
| `Border` | 边框 | `EU_CreateBorder` | 已完成 | [边框](./border.md) |
| `Divider` | 分割线 | `EU_CreateDivider` | 已完成，支持横/竖向、文本位置、图标内容、实线/虚线/点线/双线、颜色、线宽和间距 | [分割线](./divider.md) |

## 🧩 兼容内核
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `EditBox` | 兼容编辑内核 | `EU_CreateEditBox` | 已完成，表单输入推荐使用 `Input` | [兼容编辑内核](./edit-box.md) |

## 📝 表单/选择
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Checkbox` | 复选框 | `EU_CreateCheckbox` / `EU_CreateCheckboxGroup` | 已完成，支持组、按钮样式、边框、尺寸、min/max | [复选框](./checkbox.md) |
| `Radio` | 单选框 | `EU_CreateRadio` / `EU_CreateRadioGroup` | 已完成，支持 value、按钮样式、边框、尺寸、整组禁用 | [单选框](./radio.md) |
| `Switch` | 开关 | `EU_CreateSwitch` | 已完成 | [开关](./switch.md) |
| `Slider` | 滑块 | `EU_CreateSlider` | 已完成 | [滑块](./slider.md) |
| `InputNumber` | 数字输入框 | `EU_CreateInputNumber` | 已完成 | [数字输入框](./input-number.md) |
| `Input` | 输入框 | `EU_CreateInput` | 已完成 | [输入框](./input.md) |
| `InputGroup` | 组合输入 | `EU_CreateInputGroup` | 已完成 | [组合输入](./input-group.md) |
| `InputTag` | 标签输入 | `EU_CreateInputTag` | 已完成 | [标签输入](./input-tag.md) |
| `Select` | 选择器 | `EU_CreateSelect` | 已完成 | [选择器](./select.md) |
| `SelectV2` | 虚拟选择器 | `EU_CreateSelectV2` | 已完成 | [虚拟选择器](./selectv2.md) |
| `Rate` | 评分 | `EU_CreateRate` | 已完成 | [评分](./rate.md) |
| `ColorPicker` | 颜色选择器（默认值/空值/透明度/预设色/四尺寸） | `EU_CreateColorPicker` | 已完成 | [颜色选择器](./color-picker.md) |

## 📊 数据展示
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Tag` | 标签 | `EU_CreateTag` | 已完成 | [标签](./tag.md) |
| `Badge` | 徽标 | `EU_CreateBadge` / `EU_SetBadgeType` | 已完成，覆盖数值、最大值、文本、dot、四角位置、独立徽标、语义配色和自定义色 | [徽标](./badge.md) |
| `Progress` | 进度条全样式 | `EU_CreateProgress` | 已完成 | [进度条](./progress.md) |
| `Avatar` | 头像：圆形/方形、图片/图标/文字、失败回退、五种适配 | `EU_CreateAvatar` | 已完成 | [头像](./avatar.md) |
| `Empty` | 空状态：描述、图片、尺寸、操作按钮和插槽按钮 | `EU_CreateEmpty` | 全样式已完成 | [空状态](./empty.md) |
| `Skeleton` | 骨架屏 | `EU_CreateSkeleton` | 已完成 | [骨架屏](./skeleton.md) |
| `Descriptions` | 描述列表 | `EU_CreateDescriptions` | 全样式已完成 | [描述列表](./descriptions.md) |
| `Table` | 高级表格：固定列、多级表头、纵横滚动条、表头拖拽、Excel 导入导出、单元格点击回调、筛选搜索、树形、合计、内置单元格控件、虚表 | `EU_CreateTable` | 高级样式完成 | [表格](./table.md) |
| `InfiniteScroll` | 无限滚动 | `EU_CreateInfiniteScroll` | 已完成 | [无限滚动](./infinite-scroll.md) |
| `Card` | 卡片：标题、正文、列表、页脚操作、阴影、样式读回和子元素插槽图片卡片 | `EU_CreateCard` | 全样式已完成 | [卡片](./card.md) |
| `Collapse` | 折叠面板：多展开、手风琴、自定义标题、禁用项和状态读回 | `EU_CreateCollapse` | 全样式已完成 | [折叠面板](./collapse.md) |
| `Timeline` | 时间线 | `EU_CreateTimeline` / `EU_SetTimelineAdvancedOptions` | 已完成，覆盖倒序、节点图标、类型色、自定义颜色、大尺寸节点、顶部/底部时间戳、卡片式项目和三种位置 | [时间线](./timeline.md) |
| `Statistic` | 统计数值：格式化数值、前后缀样式、formatter、后缀点击、倒计时、暂停/继续、完成回调 | `EU_CreateStatistic` | 已完成 | [统计数值](./statistic.md) |

## 📈 指标/图表
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `KpiCard` | 指标卡 | `EU_CreateKpiCard` | 已完成 | [指标卡](./kpi-card.md) |
| `Trend` | 趋势 | `EU_CreateTrend` | 已完成 | [趋势](./trend.md) |
| `StatusDot` | 状态点 | `EU_CreateStatusDot` | 已完成 | [状态点](./status-dot.md) |
| `Gauge` | 仪表盘 | `EU_CreateGauge` | 已完成 | [仪表盘](./gauge.md) |
| `RingProgress` | 环形进度 | `EU_CreateRingProgress` | 已完成 | [环形进度](./ring-progress.md) |
| `BulletProgress` | 子弹进度 | `EU_CreateBulletProgress` | 已完成 | [子弹进度](./bullet-progress.md) |
| `LineChart` | 折线图 | `EU_CreateLineChart` | 已完成 | [折线图](./line-chart.md) |
| `BarChart` | 柱状图 | `EU_CreateBarChart` | 已完成 | [柱状图](./bar-chart.md) |
| `DonutChart` | 环形图 | `EU_CreateDonutChart` | 已完成 | [环形图](./donut-chart.md) |

## 📅 日期时间
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Calendar` | 日历 | `EU_CreateCalendar` / `EU_SetCalendarDisplayRange` / `EU_SetCalendarCellItems` | 已完成，覆盖基础绑定、dateCell 自定义、显示范围、状态颜色、选中标记和变化回调 | [日历](./calendar.md) |
| `DatePicker` | 日期选择器 | `EU_CreateDatePicker` | 已完成 | [日期选择器](./date-picker.md) |
| `TimePicker` | 时间选择器 | `EU_CreateTimePicker` | 已完成 | [时间选择器](./time-picker.md) |
| `DateTimePicker` | 日期时间选择器 | `EU_CreateDateTimePicker` | 已完成 | [日期时间选择器](./date-time-picker.md) |
| `TimeSelect` | 时间选择 | `EU_CreateTimeSelect` | 已完成 | [时间选择](./time-select.md) |

## 🌲 复杂选择
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Tree` | 树 | `EU_CreateTree` | 高级 JSON 全样式完成，兼容旧扁平接口 | [树](./tree.md) |
| `TreeSelect` | 树选择 | `EU_CreateTreeSelect` | 高级 JSON 全样式完成，兼容旧扁平接口 | [树选择](./tree-select.md) |
| `Transfer` | 穿梭框 | `EU_CreateTransfer` | 已完成，支持筛选占位 / 多选勾选 / 字段模板 / 底部操作区 | [穿梭框](./transfer.md) |
| `Autocomplete` | 自动补全 | `EU_CreateAutocomplete` | 已完成，支持 placeholder / trigger_on_focus / 图标 / 双行建议项 | [自动补全](./autocomplete.md) |
| `Mentions` | 提及 | `EU_CreateMentions` | 已完成 | [提及](./mentions.md) |
| `Cascader` | 级联选择 | `EU_CreateCascader` | 已完成 | [级联选择](./cascader.md) |

## 🧭 导航
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Dropdown` | 下拉菜单 | `EU_CreateDropdown` | 已完成 | [下拉菜单](./dropdown.md) |
| `Menu` | 菜单 / NavMenu 导航菜单 | `EU_CreateMenu` | 已完成，支持纵向滚动条 | [菜单 / NavMenu 导航菜单](./menu.md) |
| `Anchor` | 锚点 | `EU_CreateAnchor` | 已完成 | [锚点](./anchor.md) |
| `Backtop` | 回到顶部 | `EU_CreateBacktop` | 已完成 | [回到顶部](./backtop.md) |
| `Segmented` | 分段控制器 | `EU_CreateSegmented` | 已完成 | [分段控制器](./segmented.md) |
| `PageHeader` | 页头 | `EU_CreatePageHeader` | 已完成 | [页头](./page-header.md) |
| `Affix` | 固钉 | `EU_CreateAffix` | 已完成 | [固钉](./affix.md) |
| `Breadcrumb` | 面包屑 | `EU_CreateBreadcrumb` | 已完成 | [面包屑](./breadcrumb.md) |
| `Tabs` | 标签页 | `EU_CreateTabs` | 已完成 | [标签页](./tabs.md) |
| `Pagination` | 分页 | `EU_CreatePagination` | 已完成（全样式） | [分页](./pagination.md) |
| `Steps` | 步骤条 | `EU_CreateSteps` | 已完成，支持固定间距、居中、自定义图标、纵向和简洁模式 | [步骤条](./steps.md) |

## 🖼️ 媒体/工具
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Watermark` | 水印 | `EU_CreateWatermark` | 已完成 | [水印](./watermark.md) |
| `Tour` | 漫游引导 | `EU_CreateTour` | 已完成 | [漫游引导](./tour.md) |
| `Image` | 图片 | `EU_CreateImage` | 已完成，支持五种 fit、占位/失败自定义、懒加载、远程图片和预览列表 | [图片](./image.md) |
| `Carousel` | 轮播 | `EU_CreateCarousel` | 已完成，支持 hover/click 指示器、inside/outside、箭头模式、自动播放、普通/卡片、水平/垂直和视觉样式 | [轮播](./carousel.md) |
| `Upload` | 上传 | `EU_CreateUpload` | 已完成，支持普通列表、头像、图片卡片、图片列表、拖拽、手动上传、系统文件选择和类型过滤 | [上传](./upload.md) |

## 💬 反馈/浮层
| 组件 | 中文名 | 创建导出 | 状态 | 文档 |
|---|---|---|---|---|
| `Alert` | 警告提示 | `EU_CreateAlert` / `EU_CreateAlertEx` | 已完成，支持四类型、浅色/深色、关闭文字、显示/隐藏图标、居中和长描述换行 | [警告提示](./alert.md) |
| `Result` | 结果页 | `EU_CreateResult` | 已完成 | [结果页](./result.md) |
| `Message` | 消息提示 | `EU_ShowMessage` | 已完成，服务式轻提示，支持四类型、可关闭、居中、富文本、自动关闭、偏移和堆叠 | [消息提示](./message.md) |
| `MessageBox` | 消息框 | `EU_ShowMessageBoxEx` / `EU_ShowPromptBox` | 已完成，支持 alert/confirm/prompt/msgbox、富文本、区分关闭、loading 和输入校验 | [消息框](./message-box.md) |
| `Notification` | 通知 | `EU_CreateNotification` / `EU_ShowNotification` | 已完成，支持嵌入式与服务式通知、四角位置、offset、富文本和隐藏关闭按钮 | [通知](./notification.md) |
| `Loading` | 加载 | `EU_CreateLoading` / `EU_ShowLoading` | 已完成，支持局部遮罩、自定义背景、三种 spinner、全屏锁定和服务式调用 | [加载](./loading.md) |
| `Dialog` | 对话框 | `EU_CreateDialog` | 已完成：slot / before-close / 居中 / 嵌套内容 | [对话框](./dialog.md) |
| `Drawer` | 抽屉 | `EU_CreateDrawer` | 已完成：四方向 / 无标题栏 / 50% 尺寸 / slot / before-close / 嵌套抽屉 | [抽屉](./drawer.md) |
| `Tooltip` | 文字提示 | `EU_CreateTooltip` | 已完成：12 方位 / dark-light / disabled / 换行 | [文字提示](./tooltip.md) |
| `Popover` | 弹出框 | `EU_CreatePopover` | 已完成：slot / 四触发 / 12 方位 / 键盘关闭 | [弹出框](./popover.md) |
| `Popconfirm` | 气泡确认框 | `EU_CreatePopconfirm` | 已完成：12 方位 / 自定义按钮 / 图标 / 结果回调 | [气泡确认框](./popconfirm.md) |
