#pragma once
#include "element_base.h"
#include <d2d1.h>

class Image : public Element {
public:
    std::wstring src;
    std::wstring alt;
    int fit = 0; // 0 contain, 1 cover, 2 fill
    int load_status = 0; // 0 empty/placeholder, 1 loaded, 2 failed
    bool preview_open = false;
    bool preview_enabled = true;
    int preview_scale_percent = 100;
    int preview_offset_x = 0;
    int preview_offset_y = 0;
    bool cache_enabled = true;
    int reload_count = 0;
    int bitmap_width = 0;
    int bitmap_height = 0;

    ~Image() override;

    const wchar_t* type_name() const override { return L"Image"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_source(const std::wstring& value);
    void set_alt(const std::wstring& value);
    void set_fit(int value);
    void set_preview_open(bool value);
    void set_preview_enabled(bool value);
    void set_preview_transform(int scale_percent, int offset_x, int offset_y);
    void set_cache_enabled(bool value);
    bool is_preview_open() const;

private:
    ID2D1Bitmap* m_bitmap = nullptr;
    ID2D1RenderTarget* m_bitmap_rt = nullptr;
    std::wstring m_bitmap_src;
    bool m_pressed_preview = false;

    void release_bitmap();
    bool ensure_bitmap(RenderContext& ctx);
    D2D1_RECT_F image_rect() const;
    D2D1_RECT_F preview_rect() const;
};
