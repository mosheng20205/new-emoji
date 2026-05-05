#pragma once
#include "element_base.h"
#include <map>
#include <string>
#include <vector>

struct CalendarCellItem {
    int date = 0;
    std::wstring label;
    std::wstring extra;
    std::wstring emoji;
    std::wstring badge;
    Color bg = 0;
    Color fg = 0;
    Color border = 0;
    Color badge_bg = 0;
    Color badge_fg = 0;
    int font_flags = 0;
    bool disabled = false;
};

struct CalendarVisibleCell {
    int date = 0;
    int year = 0;
    int month = 0;
    int day = 0;
    bool current_month = true;
    bool display_range = true;
    bool selectable = true;
    bool selected = false;
    bool today = false;
    bool hot = false;
    bool in_selection_range = false;
    const CalendarCellItem* custom = nullptr;
};

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

    int display_start = 0;
    int display_end = 0;
    bool show_header = true;
    bool show_week_header = true;
    int label_mode = 0;
    bool show_adjacent_days = true;
    float cell_radius = 4.0f;
    Color selected_bg = 0;
    Color selected_fg = 0;
    Color range_bg = 0;
    Color today_border = 0;
    Color hover_bg = 0;
    Color disabled_fg = 0;
    Color adjacent_fg = 0;
    std::wstring selected_marker;
    std::wstring cell_items_spec;
    std::map<int, CalendarCellItem> cell_items;
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"Calendar"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_date(int next_year, int next_month, int next_day);
    void set_date_value(int yyyymmdd);
    void set_range(int min_yyyymmdd, int max_yyyymmdd);
    void set_options(int today_yyyymmdd, bool next_show_today);
    void set_selection_range(int start_yyyymmdd, int end_yyyymmdd, bool enabled);
    void get_selection_range(int& start_yyyymmdd, int& end_yyyymmdd, bool& enabled) const;
    void set_display_range(int start_yyyymmdd, int end_yyyymmdd);
    void get_display_range(int& start_yyyymmdd, int& end_yyyymmdd) const;
    void set_cell_items(const std::wstring& spec);
    void clear_cell_items();
    void set_visual_options(bool next_show_header, bool next_show_week_header,
                            int next_label_mode, bool next_show_adjacent_days,
                            float next_cell_radius);
    void get_visual_options(int& out_show_header, int& out_show_week_header,
                            int& out_label_mode, int& out_show_adjacent_days,
                            float& out_cell_radius) const;
    void set_state_colors(Color next_selected_bg, Color next_selected_fg,
                          Color next_range_bg, Color next_today_border,
                          Color next_hover_bg, Color next_disabled_fg,
                          Color next_adjacent_fg);
    void get_state_colors(Color& out_selected_bg, Color& out_selected_fg,
                          Color& out_range_bg, Color& out_today_border,
                          Color& out_hover_bg, Color& out_disabled_fg,
                          Color& out_adjacent_fg) const;
    void set_selected_marker(const std::wstring& marker);
    void move_month(int delta);
    int value() const;
    bool can_select(int yyyymmdd) const;
    bool can_interact(int yyyymmdd) const;

private:
    enum Part {
        PartNone,
        PartPrev,
        PartNext,
        PartDay
    };

    int m_hover_value = 0;
    int m_press_value = 0;
    Part m_press_part = PartNone;

    std::vector<CalendarVisibleCell> visible_cells() const;
    int date_at(int x, int y) const;
    Part header_part_at(int x, int y) const;
    int day_value(int day) const;
    bool display_range_enabled() const;
    void invoke_change();
};
