#include "element_image.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Image::set_source(const std::wstring& value) {
    src = value;
    load_status = src.empty() ? 0 : 2;
    ++reload_count;
    release_bitmap();
    invalidate();
}

void Image::set_alt(const std::wstring& value) {
    alt = value;
    text = value;
    invalidate();
}

void Image::set_fit(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    fit = value;
    invalidate();
}

void Image::set_preview_open(bool value) {
    preview_open = value && preview_enabled;
    invalidate();
}

void Image::set_preview_enabled(bool value) {
    preview_enabled = value;
    if (!preview_enabled) preview_open = false;
    invalidate();
}

void Image::set_preview_transform(int scale_percent, int offset_x, int offset_y) {
    preview_scale_percent = (std::max)(25, (std::min)(400, scale_percent));
    preview_offset_x = (std::max)(-2000, (std::min)(2000, offset_x));
    preview_offset_y = (std::max)(-2000, (std::min)(2000, offset_y));
    invalidate();
}

void Image::set_cache_enabled(bool value) {
    cache_enabled = value;
    if (!cache_enabled) release_bitmap();
    invalidate();
}

bool Image::is_preview_open() const {
    return preview_open;
}

Image::~Image() {
    release_bitmap();
}

void Image::release_bitmap() {
    if (m_bitmap) {
        m_bitmap->Release();
        m_bitmap = nullptr;
    }
    m_bitmap_rt = nullptr;
    m_bitmap_src.clear();
    bitmap_width = 0;
    bitmap_height = 0;
}

bool Image::ensure_bitmap(RenderContext& ctx) {
    if (src.empty()) {
        load_status = 0;
        release_bitmap();
        return false;
    }
    if (cache_enabled && m_bitmap && m_bitmap_rt == ctx.rt && m_bitmap_src == src) {
        load_status = 1;
        return true;
    }

    release_bitmap();
    if (!g_wic_factory) ensure_factories();
    if (!g_wic_factory) {
        load_status = 2;
        return false;
    }

    IWICBitmapDecoder* decoder = nullptr;
    IWICBitmapFrameDecode* frame = nullptr;
    IWICFormatConverter* converter = nullptr;
    HRESULT hr = g_wic_factory->CreateDecoderFromFilename(
        src.c_str(), nullptr, GENERIC_READ, WICDecodeMetadataCacheOnLoad, &decoder);
    if (SUCCEEDED(hr)) hr = decoder->GetFrame(0, &frame);
    if (SUCCEEDED(hr)) {
        hr = g_wic_factory->CreateFormatConverter(&converter);
    }
    if (SUCCEEDED(hr)) {
        hr = converter->Initialize(frame, GUID_WICPixelFormat32bppPBGRA,
            WICBitmapDitherTypeNone, nullptr, 0.0f, WICBitmapPaletteTypeMedianCut);
    }
    if (SUCCEEDED(hr)) {
        hr = ctx.rt->CreateBitmapFromWicBitmap(converter, nullptr, &m_bitmap);
    }

    if (converter) converter->Release();
    if (frame) frame->Release();
    if (decoder) decoder->Release();

    if (SUCCEEDED(hr) && m_bitmap) {
        m_bitmap_rt = ctx.rt;
        m_bitmap_src = src;
        load_status = 1;
        D2D1_SIZE_F bitmap_size = m_bitmap->GetSize();
        bitmap_width = (int)bitmap_size.width;
        bitmap_height = (int)bitmap_size.height;
        return true;
    }

    load_status = 2;
    release_bitmap();
    return false;
}

D2D1_RECT_F Image::image_rect() const {
    float inset = 14.0f;
    D2D1_RECT_F r = { inset, inset, (float)bounds.w - inset, (float)bounds.h - inset - 34.0f };
    if (r.bottom < r.top + 24.0f) r.bottom = (float)bounds.h - inset;
    return r;
}

D2D1_RECT_F Image::preview_rect() const {
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }
    float w = (std::min)(560.0f, (std::max)(240.0f, (float)root_w - 80.0f));
    float h = (std::min)(420.0f, (std::max)(180.0f, (float)root_h - 110.0f));
    return D2D1::RectF(((float)root_w - w) * 0.5f, ((float)root_h - h) * 0.5f,
                       ((float)root_w + w) * 0.5f, ((float)root_h + h) * 0.5f);
}

void Image::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFF5F7FA);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color muted = t->text_secondary;
    Color accent = t->accent;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    D2D1_RECT_F image_rect = this->image_rect();
    ctx.rt->FillRoundedRectangle(ROUNDED(image_rect, 5.0f, 5.0f),
        ctx.get_brush(with_alpha(accent, dark ? 0x24 : 0x18)));

    if (ensure_bitmap(ctx)) {
        D2D1_SIZE_F size = m_bitmap->GetSize();
        float box_w = image_rect.right - image_rect.left;
        float box_h = image_rect.bottom - image_rect.top;
        D2D1_RECT_F dest = image_rect;
        if (size.width > 0.0f && size.height > 0.0f && fit != 2) {
            float sx = box_w / size.width;
            float sy = box_h / size.height;
            float s = fit == 1 ? (std::max)(sx, sy) : (std::min)(sx, sy);
            float dw = size.width * s;
            float dh = size.height * s;
            dest = D2D1::RectF(image_rect.left + (box_w - dw) * 0.5f,
                               image_rect.top + (box_h - dh) * 0.5f,
                               image_rect.left + (box_w + dw) * 0.5f,
                               image_rect.top + (box_h + dh) * 0.5f);
        }
        ctx.push_clip(image_rect);
        ctx.rt->DrawBitmap(m_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
        ctx.pop_clip();
    } else {
        float cx = (image_rect.left + image_rect.right) * 0.5f;
        float cy = (image_rect.top + image_rect.bottom) * 0.5f;
        D2D1_RECT_F sun = { image_rect.right - 58.0f, image_rect.top + 22.0f,
                            image_rect.right - 34.0f, image_rect.top + 46.0f };
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((sun.left + sun.right) * 0.5f,
            (sun.top + sun.bottom) * 0.5f), 12.0f, 12.0f), ctx.get_brush(with_alpha(accent, 0x88)));
        ctx.rt->DrawLine(D2D1::Point2F(image_rect.left + 24.0f, image_rect.bottom - 24.0f),
                         D2D1::Point2F(cx - 12.0f, cy + 12.0f),
                         ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);
        ctx.rt->DrawLine(D2D1::Point2F(cx - 12.0f, cy + 12.0f),
                         D2D1::Point2F(cx + 28.0f, image_rect.bottom - 34.0f),
                         ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);
        ctx.rt->DrawLine(D2D1::Point2F(cx + 28.0f, image_rect.bottom - 34.0f),
                         D2D1::Point2F(image_rect.right - 26.0f, image_rect.bottom - 20.0f),
                         ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);
        std::wstring hint = src.empty() ? L"🖼️ 图片占位" : L"⚠️ 图片加载失败";
        draw_text(ctx, hint, style, muted, image_rect.left + 8.0f, cy - 16.0f,
                  image_rect.right - image_rect.left - 16.0f, 32.0f, 0.95f);
    }
    ctx.rt->DrawRoundedRectangle(ROUNDED(image_rect, 5.0f, 5.0f),
        ctx.get_brush(with_alpha(accent, 0x88)), 1.0f);

    std::wstring caption = alt.empty() ? (src.empty() ? L"🖼️ 图片" : src) : alt;
    draw_text(ctx, caption, style, muted,
              (float)style.pad_left, (float)bounds.h - 34.0f,
              (float)bounds.w - style.pad_left - style.pad_right, 28.0f,
              0.92f);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Image::paint_overlay(RenderContext& ctx) {
    if (!visible || !preview_open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);

    int ox = 0;
    int oy = 0;
    get_absolute_pos(ox, oy);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)-ox, (float)-oy));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }

    D2D1_RECT_F shade = { 0.0f, 0.0f, (float)root_w, (float)root_h };
    ctx.rt->FillRectangle(shade, ctx.get_brush(dark ? 0xCC000000 : 0x99000000));

    D2D1_RECT_F panel = preview_rect();
    Color bg = dark ? 0xFF202230 : 0xFFFFFFFF;
    ctx.rt->FillRoundedRectangle(ROUNDED(panel, 8.0f, 8.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(panel.left + 0.5f, panel.top + 0.5f,
        panel.right - 0.5f, panel.bottom - 0.5f), 8.0f, 8.0f),
        ctx.get_brush(t->border_default), 1.0f);

    D2D1_RECT_F close = { panel.right - 44.0f, panel.top + 8.0f, panel.right - 12.0f, panel.top + 40.0f };
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((close.left + close.right) * 0.5f,
        (close.top + close.bottom) * 0.5f), 15.0f, 15.0f), ctx.get_brush(t->button_hover));
    draw_text(ctx, L"X", style, t->text_primary, close.left, close.top, close.right - close.left, close.bottom - close.top);

    D2D1_RECT_F media = { panel.left + 22.0f, panel.top + 48.0f, panel.right - 22.0f, panel.bottom - 48.0f };
    ctx.rt->FillRoundedRectangle(ROUNDED(media, 6.0f, 6.0f),
        ctx.get_brush(dark ? 0xFF242637 : 0xFFF5F7FA));
    if (ensure_bitmap(ctx)) {
        D2D1_SIZE_F size = m_bitmap->GetSize();
        D2D1_RECT_F dest = media;
        float box_w = media.right - media.left;
        float box_h = media.bottom - media.top;
        if (size.width > 0.0f && size.height > 0.0f) {
            float s = (std::min)(box_w / size.width, box_h / size.height);
            s *= (float)preview_scale_percent / 100.0f;
            float dw = size.width * s;
            float dh = size.height * s;
            dest = D2D1::RectF(media.left + (box_w - dw) * 0.5f + (float)preview_offset_x,
                               media.top + (box_h - dh) * 0.5f + (float)preview_offset_y,
                               media.left + (box_w + dw) * 0.5f + (float)preview_offset_x,
                               media.top + (box_h + dh) * 0.5f + (float)preview_offset_y);
        }
        ctx.push_clip(media);
        ctx.rt->DrawBitmap(m_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
        ctx.pop_clip();
    } else {
        draw_text(ctx, L"\u26A0\uFE0F \u56FE\u7247\u9884\u89C8\u4E0D\u53EF\u7528", style, t->text_secondary,
                  media.left, media.top, media.right - media.left, media.bottom - media.top);
    }
    std::wstring caption = alt.empty() ? L"\U0001F5BC\uFE0F \u56FE\u7247\u9884\u89C8" : alt;
    draw_text(ctx, caption, style, t->text_primary, panel.left + 22.0f, panel.bottom - 40.0f,
              panel.right - panel.left - 44.0f, 28.0f, 0.96f);

    ctx.rt->SetTransform(saved);
}

Element* Image::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) ? this : nullptr;
}

Element* Image::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !preview_open) return nullptr;
    int ox = 0;
    int oy = 0;
    get_absolute_pos(ox, oy);
    D2D1_RECT_F pr = preview_rect();
    float lx = (float)(x - ox);
    float ly = (float)(y - oy);
    return (lx >= pr.left && lx <= pr.right && ly >= pr.top && ly <= pr.bottom) ? this : nullptr;
}

void Image::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_pressed_preview = preview_open;
    invalidate();
}

void Image::on_mouse_up(int x, int y, MouseButton) {
    if (m_pressed_preview) {
        D2D1_RECT_F pr = preview_rect();
        D2D1_RECT_F close = { pr.right - 44.0f, pr.top + 8.0f, pr.right - 12.0f, pr.top + 40.0f };
        if ((float)x >= close.left && (float)x <= close.right && (float)y >= close.top && (float)y <= close.bottom) {
            preview_open = false;
        }
    } else if (preview_enabled && load_status == 1 && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        preview_open = true;
    }
    pressed = false;
    m_pressed_preview = false;
    invalidate();
}

void Image::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE) preview_open = false;
    else if ((vk == VK_RETURN || vk == VK_SPACE) && preview_enabled && load_status == 1) preview_open = !preview_open;
    else if (preview_open && (vk == VK_OEM_PLUS || vk == VK_ADD)) set_preview_transform(preview_scale_percent + 10, preview_offset_x, preview_offset_y);
    else if (preview_open && (vk == VK_OEM_MINUS || vk == VK_SUBTRACT)) set_preview_transform(preview_scale_percent - 10, preview_offset_x, preview_offset_y);
    else if (preview_open && vk == VK_LEFT) set_preview_transform(preview_scale_percent, preview_offset_x - 10, preview_offset_y);
    else if (preview_open && vk == VK_RIGHT) set_preview_transform(preview_scale_percent, preview_offset_x + 10, preview_offset_y);
    else if (preview_open && vk == VK_UP) set_preview_transform(preview_scale_percent, preview_offset_x, preview_offset_y - 10);
    else if (preview_open && vk == VK_DOWN) set_preview_transform(preview_scale_percent, preview_offset_x, preview_offset_y + 10);
    invalidate();
}

void Image::on_blur() {
    has_focus = false;
    preview_open = false;
    invalidate();
}
