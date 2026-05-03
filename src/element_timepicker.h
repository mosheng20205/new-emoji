#pragma once
#include "element_base.h"

class TimePicker : public Element {
public:
    int hour = 9;
    int minute = 30;
    bool open = false;
    int min_time = 0;
    int max_time = 2359;
    int step_minutes = 10;
    int time_format = 0;

    const wchar_t* type_name() const override { return L"TimePicker"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_time(int next_hour, int next_minute);
    void set_range(int min_hhmm, int max_hhmm);
    void set_options(int next_step_minutes, int next_time_format);
    void set_open(bool next_open);
    void set_scroll(int next_hour_scroll, int next_minute_scroll);
    void get_scroll(int& next_hour_scroll, int& next_minute_scroll) const;
    int value() const;
    bool is_open() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartHour,
        PartMinute
    };

    int m_hover_part = PartNone;
    int m_hover_value = -1;
    int m_press_part = PartNone;
    int m_press_value = -1;
    int m_hour_scroll = 0;
    int m_minute_scroll = 0;
    Part m_active_part = PartHour;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int row_height() const;
    int visible_row_count() const;
    int hour_row_count() const;
    int minute_row_count() const;
    void clamp_scroll();
    void ensure_selected_visible();
    void scroll_part(Part part, int rows);
    bool select_step(Part part, int delta);
    bool can_select_time(int next_hour, int next_minute) const;
    Part part_at(int x, int y, int* value = nullptr) const;
    std::wstring display_text() const;
};
