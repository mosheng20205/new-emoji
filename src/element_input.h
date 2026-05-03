#pragma once
#include "element_base.h"

class Input : public Element {
public:
    std::wstring value;
    std::wstring placeholder;
    std::wstring prefix;
    std::wstring suffix;
    bool clearable = false;
    bool readonly = false;
    bool password = false;
    bool multiline = false;
    int validate_state = 0; // 0 normal, 1 success, 2 warning, 3 error
    int max_length = 0; // 0 unlimited
    ElementTextCallback text_cb = nullptr;

    const wchar_t* type_name() const override { return L"Input"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_value(const std::wstring& next_value);
    void set_placeholder(const std::wstring& next_placeholder);
    void set_affixes(const std::wstring& next_prefix, const std::wstring& next_suffix);
    void set_clearable(bool next_clearable);
    void set_options(bool next_readonly, bool next_password, bool next_multiline, int next_validate_state);
    void set_max_length(int next_max_length);
    void get_state(int& cursor, int& length) const;

private:
    int m_cursor_pos = 0;
    bool m_press_clear = false;

    Rect clear_rect() const;
    int char_width() const;
    int xpos_to_char(int x) const;
    int char_to_xpos(int index) const;
    void insert_text(const std::wstring& text);
    void delete_char_before();
    void delete_char_after();
    void notify_text_changed();
};
