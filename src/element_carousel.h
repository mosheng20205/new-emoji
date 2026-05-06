#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <vector>

struct Theme;

class Carousel : public Element {
public:
    std::vector<std::wstring> items;
    int active_index = 0;
    int previous_index = 0;
    int indicator_position = 0; // 0 inside, 1 outside
    bool loop = true;
    bool show_arrows = true;
    bool show_indicators = true;
    int trigger_mode = 1; // 0 hover, 1 click
    int arrow_mode = 1; // 0 hover, 1 always, 2 never
    int direction = 0; // 0 horizontal, 1 vertical
    int carousel_type = 0; // 0 normal, 1 card
    bool pause_on_hover = false;
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
    Color text_color = 0;
    int text_alpha = 255;
    int text_font_size = 0;
    Color odd_bg = 0;
    Color even_bg = 0;
    Color panel_bg = 0;
    Color active_indicator = 0;
    Color inactive_indicator = 0;
    int card_scale_percent = 82;

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
    void set_behavior(int trigger, int arrows, int dir, int type, int pause);
    void set_visual(Color text, int alpha, int font_size, Color odd, Color even,
                    Color panel, Color active_dot, Color inactive_dot, int card_scale);
    void set_autoplay(int enabled, int interval);
    void set_animation(int duration_ms);
    void advance(int delta);
    void tick(int elapsed_ms);

private:
    enum Part {
        PartNone,
        PartPrev,
        PartNext,
        PartIndicator,
        PartCardItem
    };

    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_hover_index = -1;
    int m_press_index = -1;
    UINT_PTR m_timer_id = 0;

    Rect prev_rect() const;
    Rect next_rect() const;
    Rect indicator_rect(int index) const;
    Rect item_rect(int index) const;
    int neighbor_index(int delta) const;
    bool arrows_visible() const;
    Color item_bg_color(int index, const Theme* t, bool dark) const;
    Color text_color_value(const Theme* t) const;
    Part part_at(int x, int y, int* index = nullptr) const;
    void set_active_index_with_action(int index, int action, int direction_hint);
    void start_transition(int old_index, int new_index, int action, int direction_hint);
    void paint_normal(RenderContext& ctx, const Theme* t, bool dark,
                      const D2D1_RECT_F& hero, const ElementStyle& text_style, Color fg);
    void paint_card(RenderContext& ctx, const Theme* t, bool dark,
                    const D2D1_RECT_F& hero, const ElementStyle& text_style, Color fg);
    void ensure_timer();
    void stop_timer_if_idle();
    static void CALLBACK carousel_timer(HWND hwnd, UINT msg, UINT_PTR id, DWORD time);
};
