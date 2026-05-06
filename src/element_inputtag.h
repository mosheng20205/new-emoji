#pragma once
#include "element_base.h"
#include <vector>

class InputTag : public Element {
public:
    std::vector<std::wstring> tags;
    std::wstring input_value;
    std::wstring placeholder;
    int max_count = 0; // 0 = unlimited
    bool allow_duplicates = false;
    ElementTextCallback change_cb = nullptr;

    const wchar_t* type_name() const override { return L"InputTag"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_tags(const std::vector<std::wstring>& values);
    void set_input_value(const std::wstring& value);
    void set_placeholder(const std::wstring& value);
    void set_options(int next_max_count, bool next_allow_duplicates);
    bool add_tag(const std::wstring& value);
    bool remove_tag(int index);
    bool remove_last_tag();
    void commit_text(const std::wstring& value);
    int tag_count() const { return (int)tags.size(); }

private:
    int m_press_close = -1;
    int m_hover_close = -1;
    int m_cursor_pos = 0;

    int tag_width(const std::wstring& tag) const;
    Rect tag_rect(int index) const;
    Rect close_rect(int index) const;
    Rect input_rect() const;
    int close_at(int x, int y) const;
    int xpos_to_cursor(int x) const;
    int normalized_cursor() const;
    void commit_input();
    void sync_text();
    void notify_changed();
};
