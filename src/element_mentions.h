#pragma once
#include "element_base.h"
#include <vector>

class Mentions : public Element {
public:
    std::wstring value;
    std::vector<std::wstring> suggestions;
    bool open = false;
    int selected_index = 0;
    wchar_t trigger_char = L'@';
    bool filter_enabled = true;
    bool insert_space_after_pick = true;
    std::wstring filter_text;

    const wchar_t* type_name() const override { return L"Mentions"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_blur() override;

    void set_value(const std::wstring& next_value);
    void set_suggestions(const std::vector<std::wstring>& values);
    void set_selected_index(int index);
    void set_open(bool next_open);
    void set_options(wchar_t trigger, bool filter_enabled, bool insert_space);
    void set_filter_text(const std::wstring& text);
    void commit_text(const std::wstring& text);
    void insert_selected();
    bool is_open() const;
    int suggestion_count() const;
    int matched_count() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    Part m_press_part = PartNone;

    int row_height() const;
    int display_count() const;
    int popup_height() const;
    int popup_y() const;
    int option_at(int x, int y) const;
    Part part_at(int x, int y, int* option_index = nullptr) const;
    std::vector<int> rendered_indices() const;
    bool matches_filter(int index) const;
    void update_filter_from_value();
};
