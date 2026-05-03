#pragma once
#include "element_base.h"

class KpiCard : public Element {
public:
    std::wstring title;
    std::wstring value;
    std::wstring subtitle;
    std::wstring trend;
    std::wstring helper;
    int trend_type = 0;
    bool loading = false;

    const wchar_t* type_name() const override { return L"KpiCard"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& next_title);
    void set_value(const std::wstring& next_value);
    void set_subtitle(const std::wstring& next_subtitle);
    void set_trend(const std::wstring& next_trend, int next_type);
    void set_options(bool loading_value, const std::wstring& helper_text);
};

class Trend : public Element {
public:
    std::wstring title;
    std::wstring value;
    std::wstring percent;
    std::wstring detail;
    int direction = 0;
    bool inverse = false;
    bool show_icon = true;

    const wchar_t* type_name() const override { return L"Trend"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& next_title);
    void set_value(const std::wstring& next_value);
    void set_percent(const std::wstring& next_percent);
    void set_detail(const std::wstring& next_detail);
    void set_direction(int next_direction);
    void set_options(bool inverse_value, bool show_icon_value);
};

class StatusDot : public Element {
public:
    std::wstring label;
    std::wstring description;
    int status = 0;
    bool pulse = false;
    bool compact = false;

    const wchar_t* type_name() const override { return L"StatusDot"; }
    void paint(RenderContext& ctx) override;

    void set_label(const std::wstring& next_label);
    void set_description(const std::wstring& next_description);
    void set_status(int next_status);
    void set_options(bool pulse_value, bool compact_value);
};
