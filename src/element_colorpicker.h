#pragma once
#include "element_base.h"
#include <vector>

class ColorPicker : public Element {
public:
    Color value = 0xFF1E66F5;
    bool has_value = true;
    bool open = false;
    bool show_alpha = false;
    bool clearable = true;
    int size_mode = 0;  // 0 default, 1 medium, 2 small, 3 mini
    ElementValueCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"ColorPicker"; }
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

    void set_color(Color color);
    void set_alpha(int alpha);
    bool set_hex_text(const std::wstring& text);
    std::wstring get_hex_text() const;
    int alpha() const;
    void set_open(bool is_open);
    void set_options(bool show_alpha_value, int size_value, bool clearable_value);
    void clear_value();
    void set_palette(const std::vector<Color>& colors);
    int palette_count() const;

private:
    static constexpr int kColumns = 4;
    std::vector<Color> m_palette = {
        0xFF1E66F5, 0xFFE53935, 0xFFFB8C00, 0xFFFDD835,
        0xFF43A047, 0xFF00ACC1, 0xFF3949AB, 0xFF8E24AA,
        0xFFD81B60, 0xFF909399, 0xFF303133, 0xFFFFFFFF
    };
    int m_hover_index = -1;
    int m_press_index = -1;
    bool m_press_main = false;
    bool m_press_clear = false;

    float size_factor() const;
    float effective_font_size() const;
    int control_padding() const;
    int cell_size() const;
    int cell_gap() const;
    int alpha_bar_height() const;
    int panel_height() const;
    int panel_y() const;
    int color_at(int x, int y) const;
    int alpha_at(int x, int y) const;
    bool clear_at(int x, int y) const;
    std::wstring hex_text() const;
    void notify_changed();
    void paint_palette(RenderContext& ctx);
};
