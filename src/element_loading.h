#pragma once
#include "element_base.h"

class Loading : public Element {
public:
    bool active = true;
    bool fullscreen = false;
    int progress = -1;
    int target_id = 0;
    int target_padding = 0;
    int animation_angle = 0;
    int tick_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 timer

    ~Loading() override;

    const wchar_t* type_name() const override { return L"Loading"; }
    void paint(RenderContext& ctx) override;

    void set_active(bool value);
    void set_options(bool value, bool full, int percent);
    void set_target(int id, int padding);
    void tick(int elapsed_ms);
    bool timer_running() const { return m_timer_id != 0; }

private:
    UINT_PTR m_timer_id = 0;

    void ensure_timer();
    void stop_timer();
};
