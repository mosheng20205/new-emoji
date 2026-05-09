#pragma once
#include "element_base.h"

class Skeleton : public Element {
public:
    int rows = 3;
    bool animated = true;
    bool loading = true;
    bool show_avatar = true;
    float animation_phase = 0.0f;
    unsigned long long last_animation_tick = 0;

    ~Skeleton() override;

    const wchar_t* type_name() const override { return L"Skeleton"; }
    void paint(RenderContext& ctx) override;

    void set_rows(int value);
    void set_animated(bool value);
    void set_options(int rows_value, bool animated_value, bool loading_value, bool show_avatar_value);
    void set_loading(bool value);
    void tick(int elapsed_ms);

private:
    UINT_PTR m_timer_id = 0;

    void ensure_timer();
    void stop_timer();
};
