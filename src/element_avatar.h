#pragma once
#include "element_base.h"
#include <d2d1.h>
#include <wincodec.h>

class Avatar : public Element {
public:
    int shape = 0;
    int fit = 0;
    bool image_loaded = false;
    bool image_failed = false;

    ~Avatar() override;
    const wchar_t* type_name() const override { return L"Avatar"; }
    void paint(RenderContext& ctx) override;

    void set_shape(int value);
    void set_source(const std::wstring& path);
    void set_fit(int value);

private:
    std::wstring m_source;
    IWICBitmapSource* m_bitmap = nullptr;
    ID2D1Bitmap* m_d2d_bitmap = nullptr;

    void release_images();
    void ensure_d2d_bitmap(RenderContext& ctx);
};
