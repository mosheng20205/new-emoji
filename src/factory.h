#pragma once
#include <d2d1.h>
#include <dwrite.h>
#include <wincodec.h>

extern ID2D1Factory*    g_d2d_factory;
extern IDWriteFactory*  g_dwrite_factory;
extern IWICImagingFactory* g_wic_factory;

/** Lazily create D2D + DWrite factories. Returns true on success. */
bool ensure_factories();
