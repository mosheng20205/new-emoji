#pragma once
#include "element_popover.h"

class Popconfirm : public Popover {
public:
    std::wstring confirm_text = L"确定";
    std::wstring cancel_text = L"取消";
    std::wstring icon_text = L"!";
    Color icon_color = 0xFFE6A23C;
    bool show_icon = true;
    int last_result = -1; // 1 confirm, 0 cancel, -1 no selection
    int confirm_count = 0;
    int cancel_count = 0;
    int result_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger
    ElementValueCallback result_cb = nullptr;

    const wchar_t* type_name() const override { return L"Popconfirm"; }
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_buttons(const std::wstring& confirm, const std::wstring& cancel);
    void set_icon(const std::wstring& icon, Color color, bool visible);
    void reset_result();
    void choose_result(int result, int action);
    int get_last_result() const { return last_result; }
    int hover_button_part() const { return (int)hover_button; }
    int press_button_part() const { return (int)press_button; }

protected:
    bool has_close_button() const override { return false; }
    void update_popup_rect() override;
    void draw_popup_content(RenderContext& ctx, const Rect& content_rect) override;

private:
    enum ButtonPart {
        ButtonNone,
        ButtonConfirm,
        ButtonCancel
    };

    Rect confirm_rect;
    Rect cancel_rect;
    ButtonPart hover_button = ButtonNone;
    ButtonPart press_button = ButtonNone;

    ButtonPart button_at(int x, int y) const;
    void draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                     bool primary, bool hot, bool down, bool focused = false);
};
