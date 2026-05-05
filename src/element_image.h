#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <vector>

bool is_shared_remote_image_source(const std::wstring& value);
int resolve_shared_image_source(HWND hwnd, const std::wstring& source, std::wstring& local_path);

class Image : public Element {
public:
    std::wstring src;
    std::wstring alt;
    int fit = 0; // 0 contain, 1 cover, 2 fill, 3 none, 4 scale-down
    int load_status = 0; // 0 placeholder/empty, 1 loaded, 2 failed, 3 loading, 4 lazy waiting
    bool lazy = false;
    bool preview_open = false;
    bool preview_enabled = true;
    int preview_index = 0;
    int preview_scale_percent = 100;
    int preview_offset_x = 0;
    int preview_offset_y = 0;
    bool cache_enabled = true;
    int reload_count = 0;
    int bitmap_width = 0;
    int bitmap_height = 0;
    std::vector<std::wstring> preview_sources;

    std::wstring placeholder_icon = L"\U0001F5BC\uFE0F";
    std::wstring placeholder_text = L"\u56FE\u7247\u52A0\u8F7D\u4E2D";
    Color placeholder_fg = 0;
    Color placeholder_bg = 0;
    std::wstring error_icon = L"\u26A0\uFE0F";
    std::wstring error_text = L"\u56FE\u7247\u52A0\u8F7D\u5931\u8D25";
    Color error_fg = 0;
    Color error_bg = 0;

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
    void set_lazy(bool value);
    void set_placeholder(const std::wstring& icon, const std::wstring& text, Color fg, Color bg);
    void set_error_content(const std::wstring& icon, const std::wstring& text, Color fg, Color bg);
    void set_preview_list(const std::vector<std::wstring>& sources, int selected_index);
    void set_preview_index(int index);
    bool is_preview_open() const;
    int preview_count() const;

private:
    ID2D1Bitmap* m_bitmap = nullptr;
    ID2D1RenderTarget* m_bitmap_rt = nullptr;
    std::wstring m_bitmap_src;
    ID2D1Bitmap* m_preview_bitmap = nullptr;
    ID2D1RenderTarget* m_preview_bitmap_rt = nullptr;
    std::wstring m_preview_bitmap_src;
    bool m_pressed_preview = false;

    void release_bitmap();
    void release_preview_bitmap();
    bool ensure_bitmap_for_source(RenderContext& ctx, const std::wstring& value,
                                  ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                  std::wstring& cached_src, int* out_w, int* out_h,
                                  bool update_status, bool honor_lazy);
    bool ensure_bitmap(RenderContext& ctx);
    bool ensure_preview_bitmap(RenderContext& ctx);
    bool is_in_viewport() const;
    std::wstring current_preview_source() const;
    D2D1_RECT_F fitted_rect(const D2D1_RECT_F& box, D2D1_SIZE_F size, int fit_mode) const;
    void draw_state(RenderContext& ctx, const D2D1_RECT_F& rect, bool error_state);
    bool change_preview_index(int delta);
    D2D1_RECT_F image_rect() const;
    D2D1_RECT_F preview_rect() const;
};
