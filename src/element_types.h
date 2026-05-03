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
typedef void (__stdcall *WindowResizeCallback)(HWND hwnd, int width, int height);
typedef void (__stdcall *WindowCloseCallback)(HWND hwnd);
typedef void (__stdcall *WindowDestroyCallback)(HWND hwnd);
typedef void (__stdcall *MessageBoxResultCallback)(int messagebox_id, int result);
