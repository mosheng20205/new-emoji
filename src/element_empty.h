#pragma once
#include "element_base.h"

class Empty : public Element {
public:
    std::wstring description;
    std::wstring icon = L"📭";
    std::wstring action_text;
    bool action_clicked = false;
    ElementClickCallback action_cb = nullptr;

    const wchar_t* type_name() const override { return L"Empty"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_description(const std::wstring& value);
    void set_icon(const std::wstring& value);
    void set_action(const std::wstring& value);
    void set_action_clicked(bool value);

private:
    bool m_action_hover = false;
    bool m_action_down = false;
    Rect action_rect() const;
    bool action_hit(int x, int y) const;
};
