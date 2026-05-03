#pragma once
#include "element_base.h"

class Popover : public Element {
public:
    std::wstring title;
    std::wstring content;
    int placement = 3; // 0 left, 1 right, 2 top, 3 bottom
    int popup_width = 250;
    int popup_height = 132;
    bool close_enabled = true;
    int open_count = 0;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 focus, 5 trigger
    int focus_part = 0; // 0 trigger, 1 popup body, 2 close button
    ElementValueCallback action_cb = nullptr;

    const wchar_t* type_name() const override { return L"Popover"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_focus() override;
    void on_blur() override;

    void set_title(const std::wstring& value);
    void set_content(const std::wstring& value);
    void set_placement(int value);
    void set_open(bool value);
    void set_options(int new_placement, int is_open, int width, int height, int closable);
    void trigger_open(bool value, int action);
    bool is_open() const { return open; }
    bool close_hot() const { return close_hover; }
    Rect get_popup_rect() const { return popup_rect; }
    Rect get_close_rect() const { return close_rect; }

protected:
    bool open = false;
    bool trigger_pressed = false;
    bool popup_pressed = false;
    bool close_hover = false;
    Rect popup_rect;
    Rect close_rect;

    virtual bool has_close_button() const { return close_enabled; }
    virtual void update_popup_rect();
    virtual void draw_popup_content(RenderContext& ctx, const Rect& content_rect);
    float scale() const;
    bool in_trigger(int x, int y) const;
    bool in_popup(int x, int y) const;
    bool in_close(int x, int y) const;
    void draw_trigger(RenderContext& ctx);
    void draw_popup(RenderContext& ctx);
    void apply_open(bool value, int action);
    void notify_action(int action);
};
