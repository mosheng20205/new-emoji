#pragma once
#include "element_base.h"
#include <vector>
#include <string>

struct TreeViewItem {
    std::wstring key;
    std::wstring label;
    std::wstring icon;
    std::wstring tag;
    std::wstring actions;
    int level = 0;
    bool expanded = true;
    bool checked = false;
    bool indeterminate = false;
    bool lazy = false;
    bool loading = false;
    bool disabled = false;
    bool leaf = false;
};

std::vector<TreeViewItem> parse_tree_json_items(const std::wstring& json,
                                                std::vector<std::wstring>* default_expanded_keys = nullptr,
                                                std::vector<std::wstring>* default_checked_keys = nullptr,
                                                std::wstring* current_key = nullptr,
                                                std::wstring* filter_text = nullptr,
                                                std::wstring* options_json = nullptr);
std::wstring serialize_tree_json_items(const std::vector<TreeViewItem>& items);
std::vector<std::wstring> parse_tree_key_array_json(const std::wstring& json);
std::wstring serialize_tree_key_array_json(const std::vector<std::wstring>& keys);
std::wstring tree_item_event_json(const std::vector<TreeViewItem>& items, int index, int extra = 0);

class TreeView : public Element {
public:
    std::vector<TreeViewItem> items;
    int selected_index = 0;
    TreeNodeEventCallback event_cb = nullptr;
    TreeNodeEventCallback lazy_cb = nullptr;
    TreeNodeEventCallback drag_cb = nullptr;
    TreeNodeAllowDragCallback allow_drag_cb = nullptr;
    TreeNodeAllowDropCallback allow_drop_cb = nullptr;

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
    bool multiple() const { return m_show_checkbox; }
    bool accordion() const { return m_accordion; }
    bool check_strictly() const { return m_check_strictly; }
    bool draggable() const { return m_draggable; }

    void set_data_json(const std::wstring& json);
    std::wstring data_json() const;
    void set_options_json(const std::wstring& json);
    std::wstring state_json() const;
    void set_checked_keys(const std::vector<std::wstring>& keys);
    std::vector<std::wstring> checked_keys() const;
    std::vector<std::wstring> half_checked_keys() const;
    void set_expanded_keys(const std::vector<std::wstring>& keys);
    std::vector<std::wstring> expanded_keys() const;
    void append_node_json(const std::wstring& parent_key, const std::wstring& json);
    void update_node_json(const std::wstring& key, const std::wstring& json);
    void remove_node_by_key(const std::wstring& key);
    int index_by_key(const std::wstring& key) const;
    std::wstring key_at(int index) const;
    void set_filter_text(const std::wstring& value);
    const std::wstring& filter_text() const { return m_filter_text; }

private:
    int m_hover_index = -1;
    int m_press_index = -1;
    bool m_show_checkbox = false;
    bool m_keyboard_navigation = true;
    bool m_lazy_mode = false;
    int m_last_lazy_index = -1;
    bool m_check_strictly = false;
    bool m_accordion = false;
    bool m_expand_on_click_node = true;
    bool m_highlight_current = true;
    bool m_check_on_click_node = false;
    bool m_draggable = false;
    bool m_show_actions = false;
    std::wstring m_filter_text;
    bool m_dragging = false;
    int m_drag_index = -1;
    int m_drop_index = -1;
    int m_drop_type = 0;
    int m_drag_event_count = 0;

    float row_height() const;
    int item_at(int x, int y) const;
    bool is_visible_item(int index) const;
    bool is_rendered_item(int index) const;
    bool matches_filter(int index) const;
    bool has_matching_descendant(int index) const;
    bool has_children(int index) const;
    bool is_checkbox_hit(int index, int x) const;
    bool is_expander_hit(int index, int x) const;
    int first_visible_index() const;
    int last_visible_index() const;
    int next_visible_index(int from, int delta) const;
    int parent_index(int index) const;
    int subtree_end(int index) const;
    void request_lazy_load(int index);
    void set_expanded_internal(int index, bool expanded);
    void update_ancestor_checks();
    void set_subtree_checked(int index, bool checked);
    void emit_event(TreeNodeEventCallback cb, int event_code, int index, int extra = 0);
    bool can_drag(int index) const;
    bool can_drop(int drag_index, int drop_index, int drop_type) const;
    void move_subtree(int drag_index, int drop_index, int drop_type);
};
