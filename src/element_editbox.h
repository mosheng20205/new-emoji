#pragma once
#include "element_base.h"
#include <string>

class EditBox : public Element {
public:
    bool multiline = false;
    bool readonly  = false;
    bool password  = false;
    Color focus_border = 0;
    std::wstring placeholder;

    const wchar_t* type_name() const override { return L"EditBox"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;
    void on_dpi_scale_changed(float old_scale, float new_scale) override;
    void set_options(int read_only, int is_password, int is_multiline, Color focus_color,
                     const std::wstring& placeholder_text);
    void set_value(const std::wstring& value);
    void set_composition_text(const std::wstring& value);
    void end_composition();
    void commit_text(const std::wstring& value);
    void get_state(int& cursor, int& sel_start, int& sel_end, int& text_length) const;
    void set_scroll_y(int value);
    void get_scroll_state(int& scroll_y, int& max_scroll_y, int& content_height, int& viewport_height) const;
    ElementTextCallback text_cb = nullptr;

    // Internal state
    int        m_cursor_pos = 0;
    int        m_scroll_x   = 0;
    int        m_scroll_y   = 0;
    int        m_sel_start  = -1;
    int        m_sel_end    = -1;
    bool       m_cursor_on  = true;
    bool       m_composing  = false;
    std::wstring m_comp_text;
    float      m_cached_text_w = 0;  // updated each paint for cursor math
    int        m_cached_content_h = 0;
    int        m_cached_view_h = 0;
    bool       m_drag_scrollbar = false;
    int        m_drag_scroll_offset = 0;

private:
    void insert_text(const std::wstring& s);
    void notify_text_changed();
    void delete_selection();
    void delete_char_before();
    void delete_char_after();
    int  xpos_to_char(int x);
    int  point_to_char(int x, int y);
    int  char_to_xpos(int idx);
    void move_cursor_vertical(int direction, bool extend);
    int  max_scroll_y() const;
    int  estimate_content_height() const;
    int  estimate_view_height() const;
    Rect scrollbar_track_rect() const;
    Rect scrollbar_thumb_rect() const;
    bool needs_vscroll() const;
    void clamp_scroll_y();
    void update_scroll_from_thumb(int y);
    void scroll_to_cursor();
    void move_cursor(int delta, bool extend);

    // Blink timer
    static void CALLBACK blink_timer(HWND hwnd, UINT, UINT_PTR id, DWORD);
    void start_blink();
    void stop_blink();
    UINT_PTR m_blink_id = 0;
};
