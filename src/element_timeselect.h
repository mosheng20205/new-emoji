#pragma once
#include "element_base.h"

class TimeSelect : public Element {
public:
    int hour = 9;
    int minute = 30;
    bool open = false;
    int min_time = 0;
    int max_time = 2359;
    int step_minutes = 10;
    int time_format = 0;
    std::wstring placeholder;

    const wchar_t* type_name() const override { return L"TimeSelect"; }
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
    void set_scroll(int next_scroll);
    int scroll() const;
    int candidate_count() const;
    int group_count() const;
    int active_index() const;
    int value() const;
    bool is_open() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    int m_hover_part = PartNone;
    int m_hover_value = -1;
    int m_press_part = PartNone;
    int m_press_value = -1;
    int m_scroll = 0;
    int m_active_index = 0;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int row_height() const;
    int visible_row_count() const;
    int total_row_count() const;
    int option_minutes(int index) const;
    int option_value(int index) const;
    int row_option_index(int row, bool* is_group = nullptr) const;
    int selected_option_index() const;
    void clamp_scroll();
    void ensure_selected_visible();
    bool select_option_index(int index);
    bool select_step(int delta);
    bool can_select_time(int next_hour, int next_minute) const;
    Part part_at(int x, int y, int* value = nullptr) const;
    std::wstring display_text() const;
    std::wstring group_text(int minutes) const;
    std::wstring option_text(int hhmm) const;
};
