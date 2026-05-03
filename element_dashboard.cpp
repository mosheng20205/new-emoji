#include "element_dashboard.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int clamp_percent(int value) {
    return (std::max)(0, (std::min)(100, value));
}

static int clamp_range_value(int value, int min_value, int max_value) {
    if (max_value <= min_value) return min_value;
    return (std::max)(min_value, (std::min)(max_value, value));
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color status_color(const Theme* t, int status) {
    switch (status) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static void draw_shell(RenderContext& ctx, HWND hwnd, const Element& el) {
    const Theme* t = theme_for_window(hwnd);
    bool dark = is_dark_theme_for_window(hwnd);
    Color bg = el.style.bg_color ? el.style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = el.style.border_color ? el.style.border_color : t->border_default;
    float radius = el.style.corner_radius > 0.0f ? el.style.corner_radius : 6.0f;
    D2D1_RECT_F rect = { 0, 0, (float)el.bounds.w, (float)el.bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)el.bounds.w - 0.5f, (float)el.bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);
}

static D2D1_POINT_2F polar(float cx, float cy, float radius, float angle) {
    return D2D1::Point2F(cx + std::cos(angle) * radius, cy + std::sin(angle) * radius);
}

static void draw_arc(RenderContext& ctx, float cx, float cy, float radius,
                     float start, float end, Color color, float stroke) {
    if (!g_d2d_factory || end <= start || radius <= 0.0f || stroke <= 0.0f) return;
    ID2D1PathGeometry* geo = nullptr;
    if (FAILED(g_d2d_factory->CreatePathGeometry(&geo)) || !geo) return;
    ID2D1GeometrySink* sink = nullptr;
    if (SUCCEEDED(geo->Open(&sink)) && sink) {
        float span = end - start;
        D2D1_POINT_2F p0 = polar(cx, cy, radius, start);
        D2D1_POINT_2F p1 = polar(cx, cy, radius, end);
        sink->BeginFigure(p0, D2D1_FIGURE_BEGIN_HOLLOW);
        sink->AddArc(D2D1::ArcSegment(
            p1, D2D1::SizeF(radius, radius), 0.0f,
            D2D1_SWEEP_DIRECTION_CLOCKWISE,
            span > 3.1415926f ? D2D1_ARC_SIZE_LARGE : D2D1_ARC_SIZE_SMALL));
        sink->EndFigure(D2D1_FIGURE_END_OPEN);
        sink->Close();
        sink->Release();
        ctx.rt->DrawGeometry(geo, ctx.get_brush(color), stroke);
    }
    geo->Release();
}

static float animate_toward(Element& el, float& shown, int target, ULONGLONG& start) {
    if (start == 0) {
        shown = (float)target;
        return shown;
    }
    ULONGLONG elapsed = GetTickCount64() - start;
    float p = (std::min)(1.0f, (float)elapsed / 280.0f);
    shown = shown + ((float)target - shown) * (1.0f - (1.0f - p) * (1.0f - p));
    if (p >= 1.0f || std::fabs(shown - (float)target) < 0.05f) {
        shown = (float)target;
        start = 0;
        if (el.owner_hwnd) KillTimer(el.owner_hwnd, 0x6000 + el.id);
    } else {
        if (el.owner_hwnd) SetTimer(el.owner_hwnd, 0x6000 + el.id, 16, nullptr);
    }
    return shown;
}

void Gauge::set_title(const std::wstring& next_title) { title = next_title; invalidate(); }
void Gauge::set_value(int next_value) {
    value = clamp_range_value(next_value, min_value, max_value);
    if (display_value <= 0.0f) display_value = (float)value;
    anim_start = GetTickCount64();
    invalidate();
}
void Gauge::set_caption(const std::wstring& next_caption) { caption = next_caption; invalidate(); }
void Gauge::set_status(int next_status) { status = (std::max)(0, (std::min)(3, next_status)); invalidate(); }

void Gauge::set_options(int min_value_arg, int max_value_arg, int warning_value_arg,
                        int danger_value_arg, int stroke_width_arg) {
    if (max_value_arg <= min_value_arg) max_value_arg = min_value_arg + 100;
    min_value = min_value_arg;
    max_value = max_value_arg;
    warning_value = clamp_range_value(warning_value_arg, min_value, max_value);
    danger_value = clamp_range_value(danger_value_arg, min_value, max_value);
    stroke_width = (std::max)(6, (std::min)(32, stroke_width_arg));
    value = clamp_range_value(value, min_value, max_value);
    invalidate();
}

void Gauge::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float shown_value = animate_toward(*this, display_value, value, anim_start);
    float normalized = (max_value == min_value) ? 0.0f : (shown_value - (float)min_value) / (float)(max_value - min_value);
    normalized = (std::max)(0.0f, (std::min)(1.0f, normalized));
    Color accent = status_color(t, status);
    if (status == 0) {
        if (value >= danger_value) accent = 0xFFF56C6C;
        else if (value >= warning_value) accent = 0xFFE6A23C;
    }
    Color track = dark ? 0xFF313244 : 0xFFE4E7ED;
    Color muted = t->text_secondary;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this);
    draw_text(ctx, title.empty() ? L"🎛️ 仪表盘" : title, style, t->text_primary,
              (float)style.pad_left, 9.0f, (float)bounds.w - style.pad_left - style.pad_right,
              28.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    float cx = (float)bounds.w * 0.5f;
    float cy = (float)bounds.h * 0.68f;
    float radius = (std::min)((float)bounds.w * 0.36f, (float)bounds.h * 0.36f);
    float start = 140.0f * 3.1415926f / 180.0f;
    float span = 260.0f * 3.1415926f / 180.0f;
    float stroke = (std::max)((float)stroke_width, style.font_size * 0.82f);
    draw_arc(ctx, cx, cy, radius, start, start + span, track, stroke);
    draw_arc(ctx, cx, cy, radius, start, start + span * normalized, accent, stroke + 1.0f);

    for (int i = 0; i <= 5; ++i) {
        float a = start + span * (float)i / 5.0f;
        D2D1_POINT_2F p0 = polar(cx, cy, radius - stroke * 0.5f - 4.0f, a);
        D2D1_POINT_2F p1 = polar(cx, cy, radius - stroke * 0.5f - 11.0f, a);
        ctx.rt->DrawLine(p0, p1, ctx.get_brush(with_alpha(muted, 0x88)), 1.0f);
    }

    float needle_a = start + span * normalized;
    D2D1_POINT_2F np = polar(cx, cy, radius - stroke - 10.0f, needle_a);
    ctx.rt->DrawLine(D2D1::Point2F(cx, cy), np, ctx.get_brush(accent), 2.0f);
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), 5.0f, 5.0f), ctx.get_brush(accent));

    draw_text(ctx, std::to_wstring((int)std::lround(shown_value)) + L"%", style, t->text_primary,
              cx - 52.0f, cy - 40.0f, 104.0f, 34.0f, 1.42f,
              DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_TEXT_ALIGNMENT_CENTER);
    draw_text(ctx, caption.empty() ? L"📍 当前状态" : caption, style, muted,
              (float)style.pad_left, (float)bounds.h - 38.0f,
              (float)bounds.w - style.pad_left - style.pad_right, 24.0f, 0.9f,
              DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void RingProgress::set_title(const std::wstring& next_title) { title = next_title; invalidate(); }
void RingProgress::set_value(int next_value) {
    value = clamp_percent(next_value);
    if (display_value <= 0.0f) display_value = (float)value;
    anim_start = GetTickCount64();
    invalidate();
}
void RingProgress::set_label(const std::wstring& next_label) { label = next_label; invalidate(); }
void RingProgress::set_status(int next_status) { status = (std::max)(0, (std::min)(3, next_status)); invalidate(); }

void RingProgress::set_options(int stroke_width_value, bool show_center_value) {
    stroke_width = (std::max)(6, (std::min)(34, stroke_width_value));
    show_center = show_center_value;
    invalidate();
}

void RingProgress::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color accent = status_color(t, status);
    Color track = dark ? 0xFF313244 : 0xFFE4E7ED;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this);
    draw_text(ctx, title.empty() ? L"⭕ 环形进度" : title, style, t->text_primary,
              (float)style.pad_left, 9.0f, (float)bounds.w - style.pad_left - style.pad_right,
              28.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    float radius = (std::min)((float)bounds.w * 0.28f, (float)bounds.h * 0.28f);
    float cx = (float)bounds.w * 0.5f;
    float cy = (float)bounds.h * 0.52f;
    float stroke = (std::max)((float)stroke_width, style.font_size * 0.75f);
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), radius, radius),
                        ctx.get_brush(track), stroke);
    float start = -90.0f * 3.1415926f / 180.0f;
    float shown_value = animate_toward(*this, display_value, value, anim_start);
    float end = start + 6.2831853f * (shown_value >= 100.0f ? 0.999f : shown_value / 100.0f);
    draw_arc(ctx, cx, cy, radius, start, end, accent, stroke + 1.0f);
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), radius - stroke - 7.0f, radius - stroke - 7.0f),
                        ctx.get_brush(with_alpha(accent, dark ? 0x18 : 0x0D)));

    if (show_center) {
        draw_text(ctx, std::to_wstring((int)std::lround(shown_value)) + L"%", style, t->text_primary,
                  cx - 54.0f, cy - 24.0f, 108.0f, 34.0f, 1.48f,
                  DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    draw_text(ctx, label.empty() ? L"🎯 完成率" : label, style, t->text_secondary,
              (float)style.pad_left, (float)bounds.h - 38.0f,
              (float)bounds.w - style.pad_left - style.pad_right, 24.0f, 0.9f,
              DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void BulletProgress::set_title(const std::wstring& next_title) { title = next_title; invalidate(); }
void BulletProgress::set_description(const std::wstring& next_description) { description = next_description; invalidate(); }
void BulletProgress::set_value(int next_value) {
    value = clamp_percent(next_value);
    if (display_value <= 0.0f) display_value = (float)value;
    anim_start = GetTickCount64();
    invalidate();
}
void BulletProgress::set_target(int next_target) { target = clamp_percent(next_target); invalidate(); }
void BulletProgress::set_status(int next_status) { status = (std::max)(0, (std::min)(3, next_status)); invalidate(); }

void BulletProgress::set_options(int good_threshold_value, int warn_threshold_value,
                                 bool show_target_value) {
    good_threshold = clamp_percent(good_threshold_value);
    warn_threshold = clamp_percent(warn_threshold_value);
    if (warn_threshold > good_threshold) std::swap(warn_threshold, good_threshold);
    show_target = show_target_value;
    invalidate();
}

void BulletProgress::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color accent = status_color(t, status);
    float shown_value = animate_toward(*this, display_value, value, anim_start);
    if (status == 0) {
        if (value >= good_threshold) accent = 0xFF67C23A;
        else if (value >= warn_threshold) accent = 0xFFE6A23C;
        else accent = 0xFFF56C6C;
    }
    Color track = dark ? 0xFF313244 : 0xFFE4E7ED;
    Color marker = dark ? 0xFFE5E7EB : 0xFF303133;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this);
    draw_text(ctx, title.empty() ? L"🧭 子弹进度" : title, style, t->text_primary,
              (float)style.pad_left, 8.0f, (float)bounds.w * 0.56f,
              24.0f, 0.96f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, description, style, t->text_secondary,
              (float)bounds.w * 0.48f, 8.0f,
              (float)bounds.w - (float)bounds.w * 0.48f - style.pad_right,
              24.0f, 0.84f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_TRAILING);

    float bar_x = (float)style.pad_left;
    float bar_y = 45.0f;
    float bar_w = (float)bounds.w - style.pad_left - style.pad_right;
    float bar_h = (std::max)(14.0f, style.font_size * 1.05f);
    D2D1_RECT_F track_rect = { bar_x, bar_y, bar_x + bar_w, bar_y + bar_h };
    ctx.rt->FillRoundedRectangle(ROUNDED(track_rect, 4.0f, 4.0f), ctx.get_brush(track));
    float fill_w = bar_w * shown_value / 100.0f;
    if (fill_w > 1.0f) {
        D2D1_RECT_F fill_rect = { bar_x, bar_y, bar_x + fill_w, bar_y + bar_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(fill_rect, 4.0f, 4.0f), ctx.get_brush(accent));
    }

    float target_x = bar_x + bar_w * (float)target / 100.0f;
    if (show_target) {
        ctx.rt->DrawLine(D2D1::Point2F(target_x, bar_y - 5.0f),
                         D2D1::Point2F(target_x, bar_y + bar_h + 5.0f),
                         ctx.get_brush(marker), 2.0f);
    }
    draw_text(ctx, std::to_wstring((int)std::lround(shown_value)) + L"%", style, t->text_primary,
              bar_x, bar_y + bar_h + 8.0f, 72.0f, 22.0f, 0.9f,
              DWRITE_FONT_WEIGHT_SEMI_BOLD);
    if (show_target) {
        draw_text(ctx, L"目标 " + std::to_wstring(target) + L"%", style, t->text_secondary,
                  bar_x + bar_w - 118.0f, bar_y + bar_h + 8.0f, 118.0f, 22.0f, 0.84f,
                  DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_TRAILING);
    }
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
