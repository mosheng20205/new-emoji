#include "element_tree.h"
#include "element_titlebar.h"
#include "element_panel.h"
#include "element_messagebox.h"
#include "element_dialog.h"
#include "element_drawer.h"
#include "element_upload.h"
#include "factory.h"
#include "dpi_context.h"
#include <algorithm>

static void notify_dpi_scale_changed(Element* el, float old_scale, float new_scale) {
    if (!el) return;
    el->on_dpi_scale_changed(old_scale, new_scale);
    for (auto& ch : el->children) {
        notify_dpi_scale_changed(ch.get(), old_scale, new_scale);
    }
}

static Upload* find_open_upload_preview(Element* el) {
    if (!el || !el->visible) return nullptr;
    for (auto it = el->children.rbegin(); it != el->children.rend(); ++it) {
        if (Upload* found = find_open_upload_preview(it->get())) return found;
    }
    auto* upload = dynamic_cast<Upload*>(el);
    return (upload && upload->preview_open) ? upload : nullptr;
}

ElementTree::ElementTree(HWND hwnd, float dpi_scale) : m_hwnd(hwnd), m_dpi_scale(dpi_scale) {
    m_root = std::make_unique<Element>();
    m_root->id = 0;
    m_root->owner_hwnd = hwnd;
    m_root->visible = true;

    // Create title bar as the first child of root (renders via Element pipeline)
    auto tb = std::make_unique<TitleBar>();
    tb->dpi_scale = m_dpi_scale;
    tb->bg_color = 0;
    tb->text_color = 0;
    wchar_t title[256];
    GetWindowTextW(hwnd, title, 256);
    tb->text = title;
    int tb_h = title_bar_height();
    tb->bounds = {0, 0, 800, tb_h};  // width updated in layout()
    tb->parent = m_root.get();
    tb->owner_hwnd = hwnd;
    tb->id = m_next_id++;
    m_root->children.push_back(std::move(tb));
}

ElementTree::~ElementTree() { m_root.reset(); }

void ElementTree::set_dpi_scale(float s) {
    float old = m_dpi_scale;
    m_dpi_scale = s;
    if (!m_root) return;
    m_root->apply_dpi_scale(s);
    notify_dpi_scale_changed(m_root.get(), old, s);
    for (auto& ch : m_root->children) {
        if (auto* tb = dynamic_cast<TitleBar*>(ch.get())) {
            tb->dpi_scale = s;
        }
    }
}

Element* ElementTree::add_child(Element* parent, std::unique_ptr<Element> child) {
    if (!parent) parent = m_root.get();
    child->parent = parent;
    child->owner_hwnd = m_hwnd;
    child->id = m_next_id++;
    child->apply_dpi_scale(m_dpi_scale);
    Element* raw = child.get();
    parent->children.push_back(std::move(child));
    return raw;
}

void ElementTree::remove_child(Element* child) {
    if (!child || !child->parent) return;
    if (m_focus == child) set_focus(nullptr);
    if (m_capture == child) release_capture();
    if (m_hover == child) { child->on_mouse_leave(); m_hover = nullptr; }
    remove_from_parent(child);
}

Element* ElementTree::find_by_id(int id) const { return find_by_id_impl(m_root.get(), id); }

Element* ElementTree::find_by_id_impl(Element* el, int id) const {
    if (!el) return nullptr;
    if (el->id == id) return el;
    for (auto& ch : el->children) {
        Element* found = find_by_id_impl(ch.get(), id);
        if (found) return found;
    }
    return nullptr;
}

void ElementTree::remove_from_parent(Element* child) {
    auto& s = child->parent->children;
    auto it = std::find_if(s.begin(), s.end(), [child](auto& p) { return p.get() == child; });
    if (it != s.end()) s.erase(it);
}

// ── Layout ───────────────────────────────────────────────────────────

void ElementTree::layout() {
    RECT rc;
    GetClientRectForWindowDpi(m_hwnd, &rc);
    int w = rc.right - rc.left, h = rc.bottom - rc.top;
    int tb_h = title_bar_height();

    // Root fills entire client area
    Rect avail = {0, 0, w, h};

    // Update title bar width
    if (!m_root->children.empty()) {
        auto* tb = m_root->children[0].get();
        tb->bounds.w = w;
        tb->bounds.h = tb_h;
        Rect modal_area = {0, 0, w, h};
        // Position regular children below title bar; modal overlays cover the full D2D client area.
        for (size_t i = 1; i < m_root->children.size(); i++) {
            auto& ch = m_root->children[i];
            if (auto* dlg = dynamic_cast<Dialog*>(ch.get())) {
                dlg->layout(modal_area);
                continue;
            }
            if (auto* dr = dynamic_cast<Drawer*>(ch.get())) {
                dr->layout(modal_area);
                continue;
            }
            if (auto* mb = dynamic_cast<MessageBoxElement*>(ch.get())) {
                mb->layout(modal_area);
                continue;
            }
            if (!ch->visible) continue;
            if (auto* p = dynamic_cast<Panel*>(ch.get())) {
                if (p->fill_parent) {
                    Rect panel_area = {0, tb_h, w, h - tb_h};
                    p->layout(panel_area);
                    continue;
                }
            }
            // Ensure child starts at or below title bar, and fits in client area
            if (ch->bounds.y < tb_h) ch->bounds.y = tb_h;
            if (ch->bounds.y + ch->bounds.h > h) ch->bounds.h = h - ch->bounds.y;
            if (ch->bounds.h < 0) ch->bounds.h = 0;
            ch->layout(ch->bounds);
        }
    }
    m_root->bounds = avail;
}

// ── Paint ────────────────────────────────────────────────────────────

void ElementTree::paint(RenderContext& ctx) {
    // Title bar and all elements are now rendered via the Element tree.
    // No separate title bar drawing needed.
    if (!m_root || !m_root->visible || m_root->bounds.w <= 0 || m_root->bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)m_root->bounds.x, (float)m_root->bounds.y));

    D2D1_RECT_F clip = { 0, 0, (float)m_root->bounds.w, (float)m_root->bounds.h };
    ctx.push_clip(clip);

    if (m_root->style.bg_color != 0) {
        D2D1_RECT_F r = { 0, 0, (float)m_root->bounds.w, (float)m_root->bounds.h };
        ctx.rt->FillRectangle(r, ctx.get_brush(m_root->style.bg_color));
    }

    for (auto& ch : m_root->children) {
        if (!ch->visible) continue;
        ch->paint(ctx);
        ch->paint_overlay(ctx);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

// ── Focus ────────────────────────────────────────────────────────────

void ElementTree::set_focus(Element* el) {
    if (m_focus == el) return;
    if (m_focus) m_focus->on_blur();
    m_focus = el;
    if (m_focus) m_focus->on_focus();
}

void ElementTree::set_capture(Element* el) {
    m_capture = el;
    if (el) SetCapture(m_hwnd); else ReleaseCapture();
}

void ElementTree::release_capture() { m_capture = nullptr; ReleaseCapture(); }

// ── Mouse dispatch ───────────────────────────────────────────────────

static void mouse_to_local(const Element* el, int& x, int& y) {
    int ox, oy; el->get_absolute_pos(ox, oy);
    x -= ox; y -= oy;
}

static void dispatch_wheel_fallback(Element* el, int delta) {
    if (!el || !el->visible || !el->enabled) return;
    for (auto it = el->children.rbegin(); it != el->children.rend(); ++it) {
        dispatch_wheel_fallback(it->get(), delta);
    }
    el->on_mouse_wheel(0, 0, delta);
}

void ElementTree::dispatch_mouse_move(int x, int y) {
    if (m_capture) {
        int lx = x, ly = y; mouse_to_local(m_capture, lx, ly);
        m_capture->on_mouse_move(lx, ly);
        return;
    }
    Element* hit = hit_test_impl(m_root.get(), x, y);
    if (hit != m_hover) {
        if (m_hover) m_hover->on_mouse_leave();
        m_hover = hit;
        if (m_hover) m_hover->on_mouse_enter();
    }
    if (m_hover) {
        int lx = x, ly = y; mouse_to_local(m_hover, lx, ly);
        m_hover->on_mouse_move(lx, ly);
    }
}

void ElementTree::dispatch_mouse_wheel(int x, int y, int delta) {
    Element* hit = hit_test_impl(m_root.get(), x, y);
    if (!hit || !hit->enabled) hit = m_hover;
    if (!hit || !hit->enabled) hit = m_focus;
    if (hit && hit->accepts_input()) {
        int lx = x, ly = y;
        mouse_to_local(hit, lx, ly);
        hit->on_mouse_wheel(lx, ly, delta);
    } else {
        dispatch_wheel_fallback(m_root.get(), delta);
    }
}

void ElementTree::dispatch_lbutton_down(int x, int y) {
    if (auto* upload = find_open_upload_preview(m_root.get())) {
        set_focus(upload);
        set_capture(upload);
        int lx = x, ly = y;
        mouse_to_local(upload, lx, ly);
        upload->on_mouse_down(lx, ly, MouseButton::Left);
        return;
    }
    Element* hit = hit_test_impl(m_root.get(), x, y);
    if (hit && hit->enabled) {
        set_focus(hit);
        set_capture(hit);
        int lx = x, ly = y; mouse_to_local(hit, lx, ly);
        hit->on_mouse_down(lx, ly, MouseButton::Left);
    }
}

void ElementTree::dispatch_lbutton_up(int x, int y) {
    Element* captured = m_capture;
    if (!captured) {
        captured = find_open_upload_preview(m_root.get());
        if (!captured) return;
    }

    int lx = x, ly = y;
    mouse_to_local(captured, lx, ly);

    int captured_id = captured->id;
    ElementClickCallback captured_cb = captured->click_cb;
    ElementClickCallback tree_cb = element_click_cb;
    bool should_click = captured->accepts_input();
    HWND hwnd = m_hwnd;

    m_capture = nullptr;
    ReleaseCapture();

    captured->on_mouse_up(lx, ly, MouseButton::Left);
    if (!IsWindow(hwnd)) return;

    if (should_click && captured_cb) captured_cb(captured_id);
    if (!IsWindow(hwnd)) return;
    if (should_click && tree_cb) tree_cb(captured_id);
}

void ElementTree::dispatch_rbutton_down(int x, int y) {
    Element* hit = hit_test_impl(m_root.get(), x, y);
    if (hit && hit->enabled) {
        set_focus(hit);
    }
}

void ElementTree::dispatch_rbutton_up(int x, int y) {
    Element* hit = hit_test_impl(m_root.get(), x, y);
    if (!hit || !hit->enabled) return;
    set_focus(hit);
    int lx = x, ly = y;
    mouse_to_local(hit, lx, ly);
    hit->on_mouse_up(lx, ly, MouseButton::Right);
}

// ── Keyboard ──────────────────────────────────────────────────────────

void ElementTree::dispatch_key_down(int vk, int mods) {
    if (vk == VK_ESCAPE) {
        if (auto* upload = find_open_upload_preview(m_root.get())) {
            set_focus(upload);
            upload->set_preview_open(-1, false);
            return;
        }
    }
    if (m_focus && m_focus->enabled) {
        m_focus->on_key_down(vk, mods);
        if (m_focus->key_cb) m_focus->key_cb(m_focus->id, vk, 1, (mods & KeyMod::Shift) != 0,
                                             (mods & KeyMod::Control) != 0, (mods & KeyMod::Alt) != 0);
    }
}

void ElementTree::dispatch_key_up(int vk, int mods) {
    if (m_focus && m_focus->enabled) {
        m_focus->on_key_up(vk, mods);
        if (m_focus->key_cb) m_focus->key_cb(m_focus->id, vk, 0, (mods & KeyMod::Shift) != 0,
                                             (mods & KeyMod::Control) != 0, (mods & KeyMod::Alt) != 0);
    }
}

void ElementTree::dispatch_char(wchar_t ch) {
    if (m_focus && m_focus->enabled) m_focus->on_char(ch);
}

// ── Hit test ──────────────────────────────────────────────────────────

bool ElementTree::has_modal_overlay_at(int x, int y) const {
    Element* hit = hit_test_impl(m_root.get(), x, y);
    auto* upload = dynamic_cast<Upload*>(hit);
    return dynamic_cast<Dialog*>(hit) != nullptr
        || dynamic_cast<Drawer*>(hit) != nullptr
        || dynamic_cast<MessageBoxElement*>(hit) != nullptr
        || (upload && upload->preview_open);
}

Element* ElementTree::hit_test_impl(Element* el, int x, int y) const {
    if (!el || !el->visible) return nullptr;
    return el->hit_test(x, y);
}
