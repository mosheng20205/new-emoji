#pragma once
#include "element_base.h"
#include <set>
#include <vector>

class Select : public Element {
public:
    std::vector<std::wstring> options;
    int selected_index = -1;
    bool open = false;
    std::wstring placeholder = L"请选择";
    std::wstring search_text;
    std::set<int> disabled_indices;
    bool multiple = false;
    std::set<int> selected_indices;
    int option_alignment = 0;
    int value_alignment = 0;
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Select"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_blur() override;

    void set_options(const std::vector<std::wstring>& values);
    void set_selected_index(int index);
    void set_open(bool is_open);
    void set_search_text(const std::wstring& value);
    void set_placeholder(const std::wstring& value);
    void set_option_disabled(int index, bool disabled);
    void set_option_alignment(int alignment);
    void set_value_alignment(int alignment);
    void set_multiple(bool enabled);
    void set_selected_indices(const std::vector<int>& indices);
    void toggle_index(int index);
    int option_count() const;
    int matched_count() const;
    bool is_option_disabled(int index) const;
    int selected_count() const;
    int selected_at(int position) const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    int m_hover_index = -1;
    int m_press_index = -1;
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
    void paint_dropdown(RenderContext& ctx);
    void notify_changed();
};
