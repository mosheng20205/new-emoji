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

int ColorPicker::panel_height() const {
    int rows = ((int)m_palette.size() + kColumns - 1) / kColumns;
    int h = cell_gap() * 2 + rows * cell_size() + (rows - 1) * cell_gap();
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
    return true;
}

std::wstring ColorPicker::get_hex_text() const {
    return hex_text();
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
    int start_y = py + gap;

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

bool ColorPicker::clear_at(int x, int y) const {
    if (!clearable || !has_value || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return false;
    int pad = control_padding();
    int size = round_px(effective_font_size() * 1.15f);
    if (size < 14) size = 14;
    int cx = bounds.w - pad - size;
    int cy = (bounds.h - size) / 2;
    return x >= cx && x < cx + size && y >= cy && y < cy + size;
}

Element* ColorPicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    if (color_at(lx, ly) >= 0 || alpha_at(lx, ly) >= 0) return this;
    return nullptr;
}

Element* ColorPicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return (color_at(lx, ly) >= 0 || alpha_at(lx, ly) >= 0) ? this : nullptr;
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
    draw_text(ctx, hex_text(), text_style, has_value ? fg : t->text_secondary, hex_x, 0.0f,
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
    int grid_w = kColumns * cs + (kColumns - 1) * gap;
    int start_x = (bounds.w - grid_w) / 2;
    if (start_x < gap) start_x = gap;
    int start_y = py + gap;
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
    int alpha_value = alpha_at(x, y);
    if (alpha_value >= 0) set_alpha(alpha_value);
    m_press_main = (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h);
    pressed = true;
    invalidate();
}

void ColorPicker::on_mouse_up(int x, int y, MouseButton) {
    int idx = color_at(x, y);
    int alpha_value = alpha_at(x, y);
    if (m_press_clear && clear_at(x, y)) {
        clear_value();
    } else if (idx >= 0 && idx == m_press_index) {
        set_color((m_palette[idx] & 0x00FFFFFF) | ((Color)(show_alpha && has_value ? alpha() : 255) << 24));
        open = false;
    } else if (alpha_value >= 0) {
        set_alpha(alpha_value);
    } else if (m_press_main && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        open = !open;
    }
    m_press_index = -1;
    m_press_main = false;
    m_press_clear = false;
    pressed = false;
    invalidate();
}

void ColorPicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) open = !open;
    else if (vk == VK_ESCAPE) open = false;
    else if ((vk == VK_DELETE || vk == VK_BACK) && clearable) clear_value();
    invalidate();
}

void ColorPicker::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    invalidate();
}
