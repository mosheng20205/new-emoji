#pragma once
#include "element_base.h"
#include <d2d1.h>

class Empty : public Element {
public:
    std::wstring description;
    std::wstring icon = L"📭";
    std::wstring image_source;
    int image_size = 0;
    int logical_image_size = 0;
    int image_status = 0; // 0 default icon/no image, 1 loaded, 2 failed, 3 loading
    std::wstring action_text;
    bool action_clicked = false;
    ElementClickCallback action_cb = nullptr;

    ~Empty() override;
    const wchar_t* type_name() const override { return L"Empty"; }
    void apply_dpi_scale(float scale) override;
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_description(const std::wstring& value);
    void set_icon(const std::wstring& value);
    void set_image(const std::wstring& value);
    void set_image_size(int value);
    void set_action(const std::wstring& value);
    void set_action_clicked(bool value);

private:
    ID2D1Bitmap* m_image_bitmap = nullptr;
    ID2D1RenderTarget* m_image_bitmap_rt = nullptr;
    std::wstring m_image_bitmap_src;
    int m_image_bitmap_w = 0;
    int m_image_bitmap_h = 0;
    bool m_action_hover = false;
    bool m_action_down = false;
    void release_image_bitmap();
    bool ensure_image_bitmap(RenderContext& ctx);
    Rect action_rect() const;
    bool action_hit(int x, int y) const;
};
