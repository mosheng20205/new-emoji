#pragma once
#include "element_base.h"

class Tooltip : public Element {
public:
    std::wstring content;
    int placement = 2; // 0 left, 1 right, 2 top, 3 bottom
    int advanced_placement = 1; // 0 top-start, 1 top, 2 top-end, 3 bottom-start, 4 bottom, 5 bottom-end, 6 left-start, 7 left, 8 left-end, 9 right-start, 10 right, 11 right-end
    bool use_advanced_placement = false;
    int effect = 0; // 0 dark, 1 light
    bool tooltip_disabled = false;
    int offset = 8;
    bool show_arrow = true;
    int show_delay_ms = 220;
    int hide_delay_ms = 120;
    int trigger_mode = 0; // 0 hover+focus, 1 hover, 2 focus, 3 manual
    int open_count = 0;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 focus, 4 keyboard, 5 trigger, 6 timer

    ~Tooltip() override;

    const wchar_t* type_name() const override { return L"Tooltip"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_focus() override;
    void on_blur() override;

    void set_content(const std::wstring& value);
    void set_placement(int value);
    void set_open(bool value);
    void set_options(int new_placement, int open, int max_width);
    void set_behavior(int show_delay, int hide_delay, int trigger, int arrow);
    void set_advanced_options(int new_placement, int new_effect, int disabled,
                              int arrow, int new_offset, int max_width);
    void trigger_open(bool open, int action);
    void tick(int elapsed_ms);
    bool is_open() const { return m_open; }
    int max_width() const { return m_max_width; }
    int timer_phase() const { return m_timer_phase; }
    bool timer_running() const { return m_timer_id != 0; }
    Rect popup_rect() const { return m_popup_rect; }

private:
    bool m_open = false;
    bool m_forced_open = false;
    int m_max_width = 280;
    Rect m_popup_rect;
    UINT_PTR m_timer_id = 0;
    int m_timer_elapsed = 0;
    int m_timer_phase = 0; // 0 none, 1 show, 2 hide
    int m_pending_action = 0;

    float scale() const;
    void update_popup_rect();
    void draw_trigger(RenderContext& ctx);
    void draw_popup(RenderContext& ctx);
    void draw_arrow(RenderContext& ctx, Color bg);
    void schedule_open(int action);
    void schedule_close(int action);
    void apply_open(bool open, int action);
    void ensure_timer(int phase, int action);
    void stop_timer();
    bool hover_enabled() const;
    bool focus_enabled() const;
};
