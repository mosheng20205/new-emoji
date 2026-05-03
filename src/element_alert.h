#pragma once
#include "element_base.h"

class Alert : public Element {
public:
    std::wstring description;
    int alert_type = 0;
    int effect = 0;
    bool closable = true;
    bool closed = false;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger
    ElementValueCallback close_cb = nullptr;

    const wchar_t* type_name() const override { return L"Alert"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_description(const std::wstring& value);
    void set_type(int value);
    void set_effect(int value);
    void set_closable(bool value);
    void set_closed(bool value);
    void close_alert(int action);
    bool close_hover() const { return m_close_hover; }
    bool close_down() const { return m_close_down; }

private:
    bool m_close_hover = false;
    bool m_close_down = false;

    Rect close_rect() const;
    bool close_hit(int x, int y) const;
};
