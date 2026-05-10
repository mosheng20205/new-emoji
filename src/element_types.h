#pragma once
#include <cstdint>
#include <string>
#include <windows.h>

// ── Color: ARGB 0xAARRGGBB ──────────────────────────────────────────
using Color = uint32_t;

// ── Rectangle (device pixels) ────────────────────────────────────────
struct Rect {
    int x = 0, y = 0, w = 0, h = 0;
    bool contains(int px, int py) const {
        return px >= x && px < x + w && py >= y && py < y + h;
    }
    int right()  const { return x + w; }
    int bottom() const { return y + h; }
};

// ── Mouse ────────────────────────────────────────────────────────────
enum class MouseButton { Left = 0, Middle = 1, Right = 2 };

struct MouseEvent {
    int x = 0, y = 0;
    MouseButton button = MouseButton::Left;
    bool ctrl = false, shift = false, alt = false;
};

// ── Keyboard modifiers ───────────────────────────────────────────────
namespace KeyMod {
    constexpr int Shift   = 1;
    constexpr int Control = 2;
    constexpr int Alt     = 4;
}

// ── Element style ────────────────────────────────────────────────────
struct ElementStyle {
    Color bg_color      = 0;           // 0 = transparent / inherit
    Color fg_color      = 0xFFFFFFFF;  // text color
    Color border_color  = 0;
    float border_width  = 0.0f;
    float corner_radius = 0.0f;
    int pad_left = 6, pad_top = 4, pad_right = 6, pad_bottom = 4;
    std::wstring font_name = L"Microsoft YaHei UI";
    float font_size = 14.0f;
};

// ── Callback typedefs (C linkage, __stdcall) ─────────────────────────
typedef void (__stdcall *ElementClickCallback)(int element_id);
typedef void (__stdcall *ElementKeyCallback)(int element_id, int vk_code, int key_down, int shift, int ctrl, int alt);
typedef void (__stdcall *ElementTextCallback)(int element_id, const unsigned char* utf8, int len);
typedef void (__stdcall *ElementValueCallback)(int element_id, int value, int range_start, int range_end);
typedef void (__stdcall *ElementReorderCallback)(int element_id, int from_index, int to_index, int count);
typedef int  (__stdcall *ElementBeforeCloseCallback)(int element_id, int action);
typedef int  (__stdcall *DateDisabledCallback)(int element_id, int yyyymmdd);
typedef void (__stdcall *TableCellCallback)(int table_id, int row, int col, int action, int value);
typedef void (__stdcall *TableCellEditCallback)(int table_id, int row, int col, int action,
                                                const unsigned char* utf8, int len);
typedef int  (__stdcall *TableVirtualRowCallback)(int table_id, int row, unsigned char* buffer, int buffer_size);
typedef void (__stdcall *DropdownCommandCallback)(int element_id, int item_index,
                                                 const unsigned char* command_utf8, int command_len);
typedef void (__stdcall *MenuSelectCallback)(int element_id, int item_index,
                                             const unsigned char* path_utf8, int path_len,
                                             const unsigned char* command_utf8, int command_len);
typedef void (__stdcall *WindowResizeCallback)(HWND hwnd, int width, int height);
typedef void (__stdcall *WindowCloseCallback)(HWND hwnd);
typedef void (__stdcall *WindowDestroyCallback)(HWND hwnd);
typedef void (__stdcall *MessageBoxResultCallback)(int messagebox_id, int result);
typedef void (__stdcall *MessageBoxExCallback)(int messagebox_id, int action,
                                               const unsigned char* value_utf8, int value_len);
typedef void (__stdcall *TreeNodeEventCallback)(int element_id, int event_code, int item_index,
                                                const unsigned char* payload_utf8, int payload_len);
typedef int  (__stdcall *TreeNodeAllowDragCallback)(int element_id,
                                                    const unsigned char* key_utf8, int key_len);
typedef int  (__stdcall *TreeNodeAllowDropCallback)(int element_id,
                                                    const unsigned char* drag_key_utf8, int drag_key_len,
                                                    const unsigned char* drop_key_utf8, int drop_key_len,
                                                    int drop_type);
