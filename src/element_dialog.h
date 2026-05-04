#pragma once
#include "element_base.h"
#include <vector>

class Dialog : public Element {
public:
    std::wstring title;
    std::vector<std::wstring> buttons;
    bool modal = true;
    bool closable = true;
    bool close_on_mask = false;
    bool draggable = true;
    bool center = false;
    bool footer_center = false;
    int width_mode = 0; // 0 logical px, 1 percent of available width
    int width_value = 0;
    int footer_height = 58;
    int content_padding = 20;
    int content_parent_id = 0;
    int footer_parent_id = 0;
    bool close_pending = false;
    int pending_close_action = 0;
    int active_button = 0;
    int last_button = -1;
    int button_click_count = 0;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger, 5 mask
    ElementValueCallback button_cb = nullptr;
    ElementBeforeCloseCallback before_close_cb = nullptr;

    const wchar_t* type_name() const override { return L"Dialog"; }
    void layout(const Rect& available) override;
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_title(const std::wstring& value);
    void set_body(const std::wstring& value);
    void set_modal(bool value);
    void set_closable(bool value);
    void set_open(bool value);
    void set_options(bool open, bool modal_value, bool closable_value,
                     bool mask_close, bool drag_enabled, int w, int h);
    void set_advanced_options(int width_mode_value, int width_value_value,
                              bool center_value, bool footer_center_value,
                              int content_padding_value, int footer_height_value);
    void set_buttons(const std::vector<std::wstring>& values);
    void trigger_button(int index, int action);
    void close_dialog(int action);
    void confirm_pending_close(bool allow);
    bool is_open() const { return visible; }
    int hover_part() const { return (int)m_hover_part; }
    int press_part() const { return (int)m_press_part; }
    int offset_x() const { return m_offset_x; }
    int offset_y() const { return m_offset_y; }
    Rect dialog_rect() const { return m_dialog_rect; }
    Rect content_rect_in_dialog() const;
    Rect footer_rect_in_dialog() const;

private:
    enum Part {
        PartNone,
        PartDialog,
        PartHeader,
        PartClose,
        PartMask,
        PartButton
    };

    Rect m_dialog_rect;
    Rect m_close_rect;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    int m_hover_button = -1;
    int m_press_button = -1;
    bool m_dragging = false;
    int m_offset_x = 0;
    int m_offset_y = 0;
    int m_drag_start_x = 0;
    int m_drag_start_y = 0;
    int m_drag_origin_x = 0;
    int m_drag_origin_y = 0;

    float scale() const;
    void update_layout();
    void clamp_offset(int dialog_w, int dialog_h);
    Part part_at(int x, int y) const;
    Rect button_rect(int index) const;
    int button_at(int x, int y) const;
};
