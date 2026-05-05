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
    std::vector<std::wstring> item_icons;
    std::vector<std::wstring> item_hrefs;
    std::vector<std::wstring> item_targets;
    std::vector<std::wstring> item_commands;
    std::vector<bool> group_items;
    int active_index = 0;
    int orientation = 0; // 0 horizontal, 1 vertical
    bool collapsed = false;
    Color menu_bg_color = 0;
    Color menu_text_color = 0;
    Color menu_active_text_color = 0;
    Color menu_hover_bg_color = 0;
    Color menu_disabled_text_color = 0;
    Color menu_border_color = 0;
    MenuSelectCallback select_cb = nullptr;

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
    void set_colors(Color bg, Color text_color, Color active_text_color,
                    Color hover_bg, Color disabled_text_color, Color border);
    void set_collapsed(bool value);
    void set_item_meta(const std::vector<std::wstring>& icons,
                       const std::vector<int>& group_indices,
                       const std::vector<std::wstring>& hrefs,
                       const std::vector<std::wstring>& targets,
                       const std::vector<std::wstring>& commands);
    int item_count() const;
    int visible_count() const;
    int expanded_count() const;
    int active_level() const;
    int hover_index() const;
    std::wstring active_path() const;
    const std::wstring& item_icon(int index) const;
    const std::wstring& item_href(int index) const;
    const std::wstring& item_target(int index) const;
    const std::wstring& item_command(int index) const;
    bool is_group(int index) const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    void resize_meta();
    bool is_disabled(int index) const;
    bool has_child(int index) const;
    bool is_visible_item(int index) const;
    bool is_expanded(int index) const;
    int visible_position(int index) const;
    std::vector<int> visible_indices() const;
    int next_visible_enabled(int start, int delta) const;
    void toggle_expanded(int index);
    void choose_item(int index);
    void fire_select(int index);
    void open_href_if_needed(int index);
    int item_height(int index) const;
    int collapsed_width() const;
    int item_at(int x, int y) const;
    Rect item_rect(int index) const;
};
