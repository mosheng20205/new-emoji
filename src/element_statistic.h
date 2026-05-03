#pragma once
#include "element_base.h"

class Statistic : public Element {
public:
    std::wstring title;
    std::wstring value;
    std::wstring prefix;
    std::wstring suffix;
    int precision = -1;
    bool animated = true;
    double target_value = 0.0;
    double display_value = 0.0;
    ULONGLONG anim_start = 0;

    const wchar_t* type_name() const override { return L"Statistic"; }
    void paint(RenderContext& ctx) override;

    void set_title(const std::wstring& value);
    void set_value(const std::wstring& value);
    void set_prefix(const std::wstring& value);
    void set_suffix(const std::wstring& value);
    void set_format(const std::wstring& title_value,
                    const std::wstring& prefix_value,
                    const std::wstring& suffix_value);
    void set_options(int precision_value, bool animated_value);

private:
    std::wstring display_number() const;
    void reset_animation();
};
