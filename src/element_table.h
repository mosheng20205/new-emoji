#pragma once
#include "element_base.h"
#include <vector>

class Table : public Element {
public:
    std::vector<std::wstring> columns;
    std::vector<std::vector<std::wstring>> rows;
    std::wstring empty_text = L"暂无数据";
    int selected_row = -1;
    int row_height_value = 30;
    int header_height_value = 32;
    bool striped = true;
    bool bordered = true;
    bool selectable = true;
    int sort_column = -1;
    bool sort_desc = false;
    int scroll_row = 0;
    int fixed_column_width = 0;

    const wchar_t* type_name() const override { return L"Table"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_columns(const std::vector<std::wstring>& values);
    void set_rows(const std::vector<std::vector<std::wstring>>& values);
    void set_striped(bool value);
    void set_bordered(bool value);
    void set_empty_text(const std::wstring& value);
    void set_selected_row(int value);
    void set_options(bool striped_value, bool bordered_value, int row_height,
                     int header_height, bool selectable_value);
    void set_sort(int column_index, bool desc);
    void set_scroll_row(int value);
    void set_column_width(int value);

private:
    int m_hover_row = -1;
    int m_press_row = -1;

    int row_at(int x, int y) const;
    void clamp_scroll();
};
