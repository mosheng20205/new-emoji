# Statistic 统计数值

## 简介

`Statistic` 是用于突出单个或一组关键数字的纯 D2D 数据展示组件。当前状态：**已完成**。

已补齐普通数值、千分位、小数精度、小数分隔符、前后缀 emoji、前后缀独立颜色、自定义 formatter 文本、后缀点击、倒计时、暂停/继续、增加时间、结束回调、状态读回、Python 封装、易语言命令和 `component_gallery.py` 全样式演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateStatistic` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_statistic` |
| 易语言命令 | `DLL命令/易语言DLL命令.md` 中的“创建统计数值” |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateStatistic` | 创建统计数值组件 |
| `EU_SetStatisticValue` | 设置普通数值文本 |
| `EU_SetStatisticFormat` | 设置标题、前缀、后缀 |
| `EU_SetStatisticOptions` | 兼容旧接口：设置精度与动画 |
| `EU_GetStatisticOptions` | 兼容旧接口：读回精度与动画 |
| `EU_SetStatisticNumberOptions` | 设置精度、动画、千分位和小数分隔符 |
| `EU_SetStatisticAffixOptions` | 设置前后缀、前后缀颜色、数值颜色和后缀可点击 |
| `EU_SetStatisticDisplayText` | 设置 formatter 风格自定义文本，如 `456/2` |
| `EU_SetStatisticCountdown` | 切换倒计时模式，目标时间为毫秒级 Unix 时间戳 |
| `EU_SetStatisticCountdownState` | 暂停或继续倒计时 |
| `EU_AddStatisticCountdownTime` | 增加或减少倒计时毫秒数 |
| `EU_SetStatisticFinishCallback` | 设置倒计时结束回调 |
| `EU_SetStatisticSuffixClickCallback` | 设置后缀点击回调 |
| `EU_GetStatisticFullState` | 读回模式、精度、动画、暂停、结束、后缀点击次数和剩余毫秒 |

## Python 使用

```python
import time
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📊 统计数值示例", 240, 120, 980, 620)
root = ui.create_container(hwnd, 0, 0, 0, 940, 560)

stat = ui.create_statistic(hwnd, root, "📈 增长人数", "1314", "", " 人", 30, 40, 240, 120)
ui.set_statistic_number_options(hwnd, stat, precision=2, animated=True, group_separator=True)
ui.set_statistic_affix_options(hwnd, stat, "", " 人", suffix_color=0xFF67C23A, value_color=0xFF67C23A)

ratio = ui.create_statistic(hwnd, root, "👥 男女比", "0", "", "", 300, 40, 240, 120)
ui.set_statistic_display_text(hwnd, ratio, "456/2")

deadline = ui.create_statistic(hwnd, root, "🎉 商品降价", "0", "", " 抢购即将开始", 30, 200, 420, 120)
ui.set_statistic_countdown(hwnd, deadline, int(time.time() * 1000) + 8 * 60 * 60 * 1000)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 倒计时格式

| 格式 | 效果 |
|---|---|
| 空文本 | 默认中文时分秒，例如 `02小时15分钟08秒` |
| `HH:mm:ss` | 时分秒，例如 `06:30:00` |
| `DD天HH小时mm分钟` | 天、小时、分钟，例如 `18天06小时30分钟` |

倒计时结束回调只触发一次。调用 `EU_AddStatisticCountdownTime` 增加时间并重新进入未结束状态后，可以再次触发结束回调。

## component_gallery 演示

`examples/python/component_gallery.py` 的 `Statistic` 独立页面覆盖：

- `📈 增长人数`：千分位、小数精度、数字动画。
- `👥 男女比`：自定义 formatter 文本。
- `🚩 活跃金额`：前后缀 emoji 与独立颜色。
- `⭐ 用户反馈`：可点击后缀，切换收藏状态。
- `🎉 商品降价`、`🎮 时间游戏`、`🚩 距离立夏还有`、`📜 距离明日`：倒计时、格式化、增加 10 秒、暂停/继续、结束回调。

## 文档维护

修改 Statistic API 时，需要同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和 `component_gallery.py`。
