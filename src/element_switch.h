#pragma once
#include "element_base.h"
#include "theme.h"

class Switch : public Element {
public:
    bool checked = false;
    bool loading = false;
    int value = 0;
    int active_value = 1;
    int inactive_value = 0;
    Color active_color = 0;
    Color inactive_color = 0;
    int size = 0;
    std::wstring active_text;
    std::wstring inactive_text;

    const wchar_t* type_name() const override { return L"Switch"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_checked(bool val);
    void set_loading(bool val);
    void set_value(int v);
    int get_value() const;
    void set_active_color(Color c);
    void set_inactive_color(Color c);
    void set_size(int sz);
    void set_texts(const std::wstring& active, const std::wstring& inactive);
private:
    bool key_armed = false;
};
