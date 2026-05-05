#pragma once
#include "element_base.h"
#include <vector>

struct Theme;

class Rate : public Element {
public:
    int max_value = 5;
    int value = 0;
    int value_x2 = 0;
    bool allow_clear = true;
    bool allow_half = false;
    bool readonly = false;
    bool show_score_text = true;
    bool show_text = false;
    bool show_score = false;
    Color low_color = 0;
    Color mid_color = 0;
    Color high_color = 0;
    Color score_text_color = 0;
    std::wstring full_icon = L"\u2605";
    std::wstring void_icon = L"\u2606";
    std::wstring low_icon;
    std::wstring mid_icon;
    std::wstring high_icon;
    std::wstring score_template = L"{value}";
    std::vector<std::wstring> text_items;
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
    void set_colors(Color low, Color mid, Color high);
    void set_icons(const std::wstring& full, const std::wstring& empty,
                   const std::wstring& low, const std::wstring& mid, const std::wstring& high);
    void set_text_items(const std::vector<std::wstring>& items);
    void set_display_options(bool next_show_text, bool next_show_score,
                             Color next_text_color, const std::wstring& next_score_template);
    Color active_color(const Theme* theme, int display_value_x2) const;
    std::wstring active_icon(int display_value_x2) const;
    std::wstring score_text() const;
    std::wstring item_text() const;

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
