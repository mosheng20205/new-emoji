---
name: new-emoji-ai-sdk
description: Use when building UI with new_emoji.dll from AI clients or generating examples for 易语言, 火山, C#, or Python. Covers the single-HWND Direct2D architecture, EU_ DLL exports, UTF-8 byte-array text rules, Chinese + emoji UI requirements, DPI first-window sizing, and language-specific binding entrypoints.
---

# new_emoji AI SDK

## Workflow

1. Identify the target language first: 易语言, 火山, C#, or Python.
2. Read `AI_USAGE.md` for shared rules and the language-specific entrypoint.
3. Use `docs/ai/api_manifest.full.json` to find components and DLL exports.
4. Read the component page in `docs/components/` only when a component needs details.
5. Start from `examples/templates/` when generating a new UI.
6. Keep all visible UI copy in Chinese and include emoji in the window title, primary action, and core display items.
7. Size the first window and root container so all first-screen controls fit with at least 20 logical px of margin.

## Language Entrypoints

- 易语言: use `DLL命令/易语言DLL命令.md` and `docs/ai/e-language-encoding.md`. Do not put emoji or special Unicode directly in 易语言 source. Pass UTF-8 byte arrays with lengths.
- 火山: use `examples/火山/src/new_emoji_接口.wsv` and `examples/火山/README.md`.
- C#: use `DLL命令/CSharp DLL命令.md` and `examples/Csharp/MinimalExample.cs`; P/Invoke must use `CallingConvention.StdCall`.
- Python: use `examples/python/new_emoji_ui.py`; do not write raw ctypes for normal examples.

## Component Choice

- Text display: `Text`, `Tag`, `Descriptions`, `Statistic`.
- Main actions: `Button`; toolbar actions: `IconButton`.
- Form input: prefer `Input`; keep `EditBox` only for compatibility examples.
- Table and data management: `Table`, `Pagination`, `Dialog`, `MessageBox`.
- Browser shell UI: `WindowFrame`, `Tabs`, `IconButton`, `Omnibox`, `BrowserViewport`.
- Feedback: `Message`, `Notification`, `Alert`, `Loading`, `Dialog`, `Drawer`.

## Hard Rules

- Do not rename or invent `EU_` exports.
- Do not mix GDI child controls into new UI examples.
- Do not leave English user-facing text in examples unless it is an API name.
- For 易语言, never write literal emoji strings such as `"🚀"` or `"✅"` in source; use UTF-8 byte sets and length parameters.
- When API or component docs change, keep `docs/components/`, `DLL命令/`, `examples/python/new_emoji_ui.py`, and `docs/ai/api_manifest.full.json` in sync.
