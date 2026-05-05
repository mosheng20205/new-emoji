# Tree 树 🌳

## 简介

`Tree` 是纯 D2D 绘制的树形组件。当前状态：**高级 JSON 全样式完成**。

推荐公共 API 已切换为 UTF-8 JSON 字节集：支持嵌套 children、props 字段映射、复选框级联/半选、严格勾选、懒加载、叶子节点、默认展开/勾选、禁用节点、按 key 读写、追加/更新/删除、过滤、手风琴、自定义桌面节点模板和拖拽。

旧版扁平项目 API 仍保留为兼容接口。

## JSON 数据模型

```json
{
  "props": {"label": "name", "children": "zones", "isLeaf": "leaf"},
  "defaultExpandedKeys": ["root"],
  "defaultCheckedKeys": ["task-tree"],
  "currentKey": "task-tree",
  "filterText": "配置",
  "data": [
    {
      "key": "root",
      "name": "📦 项目资源",
      "icon": "📦",
      "tag": "主目录",
      "actions": "查看|新增",
      "zones": [
        {"key": "task-tree", "name": "🌳 Tree 高级样式", "leaf": true},
        {"key": "locked", "name": "🔒 禁用节点", "leaf": true, "disabled": true},
        {"key": "remote", "name": "⏳ 懒加载目录", "lazy": true, "leaf": false}
      ]
    }
  ]
}
```

节点字段：`key`、`label`、`children`、`disabled`、`leaf`、`checked`、`expanded`、`icon`、`tag`、`actions`、`lazy`。
字段映射：`props.label`、`props.children`、`props.disabled`、`props.isLeaf` 可把业务字段映射到组件字段。

## JSON API

| API | 说明 |
|---|---|
| `EU_SetTreeDataJson` / `EU_GetTreeDataJson` | 设置/读取完整嵌套树 JSON |
| `EU_SetTreeOptionsJson` / `EU_GetTreeStateJson` | 设置高级选项，读取状态 JSON |
| `EU_SetTreeCheckedKeysJson` / `EU_GetTreeCheckedKeysJson` | 按 key 设置/读取勾选节点 |
| `EU_SetTreeExpandedKeysJson` / `EU_GetTreeExpandedKeysJson` | 按 key 设置/读取展开节点 |
| `EU_AppendTreeNodeJson` | 向指定 parentKey 追加 JSON 节点；parentKey 为空时追加根节点 |
| `EU_UpdateTreeNodeJson` | 按 key 更新节点 |
| `EU_RemoveTreeNodeByKey` | 按 key 删除节点及子树 |
| `EU_SetTreeNodeEventCallback` | 节点点击、勾选、展开/折叠事件 |
| `EU_SetTreeLazyLoadCallback` | 懒加载展开请求事件 |
| `EU_SetTreeDragCallback` | 拖拽完成事件 |
| `EU_SetTreeAllowDragCallback` / `EU_SetTreeAllowDropCallback` | 拖拽/放置允许规则 |

高级选项字段：`showCheckbox`、`keyboardNavigation`、`lazy`/`lazyMode`、`checkStrictly`、`accordion`、`expandOnClickNode`、`highlightCurrent`、`checkOnClickNode`、`draggable`、`showActions`、`filterText`。

状态 JSON 包含：`currentKey`、`visibleCount`、`checkedKeys`、`halfCheckedKeys`、`expandedKeys`、`lastLazyIndex`、`lastLazyKey`、`dragEventCount` 等。

## 兼容 API

`EU_CreateTree`、`EU_SetTreeItems`、`EU_SetTreeSelected`、`EU_SetTreeOptions`、`EU_SetTreeItemExpanded`、`EU_SetTreeItemChecked`、`EU_SetTreeItemLazy` 等旧扁平接口继续可用，适合已有易语言项目平滑迁移；新功能和文档示例统一使用 JSON API。

## Python 使用

```python
import sys
sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🌳 Tree JSON 示例", 240, 120, 900, 620)
root = ui.create_container(hwnd, 0, 0, 0, 860, 560)

tree_id = ui.create_tree_json(
    hwnd, root,
    {
        "data": [
            {"key": "root", "label": "📦 项目", "expanded": True, "children": [
                {"key": "task", "label": "🌳 树组件", "leaf": True, "tag": "进行中"}
            ]}
        ],
        "defaultCheckedKeys": ["task"]
    },
    options={"showCheckbox": True, "draggable": True, "showActions": True},
    x=24, y=24, w=420, h=320,
)

print(ui.get_tree_state_json(hwnd, tree_id))
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 测试与图库

- 专项测试：`tests/python/test_tree_complete_components.py`
- 图库页：`component_gallery.py` 的 `Tree` 专属演示页，覆盖基础嵌套、props、复选/半选、懒加载、叶子节点、默认 keys、禁用、key 读写、追加删除、过滤、手风琴、拖拽和自定义节点模板。
