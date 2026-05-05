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
    TreeNodeEventCallback event_cb = nullptr;
    TreeNodeEventCallback lazy_cb = nullptr;
    TreeNodeEventCallback drag_cb = nullptr;
    TreeNodeAllowDragCallback allow_drag_cb = nullptr;
    TreeNodeAllowDropCallback allow_drop_cb = nullptr;

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
    void set_data_json(const std::wstring& json);
    std::wstring data_json() const;
    void set_options_json(const std::wstring& json);
    std::wstring state_json() const;
    void set_selected_keys(const std::vector<std::wstring>& keys);
    std::vector<std::wstring> selected_keys() const;
    void set_expanded_keys(const std::vector<std::wstring>& keys);
    std::vector<std::wstring> expanded_keys() const;
    void append_node_json(const std::wstring& parent_key, const std::wstring& json);
    void update_node_json(const std::wstring& key, const std::wstring& json);
    void remove_node_by_key(const std::wstring& key);
    int index_by_key(const std::wstring& key) const;
    std::wstring key_at(int index) const;

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
    int parent_index(int index) const;
    int subtree_end(int index) const;
    void set_expanded_internal(int index, bool expanded);
    void emit_event(TreeNodeEventCallback cb, int event_code, int index, int extra = 0);
    bool m_check_strictly = false;
    bool m_accordion = false;
    bool m_draggable = false;
    bool m_show_actions = false;
    int m_last_lazy_index = -1;
    bool m_dragging = false;
    int m_drag_index = -1;
    int m_drop_index = -1;
    int m_drop_type = 0;
    int m_drag_event_count = 0;
    bool can_drag(int index) const;
    bool can_drop(int drag_index, int drop_index, int drop_type) const;
    void move_subtree(int drag_index, int drop_index, int drop_type);
};
