#include "element_colorpicker.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cwctype>

static int round_px(float v) {
    return (int)std::lround(v);
}

static float clamp01(float v) {
    if (v < 0.0f) return 0.0f;
    if (v > 1.0f) return 1.0f;
    return v;
}

static Color rgb_from_hsv(float hue, float sat, float val, int alpha) {
    while (hue < 0.0f) hue += 360.0f;
    while (hue >= 360.0f) hue -= 360.0f;
    sat = clamp01(sat);
    val = clamp01(val);
    float c = val * sat;
    float h = hue / 60.0f;
    float x = c * (1.0f - std::fabs(std::fmod(h, 2.0f) - 1.0f));
    float r1 = 0.0f, g1 = 0.0f, b1 = 0.0f;
    if (h < 1.0f) { r1 = c; g1 = x; }
    else if (h < 2.0f) { r1 = x; g1 = c; }
    else if (h < 3.0f) { g1 = c; b1 = x; }
    else if (h < 4.0f) { g1 = x; b1 = c; }
    else if (h < 5.0f) { r1 = x; b1 = c; }
    else { r1 = c; b1 = x; }
    float m = val - c;
    Color r = (Color)round_px((r1 + m) * 255.0f);
    Color g = (Color)round_px((g1 + m) * 255.0f);
    Color b = (Color)round_px((b1 + m) * 255.0f);
    if (alpha < 0) alpha = 0;
    if (alpha > 255) alpha = 255;
    return ((Color)alpha << 24) | (r << 16) | (g << 8) | b;
}

static void hsv_from_rgb(Color color, float* hue, float* sat, float* val) {
    float r = (float)((color >> 16) & 0xFF) / 255.0f;
    float g = (float)((color >> 8) & 0xFF) / 255.0f;
    float b = (float)(color & 0xFF) / 255.0f;
    float maxv = (std::max)(r, (std::max)(g, b));
    float minv = (std::min)(r, (std::min)(g, b));
    float d = maxv - minv;
    float h = 0.0f;
    if (d > 0.0001f) {
        if (maxv == r) h = 60.0f * std::fmod(((g - b) / d), 6.0f);
        else if (maxv == g) h = 60.0f * (((b - r) / d) + 2.0f);
        else h = 60.0f * (((r - g) / d) + 4.0f);
        if (h < 0.0f) h += 360.0f;
    }
    if (hue) *hue = h;
    if (sat) *sat = maxv <= 0.0001f ? 0.0f : d / maxv;
    if (val) *val = maxv;
}

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

float ColorPicker::size_factor() const {
    switch (size_mode) {
    case 1: return 0.96f;  // medium
    case 2: return 0.88f;  // small
    case 3: return 0.78f;  // mini
    default: return 1.0f;
    }
}

float ColorPicker::effective_font_size() const {
    float s = style.font_size * size_factor();
    return s < 11.0f ? 11.0f : s;
}

int ColorPicker::control_padding() const {
    int p = round_px(8.0f * size_factor());
    return p < 4 ? 4 : p;
}

int ColorPicker::cell_size() const {
    int s = round_px(effective_font_size() * 1.6f);
    int min_size = size_mode == 3 ? 16 : (size_mode == 2 ? 18 : 22);
    return s < min_size ? min_size : s;
}

int ColorPicker::cell_gap() const {
    int g = round_px(effective_font_size() * 0.45f);
    int min_gap = size_mode == 3 ? 4 : 6;
    return g < min_gap ? min_gap : g;
}

int ColorPicker::alpha_bar_height() const {
    int h = round_px(effective_font_size() * 1.2f);
    int min_h = size_mode == 3 ? 12 : (size_mode == 2 ? 14 : 16);
    return h < min_h ? min_h : h;
}

int ColorPicker::color_area_height() const {
    int h = round_px(effective_font_size() * 5.6f);
    return h < 72 ? 72 : h;
}

int ColorPicker::hue_bar_height() const {
    int h = round_px(effective_font_size() * 1.05f);
    return h < 14 ? 14 : h;
}

int ColorPicker::hex_field_height() const {
    int h = round_px(effective_font_size() * 1.9f);
    return h < 28 ? 28 : h;
}

int ColorPicker::panel_height() const {
    int rows = ((int)m_palette.size() + kColumns - 1) / kColumns;
    int h = cell_gap() * 5 + color_area_height() + hue_bar_height() +
            hex_field_height() + rows * cell_size() + (rows - 1) * cell_gap();
    if (show_alpha) h += cell_gap() + alpha_bar_height();
    return h;
}

int ColorPicker::panel_y() const {
    int ph = panel_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

Rect ColorPicker::color_area_rect() const {
    int gap = cell_gap();
    int py = panel_y();
    return { gap, py + gap, bounds.w - gap * 2, color_area_height() };
}

Rect ColorPicker::hue_bar_rect() const {
    Rect area = color_area_rect();
    int gap = cell_gap();
    return { gap, area.y + area.h + gap, bounds.w - gap * 2, hue_bar_height() };
}

Rect ColorPicker::hex_field_rect() const {
    Rect hue = hue_bar_rect();
    int gap = cell_gap();
    return { gap, hue.y + hue.h + gap, bounds.w - gap * 2, hex_field_height() };
}

std::wstring ColorPicker::hex_text() const {
    if (!has_value) return L"未选择";
    wchar_t buf[32] = {};
    if (show_alpha && alpha() < 255) {
        swprintf_s(buf, L"#%02X%02X%02X %d%%",
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF),
                   alpha() * 100 / 255);
    } else {
        swprintf_s(buf, L"#%02X%02X%02X",
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF));
    }
    return std::wstring(buf);
}

void ColorPicker::set_color(Color color) {
    if ((color >> 24) == 0) color |= 0xFF000000;
    Color old = value;
    bool old_has_value = has_value;
    value = color;
    has_value = true;
    float s = 0.0f, v = 0.0f;
    hsv_from_rgb(value, &m_hue, &s, &v);
    sync_edit_text();
    invalidate();
    if (old != value || old_has_value != has_value) notify_changed();
}

void ColorPicker::set_alpha(int alpha_value) {
    if (alpha_value < 0) alpha_value = 0;
    if (alpha_value > 255) alpha_value = 255;
    Color old = value;
    bool old_has_value = has_value;
    value = (value & 0x00FFFFFF) | ((Color)alpha_value << 24);
    has_value = true;
    sync_edit_text();
    invalidate();
    if (old != value || old_has_value != has_value) notify_changed();
}

static int colorpicker_hex_digit(wchar_t ch) {
    if (ch >= L'0' && ch <= L'9') return ch - L'0';
    ch = (wchar_t)std::towupper(ch);
    if (ch >= L'A' && ch <= L'F') return 10 + ch - L'A';
    return -1;
}

bool ColorPicker::set_hex_text(const std::wstring& input) {
    std::wstring s;
    for (wchar_t ch : input) {
        if (ch == L'#' || ch == L' ' || ch == L'\t' || ch == L'\r' || ch == L'\n') continue;
        s.push_back(ch);
    }
    if (s.size() != 6 && s.size() != 8) return false;
    Color parsed = 0;
    for (wchar_t ch : s) {
        int v = colorpicker_hex_digit(ch);
        if (v < 0) return false;
        parsed = (parsed << 4) | (Color)v;
    }
    if (s.size() == 6) parsed |= 0xFF000000;
    set_color(parsed);
    sync_edit_text();
    return true;
}

std::wstring ColorPicker::get_hex_text() const {
    return input_hex_text();
}

int ColorPicker::alpha() const {
    return (int)((value >> 24) & 0xFF);
}

void ColorPicker::set_open(bool is_open) {
    open = is_open;
    invalidate();
}

void ColorPicker::set_options(bool show_alpha_value, int size_value, bool clearable_value) {
    show_alpha = show_alpha_value;
    size_mode = (std::max)(0, (std::min)(3, size_value));
    clearable = clearable_value;
    invalidate();
}

void ColorPicker::clear_value() {
    bool changed = has_value || value != 0;
    has_value = false;
    open = false;
    value = 0;
    m_edit_text.clear();
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
    if (changed) notify_changed();
}

void ColorPicker::set_palette(const std::vector<Color>& colors) {
    if (colors.empty()) return;
    m_palette = colors;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

int ColorPicker::palette_count() const {
    return (int)m_palette.size();
}

void ColorPicker::notify_changed() {
    if (change_cb) change_cb(id, has_value ? (int)value : 0, has_value ? alpha() : 0, palette_count());
}

int ColorPicker::color_at(int x, int y) const {
    if (!open) return -1;
    int ph = panel_height();
    int py = panel_y();
    if (x < 0 || x >= bounds.w || y < py || y >= py + ph) return -1;

    int cs = cell_size();
    int gap = cell_gap();
    int grid_w = kColumns * cs + (kColumns - 1) * gap;
    int start_x = (bounds.w - grid_w) / 2;
    if (start_x < gap) start_x = gap;
    Rect hex = hex_field_rect();
    int start_y = hex.y + hex.h + gap;

    for (int i = 0; i < (int)m_palette.size(); ++i) {
        int row = i / kColumns;
        int col = i % kColumns;
        int cx = start_x + col * (cs + gap);
        int cy = start_y + row * (cs + gap);
        if (x >= cx && x < cx + cs && y >= cy && y < cy + cs) return i;
    }
    return -1;
}

int ColorPicker::alpha_at(int x, int y) const {
    if (!open || !show_alpha) return -1;
    int ph = panel_height();
    int py = panel_y();
    if (x < 0 || x >= bounds.w || y < py || y >= py + ph) return -1;

    int gap = cell_gap();
    int bar_h = alpha_bar_height();
    int bar_x = gap;
    int bar_y = py + ph - gap - bar_h;
    int bar_w = bounds.w - gap * 2;
    if (x < bar_x || x >= bar_x + bar_w || y < bar_y || y >= bar_y + bar_h) return -1;
    int alpha_value = (x - bar_x) * 255 / (std::max)(1, bar_w - 1);
    return (std::max)(0, (std::min)(255, alpha_value));
}

bool ColorPicker::color_area_at(int x, int y, float* sat, float* val) const {
    if (!open) return false;
    Rect r = color_area_rect();
    if (x < r.x || x >= r.x + r.w || y < r.y || y >= r.y + r.h) return false;
    if (sat) *sat = clamp01((float)(x - r.x) / (float)(std::max)(1, r.w - 1));
    if (val) *val = 1.0f - clamp01((float)(y - r.y) / (float)(std::max)(1, r.h - 1));
    return true;
}

float ColorPicker::hue_at(int x, int y) const {
    if (!open) return -1.0f;
    Rect r = hue_bar_rect();
    if (x < r.x || x >= r.x + r.w || y < r.y || y >= r.y + r.h) return -1.0f;
    return clamp01((float)(x - r.x) / (float)(std::max)(1, r.w - 1)) * 360.0f;
}

bool ColorPicker::clear_at(int x, int y) const {
    if (!clearable || !has_value || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return false;
    int pad = control_padding();
    int size = round_px(effective_font_size() * 1.15f);
    if (size < 14) size = 14;
    int cx = bounds.w - pad - size;
    int cy = (bounds.h - size) / 2;
    return x >= cx && x < cx + size && y >= cy && y < cy + size;
}

std::wstring ColorPicker::input_hex_text() const {
    if (m_editing && !m_edit_text.empty()) return m_edit_text;
    if (!has_value) return L"";
    wchar_t buf[16] = {};
    if (show_alpha) {
        swprintf_s(buf, L"#%02X%02X%02X%02X",
                   (unsigned)alpha(),
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF));
    } else {
        swprintf_s(buf, L"#%02X%02X%02X",
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF));
    }
    return std::wstring(buf);
}

bool ColorPicker::edit_text_is_valid() const {
    std::wstring s;
    for (wchar_t ch : m_edit_text) {
        if (ch == L'#' || ch == L' ' || ch == L'\t' || ch == L'\r' || ch == L'\n') continue;
        s.push_back(ch);
    }
    if (s.size() != 6 && s.size() != 8) return false;
    for (wchar_t ch : s) {
        if (colorpicker_hex_digit(ch) < 0) return false;
    }
    return true;
}

void ColorPicker::sync_edit_text() {
    if (!has_value) {
        m_edit_text.clear();
        return;
    }
    wchar_t buf[16] = {};
    if (show_alpha) {
        swprintf_s(buf, L"#%02X%02X%02X%02X",
                   (unsigned)alpha(),
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF));
    } else {
        swprintf_s(buf, L"#%02X%02X%02X",
                   (unsigned)((value >> 16) & 0xFF),
                   (unsigned)((value >> 8) & 0xFF),
                   (unsigned)(value & 0xFF));
    }
    m_edit_text = buf;
}

void ColorPicker::apply_color_from_area(float sat, float val) {
    set_color(rgb_from_hsv(m_hue, sat, val, show_alpha && has_value ? alpha() : 255));
}

void ColorPicker::apply_hue(float hue) {
    float old_hue = m_hue;
    float s = 1.0f, v = 1.0f;
    if (has_value) hsv_from_rgb(value, &old_hue, &s, &v);
    m_hue = hue;
    set_color(rgb_from_hsv(m_hue, s, v, show_alpha && has_value ? alpha() : 255));
}

void ColorPicker::apply_edit_text_if_valid() {
    if (edit_text_is_valid()) {
        set_hex_text(m_edit_text);
    } else {
        invalidate();
    }
}

Element* ColorPicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    float s = 0.0f, v = 0.0f;
    Rect hex = hex_field_rect();
    if (color_at(lx, ly) >= 0 || alpha_at(lx, ly) >= 0 || hex.contains(lx, ly) ||
        color_area_at(lx, ly, &s, &v) || hue_at(lx, ly) >= 0.0f) return this;
    return nullptr;
}

Element* ColorPicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    float s = 0.0f, v = 0.0f;
    Rect hex = hex_field_rect();
    return (color_at(lx, ly) >= 0 || alpha_at(lx, ly) >= 0 || hex.contains(lx, ly) ||
            color_area_at(lx, ly, &s, &v) || hue_at(lx, ly) >= 0.0f) ? this : nullptr;
}

void ColorPicker::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    ElementStyle text_style = style;
    text_style.font_size = effective_font_size();

    D2D1_RECT_F field = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float label_w = text.empty() ? 0.0f : (float)((std::min)(round_px(bounds.w * 0.34f), round_px(120.0f * style.font_size / 14.0f)));
    float pad_l = (float)control_padding();
    float pad_r = (float)control_padding();
    if (clearable && has_value) {
        pad_r += (float)round_px(effective_font_size() * 1.45f);
    }
    if (!text.empty()) {
        draw_text(ctx, text, text_style, t->text_secondary, pad_l, 0.0f, label_w, (float)bounds.h);
    }

    int swatch = round_px(effective_font_size() * 1.45f);
    int min_swatch = size_mode == 3 ? 14 : (size_mode == 2 ? 16 : 20);
    if (swatch < min_swatch) swatch = min_swatch;
    float swatch_x = pad_l + label_w + (label_w > 0.0f ? 8.0f : 0.0f);
    float swatch_y = ((float)bounds.h - (float)swatch) * 0.5f;
    D2D1_RECT_F swatch_rect = { swatch_x, swatch_y, swatch_x + (float)swatch, swatch_y + (float)swatch };
    if (has_value) {
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(swatch_rect, 4.0f, 4.0f), ctx.get_brush(value));
    } else {
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(swatch_rect, 4.0f, 4.0f), ctx.get_brush(t->edit_bg));
        ctx.rt->DrawLine(D2D1::Point2F(swatch_rect.left + 3.0f, swatch_rect.bottom - 3.0f),
                         D2D1::Point2F(swatch_rect.right - 3.0f, swatch_rect.top + 3.0f),
                         ctx.get_brush(t->text_secondary), 1.2f);
    }
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(swatch_rect, 4.0f, 4.0f),
                                 ctx.get_brush(t->border_default), 1.0f);

    float hex_x = swatch_x + (float)swatch + 8.0f;
    std::wstring shown_text = (has_focus && m_editing) ? input_hex_text() : hex_text();
    draw_text(ctx, shown_text, text_style, has_value || m_editing ? fg : t->text_secondary, hex_x, 0.0f,
              (float)bounds.w - hex_x - pad_r, (float)bounds.h);

    if (clearable && has_value) {
        int clear_size = round_px(effective_font_size() * 1.15f);
        if (clear_size < 14) clear_size = 14;
        float cx = (float)(bounds.w - control_padding() - clear_size);
        float cy = ((float)bounds.h - (float)clear_size) * 0.5f;
        D2D1_RECT_F clear_rect = { cx, cy, cx + (float)clear_size, cy + (float)clear_size };
        Color clear_bg = m_press_clear ? t->edit_focus : (hovered ? t->edit_border : 0x00000000);
        if (clear_bg) {
            ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(clear_rect, clear_size / 2.0f, clear_size / 2.0f),
                                         ctx.get_brush(clear_bg));
        }
        ctx.rt->DrawLine(D2D1::Point2F(clear_rect.left + 4.0f, clear_rect.top + 4.0f),
                         D2D1::Point2F(clear_rect.right - 4.0f, clear_rect.bottom - 4.0f),
                         ctx.get_brush(t->text_secondary), 1.4f);
        ctx.rt->DrawLine(D2D1::Point2F(clear_rect.right - 4.0f, clear_rect.top + 4.0f),
                         D2D1::Point2F(clear_rect.left + 4.0f, clear_rect.bottom - 4.0f),
                         ctx.get_brush(t->text_secondary), 1.4f);
    }

    ctx.rt->SetTransform(saved);
}

void ColorPicker::paint_palette(RenderContext& ctx) {
    if (!open) return;

    const Theme* t = theme_for_window(owner_hwnd);
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    int py = panel_y();
    int ph = panel_height();
    D2D1_RECT_F panel = { 0, (float)py, (float)bounds.w, (float)(py + ph) };
    Color panel_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(panel, radius, radius), ctx.get_brush(panel_bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(panel.left + 0.5f, panel.top + 0.5f,
                                      panel.right - 0.5f, panel.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);

    int cs = cell_size();
    int gap = cell_gap();

    Rect area = color_area_rect();
    float current_h = m_hue;
    float current_s = 1.0f;
    float current_v = 1.0f;
    if (has_value) hsv_from_rgb(value, &current_h, &current_s, &current_v);
    for (int yy = 0; yy < area.h; yy += 3) {
        float v = 1.0f - clamp01((float)yy / (float)(std::max)(1, area.h - 1));
        for (int xx = 0; xx < area.w; xx += 3) {
            float s = clamp01((float)xx / (float)(std::max)(1, area.w - 1));
            D2D1_RECT_F cell = {
                (float)(area.x + xx), (float)(area.y + yy),
                (float)(area.x + (std::min)(area.w, xx + 3)),
                (float)(area.y + (std::min)(area.h, yy + 3))
            };
            ctx.rt->FillRectangle(cell, ctx.get_brush(rgb_from_hsv(current_h, s, v, 255)));
        }
    }
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF((float)area.x + 0.5f, (float)area.y + 0.5f,
                                      (float)(area.x + area.w) - 0.5f,
                                      (float)(area.y + area.h) - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);
    float knob_x = (float)area.x + current_s * (float)(std::max)(1, area.w - 1);
    float knob_y = (float)area.y + (1.0f - current_v) * (float)(std::max)(1, area.h - 1);
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(knob_x, knob_y), 5.0f, 5.0f),
                        ctx.get_brush(0xFFFFFFFF), 2.0f);
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(knob_x, knob_y), 6.0f, 6.0f),
                        ctx.get_brush(0xAA000000), 1.0f);

    Rect hue = hue_bar_rect();
    for (int xx = 0; xx < hue.w; xx += 2) {
        float h = clamp01((float)xx / (float)(std::max)(1, hue.w - 1)) * 360.0f;
        D2D1_RECT_F strip = {
            (float)(hue.x + xx), (float)hue.y,
            (float)(hue.x + (std::min)(hue.w, xx + 2)), (float)(hue.y + hue.h)
        };
        ctx.rt->FillRectangle(strip, ctx.get_brush(rgb_from_hsv(h, 1.0f, 1.0f, 255)));
    }
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF((float)hue.x + 0.5f, (float)hue.y + 0.5f,
                                      (float)(hue.x + hue.w) - 0.5f,
                                      (float)(hue.y + hue.h) - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);
    float hue_x = (float)hue.x + current_h / 360.0f * (float)(std::max)(1, hue.w - 1);
    ctx.rt->DrawLine(D2D1::Point2F(hue_x, (float)hue.y - 2.0f),
                     D2D1::Point2F(hue_x, (float)(hue.y + hue.h) + 2.0f),
                     ctx.get_brush(0xFFFFFFFF), 2.0f);

    Rect hex = hex_field_rect();
    D2D1_RECT_F hex_rect = { (float)hex.x, (float)hex.y, (float)(hex.x + hex.w), (float)(hex.y + hex.h) };
    Color hex_border = edit_text_is_valid() || m_edit_text.empty() ? t->edit_border : 0xFFE53935;
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(hex_rect, 4.0f, 4.0f), ctx.get_brush(t->edit_bg));
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(hex_rect, 4.0f, 4.0f),
                                 ctx.get_brush(hex_border), 1.0f);
    draw_text(ctx, input_hex_text().empty() ? L"输入 #RRGGBB 或 #AARRGGBB" : input_hex_text(),
              style, input_hex_text().empty() ? t->text_secondary : t->text_primary,
              (float)hex.x + 8.0f, (float)hex.y,
              (float)hex.w - 16.0f, (float)hex.h);

    int grid_w = kColumns * cs + (kColumns - 1) * gap;
    int start_x = (bounds.w - grid_w) / 2;
    if (start_x < gap) start_x = gap;
    int start_y = hex.y + hex.h + gap;
    for (int i = 0; i < (int)m_palette.size(); ++i) {
        int row = i / kColumns;
        int col = i % kColumns;
        float cx = (float)(start_x + col * (cs + gap));
        float cy = (float)(start_y + row * (cs + gap));
        D2D1_RECT_F cell = { cx, cy, cx + (float)cs, cy + (float)cs };
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(cell, 4.0f, 4.0f), ctx.get_brush(m_palette[i]));
        Color normalized = (m_palette[i] & 0x00FFFFFF) | ((Color)(show_alpha && has_value ? alpha() : 255) << 24);
        Color cell_border = (normalized == value || i == m_hover_index) ? t->accent : t->border_default;
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(cell, 4.0f, 4.0f),
                                     ctx.get_brush(cell_border),
                                     (normalized == value || i == m_hover_index) ? 2.0f : 1.0f);
    }

    if (show_alpha) {
        int bar_h = alpha_bar_height();
        int bar_x = gap;
        int bar_y = py + ph - gap - bar_h;
        int bar_w = bounds.w - gap * 2;
        D2D1_RECT_F bar = { (float)bar_x, (float)bar_y, (float)(bar_x + bar_w), (float)(bar_y + bar_h) };
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(bar, 4.0f, 4.0f), ctx.get_brush(0xFFE5E7EB));
        D2D1_RECT_F fill = { (float)bar_x, (float)bar_y,
                             (float)(bar_x + bar_w * alpha() / 255), (float)(bar_y + bar_h) };
        if (fill.right > fill.left) {
            Color alpha_fill = has_value ? value : 0xFF909399;
            ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(fill, 4.0f, 4.0f), ctx.get_brush(alpha_fill));
        }
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(bar, 4.0f, 4.0f),
                                     ctx.get_brush(t->border_default), 1.0f);
    }
}

void ColorPicker::paint_overlay(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    paint_palette(ctx);

    ctx.rt->SetTransform(saved);
}

void ColorPicker::on_mouse_move(int x, int y) {
    if (m_drag_color_area) {
        float s = 0.0f, v = 0.0f;
        if (color_area_at(x, y, &s, &v)) apply_color_from_area(s, v);
        return;
    }
    if (m_drag_hue) {
        float h = hue_at(x, y);
        if (h >= 0.0f) apply_hue(h);
        return;
    }
    if (m_drag_alpha) {
        int a = alpha_at(x, y);
        if (a >= 0) set_alpha(a);
        return;
    }
    int idx = color_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void ColorPicker::on_mouse_leave() {
    m_hover_index = -1;
    hovered = false;
    invalidate();
}

void ColorPicker::on_mouse_down(int x, int y, MouseButton) {
    m_press_clear = clear_at(x, y);
    m_press_index = color_at(x, y);
    float s = 0.0f, v = 0.0f;
    m_drag_color_area = color_area_at(x, y, &s, &v);
    if (m_drag_color_area) apply_color_from_area(s, v);
    float h = hue_at(x, y);
    m_drag_hue = h >= 0.0f;
    if (m_drag_hue) apply_hue(h);
    int alpha_value = alpha_at(x, y);
    m_drag_alpha = alpha_value >= 0;
    if (alpha_value >= 0) set_alpha(alpha_value);
    m_press_main = (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h);
    if (m_press_main && m_edit_text.empty()) sync_edit_text();
    if (m_press_main) {
        m_editing = true;
        m_replace_on_next_char = true;
    }
    pressed = true;
    invalidate();
}

void ColorPicker::on_mouse_up(int x, int y, MouseButton) {
    int idx = color_at(x, y);
    int alpha_value = alpha_at(x, y);
    if (m_press_clear && clear_at(x, y)) {
        clear_value();
    } else if (m_drag_color_area || m_drag_hue) {
        open = true;
    } else if (idx >= 0 && idx == m_press_index) {
        set_color((m_palette[idx] & 0x00FFFFFF) | ((Color)(show_alpha && has_value ? alpha() : 255) << 24));
        sync_edit_text();
        open = false;
    } else if (alpha_value >= 0) {
        set_alpha(alpha_value);
    } else if (m_press_main && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        open = !open;
    }
    m_press_index = -1;
    m_press_main = false;
    m_press_clear = false;
    m_drag_color_area = false;
    m_drag_hue = false;
    m_drag_alpha = false;
    pressed = false;
    invalidate();
}

void ColorPicker::on_key_down(int vk, int mods) {
    bool ctrl = (mods & KeyMod::Control) != 0;
    if (vk == VK_RETURN) {
        apply_edit_text_if_valid();
        open = !open;
    } else if (vk == VK_SPACE && !m_editing) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
        sync_edit_text();
    } else if (ctrl && vk == 'A') {
        m_edit_text.clear();
        m_editing = true;
        m_replace_on_next_char = false;
    } else if (vk == VK_BACK) {
        m_replace_on_next_char = false;
        if (m_editing && !m_edit_text.empty()) {
            m_edit_text.pop_back();
            apply_edit_text_if_valid();
        } else if (clearable) {
            clear_value();
        }
    } else if (vk == VK_DELETE) {
        m_replace_on_next_char = false;
        if (m_editing) {
            m_edit_text.clear();
            invalidate();
        } else if (clearable) {
            clear_value();
        }
    }
    invalidate();
}

void ColorPicker::on_char(wchar_t ch) {
    if (ch == L'\r' || ch == L'\n' || ch == 27 || ch < 32) return;
    wchar_t up = (wchar_t)std::towupper(ch);
    if (ch == L'#' || (up >= L'0' && up <= L'9') || (up >= L'A' && up <= L'F')) {
        if (!m_editing) {
            m_edit_text.clear();
            m_editing = true;
        }
        if (m_replace_on_next_char) {
            m_edit_text.clear();
            m_replace_on_next_char = false;
        }
        if (m_edit_text.empty() && ch != L'#') m_edit_text.push_back(L'#');
        if ((int)m_edit_text.size() < 9) m_edit_text.push_back(up);
        apply_edit_text_if_valid();
    }
    invalidate();
}

void ColorPicker::on_focus() {
    has_focus = true;
    m_editing = true;
    m_replace_on_next_char = true;
    if (m_edit_text.empty()) sync_edit_text();
    invalidate();
}

void ColorPicker::on_blur() {
    has_focus = false;
    m_editing = false;
    m_replace_on_next_char = false;
    open = false;
    m_hover_index = -1;
    sync_edit_text();
    invalidate();
}
