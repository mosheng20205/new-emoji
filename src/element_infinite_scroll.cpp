#include "element_infinite_scroll.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP,
                      float size_scale = 1.0f) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * size_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static D2D1_RECT_F to_d2d_rect(const Rect& r) {
    return { (float)r.x, (float)r.y, (float)(r.x + r.w), (float)(r.y + r.h) };
}

void InfiniteScroll::apply_option_scale(float scale) {
    item_height = (int)std::lround((float)logical_item_height * scale);
    gap = (int)std::lround((float)logical_gap * scale);
    threshold = (int)std::lround((float)logical_threshold * scale);
    if (item_height < 24) item_height = 24;
    if (gap < 0) gap = 0;
    if (threshold < 0) threshold = 0;
    clamp_scroll();
}

void InfiniteScroll::apply_dpi_scale(float scale) {
    Element::apply_dpi_scale(scale);
    apply_option_scale(scale);
}

Rect InfiniteScroll::viewport_rect() const {
    Rect r = content_rect();
    if (show_scrollbar && max_scroll() > 0) {
        r.w -= 14;
        if (r.w < 0) r.w = 0;
    }
    return r;
}

int InfiniteScroll::viewport_height() const {
    Rect r = content_rect();
    return (std::max)(0, r.h);
}

int InfiniteScroll::content_height() const {
    int row_count = (int)items.size();
    int status_h = (int)(style.font_size * 2.4f);
    if (status_h < 32) status_h = 32;

    if (row_count <= 0) {
        return style.pad_top + style.pad_bottom + (std::max)(status_h * 2, viewport_height());
    }

    int total = style.pad_top + style.pad_bottom;
    total += row_count * item_height;
    if (row_count > 1) total += (row_count - 1) * gap;
    if (loading || no_more) total += gap + status_h;
    return total;
}

int InfiniteScroll::max_scroll() const {
    return (std::max)(0, content_height() - viewport_height());
}

void InfiniteScroll::clamp_scroll() {
    int max_value = max_scroll();
    if (scroll_y < 0) scroll_y = 0;
    if (scroll_y > max_value) scroll_y = max_value;
}

void InfiniteScroll::update_scroll(int value, int action) {
    int old = scroll_y;
    scroll_y = value;
    clamp_scroll();
    last_action = action;
    if (scroll_y != old) ++change_count;
    invalidate();
    maybe_trigger_load();
}

void InfiniteScroll::maybe_trigger_load() {
    if (disabled || no_more || loading || items.empty()) return;
    int max_value = max_scroll();
    if (max_value <= 0) return;
    if (scroll_y + viewport_height() + threshold < content_height()) return;

    loading = true;
    ++load_count;
    ++change_count;
    last_action = 10;
    invalidate();
    if (load_cb) load_cb(id, (int)items.size(), scroll_y, max_value);
}

void InfiniteScroll::set_items(const std::vector<InfiniteScrollItem>& next) {
    items = next;
    scroll_y = 0;
    ++change_count;
    last_action = 1;
    invalidate();
}

void InfiniteScroll::append_items(const std::vector<InfiniteScrollItem>& more) {
    if (more.empty()) return;
    items.insert(items.end(), more.begin(), more.end());
    clamp_scroll();
    ++change_count;
    last_action = 2;
    invalidate();
}

void InfiniteScroll::clear_items() {
    items.clear();
    scroll_y = 0;
    ++change_count;
    last_action = 3;
    invalidate();
}

void InfiniteScroll::set_state(bool next_loading, bool next_no_more, bool next_disabled) {
    loading = next_loading;
    no_more = next_no_more;
    disabled = next_disabled;
    if (no_more) loading = false;
    clamp_scroll();
    ++change_count;
    last_action = 4;
    invalidate();
}

void InfiniteScroll::set_options(int next_item_height, int next_gap, int next_threshold,
                                 int next_style_mode, bool next_show_scrollbar,
                                 bool next_show_index, float scale) {
    if (next_item_height < 24) next_item_height = 24;
    if (next_item_height > 220) next_item_height = 220;
    if (next_gap < 0) next_gap = 0;
    if (next_gap > 48) next_gap = 48;
    if (next_threshold < 0) next_threshold = 0;
    if (next_threshold > 2000) next_threshold = 2000;
    logical_item_height = next_item_height;
    logical_gap = next_gap;
    logical_threshold = next_threshold;
    style_mode = (std::max)(0, (std::min)(3, next_style_mode));
    show_scrollbar = next_show_scrollbar;
    show_index = next_show_index;
    apply_option_scale(scale <= 0.0f ? 1.0f : scale);
    ++change_count;
    last_action = 5;
    invalidate();
}

void InfiniteScroll::set_texts(const std::wstring& loading_value,
                               const std::wstring& no_more_value,
                               const std::wstring& empty_value) {
    loading_text = loading_value.empty() ? L"加载中..." : loading_value;
    no_more_text = no_more_value.empty() ? L"没有更多了" : no_more_value;
    empty_text = empty_value.empty() ? L"暂无数据" : empty_value;
    ++change_count;
    last_action = 11;
    invalidate();
}

void InfiniteScroll::set_scroll(int value) {
    update_scroll(value, 6);
}

Rect InfiniteScroll::scrollbar_track_rect() const {
    Rect c = content_rect();
    int w = (std::min)(10, (std::max)(6, c.w / 24));
    return { c.x + c.w - w, c.y + 2, w, (std::max)(1, c.h - 4) };
}

Rect InfiniteScroll::scrollbar_thumb_rect() const {
    Rect track = scrollbar_track_rect();
    int max_value = max_scroll();
    if (max_value <= 0) return { track.x, track.y, track.w, track.h };

    int view = viewport_height();
    int total = content_height();
    int min_thumb = (std::min)(54, (std::max)(28, track.h / 6));
    int thumb_h = (int)((double)track.h * view / (std::max)(view, total) + 0.5);
    thumb_h = (std::min)(track.h, (std::max)(min_thumb, thumb_h));
    int travel = (std::max)(0, track.h - thumb_h);
    int y = track.y + (int)((double)travel * scroll_y / max_value + 0.5);
    return { track.x, y, track.w, thumb_h };
}

void InfiniteScroll::update_scroll_from_thumb(int y) {
    Rect track = scrollbar_track_rect();
    Rect thumb = scrollbar_thumb_rect();
    int travel = track.h - thumb.h;
    if (travel <= 0) {
        update_scroll(0, 8);
        return;
    }
    int pos = y - track.y - drag_offset;
    if (pos < 0) pos = 0;
    if (pos > travel) pos = travel;
    update_scroll((int)((double)max_scroll() * pos / travel + 0.5), 8);
}

void InfiniteScroll::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF20243A : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : (dark ? 0xFF3D4668 : 0xFFD2DCEB);
    Color text_color = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color card = dark ? 0xFF282D45 : 0xFFF8FBFF;
    Color card_alt = dark ? 0xFF252B42 : 0xFFFFFFFF;
    Color selected = dark ? 0xFF253654 : 0xFFEBF5FF;

    D2D1_RECT_F outer = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(outer, style.corner_radius, style.corner_radius),
                                 ctx.get_brush(bg));
    if (style.border_width > 0.0f) {
        float hw = style.border_width * 0.5f;
        D2D1_RECT_F br = { hw, hw, (float)bounds.w - hw, (float)bounds.h - hw };
        ctx.rt->DrawRoundedRectangle(ROUNDED(br, style.corner_radius, style.corner_radius),
                                     ctx.get_brush(border), style.border_width);
    }

    Rect c = content_rect();
    D2D1_RECT_F clip = to_d2d_rect(c);
    ctx.push_clip(clip);

    if (items.empty()) {
        draw_text(ctx, empty_text, style, muted,
                  (float)c.x, (float)c.y, (float)c.w, (float)c.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                  DWRITE_WORD_WRAPPING_WRAP, 1.05f);
    } else {
        Rect view = viewport_rect();
        int y = style.pad_top - scroll_y;
        for (int i = 0; i < (int)items.size(); ++i) {
            Rect row = { view.x, y, view.w, item_height };
            y += item_height + gap;
            if (row.y + row.h < c.y || row.y > c.y + c.h) continue;

            Color row_bg = (i % 2 == 0) ? card : card_alt;
            float radius = 7.0f;
            if (style_mode == 2) {
                row_bg = 0;
                radius = 0.0f;
            } else if (style_mode == 3) {
                row_bg = (i % 2 == 0) ? selected : card;
            }

            if (row_bg) {
                D2D1_RECT_F rr = to_d2d_rect(row);
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, radius, radius), ctx.get_brush(row_bg));
                ctx.rt->DrawRoundedRectangle(ROUNDED(rr, radius, radius),
                                             ctx.get_brush(with_alpha(border, dark ? 0x80 : 0xB0)), 1.0f);
            }

            if (style_mode == 3) {
                D2D1_RECT_F stripe = { (float)row.x, (float)row.y + 8.0f,
                                       (float)row.x + 4.0f, (float)(row.y + row.h - 8) };
                ctx.rt->FillRoundedRectangle(ROUNDED(stripe, 2.0f, 2.0f), ctx.get_brush(t->accent));
            }

            int left = row.x + (style_mode == 3 ? 18 : 14);
            if (show_index) {
                wchar_t buf[32];
                swprintf_s(buf, L"%02d", i + 1);
                draw_text(ctx, buf, style, muted, (float)left, (float)row.y,
                          36.0f, (float)row.h, DWRITE_TEXT_ALIGNMENT_CENTER);
                left += 48;
            }

            const auto& item = items[i];
            int tag_w = item.tag.empty() ? 0 : (std::min)(120, (std::max)(58, (int)item.tag.size() * 15 + 18));
            float title_h = item.subtitle.empty() ? (float)row.h : (float)row.h * 0.48f;
            draw_text(ctx, item.title, style, text_color,
                      (float)left, (float)row.y + (item.subtitle.empty() ? 0.0f : 8.0f),
                      (float)(row.w - (left - row.x) - tag_w - 14), title_h,
                      DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      DWRITE_WORD_WRAPPING_NO_WRAP, style_mode == 2 ? 0.95f : 1.0f);
            if (!item.subtitle.empty()) {
                draw_text(ctx, item.subtitle, style, muted,
                          (float)left, (float)row.y + title_h,
                          (float)(row.w - (left - row.x) - tag_w - 14), (float)row.h - title_h,
                          DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                          DWRITE_WORD_WRAPPING_NO_WRAP, 0.86f);
            }
            if (!item.tag.empty() && tag_w > 0) {
                D2D1_RECT_F pill = {
                    (float)(row.x + row.w - tag_w - 12),
                    (float)(row.y + row.h / 2 - 13),
                    (float)(row.x + row.w - 12),
                    (float)(row.y + row.h / 2 + 13)
                };
                ctx.rt->FillRoundedRectangle(ROUNDED(pill, 13.0f, 13.0f),
                                             ctx.get_brush(with_alpha(t->accent, dark ? 0x36 : 0x24)));
                draw_text(ctx, item.tag, style, t->accent,
                          pill.left + 8.0f, pill.top, pill.right - pill.left - 16.0f,
                          pill.bottom - pill.top, DWRITE_TEXT_ALIGNMENT_CENTER,
                          DWRITE_PARAGRAPH_ALIGNMENT_CENTER, DWRITE_WORD_WRAPPING_NO_WRAP, 0.82f);
            }
        }

        if (loading || no_more) {
            std::wstring status = loading ? loading_text : no_more_text;
            int status_y = style.pad_top - scroll_y + (int)items.size() * item_height
                + (std::max)(0, (int)items.size() - 1) * gap + gap;
            draw_text(ctx, status, style, muted,
                      (float)c.x, (float)status_y, (float)c.w, style.font_size * 2.4f,
                      DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      DWRITE_WORD_WRAPPING_NO_WRAP, 0.92f);
        }
    }

    ctx.pop_clip();

    if (show_scrollbar && max_scroll() > 0) {
        Rect tr = scrollbar_track_rect();
        Rect th = scrollbar_thumb_rect();
        float radius = tr.w * 0.5f;
        ctx.rt->FillRoundedRectangle(ROUNDED(to_d2d_rect(tr), radius, radius),
                                     ctx.get_brush(dark ? with_alpha(0xFFFFFFFF, 0x12) : with_alpha(0xFF000000, 0x0A)));
        ctx.rt->FillRoundedRectangle(ROUNDED(to_d2d_rect(th), radius, radius),
                                     ctx.get_brush(pressed ? t->accent : with_alpha(t->text_secondary, dark ? 0xAA : 0x90)));
    }

    ctx.rt->SetTransform(saved);
}

void InfiniteScroll::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    dragging_thumb = false;
    drag_start_scroll = scroll_y;
    if (show_scrollbar && max_scroll() > 0) {
        Rect thumb = scrollbar_thumb_rect();
        Rect track = scrollbar_track_rect();
        if (thumb.contains(x, y)) {
            dragging_thumb = true;
            drag_offset = y - thumb.y;
        } else if (track.contains(x, y)) {
            drag_offset = thumb.h / 2;
            update_scroll_from_thumb(y);
        }
    }
    invalidate();
}

void InfiniteScroll::on_mouse_up(int, int, MouseButton) {
    if (scroll_y != drag_start_scroll) {
        ++change_count;
        last_action = 8;
    }
    pressed = false;
    dragging_thumb = false;
    drag_offset = 0;
    invalidate();
}

void InfiniteScroll::on_mouse_move(int, int y) {
    if (pressed && dragging_thumb) update_scroll_from_thumb(y);
}

void InfiniteScroll::on_mouse_wheel(int, int, int delta) {
    if (delta == 0) return;
    int steps = delta / WHEEL_DELTA;
    if (steps == 0) steps = delta > 0 ? 1 : -1;
    int wheel_step = (std::max)(24, item_height + gap);
    last_wheel_delta = delta;
    update_scroll(scroll_y - steps * wheel_step, 7);
}

void InfiniteScroll::on_key_down(int vk, int) {
    int page = (std::max)(item_height + gap, viewport_height() - item_height);
    switch (vk) {
    case VK_UP:
        update_scroll(scroll_y - (item_height + gap), 9);
        break;
    case VK_DOWN:
        update_scroll(scroll_y + item_height + gap, 9);
        break;
    case VK_PRIOR:
        update_scroll(scroll_y - page, 9);
        break;
    case VK_NEXT:
        update_scroll(scroll_y + page, 9);
        break;
    case VK_HOME:
        update_scroll(0, 9);
        break;
    case VK_END:
        update_scroll(max_scroll(), 9);
        break;
    }
}
