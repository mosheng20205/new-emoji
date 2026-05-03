#include "element_dialog.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_NEAR,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Dialog::scale() const {
    float s = style.font_size / 14.0f;
    return s < 0.75f ? 0.75f : s;
}

void Dialog::set_title(const std::wstring& value) {
    title = value;
    last_action = 1;
    invalidate();
}

void Dialog::set_body(const std::wstring& value) {
    text = value;
    last_action = 1;
    invalidate();
}

void Dialog::set_modal(bool value) {
    modal = value;
    last_action = 1;
    invalidate();
}

void Dialog::set_closable(bool value) {
    closable = value;
    last_action = 1;
    invalidate();
}

void Dialog::set_open(bool value) {
    visible = value;
    last_action = 1;
    invalidate();
}

void Dialog::set_options(bool open, bool modal_value, bool closable_value,
                         bool mask_close, bool drag_enabled, int w, int h) {
    visible = open;
    modal = modal_value;
    closable = closable_value;
    close_on_mask = mask_close;
    draggable = drag_enabled;
    if (w > 0 || h > 0) {
        int next_w = w > 0 ? w : logical_bounds.w;
        int next_h = h > 0 ? h : logical_bounds.h;
        set_logical_bounds({ logical_bounds.x, logical_bounds.y, next_w, next_h });
    }
    last_action = 1;
    invalidate();
}

void Dialog::set_buttons(const std::vector<std::wstring>& values) {
    buttons = values;
    if ((int)buttons.size() > 4) buttons.resize(4);
    if (buttons.empty()) active_button = -1;
    else if (active_button < 0 || active_button >= (int)buttons.size()) active_button = 0;
    last_action = 1;
    invalidate();
}

void Dialog::trigger_button(int index, int action) {
    if (index < 0 || index >= (int)buttons.size()) return;
    active_button = index;
    last_button = index;
    last_action = action;
    ++button_click_count;
    if (button_cb) button_cb(id, last_button, (int)buttons.size(), last_action);
    visible = false;
    ++close_count;
    invalidate();
}

void Dialog::close_dialog(int action) {
    if (!closable && action != 5) return;
    if (!visible) return;
    visible = false;
    last_action = action;
    ++close_count;
    invalidate();
}

void Dialog::layout(const Rect& available) {
    bounds = available;
    update_layout();
}

void Dialog::update_layout() {
    float s = scale();
    int margin = round_px(28.0f * s);
    int min_w = round_px(300.0f * s);
    int dialog_w = logical_bounds.w > 0 ? round_px((float)logical_bounds.w * s) : round_px(460.0f * s);
    int dialog_h = logical_bounds.h > 0 ? round_px((float)logical_bounds.h * s) : round_px(250.0f * s);

    int max_w = (std::max)(0, bounds.w - margin * 2);
    int max_h = (std::max)(0, bounds.h - margin * 2);
    if (max_w > 0) dialog_w = (std::min)(dialog_w, max_w);
    if (max_h > 0) dialog_h = (std::min)(dialog_h, max_h);
    if (dialog_w < min_w && bounds.w >= min_w) dialog_w = min_w;
    if (dialog_w > bounds.w) dialog_w = bounds.w;
    if (dialog_h > bounds.h) dialog_h = bounds.h;
    if (dialog_w < 0) dialog_w = 0;
    if (dialog_h < 0) dialog_h = 0;

    clamp_offset(dialog_w, dialog_h);
    int x = (bounds.w - dialog_w) / 2 + m_offset_x;
    int y = (bounds.h - dialog_h) / 2 + m_offset_y;
    if (x < 0) x = 0;
    if (y < 0) y = 0;
    m_dialog_rect = { x, y, dialog_w, dialog_h };

    int close_size = round_px(28.0f * s);
    int pad = round_px(16.0f * s);
    m_close_rect = {
        m_dialog_rect.x + m_dialog_rect.w - pad - close_size,
        m_dialog_rect.y + round_px(12.0f * s),
        close_size,
        close_size
    };
}

void Dialog::clamp_offset(int dialog_w, int dialog_h) {
    int center_x = (bounds.w - dialog_w) / 2;
    int center_y = (bounds.h - dialog_h) / 2;
    int min_x = -center_x;
    int max_x = bounds.w - dialog_w - center_x;
    int min_y = -center_y;
    int max_y = bounds.h - dialog_h - center_y;
    if (min_x > max_x) { min_x = 0; max_x = 0; }
    if (min_y > max_y) { min_y = 0; max_y = 0; }
    if (m_offset_x < min_x) m_offset_x = min_x;
    if (m_offset_x > max_x) m_offset_x = max_x;
    if (m_offset_y < min_y) m_offset_y = min_y;
    if (m_offset_y > max_y) m_offset_y = max_y;
}

Dialog::Part Dialog::part_at(int x, int y) const {
    if (button_at(x, y) >= 0) return PartButton;
    if (closable && m_close_rect.contains(x, y)) return PartClose;
    if (m_dialog_rect.contains(x, y)) {
        int header_h = round_px(52.0f * (style.font_size / 14.0f < 0.75f ? 0.75f : style.font_size / 14.0f));
        if (draggable && y < m_dialog_rect.y + header_h) return PartHeader;
        return PartDialog;
    }
    return modal ? PartMask : PartNone;
}

Rect Dialog::button_rect(int index) const {
    if (index < 0 || index >= (int)buttons.size()) return {};
    int s = round_px(scale());
    if (s < 1) s = 1;
    int button_w = round_px(92.0f * scale());
    int button_h = round_px(34.0f * scale());
    int gap = round_px(10.0f * scale());
    int pad = round_px(18.0f * scale());
    int count = (int)buttons.size();
    int total_w = count * button_w + (count - 1) * gap;
    int x = m_dialog_rect.x + m_dialog_rect.w - pad - total_w + index * (button_w + gap);
    int y = m_dialog_rect.y + m_dialog_rect.h - pad - button_h;
    return { x, y, button_w, button_h };
}

int Dialog::button_at(int x, int y) const {
    for (int i = 0; i < (int)buttons.size(); ++i) {
        if (button_rect(i).contains(x, y)) return i;
    }
    return -1;
}

Element* Dialog::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

void Dialog::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    update_layout();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();

    if (modal) {
        D2D1_RECT_F overlay = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(overlay, ctx.get_brush(dark ? 0x99000000 : 0x66000000));
    }

    D2D1_RECT_F dialog = {
        (float)m_dialog_rect.x,
        (float)m_dialog_rect.y,
        (float)(m_dialog_rect.x + m_dialog_rect.w),
        (float)(m_dialog_rect.y + m_dialog_rect.h)
    };
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f * s;
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;

    ctx.rt->FillRoundedRectangle(ROUNDED(dialog, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(dialog.left + 0.5f, dialog.top + 0.5f,
        dialog.right - 0.5f, dialog.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    float pad = 20.0f * s;
    float header_h = 52.0f * s;
    draw_text(ctx, title.empty() ? L"Dialog" : title, style, title_fg,
              dialog.left + pad, dialog.top + 14.0f * s,
              (float)m_dialog_rect.w - pad * 2.0f - 28.0f * s,
              26.0f * s, 1.12f, DWRITE_TEXT_ALIGNMENT_LEADING,
              DWRITE_PARAGRAPH_ALIGNMENT_CENTER, DWRITE_WORD_WRAPPING_NO_WRAP);

    if (closable) {
        Color close_fg = m_hover_part == PartClose ? t->accent : t->text_secondary;
        float cx = (float)m_close_rect.x + m_close_rect.w * 0.5f;
        float cy = (float)m_close_rect.y + m_close_rect.h * 0.5f;
        float cs = 6.0f * s;
        if (m_hover_part == PartClose) {
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy),
                m_close_rect.w * 0.45f, m_close_rect.h * 0.45f),
                ctx.get_brush(dark ? 0x33454A5F : 0xFFEAF2FF));
        }
        ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
        ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
    }

    ctx.rt->DrawLine(D2D1::Point2F(dialog.left, dialog.top + header_h),
                     D2D1::Point2F(dialog.right, dialog.top + header_h),
                     ctx.get_brush(border), 1.0f);
    float footer_h = buttons.empty() ? 0.0f : 58.0f * s;
    draw_text(ctx, text, style, body_fg,
              dialog.left + pad, dialog.top + header_h + 16.0f * s,
              (float)m_dialog_rect.w - pad * 2.0f,
              (float)m_dialog_rect.h - header_h - 32.0f * s - footer_h);

    for (int i = 0; i < (int)buttons.size(); ++i) {
        Rect br = button_rect(i);
        D2D1_RECT_F rr = { (float)br.x, (float)br.y, (float)(br.x + br.w), (float)(br.y + br.h) };
        bool primary = i == 0;
        bool active = i == active_button;
        Color bg = primary ? t->accent : (active || m_hover_button == i ? t->button_hover : 0);
        if (m_press_button == i) bg = t->button_press;
        Color border_c = primary ? t->accent : t->border_default;
        Color fg = primary ? 0xFFFFFFFF : title_fg;
        if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(rr, 5.0f * s, 5.0f * s), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rr.left + 0.5f, rr.top + 0.5f,
            rr.right - 0.5f, rr.bottom - 0.5f), 5.0f * s, 5.0f * s), ctx.get_brush(border_c), active ? 1.6f : 1.0f);
        draw_text(ctx, buttons[i], style, fg, rr.left, rr.top, (float)br.w, (float)br.h,
                  0.92f, DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                  DWRITE_WORD_WRAPPING_NO_WRAP);
    }

    ctx.rt->SetTransform(saved);
}

void Dialog::on_mouse_move(int x, int y) {
    if (m_dragging) {
        m_offset_x = m_drag_origin_x + (x - m_drag_start_x);
        m_offset_y = m_drag_origin_y + (y - m_drag_start_y);
        invalidate();
        return;
    }
    Part part = part_at(x, y);
    m_hover_button = part == PartButton ? button_at(x, y) : -1;
    if (part != m_hover_part) {
        m_hover_part = part;
        invalidate();
    }
}

void Dialog::on_mouse_leave() {
    if (m_dragging) return;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    m_hover_button = -1;
    m_press_button = -1;
    invalidate();
}

void Dialog::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y);
    m_press_button = m_press_part == PartButton ? button_at(x, y) : -1;
    if (m_press_part == PartHeader && draggable) {
        m_dragging = true;
        m_drag_start_x = x;
        m_drag_start_y = y;
        m_drag_origin_x = m_offset_x;
        m_drag_origin_y = m_offset_y;
    }
    invalidate();
}

void Dialog::on_mouse_up(int x, int y, MouseButton) {
    Part part = part_at(x, y);
    if (m_press_part == PartClose && part == PartClose) {
        close_dialog(2);
    } else if (m_press_part == PartMask && part == PartMask && close_on_mask) {
        close_dialog(5);
    } else if (m_press_part == PartButton && part == PartButton && m_press_button == button_at(x, y)) {
        trigger_button(m_press_button, 2);
    }
    m_dragging = false;
    m_press_part = PartNone;
    m_press_button = -1;
    m_hover_part = part;
    m_hover_button = part == PartButton ? button_at(x, y) : -1;
    invalidate();
}

void Dialog::on_key_down(int vk, int) {
    if (!buttons.empty() && (vk == VK_TAB || vk == VK_LEFT || vk == VK_RIGHT || vk == VK_HOME || vk == VK_END)) {
        if (vk == VK_HOME) active_button = 0;
        else if (vk == VK_END) active_button = (int)buttons.size() - 1;
        else if (vk == VK_LEFT) active_button = (active_button + (int)buttons.size() - 1) % (int)buttons.size();
        else active_button = (active_button + 1) % (int)buttons.size();
        invalidate();
    } else if (!buttons.empty() && (vk == VK_RETURN || vk == VK_SPACE)) {
        int idx = active_button >= 0 ? active_button : 0;
        trigger_button(idx, 3);
    } else if (closable && vk == VK_ESCAPE) {
        close_dialog(3);
    }
}
