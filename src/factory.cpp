#include "factory.h"

ID2D1Factory*          g_d2d_factory   = nullptr;
IDWriteFactory*        g_dwrite_factory = nullptr;
IWICImagingFactory*    g_wic_factory    = nullptr;

bool ensure_factories() {
    if (g_d2d_factory && g_dwrite_factory && g_wic_factory) return true;

    HRESULT hr = S_OK;
    if (!g_d2d_factory) {
        hr = D2D1CreateFactory(D2D1_FACTORY_TYPE_SINGLE_THREADED, &g_d2d_factory);
        if (FAILED(hr)) return false;
    }

    if (!g_dwrite_factory) {
        hr = DWriteCreateFactory(DWRITE_FACTORY_TYPE_SHARED, __uuidof(IDWriteFactory),
                                 reinterpret_cast<IUnknown**>(&g_dwrite_factory));
        if (FAILED(hr)) return false;
    }

    if (!g_wic_factory) {
        hr = CoCreateInstance(CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
                              IID_PPV_ARGS(&g_wic_factory));
        if (hr == CO_E_NOTINITIALIZED) {
            HRESULT co_hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
            if (SUCCEEDED(co_hr) || co_hr == RPC_E_CHANGED_MODE) {
                hr = CoCreateInstance(CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
                                      IID_PPV_ARGS(&g_wic_factory));
            }
        }
    }
    return SUCCEEDED(hr);
}
