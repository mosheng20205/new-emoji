#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <vector>

struct TabsItem {
    std::wstring label;
    std::wstring name;
    std::wstring content;
    std::wstring icon;
    bool disabled = false;
    bool closable = true;
};

class Tabs : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<TabsItem> tab_items;
    int active_index = 0;
    int tab_type = 0;
    int tab_position = 0;
    int header_align = 0; // 0 left, 1 center, 2 right
    bool closable = false;
    bool addable = false;
    bool editable = false;
    bool content_visible = false;
    int scroll_offset = 0;
    int max_scroll_offset = 0;
    int last_closed_index = -1;
    int last_added_index = -1;
    int close_count = 0;
    int add_count = 0;
    int select_count = 0;
    int scroll_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 close, 5 add, 6 scroll
    ElementValueCallback change_cb = nullptr;
    ElementValueCallback close_cb = nullptr;
    ElementValueCallback add_cb = nullptr;

    const wchar_t* type_name() const override { return L"Tabs"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_items_ex(const std::vector<TabsItem>& values);
    void set_active_index(int value);
    void set_active_name(const std::wstring& name);
    void set_tab_type(int value);
    void set_tab_position(int value);
    void set_header_align(int value);
    void set_options(int type, bool close_enabled, bool add_enabled);
    void set_editable(bool value);
    void set_content_visible(bool value);
    void add_tab(const std::wstring& label);
    void close_tab(int index);
    void set_scroll_offset(int offset);
    void scroll_delta(int delta);
    std::wstring active_name() const;
    std::wstring item_content(int index) const;
    int hover_index() const { return m_hover_index; }
    int press_index() const { return m_press_index; }
    int hover_part() const { return m_hover_part; }
    int press_part() const { return m_press_part; }

private:
    int m_hover_index = -1;
    int m_press_index = -1;
    int m_hover_part = 0; // 0 none, 1 tab, 2 close, 3 add
    int m_press_part = 0;

    int part_at(int x, int y, int* part) const;
    int tab_at(int x, int y) const;
    bool is_vertical() const;
    float header_extent() const;
    D2D1_RECT_F header_rect() const;
    D2D1_RECT_F content_rect() const;
    float tab_extent() const;
    float tabs_view_extent() const;
    int total_tabs_extent() const;
    bool item_close_enabled(int index) const;
    void clamp_scroll();
    void ensure_active_visible();
    void select_index(int value, int action);
    void sync_legacy_items();
};
