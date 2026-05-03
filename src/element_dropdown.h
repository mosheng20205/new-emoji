#pragma once
#include "element_base.h"
#include <vector>

class Dropdown : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<std::wstring> display_items;
    std::vector<int> item_levels;
    std::vector<bool> disabled_items;
    int selected_index = -1;
    bool open = false;

    const wchar_t* type_name() const override { return L"Dropdown"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
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
    bool is_open() const;
    int item_count() const;
    int disabled_count() const;
    int selected_level() const;
    int hover_index() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartItem
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    Part m_press_part = PartNone;
    int m_scroll = 0;

    int row_height() const;
    int visible_row_count() const;
    int menu_width() const;
    int menu_height() const;
    int menu_y() const;
    int item_at(int x, int y) const;
    bool is_disabled(int index) const;
    bool has_child(int index) const;
    void clamp_scroll();
    void ensure_selected_visible();
    int next_enabled_index(int start, int delta) const;
    Part part_at(int x, int y, int* item_index = nullptr) const;
};
