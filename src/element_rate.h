#pragma once
#include "element_base.h"

class Rate : public Element {
public:
    int max_value = 5;
    int value = 0;
    int value_x2 = 0;
    bool allow_clear = true;
    bool allow_half = false;
    bool readonly = false;
    bool show_score_text = true;
    std::wstring low_text = L"\u5f85\u8bc4\u5206";
    std::wstring high_text = L"\u5df2\u8bc4\u5206";
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Rate"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_max_value(int max_v);
    void set_value(int new_value);
    void set_value_x2(int new_value_x2);
    void set_options(bool allow_clear_value, bool allow_half_value, bool readonly_value);
    void set_texts(const std::wstring& low, const std::wstring& high, bool show_score);

private:
    int m_hover_value = 0;
    int m_press_value = 0;
    int m_hover_value_x2 = 0;
    int m_press_value_x2 = 0;

    float label_width() const;
    float star_size() const;
    int value_x2_at(int x, int y) const;
    void notify_changed();
};
