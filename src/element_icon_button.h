#pragma once
#include "element_base.h"

class IconButton : public Element {
public:
    std::wstring icon;
    std::wstring tooltip;
    std::wstring badge_text;
    bool badge_visible = false;
    bool checked = false;
    int dropdown_element_id = 0;
    bool suppress_tooltip_until_leave = false;

    Color normal_bg = 0x00000000;
    Color hover_bg = 0x1A000000;
    Color pressed_bg = 0x26000000;
    Color checked_bg = 0x22000000;
    Color disabled_bg = 0x00000000;
    Color icon_color = 0;
    Color disabled_icon_color = 0;
    int shape = 1; // 0 rounded rect, 1 circle, 2 pill
    int icon_size = 18;

    const wchar_t* type_name() const override { return L"IconButton"; }
    bool accepts_input() const override { return enabled; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_colors(Color normal, Color hover, Color press, Color checked_color,
                    Color disabled, Color icon, Color disabled_icon);
    void set_shape(int next_shape, int radius);
    void set_padding(int left, int top, int right, int bottom);
    void set_icon_size(int size);
    void suppress_tooltip_once();

private:
    bool keyboard_armed = false;
};
