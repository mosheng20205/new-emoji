#include "element_avatar.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

Avatar::~Avatar() {
    release_images();
}

void Avatar::release_images() {
    if (m_d2d_bitmap) {
        m_d2d_bitmap->Release();
        m_d2d_bitmap = nullptr;
    }
    if (m_bitmap) {
        m_bitmap->Release();
        m_bitmap = nullptr;
    }
}

void Avatar::set_shape(int value) {
    shape = value == 1 ? 1 : 0;
    invalidate();
}

void Avatar::set_source(const std::wstring& path) {
    m_source = path;
    image_loaded = false;
    image_failed = !m_source.empty();
    release_images();
    invalidate();
}

void Avatar::set_fit(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    fit = value;
    invalidate();
}

void Avatar::ensure_d2d_bitmap(RenderContext& ctx) {
    if (m_source.empty() || m_d2d_bitmap) return;
    if (!g_wic_factory) ensure_factories();
    if (!g_wic_factory) {
        image_failed = true;
        return;
    }

    IWICBitmapDecoder* decoder = nullptr;
    IWICBitmapFrameDecode* frame = nullptr;
    IWICFormatConverter* converter = nullptr;
    HRESULT hr = g_wic_factory->CreateDecoderFromFilename(
        m_source.c_str(), nullptr, GENERIC_READ, WICDecodeMetadataCacheOnLoad, &decoder);
    if (SUCCEEDED(hr)) hr = decoder->GetFrame(0, &frame);
    if (SUCCEEDED(hr)) hr = g_wic_factory->CreateFormatConverter(&converter);
    if (SUCCEEDED(hr)) {
        hr = converter->Initialize(frame, GUID_WICPixelFormat32bppPBGRA,
            WICBitmapDitherTypeNone, nullptr, 0.0f, WICBitmapPaletteTypeMedianCut);
    }
    if (SUCCEEDED(hr)) hr = ctx.rt->CreateBitmapFromWicBitmap(converter, nullptr, &m_d2d_bitmap);

    if (converter) converter->Release();
    if (frame) frame->Release();
    if (decoder) decoder->Release();

    image_loaded = SUCCEEDED(hr) && m_d2d_bitmap;
    image_failed = !image_loaded && !m_source.empty();
}

void Avatar::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->accent;
    Color fg = style.fg_color ? style.fg_color : 0xFFFFFFFF;
    Color border = style.border_color ? style.border_color : 0;

    float size = (float)(std::min)(bounds.w, bounds.h);
    float x = ((float)bounds.w - size) * 0.5f;
    float y = ((float)bounds.h - size) * 0.5f;
    D2D1_RECT_F rect = { x, y, x + size, y + size };

    ID2D1EllipseGeometry* ellipse_mask = nullptr;
    ID2D1Layer* layer = nullptr;
    if (shape == 1) {
        float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;
        ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
        ctx.push_clip(rect);
    } else {
        D2D1_ELLIPSE ellipse = D2D1::Ellipse(D2D1::Point2F(x + size * 0.5f, y + size * 0.5f),
                                             size * 0.5f, size * 0.5f);
        ctx.rt->FillEllipse(ellipse, ctx.get_brush(bg));
        if (g_d2d_factory &&
            SUCCEEDED(g_d2d_factory->CreateEllipseGeometry(ellipse, &ellipse_mask)) &&
            SUCCEEDED(ctx.rt->CreateLayer(nullptr, &layer))) {
            ctx.rt->PushLayer(D2D1::LayerParameters(rect, ellipse_mask), layer);
        } else {
            ctx.push_clip(rect);
        }
    }

    ensure_d2d_bitmap(ctx);
    if (m_d2d_bitmap) {
        D2D1_SIZE_F source_size = m_d2d_bitmap->GetSize();
        D2D1_RECT_F dest = rect;
        if (source_size.width > 0.0f && source_size.height > 0.0f && fit != 2) {
            float sx = size / source_size.width;
            float sy = size / source_size.height;
            float scale = fit == 1 ? (std::max)(sx, sy) : (std::min)(sx, sy);
            float dw = source_size.width * scale;
            float dh = source_size.height * scale;
            dest = D2D1::RectF(x + (size - dw) * 0.5f, y + (size - dh) * 0.5f,
                               x + (size + dw) * 0.5f, y + (size + dh) * 0.5f);
        }
        ctx.rt->DrawBitmap(m_d2d_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
    } else {
        float text_pad = (std::max)(2.0f, size * 0.12f);
        float font_scale = text.size() <= 2 ? 1.15f : 0.95f;
        draw_text(ctx, text.empty() && image_failed ? L"!" : text, style, fg,
                  x + text_pad, y, size - text_pad * 2.0f, size, font_scale);
    }
    if (shape == 1 || !layer) ctx.pop_clip();
    else ctx.rt->PopLayer();
    if (layer) layer->Release();
    if (ellipse_mask) ellipse_mask->Release();

    if (shape == 1) {
        float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;
        if (border) {
            ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
                rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);
        }
    } else if (border) {
        D2D1_ELLIPSE ellipse = D2D1::Ellipse(D2D1::Point2F(x + size * 0.5f, y + size * 0.5f),
                                             size * 0.5f, size * 0.5f);
        ctx.rt->DrawEllipse(ellipse, ctx.get_brush(border), 1.0f);
    }

    ctx.rt->SetTransform(saved);
}
