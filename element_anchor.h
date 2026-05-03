#pragma once
#include "element_base.h"
#include <vector>

class Anchor : public Element {
public:
    std::vector<std::wstring> items;
    std::vector<int> target_positions;
    int active_index = 0;
    int scroll_position = 0;
    int offset = 0;
    int container_id = 0;
    int last_target_position = 0;

    const wchar_t* type_name() const override { return L"Anchor"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_items(const std::vector<std::wstring>& values);
    void set_active_index(int index);
    void set_targets(const std::vector<int>& positions);
    void set_options(int scroll_offset, int target_container_id);
    void set_scroll_position(int position);
    int item_count() const;
    int hover_index() const;
    int target_position_for(int index) const;

private:
    int m_hover_index = -1;
    int m_press_index = -1;

    int item_at(int x, int y) const;
    int row_height() const;
};
