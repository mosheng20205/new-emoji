#pragma once
#include "element_base.h"

class Statistic : public Element {
public:
    enum Mode {
        ModeNumber = 0,
        ModeText = 1,
        ModeCountdown = 2,
    };

    std::wstring title;
    std::wstring value;
    std::wstring prefix;
    std::wstring suffix;
    std::wstring display_text;
    std::wstring countdown_format;
    int precision = -1;
    bool animated = true;
    bool group_separator = false;
    wchar_t group_separator_char = L',';
    wchar_t decimal_separator_char = L'.';
    Color prefix_color = 0;
    Color suffix_color = 0;
    Color value_color = 0;
    bool suffix_clickable = false;
    int mode = ModeNumber;
    long long countdown_target_ms = 0;
    long long pause_remaining_ms = 0;
    bool countdown_paused = false;
    bool countdown_finished = false;
    int suffix_click_count = 0;
    double target_value = 0.0;
    mutable double display_value = 0.0;
    ULONGLONG anim_start = 0;
    ElementClickCallback suffix_click_cb = nullptr;
    ElementClickCallback finish_cb = nullptr;

    ~Statistic() override;
    const wchar_t* type_name() const override { return L"Statistic"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_title(const std::wstring& value);
    void set_value(const std::wstring& value);
    void set_prefix(const std::wstring& value);
    void set_suffix(const std::wstring& value);
    void set_format(const std::wstring& title_value,
                    const std::wstring& prefix_value,
                    const std::wstring& suffix_value);
    void set_options(int precision_value, bool animated_value);
    void set_number_options(int precision_value, bool animated_value,
                            bool group_separator_value,
                            wchar_t group_separator_value_char,
                            wchar_t decimal_separator_value_char);
    void set_affix_options(const std::wstring& prefix_value,
                           const std::wstring& suffix_value,
                           Color prefix_color_value,
                           Color suffix_color_value,
                           Color value_color_value,
                           bool suffix_clickable_value);
    void set_display_text(const std::wstring& text_value);
    void set_countdown(long long target_unix_ms, const std::wstring& format_value);
    void set_countdown_paused(bool paused_value);
    void add_countdown_time(long long delta_ms);
    void tick(int elapsed_ms);
    long long remaining_ms() const;
    bool timer_running() const { return m_timer_id != 0; }

private:
    Rect m_suffix_rect;
    bool m_suffix_hover = false;
    bool m_suffix_down = false;
    UINT_PTR m_timer_id = 0;

    std::wstring display_number() const;
    std::wstring display_value_text() const;
    std::wstring display_countdown() const;
    void reset_animation();
    void ensure_timer();
    void stop_timer();
    bool suffix_hit(int x, int y) const;
    void maybe_finish_countdown();
};
