#include "element_titlebar.h"
#include "render_context.h"
#include "theme.h"

static const int kBtnCount = 3;

void TitleBar::get_btn_rect(Btn b, int& x, int& y, int& w, int& h) const {
    w = btn_w(); h = btn_h();
    int idx = (int)b - 1;  // 0=Minimize, 1=Maximize, 2=Close
    x = bounds.w - (kBtnCount - idx) * w;
    y = (bounds.h - h) / 2;
    if (y < 0) y = 0;
}

TitleBar::Btn TitleBar::button_at(int x, int y) const {
    for (int i = 0; i < kBtnCount; i++) {
        Btn b = (Btn)((int)Minimize + i);
        int bx, by, bw, bh;
        get_btn_rect(b, bx, by, bw, bh);
        if (x >= bx && x < bx + bw && y >= by && y < by + bh) return b;
    }
    return None;
}

bool TitleBar::hit_test_button(int x, int y) const {
    return button_at(x, y) != None;
}

// ── Paint ────────────────────────────────────────────────────────────

void TitleBar::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    // Background
    {
        const Theme* t = theme_for_window(owner_hwnd);
        auto* br = ctx.get_brush(bg_color ? bg_color : t->titlebar_bg);
        D2D1_RECT_F bar = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bar, br);
    }

    // Window control buttons (drawn before title text, right-aligned)
    for (int i = 0; i < kBtnCount; i++) {
        Btn b = (Btn)((int)Minimize + i);
        int bx, by, bw, bh;
        get_btn_rect(b, bx, by, bw, bh);
        const Theme* t = theme_for_window(owner_hwnd);
        Color c = text_color ? text_color : t->titlebar_text;
        if (m_press_btn == b && m_hover_btn == b) {
            c = (b == Close) ? 0xFFFFFFFF : 0x80FFFFFF;
            // Subtle background
            D2D1_RECT_F br = { (float)bx, (float)by, (float)(bx + bw), (float)(by + bh) };
            Color bg = (b == Close) ? 0xFFE81123 : 0x40FFFFFF;
            ctx.rt->FillRectangle(br, ctx.get_brush(bg));
        } else if (m_hover_btn == b) {
            c = 0xFFFFFFFF;
            D2D1_RECT_F br = { (float)bx, (float)by, (float)(bx + bw), (float)(by + bh) };
            Color bg = (b == Close) ? 0xFFE81123 : 0x30FFFFFF;
            ctx.rt->FillRectangle(br, ctx.get_brush(bg));
        }
        switch (b) {
        case Minimize: draw_minimize(ctx, bx, by, bw, bh, c); break;
        case Maximize: {
            bool maxed = IsZoomed(owner_hwnd);
            if (maxed) draw_restore(ctx, bx, by, bw, bh, c);
            else       draw_maximize(ctx, bx, by, bw, bh, c);
            break;
        }
        case Close:    draw_close(ctx, bx, by, bw, bh, c); break;
        }
    }

    // Title text (left-aligned with padding)
    wchar_t title[256];
    GetWindowTextW(owner_hwnd, title, 256);
    if (wcslen(title) > 0) {
        const Theme* t = theme_for_window(owner_hwnd);
        float fs = 12.0f * dpi_scale;
        float max_w = (float)bounds.w - (float)(kBtnCount * btn_w()) - 20.0f;
        if (max_w < 20.0f) max_w = 20.0f;
        auto* layout = ctx.create_text_layout(
            title, L"Microsoft YaHei UI", fs, max_w, (float)bounds.h);
        if (layout) {
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            ctx.rt->DrawTextLayout(D2D1::Point2F(12.0f, 0), layout,
                ctx.get_brush(text_color ? text_color : t->titlebar_text),
                D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    ctx.rt->SetTransform(saved);
}

// ── Hit test ─────────────────────────────────────────────────────────

Element* TitleBar::hit_test(int x, int y) {
    if (!visible) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (lx < 0 || ly < 0 || lx >= bounds.w || ly >= bounds.h) return nullptr;

    // Check buttons first
    if (hit_test_button(lx, ly)) return this;  // self handles

    // Check children (none currently, but for future)
    for (auto it = children.rbegin(); it != children.rend(); ++it) {
        Element* hit = (*it)->hit_test(lx, ly);
        if (hit) return hit;
    }
    // Title bar itself is hit
    return parent ? this : nullptr;
}

// ── Mouse ─────────────────────────────────────────────────────────────

void TitleBar::on_mouse_move(int x, int y) {
    Btn old = m_hover_btn;
    m_hover_btn = button_at(x, y);
    if (m_hover_btn != old) invalidate();
}

void TitleBar::on_mouse_down(int x, int y, MouseButton) {
    Btn b = button_at(x, y);
    if (b != None) {
        m_hover_btn = b;
        m_press_btn = b;
        invalidate();
    }
}

void TitleBar::on_mouse_up(int x, int y, MouseButton) {
    Btn release_btn = button_at(x, y);
    Btn clicked = (m_press_btn != None && m_press_btn == release_btn) ? m_press_btn : None;
    HWND hwnd = owner_hwnd;

    m_press_btn = None;
    m_hover_btn = release_btn;
    invalidate();

    if (clicked != None && hwnd) {
        switch (clicked) {
        case Minimize: ShowWindow(hwnd, SW_MINIMIZE); break;
        case Maximize: {
            ShowWindow(hwnd, IsZoomed(hwnd) ? SW_RESTORE : SW_MAXIMIZE);
            break;
        }
        case Close:    PostMessageW(hwnd, WM_CLOSE, 0, 0); break;
        }
    }
}

void TitleBar::on_mouse_leave() {
    m_hover_btn = None;
    m_press_btn = None;
    invalidate();
}

// ── Button icons ─────────────────────────────────────────────────────

void TitleBar::draw_minimize(RenderContext& ctx, int x, int y, int w, int h, Color c) {
    float cx = x + w * 0.5f;
    float cy = y + h * 0.65f;
    float len = (float)(int)(8.0f * dpi_scale);
    ctx.rt->DrawLine(D2D1::Point2F(cx - len, cy), D2D1::Point2F(cx + len, cy),
                     ctx.get_brush(c), 1.5f);
}

void TitleBar::draw_maximize(RenderContext& ctx, int x, int y, int w, int h, Color c) {
    float s = (float)(int)(8.0f * dpi_scale);
    float cx = x + w * 0.5f, cy = y + h * 0.5f;
    D2D1_RECT_F r = { cx - s, cy - s, cx + s, cy + s };
    ctx.rt->DrawRectangle(r, ctx.get_brush(c), 1.5f);
}

void TitleBar::draw_restore(RenderContext& ctx, int x, int y, int w, int h, Color c) {
    float s = (float)(int)(7.0f * dpi_scale);
    float off = (float)(int)(3.0f * dpi_scale);
    float cx = x + w * 0.5f, cy = y + h * 0.5f;
    auto* br = ctx.get_brush(c);

    D2D1_RECT_F back = { cx - s + off, cy - s - off, cx + s + off, cy + s - off };
    D2D1_RECT_F front = { cx - s - off, cy - s + off, cx + s - off, cy + s + off };
    ctx.rt->DrawRectangle(back, br, 1.5f);
    ctx.rt->DrawRectangle(front, br, 1.5f);
}

void TitleBar::draw_close(RenderContext& ctx, int x, int y, int w, int h, Color c) {
    float s = (float)(int)(7.0f * dpi_scale);
    float cx = x + w * 0.5f, cy = y + h * 0.5f;
    auto* br = ctx.get_brush(c);
    ctx.rt->DrawLine(D2D1::Point2F(cx - s, cy - s), D2D1::Point2F(cx + s, cy + s), br, 1.5f);
    ctx.rt->DrawLine(D2D1::Point2F(cx + s, cy - s), D2D1::Point2F(cx - s, cy + s), br, 1.5f);
}
