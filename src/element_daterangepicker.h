#pragma once
#include "element_base.h"

class DateRangePicker : public Element {
public:
    int range_start = 0;
    int range_end = 0;
    int year = 2026, month = 5;
    bool open = false;
    int min_value = 0, max_value = 0;
    int today_value = 0;
    int date_format = 0;
    int text_align = 0;
    std::wstring start_placeholder = L"开始日期";
    std::wstring end_placeholder = L"结束日期";
    std::wstring range_separator = L" 至 ";

    struct Shortcut { std::wstring text; int yyyymmdd; int yyyymmdd_end; };
    std::vector<Shortcut> shortcuts;
    DateDisabledCallback disabled_date_cb = nullptr;

    const wchar_t* type_name() const override { return L"DateRangePicker"; }
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

    void set_value(int start, int end);
    void set_range(int min_yyyymmdd, int max_yyyymmdd);
    void set_options(int today, int fmt);
    void set_open(bool next_open);
    void clear_value();
    void move_month(int delta);
    bool can_select(int yyyymmdd) const;

private:
    enum Part { PartNone = 0, PartMain, PartPrev, PartNext, PartShortcut, PartToday, PartClear, PartDay };
    int m_hover_day = 0;
    Part m_hover_part = PartNone;
    int m_hover_panel = 0; // 0=left, 1=right
    Part m_press_part = PartNone;
    int m_press_day = 0;
    int m_press_panel = 0;
    bool m_picking_end = false;

    int popup_width() const;
    int popup_height() const;
    int popup_y() const;
    int panel_width() const;
    int hover_day() const;
    std::wstring fmt_date(int val) const;
    std::wstring display_text() const;
};
