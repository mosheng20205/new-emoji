#pragma once
#include "element_base.h"

class Drawer : public Element {
public:
    std::wstring title;
    int placement = 1; // 0 left, 1 right, 2 top, 3 bottom
    bool modal = true;
    bool closable = true;
    bool close_on_mask = false;
    int animation_progress = 100;
    int animation_ms = 180;
    int tick_count = 0;
    int close_count = 0;
    int last_action = 0; // 0 none, 1 set, 2 mouse, 3 keyboard, 4 trigger, 5 mask, 6 timer
    ElementValueCallback close_cb = nullptr;

    ~Drawer() override;

    const wchar_t* type_name() const override { return L"Drawer"; }
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
    void set_placement(int value);
    void set_modal(bool value);
    void set_closable(bool value);
    void set_open(bool value);
    void set_options(int new_placement, bool open, bool modal_value,
                     bool closable_value, bool mask_close, int size);
    void set_animation(int duration_ms);
    void close_drawer(int action);
    void tick(int elapsed_ms);
    bool is_open() const { return visible; }
    int hover_part() const { return (int)m_hover_part; }
    int press_part() const { return (int)m_press_part; }
    bool timer_running() const { return m_timer_id != 0; }

private:
    enum Part {
        PartNone,
        PartPanel,
        PartClose,
        PartMask
    };

    Rect m_panel_rect;
    Rect m_close_rect;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    UINT_PTR m_timer_id = 0;

    float scale() const;
    void update_layout();
    Part part_at(int x, int y) const;
    void ensure_timer();
    void stop_timer();
};
