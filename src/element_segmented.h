#pragma once
#include "element_base.h"
#include <vector>

class Segmented : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<bool> disabled_items;
    int active_index = 0;

    const wchar_t* type_name() const override { return L"Segmented"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_active_index(int index);
    void set_disabled_indices(const std::vector<int>& indices);
    int item_count() const;
    int disabled_count() const;
    int hover_index() const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    bool is_disabled(int index) const;
    int segment_at(int x, int y) const;
    float segment_width() const;
};
