#pragma once
#include "element_base.h"
#include "theme.h"

class Radio : public Element {
public:
    bool checked = false;
    std::wstring group_name;

    const wchar_t* type_name() const override { return L"Radio"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_checked(bool value);
    void set_group_name(const std::wstring& value);
    void select_relative(int delta);

private:
    bool key_armed = false;
};
