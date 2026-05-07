#include "element_omnibox.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text,
                      const ElementStyle& style, Color color,
                      float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

int Omnibox::char_width() const {
    return (std::max)(6, (int)std::lround(style.font_size * 0.58f));
}

bool Omnibox::has_selection() const {
    return sel_start >= 0 && sel_end >= 0 && sel_start != sel_end;
}

void Omnibox::clear_selection() {
    sel_start = -1;
    sel_end = -1;
}

void Omnibox::select_all() {
    sel_start = 0;
    sel_end = (int)value.size();
    cursor_pos = sel_end;
}

float Omnibox::text_start_x() const {
    float x = 12.0f + 28.0f;
    if (!chip_text.empty() || !chip_icon.empty()) {
        std::wstring chip = chip_icon.empty() ? chip_text : (chip_icon + L" " + chip_text);
        float cw = (std::max)(42.0f, 18.0f + (float)chip.size() * style.font_size * 0.5f);
        x += cw + 8.0f;
    } else if (!security_label.empty()) {
        x += 88.0f;
    }
    return x;
}

float Omnibox::text_width() const {
    float action_w = (float)action_icons.size() * 30.0f;
    float w = (float)bounds.w - text_start_x() - action_w - 12.0f;
    return w < 1.0f ? 1.0f : w;
}

float Omnibox::text_x_for_index(RenderContext& ctx, const std::wstring& text, int index, float max_w, float max_h) const {
    if (index <= 0 || text.empty()) return 0.0f;
    if (index > (int)text.size()) index = (int)text.size();
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, max_w, max_h);
    if (!layout) return (float)index * (float)char_width();
    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    BOOL trailing = FALSE;
    BOOL inside = FALSE;
    DWRITE_HIT_TEST_METRICS metrics{};
    float x = 0.0f, y = 0.0f;
    layout->HitTestTextPosition((UINT32)index, FALSE, &x, &y, &metrics);
    layout->Release();
    return x;
}

int Omnibox::text_index_from_x(float local_x) const {
    if (value.empty()) return 0;
    float max_w = text_width();
    float max_h = (float)bounds.h;
    if (!g_dwrite_factory) {
        return (std::max)(0, (std::min)((int)value.size(), (int)std::lround(local_x / (float)char_width())));
    }
    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = g_dwrite_factory->CreateTextFormat(
        style.font_name.c_str(), nullptr, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL,
        DWRITE_FONT_STRETCH_NORMAL, style.font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) {
        return (std::max)(0, (std::min)((int)value.size(), (int)std::lround(local_x / (float)char_width())));
    }
    IDWriteTextLayout* layout = nullptr;
    hr = g_dwrite_factory->CreateTextLayout(value.c_str(), (UINT32)value.size(), fmt, max_w, max_h, &layout);
    fmt->Release();
    if (FAILED(hr) || !layout) {
        return (std::max)(0, (std::min)((int)value.size(), (int)std::lround(local_x / (float)char_width())));
    }
    apply_emoji_font_fallback(layout, value);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    BOOL trailing = FALSE;
    BOOL inside = FALSE;
    DWRITE_HIT_TEST_METRICS metrics{};
    layout->HitTestPoint(local_x, max_h * 0.5f, &trailing, &inside, &metrics);
    int idx = (int)metrics.textPosition + (trailing ? 1 : 0);
    layout->Release();
    return (std::max)(0, (std::min)((int)value.size(), idx));
}

std::wstring Omnibox::security_icon() const {
    switch (security_state) {
    case 1: return L"\U0001F512";
    case 2: return L"\u26A0\uFE0F";
    case 3: return L"\u26A0\uFE0F";
    case 4: return L"\U0001F4C4";
    case 5: return L"\U0001F50D";
    default: return L"\U0001F310";
    }
}

void Omnibox::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    ctx.push_clip({0, 0, (float)bounds.w, (float)bounds.h});

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = has_focus ? t->chrome_omnibox_focus_bg : t->chrome_omnibox_bg;
    Color border = has_focus ? t->chrome_omnibox_focus_border : t->chrome_omnibox_border;
    D2D1_RECT_F r = {0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f};
    float radius = bounds.h * 0.5f;
    ctx.rt->FillRoundedRectangle(ROUNDED(r, radius, radius), ctx.get_brush(bg));
    if ((border >> 24) != 0) {
        ctx.rt->DrawRoundedRectangle(ROUNDED(r, radius, radius), ctx.get_brush(border), 1.0f);
    }

    float x = 12.0f;
    ElementStyle icon_style = style;
    icon_style.font_size = style.font_size + 1.0f;
    draw_text(ctx, security_icon(), icon_style, t->chrome_omnibox_placeholder, x, 0, 24, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_CENTER);
    x += 28.0f;

    if (!chip_text.empty() || !chip_icon.empty()) {
        std::wstring chip = chip_icon.empty() ? chip_text : (chip_icon + L" " + chip_text);
        float cw = (std::max)(42.0f, 18.0f + (float)chip.size() * style.font_size * 0.5f);
        D2D1_RECT_F cr = {x, 5.0f, x + cw, (float)bounds.h - 5.0f};
        ctx.rt->FillRoundedRectangle(ROUNDED(cr, 10.0f, 10.0f),
            ctx.get_brush(chip_bg ? chip_bg : t->chrome_omnibox_chip_bg));
        draw_text(ctx, chip, style, chip_fg ? chip_fg : t->chrome_omnibox_chip_fg,
                  cr.left + 9.0f, cr.top, cw - 18.0f, cr.bottom - cr.top);
        x += cw + 8.0f;
    } else if (!security_label.empty()) {
        draw_text(ctx, security_label, style, t->chrome_omnibox_placeholder, x, 0, 84.0f, (float)bounds.h);
        x += 88.0f;
    }

    float action_w = (float)action_icons.size() * 30.0f;
    float text_w = (float)bounds.w - x - action_w - 12.0f;
    if (text_w < 1.0f) text_w = 1.0f;
    bool showing_placeholder = value.empty();
    if (!showing_placeholder && has_selection()) {
        int s = sel_start, e = sel_end;
        if (s > e) std::swap(s, e);
        s = (std::max)(0, (std::min)((int)value.size(), s));
        e = (std::max)(0, (std::min)((int)value.size(), e));
        if (e > s) {
            auto* layout = ctx.create_text_layout(value, style.font_name, style.font_size, text_w, (float)bounds.h);
            if (layout) {
                apply_emoji_font_fallback(layout, value);
                layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
                DWRITE_HIT_TEST_METRICS metrics[8]{};
                UINT32 actual_count = 0;
                layout->HitTestTextRange((UINT32)s, (UINT32)(e - s), 0, 0, metrics, 8, &actual_count);
                for (UINT32 i = 0; i < actual_count; ++i) {
                    D2D1_RECT_F sr = {
                        x + metrics[i].left,
                        metrics[i].top + 6.0f,
                        x + metrics[i].left + metrics[i].width,
                        metrics[i].top + (float)bounds.h - 6.0f
                    };
                    ctx.rt->FillRectangle(sr, ctx.get_brush(0x663B82F6));
                }
                layout->Release();
            }
        }
    }
    draw_text(ctx, showing_placeholder ? placeholder : value, style,
              showing_placeholder ? t->chrome_omnibox_placeholder : t->chrome_omnibox_fg,
              x, 0, text_w, (float)bounds.h);

    if (has_focus && !has_selection()) {
        int cx = (int)std::lround(x + text_x_for_index(ctx, value, cursor_pos, text_w, (float)bounds.h));
        ctx.rt->DrawLine(D2D1::Point2F((float)cx, 9.0f),
                         D2D1::Point2F((float)cx, (float)bounds.h - 9.0f),
                         ctx.get_brush(t->chrome_omnibox_fg), 1.0f);
    }

    float ax = (float)bounds.w - action_w - 8.0f;
    for (size_t i = 0; i < action_icons.size(); ++i) {
        D2D1_RECT_F ar = {ax + (float)i * 30.0f, 4.0f, ax + (float)i * 30.0f + 26.0f, (float)bounds.h - 4.0f};
        if ((int)i == hovered_action) {
            ctx.rt->FillRoundedRectangle(ROUNDED(ar, 13.0f, 13.0f), ctx.get_brush(t->chrome_icon_button_hover_bg));
        }
        draw_text(ctx, action_icons[i].icon, icon_style, t->chrome_icon_button_fg,
                  ar.left, ar.top, ar.right - ar.left, ar.bottom - ar.top, DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Omnibox::paint_overlay(RenderContext& ctx) {
    if (!visible || !suggestions_open || suggestions.empty()) return;
    Rect pr = suggestion_popup_rect();
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)pr.x, (float)pr.y));
    const Theme* t = theme_for_window(owner_hwnd);
    D2D1_RECT_F box = {0, 0, (float)pr.w, (float)pr.h};
    ctx.rt->FillRoundedRectangle(ROUNDED(box, 12.0f, 12.0f), ctx.get_brush(t->chrome_menu_bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(box, 12.0f, 12.0f), ctx.get_brush(t->chrome_popover_border), 1.0f);
    int row_h = 36;
    for (int i = 0; i < (int)suggestions.size(); ++i) {
        float y = (float)(8 + i * row_h);
        if (i == selected_suggestion) {
            D2D1_RECT_F rr = {8.0f, y, (float)pr.w - 8.0f, y + (float)row_h};
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 8.0f, 8.0f), ctx.get_brush(t->chrome_menu_hover_bg));
        }
        const auto& s = suggestions[i];
        draw_text(ctx, s.icon.empty() ? L"\U0001F50D" : s.icon, style, t->chrome_menu_secondary_fg,
                  18.0f, y, 24.0f, (float)row_h, DWRITE_TEXT_ALIGNMENT_CENTER);
        draw_text(ctx, s.primary, style, t->chrome_menu_fg, 50.0f, y, (float)pr.w * 0.52f, (float)row_h);
        draw_text(ctx, s.secondary, style, t->chrome_menu_secondary_fg,
                  (float)pr.w * 0.58f, y, (float)pr.w * 0.36f, (float)row_h);
    }
    ctx.rt->SetTransform(saved);
}

Element* Omnibox::hit_test_overlay(int x, int y) {
    if (!visible || !suggestions_open || suggestions.empty()) return nullptr;
    Rect pr = suggestion_popup_rect();
    if (x >= pr.x && x < pr.x + pr.w && y >= pr.y && y < pr.y + pr.h) return this;
    return nullptr;
}

int Omnibox::action_at(int x, int y) const {
    if (y < 0 || y >= bounds.h) return -1;
    float action_w = (float)action_icons.size() * 30.0f;
    float ax = (float)bounds.w - action_w - 8.0f;
    for (int i = 0; i < (int)action_icons.size(); ++i) {
        if ((float)x >= ax + i * 30.0f && (float)x < ax + i * 30.0f + 28.0f) return i;
    }
    return -1;
}

int Omnibox::suggestion_at(int x, int y) const {
    int ox = 0, oy = 0;
    get_absolute_pos(ox, oy);
    Rect pr = suggestion_popup_rect();
    int local_y = y + oy - pr.y - 8;
    if (local_y < 0) return -1;
    int idx = local_y / 36;
    return idx >= 0 && idx < (int)suggestions.size() ? idx : -1;
}

Rect Omnibox::suggestion_popup_rect() const {
    int ox = 0, oy = 0;
    get_absolute_pos(ox, oy);
    int rows = (std::min)(8, (int)suggestions.size());
    return {ox, oy + bounds.h + 6, bounds.w, 16 + rows * 36};
}

void Omnibox::delete_selection() {
    if (!has_selection()) return;
    int s = sel_start, e = sel_end;
    if (s > e) std::swap(s, e);
    s = (std::max)(0, (std::min)((int)value.size(), s));
    e = (std::max)(0, (std::min)((int)value.size(), e));
    if (e <= s) { clear_selection(); return; }
    value.erase(s, e - s);
    cursor_pos = s;
    clear_selection();
}

void Omnibox::insert_text(const std::wstring& text) {
    if (text.empty()) return;
    delete_selection();
    cursor_pos = (std::max)(0, (std::min)((int)value.size(), cursor_pos));
    value.insert(cursor_pos, text);
    cursor_pos += (int)text.size();
    clear_selection();
}

void Omnibox::copy_selection_to_clipboard() const {
    if (!has_selection() || !owner_hwnd) return;
    int s = sel_start, e = sel_end;
    if (s > e) std::swap(s, e);
    s = (std::max)(0, (std::min)((int)value.size(), s));
    e = (std::max)(0, (std::min)((int)value.size(), e));
    if (e <= s) return;
    std::wstring selected = value.substr(s, e - s);
    if (!OpenClipboard(owner_hwnd)) return;
    EmptyClipboard();
    size_t bytes = (selected.size() + 1) * sizeof(wchar_t);
    HGLOBAL hmem = GlobalAlloc(GMEM_MOVEABLE, bytes);
    if (hmem) {
        void* ptr = GlobalLock(hmem);
        if (ptr) {
            memcpy(ptr, selected.c_str(), bytes);
            GlobalUnlock(hmem);
            SetClipboardData(CF_UNICODETEXT, hmem);
        } else {
            GlobalFree(hmem);
        }
    }
    CloseClipboard();
}

void Omnibox::cut_selection_to_clipboard() {
    if (!has_selection()) return;
    copy_selection_to_clipboard();
    delete_selection();
    invalidate();
}

void Omnibox::paste_from_clipboard() {
    if (!owner_hwnd || !IsClipboardFormatAvailable(CF_UNICODETEXT)) return;
    if (!OpenClipboard(owner_hwnd)) return;
    HANDLE hdata = GetClipboardData(CF_UNICODETEXT);
    if (hdata) {
        wchar_t* text = (wchar_t*)GlobalLock(hdata);
        if (text) {
            std::wstring paste = text;
            paste.erase(std::remove(paste.begin(), paste.end(), L'\r'), paste.end());
            std::replace(paste.begin(), paste.end(), L'\n', L' ');
            insert_text(paste);
            GlobalUnlock(hdata);
        }
    }
    CloseClipboard();
    invalidate();
}

void Omnibox::show_context_menu() {
    if (!owner_hwnd) return;
    HMENU menu = CreatePopupMenu();
    if (!menu) return;
    bool can_select = !value.empty();
    bool can_clip = has_selection();
    bool can_paste = IsClipboardFormatAvailable(CF_UNICODETEXT) != 0;
    AppendMenuW(menu, MF_STRING | (can_clip ? MF_ENABLED : MF_GRAYED), 1, L"复制");
    AppendMenuW(menu, MF_STRING | (can_clip ? MF_ENABLED : MF_GRAYED), 2, L"剪切");
    AppendMenuW(menu, MF_STRING | (can_paste ? MF_ENABLED : MF_GRAYED), 3, L"粘贴");
    AppendMenuW(menu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(menu, MF_STRING | (can_select ? MF_ENABLED : MF_GRAYED), 4, L"全选");
    POINT pt{};
    GetCursorPos(&pt);
    int cmd = TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON, pt.x, pt.y, 0, owner_hwnd, nullptr);
    DestroyMenu(menu);
    switch (cmd) {
    case 1: copy_selection_to_clipboard(); break;
    case 2: cut_selection_to_clipboard(); break;
    case 3: paste_from_clipboard(); break;
    case 4: select_all(); invalidate(); break;
    default: break;
    }
}

void Omnibox::on_mouse_down(int x, int y, MouseButton btn) {
    if (btn != MouseButton::Left) return;
    pressed_action = action_at(x, y);
    if (pressed_action < 0) {
        cursor_pos = text_index_from_x((float)x - text_start_x());
        clear_selection();
    }
    selecting_suggestion = suggestions_open && suggestion_at(x, y) >= 0;
    pressed = true;
    invalidate();
}

void Omnibox::on_mouse_up(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Right) {
        cursor_pos = text_index_from_x((float)x - text_start_x());
        show_context_menu();
        invalidate();
        return;
    }
    int action = action_at(x, y);
    if (pressed_action >= 0 && pressed_action == action && icon_cb) {
        icon_cb(id, action, 0, 0);
    } else if (selecting_suggestion) {
        int idx = suggestion_at(x, y);
        if (idx >= 0) {
            selected_suggestion = idx;
            value = suggestions[idx].completion.empty() ? suggestions[idx].primary : suggestions[idx].completion;
            cursor_pos = (int)value.size();
            commit();
        }
    }
    pressed_action = -1;
    selecting_suggestion = false;
    pressed = false;
    invalidate();
}

void Omnibox::on_key_down(int vk, int mods) {
    bool ctrl = (mods & KeyMod::Control) != 0;
    bool shift = (mods & KeyMod::Shift) != 0;
    if (ctrl && vk == 'A') {
        select_all();
    } else if (ctrl && vk == 'C') {
        copy_selection_to_clipboard();
    } else if (ctrl && vk == 'X') {
        cut_selection_to_clipboard();
    } else if (ctrl && vk == 'V') {
        paste_from_clipboard();
    } else if (vk == VK_LEFT) {
        if (shift && sel_start < 0) sel_start = cursor_pos;
        if (!shift) clear_selection();
        if (cursor_pos > 0) --cursor_pos;
        if (shift) sel_end = cursor_pos;
    } else if (vk == VK_RIGHT) {
        if (shift && sel_start < 0) sel_start = cursor_pos;
        if (!shift) clear_selection();
        if (cursor_pos < (int)value.size()) ++cursor_pos;
        if (shift) sel_end = cursor_pos;
    } else if (vk == VK_HOME) {
        if (shift && sel_start < 0) sel_start = cursor_pos;
        if (!shift) clear_selection();
        cursor_pos = 0;
        if (shift) sel_end = cursor_pos;
    } else if (vk == VK_END) {
        if (shift && sel_start < 0) sel_start = cursor_pos;
        if (!shift) clear_selection();
        cursor_pos = (int)value.size();
        if (shift) sel_end = cursor_pos;
    } else if (vk == VK_BACK) {
        if (has_selection()) {
            delete_selection();
        } else if (cursor_pos > 0) {
            value.erase(cursor_pos - 1, 1);
            --cursor_pos;
        }
    } else if (vk == VK_DELETE) {
        if (has_selection()) {
            delete_selection();
        } else if (cursor_pos < (int)value.size()) {
            value.erase(cursor_pos, 1);
        }
    } else if (vk == VK_DOWN) {
        if (!suggestions.empty()) {
            suggestions_open = true;
            selected_suggestion = (selected_suggestion + 1) % (int)suggestions.size();
        }
    } else if (vk == VK_UP) {
        if (!suggestions.empty()) {
            suggestions_open = true;
            selected_suggestion = selected_suggestion <= 0 ? (int)suggestions.size() - 1 : selected_suggestion - 1;
        }
    } else if (vk == VK_RETURN) {
        if (suggestions_open && selected_suggestion >= 0 && selected_suggestion < (int)suggestions.size()) {
            value = suggestions[selected_suggestion].completion.empty()
                ? suggestions[selected_suggestion].primary : suggestions[selected_suggestion].completion;
            cursor_pos = (int)value.size();
        }
        commit();
    } else if (vk == VK_ESCAPE) {
        suggestions_open = false;
    }
    invalidate();
}

void Omnibox::on_char(wchar_t ch) {
    if (ch < 32) return;
    if (cursor_pos < 0) cursor_pos = 0;
    if (cursor_pos > (int)value.size()) cursor_pos = (int)value.size();
    insert_text(std::wstring(1, ch));
    invalidate();
}

void Omnibox::on_focus() { has_focus = true; cursor_pos = (int)value.size(); invalidate(); }
void Omnibox::on_blur() { has_focus = false; pressed = false; pressed_action = -1; clear_selection(); invalidate(); }

void Omnibox::set_value(const std::wstring& next) { value = next; cursor_pos = (int)value.size(); clear_selection(); invalidate(); }
void Omnibox::set_placeholder(const std::wstring& next) { placeholder = next; invalidate(); }
void Omnibox::set_security_state(int state, const std::wstring& label) {
    security_state = (std::max)(0, (std::min)(5, state));
    security_label = label;
    invalidate();
}
void Omnibox::set_prefix_chip(const std::wstring& icon, const std::wstring& text, Color bg, Color fg) {
    chip_icon = icon; chip_text = text; chip_bg = bg; chip_fg = fg; invalidate();
}
void Omnibox::set_action_icons(const std::vector<OmniboxActionIcon>& icons) {
    action_icons = icons; invalidate();
}
void Omnibox::set_suggestions(const std::vector<OmniboxSuggestion>& items) {
    suggestions = items;
    if (selected_suggestion >= (int)suggestions.size()) selected_suggestion = -1;
    invalidate();
}
void Omnibox::set_suggestion_open(bool open) {
    suggestions_open = open;
    if (open && selected_suggestion < 0 && !suggestions.empty()) selected_suggestion = 0;
    invalidate();
}
void Omnibox::set_selected_suggestion(int index) {
    selected_suggestion = (index >= 0 && index < (int)suggestions.size()) ? index : -1;
    invalidate();
}
void Omnibox::commit() {
    suggestions_open = false;
    if (commit_cb) {
        std::string u8 = wide_to_utf8(value);
        commit_cb(id, reinterpret_cast<const unsigned char*>(u8.data()), (int)u8.size());
    }
}
