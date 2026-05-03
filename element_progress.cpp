#include "element_progress.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static Color progress_color(const Theme* t, int status) {
    switch (status) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

void Progress::set_percentage(int value) {
    if (value < 0) value = 0;
    if (value > 100) value = 100;
    percentage = value;
    invalidate();
}

void Progress::set_status(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    status = value;
    invalidate();
}

void Progress::set_show_text(bool value) {
    show_text = value;
    invalidate();
}

void Progress::set_options(int type_value, int stroke_width_value, bool show_text_value) {
    if (type_value < 0) type_value = 0;
    if (type_value > 1) type_value = 1;
    progress_type = type_value;
    if (stroke_width_value < 0) stroke_width_value = 0;
    if (stroke_width_value > 48) stroke_width_value = 48;
    stroke_width = stroke_width_value;
    show_text = show_text_value;
    invalidate();
}

void Progress::set_format_options(int text_format_value, bool striped_value) {
    if (text_format_value < 0) text_format_value = 0;
    if (text_format_value > 2) text_format_value = 2;
    text_format = text_format_value;
    striped = striped_value;
    invalidate();
}

static std::wstring progress_text(const Progress& progress) {
    std::wstring pct = std::to_wstring(progress.percentage) + L"%";
    if (progress.text_format == 1) {
        switch (progress.status) {
        case 1: return L"成功 " + pct;
        case 2: return L"警告 " + pct;
        case 3: return L"异常 " + pct;
        default: return L"进行中 " + pct;
        }
    }
    if (progress.text_format == 2 && !progress.text.empty()) {
        return progress.text + L" " + pct;
    }
    return pct;
}

void Progress::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color track = style.bg_color ? style.bg_color : (dark ? 0xFF313244 : 0xFFE4E7ED);
    Color fill = style.border_color ? style.border_color : progress_color(t, status);

    if (progress_type == 1) {
        float size = (float)(std::min)(bounds.w, bounds.h);
        float cx = (float)bounds.w * 0.5f;
        float cy = (float)bounds.h * 0.5f;
        float sw = stroke_width > 0 ? (float)stroke_width : (std::max)(4.0f, size * 0.08f);
        float radius = (std::max)(4.0f, size * 0.5f - sw * 0.5f - 2.0f);
        D2D1_ELLIPSE ellipse = D2D1::Ellipse(D2D1::Point2F(cx, cy), radius, radius);
        ctx.rt->DrawEllipse(ellipse, ctx.get_brush(track), sw);

        float sweep = 360.0f * (float)percentage / 100.0f;
        if (sweep > 0.0f) {
            ID2D1PathGeometry* geom = nullptr;
            if (SUCCEEDED(g_d2d_factory->CreatePathGeometry(&geom)) && geom) {
                ID2D1GeometrySink* sink = nullptr;
                if (SUCCEEDED(geom->Open(&sink)) && sink) {
                    float start_deg = -90.0f;
                    float end_deg = start_deg + sweep;
                    float pi = 3.1415926535f;
                    float start_rad = start_deg * pi / 180.0f;
                    float end_rad = end_deg * pi / 180.0f;
                    D2D1_POINT_2F start = D2D1::Point2F(cx + cosf(start_rad) * radius,
                                                        cy + sinf(start_rad) * radius);
                    D2D1_POINT_2F end = D2D1::Point2F(cx + cosf(end_rad) * radius,
                                                      cy + sinf(end_rad) * radius);
                    sink->BeginFigure(start, D2D1_FIGURE_BEGIN_HOLLOW);
                    D2D1_ARC_SEGMENT arc = {};
                    arc.point = end;
                    arc.size = D2D1::SizeF(radius, radius);
                    arc.rotationAngle = 0.0f;
                    arc.sweepDirection = D2D1_SWEEP_DIRECTION_CLOCKWISE;
                    arc.arcSize = sweep > 180.0f ? D2D1_ARC_SIZE_LARGE : D2D1_ARC_SIZE_SMALL;
                    sink->AddArc(arc);
                    sink->EndFigure(D2D1_FIGURE_END_OPEN);
                    sink->Close();
                    sink->Release();
                    ctx.rt->DrawGeometry(geom, ctx.get_brush(fill), sw);
                }
                geom->Release();
            }
        }

        if (show_text) {
            std::wstring pct = progress_text(*this);
            draw_text(ctx, pct, style, fg, 0.0f, 0.0f, (float)bounds.w, (float)bounds.h,
                      DWRITE_TEXT_ALIGNMENT_CENTER);
        }
        ctx.rt->SetTransform(saved);
        return;
    }

    float label_w = text.empty() ? 0.0f : (std::min)((float)bounds.w * 0.28f, 120.0f * style.font_size / 14.0f);
    if (!text.empty()) {
        draw_text(ctx, text, style, fg, (float)style.pad_left, 0.0f,
                  label_w, (float)bounds.h);
    }

    float percent_w = show_text ? 48.0f * style.font_size / 14.0f : 0.0f;
    float bar_x = (float)style.pad_left + label_w + (label_w > 0.0f ? 10.0f : 0.0f);
    float bar_w = (float)bounds.w - bar_x - (float)style.pad_right - percent_w;
    if (bar_w < 1.0f) bar_w = 1.0f;
    float bar_h = stroke_width > 0 ? (float)stroke_width : (std::max)(6.0f, style.font_size * 0.55f);
    if (bar_h > bounds.h - 4.0f) bar_h = (float)bounds.h - 4.0f;
    if (bar_h < 2.0f) bar_h = 2.0f;
    float bar_y = ((float)bounds.h - bar_h) * 0.5f;
    float radius = bar_h * 0.5f;

    D2D1_RECT_F track_rect = { bar_x, bar_y, bar_x + bar_w, bar_y + bar_h };
    ctx.rt->FillRoundedRectangle(ROUNDED(track_rect, radius, radius), ctx.get_brush(track));

    float fill_w = bar_w * (float)percentage / 100.0f;
    if (fill_w > 0.5f) {
        D2D1_RECT_F fill_rect = { bar_x, bar_y, bar_x + fill_w, bar_y + bar_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(fill_rect, radius, radius), ctx.get_brush(fill));
        if (striped) {
            Color stripe = ((fill >> 24) > 0x80) ? ((fill & 0x00FFFFFF) | 0x33000000) : fill;
            float step = (std::max)(8.0f, bar_h * 1.8f);
            for (float sx = bar_x - bar_h; sx < bar_x + fill_w; sx += step) {
                ctx.rt->DrawLine(D2D1::Point2F(sx, bar_y + bar_h),
                                 D2D1::Point2F(sx + bar_h, bar_y),
                                 ctx.get_brush(stripe), 2.0f);
            }
        }
    }

    if (show_text) {
        std::wstring pct = progress_text(*this);
        draw_text(ctx, pct, style, fg, bar_x + bar_w + 8.0f, 0.0f,
                  percent_w - 8.0f, (float)bounds.h);
    }

    ctx.rt->SetTransform(saved);
}
