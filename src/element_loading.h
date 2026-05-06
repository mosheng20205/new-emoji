#pragma once
#include "element_base.h"

class Loading : public Element {
public:
    bool active = true;
    bool fullscreen = false;
    bool lock_input = false;
    bool service_owned = false;
    Color overlay_color = 0;
    Color spinner_color = 0;
    Color text_color = 0;
    int spinner_type = 0; // 0 dots, 1 arc, 2 pulse
    int progress = -1;
    int target_id = 0;
    int target_padding = 0;
    int animation_angle = 0;
    int tick_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 timer

    ~Loading() override;

    const wchar_t* type_name() const override { return L"Loading"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    bool accepts_input() const override { return active && lock_input; }

    void set_active(bool value);
    void set_options(bool value, bool full, int percent);
    void set_style(Color overlay, Color spinner, Color text, int spinner_kind, bool lock);
    void set_target(int id, int padding);
    void tick(int elapsed_ms);
    bool timer_running() const { return m_timer_id != 0; }

private:
    UINT_PTR m_timer_id = 0;

    void ensure_timer();
    void stop_timer();
};
