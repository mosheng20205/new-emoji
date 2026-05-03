#include "element_charts.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color palette_color(const Theme* t, int index) {
    static const Color colors[] = {
        0xFF1E66F5, 0xFF67C23A, 0xFFE6A23C, 0xFFF56C6C,
        0xFF8B5CF6, 0xFF14B8A6, 0xFFEC4899, 0xFF64748B
    };
    if (index == 0) return t->accent;
    return colors[index % (int)(sizeof(colors) / sizeof(colors[0]))];
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static float max_value(const std::vector<ChartPoint>& values) {
    float out = 1.0f;
    for (const auto& item : values) out = (std::max)(out, item.value);
    return out;
}

static float max_series_value(const std::vector<std::vector<ChartPoint>>& values) {
    float out = 1.0f;
    for (const auto& series : values) {
        for (const auto& item : series) out = (std::max)(out, item.value);
    }
    return out;
}

static float total_value(const std::vector<ChartPoint>& values) {
    float total = 0.0f;
    for (const auto& item : values) total += (std::max)(0.0f, item.value);
    return total > 0.0f ? total : 1.0f;
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

static void draw_shell(RenderContext& ctx, HWND hwnd, const Element& el, const std::wstring& title) {
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
    draw_text(ctx, title, el.style, t->text_primary, (float)el.style.pad_left, 8.0f,
              (float)el.bounds.w - el.style.pad_left - el.style.pad_right,
              28.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
}

static D2D1_POINT_2F polar(float cx, float cy, float radius, float angle) {
    return D2D1::Point2F(cx + std::cos(angle) * radius, cy + std::sin(angle) * radius);
}

static void draw_empty(RenderContext& ctx, HWND hwnd, const Element& el, const std::wstring& text) {
    const Theme* t = theme_for_window(hwnd);
    draw_text(ctx, text, el.style, t->text_secondary,
              (float)el.style.pad_left, (float)el.bounds.h * 0.45f - 12.0f,
              (float)el.bounds.w - el.style.pad_left - el.style.pad_right,
              24.0f, 0.92f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
}

static D2D1_RECT_F line_plot_rect(const LineChart& chart) {
    return D2D1::RectF((float)chart.style.pad_left + 16.0f, 46.0f,
        (float)chart.bounds.w - chart.style.pad_right - 8.0f,
        (float)chart.bounds.h - chart.style.pad_bottom - 24.0f);
}

static D2D1_RECT_F bar_plot_rect(const BarChart& chart) {
    float label_h = chart.orientation == 1
        ? (std::max)(22.0f, chart.style.font_size * 1.55f)
        : 0.0f;
    return D2D1::RectF((float)chart.style.pad_left, 50.0f,
        (float)chart.bounds.w - chart.style.pad_right,
        (float)chart.bounds.h - chart.style.pad_bottom - label_h);
}

void LineChart::set_title(const std::wstring& value) { title = value; invalidate(); }
void LineChart::set_points(const std::vector<ChartPoint>& values) {
    points = values;
    series.clear();
    if (selected_index >= (int)points.size()) selected_index = points.empty() ? -1 : (int)points.size() - 1;
    invalidate();
}
void LineChart::set_series(const std::vector<std::vector<ChartPoint>>& values) {
    series = values;
    points = series.empty() ? std::vector<ChartPoint>() : series[0];
    if (selected_index >= (int)points.size()) selected_index = points.empty() ? -1 : (int)points.size() - 1;
    invalidate();
}
void LineChart::set_chart_style(int value) { chart_style = value < 0 ? 0 : (value > 1 ? 1 : value); invalidate(); }
void LineChart::set_selected_index(int value) {
    if (points.empty()) selected_index = -1;
    else selected_index = (std::max)(-1, (std::min)((int)points.size() - 1, value));
    invalidate();
}
void LineChart::set_options(int style_value, bool axis, bool area, bool tooltip) {
    set_chart_style(style_value);
    show_axis = axis;
    show_area = area;
    show_tooltip = tooltip;
    invalidate();
}

int LineChart::point_at(int x, int y) const {
    if (points.empty()) return -1;
    D2D1_RECT_F r = line_plot_rect(*this);
    if (x < r.left - 10 || x > r.right + 10 || y < r.top - 14 || y > r.bottom + 14) return -1;
    float maxv = max_value(points);
    float best_dist = 999999.0f;
    int best = -1;
    for (size_t i = 0; i < points.size(); ++i) {
        float px = points.size() > 1 ? r.left + (r.right - r.left) * (float)i / (float)(points.size() - 1) : (r.left + r.right) * 0.5f;
        float py = r.bottom - (r.bottom - r.top) * (std::max)(0.0f, points[i].value) / maxv;
        float dx = px - (float)x;
        float dy = py - (float)y;
        float d = dx * dx + dy * dy;
        if (d < best_dist) {
            best_dist = d;
            best = (int)i;
        }
    }
    return best_dist <= 180.0f ? best : -1;
}

void LineChart::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color grid = dark ? 0xFF313244 : 0xFFE4E7ED;
    Color muted = t->text_secondary;
    Color accent = t->accent;
    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this, title.empty() ? L"📈 折线趋势" : title);
    if (points.empty() && series.empty()) {
        draw_empty(ctx, owner_hwnd, *this, L"📭 暂无折线数据");
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }
    D2D1_RECT_F plot = line_plot_rect(*this);
    float left = plot.left;
    float top = plot.top, right = plot.right;
    float bottom = plot.bottom;
    if (right <= left || bottom <= top) { ctx.pop_clip(); ctx.rt->SetTransform(saved); return; }
    if (show_axis) {
        for (int i = 0; i < 4; ++i) {
            float y = top + (bottom - top) * i / 3.0f;
            ctx.rt->DrawLine(D2D1::Point2F(left, y), D2D1::Point2F(right, y), ctx.get_brush(grid), 1.0f);
        }
        ctx.rt->DrawLine(D2D1::Point2F(left, top), D2D1::Point2F(left, bottom), ctx.get_brush(grid), 1.0f);
        ctx.rt->DrawLine(D2D1::Point2F(left, bottom), D2D1::Point2F(right, bottom), ctx.get_brush(grid), 1.0f);
    }
    if (!series.empty()) {
        float maxv_all = max_series_value(series);
        for (size_t s = 0; s < series.size(); ++s) {
            const auto& line = series[s];
            if (line.size() < 2 || !g_d2d_factory) continue;
            ID2D1PathGeometry* geo = nullptr;
            if (SUCCEEDED(g_d2d_factory->CreatePathGeometry(&geo)) && geo) {
                ID2D1GeometrySink* sink = nullptr;
                if (SUCCEEDED(geo->Open(&sink)) && sink) {
                    for (size_t i = 0; i < line.size(); ++i) {
                        float x = left + (right - left) * (float)i / (float)(line.size() - 1);
                        float y = bottom - (bottom - top) * (std::max)(0.0f, line[i].value) / maxv_all;
                        if (i == 0) sink->BeginFigure(D2D1::Point2F(x, y), D2D1_FIGURE_BEGIN_HOLLOW);
                        else sink->AddLine(D2D1::Point2F(x, y));
                    }
                    sink->EndFigure(D2D1_FIGURE_END_OPEN);
                    sink->Close();
                    sink->Release();
                    ctx.rt->DrawGeometry(geo, ctx.get_brush(palette_color(t, (int)s)), s == 0 ? 3.0f : 2.0f);
                }
                geo->Release();
            }
            for (size_t i = 0; i < line.size(); ++i) {
                float x = line.size() > 1 ? left + (right - left) * (float)i / (float)(line.size() - 1) : (left + right) * 0.5f;
                float y = bottom - (bottom - top) * (std::max)(0.0f, line[i].value) / maxv_all;
                ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(x, y), s == 0 ? 4.6f : 3.2f, s == 0 ? 4.6f : 3.2f),
                                    ctx.get_brush(palette_color(t, (int)s)));
            }
            if (!line.empty()) {
                float ly = 10.0f + (float)s * 18.0f;
                float lx = (float)bounds.w - style.pad_right - 92.0f;
                ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(lx, ly + 5.0f, lx + 12.0f, ly + 13.0f), 3.0f, 3.0f),
                                             ctx.get_brush(palette_color(t, (int)s)));
                draw_text(ctx, L"序列 " + std::to_wstring((int)s + 1), style, muted,
                          lx + 16.0f, ly, 70.0f, 18.0f, 0.72f);
            }
        }
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }
    if (show_area && points.size() >= 2 && g_d2d_factory) {
        ID2D1PathGeometry* area = nullptr;
        if (SUCCEEDED(g_d2d_factory->CreatePathGeometry(&area)) && area) {
            ID2D1GeometrySink* sink = nullptr;
            if (SUCCEEDED(area->Open(&sink)) && sink) {
                float maxv = max_value(points);
                sink->BeginFigure(D2D1::Point2F(left, bottom), D2D1_FIGURE_BEGIN_FILLED);
                for (size_t i = 0; i < points.size(); ++i) {
                    float x = points.size() > 1 ? left + (right - left) * (float)i / (float)(points.size() - 1) : (left + right) * 0.5f;
                    float y = bottom - (bottom - top) * (std::max)(0.0f, points[i].value) / maxv;
                    sink->AddLine(D2D1::Point2F(x, y));
                }
                sink->AddLine(D2D1::Point2F(right, bottom));
                sink->EndFigure(D2D1_FIGURE_END_CLOSED);
                sink->Close();
                sink->Release();
                ctx.rt->FillGeometry(area, ctx.get_brush(with_alpha(accent, dark ? 0x22 : 0x18)));
            }
            area->Release();
        }
    }
    if (points.size() >= 2 && g_d2d_factory) {
        ID2D1PathGeometry* geo = nullptr;
        if (SUCCEEDED(g_d2d_factory->CreatePathGeometry(&geo)) && geo) {
            ID2D1GeometrySink* sink = nullptr;
            if (SUCCEEDED(geo->Open(&sink)) && sink) {
                float maxv = max_value(points);
                for (size_t i = 0; i < points.size(); ++i) {
                    float x = left + (right - left) * (float)i / (float)(points.size() - 1);
                    float y = bottom - (bottom - top) * (std::max)(0.0f, points[i].value) / maxv;
                    if (i == 0) sink->BeginFigure(D2D1::Point2F(x, y), D2D1_FIGURE_BEGIN_HOLLOW);
                    else sink->AddLine(D2D1::Point2F(x, y));
                }
                sink->EndFigure(D2D1_FIGURE_END_OPEN);
                sink->Close();
                sink->Release();
                ctx.rt->DrawGeometry(geo, ctx.get_brush(accent), chart_style == 1 ? 3.0f : 2.0f);
            }
            geo->Release();
        }
    }
    float maxv = max_value(points);
    for (size_t i = 0; i < points.size(); ++i) {
        float x = points.size() > 1 ? left + (right - left) * (float)i / (float)(points.size() - 1) : (left + right) * 0.5f;
        float y = bottom - (bottom - top) * (std::max)(0.0f, points[i].value) / maxv;
        bool selected = (int)i == selected_index;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(x, y),
            selected ? 6.2f : 3.8f, selected ? 6.2f : 3.8f), ctx.get_brush(accent));
        if (i == 0 || i + 1 == points.size()) draw_text(ctx, points[i].label, style, muted, x - 28.0f, bottom + 3.0f, 56.0f, 18.0f, 0.78f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    if (show_tooltip && selected_index >= 0 && selected_index < (int)points.size()) {
        float maxv = max_value(points);
        float x = points.size() > 1 ? left + (right - left) * (float)selected_index / (float)(points.size() - 1) : (left + right) * 0.5f;
        float y = bottom - (bottom - top) * (std::max)(0.0f, points[selected_index].value) / maxv;
        float tw = 112.0f, th = 34.0f;
        float tx = (std::min)((std::max)(x - tw * 0.5f, 6.0f), (float)bounds.w - tw - 6.0f);
        float ty = (std::max)(42.0f, y - th - 10.0f);
        D2D1_RECT_F box = { tx, ty, tx + tw, ty + th };
        ctx.rt->FillRoundedRectangle(ROUNDED(box, 5.0f, 5.0f), ctx.get_brush(dark ? 0xEE111827 : 0xEEFFFFFF));
        ctx.rt->DrawRoundedRectangle(ROUNDED(box, 5.0f, 5.0f), ctx.get_brush(grid), 1.0f);
        draw_text(ctx, points[selected_index].label + L"  " + std::to_wstring((int)std::lround(points[selected_index].value)),
                  style, t->text_primary, tx + 8.0f, ty, tw - 16.0f, th, 0.82f);
    }
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void LineChart::on_mouse_move(int x, int y) {
    int idx = point_at(x, y);
    if (idx != selected_index) set_selected_index(idx);
}

void LineChart::on_mouse_leave() {
    hovered = false;
    if (show_tooltip) set_selected_index(-1);
}

void LineChart::on_mouse_down(int x, int y, MouseButton) {
    set_selected_index(point_at(x, y));
}

void BarChart::set_title(const std::wstring& value) { title = value; invalidate(); }
void BarChart::set_bars(const std::vector<ChartPoint>& values) {
    bars = values;
    series.clear();
    if (selected_index >= (int)bars.size()) selected_index = bars.empty() ? -1 : (int)bars.size() - 1;
    invalidate();
}
void BarChart::set_series(const std::vector<std::vector<ChartPoint>>& values) {
    series = values;
    bars = series.empty() ? std::vector<ChartPoint>() : series[0];
    if (selected_index >= (int)bars.size()) selected_index = bars.empty() ? -1 : (int)bars.size() - 1;
    invalidate();
}
void BarChart::set_orientation(int value) { orientation = value == 1 ? 1 : 0; invalidate(); }
void BarChart::set_selected_index(int value) {
    if (bars.empty()) selected_index = -1;
    else selected_index = (std::max)(-1, (std::min)((int)bars.size() - 1, value));
    invalidate();
}
void BarChart::set_options(int orientation_value, bool values, bool axis) {
    set_orientation(orientation_value);
    show_values = values;
    show_axis = axis;
    invalidate();
}

int BarChart::bar_at(int x, int y) const {
    if (bars.empty()) return -1;
    D2D1_RECT_F r = bar_plot_rect(*this);
    if (x < r.left || x > r.right || y < r.top || y > r.bottom) return -1;
    if (orientation == 1) {
        float slot = (r.right - r.left) / (float)bars.size();
        int idx = (int)(((float)x - r.left) / slot);
        return idx >= 0 && idx < (int)bars.size() ? idx : -1;
    }
    float row_h = (r.bottom - r.top) / (float)bars.size();
    int idx = (int)(((float)y - r.top) / row_h);
    return idx >= 0 && idx < (int)bars.size() ? idx : -1;
}

void BarChart::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    Color muted = t->text_secondary;
    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this, title.empty() ? L"📊 柱状排行" : title);
    if (bars.empty() && series.empty()) {
        draw_empty(ctx, owner_hwnd, *this, L"📭 暂无柱状图数据");
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }
    float maxv = series.empty() ? max_value(bars) : max_series_value(series);
    D2D1_RECT_F plot = bar_plot_rect(*this);
    if (show_axis) {
        Color grid = is_dark_theme_for_window(owner_hwnd) ? 0xFF313244 : 0xFFE4E7ED;
        ctx.rt->DrawLine(D2D1::Point2F(plot.left, plot.bottom),
                         D2D1::Point2F(plot.right, plot.bottom), ctx.get_brush(grid), 1.0f);
    }
    if (!series.empty() && orientation == 1) {
        size_t count = 0;
        for (const auto& s : series) count = (std::max)(count, s.size());
        if (count == 0) { ctx.pop_clip(); ctx.rt->SetTransform(saved); return; }
        float slot = (plot.right - plot.left) / (float)count;
        float label_h = (std::max)(22.0f, style.font_size * 1.55f);
        float group_gap = 6.0f;
        float bar_w = (std::max)(4.0f, (slot - group_gap) / (float)(std::max)(1, (int)series.size()) - 2.0f);
        for (size_t i = 0; i < count; ++i) {
            float slot_x = plot.left + slot * (float)i;
            for (size_t s = 0; s < series.size(); ++s) {
                if (i >= series[s].size()) continue;
                float bar_h = (plot.bottom - plot.top - 8.0f) * (std::max)(0.0f, series[s][i].value) / maxv;
                float x = slot_x + group_gap * 0.5f + (float)s * (bar_w + 2.0f);
                float y = plot.bottom - bar_h;
                ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(x, y, x + bar_w, plot.bottom), 3.0f, 3.0f),
                                             ctx.get_brush(palette_color(t, (int)s)));
            }
            if (!series[0].empty() && i < series[0].size()) {
                draw_text(ctx, series[0][i].label, style, muted, slot_x, plot.bottom + 4.0f,
                          slot, label_h, 0.68f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
            }
        }
    } else if (orientation == 1) {
        float slot = (plot.right - plot.left) / (float)bars.size();
        float label_h = (std::max)(22.0f, style.font_size * 1.55f);
        float label_y = plot.bottom + 4.0f;
        for (size_t i = 0; i < bars.size(); ++i) {
            float slot_x = plot.left + slot * (float)i;
            float bar_w = (std::max)(8.0f, slot * 0.54f);
            float bar_h = (plot.bottom - plot.top - 8.0f) * (std::max)(0.0f, bars[i].value) / maxv;
            float x = slot_x + (slot - bar_w) * 0.5f;
            float y = plot.bottom - bar_h;
            D2D1_RECT_F r = { x, y, x + bar_w, plot.bottom };
            Color color = palette_color(t, (int)i);
            if ((int)i == selected_index) color = with_alpha(color, 0xEE);
            ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(color));
            float label_w = (std::min)(slot, 96.0f);
            float label_x = slot_x + slot * 0.5f - label_w * 0.5f;
            draw_text(ctx, bars[i].label, style, muted, label_x, label_y,
                      label_w, label_h, 0.72f, DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT_CENTER);
            if (show_values && (int)i == selected_index) {
                draw_text(ctx, std::to_wstring((int)std::lround(bars[i].value)), style, t->text_primary,
                          x - 16.0f, y - 22.0f, bar_w + 32.0f, 20.0f, 0.82f,
                          DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_TEXT_ALIGNMENT_CENTER);
            }
        }
    } else {
        float chart_w = (float)bounds.w - style.pad_left - style.pad_right;
        float row_h = (plot.bottom - plot.top) / (float)bars.size();
        for (size_t i = 0; i < bars.size(); ++i) {
            float y = plot.top + row_h * (float)i + 5.0f;
            float label_w = 78.0f;
            draw_text(ctx, bars[i].label, style, muted, plot.left, y, label_w, row_h - 8.0f, 0.82f);
            float bar_x = plot.left + label_w + 8.0f;
            float bar_w = (std::max)(2.0f, (chart_w - label_w - 60.0f) * (std::max)(0.0f, bars[i].value) / maxv);
            float bar_h = (std::max)(8.0f, row_h - 16.0f);
            D2D1_RECT_F r = { bar_x, y + 4.0f, bar_x + bar_w, y + 4.0f + bar_h };
            Color color = palette_color(t, (int)i);
            if ((int)i == selected_index) {
                ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(bar_x - 4.0f, y, bar_x + bar_w + 4.0f, y + bar_h + 8.0f), 5.0f, 5.0f),
                                             ctx.get_brush(with_alpha(color, 0x20)));
            }
            ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(color));
            if (show_values) {
                draw_text(ctx, std::to_wstring((int)std::lround(bars[i].value)), style, t->text_primary,
                          bar_x + bar_w + 7.0f, y, 50.0f, row_h - 8.0f, 0.82f);
            }
        }
    }
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void BarChart::on_mouse_move(int x, int y) {
    int idx = bar_at(x, y);
    if (idx != selected_index) set_selected_index(idx);
}

void BarChart::on_mouse_leave() {
    hovered = false;
    set_selected_index(-1);
}

void BarChart::on_mouse_down(int x, int y, MouseButton) {
    set_selected_index(bar_at(x, y));
}

void DonutChart::set_title(const std::wstring& value) { title = value; invalidate(); }
void DonutChart::set_slices(const std::vector<ChartPoint>& values) { slices = values; if (active_index >= (int)slices.size()) active_index = 0; invalidate(); }
void DonutChart::set_active_index(int value) { active_index = slices.empty() ? -1 : (std::max)(0, (std::min)((int)slices.size() - 1, value)); invalidate(); }
void DonutChart::set_options(bool legend, int width, bool labels) {
    show_legend = legend;
    show_labels = labels;
    ring_width = (std::max)(10, (std::min)(42, width));
    invalidate();
}

int DonutChart::slice_at(int x, int y) const {
    if (slices.empty()) return -1;
    float cx = (float)style.pad_left + 92.0f, cy = 132.0f;
    float radius = 64.0f;
    float dx = (float)x - cx, dy = (float)y - cy;
    float dist = std::sqrt(dx * dx + dy * dy);
    if (dist < radius - (float)ring_width * 0.7f || dist > radius + (float)ring_width * 0.8f) return -1;
    float angle = std::atan2(dy, dx);
    float start_base = -3.1415926f * 0.5f;
    while (angle < start_base) angle += 6.2831853f;
    float total = total_value(slices);
    float start = start_base;
    for (size_t i = 0; i < slices.size(); ++i) {
        float span = (std::max)(0.0f, slices[i].value) / total * 6.2831853f;
        if (angle >= start && angle <= start + span) return (int)i;
        start += span;
    }
    return -1;
}

void DonutChart::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_shell(ctx, owner_hwnd, *this, title.empty() ? L"🍩 环形占比" : title);
    if (slices.empty()) {
        draw_empty(ctx, owner_hwnd, *this, L"📭 暂无环形图数据");
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }
    float cx = (float)style.pad_left + 92.0f, cy = 132.0f;
    float radius = 64.0f, stroke = (float)ring_width;
    float total = total_value(slices);
    float start = -3.1415926f * 0.5f;
    for (size_t i = 0; i < slices.size(); ++i) {
        float span = (std::max)(0.0f, slices[i].value) / total * 6.2831853f;
        ID2D1PathGeometry* geo = nullptr;
        if (span > 0.001f && g_d2d_factory && SUCCEEDED(g_d2d_factory->CreatePathGeometry(&geo)) && geo) {
            ID2D1GeometrySink* sink = nullptr;
            if (SUCCEEDED(geo->Open(&sink)) && sink) {
                D2D1_POINT_2F p0 = polar(cx, cy, radius, start);
                D2D1_POINT_2F p1 = polar(cx, cy, radius, start + span);
                sink->BeginFigure(p0, D2D1_FIGURE_BEGIN_HOLLOW);
                sink->AddArc(D2D1::ArcSegment(p1, D2D1::SizeF(radius, radius), 0.0f,
                    span > 3.1415926f ? D2D1_SWEEP_DIRECTION_CLOCKWISE : D2D1_SWEEP_DIRECTION_CLOCKWISE,
                    span > 3.1415926f ? D2D1_ARC_SIZE_LARGE : D2D1_ARC_SIZE_SMALL));
                sink->EndFigure(D2D1_FIGURE_END_OPEN);
                sink->Close();
                sink->Release();
                ctx.rt->DrawGeometry(geo, ctx.get_brush(palette_color(t, (int)i)), i == (size_t)active_index ? stroke + 4.0f : stroke);
            }
            geo->Release();
        }
        if (show_labels && span > 0.08f) {
            float mid = start + span * 0.5f;
            D2D1_POINT_2F lp = polar(cx, cy, radius + stroke * 0.9f, mid);
            int item_pct = (int)std::lround((std::max)(0.0f, slices[i].value) / total * 100.0f);
            draw_text(ctx, std::to_wstring(item_pct) + L"%", style, t->text_secondary,
                      lp.x - 18.0f, lp.y - 10.0f, 36.0f, 20.0f, 0.72f,
                      DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
        start += span;
    }
    int active = active_index >= 0 && active_index < (int)slices.size() ? active_index : 0;
    int pct = (int)std::lround((std::max)(0.0f, slices[active].value) / total * 100.0f);
    draw_text(ctx, std::to_wstring(pct) + L"%", style, t->text_primary, cx - 42.0f, cy - 18.0f, 84.0f, 28.0f, 1.35f, DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_TEXT_ALIGNMENT_CENTER);
    draw_text(ctx, slices[active].label, style, t->text_secondary, cx - 54.0f, cy + 10.0f, 108.0f, 22.0f, 0.8f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
    float lx = (float)style.pad_left + 190.0f, ly = 62.0f;
    if (show_legend) {
        for (size_t i = 0; i < slices.size() && i < 5; ++i) {
            float y = ly + (float)i * 28.0f;
            ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(lx, y + 7.0f, lx + 14.0f, y + 21.0f), 3.0f, 3.0f), ctx.get_brush(palette_color(t, (int)i)));
            draw_text(ctx, slices[i].label, style, t->text_primary, lx + 22.0f, y, 120.0f, 26.0f, 0.84f);
            int item_pct = (int)std::lround((std::max)(0.0f, slices[i].value) / total * 100.0f);
            draw_text(ctx, std::to_wstring(item_pct) + L"%", style, t->text_secondary, lx + 140.0f, y, 42.0f, 26.0f, 0.84f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_TRAILING);
        }
    }
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void DonutChart::on_mouse_move(int x, int y) {
    int idx = slice_at(x, y);
    if (idx >= 0 && idx != active_index) set_active_index(idx);
}

void DonutChart::on_mouse_leave() {
    hovered = false;
}

void DonutChart::on_mouse_down(int x, int y, MouseButton) {
    int idx = slice_at(x, y);
    if (idx >= 0) set_active_index(idx);
}
