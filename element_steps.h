#pragma once
#include "element_base.h"
#include <vector>

class Steps : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<std::wstring> descriptions;
    std::vector<int> statuses; // 0 wait, 1 process, 2 finish, 3 error
    int active_index = 0;
    int direction = 0; // 0 horizontal, 1 vertical
    int last_clicked_index = -1;
    int click_count = 0;
    int change_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Steps"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_step_items(const std::vector<std::pair<std::wstring, std::wstring>>& values);
    void set_active_index(int value);
    void set_direction(int value);
    void set_statuses(const std::vector<int>& values);
    void activate_index(int value, int action);
    int hover_index() const { return m_hover_index; }
    int press_index() const { return m_press_index; }
    int status_at(int index) const;
    int failed_count() const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    int step_at(int x, int y) const;
};
