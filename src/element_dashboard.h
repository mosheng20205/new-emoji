#pragma once
#include "element_base.h"

class Gauge : public Element {
public:
    std::wstring title;
    std::wstring caption;
    int value = 0;
    int status = 0;
    int min_value = 0;
    int max_value = 100;
    int warning_value = 70;
    int danger_value = 90;
    int stroke_width = 12;
    float display_value = 0.0f;
    ULONGLONG anim_start = 0;

    const wchar_t* type_name() const override { return L"Gauge"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& next_title);
    void set_value(int next_value);
    void set_caption(const std::wstring& next_caption);
    void set_status(int next_status);
    void set_options(int min_value, int max_value, int warning_value,
                     int danger_value, int stroke_width);
};

class RingProgress : public Element {
public:
    std::wstring title;
    std::wstring label;
    int value = 0;
    int status = 0;
    int stroke_width = 14;
    bool show_center = true;
    float display_value = 0.0f;
    ULONGLONG anim_start = 0;

    const wchar_t* type_name() const override { return L"RingProgress"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& next_title);
    void set_value(int next_value);
    void set_label(const std::wstring& next_label);
    void set_status(int next_status);
    void set_options(int stroke_width_value, bool show_center_value);
};

class BulletProgress : public Element {
public:
    std::wstring title;
    std::wstring description;
    int value = 0;
    int target = 80;
    int status = 0;
    int good_threshold = 80;
    int warn_threshold = 60;
    bool show_target = true;
    float display_value = 0.0f;
    ULONGLONG anim_start = 0;

    const wchar_t* type_name() const override { return L"BulletProgress"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& next_title);
    void set_description(const std::wstring& next_description);
    void set_value(int next_value);
    void set_target(int next_target);
    void set_status(int next_status);
    void set_options(int good_threshold_value, int warn_threshold_value,
                     bool show_target_value);
};
