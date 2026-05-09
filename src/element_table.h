#pragma once
#include "element_base.h"
#include <map>
#include <set>
#include <string>
#include <vector>

enum class TableCellKind {
    Text = 0, Index, Selection, Expand, Button, Buttons, Combo,
    Switch, Select, Progress, Status, Tag, PopoverTag
};

struct TableStyleOverride {
    bool has_bg = false;
    bool has_fg = false;
    bool has_align = false;
    bool has_font_flags = false;
    bool has_font_size = false;
    Color bg = 0;
    Color fg = 0;
    int align = 0;       // 0 left, 1 center, 2 right
    int font_flags = 0;  // 1 bold, 2 italic, 4 underline
    int font_size = 0;   // logical px; 0 = inherit
};

struct TableColumn {
    std::wstring key;
    std::wstring title;
    std::wstring parent_title;
    int width = 0;
    int min_width = 80;
    int fixed = 0;       // -1 left, 0 normal, 1 right
    int align = 0;
    int type = 0;
    bool sortable = false;
    bool filterable = false;
    bool searchable = true;
    bool overflow_tooltip = false;
    std::vector<std::wstring> options;
    TableStyleOverride style;
};

struct TableCell {
    TableCellKind kind = TableCellKind::Text;
    std::wstring value;
    std::vector<std::wstring> parts;
    std::map<std::wstring, std::wstring> options;
    TableStyleOverride style;
    bool checked = false;
    int number = 0;
    int status = 0;
};

struct TableRow {
    std::wstring key;
    std::wstring parent_key;
    std::vector<TableCell> cells;
    TableStyleOverride style;
    int level = 0;
    bool expanded = false;
    bool has_children = false;
    bool lazy = false;
    bool selectable = true;
};

struct TableSpan {
    int row = 0;
    int col = 0;
    int rowspan = 1;
    int colspan = 1;
};

class Table : public Element {
public:
    std::vector<std::wstring> columns;
    std::vector<std::vector<std::wstring>> rows;
    std::wstring empty_text = L"暂无数据";
    int selected_row = -1;
    int row_height_value = 42;
    int header_height_value = 46;
    bool striped = true;
    bool bordered = true;
    bool selectable = true;
    int sort_column = -1;
    bool sort_desc = false;
    int scroll_row = 0;
    int fixed_column_width = 0;

    std::vector<TableColumn> adv_columns;
    std::vector<TableRow> adv_rows;
    bool virtual_mode = false;
    int virtual_row_count = 0;
    int virtual_cache_window = 32;
    TableVirtualRowCallback virtual_row_cb = nullptr;
    std::vector<int> selected_rows;
    std::map<int, std::wstring> filters;
    std::vector<TableSpan> spans;
    std::vector<std::wstring> summary_values;
    std::wstring search_text;
    TableCellCallback cell_cb = nullptr;
    TableCellCallback cell_click_cb = nullptr;

    int selection_mode = 1;       // 0 none, 1 single, 2 multiple
    int scroll_x = 0;
    int max_height_value = 0;
    int tree_indent = 18;
    bool fixed_header = true;
    bool horizontal_scroll = false;
    bool show_summary = false;
    bool tree_mode = false;
    bool lazy_mode = false;
    bool show_header = true;
    bool header_column_resize = false;
    bool header_height_resize = false;
    int header_min_col_width = 48;
    int header_max_col_width = 720;
    int header_min_height = 34;
    int header_max_height = 180;

    const wchar_t* type_name() const override { return L"Table"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_wheel(int x, int y, int delta) override;
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

    void set_columns_ex(const std::wstring& spec);
    void set_rows_ex(const std::wstring& spec);
    int add_row_ex(const std::wstring& spec);
    int insert_row_ex(int row_index, const std::wstring& spec);
    bool delete_row(int row_index);
    bool clear_rows();
    void set_cell_ex(int row, int col, int type, const std::wstring& value,
                     const std::wstring& options);
    void set_row_style(int row, Color bg, Color fg, int align, int flags, int font_size);
    void set_cell_style(int row, int col, Color bg, Color fg, int align, int flags, int font_size);
    void set_selection_mode(int mode);
    void set_selected_rows_text(const std::wstring& spec);
    void set_filter(int col, const std::wstring& value);
    void clear_filter(int col);
    void set_search(const std::wstring& value);
    void set_span(int row, int col, int rowspan, int colspan);
    void clear_spans();
    void set_summary(const std::wstring& spec);
    void set_row_expanded(int row, bool expanded);
    void set_tree_options(bool enabled, int indent, bool lazy);
    void set_viewport_options(int max_height, bool fixed_header_value,
                              bool horizontal_scroll_value, bool show_summary_value);
    void set_scroll(int row, int x);
    void set_header_drag_options(bool column_resize, bool header_height_resize,
                                 int min_col_width, int max_col_width,
                                 int min_header_height, int max_header_height);
    void set_virtual_options(bool enabled, int row_count, int cache_window);
    void set_virtual_row_provider(TableVirtualRowCallback cb);
    void clear_virtual_cache();
    int row_count() const;
    const TableRow* row_ptr(int row) const;
    TableRow* row_ptr(int row);
    std::wstring get_cell_value(int row, int col) const;
    std::wstring full_state_text() const;

    int row_at(int x, int y) const;
    int column_at(int x, int y) const;
    std::vector<int> visible_row_indices() const;
    float column_x(int col, float left, float table_w) const;
    float column_width_at(int col, float table_w) const;
    int header_height_px() const;
    int row_height_px() const;
    int summary_height_px() const;
    int table_height_px() const;
    int visible_row_count() const;
    int max_scroll_row() const;
    int max_scroll_x() const;
    bool needs_vertical_scrollbar() const;
    bool needs_horizontal_scrollbar() const;
    void clamp_scroll();

private:
    int m_hover_row = -1;
    int m_hover_col = -1;
    int m_press_row = -1;
    int m_press_col = -1;
    int m_press_action = 0;
    int popup_row = -1;
    int popup_col = -1;
    int popup_hover = -1;
    int m_scroll_drag = 0;        // 0 none, 1 vertical, 2 horizontal
    int m_scroll_drag_start = 0;
    int m_scroll_drag_origin = 0;
    int m_header_drag = 0;        // 0 none, 1 column width, 2 header height
    int m_header_drag_col = -1;
    int m_header_drag_start = 0;
    int m_header_drag_origin = 0;
    mutable std::map<int, TableRow> virtual_cache;

    void sync_legacy_vectors();
    void ensure_cell_count(TableRow& row) const;
    void sync_selection_cells();
    TableRow parse_row_line(const std::wstring& line, int row_index) const;
    void apply_selection_state(TableRow& row, int row_index) const;
    bool ensure_virtual_row(int row) const;
    bool is_virtual_active() const;
    void invoke_cell(int row, int col, int action, int value);
    void invoke_cell_click(int row, int col);
    bool is_span_hidden(int row, int col) const;
    TableSpan span_for(int row, int col) const;
};
