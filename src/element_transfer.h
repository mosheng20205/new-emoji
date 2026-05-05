#pragma once
#include "element_base.h"
#include <vector>

struct TransferItem {
    std::wstring key;
    std::wstring label;
    std::wstring value;
    std::wstring desc;
    std::wstring pinyin;
    bool disabled = false;
    bool checked = false;
};

class Transfer : public Element {
public:
    std::vector<TransferItem> left_items;
    std::vector<TransferItem> right_items;
    int left_selected = -1;
    int right_selected = -1;
    std::wstring left_filter;
    std::wstring right_filter;

    bool filterable = false;
    bool multiple = true;
    bool show_footer = false;
    bool show_select_all = true;
    bool show_count = true;
    int render_mode = 0;

    std::wstring left_title = L"源列表";
    std::wstring right_title = L"目标列表";
    std::wstring move_left_text = L"到左边";
    std::wstring move_right_text = L"到右边";
    std::wstring no_checked_format = L"${total}";
    std::wstring has_checked_format = L"${checked}/${total}";
    std::wstring item_template = L"{label}";
    std::wstring left_footer_text = L"左侧操作";
    std::wstring right_footer_text = L"右侧操作";
    std::wstring filter_placeholder = L"请输入关键词 🔎";

    const wchar_t* type_name() const override { return L"Transfer"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_blur() override;

    void set_items(const std::vector<std::wstring>& left, const std::vector<std::wstring>& right);
    void set_data_ex(const std::vector<TransferItem>& items, const std::vector<std::wstring>& target_keys);
    void move_selected_right();
    void move_selected_left();
    void move_all_right();
    void move_all_left();
    void set_left_selected(int index);
    void set_right_selected(int index);
    void set_filters(const std::wstring& left, const std::wstring& right);
    void set_item_disabled(int side, int index, bool disabled);
    bool get_item_disabled(int side, int index) const;
    void set_checked_keys(const std::vector<std::wstring>& left_keys,
                          const std::vector<std::wstring>& right_keys);
    void set_options(bool filterable_value, bool multiple_value, bool show_footer_value,
                     bool show_select_all_value, bool show_count_value, int render_mode_value);
    void set_titles(const std::wstring& left, const std::wstring& right);
    void set_button_texts(const std::wstring& left, const std::wstring& right);
    void set_format(const std::wstring& no_checked, const std::wstring& has_checked);
    void set_item_template(const std::wstring& templ);
    void set_footer_texts(const std::wstring& left, const std::wstring& right);
    void set_filter_placeholder(const std::wstring& text);

    int left_count() const;
    int right_count() const;
    int matched_count(int side) const;
    int disabled_count(int side) const;
    int checked_count(int side) const;
    std::wstring value_keys_text() const;
    std::wstring text_value(int text_type) const;

private:
    enum Part {
        PartNone,
        PartLeftItem,
        PartRightItem,
        PartMoveRight,
        PartMoveLeft,
        PartMoveAllRight,
        PartMoveAllLeft,
        PartLeftFilter,
        PartRightFilter,
        PartLeftSelectAll,
        PartRightSelectAll,
        PartLeftFooter,
        PartRightFooter
    };

    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_hover_index = -1;
    int m_press_index = -1;
    int m_active_filter_side = -1;

    Rect left_rect() const;
    Rect right_rect() const;
    Rect move_right_rect() const;
    Rect move_left_rect() const;
    Rect move_all_right_rect() const;
    Rect move_all_left_rect() const;
    Rect filter_rect(int side) const;
    Rect footer_rect(int side) const;
    float row_height() const;
    float header_height() const;
    float filter_height() const;
    float footer_height() const;
    float rows_top(int side) const;
    float rows_bottom(int side) const;
    Part hit_part(int x, int y, int& index) const;
    std::vector<int> rendered_indices(int side) const;
    bool matches_filter(int side, int index) const;
    bool is_disabled(int side, int index) const;
    bool any_checked(int side) const;
    void normalize_state();
    void move_indices(int from_side, std::vector<int> indices);
    void toggle_item_checked(int side, int index);
    void set_all_checked(int side, bool checked);
    std::wstring display_text(const TransferItem& item) const;
    std::wstring primary_key(const TransferItem& item) const;
    std::wstring side_format_text(int side) const;
};
