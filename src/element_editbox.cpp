#include "element_editbox.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cmath>

// Global blink timer → EditBox* mapping
std::map<UINT_PTR, EditBox*> g_blink_map;

// ── Blink timer ──────────────────────────────────────────────────────

void CALLBACK EditBox::blink_timer(HWND hwnd, UINT, UINT_PTR id, DWORD) {
    PostMessageW(hwnd, WM_USER + 100, 0, (LPARAM)id);
}

void EditBox::start_blink() {
    if (m_blink_id) return;
    if (!owner_hwnd) return;
    m_blink_id = SetTimer(owner_hwnd, 0xE000, 530, blink_timer);
    m_cursor_on = true;
}

void EditBox::stop_blink() {
    if (m_blink_id && owner_hwnd) {
        KillTimer(owner_hwnd, m_blink_id);
        m_blink_id = 0;
    }
}

// ── Paint ────────────────────────────────────────────────────────────

void EditBox::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    // Save transform and translate to local coords
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg     = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = style.border_color ? style.border_color : t->edit_border;
    Color fg     = style.fg_color ? style.fg_color : t->text_primary;
    Color fb     = focus_border ? focus_border : t->edit_focus;

    float r = style.corner_radius > 0 ? style.corner_radius : 4.0f;
    float pad_l = (float)style.pad_left;
    float pad_t = (float)style.pad_top;
    float pad_r = (float)style.pad_right;
    float pad_b = (float)style.pad_bottom;

    // Background at (0,0)
    {
        auto* br = ctx.get_brush(bg);
        D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
        D2D1_ROUNDED_RECT rr = { rect, r, r };
        ctx.rt->FillRoundedRectangle(rr, br);
    }

    // Border at (0,0)
    {
        auto* br = ctx.get_brush(has_focus ? fb : border);
        float bw = has_focus ? 2.0f : 1.0f;
        D2D1_RECT_F rect = { bw * 0.5f, bw * 0.5f,
                             (float)bounds.w - bw * 0.5f, (float)bounds.h - bw * 0.5f };
        D2D1_ROUNDED_RECT rr = { rect, r, r };
        ctx.rt->DrawRoundedRectangle(rr, br, bw);
    }

    // Text
    std::wstring display;
    if (password && !text.empty()) {
        display = std::wstring(text.size(), L'•');
    } else {
        display = text;
        if (m_composing && !m_comp_text.empty()) {
            int pos = m_cursor_pos < 0 ? 0 : m_cursor_pos;
            if (pos > (int)display.size()) pos = (int)display.size();
            display.insert(pos, m_comp_text);
        }
    }

    bool drawing_placeholder = display.empty() && !has_focus && !placeholder.empty();
    const std::wstring& draw_value = drawing_placeholder ? placeholder : display;

    if (!draw_value.empty()) {
        float max_w = (float)bounds.w - pad_l - pad_r - (needs_vscroll() ? 14.0f : 0.0f);
        float max_h = (float)bounds.h - pad_t - pad_b;
        if (max_w < 1.0f) max_w = 1.0f;
        if (max_h < 1.0f) max_h = 1.0f;

        auto* layout = ctx.create_text_layout(draw_value, style.font_name, style.font_size,
                                              max_w, multiline ? 8192.0f : max_h);
        if (layout) {
            layout->SetParagraphAlignment(multiline
                ? DWRITE_PARAGRAPH_ALIGNMENT_NEAR
                : DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            layout->SetWordWrapping(multiline ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);

            // Cache text width for cursor positioning
            DWRITE_TEXT_METRICS tm;
            layout->GetMetrics(&tm);
            m_cached_text_w = tm.width;
            m_cached_content_h = (std::max)(1, (int)std::ceil(tm.height));
            m_cached_view_h = estimate_view_height();
            clamp_scroll_y();

            // Selection highlight
            if (m_sel_start >= 0 && m_sel_end > m_sel_start) {
                int s = m_sel_start, e = m_sel_end;
                if (s > e) std::swap(s, e);

                DWRITE_HIT_TEST_METRICS htm;
                UINT32 actual_count = 0;
                layout->HitTestTextRange(s, (UINT32)(e - s), 0, 0, &htm, 1, &actual_count);
                float sel_left = htm.left;
                float sel_top  = htm.top;
                float sel_w    = htm.width;
                float sel_h    = htm.height;

                auto* sel_br = ctx.get_brush(t->accent & 0x80FFFFFF);
                D2D1_RECT_F sel_rect = {
                    pad_l + sel_left - m_scroll_x,
                    pad_t + sel_top - (multiline ? (float)m_scroll_y : 0.0f),
                    pad_l + sel_left + sel_w - m_scroll_x,
                    pad_t + sel_top + sel_h - (multiline ? (float)m_scroll_y : 0.0f)
                };
                if (multiline) {
                    ctx.push_clip(D2D1::RectF(0.0f, 0.0f,
                        (float)bounds.w - (needs_vscroll() ? 14.0f : 0.0f),
                        (float)bounds.h));
                }
                ctx.rt->FillRectangle(sel_rect, sel_br);
                if (multiline) ctx.pop_clip();
            }

            // Draw text at (0,0)
            if (multiline) {
                ctx.push_clip(D2D1::RectF(pad_l, pad_t, pad_l + max_w, pad_t + max_h));
            }
            D2D1_POINT_2F pt = { pad_l - m_scroll_x, pad_t - (multiline ? (float)m_scroll_y : 0.0f) };
            ctx.rt->DrawTextLayout(pt, layout, ctx.get_brush(drawing_placeholder ? t->text_muted : fg),
                                   D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            if (multiline) ctx.pop_clip();

            // Caret
            if (has_focus && m_cursor_on) {
                DWRITE_HIT_TEST_METRICS hit{};
                float hit_x = 0.0f;
                float hit_y = 0.0f;
                BOOL trailing = FALSE;
                BOOL inside = FALSE;
                layout->HitTestTextPosition((UINT32)(std::max)(0, (std::min)(m_cursor_pos, (int)draw_value.size())),
                                            FALSE, &hit_x, &hit_y, &hit);
                float cx = pad_l + (multiline ? hit_x : char_to_xpos(m_cursor_pos)) - m_scroll_x;
                float cy = pad_t + (multiline ? hit_y - (float)m_scroll_y : 0.0f);
                float ch = multiline ? hit.height : (float)bounds.h - pad_t - pad_b;
                if (ch < 4) ch = (float)bounds.h;
                if (!multiline || (cy + ch >= pad_t && cy <= pad_t + max_h)) {
                    ctx.rt->DrawLine(D2D1::Point2F(cx, cy), D2D1::Point2F(cx, cy + ch),
                                     ctx.get_brush(fg), 1.5f);
                }
            }

            layout->Release();
        }
    } else if (has_focus && m_cursor_on) {
        float cx = pad_l, cy = pad_t, ch = (float)bounds.h - pad_t - pad_b;
        ctx.rt->DrawLine(D2D1::Point2F(cx, cy), D2D1::Point2F(cx, cy + ch),
                         ctx.get_brush(fg), 1.5f);
    }

    if (needs_vscroll()) {
        Rect tr = scrollbar_track_rect();
        Rect th = scrollbar_thumb_rect();
        float radius = (float)tr.w * 0.5f;
        ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ D2D1::RectF((float)tr.x, (float)tr.y, (float)(tr.x + tr.w), (float)(tr.y + tr.h)), radius, radius },
                                     ctx.get_brush(0x18000000));
        ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ D2D1::RectF((float)th.x, (float)th.y, (float)(th.x + th.w), (float)(th.y + th.h)), radius, radius },
                                     ctx.get_brush(has_focus ? fb : 0x66000000));
    }

    ctx.rt->SetTransform(saved);
}

// ── Mouse ────────────────────────────────────────────────────────────

void EditBox::on_mouse_down(int x, int y, MouseButton) {
    if (!enabled) return;
    if (multiline && needs_vscroll()) {
        Rect thumb = scrollbar_thumb_rect();
        Rect track = scrollbar_track_rect();
        if (thumb.contains(x, y)) {
            m_drag_scrollbar = true;
            m_drag_scroll_offset = y - thumb.y;
            pressed = true;
            invalidate();
            return;
        }
        if (track.contains(x, y)) {
            set_scroll_y(m_scroll_y + (y < thumb.y ? -estimate_view_height() : estimate_view_height()));
            return;
        }
    }
    if (readonly) return;
    m_cursor_pos = xpos_to_char(x - style.pad_left);
    m_sel_start = -1;
    m_sel_end   = -1;
    start_blink();
    invalidate();
}

void EditBox::on_mouse_up(int, int, MouseButton) {
    m_drag_scrollbar = false;
    pressed = false;
    invalidate();
}

void EditBox::on_mouse_move(int, int y) {
    if (m_drag_scrollbar) update_scroll_from_thumb(y);
}

void EditBox::on_mouse_wheel(int, int, int delta) {
    if (!multiline || max_scroll_y() <= 0) return;
    int steps = delta / WHEEL_DELTA;
    if (steps == 0) steps = delta > 0 ? 1 : -1;
    int line = (int)std::lround(style.font_size * 1.4f);
    if (line < 16) line = 16;
    set_scroll_y(m_scroll_y - steps * line * 3);
}

// ── Keyboard ─────────────────────────────────────────────────────────

void EditBox::on_key_down(int vk, int mods) {
    bool shift = (mods & KeyMod::Shift) != 0;
    bool ctrl  = (mods & KeyMod::Control) != 0;

    switch (vk) {
    case VK_LEFT:  move_cursor(-1, shift); break;
    case VK_RIGHT: move_cursor(1, shift); break;
    case VK_HOME:
        if (!shift) { m_sel_start = -1; m_sel_end = -1; }
        if (shift && m_sel_start < 0) m_sel_start = m_cursor_pos;
        m_cursor_pos = 0;
        if (shift) m_sel_end = m_cursor_pos;
        break;
    case VK_END:
        if (!shift) { m_sel_start = -1; m_sel_end = -1; }
        if (shift && m_sel_start < 0) m_sel_start = m_cursor_pos;
        m_cursor_pos = (int)text.size();
        if (shift) m_sel_end = m_cursor_pos;
        break;
    case VK_BACK:
        if (m_sel_start >= 0 && m_sel_end > m_sel_start) delete_selection();
        else delete_char_before();
        break;
    case VK_DELETE:
        if (m_sel_start >= 0 && m_sel_end > m_sel_start) delete_selection();
        else delete_char_after();
        break;
    case 'A':
        if (ctrl) { m_sel_start = 0; m_sel_end = (int)text.size(); m_cursor_pos = m_sel_end; }
        break;
    case 'C':
        if (ctrl && m_sel_start >= 0 && m_sel_end > m_sel_start && !password) {
            int s = m_sel_start, e = m_sel_end;
            if (s > e) std::swap(s, e);
            std::wstring sel = text.substr(s, e - s);
            if (OpenClipboard(owner_hwnd)) {
                EmptyClipboard();
                size_t bytes = (sel.size() + 1) * sizeof(wchar_t);
                HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, bytes);
                if (hMem) {
                    memcpy(GlobalLock(hMem), sel.c_str(), bytes);
                    GlobalUnlock(hMem);
                    SetClipboardData(CF_UNICODETEXT, hMem);
                }
                CloseClipboard();
            }
        }
        break;
    case 'V':
        if (ctrl && !readonly) {
            if (OpenClipboard(owner_hwnd)) {
                HANDLE hData = GetClipboardData(CF_UNICODETEXT);
                if (hData) {
                    wchar_t* p = (wchar_t*)GlobalLock(hData);
                    if (p) { delete_selection(); insert_text(p); }
                    GlobalUnlock(hData);
                }
                CloseClipboard();
            }
        }
        break;
    case 'X':
        if (ctrl && !readonly && !password && m_sel_start >= 0 && m_sel_end > m_sel_start) {
            int s = m_sel_start, e = m_sel_end;
            if (s > e) std::swap(s, e);
            std::wstring sel = text.substr(s, e - s);
            if (OpenClipboard(owner_hwnd)) {
                EmptyClipboard();
                size_t bytes = (sel.size() + 1) * sizeof(wchar_t);
                HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, bytes);
                if (hMem) { memcpy(GlobalLock(hMem), sel.c_str(), bytes); GlobalUnlock(hMem); SetClipboardData(CF_UNICODETEXT, hMem); }
                CloseClipboard();
            }
            delete_selection();
        }
        break;
case VK_RETURN:
        if (multiline) { delete_selection(); insert_text(L"\n"); }
        break;
    }
    start_blink();
    invalidate();
}

void EditBox::on_char(wchar_t ch) {
    if (readonly || !enabled) return;
    if (ch < 32) return;
    delete_selection();
    insert_text(std::wstring(1, ch));
    start_blink();
    invalidate();
}

void EditBox::on_focus()  { has_focus = true; m_cursor_on = true; start_blink(); invalidate(); }
void EditBox::on_blur()   { has_focus = false; stop_blink(); invalidate(); }

void EditBox::on_dpi_scale_changed(float old_scale, float new_scale) {
    if (old_scale > 0.0f && new_scale > 0.0f) {
        m_scroll_x = (int)(m_scroll_x * new_scale / old_scale + 0.5f);
    }
    m_cached_text_w = 0.0f;
}

// ── Text editing helpers ─────────────────────────────────────────────

void EditBox::set_options(int read_only, int is_password, int is_multiline, Color focus_color,
                          const std::wstring& placeholder_text) {
    readonly = read_only != 0;
    password = is_password != 0;
    multiline = is_multiline != 0;
    m_cached_content_h = 0;
    if (!multiline) m_scroll_y = 0;
    focus_border = focus_color;
    placeholder = placeholder_text;
    invalidate();
}

void EditBox::set_value(const std::wstring& value) {
    text = value;
    m_cached_content_h = 0;
    m_cursor_pos = (int)text.size();
    m_sel_start = -1;
    m_sel_end = -1;
    scroll_to_cursor();
    notify_text_changed();
    invalidate();
}

void EditBox::set_composition_text(const std::wstring& value) {
    m_composing = !value.empty();
    m_comp_text = value;
    invalidate();
}

void EditBox::end_composition() {
    m_composing = false;
    m_comp_text.clear();
    invalidate();
}

void EditBox::commit_text(const std::wstring& value) {
    if (readonly || !enabled || value.empty()) return;
    delete_selection();
    insert_text(value);
    end_composition();
    start_blink();
}

void EditBox::get_state(int& cursor, int& sel_start, int& sel_end, int& text_length) const {
    cursor = m_cursor_pos;
    sel_start = m_sel_start;
    sel_end = m_sel_end;
    text_length = (int)text.size();
}

void EditBox::set_scroll_y(int value) {
    m_scroll_y = value;
    clamp_scroll_y();
    invalidate();
}

void EditBox::get_scroll_state(int& scroll_y, int& max_value, int& content_height, int& viewport_height) const {
    content_height = estimate_content_height();
    viewport_height = estimate_view_height();
    max_value = (std::max)(0, content_height - viewport_height);
    scroll_y = (std::max)(0, (std::min)(m_scroll_y, max_value));
}

void EditBox::insert_text(const std::wstring& s) {
    if (s.empty()) return;
    int pos = m_cursor_pos;
    if (pos < 0) pos = 0;
    if (pos > (int)text.size()) pos = (int)text.size();
    text.insert(pos, s);
    m_cached_content_h = 0;
    m_cursor_pos = pos + (int)s.size();
    m_sel_start = -1; m_sel_end = -1;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::delete_selection() {
    if (m_sel_start < 0 || m_sel_end <= m_sel_start) return;
    int s = m_sel_start, e = m_sel_end;
    if (s > e) std::swap(s, e);
    text.erase(s, e - s);
    m_cached_content_h = 0;
    m_cursor_pos = s;
    m_sel_start = -1; m_sel_end = -1;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::delete_char_before() {
    if (m_cursor_pos <= 0) return;
    text.erase(m_cursor_pos - 1, 1);
    m_cached_content_h = 0;
    m_cursor_pos--;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::delete_char_after() {
    if (m_cursor_pos >= (int)text.size()) return;
    text.erase(m_cursor_pos, 1);
    m_cached_content_h = 0;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::notify_text_changed() {
    if (!text_cb) return;
    std::string utf8 = wide_to_utf8(text);
    text_cb(id, reinterpret_cast<const unsigned char*>(utf8.data()), (int)utf8.size());
}

void EditBox::move_cursor(int delta, bool extend) {
    if (!extend) { m_sel_start = -1; m_sel_end = -1; }
    if (extend && m_sel_start < 0) m_sel_start = m_cursor_pos;
    m_cursor_pos += delta;
    if (m_cursor_pos < 0) m_cursor_pos = 0;
    if (m_cursor_pos > (int)text.size()) m_cursor_pos = (int)text.size();
    if (extend) m_sel_end = m_cursor_pos;
    scroll_to_cursor();
}

// ── Position helpers ────────────────────────────────────────────────

int EditBox::xpos_to_char(int x) {
    int total = (int)text.size();
    if (total == 0) return 0;
    x += m_scroll_x;
    if (m_cached_text_w > 1.0f) {
        int idx = (int)(x * total / m_cached_text_w + 0.5f);
        if (idx < 0) idx = 0;
        if (idx > total) idx = total;
        return idx;
    }
    float cw = style.font_size * 0.6f;
    if (cw <= 0) cw = 8.0f;
    int idx = (int)(x / cw + 0.5f);
    if (idx < 0) idx = 0;
    if (idx > total) idx = total;
    return idx;
}

int EditBox::char_to_xpos(int idx) {
    int total = (int)text.size();
    if (total == 0) return 0;
    if (m_cached_text_w > 1.0f) {
        return (int)(idx * m_cached_text_w / total);
    }
    float cw = style.font_size * 0.6f;
    if (cw <= 0) cw = 8.0f;
    return (int)(idx * cw);
}

int EditBox::estimate_view_height() const {
    return (std::max)(1, bounds.h - style.pad_top - style.pad_bottom);
}

int EditBox::estimate_content_height() const {
    if (!multiline) return estimate_view_height();
    if (m_cached_content_h > 1) return m_cached_content_h;
    int max_w = bounds.w - style.pad_left - style.pad_right - 14;
    int chars_per_line = (std::max)(1, max_w / (std::max)(6, (int)(style.font_size * 0.62f)));
    int rows = 1;
    int current = 0;
    for (wchar_t ch : text.empty() ? placeholder : text) {
        if (ch == L'\n') {
            rows += (std::max)(1, (current + chars_per_line - 1) / chars_per_line);
            current = 0;
        } else {
            ++current;
        }
    }
    rows += (std::max)(0, (current + chars_per_line - 1) / chars_per_line);
    int line_h = (int)std::lround(style.font_size * 1.35f);
    if (line_h < 18) line_h = 18;
    return rows * line_h;
}

int EditBox::max_scroll_y() const {
    return (std::max)(0, estimate_content_height() - estimate_view_height());
}

bool EditBox::needs_vscroll() const {
    return multiline && max_scroll_y() > 0;
}

void EditBox::clamp_scroll_y() {
    int max_value = max_scroll_y();
    if (m_scroll_y < 0) m_scroll_y = 0;
    if (m_scroll_y > max_value) m_scroll_y = max_value;
}

Rect EditBox::scrollbar_track_rect() const {
    int w = (std::min)(10, (std::max)(6, bounds.w / 24));
    return { bounds.w - style.pad_right - w, style.pad_top + 2, w, (std::max)(1, bounds.h - style.pad_top - style.pad_bottom - 4) };
}

Rect EditBox::scrollbar_thumb_rect() const {
    Rect track = scrollbar_track_rect();
    int max_value = max_scroll_y();
    if (max_value <= 0) return track;
    int view = estimate_view_height();
    int content = estimate_content_height();
    int thumb_h = (int)((double)track.h * view / (std::max)(1, content));
    thumb_h = (std::max)(24, (std::min)(track.h, thumb_h));
    int travel = (std::max)(0, track.h - thumb_h);
    int y = track.y + (int)((double)travel * m_scroll_y / max_value + 0.5);
    return { track.x, y, track.w, thumb_h };
}

void EditBox::update_scroll_from_thumb(int y) {
    Rect track = scrollbar_track_rect();
    Rect thumb = scrollbar_thumb_rect();
    int travel = track.h - thumb.h;
    if (travel <= 0) {
        set_scroll_y(0);
        return;
    }
    int pos = y - track.y - m_drag_scroll_offset;
    if (pos < 0) pos = 0;
    if (pos > travel) pos = travel;
    m_scroll_y = (int)((double)max_scroll_y() * pos / travel + 0.5);
    clamp_scroll_y();
    invalidate();
}

void EditBox::scroll_to_cursor() {
    if (multiline) {
        int line_h = (int)std::lround(style.font_size * 1.35f);
        if (line_h < 18) line_h = 18;
        int line = 0;
        for (int i = 0; i < m_cursor_pos && i < (int)text.size(); ++i) {
            if (text[i] == L'\n') ++line;
        }
        int cy = line * line_h;
        int view = estimate_view_height();
        if (cy < m_scroll_y) m_scroll_y = cy;
        else if (cy + line_h > m_scroll_y + view) m_scroll_y = cy + line_h - view;
        clamp_scroll_y();
        return;
    }
    int cx = char_to_xpos(m_cursor_pos);
    int max_vis = bounds.w - style.pad_left - style.pad_right;
    if (cx - m_scroll_x < 0) {
        m_scroll_x = cx - 20;
        if (m_scroll_x < 0) m_scroll_x = 0;
    } else if (cx - m_scroll_x > max_vis) {
        m_scroll_x = cx - max_vis + 20;
    }
}
