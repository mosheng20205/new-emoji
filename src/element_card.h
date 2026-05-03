#pragma once
#include "element_base.h"
#include <vector>

class Card : public Element {
public:
    std::wstring title;
    std::wstring body;
    std::wstring footer;
    std::vector<std::wstring> actions;
    int shadow = 1; // 0 never, 1 always, 2 hover
    bool hoverable = true;
    int action_index = -1;

    const wchar_t* type_name() const override { return L"Card"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;

    void set_title(const std::wstring& value);
    void set_body(const std::wstring& value);
    void set_footer(const std::wstring& value);
    void set_actions(const std::vector<std::wstring>& values);
    void reset_action();
    void set_shadow(int value);
    void set_options(int shadow_value, bool hoverable_value);

private:
    int hover_action = -1;
    int press_action = -1;

    int action_at(int x, int y) const;
    float footer_height() const;
};
