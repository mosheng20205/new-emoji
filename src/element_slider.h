#pragma once
#include "element_base.h"
#include "theme.h"

class Slider : public Element {
public:
    int min_value = 0;
    int max_value = 100;
    int value = 0;
    int step = 1;
    bool show_tooltip = false;
    bool range_mode = false;
    int range_start = 0;
    int range_end = 0;
    ElementValueCallback value_cb = nullptr;

    const wchar_t* type_name() const override { return L"Slider"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_key_down(int vk, int mods) override;

    void set_range(int min_v, int max_v);
    void set_value(int new_value);
    void set_range_value(int start_value, int end_value);
    void set_range_mode(bool enabled, int start_value, int end_value);
    void set_options(int new_step, bool tooltip);

private:
    int active_thumb = 0;
    int clamp_value(int v) const;
    int snap_value(int v) const;
    float value_to_x(int v, float track_left, float track_w) const;
    int value_from_local_x(int x) const;
    void update_from_local_x(int x);
    void notify_value_changed();
};
