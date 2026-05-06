#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <wincodec.h>

class Avatar : public Element {
public:
    int shape = 0;
    int fit = 0;
    int image_status = 0;
    bool image_loaded = false;
    bool image_failed = false;

    ~Avatar() override;
    const wchar_t* type_name() const override { return L"Avatar"; }
    void paint(RenderContext& ctx) override;

    void set_shape(int value);
    void set_source(const std::wstring& path);
    void set_fallback_source(const std::wstring& path);
    void set_icon(const std::wstring& value);
    void set_error_text(const std::wstring& value);
    void set_fit(int value);

private:
    std::wstring m_source;
    std::wstring m_fallback_source;
    std::wstring m_icon;
    std::wstring m_error_text;
    ID2D1Bitmap* m_primary_bitmap = nullptr;
    ID2D1RenderTarget* m_primary_rt = nullptr;
    std::wstring m_primary_cached_src;
    ID2D1Bitmap* m_fallback_bitmap = nullptr;
    ID2D1RenderTarget* m_fallback_rt = nullptr;
    std::wstring m_fallback_cached_src;

    void release_images();
    void release_bitmap_slot(ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt, std::wstring& cached_src);
    bool ensure_bitmap_for_source(RenderContext& ctx, const std::wstring& source,
                                  ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                  std::wstring& cached_src, bool update_status);
    ID2D1Bitmap* ensure_paint_bitmap(RenderContext& ctx);
    D2D1_RECT_F fitted_rect(const D2D1_RECT_F& box, D2D1_SIZE_F size) const;
};
