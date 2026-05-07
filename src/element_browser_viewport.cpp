#include "element_browser_viewport.h"
#include "element_image.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text,
                      const ElementStyle& style, Color color,
                      float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER,
                      DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

BrowserViewport::~BrowserViewport() {
    release_bitmap();
}

void BrowserViewport::release_bitmap() {
    if (bitmap) {
        bitmap->Release();
        bitmap = nullptr;
    }
    bitmap_rt = nullptr;
    bitmap_source.clear();
    bitmap_width = 0;
    bitmap_height = 0;
}

bool BrowserViewport::ensure_bitmap(RenderContext& ctx) {
    if (screenshot_source.empty()) return false;
    if (bitmap && bitmap_rt == ctx.rt && bitmap_source == screenshot_source) return true;
    release_bitmap();
    if (is_shared_remote_image_source(screenshot_source)) {
        std::wstring local;
        int status = resolve_shared_image_source(owner_hwnd, screenshot_source, local);
        if (status != 1) return false;
        if (load_shared_bitmap_from_path(ctx, local, &bitmap, &bitmap_width, &bitmap_height)) {
            bitmap_rt = ctx.rt;
            bitmap_source = screenshot_source;
            return true;
        }
    } else if (load_shared_bitmap_from_path(ctx, screenshot_source, &bitmap, &bitmap_width, &bitmap_height)) {
        bitmap_rt = ctx.rt;
        bitmap_source = screenshot_source;
        return true;
    }
    return false;
}

void BrowserViewport::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    ctx.push_clip({0, 0, (float)bounds.w, (float)bounds.h});

    const Theme* t = theme_for_window(owner_hwnd);
    D2D1_RECT_F bg = {0, 0, (float)bounds.w, (float)bounds.h};
    ctx.rt->FillRectangle(bg, ctx.get_brush(t->chrome_viewport_bg));

    if (state == 2 && ensure_bitmap(ctx) && bitmap && bitmap_width > 0 && bitmap_height > 0) {
        float scale = (std::min)((float)bounds.w / (float)bitmap_width,
                                 (float)bounds.h / (float)bitmap_height);
        if (scale <= 0.0f) scale = 1.0f;
        float w = bitmap_width * scale;
        float h = bitmap_height * scale;
        D2D1_RECT_F r = {(bounds.w - w) * 0.5f, (bounds.h - h) * 0.5f,
                         (bounds.w + w) * 0.5f, (bounds.h + h) * 0.5f};
        ctx.rt->DrawBitmap(bitmap, r, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
    } else {
        ElementStyle icon_style = style;
        icon_style.font_size = 44.0f;
        ElementStyle title_style = style;
        title_style.font_size = 22.0f;
        ElementStyle desc_style = style;
        desc_style.font_size = 14.0f;
        std::wstring shown_icon = state == 3 ? L"\u26A0\uFE0F" : (icon.empty() ? L"\U0001F310" : icon);
        std::wstring shown_title = state == 1 ? L"页面加载中" : (title.empty() ? L"新标签页" : title);
        std::wstring shown_desc = state == 1 ? L"正在准备页面内容，请稍候。" : description;
        float cy = (float)bounds.h * 0.42f;
        draw_text(ctx, shown_icon, icon_style, t->chrome_viewport_fg,
                  0.0f, cy - 82.0f, (float)bounds.w, 60.0f);
        draw_text(ctx, shown_title, title_style, t->chrome_viewport_fg,
                  32.0f, cy - 20.0f, (float)bounds.w - 64.0f, 36.0f);
        draw_text(ctx, shown_desc, desc_style, t->text_secondary,
                  64.0f, cy + 18.0f, (float)bounds.w - 128.0f, 52.0f);
    }

    if (loading || state == 1) {
        int p = (std::max)(0, (std::min)(100, progress));
        D2D1_RECT_F track = {0.0f, 0.0f, (float)bounds.w, 3.0f};
        D2D1_RECT_F bar = {0.0f, 0.0f, (float)bounds.w * p / 100.0f, 3.0f};
        ctx.rt->FillRectangle(track, ctx.get_brush(t->chrome_toolbar_separator));
        ctx.rt->FillRectangle(bar, ctx.get_brush(t->accent));
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void BrowserViewport::set_state(int next_state) {
    state = (std::max)(0, (std::min)(4, next_state));
    invalidate();
}

void BrowserViewport::set_placeholder(const std::wstring& next_title,
                                      const std::wstring& next_desc,
                                      const std::wstring& next_icon) {
    title = next_title.empty() ? L"新标签页" : next_title;
    description = next_desc;
    icon = next_icon.empty() ? L"\U0001F310" : next_icon;
    invalidate();
}

void BrowserViewport::set_loading(bool value, int next_progress) {
    loading = value;
    progress = (std::max)(0, (std::min)(100, next_progress));
    if (loading) state = 1;
    invalidate();
}

void BrowserViewport::set_screenshot_source(const std::wstring& source) {
    screenshot_source = source;
    release_bitmap();
    if (!screenshot_source.empty()) state = 2;
    invalidate();
}
