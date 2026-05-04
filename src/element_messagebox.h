#pragma once
#include "element_base.h"

class MessageBoxElement : public Element {
public:
    enum Result {
        ResultCancel = 0,
        ResultConfirm = 1,
        ResultClose = -1
    };

    std::wstring title;
    std::wstring confirm_text = L"确定";
    std::wstring cancel_text = L"取消";
    std::wstring loading_text;
    std::wstring input_value;
    std::wstring input_placeholder;
    std::wstring input_pattern;
    std::wstring input_error;
    bool show_cancel = false;
    bool center = false;
    bool rich = false;
    bool distinguish_cancel_and_close = false;
    bool prompt = false;
    bool confirm_loading = false;
    bool input_error_visible = false;
    int box_type = 0;
    int before_close_delay_ms = 0;
    int timer_elapsed_ms = 0;
    int last_action = 0;
    MessageBoxResultCallback result_cb = nullptr;
    MessageBoxExCallback result_ex_cb = nullptr;

    ~MessageBoxElement() override;
    const wchar_t* type_name() const override { return L"MessageBox"; }
    void layout(const Rect& available) override;
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    bool wants_text_cursor_at(int x, int y) const;

    void tick(int elapsed_ms);
    void set_before_close(int delay_ms, const std::wstring& loading);
    void set_input(const std::wstring& value, const std::wstring& placeholder,
                   const std::wstring& pattern, const std::wstring& error);
    void set_options(int type, bool centered, bool rich_text, bool distinguish);

private:
    enum Part {
        PartNone,
        PartClose,
        PartConfirm,
        PartCancel
    };

    Rect m_dialog_rect;
    Rect m_close_rect;
    Rect m_confirm_rect;
    Rect m_cancel_rect;
    Rect m_input_rect;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    bool m_close_requested = false;
    UINT_PTR m_timer_id = 0;
    int m_input_cursor_pos = 0;
    int m_input_sel_start = -1;
    int m_input_sel_end = -1;
    int m_input_select_anchor = 0;
    bool m_input_drag_selecting = false;
    bool m_input_focused = false;

    float scale() const;
    void update_layout();
    Part part_at(int x, int y) const;
    void request_result(Result result);
    bool validate_prompt();
    void start_before_close();
    void stop_timer();
    void draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                     bool primary, bool hot, bool pressed);
    void input_text_rect(float& x, float& y, float& w, float& h) const;
    int input_x_to_char(int x) const;
    float input_char_to_x(int index) const;
    int clamp_input_pos(int pos) const;
    int previous_input_pos(int pos) const;
    int next_input_pos(int pos) const;
    bool has_input_selection() const;
    void normalized_input_selection(int& start, int& end) const;
    void clear_input_selection();
    void delete_input_selection();
    void select_all_input();
    void move_input_cursor_to(int pos, bool extend);
    std::wstring selected_input_text() const;
    void copy_input_selection_to_clipboard() const;
    void cut_input_selection_to_clipboard();
    void paste_input_from_clipboard();
    void show_input_context_menu(int x, int y);
    void insert_input_text(const std::wstring& text);
    void delete_input_char_before();
    void delete_input_char_after();
};
