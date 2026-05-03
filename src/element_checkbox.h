#pragma once
#include "element_base.h"
#include "theme.h"

class Checkbox : public Element {
public:
    bool checked = false;
    bool indeterminate = false;

    const wchar_t* type_name() const override { return L"Checkbox"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_checked(bool value);
    void set_indeterminate(bool value);
    void toggle();
private:
    bool key_armed = false;
};
