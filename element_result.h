#pragma once
#include "element_base.h"
#include <vector>

class Result : public Element {
public:
    std::wstring subtitle;
    std::wstring extra_content;
    std::vector<std::wstring> actions;
    int result_type = 0;
    int last_action = -1;
    int action_click_count = 0;
    int last_action_source = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger
    ElementValueCallback action_cb = nullptr;

    const wchar_t* type_name() const override { return L"Result"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_subtitle(const std::wstring& value);
    void set_extra_content(const std::wstring& value);
    void set_type(int value);
    void set_actions(const std::vector<std::wstring>& values);
    void trigger_action(int index, int source);
    int hover_action() const { return m_hover_action; }
    int press_action() const { return m_press_action; }

private:
    int m_hover_action = -1;
    int m_press_action = -1;

    Rect action_rect(int index) const;
    int action_at(int x, int y) const;
};
