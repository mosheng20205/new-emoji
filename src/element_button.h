#pragma once
#include "element_base.h"

class Button : public Element {
public:
    std::wstring emoji;              // Emoji displayed before text
    Color hover_bg     = 0;
    Color hover_border = 0;
    Color hover_fg     = 0;
    Color press_bg     = 0;
    Color press_border = 0;
    Color press_fg     = 0;
    int variant = 0; // 0 default, 1 primary, 2 success, 3 warning, 4 danger, 5 text
    bool keyboard_armed = false;

    const wchar_t* type_name() const override { return L"Button"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;
    void set_variant(int value);
};
