#pragma once
#include "element_text.h"

class Link : public Text {
public:
    Link() { mouse_passthrough = false; }
    bool visited = false;
    int link_type = 0; // 0 default, 1 primary, 2 success, 3 warning, 4 danger, 5 info
    bool underline_enabled = true;
    bool auto_open = false;
    std::wstring prefix_icon;
    std::wstring suffix_icon;
    std::wstring href;
    std::wstring target;

    const wchar_t* type_name() const override { return L"Link"; }
    Element* hit_test(int x, int y) override;
    void paint(RenderContext& ctx) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;
    void set_options(int type, int underline, int open, int is_visited);
    void set_content(const std::wstring& prefix, const std::wstring& suffix,
                     const std::wstring& link_href, const std::wstring& link_target);

protected:
    Color text_color(const Theme* theme) const override;
    bool underline() const override { return underline_enabled; }

private:
    bool m_key_armed = false;

    std::wstring display_text() const;
    void open_href_if_needed();
};
