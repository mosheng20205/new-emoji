#pragma once
#include "element_base.h"
#include <vector>

class Tabs : public Element {
public:
    std::vector<std::wstring> items;
    int active_index = 0;
    int tab_type = 0;
    bool closable = false;
    bool addable = false;
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
    void set_active_index(int value);
    void set_tab_type(int value);
    void set_options(int type, bool close_enabled, bool add_enabled);
    void add_tab(const std::wstring& label);
    void close_tab(int index);
    void set_scroll_offset(int offset);
    void scroll_delta(int delta);
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
    float tab_width() const;
    float tabs_view_width() const;
    int total_tabs_width() const;
    void clamp_scroll();
    void ensure_active_visible();
    void select_index(int value, int action);
};
