#pragma once
#include "element_base.h"

class Backtop : public Element {
public:
    int scroll_position = 0;
    int threshold = 200;
    int target_position = 0;
    int container_id = 0;
    int duration_ms = 240;
    int last_scroll_before_jump = 0;
    int activated_count = 0;

    const wchar_t* type_name() const override { return L"Backtop"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_leave() override;
    void on_key_down(int vk, int mods) override;

    void set_state(int scroll, int show_threshold, int target);
    void set_options(int scroll, int show_threshold, int target, int target_container_id, int duration);
    void set_scroll_position(int scroll);
    void trigger_backtop();
    int is_shown() const;
};
