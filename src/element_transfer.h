#pragma once
#include "element_base.h"
#include <vector>

class Transfer : public Element {
public:
    std::vector<std::wstring> left_items;
    std::vector<std::wstring> right_items;
    std::vector<bool> left_disabled;
    std::vector<bool> right_disabled;
    int left_selected = -1;
    int right_selected = -1;
    std::wstring left_filter;
    std::wstring right_filter;

    const wchar_t* type_name() const override { return L"Transfer"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_items(const std::vector<std::wstring>& left, const std::vector<std::wstring>& right);
    void move_selected_right();
    void move_selected_left();
    void move_all_right();
    void move_all_left();
    void set_left_selected(int index);
    void set_right_selected(int index);
    void set_filters(const std::wstring& left, const std::wstring& right);
    void set_item_disabled(int side, int index, bool disabled);
    bool get_item_disabled(int side, int index) const;
    int left_count() const;
    int right_count() const;
    int matched_count(int side) const;
    int disabled_count(int side) const;

private:
    enum Part {
        PartNone,
        PartLeftItem,
        PartRightItem,
        PartMoveRight,
        PartMoveLeft,
        PartMoveAllRight,
        PartMoveAllLeft
    };

    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_hover_index = -1;
    int m_press_index = -1;

    Rect left_rect() const;
    Rect right_rect() const;
    Rect move_right_rect() const;
    Rect move_left_rect() const;
    Rect move_all_right_rect() const;
    Rect move_all_left_rect() const;
    float row_height() const;
    Part hit_part(int x, int y, int& index) const;
    std::vector<int> rendered_indices(int side) const;
    bool matches_filter(int side, int index) const;
    bool is_disabled(int side, int index) const;
    void normalize_state();
};
