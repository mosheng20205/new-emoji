#pragma once
#include "element_base.h"
#include <utility>
#include <vector>

class Descriptions : public Element {
public:
    std::vector<std::pair<std::wstring, std::wstring>> items;
    int columns = 3;
    int label_width = 88;
    int min_row_height = 28;
    bool bordered = true;
    bool wrap_values = false;
    bool responsive = true;
    bool last_item_span = false;

    const wchar_t* type_name() const override { return L"Descriptions"; }
    void paint(RenderContext& ctx) override;

    void set_items(const std::vector<std::pair<std::wstring, std::wstring>>& values);
    void set_columns(int value);
    void set_bordered(bool value);
    void set_options(int column_count, bool has_border, int label_width_value,
                     int min_row_height_value, bool wrap);
    void set_advanced_options(bool responsive_value, bool last_item_span_value);

private:
    int effective_columns() const;
};
