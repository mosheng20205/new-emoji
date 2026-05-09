#pragma once
#include "element_base.h"
#include "render_context.h"
#include "theme.h"
#include <map>
#include <functional>

class ElementTree {
public:
    explicit ElementTree(HWND hwnd, float dpi_scale = 1.0f);
    ~ElementTree();

    HWND hwnd() const { return m_hwnd; }
    Element* root() const { return m_root.get(); }
    Element* focused() const { return m_focus; }
    void set_dpi_scale(float s);
    float dpi_scale() const { return m_dpi_scale; }
    int title_bar_height() const;

    // ── Element management ────────────────────────────────────────
    Element* add_child(Element* parent, std::unique_ptr<Element> child);
    void     remove_child(Element* child);
    Element* find_by_id(int id) const;

    // ── Layout & paint ────────────────────────────────────────────
    void layout();
    void paint(RenderContext& ctx);

    // ── Focus & capture ───────────────────────────────────────────
    void set_focus(Element* el);
    void set_capture(Element* el);
    void release_capture();

    // ── Input dispatch ────────────────────────────────────────────
    void dispatch_mouse_move(int x, int y);
    void dispatch_mouse_wheel(int x, int y, int delta);
    void dispatch_lbutton_down(int x, int y);
    void dispatch_lbutton_up(int x, int y);
    void dispatch_rbutton_down(int x, int y);
    void dispatch_rbutton_up(int x, int y);
    void dispatch_key_down(int vk, int mods);
    void dispatch_key_up(int vk, int mods);
    void dispatch_char(wchar_t ch);
    bool has_modal_overlay_at(int x, int y) const;

    // ── Callbacks ─────────────────────────────────────────────────
    ElementClickCallback element_click_cb = nullptr;
    ElementKeyCallback   element_key_cb   = nullptr;

private:
    HWND m_hwnd;
    float m_dpi_scale = 1.0f;
    std::unique_ptr<Element> m_root;
    Element* m_focus   = nullptr;
    Element* m_capture = nullptr;
    Element* m_hover   = nullptr;
    int      m_next_id = 1;

    Element* hit_test_impl(Element* el, int x, int y) const;
    Element* find_by_id_impl(Element* el, int id) const;
    void     remove_from_parent(Element* child);
    bool     dismiss_popups_at(int x, int y);
    bool     dismiss_popups_on_escape();
    bool     toggle_icon_button_popup(Element* button);
    bool     trigger_element_popup(Element* element, int trigger, bool toggle, int x = -1, int y = -1);
    void     close_other_popups(int keep_popup_id);
};
