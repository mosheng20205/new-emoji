# TreeSelect 树选择 🌲

## 简介

`TreeSelect` 是 Tree 数据模型 + 下拉选择器组合而成的高级组件。当前状态：**高级 JSON 全样式完成**。

推荐公共 API 使用 UTF-8 JSON 字节集，和 `Tree` 共享节点模型，并额外支持单选/多选值、搜索值、弹层开关、清空选择和选中 keys 读回。旧扁平索引 API 保留为兼容接口。

## JSON 数据模型

TreeSelect 使用与 Tree 相同的节点字段：`key`、`label`、`children`、`disabled`、`leaf`、`checked`、`expanded`、`icon`、`tag`、`actions`、`lazy`，并支持 `props` 字段映射。

```json
{
  "props": {"label": "name", "children": "zones", "isLeaf": "leaf"},
  "defaultExpandedKeys": ["dept"],
  "defaultCheckedKeys": ["rd"],
  "currentKey": "rd",
  "data": [
    {
      "key": "dept",
      "name": "🏢 部门目录",
      "zones": [
        {"key": "rd", "name": "👩‍💻 研发中心", "leaf": true},
        {"key": "ops", "name": "🔒 运维中心", "leaf": true, "disabled": true},
        {"key": "remote", "name": "⏳ 远程成员", "lazy": true, "leaf": false}
      ]
    }
  ]
}
```

## JSON API

| API | 说明 |
|---|---|
| `EU_SetTreeSelectDataJson` / `EU_GetTreeSelectDataJson` | 设置/读取完整下拉树 JSON |
| `EU_SetTreeSelectOptionsJson` / `EU_GetTreeSelectStateJson` | 设置高级选项，读取弹层与选择状态 |
| `EU_SetTreeSelectSelectedKeysJson` / `EU_GetTreeSelectSelectedKeysJson` | 按 key 设置/读取选中值 |
| `EU_SetTreeSelectExpandedKeysJson` / `EU_GetTreeSelectExpandedKeysJson` | 按 key 设置/读取展开节点 |
| `EU_AppendTreeSelectNodeJson` | 向指定 parentKey 追加节点 |
| `EU_UpdateTreeSelectNodeJson` | 按 key 更新节点 |
| `EU_RemoveTreeSelectNodeByKey` | 按 key 删除节点及子树 |
| `EU_SetTreeSelectNodeEventCallback` | 节点选择、展开/折叠事件 |
| `EU_SetTreeSelectLazyLoadCallback` | 懒加载展开请求事件 |
| `EU_SetTreeSelectDragCallback` | 拖拽完成事件 |
| `EU_SetTreeSelectAllowDragCallback` / `EU_SetTreeSelectAllowDropCallback` | 拖拽/放置允许规则 |

高级选项字段：`multiple`、`clearable`、`searchable`、`open`、`searchText`、`checkStrictly`、`accordion`、`draggable`、`showActions`。

状态 JSON 包含：`selectedIndex`、`selectedKeys`、`expandedKeys`、`open`、`multiple`、`clearable`、`searchable`、`searchText`、`matchedCount`、`lastLazyIndex`、`dragEventCount`。

## 兼容 API

`EU_CreateTreeSelect`、`EU_SetTreeSelectItems`、`EU_SetTreeSelectSelected`、`EU_SetTreeSelectOpen`、`EU_SetTreeSelectOptions`、`EU_SetTreeSelectSearch`、`EU_ClearTreeSelect`、`EU_SetTreeSelectSelectedItems` 等旧接口继续可用。

## Python 使用

```python
import sys
sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🌲 TreeSelect JSON 示例", 240, 120, 900, 620)
root = ui.create_container(hwnd, 0, 0, 0, 860, 560)

select_id = ui.create_tree_select_json(
    hwnd, root,
    {
        "data": [
            {"key": "dept", "label": "🏢 部门", "expanded": True, "children": [
                {"key": "rd", "label": "👩‍💻 研发中心", "leaf": True}
            ]}
        ],
        "defaultCheckedKeys": ["rd"]
    },
    options={"multiple": True, "clearable": True, "searchable": True, "open": True},
    selected_keys=["rd"],
    x=24, y=24, w=360, h=40,
)

print(ui.get_tree_select_state_json(hwnd, select_id))
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 测试与图库

- 专项测试：`tests/python/test_treeselect_complete_components.py`
- 图库页：`component_gallery.py` 的 `TreeSelect` 专属演示页，覆盖单选、多选、清空、搜索、弹层状态、props、懒加载、禁用节点、自定义节点模板和按 key 读写。
