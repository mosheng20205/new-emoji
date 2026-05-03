#pragma once
#include "element_base.h"

class Calendar : public Element {
public:
    int year = 2026;
    int month = 5;
    int selected_day = 1;
    int min_value = 0;
    int max_value = 0;
    int today_value = 0;
    bool show_today = true;
    bool range_select = false;
    int range_start = 0;
    int range_end = 0;

    const wchar_t* type_name() const override { return L"Calendar"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_date(int next_year, int next_month, int next_day);
    void set_range(int min_yyyymmdd, int max_yyyymmdd);
    void set_options(int today_yyyymmdd, bool next_show_today);
    void set_selection_range(int start_yyyymmdd, int end_yyyymmdd, bool enabled);
    void get_selection_range(int& start_yyyymmdd, int& end_yyyymmdd, bool& enabled) const;
    void move_month(int delta);
    int value() const;
    bool can_select(int yyyymmdd) const;

private:
    enum Part {
        PartNone,
        PartPrev,
        PartNext,
        PartDay
    };

    int m_hover_day = 0;
    int m_press_day = 0;
    Part m_press_part = PartNone;

    int day_at(int x, int y) const;
    int day_value(int day) const;
    Part header_part_at(int x, int y) const;
};
