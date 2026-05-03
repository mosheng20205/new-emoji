#pragma once
#include "element_base.h"
#include <vector>

struct UploadFileItem {
    std::wstring name;
    std::wstring full_path;
    int status = 1; // 0 waiting, 1 success, 2 uploading, 3 failed
    int progress = 100;
};

class Upload : public Element {
public:
    std::wstring title;
    std::wstring tip;
    std::vector<std::wstring> files;
    std::vector<UploadFileItem> file_items;
    std::wstring last_selected_files;
    int multiple = 1;
    int auto_upload = 0;
    int selected_count = 0;
    int last_selected_count = 0;
    int upload_request_count = 0;
    int retry_count = 0;
    int remove_count = 0;
    int last_action = 0; // 0 none, 1 dialog, 2 selected, 3 upload, 4 retry, 5 remove, 6 clear, 7 status
    ElementTextCallback select_cb = nullptr;
    ElementValueCallback upload_cb = nullptr;

    const wchar_t* type_name() const override { return L"Upload"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;

    void set_title(const std::wstring& value);
    void set_tip(const std::wstring& value);
    void set_files(const std::vector<std::wstring>& values);
    void set_file_items(const std::vector<UploadFileItem>& values);
    void set_options(int multiple_enabled, int auto_upload_enabled);
    void set_selected_files(const std::vector<std::wstring>& values);
    void set_file_status(int index, int status, int progress);
    void remove_file(int index);
    void retry_file(int index);
    void clear_files();
    int open_file_dialog(HWND hwnd);
    int start_upload(int index);
    std::wstring selected_files_text() const;

private:
    void sync_files_from_items();
    void notify_select();
    void notify_upload(int action, int index, int value);
    static std::wstring display_name_for_path(const std::wstring& path);
};
