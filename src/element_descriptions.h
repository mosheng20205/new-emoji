#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <utility>
#include <vector>

struct DescriptionItem {
    std::wstring label;
    std::wstring content;
    int span = 1;
    std::wstring label_icon;
    int content_type = 0;  // 0 text, 1 tag
    int tag_type = 0;      // 0 default, 1 success, 2 info, 3 warning, 4 danger
    int content_align = 0; // 0 left, 1 center, 2 right
    Color label_bg = 0;
    Color content_bg = 0;
    Color label_fg = 0;
    Color content_fg = 0;
};

class Descriptions : public Element {
public:
    std::vector<std::pair<std::wstring, std::wstring>> items;
    std::vector<DescriptionItem> rich_items;
    int columns = 3;
    int label_width = 88;
    int min_row_height = 28;
    bool bordered = true;
    bool wrap_values = false;
    bool responsive = true;
    bool last_item_span = false;
    int direction = 0;
    int size = 0;
    Color custom_border = 0;
    Color custom_label_bg = 0;
    Color custom_content_bg = 0;
    Color custom_label_fg = 0;
    Color custom_content_fg = 0;
    Color custom_title_fg = 0;
    std::wstring extra_emoji;
    std::wstring extra_text;
    bool extra_visible = false;
    int extra_variant = 1;
    int extra_click_count = 0;

    const wchar_t* type_name() const override { return L"Descriptions"; }
    void paint(RenderContext& ctx) override;
    bool accepts_input() const override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_items(const std::vector<std::pair<std::wstring, std::wstring>>& values);
    void set_rich_items(const std::vector<DescriptionItem>& values);
    void set_columns(int value);
    void set_bordered(bool value);
    void set_options(int column_count, bool has_border, int label_width_value,
                     int min_row_height_value, bool wrap);
    void set_advanced_options(bool responsive_value, bool last_item_span_value);
    void set_layout(int direction_value, int size_value, int column_count, bool has_border);
    void set_colors(Color border, Color label_bg, Color content_bg,
                    Color label_fg, Color content_fg, Color title_fg);
    void set_extra(const std::wstring& emoji, const std::wstring& value,
                   bool visible_value, int variant_value);

private:
    int effective_columns() const;
    float scaled_font_size() const;
    int scaled_min_row_height() const;
    bool point_in_extra(int x, int y) const;
    D2D1_RECT_F extra_rect = { 0, 0, 0, 0 };
    bool extra_hovered = false;
    bool extra_pressed = false;
};
