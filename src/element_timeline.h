#pragma once
#include "element_base.h"
#include <vector>

struct TimelineItem {
    std::wstring time;
    std::wstring content;
    std::wstring icon;
    std::wstring card_title;
    std::wstring card_body;
    Color color = 0;
    int item_type = 0;
    int size = 0;       // 0 normal, 1 large
    int placement = -1; // -1 inherit, 0 top, 1 bottom
};

class Timeline : public Element {
public:
    std::vector<TimelineItem> items;
    int position = 0; // 0 left, 1 right, 2 alternate
    bool show_time = true;
    bool reverse = false;
    int default_placement = 0; // 0 top, 1 bottom

    const wchar_t* type_name() const override { return L"Timeline"; }
    void paint(RenderContext& ctx) override;

    void set_items(const std::vector<TimelineItem>& values);
    void set_options(int position_value, bool show_time_value);
    void set_advanced_options(int position_value, bool show_time_value,
                              bool reverse_value, int default_placement_value);
};
