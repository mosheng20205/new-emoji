#pragma once
#include "element_base.h"
#include <vector>

class Pagination : public Element {
public:
    int total = 100;
    int page_size = 10;
    int current_page = 1;
    int jump_page = 1;
    int visible_page_count = 7;
    bool show_jumper = true;
    bool show_size_changer = true;
    std::vector<int> page_size_options = { 10, 20, 50, 100 };
    int change_count = 0;
    int size_change_count = 0;
    int jump_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 size, 5 jump
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Pagination"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_total(int value);
    void set_page_size(int value);
    void set_current_page(int value);
    void set_options(int show_jump, int show_size, int visible_count);
    void set_page_size_options(const std::vector<int>& values);
    void set_jump_page(int value);
    void trigger_jump(int action);
    void next_page_size();
    int page_count() const;
    int hover_part() const { return m_hover_part; }
    int press_part() const { return m_press_part; }

private:
    int m_hover_part = 0;
    int m_press_part = 0;

    int part_count() const;
    int width_for_part(int part) const;
    int part_at(int x, int y) const;
    Rect part_rect(int part) const;
    int page_for_part(int part) const;
    std::vector<int> visible_pages() const;
    void update_current_page(int value, int action);
    void clamp_jump_page();
};
