#pragma once
#include "element_base.h"

class Skeleton : public Element {
public:
    int rows = 3;
    bool animated = true;
    bool loading = true;
    bool show_avatar = true;
    unsigned long long last_animation_tick = 0;

    const wchar_t* type_name() const override { return L"Skeleton"; }
    void paint(RenderContext& ctx) override;

    void set_rows(int value);
    void set_animated(bool value);
    void set_options(int rows_value, bool animated_value, bool loading_value, bool show_avatar_value);
    void set_loading(bool value);
};
