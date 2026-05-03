#pragma once
#include "element_base.h"
#include <vector>

struct TreeViewItem {
    std::wstring label;
    int level = 0;
    bool expanded = true;
    bool checked = false;
    bool lazy = false;
    bool loading = false;
};

class TreeView : public Element {
public:
    std::vector<TreeViewItem> items;
    int selected_index = 0;

    const wchar_t* type_name() const override { return L"Tree"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<TreeViewItem>& values);
    void set_selected_index(int value);
    void set_options(bool show_checkbox, bool keyboard_navigation, bool lazy_mode);
    void set_item_expanded(int index, bool expanded);
    void toggle_item_expanded(int index);
    bool get_item_expanded(int index) const;
    void set_item_checked(int index, bool checked);
    bool get_item_checked(int index) const;
    void set_item_lazy(int index, bool lazy);
    bool get_item_lazy(int index) const;
    int visible_count() const;
    int checked_count() const;
    int lazy_count() const;
    int last_lazy_index() const { return m_last_lazy_index; }
    bool show_checkbox() const { return m_show_checkbox; }
    bool keyboard_navigation() const { return m_keyboard_navigation; }
    bool lazy_mode() const { return m_lazy_mode; }

private:
    int m_hover_index = -1;
    int m_press_index = -1;
    bool m_show_checkbox = false;
    bool m_keyboard_navigation = true;
    bool m_lazy_mode = false;
    int m_last_lazy_index = -1;

    float row_height() const;
    int item_at(int x, int y) const;
    bool is_visible_item(int index) const;
    bool has_children(int index) const;
    bool is_checkbox_hit(int index, int x) const;
    int first_visible_index() const;
    int last_visible_index() const;
    int next_visible_index(int from, int delta) const;
    int parent_index(int index) const;
    void request_lazy_load(int index);
};
