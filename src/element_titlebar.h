#pragma once
#include "element_base.h"

class TitleBar : public Element {
public:
    float dpi_scale = 1.0f;
    Color bg_color = 0xFF181825;
    Color text_color = 0xFFCDD6F4;

    const wchar_t* type_name() const override { return L"TitleBar"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    bool hit_test_button(int x, int y) const;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;

private:
    enum Btn { None = 0, Minimize, Maximize, Close };
    Btn m_hover_btn = None;
    Btn m_press_btn = None;

    int  btn_w()  const { return (int)(46.0f * dpi_scale); }
    int  btn_h()  const { return bounds.h; }
    int  corner_safe_inset() const;
    void get_btn_rect(Btn b, int& x, int& y, int& w, int& h) const;
    Btn  button_at(int x, int y) const;
    void draw_minimize(RenderContext& ctx, int x, int y, int w, int h, Color c);
    void draw_maximize(RenderContext& ctx, int x, int y, int w, int h, Color c);
    void draw_restore(RenderContext& ctx, int x, int y, int w, int h, Color c);
    void draw_close(RenderContext& ctx, int x, int y, int w, int h, Color c);
};
