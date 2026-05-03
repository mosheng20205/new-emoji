#pragma once
#include "element_base.h"
#include <vector>

class PageHeader : public Element {
public:
    std::wstring title;
    std::wstring subtitle;
    std::vector<std::wstring> breadcrumbs;
    std::vector<std::wstring> actions;
    int active_action = -1;
    int active_breadcrumb = -1;
    int back_clicked_count = 0;
    std::wstring back_text = L"返回";

    const wchar_t* type_name() const override { return L"PageHeader"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_title(const std::wstring& value);
    void set_subtitle(const std::wstring& value);
    void set_back_text(const std::wstring& value);
    void set_breadcrumbs(const std::vector<std::wstring>& items);
    void set_actions(const std::vector<std::wstring>& items);
    void set_active_action(int index);
    void set_active_breadcrumb(int index);
    void trigger_back();
    void reset_result();
    int get_active_action() const { return active_action; }
    int breadcrumb_count() const { return (int)breadcrumbs.size(); }
    int action_count() const { return (int)actions.size(); }
    int hovered_action() const { return m_action_hover; }
    int hovered_breadcrumb() const { return m_breadcrumb_hover; }
    int back_hovered() const { return m_back_hover ? 1 : 0; }

private:
    bool m_back_hover = false;
    bool m_back_pressed = false;
    int m_action_hover = -1;
    int m_action_pressed = -1;
    int m_breadcrumb_hover = -1;
    int m_breadcrumb_pressed = -1;

    Rect back_rect() const;
    Rect action_rect(int index) const;
    Rect breadcrumb_rect(int index) const;
    int breadcrumb_at(int x, int y) const;
};
