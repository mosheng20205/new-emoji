#include "element_avatar.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "element_image.h"
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
    release_bitmap_slot(m_primary_bitmap, m_primary_rt, m_primary_cached_src);
    release_bitmap_slot(m_fallback_bitmap, m_fallback_rt, m_fallback_cached_src);
}

void Avatar::release_bitmap_slot(ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                 std::wstring& cached_src) {
    if (bitmap) {
        bitmap->Release();
        bitmap = nullptr;
    }
    rt = nullptr;
    cached_src.clear();
}

void Avatar::set_shape(int value) {
    shape = value == 1 ? 1 : 0;
    invalidate();
}

void Avatar::set_source(const std::wstring& path) {
    m_source = path;
    image_loaded = false;
    image_failed = false;
    image_status = m_source.empty() ? 0 : 3;
    release_bitmap_slot(m_primary_bitmap, m_primary_rt, m_primary_cached_src);
    invalidate();
}

void Avatar::set_fallback_source(const std::wstring& path) {
    m_fallback_source = path;
    release_bitmap_slot(m_fallback_bitmap, m_fallback_rt, m_fallback_cached_src);
    invalidate();
}

void Avatar::set_icon(const std::wstring& value) {
    m_icon = value;
    invalidate();
}

void Avatar::set_error_text(const std::wstring& value) {
    m_error_text = value;
    invalidate();
}

void Avatar::set_fit(int value) {
    if (value < 0) value = 0;
    if (value > 4) value = 4;
    fit = value;
    invalidate();
}

static bool load_avatar_bitmap_from_path(RenderContext& ctx, const std::wstring& path,
                                         ID2D1Bitmap** out_bitmap) {
    if (!out_bitmap) return false;
    *out_bitmap = nullptr;
    if (path.empty()) return false;
    if (!g_wic_factory) ensure_factories();
    if (!g_wic_factory) return false;

    IWICBitmapDecoder* decoder = nullptr;
    IWICBitmapFrameDecode* frame = nullptr;
    IWICFormatConverter* converter = nullptr;
    HRESULT hr = g_wic_factory->CreateDecoderFromFilename(
        path.c_str(), nullptr, GENERIC_READ, WICDecodeMetadataCacheOnLoad, &decoder);
    if (SUCCEEDED(hr)) hr = decoder->GetFrame(0, &frame);
    if (SUCCEEDED(hr)) hr = g_wic_factory->CreateFormatConverter(&converter);
    if (SUCCEEDED(hr)) {
        hr = converter->Initialize(frame, GUID_WICPixelFormat32bppPBGRA,
            WICBitmapDitherTypeNone, nullptr, 0.0f, WICBitmapPaletteTypeMedianCut);
    }
    if (SUCCEEDED(hr)) hr = ctx.rt->CreateBitmapFromWicBitmap(converter, nullptr, out_bitmap);

    if (converter) converter->Release();
    if (frame) frame->Release();
    if (decoder) decoder->Release();

    return SUCCEEDED(hr) && *out_bitmap;
}

bool Avatar::ensure_bitmap_for_source(RenderContext& ctx, const std::wstring& source,
                                      ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                      std::wstring& cached_src, bool update_status) {
    if (source.empty()) {
        if (update_status) {
            image_status = 0;
            image_loaded = false;
            image_failed = false;
        }
        return false;
    }
    if (bitmap && rt == ctx.rt && cached_src == source) {
        if (update_status) {
            image_status = 1;
            image_loaded = true;
            image_failed = false;
        }
        return true;
    }
    if (bitmap && rt != ctx.rt) {
        release_bitmap_slot(bitmap, rt, cached_src);
    }

    std::wstring decode_path;
    int state = resolve_shared_image_source(owner_hwnd, source, decode_path);
    if (state == 3) {
        if (update_status) {
            image_status = 3;
            image_loaded = false;
            image_failed = false;
        }
        return false;
    }
    if (state != 1 || decode_path.empty()) {
        if (update_status) {
            image_status = 2;
            image_loaded = false;
            image_failed = true;
        }
        return false;
    }

    release_bitmap_slot(bitmap, rt, cached_src);
    ID2D1Bitmap* loaded = nullptr;
    if (load_avatar_bitmap_from_path(ctx, decode_path, &loaded)) {
        bitmap = loaded;
        rt = ctx.rt;
        cached_src = source;
        if (update_status) {
            image_status = 1;
            image_loaded = true;
            image_failed = false;
        }
        return true;
    }

    if (update_status) {
        image_status = 2;
        image_loaded = false;
        image_failed = true;
    }
    return false;
}

ID2D1Bitmap* Avatar::ensure_paint_bitmap(RenderContext& ctx) {
    if (ensure_bitmap_for_source(ctx, m_source, m_primary_bitmap, m_primary_rt,
                                 m_primary_cached_src, true)) {
        return m_primary_bitmap;
    }
    if (image_status == 3) return nullptr;
    if (ensure_bitmap_for_source(ctx, m_fallback_source, m_fallback_bitmap, m_fallback_rt,
                                 m_fallback_cached_src, false)) {
        image_status = 1;
        image_loaded = true;
        image_failed = false;
        return m_fallback_bitmap;
    }
    return nullptr;
}

D2D1_RECT_F Avatar::fitted_rect(const D2D1_RECT_F& box, D2D1_SIZE_F source_size) const {
    float box_w = box.right - box.left;
    float box_h = box.bottom - box.top;
    if (source_size.width <= 0.0f || source_size.height <= 0.0f || box_w <= 0.0f || box_h <= 0.0f) {
        return box;
    }

    float dw = box_w;
    float dh = box_h;
    if (fit == 3 || (fit == 4 && source_size.width <= box_w && source_size.height <= box_h)) {
        dw = source_size.width;
        dh = source_size.height;
    } else if (fit != 2) {
        float sx = box_w / source_size.width;
        float sy = box_h / source_size.height;
        float scale = fit == 1 ? (std::max)(sx, sy) : (std::min)(sx, sy);
        dw = source_size.width * scale;
        dh = source_size.height * scale;
    }
    return D2D1::RectF(box.left + (box_w - dw) * 0.5f,
                       box.top + (box_h - dh) * 0.5f,
                       box.left + (box_w + dw) * 0.5f,
                       box.top + (box_h + dh) * 0.5f);
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

    ID2D1Bitmap* paint_bitmap = ensure_paint_bitmap(ctx);
    if (paint_bitmap) {
        D2D1_RECT_F dest = fitted_rect(rect, paint_bitmap->GetSize());
        ctx.rt->DrawBitmap(paint_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
    } else {
        float text_pad = (std::max)(2.0f, size * 0.12f);
        std::wstring content;
        if (image_status == 2 && !m_error_text.empty()) content = m_error_text;
        else if (!m_icon.empty()) content = m_icon;
        else if (!text.empty()) content = text;
        else if (image_status == 3) content = L"...";
        else if (image_status == 2) content = L"!";
        float font_scale = content.size() <= 2 ? 1.15f : 0.95f;
        draw_text(ctx, content, style, fg,
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
