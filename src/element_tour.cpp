#include "element_tour.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void tour_draw_text(RenderContext& ctx, const std::wstring& text,
                           const ElementStyle& style, Color color,
                           float x, float y, float w, float h,
                           float scale = 1.0f,
                           DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                           DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                           DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_NEAR) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name,
                                          style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Tour::set_steps(const std::vector<TourStep>& values) {
    steps = values;
    if (steps.empty()) active_index = -1;
    else if (active_index < 0 || active_index >= (int)steps.size()) active_index = 0;
    invalidate();
}

void Tour::set_active_index(int value) {
    int old_index = active_index;
    if (steps.empty()) active_index = -1;
    else {
        if (value < 0) value = 0;
        if (value >= (int)steps.size()) value = (int)steps.size() - 1;
        active_index = value;
    }
    if (active_index != old_index) ++change_count;
    invalidate();
}

void Tour::set_open(bool value) {
    if (open != value) ++change_count;
    open = value;
    invalidate();
}

void Tour::set_options(bool is_open, bool show_mask, int target_x, int target_y, int target_w, int target_h) {
    open = is_open;
    mask = show_mask;
    has_target = target_w > 0 && target_h > 0;
    target_rect = { target_x, target_y, target_w, target_h };
    invalidate();
}

void Tour::set_target_element(int element_id, const Rect& rect) {
    target_element_id = element_id < 0 ? 0 : element_id;
    has_target = target_element_id > 0 && rect.w > 0 && rect.h > 0;
    target_rect = rect;
    invalidate();
}

void Tour::set_mask_behavior(bool passthrough, bool close_when_clicked) {
    mask_passthrough = passthrough;
    close_on_mask = close_when_clicked;
    mouse_passthrough = passthrough && mask;
    invalidate();
}

Tour::Part Tour::part_at(int x, int y) const {
    if (!open) return PartNone;
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) {
        return (mask && !mask_passthrough) ? PartMask : PartNone;
    }
    int btn_y = bounds.h - style.pad_bottom - 34;
    Rect close = { bounds.w - style.pad_right - 28, style.pad_top, 24, 24 };
    Rect prev = { bounds.w - style.pad_right - 166, btn_y, 70, 30 };
    Rect next = { bounds.w - style.pad_right - 86, btn_y, 70, 30 };
    if (close.contains(x, y)) return PartClose;
    if (prev.contains(x, y)) return PartPrev;
    if (next.contains(x, y)) return PartNext;
    return PartNone;
}

Element* Tour::hit_test(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    if (mask && !mask_passthrough && parent
        && x >= 0 && y >= 0 && x < parent->bounds.w && y < parent->bounds.h) {
        return this;
    }
    return nullptr;
}

void Tour::paint(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 8.0f;

    if (mask) {
        int ox = 0, oy = 0;
        get_absolute_pos(ox, oy);
        D2D1_MATRIX_3X2_F parent_transform = saved * D2D1::Matrix3x2F::Translation(
            (float)-ox, (float)-oy);
        ctx.rt->SetTransform(parent_transform);
        D2D1_RECT_F full = { 0, 0, (float)bounds.w + (float)ox * 2.0f, (float)bounds.h + (float)oy * 2.0f };
        if (has_target) {
            D2D1_RECT_F top = { 0, 0, full.right, (float)target_rect.y };
            D2D1_RECT_F bottom = { 0, (float)target_rect.bottom(), full.right, full.bottom };
            D2D1_RECT_F left = { 0, (float)target_rect.y, (float)target_rect.x, (float)target_rect.bottom() };
            D2D1_RECT_F right = { (float)target_rect.right(), (float)target_rect.y, full.right, (float)target_rect.bottom() };
            Color mask_color = dark ? 0x88000000 : 0x66000000;
            ctx.rt->FillRectangle(top, ctx.get_brush(mask_color));
            ctx.rt->FillRectangle(bottom, ctx.get_brush(mask_color));
            ctx.rt->FillRectangle(left, ctx.get_brush(mask_color));
            ctx.rt->FillRectangle(right, ctx.get_brush(mask_color));
            D2D1_RECT_F target = { (float)target_rect.x, (float)target_rect.y,
                                   (float)target_rect.right(), (float)target_rect.bottom() };
            ctx.rt->DrawRoundedRectangle(ROUNDED(target, 8.0f, 8.0f),
                                         ctx.get_brush(t->accent), 2.0f);
        } else {
            ctx.rt->FillRectangle(full, ctx.get_brush(dark ? 0x77000000 : 0x55000000));
        }
        ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
            (float)bounds.x, (float)bounds.y));
    }

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    std::wstring title = L"🧭 引导";
    std::wstring body = L"";
    if (active_index >= 0 && active_index < (int)steps.size()) {
        title = steps[active_index].title;
        body = steps[active_index].body;
    }
    tour_draw_text(ctx, title, style, fg,
                   (float)style.pad_left, (float)style.pad_top,
                   (float)bounds.w - style.pad_left - style.pad_right - 34.0f,
                   30.0f, 1.08f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    tour_draw_text(ctx, L"×", style, muted,
                   (float)bounds.w - style.pad_right - 28.0f, (float)style.pad_top,
                   24.0f, 24.0f, 1.0f, DWRITE_FONT_WEIGHT_NORMAL,
                   DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    tour_draw_text(ctx, body, style, muted,
                   (float)style.pad_left, (float)style.pad_top + 40.0f,
                   (float)bounds.w - style.pad_left - style.pad_right,
                   (float)bounds.h - style.pad_top - style.pad_bottom - 84.0f);

    int count = (int)steps.size();
    wchar_t index_buf[32];
    if (count > 0) swprintf_s(index_buf, L"%d / %d", active_index + 1, count);
    else swprintf_s(index_buf, L"0 / 0");
    tour_draw_text(ctx, index_buf, style, muted,
                   (float)style.pad_left, (float)bounds.h - style.pad_bottom - 30.0f,
                   80.0f, 30.0f, 0.92f);

    int btn_y = bounds.h - style.pad_bottom - 34;
    struct ButtonSpec { Rect r; const wchar_t* label; bool primary; };
    ButtonSpec buttons[] = {
        { { bounds.w - style.pad_right - 166, btn_y, 70, 30 }, L"上一步", false },
        { { bounds.w - style.pad_right - 86, btn_y, 70, 30 }, L"下一步", true }
    };
    for (const auto& b : buttons) {
        D2D1_RECT_F br = { (float)b.r.x, (float)b.r.y, (float)b.r.right(), (float)b.r.bottom() };
        Color bbg = b.primary ? t->accent : t->button_bg;
        Color bfg = b.primary ? 0xFFFFFFFF : fg;
        ctx.rt->FillRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(bbg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(br.left + 0.5f, br.top + 0.5f,
            br.right - 0.5f, br.bottom - 0.5f), 4.0f, 4.0f),
            ctx.get_brush(b.primary ? t->accent : border), 1.0f);
        tour_draw_text(ctx, b.label, style, bfg, br.left, br.top, br.right - br.left,
                       br.bottom - br.top, 0.95f, DWRITE_FONT_WEIGHT_NORMAL,
                       DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}

void Tour::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y);
    pressed = true;
    invalidate();
}

void Tour::on_mouse_up(int x, int y, MouseButton) {
    Part p = part_at(x, y);
    if (p == m_press_part) {
        if (p == PartClose) {
            last_action = 3;
            set_open(false);
        } else if (p == PartPrev) {
            last_action = 1;
            set_active_index(active_index - 1);
        } else if (p == PartNext) {
            last_action = 2;
            set_active_index(active_index + 1);
        } else if (p == PartMask && close_on_mask) {
            last_action = 4;
            set_open(false);
        }
    }
    m_press_part = PartNone;
    pressed = false;
    invalidate();
}

void Tour::on_key_down(int vk, int) {
    if (!open) return;
    if (vk == VK_ESCAPE) {
        last_action = 3;
        set_open(false);
    } else if (vk == VK_LEFT || vk == VK_UP) {
        last_action = 1;
        set_active_index(active_index - 1);
    } else if (vk == VK_RIGHT || vk == VK_DOWN || vk == VK_RETURN || vk == VK_SPACE) {
        last_action = 2;
        set_active_index(active_index + 1);
    }
}
