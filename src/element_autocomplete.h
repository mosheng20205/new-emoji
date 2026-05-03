#pragma once
#include "element_base.h"
#include <vector>

class Autocomplete : public Element {
public:
    std::vector<std::wstring> suggestions;
    std::wstring value;
    int selected_index = -1;
    bool open = false;
    bool async_loading = false;
    int async_request_id = 0;
    std::wstring empty_text = L"🫥 没有匹配建议";

    const wchar_t* type_name() const override { return L"Autocomplete"; }
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

    void set_suggestions(const std::vector<std::wstring>& values);
    void set_value(const std::wstring& next_value);
    void set_selected_index(int index);
    void set_open(bool next_open);
    void set_async_state(bool loading, int request_id);
    void set_empty_text(const std::wstring& text);
    bool is_open() const;
    int suggestion_count() const;

private:
    enum Part {
        PartNone,
        PartMain,
        PartOption
    };

    int m_hover_index = -1;
    int m_press_index = -1;
    Part m_press_part = PartNone;
    bool m_replace_on_next_char = false;

    int row_height() const;
    int display_count() const;
    int menu_height() const;
    int menu_y() const;
    int option_at(int x, int y) const;
    Part part_at(int x, int y, int* option_index = nullptr) const;
};
