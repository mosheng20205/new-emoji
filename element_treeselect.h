#pragma once
#include "element_base.h"
#include "element_treeview.h"
#include <vector>

class TreeSelect : public Element {
public:
    std::vector<TreeViewItem> items;
    int selected_index = 0;
    bool open = false;
    bool multiple = false;
    bool clearable = true;
    bool searchable = false;
    std::wstring search_text;
    std::vector<int> selected_indices;

    const wchar_t* type_name() const override { return L"TreeSelect"; }
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

    void set_items(const std::vector<TreeViewItem>& values);
    void set_selected_index(int value);
    void set_open(bool next_open);
    bool is_open() const;
    void set_options(bool multiple, bool clearable, bool searchable);
    void set_search_text(const std::wstring& value);
    void clear_selection();
    void set_selected_items(const std::vector<int>& indices);
    int selected_count() const;
    int selected_item(int position) const;
    int matched_count() const;
    void set_item_expanded(int index, bool expanded);
    void toggle_item_expanded(int index);
    bool get_item_expanded(int index) const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartItem
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    Part m_press_part = PartNone;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int row_height() const;
    bool is_visible_item(int index) const;
    bool matches_filter(int index) const;
    bool is_rendered_item(int index) const;
    bool has_children(int index) const;
    int item_at(int x, int y) const;
    std::wstring selected_text() const;
    void sync_single_from_multi();
    bool is_selected_multi(int index) const;
    void toggle_selected_multi(int index);
    int next_rendered_index(int from, int delta) const;
    int first_rendered_index() const;
};
