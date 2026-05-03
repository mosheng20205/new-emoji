#pragma once
#include <d2d1.h>
#include <dwrite.h>
#include <map>
#include <string>
#include "element_types.h"

/**
 * Per-paint rendering context. Wraps a D2D render target and provides
 * cached brushes and text-layout creation.
 */
class RenderContext {
public:
    RenderContext(ID2D1RenderTarget* rt, IDWriteFactory* dw);
    ~RenderContext();

    ID2D1RenderTarget* rt = nullptr;
    IDWriteFactory* dwrite = nullptr;

    ID2D1SolidColorBrush* get_brush(Color argb);

    /** Create a text layout. Caller must Release(). */
    IDWriteTextLayout* create_text_layout(const std::wstring& text,
                                          const std::wstring& font_name,
                                          float font_size,
                                          float max_w, float max_h);

    void push_clip(const D2D1_RECT_F& rect);
    void pop_clip();

    void clear_brush_cache();

private:
    std::map<Color, ID2D1SolidColorBrush*> m_brushes;
};
