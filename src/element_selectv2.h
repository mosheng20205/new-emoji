#pragma once
#include "element_base.h"
#include <set>
#include <vector>

class SelectV2 : public Element {
public:
    std::vector<std::wstring> options;
    int selected_index = -1;
    bool open = false;
    int visible_count = 7;
    std::wstring search_text;
    std::set<int> disabled_indices;
    int option_alignment = 0;
    int value_alignment = 0;
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"SelectV2"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_blur() override;

    void set_options(const std::vector<std::wstring>& values);
    void set_selected_index(int index);
    void set_visible_count(int count);
    void set_open(bool is_open);
    void set_search_text(const std::wstring& value);
    void set_option_disabled(int index, bool disabled);
    void set_option_alignment(int alignment);
    void set_value_alignment(int alignment);
    void set_scroll_index(int index);
    void scroll_by(int delta_rows);
    int option_count() const;
    int matched_count() const;
    bool is_option_disabled(int index) const;
    int scroll_index() const { return m_scroll_index; }

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    int m_scroll_index = 0;
    Part m_press_part = PartNone;

    int option_height() const;
    int menu_height() const;
    int menu_y() const;
    int option_at(int x, int y) const;
    Part part_at(int x, int y, int* option_index = nullptr) const;
    std::wstring selected_text() const;
    std::vector<int> visible_indices() const;
    void select_relative(int delta);
    void select_first_or_last(bool last);
    void ensure_selected_visible();
    void notify_changed();
};
