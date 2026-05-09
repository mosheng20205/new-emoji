#pragma once
#include "element_base.h"

class Input : public Element {
public:
    std::wstring value;
    std::wstring placeholder;
    std::wstring prefix;
    std::wstring suffix;
    std::wstring prefix_icon;
    std::wstring suffix_icon;
    bool clearable = false;
    bool readonly = false;
    bool password = false;
    bool multiline = false;
    bool show_password_toggle = false;
    bool show_word_limit = false;
    bool autosize = false;
    bool context_menu_enabled = true;
    int min_rows = 0;
    int max_rows = 0;
    int size = 0; // 0 default, 1 medium, 2 small, 3 mini
    int validate_state = 0; // 0 normal, 1 success, 2 warning, 3 error
    int max_length = 0; // 0 unlimited
    ElementTextCallback text_cb = nullptr;

    const wchar_t* type_name() const override { return L"Input"; }
    void layout(const Rect& available) override;
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_value(const std::wstring& next_value);
    void set_placeholder(const std::wstring& next_placeholder);
    void set_affixes(const std::wstring& next_prefix, const std::wstring& next_suffix);
    void set_icons(const std::wstring& next_prefix_icon, const std::wstring& next_suffix_icon);
    void set_clearable(bool next_clearable);
    void set_options(bool next_readonly, bool next_password, bool next_multiline, int next_validate_state);
    void set_visual_options(int next_size, bool next_show_password_toggle,
                            bool next_show_word_limit, bool next_autosize,
                            int next_min_rows, int next_max_rows);
    void set_context_menu_enabled(bool enabled);
    void set_selection(int start, int end);
    void get_selection(int& start, int& end) const;
    void set_max_length(int next_max_length);
    void get_state(int& cursor, int& length) const;
    void set_scroll_y(int value);
    void get_scroll_state(int& scroll_y, int& max_scroll_y, int& content_height, int& viewport_height) const;

private:
    int m_cursor_pos = 0;
    int m_sel_start = -1;
    int m_sel_end = -1;
    int m_select_anchor = 0;
    bool m_drag_selecting = false;
    bool m_press_clear = false;
    bool m_press_password_toggle = false;
    bool m_password_visible = false;
    int m_scroll_y = 0;
    int m_cached_content_h = 0;
    int m_cached_view_h = 0;
    bool m_drag_scrollbar = false;
    int m_drag_scroll_offset = 0;

    struct LayoutMetrics {
        float text_x = 0.0f;
        float text_y = 0.0f;
        float text_w = 0.0f;
        float text_h = 0.0f;
        float prefix_icon_x = 0.0f;
        float prefix_icon_w = 0.0f;
        float prefix_text_x = 0.0f;
        float prefix_text_w = 0.0f;
        float suffix_text_x = 0.0f;
        float suffix_text_w = 0.0f;
        float suffix_icon_x = 0.0f;
        float suffix_icon_w = 0.0f;
        float word_limit_x = 0.0f;
        float word_limit_w = 0.0f;
        Rect clear_rect{};
        Rect password_rect{};
        Rect suffix_icon_rect{};
        bool show_clear = false;
        bool show_password_toggle = false;
        bool show_suffix_icon = false;
        bool show_word_limit = false;
    };

    LayoutMetrics compute_metrics() const;
    std::wstring display_text() const;
    std::wstring word_limit_text() const;
    int effective_rows() const;
    int autosize_height_for_width(int width) const;
    int content_height_estimate() const;
    int viewport_height_estimate() const;
    int max_scroll_y() const;
    bool needs_vscroll() const;
    Rect scrollbar_track_rect() const;
    Rect scrollbar_thumb_rect() const;
    void clamp_scroll_y();
    void update_scroll_from_thumb(int y);
    void scroll_to_cursor();
    void apply_size_preset();
    void update_autosize_height();
    int char_width() const;
    int xpos_to_char(int x) const;
    int char_to_xpos(int index) const;
    bool has_selection() const;
    void normalized_selection(int& start, int& end) const;
    void clear_selection();
    void delete_selection();
    void select_all();
    void move_cursor_to(int pos, bool extend);
    std::wstring selected_text() const;
    void copy_selection_to_clipboard() const;
    void cut_selection_to_clipboard();
    void paste_from_clipboard();
    void show_context_menu(int x, int y);
    void insert_text(const std::wstring& text);
    void delete_char_before();
    void delete_char_after();
    void notify_text_changed();
};
