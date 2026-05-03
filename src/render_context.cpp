#include "render_context.h"
#include <cassert>

RenderContext::RenderContext(ID2D1RenderTarget* target, IDWriteFactory* dw)
    : rt(target), dwrite(dw) {}

RenderContext::~RenderContext() {
    clear_brush_cache();
    // Clear any remaining clips
    while (!m_brushes.empty()) pop_clip();
}

ID2D1SolidColorBrush* RenderContext::get_brush(Color argb) {
    auto it = m_brushes.find(argb);
    if (it != m_brushes.end()) return it->second;
    ID2D1SolidColorBrush* brush = nullptr;
    rt->CreateSolidColorBrush(
        D2D1::ColorF(((argb >> 16) & 0xFF) / 255.0f,
                     ((argb >> 8) & 0xFF) / 255.0f,
                     (argb & 0xFF) / 255.0f,
                     ((argb >> 24) & 0xFF) / 255.0f),
        &brush);
    m_brushes[argb] = brush;
    return brush;
}

IDWriteTextLayout* RenderContext::create_text_layout(const std::wstring& text,
                                                     const std::wstring& font_name,
                                                     float font_size,
                                                     float max_w, float max_h) {
    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = dwrite->CreateTextFormat(
        font_name.c_str(), nullptr,
        DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL,
        font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) return nullptr;

    IDWriteTextLayout* layout = nullptr;
    hr = dwrite->CreateTextLayout(text.c_str(), static_cast<UINT32>(text.size()),
                                  fmt, max_w, max_h, &layout);
    fmt->Release();
    return SUCCEEDED(hr) ? layout : nullptr;
}

void RenderContext::push_clip(const D2D1_RECT_F& rect) {
    rt->PushAxisAlignedClip(rect, D2D1_ANTIALIAS_MODE_ALIASED);
}

void RenderContext::pop_clip() {
    rt->PopAxisAlignedClip();
}

void RenderContext::clear_brush_cache() {
    for (auto& kv : m_brushes) kv.second->Release();
    m_brushes.clear();
}
