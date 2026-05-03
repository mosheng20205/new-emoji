#pragma once
#include "element_base.h"

class DateTimePicker : public Element {
public:
    int year = 2026;
    int month = 5;
    int day = 1;
    int hour = 9;
    int minute = 30;
    bool open = false;
    int min_date = 0;
    int max_date = 0;
    int min_time = 0;
    int max_time = 2359;
    int today_value = 0;
    bool show_today = true;
    int minute_step = 10;
    int date_format = 0;

    const wchar_t* type_name() const override { return L"DateTimePicker"; }
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

    void set_datetime(int next_year, int next_month, int next_day,
                      int next_hour, int next_minute);
    void set_range(int min_yyyymmdd, int max_yyyymmdd, int min_hhmm, int max_hhmm);
    void set_options(int today_yyyymmdd, bool next_show_today, int next_minute_step, int next_date_format);
    void set_open(bool next_open);
    void clear_datetime();
    void select_today();
    void select_now();
    void set_scroll(int next_hour_scroll, int next_minute_scroll);
    void get_scroll(int& next_hour_scroll, int& next_minute_scroll) const;
    void move_month(int delta);
    int date_value() const;
    int time_value() const;
    bool is_open() const;
    bool can_select_date(int yyyymmdd) const;
    bool can_select_time(int next_hour, int next_minute) const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartPrev,
        PartNext,
        PartToday,
        PartNow,
        PartClear,
        PartDay,
        PartHour,
        PartMinute
    };

    Part m_hover_part = PartNone;
    int m_hover_value = -1;
    Part m_press_part = PartNone;
    int m_press_value = -1;
    int m_hour_scroll = 0;
    int m_minute_scroll = 0;
    Part m_active_part = PartDay;
    bool has_value = true;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int visible_row_count() const;
    int hour_row_count() const;
    int minute_row_count() const;
    void clamp_scroll();
    void ensure_selected_visible();
    void scroll_part(Part part, int rows);
    bool select_step(Part part, int delta);
    int effective_min_time(int yyyymmdd) const;
    int effective_max_time(int yyyymmdd) const;
    Part part_at(int x, int y, int* value = nullptr) const;
    Part header_part_at(int x, int y) const;
    std::wstring display_text() const;
};
