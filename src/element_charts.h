#pragma once
#include "element_base.h"
#include <vector>

struct ChartPoint {
    std::wstring label;
    float value = 0.0f;
};

class LineChart : public Element {
public:
    std::wstring title;
    std::vector<ChartPoint> points;
    std::vector<std::vector<ChartPoint>> series;
    int chart_style = 0;
    int selected_index = -1;
    bool show_axis = true;
    bool show_area = false;
    bool show_tooltip = true;

    const wchar_t* type_name() const override { return L"LineChart"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;

    void set_title(const std::wstring& value);
    void set_points(const std::vector<ChartPoint>& values);
    void set_series(const std::vector<std::vector<ChartPoint>>& values);
    void set_chart_style(int value);
    void set_selected_index(int value);
    void set_options(int style_value, bool axis, bool area, bool tooltip);

private:
    int point_at(int x, int y) const;
};

class BarChart : public Element {
public:
    std::wstring title;
    std::vector<ChartPoint> bars;
    std::vector<std::vector<ChartPoint>> series;
    int orientation = 0;
    int selected_index = -1;
    bool show_values = true;
    bool show_axis = true;

    const wchar_t* type_name() const override { return L"BarChart"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;

    void set_title(const std::wstring& value);
    void set_bars(const std::vector<ChartPoint>& values);
    void set_series(const std::vector<std::vector<ChartPoint>>& values);
    void set_orientation(int value);
    void set_selected_index(int value);
    void set_options(int orientation_value, bool values, bool axis);

private:
    int bar_at(int x, int y) const;
};

class DonutChart : public Element {
public:
    std::wstring title;
    std::vector<ChartPoint> slices;
    int active_index = 0;
    bool show_legend = true;
    bool show_labels = true;
    int ring_width = 22;

    const wchar_t* type_name() const override { return L"DonutChart"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;

    void set_title(const std::wstring& value);
    void set_slices(const std::vector<ChartPoint>& values);
    void set_active_index(int value);
    void set_options(bool legend, int width, bool labels = true);

private:
    int slice_at(int x, int y) const;
};
