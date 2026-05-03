#pragma once
#include "element_base.h"
#include <vector>

class Menu : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<std::wstring> display_items;
    std::vector<int> item_levels;
    std::vector<bool> disabled_items;
    std::vector<bool> expanded_items;
    int active_index = 0;
    int orientation = 0; // 0 horizontal, 1 vertical

    const wchar_t* type_name() const override { return L"Menu"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_active_index(int index);
    void set_orientation(int value);
    void set_expanded_indices(const std::vector<int>& indices);
    int item_count() const;
    int visible_count() const;
    int expanded_count() const;
    int active_level() const;
    int hover_index() const;
    std::wstring active_path() const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    bool is_disabled(int index) const;
    bool has_child(int index) const;
    bool is_visible_item(int index) const;
    bool is_expanded(int index) const;
    int visible_position(int index) const;
    std::vector<int> visible_indices() const;
    int next_visible_enabled(int start, int delta) const;
    void toggle_expanded(int index);
    int item_at(int x, int y) const;
    Rect item_rect(int index) const;
};
