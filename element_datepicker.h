#pragma once
#include "element_base.h"

class DatePicker : public Element {
public:
    int year = 2026;
    int month = 5;
    int selected_day = 1;
    bool open = false;
    int min_value = 0;
    int max_value = 0;
    int today_value = 0;
    bool show_today = true;
    int date_format = 0;
    bool has_value = true;
    bool range_select = false;
    int range_start = 0;
    int range_end = 0;

    const wchar_t* type_name() const override { return L"DatePicker"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_date(int next_year, int next_month, int next_day);
    void set_range(int min_yyyymmdd, int max_yyyymmdd);
    void set_options(int today_yyyymmdd, bool next_show_today, int next_date_format);
    void set_open(bool next_open);
    void clear_date();
    void select_today();
    void set_selection_range(int start_yyyymmdd, int end_yyyymmdd, bool enabled);
    void get_selection_range(int& start_yyyymmdd, int& end_yyyymmdd, bool& enabled) const;
    void move_month(int delta);
    int value() const;
    bool is_open() const;
    bool can_select(int yyyymmdd) const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartPrev,
        PartNext,
        PartToday,
        PartClear,
        PartDay
    };

    int m_hover_day = 0;
    int m_press_day = 0;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int day_at(int x, int y) const;
    int day_value(int day) const;
    Part header_part_at(int x, int y) const;
    std::wstring display_text() const;
};
