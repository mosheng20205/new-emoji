#pragma once
#include "element_base.h"
#include <vector>

struct AutocompleteSuggestion {
    std::wstring title;
    std::wstring subtitle;
    std::wstring value;
};

class Autocomplete : public Element {
public:
    std::vector<AutocompleteSuggestion> suggestions;
    std::wstring value;
    std::wstring placeholder = L"请输入内容";
    std::wstring prefix_icon;
    std::wstring suffix_icon;
    int selected_index = -1;
    bool open = false;
    bool trigger_on_focus = true;
    bool async_loading = false;
    int async_request_id = 0;
    std::wstring empty_text = L"🫥 没有匹配建议";

    const wchar_t* type_name() const override { return L"Autocomplete"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    bool accepts_input() const override { return enabled && m_click_callback_armed; }
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_suggestions(const std::vector<AutocompleteSuggestion>& values);
    void set_value(const std::wstring& next_value);
    void set_selected_index(int index);
    void set_open(bool next_open);
    void set_async_state(bool loading, int request_id);
    void set_placeholder(const std::wstring& text);
    void set_icons(const std::wstring& next_prefix_icon, const std::wstring& next_suffix_icon);
    void set_behavior(bool next_trigger_on_focus);
    void set_empty_text(const std::wstring& text);
    bool is_open() const;
    int suggestion_count() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartSuffixIcon,
        PartOption
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    Part m_press_part = PartNone;
    bool m_click_callback_armed = false;
    bool m_replace_on_next_char = false;

    Rect suffix_icon_rect() const;
    float left_padding() const;
    float right_padding() const;
    int row_height() const;
    int display_count() const;
    int menu_height() const;
    int menu_y() const;
    int option_at(int x, int y) const;
    Part part_at(int x, int y, int* option_index = nullptr) const;
    const AutocompleteSuggestion* selected_suggestion() const;
};
