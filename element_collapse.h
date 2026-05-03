#pragma once
#include "element_base.h"
#include <set>
#include <vector>

struct CollapseItem {
    std::wstring title;
    std::wstring body;
};

class Collapse : public Element {
public:
    std::vector<CollapseItem> items;
    std::set<int> disabled_indices;
    int active_index = 0;
    bool accordion = true;
    bool allow_collapse = true;
    bool animated = true;

    const wchar_t* type_name() const override { return L"Collapse"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<CollapseItem>& values);
    void set_active_index(int value);
    void set_accordion(bool value);
    void set_options(bool accordion_value, bool allow_collapse_value,
                     const std::set<int>& disabled, bool animated_value = true);

private:
    int m_hover_index = -1;
    int m_press_index = -1;
    int m_anim_index = -1;
    ULONGLONG m_anim_start = 0;
    static const int kAnimDurationMs = 180;

    int header_at(int x, int y) const;
    int next_enabled_index(int start, int direction) const;
    bool is_disabled(int index) const;
    float header_height() const;
    float animation_progress() const;
    void begin_animation(int index);
};
