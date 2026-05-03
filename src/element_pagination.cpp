#include "element_pagination.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) { return (int)std::lround(v); }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
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

void Pagination::set_total(int value) {
    total = value < 0 ? 0 : value;
    update_current_page(current_page, 1);
}

void Pagination::set_page_size(int value) {
    page_size = value < 1 ? 1 : value;
    ++size_change_count;
    update_current_page(current_page, 4);
}

void Pagination::set_current_page(int value) {
    update_current_page(value, 1);
}

void Pagination::set_options(int show_jump, int show_size, int visible_count) {
    show_jumper = show_jump != 0;
    show_size_changer = show_size != 0;
    if (visible_count < 5) visible_count = 5;
    if (visible_count > 11) visible_count = 11;
    if ((visible_count % 2) == 0) ++visible_count;
    visible_page_count = visible_count;
    last_action = 1;
    invalidate();
}

void Pagination::set_page_size_options(const std::vector<int>& values) {
    page_size_options.clear();
    for (int v : values) {
        if (v > 0 && std::find(page_size_options.begin(), page_size_options.end(), v) == page_size_options.end()) {
            page_size_options.push_back(v);
        }
    }
    if (page_size_options.empty()) page_size_options = { 10, 20, 50, 100 };
    if (std::find(page_size_options.begin(), page_size_options.end(), page_size) == page_size_options.end()) {
        page_size = page_size_options.front();
    }
    update_current_page(current_page, 1);
}

void Pagination::set_jump_page(int value) {
    jump_page = value;
    clamp_jump_page();
    last_action = 1;
    invalidate();
}

void Pagination::trigger_jump(int action) {
    clamp_jump_page();
    ++jump_count;
    update_current_page(jump_page, action);
}

void Pagination::next_page_size() {
    if (page_size_options.empty()) page_size_options = { 10, 20, 50, 100 };
    auto it = std::find(page_size_options.begin(), page_size_options.end(), page_size);
    if (it == page_size_options.end() || ++it == page_size_options.end()) it = page_size_options.begin();
    set_page_size(*it);
}

int Pagination::page_count() const {
    if (page_size <= 0) return 1;
    int count = (total + page_size - 1) / page_size;
    return count < 1 ? 1 : count;
}

void Pagination::clamp_jump_page() {
    int count = page_count();
    if (jump_page < 1) jump_page = 1;
    if (jump_page > count) jump_page = count;
}

void Pagination::update_current_page(int value, int action) {
    int count = page_count();
    if (value < 1) value = 1;
    if (value > count) value = count;
    current_page = value;
    jump_page = current_page;
    ++change_count;
    last_action = action;
    if (change_cb) change_cb(id, current_page, page_size, last_action);
    invalidate();
}

std::vector<int> Pagination::visible_pages() const {
    int count = page_count();
    int visible = visible_page_count;
    if (visible < 5) visible = 5;
    if (count <= visible) {
        std::vector<int> pages;
        for (int i = 1; i <= count; ++i) pages.push_back(i);
        return pages;
    }
    int middle = visible - 2;
    int start = current_page - middle / 2;
    int end = current_page + middle / 2;
    if (start < 2) {
        start = 2;
        end = start + middle - 1;
    }
    if (end > count - 1) {
        end = count - 1;
        start = end - middle + 1;
        if (start < 2) start = 2;
    }
    std::vector<int> pages = { 1 };
    if (start > 2) pages.push_back(0);
    for (int i = start; i <= end; ++i) pages.push_back(i);
    if (end < count - 1) pages.push_back(0);
    pages.push_back(count);
    return pages;
}

int Pagination::part_count() const {
    int count = 1 + (int)visible_pages().size() + 1;
    if (show_size_changer) ++count;
    if (show_jumper) count += 4;
    return count;
}

int Pagination::width_for_part(int part) const {
    int size = round_px(style.font_size * 2.15f);
    if (size < 28) size = 28;
    int pages_end = 1 + (int)visible_pages().size();
    int size_part = pages_end + 2;
    if (show_size_changer && part == size_part) return round_px(86.0f * style.font_size / 14.0f);
    int jump_start = size_part + (show_size_changer ? 1 : 0);
    if (show_jumper && part == jump_start + 1) return round_px(58.0f * style.font_size / 14.0f);
    if (show_jumper && part == jump_start + 3) return round_px(54.0f * style.font_size / 14.0f);
    return size;
}

Rect Pagination::part_rect(int part) const {
    int size = round_px(style.font_size * 2.15f);
    if (size < 28) size = 28;
    int gap = round_px(6.0f * style.font_size / 14.0f);
    int y = (bounds.h - size) / 2;
    int x = style.pad_left;
    for (int p = 1; p < part; ++p) x += width_for_part(p) + gap;
    return { x, y, width_for_part(part), size };
}

int Pagination::part_at(int x, int y) const {
    for (int i = 1; i <= part_count(); ++i) {
        if (part_rect(i).contains(x, y)) return i;
    }
    return 0;
}

int Pagination::page_for_part(int part) const {
    auto pages = visible_pages();
    if (part <= 1 || part > 1 + (int)pages.size()) return 0;
    return pages[part - 2];
}

void Pagination::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color active = t->accent;
    int count = page_count();
    auto pages = visible_pages();
    int pages_end = 1 + (int)pages.size();
    int next_part = pages_end + 1;
    int size_part = next_part + 1;
    int jump_start = size_part + (show_size_changer ? 1 : 0);

    ctx.push_clip({ 0, 0, (float)bounds.w, (float)bounds.h });
    for (int part = 1; part <= part_count(); ++part) {
        Rect r = part_rect(part);
        if (r.x + r.w > bounds.w - style.pad_right) break;
        bool disabled = false;
        bool is_active = false;
        std::wstring label;
        if (part == 1) {
            label = L"<";
            disabled = current_page <= 1;
        } else if (part == next_part) {
            label = L">";
            disabled = current_page >= count;
        } else if (part <= pages_end) {
            int page = page_for_part(part);
            disabled = page == 0;
            is_active = page == current_page;
            label = page == 0 ? L"..." : std::to_wstring(page);
        } else if (show_size_changer && part == size_part) {
            label = std::to_wstring(page_size) + L"条/页";
        } else if (show_jumper && part == jump_start) {
            label = L"-";
        } else if (show_jumper && part == jump_start + 1) {
            label = std::to_wstring(jump_page);
        } else if (show_jumper && part == jump_start + 2) {
            label = L"+";
        } else if (show_jumper && part == jump_start + 3) {
            label = L"跳转";
        }

        bool hot = part == m_hover_part && !disabled;
        D2D1_RECT_F rr = { (float)r.x, (float)r.y, (float)(r.x + r.w), (float)(r.y + r.h) };
        Color bg = is_active ? active : (hot ? t->button_hover : 0);
        Color text_color = disabled ? t->text_muted : (is_active ? 0xFFFFFFFF : fg);
        if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rr.left + 0.5f, rr.top + 0.5f,
            rr.right - 0.5f, rr.bottom - 0.5f), 4.0f, 4.0f),
            ctx.get_brush(is_active ? active : border), 1.0f);
        draw_text(ctx, label, style, text_color, rr.left, rr.top, (float)r.w, (float)r.h);
    }

    Rect last = part_rect(part_count());
    std::wstring total_text = L"共 " + std::to_wstring(total) + L" 条 / " + std::to_wstring(count) + L" 页";
    draw_text(ctx, total_text, style, fg, (float)(last.x + last.w + 10), 0.0f,
              (float)bounds.w - (float)(last.x + last.w + 10) - style.pad_right, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_LEADING);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Pagination::on_mouse_move(int x, int y) {
    int part = part_at(x, y);
    if (part != m_hover_part) {
        m_hover_part = part;
        invalidate();
    }
}

void Pagination::on_mouse_leave() {
    m_hover_part = 0;
    m_press_part = 0;
    hovered = false;
    invalidate();
}

void Pagination::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y);
    pressed = true;
    invalidate();
}

void Pagination::on_mouse_up(int x, int y, MouseButton) {
    int part = part_at(x, y);
    auto pages = visible_pages();
    int pages_end = 1 + (int)pages.size();
    int next_part = pages_end + 1;
    int size_part = next_part + 1;
    int jump_start = size_part + (show_size_changer ? 1 : 0);
    if (part > 0 && part == m_press_part) {
        if (part == 1) update_current_page(current_page - 1, 2);
        else if (part == next_part) update_current_page(current_page + 1, 2);
        else if (part <= pages_end && page_for_part(part) > 0) update_current_page(page_for_part(part), 2);
        else if (show_size_changer && part == size_part) next_page_size();
        else if (show_jumper && part == jump_start) set_jump_page(jump_page - 1);
        else if (show_jumper && part == jump_start + 2) set_jump_page(jump_page + 1);
        else if (show_jumper && part == jump_start + 3) trigger_jump(5);
    }
    m_press_part = 0;
    pressed = false;
    invalidate();
}

void Pagination::on_key_down(int vk, int) {
    if (vk == VK_LEFT) update_current_page(current_page - 1, 3);
    else if (vk == VK_RIGHT) update_current_page(current_page + 1, 3);
    else if (vk == VK_HOME) update_current_page(1, 3);
    else if (vk == VK_END) update_current_page(page_count(), 3);
    else if (vk == VK_PRIOR) update_current_page(current_page - 5, 3);
    else if (vk == VK_NEXT) update_current_page(current_page + 5, 3);
    else if (vk == VK_RETURN) trigger_jump(5);
    else if (vk == VK_SPACE) next_page_size();
    else if (vk == VK_BACK) set_jump_page(jump_page / 10);
    else if (vk >= '0' && vk <= '9') {
        int digit = vk - '0';
        int next = jump_page * 10 + digit;
        if (next > page_count()) next = digit == 0 ? page_count() : digit;
        set_jump_page(next);
    }
}
