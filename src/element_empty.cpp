#include "element_empty.h"
#include "emoji_fallback.h"
#include "element_image.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

struct EmptyMetrics {
    float media_w = 0.0f;
    float media_h = 0.0f;
    float media_x = 0.0f;
    float media_y = 0.0f;
    float title_y = 0.0f;
};

static EmptyMetrics empty_metrics(const Empty& el, bool has_action) {
    EmptyMetrics m;
    float fallback_w = (std::min)((float)el.bounds.w * 0.36f, el.style.font_size * 5.2f);
    if (fallback_w < 42.0f) fallback_w = 42.0f;

    float max_media_w = (std::max)(24.0f,
        (float)el.bounds.w - (float)el.style.pad_left - (float)el.style.pad_right);
    if (el.image_size > 0) {
        m.media_w = (std::min)((float)el.image_size, max_media_w);
        m.media_h = m.media_w;
    } else {
        m.media_w = (std::min)(fallback_w, max_media_w);
        m.media_h = el.image_source.empty() ? m.media_w * 0.62f : m.media_w;
    }

    float action_h = has_action ? el.style.font_size * 2.15f : 0.0f;
    float total_h = m.media_h + el.style.font_size * 3.2f + action_h;
    float top = ((float)el.bounds.h - total_h) * 0.5f;
    if (top < 4.0f) top = 4.0f;

    m.media_x = ((float)el.bounds.w - m.media_w) * 0.5f;
    m.media_y = top;
    m.title_y = m.media_y + m.media_h + 6.0f;
    return m;
}

static D2D1_RECT_F contain_rect(const D2D1_RECT_F& box, int bitmap_w, int bitmap_h) {
    if (bitmap_w <= 0 || bitmap_h <= 0) return box;
    float bw = (float)bitmap_w;
    float bh = (float)bitmap_h;
    float box_w = box.right - box.left;
    float box_h = box.bottom - box.top;
    float scale = (std::min)(box_w / bw, box_h / bh);
    float w = bw * scale;
    float h = bh * scale;
    float x = box.left + (box_w - w) * 0.5f;
    float y = box.top + (box_h - h) * 0.5f;
    return { x, y, x + w, y + h };
}

Empty::~Empty() {
    release_image_bitmap();
}

void Empty::release_image_bitmap() {
    if (m_image_bitmap) {
        m_image_bitmap->Release();
        m_image_bitmap = nullptr;
    }
    m_image_bitmap_rt = nullptr;
    m_image_bitmap_src.clear();
    m_image_bitmap_w = 0;
    m_image_bitmap_h = 0;
}

bool Empty::ensure_image_bitmap(RenderContext& ctx) {
    if (image_source.empty()) {
        image_status = 0;
        release_image_bitmap();
        return false;
    }
    if (m_image_bitmap && m_image_bitmap_rt == ctx.rt && m_image_bitmap_src == image_source) {
        image_status = 1;
        return true;
    }

    std::wstring decode_path;
    int state = resolve_shared_image_source(owner_hwnd, image_source, decode_path);
    if (state != 1 || decode_path.empty()) {
        image_status = (state == 2) ? 2 : 3;
        return false;
    }

    release_image_bitmap();
    ID2D1Bitmap* loaded = nullptr;
    int bitmap_w = 0;
    int bitmap_h = 0;
    if (load_shared_bitmap_from_path(ctx, decode_path, &loaded, &bitmap_w, &bitmap_h)) {
        m_image_bitmap = loaded;
        m_image_bitmap_rt = ctx.rt;
        m_image_bitmap_src = image_source;
        m_image_bitmap_w = bitmap_w;
        m_image_bitmap_h = bitmap_h;
        image_status = 1;
        return true;
    }

    image_status = 2;
    return false;
}

void Empty::set_description(const std::wstring& value) {
    description = value;
    invalidate();
}

void Empty::set_icon(const std::wstring& value) {
    icon = value.empty() ? L"📭" : value;
    invalidate();
}

void Empty::set_image(const std::wstring& value) {
    image_source = value;
    image_status = image_source.empty() ? 0 : 3;
    release_image_bitmap();
    invalidate();
}

void Empty::set_image_size(int value) {
    logical_image_size = (std::max)(0, value);
    image_size = logical_image_size;
    invalidate();
}

void Empty::set_action(const std::wstring& value) {
    action_text = value;
    action_clicked = false;
    invalidate();
}

void Empty::set_action_clicked(bool value) {
    action_clicked = value;
    invalidate();
}

void Empty::apply_dpi_scale(float scale) {
    Element::apply_dpi_scale(scale);
    image_size = logical_image_size > 0
        ? (int)std::lround((float)logical_image_size * scale)
        : 0;
}

Rect Empty::action_rect() const {
    if (action_text.empty()) return { 0, 0, 0, 0 };
    EmptyMetrics m = empty_metrics(*this, true);
    float btn_w = (std::min)((float)bounds.w - style.pad_left - style.pad_right,
                             (float)action_text.size() * style.font_size + 34.0f);
    if (btn_w < 96.0f) btn_w = 96.0f;
    float btn_h = style.font_size * 2.15f;
    float btn_x = ((float)bounds.w - btn_w) * 0.5f;
    float btn_y = m.title_y + style.font_size * 3.2f;
    return { (int)std::lround(btn_x), (int)std::lround(btn_y),
             (int)std::lround(btn_w), (int)std::lround(btn_h) };
}

bool Empty::action_hit(int x, int y) const {
    Rect r = action_rect();
    return r.w > 0 && r.h > 0 && r.contains(x, y);
}

Element* Empty::hit_test(int x, int y) {
    return Element::hit_test(x, y);
}

void Empty::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color muted = dark ? 0xFF585B70 : 0xFFC0C4CC;
    Color action_bg = style.bg_color ? style.bg_color : t->accent;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    EmptyMetrics m = empty_metrics(*this, !action_text.empty());
    D2D1_RECT_F media_box = { m.media_x, m.media_y, m.media_x + m.media_w, m.media_y + m.media_h };
    if (!image_source.empty() && ensure_image_bitmap(ctx)) {
        D2D1_RECT_F dst = contain_rect(media_box, m_image_bitmap_w, m_image_bitmap_h);
        ctx.rt->DrawBitmap(m_image_bitmap, dst, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
    } else {
        std::wstring shown_icon = icon;
        if (!image_source.empty()) shown_icon = (image_status == 2) ? L"⚠️" : L"🖼️";
        float icon_scale = (std::max)(1.0f, m.media_h / (std::max)(1.0f, style.font_size) * 0.58f);
        draw_text(ctx, shown_icon, style, muted, m.media_x, m.media_y, m.media_w, m.media_h, icon_scale);
    }

    float title_y = m.title_y;
    draw_text(ctx, text.empty() ? L"暂无数据" : text, style, fg,
              0.0f, title_y, (float)bounds.w, style.font_size * 1.7f, 1.0f);
    draw_text(ctx, description, style, t->text_muted,
              (float)style.pad_left, title_y + style.font_size * 1.55f,
              (float)bounds.w - style.pad_left - style.pad_right,
              style.font_size * 1.6f, 0.92f);

    if (!action_text.empty()) {
        float btn_w = (std::min)((float)bounds.w - style.pad_left - style.pad_right,
                                 (float)action_text.size() * style.font_size + 34.0f);
        if (btn_w < 96.0f) btn_w = 96.0f;
        float btn_h = style.font_size * 2.15f;
        float btn_x = ((float)bounds.w - btn_w) * 0.5f;
        float btn_y = title_y + style.font_size * 3.2f;
        D2D1_RECT_F btn = { btn_x, btn_y, btn_x + btn_w, btn_y + btn_h };
        Color btn_bg = m_action_down ? t->button_press : (m_action_hover ? t->button_hover : action_bg);
        ctx.rt->FillRoundedRectangle(ROUNDED(btn, 5.0f, 5.0f), ctx.get_brush(btn_bg));
        if (m_action_hover || m_action_down) {
            ctx.rt->DrawRoundedRectangle(ROUNDED(btn, 5.0f, 5.0f), ctx.get_brush(action_bg), 1.0f);
        }
        draw_text(ctx, action_text, style, 0xFFFFFFFF, btn_x, btn_y, btn_w, btn_h, 0.95f);
    }

    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Empty::on_mouse_move(int x, int y) {
    bool hot = action_hit(x, y);
    if (hot != m_action_hover) {
        m_action_hover = hot;
        invalidate();
    }
}

void Empty::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_action_hover = false;
    m_action_down = false;
    invalidate();
}

void Empty::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_action_down = action_hit(x, y);
    invalidate();
}

void Empty::on_mouse_up(int x, int y, MouseButton) {
    if (m_action_down && action_hit(x, y)) {
        action_clicked = true;
        if (action_cb) action_cb(id);
    }
    pressed = false;
    m_action_down = false;
    invalidate();
}
