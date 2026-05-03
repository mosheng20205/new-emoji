#pragma once
#include "element_base.h"
#include "theme.h"
#include <vector>

struct CheckboxGroupItem {
    std::wstring text;
    std::wstring value;
    bool disabled = false;
    bool checked = false;
};

class Checkbox : public Element {
public:
    bool checked = false;
    bool indeterminate = false;
    bool border = false;
    int size = 0; // 0 default, 1 medium, 2 small, 3 mini

    const wchar_t* type_name() const override { return L"Checkbox"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_checked(bool value);
    void set_indeterminate(bool value);
    void set_options(bool border_value, int size_value);
    void toggle();
private:
    bool key_armed = false;
};

class CheckboxGroup : public Element {
public:
    std::vector<CheckboxGroupItem> items;
    bool group_disabled = false;
    int style_mode = 0; // 0 normal, 1 button, 2 border
    int size = 0;       // 0 default, 1 medium, 2 small, 3 mini
    int min_checked = 0;
    int max_checked = 0; // 0 means unlimited
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 items
    ElementValueCallback change_cb = nullptr;
    bool suppress_click = false;

    const wchar_t* type_name() const override { return L"CheckboxGroup"; }
    bool accepts_input() const override { return enabled && !group_disabled && !suppress_click; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

    void set_items(const std::vector<CheckboxGroupItem>& next_items);
    void set_checked_values(const std::vector<std::wstring>& values);
    std::wstring checked_values() const;
    void set_options(bool disabled_value, int style_value, int size_value,
                     int min_value, int max_value);
    int item_count() const;
    int checked_count() const;
    int disabled_count() const;
    int hover_index() const;
    int press_index() const;
    int focus_index() const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;
    int m_focus_index = -1;
    bool m_key_armed = false;

    bool is_item_disabled(int index) const;
    bool can_toggle_index(int index) const;
    int item_at(int x, int y) const;
    int next_enabled_index(int from, int delta) const;
    void toggle_index(int index, int action);
};
