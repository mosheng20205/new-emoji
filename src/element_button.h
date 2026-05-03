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
    int variant = 0; // 0 default, 1 primary, 2 success, 3 warning, 4 danger, 5 text, 6 info
    bool plain = false;
    bool round = false;
    bool circle = false;
    bool loading = false;
    int size = 0; // 0 default, 1 medium, 2 small, 3 mini
    int animation_angle = 0;
    int tick_count = 0;
    bool keyboard_armed = false;

    ~Button() override;

    const wchar_t* type_name() const override { return L"Button"; }
    bool accepts_input() const override { return enabled && !loading; }
    void paint(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;
    void set_variant(int value);
    void set_options(int variant_value, int plain_value, int round_value,
                     int circle_value, int loading_value, int size_value);
    void tick(int elapsed_ms);

private:
    UINT_PTR m_timer_id = 0;

    void set_loading(bool value);
    void ensure_timer();
    void stop_timer();
};
