#pragma once
#include "element_base.h"
#include <vector>

struct TimelineItem {
    std::wstring time;
    std::wstring content;
    std::wstring icon;
    int item_type = 0;
};

class Timeline : public Element {
public:
    std::vector<TimelineItem> items;
    int position = 0; // 0 left, 1 right, 2 alternate
    bool show_time = true;

    const wchar_t* type_name() const override { return L"Timeline"; }
    void paint(RenderContext& ctx) override;

    void set_items(const std::vector<TimelineItem>& values);
    void set_options(int position_value, bool show_time_value);
};
