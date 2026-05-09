#pragma once
#include "element_base.h"
#include <vector>

class Dropdown : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<std::wstring> display_items;
    std::vector<int> item_levels;
    std::vector<bool> disabled_items;
    std::vector<std::wstring> item_icons;
    std::vector<std::wstring> item_commands;
    std::vector<bool> divided_items;
    std::vector<bool> marker_disabled_items;
    int selected_index = -1;
    bool open = false;
    int trigger_mode = 0;   // 0 click, 1 hover, 2 manual
    int trigger_style = 0;  // 0 button, 1 text link
    int button_variant = 0; // Button variant values
    int size = 0;           // 0 default, 1 medium, 2 small, 3 mini
    bool split_button = false;
    bool hide_on_click = true;
    int popup_anchor_element_id = 0;
    int popup_placement = 4;
    int popup_offset = 8;
    int popup_offset_x = 0;
    int popup_offset_y = 0;
    bool popup_anchor_point_active = false;
    int popup_anchor_point_x = 0;
    int popup_anchor_point_y = 0;
    bool popup_close_on_outside = true;
    bool popup_close_on_escape = true;
    ElementClickCallback main_click_cb = nullptr;
    DropdownCommandCallback command_cb = nullptr;

    const wchar_t* type_name() const override { return L"Dropdown"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_enter() override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_items(const std::vector<std::wstring>& values);
    void set_selected_index(int index);
    void set_open(bool next_open);
    void set_disabled_indices(const std::vector<int>& indices);
    void set_options(int next_trigger_mode, int next_hide_on_click, int next_split_button,
                     int next_button_variant, int next_size, int next_trigger_style);
    void set_item_meta(const std::vector<std::wstring>& icons,
                       const std::vector<std::wstring>& commands,
                       const std::vector<int>& divided_indices);
    const std::wstring& item_icon(int index) const;
    const std::wstring& item_command(int index) const;
    bool is_divided(int index) const;
    bool is_open() const;
    void set_popup_anchor(int anchor_id);
    void set_popup_anchor_point(int absolute_x, int absolute_y);
    void set_popup_placement(int placement, int offset_x, int offset_y);
    void set_popup_dismiss_behavior(bool close_on_outside, bool close_on_escape);
    Rect popup_rect() const;
    int item_count() const;
    int disabled_count() const;
    int selected_level() const;
    int hover_index() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartSplitMain,
        PartSplitArrow,
        PartItem
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    std::vector<int> m_runtime_disabled_indices;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_scroll = 0;

    int row_height() const;
    int arrow_width() const;
    int split_arrow_width() const;
    int trigger_pad_x() const;
    float effective_font_size() const;
    int visible_row_count() const;
    int menu_width() const;
    int menu_height() const;
    int menu_x() const;
    int menu_y() const;
    int item_at(int x, int y) const;
    bool hover_bridge_contains(int x, int y) const;
    bool is_disabled(int index) const;
    bool has_child(int index) const;
    void clamp_scroll();
    void ensure_selected_visible();
    int next_enabled_index(int start, int delta) const;
    void resize_meta();
    void choose_item(int index);
    void fire_command(int index);
    Part part_at(int x, int y, int* item_index = nullptr) const;
};
