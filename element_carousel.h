#pragma once
#include "element_base.h"
#include <vector>

class Carousel : public Element {
public:
    std::vector<std::wstring> items;
    int active_index = 0;
    int previous_index = 0;
    int indicator_position = 0; // 0 inside, 1 outside
    bool loop = true;
    bool show_arrows = true;
    bool show_indicators = true;
    bool autoplay = false;
    int interval_ms = 3000;
    int autoplay_tick = 0;
    int autoplay_elapsed_ms = 0;
    int transition_ms = 260;
    int transition_elapsed_ms = 260;
    int transition_progress = 100;
    int transition_direction = 1;
    int last_action = 0; // 0 none, 1 set, 2 prev, 3 next, 4 indicator, 5 keyboard, 6 autoplay
    int change_count = 0;

    ~Carousel() override;

    const wchar_t* type_name() const override { return L"Carousel"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_active_index(int index);
    void set_indicator_position(int value);
    void set_options(int loop_enabled, int indicator_pos, int arrows_visible, int indicators_visible);
    void set_autoplay(int enabled, int interval);
    void set_animation(int duration_ms);
    void advance(int delta);
    void tick(int elapsed_ms);

private:
    enum Part {
        PartNone,
        PartPrev,
        PartNext,
        PartIndicator
    };

    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_hover_index = -1;
    int m_press_index = -1;
    UINT_PTR m_timer_id = 0;

    Rect prev_rect() const;
    Rect next_rect() const;
    Rect indicator_rect(int index) const;
    Part part_at(int x, int y, int* index = nullptr) const;
    void set_active_index_with_action(int index, int action, int direction_hint);
    void start_transition(int old_index, int new_index, int action, int direction_hint);
    void ensure_timer();
    void stop_timer_if_idle();
    static void CALLBACK carousel_timer(HWND hwnd, UINT msg, UINT_PTR id, DWORD time);
};
