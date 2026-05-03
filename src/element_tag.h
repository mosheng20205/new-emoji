#pragma once
#include "element_base.h"

class Tag : public Element {
public:
    int tag_type = 0;
    int effect = 0;
    bool closable = false;
    bool closed = false;
    int size_preset = 1;
    Color theme_color = 0;
    ElementClickCallback close_cb = nullptr;

    const wchar_t* type_name() const override { return L"Tag"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_type(int value);
    void set_effect(int value);
    void set_closable(bool value);
    void set_closed(bool value);
    void set_size_preset(int value);
    void set_theme_color(Color value);

private:
    bool m_close_hover = false;
    bool m_close_down = false;

    Rect close_rect() const;
    bool close_hit(int x, int y) const;
};
