#pragma once
#include "element_base.h"

class InputNumber : public Element {
public:
    int min_value = 0;
    int max_value = 100;
    int step = 1;
    int value = 0;
    int precision = 0;
    bool step_strictly = false;
    bool last_input_valid = true;
    ElementValueCallback value_cb = nullptr;

    ~InputNumber() override;
    const wchar_t* type_name() const override { return L"InputNumber"; }
    bool accepts_input() const override { return enabled; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_range(int min_v, int max_v);
    void set_step(int new_step);
    void set_value(int new_value);
    void set_precision(int new_precision);
    void set_step_strictly(bool strict);
    bool set_value_from_text(const std::wstring& value_text);
    bool can_step(int delta) const;
    std::wstring display_value() const;
    bool is_editing() const { return m_editing; }

private:
    enum Part {
        PartNone,
        PartMain,
        PartUp,
        PartDown
    };

    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    bool m_editing = false;
    bool m_replace_on_next_char = true;
    bool m_spun_on_press = false;
    UINT_PTR m_repeat_timer = 0;
    int m_repeat_delta = 0;
    std::wstring m_edit_buffer;

    static void CALLBACK repeat_timer(HWND hwnd, UINT msg, UINT_PTR id, DWORD time);
    int spin_width() const;
    int scale_factor() const;
    int clamp_value(int v) const;
    Part part_at(int x, int y) const;
    void step_by(int delta);
    void start_repeat(int delta);
    void stop_repeat();
    void start_edit();
    void commit_edit();
    bool parse_edit_buffer(int& out) const;
    std::wstring format_value(int v) const;
    void notify_value_changed();
};
