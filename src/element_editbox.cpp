#include "element_editbox.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"

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
        float max_w = (float)bounds.w - pad_l - pad_r;
        float max_h = (float)bounds.h - pad_t - pad_b;
        if (max_w < 1.0f) max_w = 1.0f;
        if (max_h < 1.0f) max_h = 1.0f;

        auto* layout = ctx.create_text_layout(draw_value, style.font_name, style.font_size,
                                              max_w, max_h);
        if (layout) {
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);

            // Cache text width for cursor positioning
            DWRITE_TEXT_METRICS tm;
            layout->GetMetrics(&tm);
            m_cached_text_w = tm.width;

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
                    pad_t + sel_top,
                    pad_l + sel_left + sel_w - m_scroll_x,
                    pad_t + sel_top + sel_h
                };
                ctx.rt->FillRectangle(sel_rect, sel_br);
            }

            // Draw text at (0,0)
            D2D1_POINT_2F pt = { pad_l - m_scroll_x, pad_t };
            ctx.rt->DrawTextLayout(pt, layout, ctx.get_brush(drawing_placeholder ? t->text_muted : fg),
                                   D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);

            // Caret
            if (has_focus && m_cursor_on) {
                float cx = pad_l + char_to_xpos(m_cursor_pos) - m_scroll_x;
                float cy = pad_t;
                float ch = (float)bounds.h - pad_t - pad_b;
                if (ch < 4) ch = (float)bounds.h;
                ctx.rt->DrawLine(D2D1::Point2F(cx, cy), D2D1::Point2F(cx, cy + ch),
                                 ctx.get_brush(fg), 1.5f);
            }

            layout->Release();
        }
    } else if (has_focus && m_cursor_on) {
        float cx = pad_l, cy = pad_t, ch = (float)bounds.h - pad_t - pad_b;
        ctx.rt->DrawLine(D2D1::Point2F(cx, cy), D2D1::Point2F(cx, cy + ch),
                         ctx.get_brush(fg), 1.5f);
    }

    ctx.rt->SetTransform(saved);
}

// ── Mouse ────────────────────────────────────────────────────────────

void EditBox::on_mouse_down(int x, int y, MouseButton) {
    if (!enabled || readonly) return;
    m_cursor_pos = xpos_to_char(x - style.pad_left);
    m_sel_start = -1;
    m_sel_end   = -1;
    start_blink();
    invalidate();
}

void EditBox::on_mouse_move(int, int) {}

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
    focus_border = focus_color;
    placeholder = placeholder_text;
    invalidate();
}

void EditBox::set_value(const std::wstring& value) {
    text = value;
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

void EditBox::insert_text(const std::wstring& s) {
    if (s.empty()) return;
    int pos = m_cursor_pos;
    if (pos < 0) pos = 0;
    if (pos > (int)text.size()) pos = (int)text.size();
    text.insert(pos, s);
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
    m_cursor_pos = s;
    m_sel_start = -1; m_sel_end = -1;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::delete_char_before() {
    if (m_cursor_pos <= 0) return;
    text.erase(m_cursor_pos - 1, 1);
    m_cursor_pos--;
    scroll_to_cursor();
    notify_text_changed();
}

void EditBox::delete_char_after() {
    if (m_cursor_pos >= (int)text.size()) return;
    text.erase(m_cursor_pos, 1);
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

void EditBox::scroll_to_cursor() {
    int cx = char_to_xpos(m_cursor_pos);
    int max_vis = bounds.w - style.pad_left - style.pad_right;
    if (cx - m_scroll_x < 0) {
        m_scroll_x = cx - 20;
        if (m_scroll_x < 0) m_scroll_x = 0;
    } else if (cx - m_scroll_x > max_vis) {
        m_scroll_x = cx - max_vis + 20;
    }
}
