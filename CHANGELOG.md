# 更新日志

本文档记录 `new_emoji` 的公开变化。版本号可在正式发布前按实际策略调整。

## Unreleased

- 新增开源文档结构：根目录 `README.md`、`docs/` 文档总览、组件导航、API 索引和 81 个组件独立文档。
- 新增 `tools/generate_docs.py`，用于从 `组件封装计划.md` 和 `new_emoji.def` 生成组件文档与 API 索引。
- 新增 `CONTRIBUTING.md`，说明构建、测试、组件 API 与文档同步要求。
- 更新 `AGENTS.md`，明确组件 API 变化时必须同步更新对应组件文档、组件导航、API 索引、Python helper 和易语言 DLL 命令文档。

## v0.1.0

- 计划内 81 个 Element 组件完成封装。
- Win32 / x64 Release 构建通过。
- 组件级 Python UI 验证使用中文文案和 emoji，并覆盖首次窗口尺寸适配要求。
