#pragma once
#include "element_base.h"

class Message : public Element {
public:
    int message_type = 0;
    bool closable = false;
    bool closed = false;
    bool center = false;
    bool rich = false;
    int duration_ms = 3000;
    int timer_elapsed_ms = 0;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger, 5 timer
    int stack_index = 0;
    int stack_gap = 12;
    int offset = 20;
    ElementValueCallback close_cb = nullptr;

    ~Message() override;
    const wchar_t* type_name() const override { return L"Message"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_text(const std::wstring& value);
    void set_options(int type, bool closeable, bool centered, bool rich_text, int duration, int top_offset);
    void set_closed(bool value);
    void set_stack(int index, int gap);
    void close_message(int action);
    void reset_timer();
    void tick(int elapsed_ms);
    bool close_hover() const { return m_close_hover; }
    bool close_down() const { return m_close_down; }
    bool timer_running() const { return m_timer_id != 0; }

private:
    bool m_close_hover = false;
    bool m_close_down = false;
    int m_base_y = 0;
    bool m_has_base_y = false;
    UINT_PTR m_timer_id = 0;

    Rect close_rect() const;
    bool close_hit(int x, int y) const;
    void ensure_timer();
    void stop_timer();
};
