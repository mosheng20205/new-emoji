#pragma once
#include "element_base.h"

class InfoBox : public Element {
public:
    InfoBox() { mouse_passthrough = true; }
    std::wstring header;
    Color accent_color = 0;
    int info_type = 0; // 0 info, 1 success, 2 warning, 3 error
    bool closable = false;
    bool closed = false;
    std::wstring icon_text;

    const wchar_t* type_name() const override { return L"InfoBox"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void set_texts(const std::wstring& new_header, const std::wstring& new_body);
    void set_options(int type, int close_enabled, Color accent, const std::wstring& icon);
    void set_closed(bool value);
    bool is_closed() const;
    int preferred_height() const;

private:
    bool close_hit(int x, int y) const;
};
