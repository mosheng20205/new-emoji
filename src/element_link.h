#pragma once
#include "element_text.h"

class Link : public Text {
public:
    Link() { mouse_passthrough = false; }
    bool visited = false;

    const wchar_t* type_name() const override { return L"Link"; }
    Element* hit_test(int x, int y) override;
    void paint(RenderContext& ctx) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_key_up(int vk, int mods) override;

protected:
    Color text_color(const Theme* theme) const override;
    bool underline() const override { return true; }

private:
    bool m_key_armed = false;
};
