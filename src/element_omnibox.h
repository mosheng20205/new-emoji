#pragma once
#include "element_base.h"
#include <vector>

struct OmniboxSuggestion {
    std::wstring type;
    std::wstring icon;
    std::wstring primary;
    std::wstring secondary;
    std::wstring completion;
};

struct OmniboxActionIcon {
    std::wstring icon;
    std::wstring name;
};

class Omnibox : public Element {
public:
    std::wstring value;
    std::wstring placeholder;
    int security_state = 0;
    std::wstring security_label;
    std::wstring chip_icon;
    std::wstring chip_text;
    Color chip_bg = 0;
    Color chip_fg = 0;
    std::vector<OmniboxActionIcon> action_icons;
    std::vector<OmniboxSuggestion> suggestions;
    bool suggestions_open = false;
    int selected_suggestion = -1;
    ElementTextCallback commit_cb = nullptr;
    ElementValueCallback icon_cb = nullptr;

    const wchar_t* type_name() const override { return L"Omnibox"; }
    bool accepts_input() const override { return enabled; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_char(wchar_t ch) override;
    void on_focus() override;
    void on_blur() override;

    void set_value(const std::wstring& next);
    void set_placeholder(const std::wstring& next);
    void set_security_state(int state, const std::wstring& label);
    void set_prefix_chip(const std::wstring& icon, const std::wstring& text, Color bg, Color fg);
    void set_action_icons(const std::vector<OmniboxActionIcon>& icons);
    void set_suggestions(const std::vector<OmniboxSuggestion>& items);
    void set_suggestion_open(bool open);
    void set_selected_suggestion(int index);

private:
    int cursor_pos = 0;
    int sel_start = -1;
    int sel_end = -1;
    int pressed_action = -1;
    int hovered_action = -1;
    bool selecting_suggestion = false;

    int char_width() const;
    bool has_selection() const;
    void clear_selection();
    void select_all();
    void delete_selection();
    void insert_text(const std::wstring& text);
    void copy_selection_to_clipboard() const;
    void cut_selection_to_clipboard();
    void paste_from_clipboard();
    void show_context_menu();
    int text_index_from_x(float local_x) const;
    float text_x_for_index(RenderContext& ctx, const std::wstring& text, int index, float max_w, float max_h) const;
    int action_at(int x, int y) const;
    int suggestion_at(int x, int y) const;
    Rect suggestion_popup_rect() const;
    float text_start_x() const;
    float text_width() const;
    std::wstring security_icon() const;
    void commit();
};
