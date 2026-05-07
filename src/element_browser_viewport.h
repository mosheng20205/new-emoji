#pragma once
#include "element_base.h"
#include <d2d1.h>

class BrowserViewport : public Element {
public:
    int state = 4; // 0 blank, 1 loading, 2 screenshot, 3 error, 4 new tab
    bool loading = false;
    int progress = 0;
    std::wstring title = L"新标签页";
    std::wstring description = L"搜索或输入网址，开始浏览。";
    std::wstring icon = L"\U0001F310";
    std::wstring screenshot_source;
    int bitmap_width = 0;
    int bitmap_height = 0;

    ~BrowserViewport() override;
    const wchar_t* type_name() const override { return L"BrowserViewport"; }
    void paint(RenderContext& ctx) override;
    void set_state(int next_state);
    void set_placeholder(const std::wstring& next_title,
                         const std::wstring& next_desc,
                         const std::wstring& next_icon);
    void set_loading(bool value, int next_progress);
    void set_screenshot_source(const std::wstring& source);

private:
    ID2D1Bitmap* bitmap = nullptr;
    ID2D1RenderTarget* bitmap_rt = nullptr;
    std::wstring bitmap_source;

    void release_bitmap();
    bool ensure_bitmap(RenderContext& ctx);
};
