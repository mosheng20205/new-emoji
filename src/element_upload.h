#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <vector>

struct UploadFileItem {
    std::wstring name;
    std::wstring full_path;
    std::wstring thumbnail_path;
    int status = 1; // 0 waiting, 1 success, 2 uploading, 3 failed
    int progress = 100;
    long long size_bytes = 0;
};

class Upload : public Element {
public:
    std::wstring title;
    std::wstring tip;
    std::wstring trigger_text;
    std::wstring submit_text;
    std::wstring accept_filter;
    std::vector<std::wstring> files;
    std::vector<UploadFileItem> file_items;
    std::wstring last_selected_files;
    int multiple = 1;
    int auto_upload = 0;
    int style_mode = 5; // 0 list, 1 avatar, 2 picture-card, 3 custom-card, 4 picture-list, 5 drag, 6 manual
    int show_file_list = 1;
    int show_tip = 1;
    int show_actions = 1;
    int drop_enabled = 0;
    int limit = 0;
    int max_size_kb = 0;
    int preview_open = 0;
    int preview_index = -1;
    int selected_count = 0;
    int last_selected_count = 0;
    int upload_request_count = 0;
    int retry_count = 0;
    int remove_count = 0;
    int last_action = 0; // 0 none, 1 dialog, 2 selected, 3 upload, 4 retry, 5 remove, 6 clear, 7 status, 8 preview, 9 download, 10 exceed, 11 invalid, 12 drop
    ElementTextCallback select_cb = nullptr;
    ElementValueCallback upload_cb = nullptr;

    ~Upload() override = default;
    const wchar_t* type_name() const override { return L"Upload"; }
    void paint(RenderContext& ctx) override;
    void paint_overlay(RenderContext& ctx) override;
    Element* hit_test_overlay(int x, int y) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;
    void on_blur() override;

    void set_title(const std::wstring& value);
    void set_tip(const std::wstring& value);
    void set_files(const std::vector<std::wstring>& values);
    void set_file_items(const std::vector<UploadFileItem>& values);
    void set_options(int multiple_enabled, int auto_upload_enabled);
    void set_style(int next_style, int next_show_file_list, int next_show_tip,
                   int next_show_actions, int next_drop_enabled);
    void set_texts(const std::wstring& next_title, const std::wstring& next_tip,
                   const std::wstring& next_trigger, const std::wstring& next_submit);
    void set_constraints(int next_limit, int next_max_size_kb, const std::wstring& next_accept);
    void set_selected_files(const std::vector<std::wstring>& values);
    void set_file_status(int index, int status, int progress);
    void set_preview_open(int index, bool open);
    void remove_file(int index);
    void retry_file(int index);
    void clear_files();
    int open_file_dialog(HWND hwnd);
    int accept_dropped_files(const std::vector<std::wstring>& values);
    int start_upload(int index);
    std::wstring selected_files_text() const;
    std::wstring dialog_filter_text() const;
    bool wants_dropped_files() const;

private:
    int m_press_part = 0;
    int m_press_index = -1;

    void sync_files_from_items();
    int accept_selected_files(const std::vector<std::wstring>& values, int action);
    void notify_select();
    void notify_upload(int action, int index, int value);
    bool validate_files(const std::vector<std::wstring>& values, std::vector<UploadFileItem>& accepted);
    bool is_allowed_file_type(const std::wstring& path) const;
    bool is_image_file(const std::wstring& path) const;
    long long file_size_bytes(const std::wstring& path) const;
    int hit_part(int x, int y, int& index) const;
    D2D1_RECT_F preview_rect() const;
    bool load_bitmap(RenderContext& ctx, const std::wstring& path, ID2D1Bitmap** out_bitmap) const;
    void draw_bitmap_fit(RenderContext& ctx, const std::wstring& path, const D2D1_RECT_F& rect, bool cover) const;
    void paint_file_rows(RenderContext& ctx, float x, float y, float w, float h, bool thumbnails);
    void paint_picture_cards(RenderContext& ctx, float x, float y, float w, float h, bool custom_actions);
    void paint_avatar(RenderContext& ctx, float x, float y, float w, float h);
    void paint_trigger_button(RenderContext& ctx, const D2D1_RECT_F& rect, const std::wstring& label, Color bg, Color fg, Color border);
    static std::wstring display_name_for_path(const std::wstring& path);
};
