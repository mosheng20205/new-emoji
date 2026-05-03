#pragma once
#include "element_base.h"
#include <vector>

class Breadcrumb : public Element {
public:
    std::vector<std::wstring> items;
    std::wstring separator = L"/";
    int current_index = -1;
    int last_clicked_index = -1;
    int click_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger
    ElementValueCallback select_cb = nullptr;

    const wchar_t* type_name() const override { return L"Breadcrumb"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_separator(const std::wstring& value);
    void set_current_index(int value);
    void activate_index(int value, int action);
    int hover_index() const { return m_hover_index; }
    int press_index() const { return m_press_index; }

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    int item_at(int x, int y) const;
    Rect item_rect(int index) const;
};
