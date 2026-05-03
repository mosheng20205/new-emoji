#pragma once
#include "element_base.h"
#include <vector>

struct CascaderOption {
    std::vector<std::wstring> parts;
};

class Cascader : public Element {
public:
    std::vector<CascaderOption> options;
    std::vector<std::wstring> selected_path;
    bool open = false;
    bool searchable = false;
    bool lazy_mode = false;
    std::wstring search_text;
    int last_lazy_level = -1;

    const wchar_t* type_name() const override { return L"Cascader"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_options(const std::vector<CascaderOption>& values);
    void set_selected_path(const std::vector<std::wstring>& path);
    void set_open(bool next_open);
    void set_advanced_options(bool searchable, bool lazy_mode);
    void set_search_text(const std::wstring& text);
    bool is_open() const;
    int option_count() const;
    int selected_depth() const;
    int active_level_count() const;
    int matched_count() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    std::vector<std::wstring> active_path;
    int m_hover_col = -1;
    int m_hover_row = -1;
    int m_press_col = -1;
    int m_press_row = -1;
    Part m_press_part = PartNone;

    int row_height() const;
    int column_width() const;
    int level_count() const;
    int menu_height() const;
    int menu_y() const;
    int menu_width() const;
    bool search_active() const;
    std::vector<CascaderOption> matching_options() const;
    std::wstring join_path(const std::vector<std::wstring>& path) const;
    std::vector<std::wstring> values_at_level(int level) const;
    bool has_children(const std::vector<std::wstring>& path) const;
    bool is_leaf_path(const std::vector<std::wstring>& path) const;
    std::wstring display_text() const;
    Part part_at(int x, int y, int* col = nullptr, int* row = nullptr) const;
};
