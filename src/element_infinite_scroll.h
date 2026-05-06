#pragma once
#include "element_base.h"
#include <string>
#include <vector>

struct InfiniteScrollItem {
    std::wstring title;
    std::wstring subtitle;
    std::wstring tag;
};

class InfiniteScroll : public Element {
public:
    std::vector<InfiniteScrollItem> items;
    int scroll_y = 0;
    int item_height = 54;
    int gap = 8;
    int threshold = 60;
    int style_mode = 0;
    bool loading = false;
    bool no_more = false;
    bool disabled = false;
    bool show_scrollbar = true;
    bool show_index = false;
    std::wstring loading_text = L"加载中...";
    std::wstring no_more_text = L"没有更多了";
    std::wstring empty_text = L"暂无数据";
    int load_count = 0;
    int change_count = 0;
    int last_action = 0;
    int last_wheel_delta = 0;
    ElementValueCallback load_cb = nullptr;

    const wchar_t* type_name() const override { return L"InfiniteScroll"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_wheel(int x, int y, int delta) override;
    void on_key_down(int vk, int mods) override;
    void apply_dpi_scale(float scale) override;

    void set_items(const std::vector<InfiniteScrollItem>& next);
    void append_items(const std::vector<InfiniteScrollItem>& more);
    void clear_items();
    void set_state(bool next_loading, bool next_no_more, bool next_disabled);
    void set_options(int logical_item_height, int logical_gap, int logical_threshold,
                     int next_style_mode, bool next_show_scrollbar, bool next_show_index,
                     float scale);
    void set_texts(const std::wstring& loading_value,
                   const std::wstring& no_more_value,
                   const std::wstring& empty_value);
    void set_scroll(int value);

    int content_height() const;
    int viewport_height() const;
    int max_scroll() const;

private:
    int logical_item_height = 54;
    int logical_gap = 8;
    int logical_threshold = 60;
    bool dragging_thumb = false;
    int drag_offset = 0;
    int drag_start_scroll = 0;

    void apply_option_scale(float scale);
    void clamp_scroll();
    void update_scroll(int value, int action);
    void maybe_trigger_load();
    Rect viewport_rect() const;
    Rect scrollbar_track_rect() const;
    Rect scrollbar_thumb_rect() const;
    void update_scroll_from_thumb(int y);
};
