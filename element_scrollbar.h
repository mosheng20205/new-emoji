#pragma once
#include "element_base.h"

class Scrollbar : public Element {
public:
    int value = 0;
    int max_value = 100;
    int page_size = 20;
    int orientation = 1; // 0 horizontal, 1 vertical
    bool auto_hide = false;
    int wheel_step = 20;
    int bound_element_id = 0;
    int content_size = 0;
    int viewport_size = 0;
    int content_offset = 0;
    int wheel_event_count = 0;
    int drag_event_count = 0;
    int change_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 api scroll, 3 wheel, 4 drag, 5 track, 6 bind, 7 key
    int last_wheel_delta = 0;
    Rect bound_base = {};
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Scrollbar"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;

    void set_value(int new_value);
    void set_max_value(int new_max);
    void set_range(int new_max, int new_page_size);
    void set_orientation(int value);
    void set_options(int new_max, int new_page_size, int new_orientation, int auto_hide_enabled);
    void set_wheel_step(int step);
    void scroll_delta(int delta);
    void bind_content(int element_id, const Rect& base, int new_content_size, int new_viewport_size);
    void wheel_delta(int delta);

private:
    int m_drag_offset = 0;
    int m_drag_start_value = 0;

    int clamp_value(int candidate) const;
    Rect track_rect() const;
    Rect thumb_rect() const;
    void update_value(int new_value, int action);
    void update_from_point(int x, int y);
    void apply_binding();
};
