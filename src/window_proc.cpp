#include <windows.h>
#include <windowsx.h>
#include <shellapi.h>
#include <imm.h>
#include <d2d1.h>
#include <dwrite.h>
#include "factory.h"
#include "window_state.h"
#include "element_tree.h"
#include "element_button.h"
#include "element_titlebar.h"
#include "element_editbox.h"
#include "element_input.h"
#include "element_inputtag.h"
#include "element_mentions.h"
#include "element_upload.h"
#include "element_message.h"
#include "element_messagebox.h"
#include "element_carousel.h"
#include "element_notification.h"
#include "element_loading.h"
#include "element_skeleton.h"
#include "element_drawer.h"
#include "element_tooltip.h"
#include "element_statistic.h"
#include "theme.h"
#include "dpi_context.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <map>
#include <vector>
#include <cmath>
#include <cstring>

extern HMODULE g_module;

std::map<HWND, WindowState*> g_windows;
thread_local WindowCreateParams* g_pending_create_params = nullptr;
constexpr UINT WM_NEWEMOJI_RENDER_LAYERED = WM_APP + 0x4E1;
static const wchar_t* kWindowClass = L"NewEmojiWindow";
extern std::map<UINT_PTR, EditBox*> g_blink_map;
extern std::map<UINT_PTR, Button*> g_button_timer_map;
extern std::map<UINT_PTR, Statistic*> g_statistic_timer_map;
extern std::map<UINT_PTR, Carousel*> g_carousel_timer_map;
extern std::map<UINT_PTR, Message*> g_message_timer_map;
extern std::map<UINT_PTR, MessageBoxElement*> g_messagebox_timer_map;
extern std::map<UINT_PTR, Notification*> g_notification_timer_map;
extern std::map<UINT_PTR, Loading*> g_loading_timer_map;
extern std::map<UINT_PTR, Skeleton*> g_skeleton_timer_map;
extern std::map<UINT_PTR, Drawer*> g_drawer_timer_map;
extern std::map<UINT_PTR, Tooltip*> g_tooltip_timer_map;

WindowState* window_state(HWND hwnd) {
    auto it = g_windows.find(hwnd);
    return it != g_windows.end() ? it->second : nullptr;
}

static bool apply_dwm_corner_preference(HWND hwnd, bool rounded, int radius) {
    static int is_win11_or_later = -1;
    if (is_win11_or_later < 0) {
        is_win11_or_later = 0;
        HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
        using RtlGetVersionFn = LONG(WINAPI*)(OSVERSIONINFOW*);
        auto rtl_get_version = ntdll
            ? reinterpret_cast<RtlGetVersionFn>(GetProcAddress(ntdll, "RtlGetVersion"))
            : nullptr;
        OSVERSIONINFOW version = {};
        version.dwOSVersionInfoSize = sizeof(version);
        if (rtl_get_version && rtl_get_version(&version) == 0) {
            is_win11_or_later =
                (version.dwMajorVersion > 10 ||
                 (version.dwMajorVersion == 10 && version.dwBuildNumber >= 22000))
                ? 1 : 0;
        }
    }
    if (!is_win11_or_later) return false;

    using DwmSetWindowAttributeFn = HRESULT(WINAPI*)(HWND, DWORD, LPCVOID, DWORD);
    static HMODULE dwm = LoadLibraryW(L"dwmapi.dll");
    static auto fn = dwm ? reinterpret_cast<DwmSetWindowAttributeFn>(
        GetProcAddress(dwm, "DwmSetWindowAttribute")) : nullptr;
    if (!fn) return false;

    constexpr DWORD kDwmWindowCornerPreference = 33;
    constexpr DWORD kDwmCornerDoNotRound = 1;
    constexpr DWORD kDwmCornerRound = 2;
    constexpr DWORD kDwmCornerRoundSmall = 3;
    DWORD preference = rounded
        ? (radius > 0 && radius <= 12 ? kDwmCornerRoundSmall : kDwmCornerRound)
        : kDwmCornerDoNotRound;
    return SUCCEEDED(fn(hwnd, kDwmWindowCornerPreference, &preference, sizeof(preference)));
}

static void clear_window_region(HWND hwnd, bool redraw) {
    SetWindowRgn(hwnd, nullptr, redraw ? TRUE : FALSE);
}

static bool apply_rounded_window_region(WindowState* st) {
    if (!st || !st->hwnd || st->rounded_layered_radius_px <= 0) return false;
    RECT wr{};
    if (!GetWindowRect(st->hwnd, &wr)) return false;
    int w = wr.right - wr.left;
    int h = wr.bottom - wr.top;
    if (w <= 0 || h <= 0) return false;

    int radius = (std::max)(1, (std::min)(st->rounded_layered_radius_px,
                                          (std::min)(w, h) / 2));
    HRGN region = CreateRoundRectRgn(0, 0, w + 1, h + 1, radius * 2, radius * 2);
    if (!region) return false;
    SetWindowRgn(st->hwnd, region, TRUE);
    st->rounded_region_active = true;
    st->rounded_region_radius_px = radius;
    st->rounded_layered_active = false;
    st->rounded_layered_radius_px = 0;
    st->rounded_layered_failures = 0;
    return true;
}

static void set_layered_window(HWND hwnd, bool enabled) {
    LONG_PTR ex = GetWindowLongPtrW(hwnd, GWL_EXSTYLE);
    LONG_PTR next = enabled ? (ex | WS_EX_LAYERED) : (ex & ~WS_EX_LAYERED);
    if (next == ex) return;
    SetWindowLongPtrW(hwnd, GWL_EXSTYLE, next);
    SetWindowPos(hwnd, nullptr, 0, 0, 0, 0,
                 SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER |
                 SWP_NOACTIVATE | SWP_FRAMECHANGED);
}

static int scaled_window_radius(WindowState* st, int width, int height) {
    if (!st || st->rounded_corner_radius <= 0 || width <= 0 || height <= 0) return 0;
    int radius = (int)std::lround((float)st->rounded_corner_radius * st->dpi_scale);
    int max_radius = (std::max)(1, (std::min)(width, height) / 2);
    return (std::max)(1, (std::min)(radius, max_radius));
}

static bool point_inside_rounded_rect(int x, int y, int w, int h, int radius) {
    if (x < 0 || y < 0 || x >= w || y >= h) return false;
    if (radius <= 0) return true;
    radius = (std::min)(radius, (std::min)(w, h) / 2);
    auto inside_corner = [radius](int dx, int dy) {
        long long xx = (long long)dx;
        long long yy = (long long)dy;
        long long rr = (long long)radius;
        return xx * xx + yy * yy <= rr * rr;
    };
    if (x < radius && y < radius) return inside_corner(x - radius, y - radius);
    if (x >= w - radius && y < radius) return inside_corner(x - (w - radius - 1), y - radius);
    if (x < radius && y >= h - radius) return inside_corner(x - radius, y - (h - radius - 1));
    if (x >= w - radius && y >= h - radius) return inside_corner(x - (w - radius - 1), y - (h - radius - 1));
    return true;
}

static bool point_inside_window_shape(WindowState* st, int x, int y) {
    if (!st || !st->rounded_layered_active) return true;
    RECT rc{};
    GetClientRectForWindowDpi(st->hwnd, &rc);
    return point_inside_rounded_rect(x, y, rc.right - rc.left, rc.bottom - rc.top,
                                     st->rounded_layered_radius_px);
}

static float rounded_rect_coverage(int x, int y, int w, int h, float radius) {
    if (radius <= 0.0f || w <= 0 || h <= 0) return 1.0f;
    radius = (std::min)(radius, (float)(std::min)(w, h) * 0.5f);

    float px = (float)x + 0.5f;
    float py = (float)y + 0.5f;
    float left = radius;
    float top = radius;
    float right = (float)w - radius;
    float bottom = (float)h - radius;

    float dx = 0.0f;
    if (px < left) dx = left - px;
    else if (px > right) dx = px - right;

    float dy = 0.0f;
    if (py < top) dy = top - py;
    else if (py > bottom) dy = py - bottom;

    if (dx <= 0.0f && dy <= 0.0f) return 1.0f;
    float dist = std::sqrt(dx * dx + dy * dy);
    float edge = radius - dist;
    if (edge >= 0.5f) return 1.0f;
    if (edge <= -0.5f) return 0.0f;
    return edge + 0.5f;
}

static void apply_rounded_alpha_mask(BYTE* bits, int w, int h, int stride, int radius) {
    if (!bits || w <= 0 || h <= 0 || stride <= 0 || radius <= 0) return;
    for (int y = 0; y < h; ++y) {
        BYTE* row = bits + y * stride;
        for (int x = 0; x < w; ++x) {
            if (x >= radius && x < w - radius && y >= radius && y < h - radius) continue;
            float coverage = rounded_rect_coverage(x, y, w, h, (float)radius);
            if (coverage >= 0.999f) continue;
            BYTE* p = row + x * 4;
            p[0] = (BYTE)std::lround((float)p[0] * coverage);
            p[1] = (BYTE)std::lround((float)p[1] * coverage);
            p[2] = (BYTE)std::lround((float)p[2] * coverage);
            p[3] = (BYTE)std::lround((float)p[3] * coverage);
        }
    }
}

static bool render_layered_window(WindowState* st) {
    if (!st || !st->hwnd || !st->rounded_layered_active || !g_d2d_factory ||
        !g_dwrite_factory || !g_wic_factory || !st->element_tree) {
        return false;
    }

    RECT rc{};
    GetClientRectForWindowDpi(st->hwnd, &rc);
    int w = rc.right - rc.left;
    int h = rc.bottom - rc.top;
    if (w <= 0 || h <= 0) return false;

    IWICBitmap* bitmap = nullptr;
    HRESULT hr = g_wic_factory->CreateBitmap(
        w, h, GUID_WICPixelFormat32bppPBGRA, WICBitmapCacheOnLoad, &bitmap);
    if (FAILED(hr) || !bitmap) return false;

    ID2D1RenderTarget* rt = nullptr;
    D2D1_RENDER_TARGET_PROPERTIES props = D2D1::RenderTargetProperties(
        D2D1_RENDER_TARGET_TYPE_DEFAULT,
        D2D1::PixelFormat(DXGI_FORMAT_B8G8R8A8_UNORM, D2D1_ALPHA_MODE_PREMULTIPLIED),
        96.0f, 96.0f);
    hr = g_d2d_factory->CreateWicBitmapRenderTarget(bitmap, props, &rt);
    if (FAILED(hr) || !rt) {
        bitmap->Release();
        return false;
    }

    int radius = (std::max)(1, (std::min)(st->rounded_layered_radius_px, (std::min)(w, h) / 2));

    rt->BeginDraw();
    rt->SetAntialiasMode(D2D1_ANTIALIAS_MODE_PER_PRIMITIVE);
    rt->Clear(D2D1::ColorF(0.0f, 0.0f, 0.0f, 0.0f));

    {
        const Theme* t = theme_for_window(st->hwnd);
        RenderContext ctx(rt, g_dwrite_factory);
        rt->FillRectangle(D2D1::RectF(0.0f, 0.0f, (float)w, (float)h),
                          ctx.get_brush(t->panel_bg));
        st->element_tree->paint(ctx);
        hr = rt->EndDraw();
    }

    rt->Release();
    if (FAILED(hr)) {
        bitmap->Release();
        return false;
    }

    WICRect lock_rect = { 0, 0, w, h };
    IWICBitmapLock* lock = nullptr;
    hr = bitmap->Lock(&lock_rect, WICBitmapLockRead, &lock);
    if (FAILED(hr) || !lock) {
        bitmap->Release();
        return false;
    }

    UINT src_stride = 0;
    UINT src_size = 0;
    BYTE* src_bits = nullptr;
    lock->GetStride(&src_stride);
    lock->GetDataPointer(&src_size, &src_bits);
    if (!src_bits || src_stride == 0) {
        lock->Release();
        bitmap->Release();
        return false;
    }

    HDC screen_dc = GetDC(nullptr);
    HDC mem_dc = CreateCompatibleDC(screen_dc);
    BITMAPINFO bmi = {};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = w;
    bmi.bmiHeader.biHeight = -h;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;
    void* dib_bits = nullptr;
    HBITMAP dib = CreateDIBSection(screen_dc, &bmi, DIB_RGB_COLORS, &dib_bits, nullptr, 0);
    bool ok = false;
    if (mem_dc && dib && dib_bits) {
        HGDIOBJ old = SelectObject(mem_dc, dib);
        int dst_stride = w * 4;
        int copy_stride = (std::min)(dst_stride, (int)src_stride);
        BYTE* dst_bits = (BYTE*)dib_bits;
        std::memset(dst_bits, 0, (size_t)dst_stride * (size_t)h);
        for (int y = 0; y < h; ++y) {
            std::memcpy(dst_bits + y * dst_stride, src_bits + y * src_stride, copy_stride);
        }
        apply_rounded_alpha_mask(dst_bits, w, h, dst_stride, radius);

        RECT wr{};
        GetWindowRect(st->hwnd, &wr);
        POINT dst = { wr.left, wr.top };
        POINT src = { 0, 0 };
        SIZE size = { w, h };
        BLENDFUNCTION blend = { AC_SRC_OVER, 0, 255, AC_SRC_ALPHA };
        ok = UpdateLayeredWindow(st->hwnd, screen_dc, &dst, &size, mem_dc, &src,
                                 0, &blend, ULW_ALPHA) != FALSE;
        SelectObject(mem_dc, old);
    }

    if (dib) DeleteObject(dib);
    if (mem_dc) DeleteDC(mem_dc);
    if (screen_dc) ReleaseDC(nullptr, screen_dc);
    lock->Release();
    bitmap->Release();
    return ok;
}

static bool render_layered_window_or_retry(WindowState* st, bool allow_region_fallback) {
    if (!st || !st->rounded_layered_active) return false;
    if (render_layered_window(st)) {
        st->rounded_layered_failures = 0;
        return true;
    }

    ++st->rounded_layered_failures;
    if (allow_region_fallback && st->rounded_layered_failures >= 3) {
        int radius = st->rounded_layered_radius_px;
        set_layered_window(st->hwnd, false);
        st->rounded_layered_radius_px = radius;
        if (apply_rounded_window_region(st)) {
            InvalidateRect(st->hwnd, nullptr, FALSE);
        }
        return false;
    }

    if (IsWindowVisible(st->hwnd)) {
        PostMessageW(st->hwnd, WM_NEWEMOJI_RENDER_LAYERED, 0, 0);
    }
    return false;
}

void apply_window_rounded_corners(WindowState* st) {
    if (!st || !st->hwnd || !IsWindow(st->hwnd)) return;

    bool should_round = st->rounded_corners && st->rounded_corner_radius > 0 && !IsZoomed(st->hwnd);
    st->rounded_region_active = false;
    st->rounded_region_radius_px = 0;
    st->rounded_layered_active = false;
    st->rounded_layered_radius_px = 0;
    st->rounded_layered_failures = 0;
    if (should_round && apply_dwm_corner_preference(st->hwnd, true, st->rounded_corner_radius)) {
        set_layered_window(st->hwnd, false);
        clear_window_region(st->hwnd, true);
        return;
    }
    if (!should_round) apply_dwm_corner_preference(st->hwnd, false, 0);
    if (!should_round) {
        set_layered_window(st->hwnd, false);
        clear_window_region(st->hwnd, true);
        return;
    }

    RECT wr{};
    if (!GetWindowRect(st->hwnd, &wr)) return;
    int width = wr.right - wr.left;
    int height = wr.bottom - wr.top;
    if (width <= 0 || height <= 0) return;

    int radius = scaled_window_radius(st, width, height);
    st->rounded_layered_active = radius > 0;
    st->rounded_layered_radius_px = radius;
    st->rounded_layered_failures = 0;
    set_layered_window(st->hwnd, st->rounded_layered_active);
    clear_window_region(st->hwnd, true);
    if (st->rounded_layered_active && IsWindowVisible(st->hwnd)) {
        render_layered_window_or_retry(st, true);
    }
    if (!st->rounded_layered_active) {
        InvalidateRect(st->hwnd, nullptr, FALSE);
    }
}

static std::wstring get_ime_string(HWND hwnd, HIMC imc, DWORD index) {
    LONG bytes = ImmGetCompositionStringW(imc, index, nullptr, 0);
    if (bytes <= 0) return L"";
    std::wstring value((size_t)bytes / sizeof(wchar_t), L'\0');
    ImmGetCompositionStringW(imc, index, value.data(), bytes);
    return value;
}

// ── Hit test helpers ─────────────────────────────────────────────────

void apply_window_frame_flags(WindowState* st, int flags, bool explicit_flags) {
    if (!st) return;
    st->frame_flags = flags;
    st->frame_flags_explicit = explicit_flags;
    st->titlebar_visible = (flags & EU_WINDOW_FRAME_HIDE_TITLEBAR) == 0;
    st->rounded_corners = (flags & EU_WINDOW_FRAME_ROUNDED) != 0;
    if (st->rounded_corners) {
        if (st->rounded_corner_radius <= 0) st->rounded_corner_radius = 8;
    }
    apply_window_rounded_corners(st);
    if (st->element_tree) st->element_tree->layout();
    if (st->hwnd) InvalidateRect(st->hwnd, nullptr, FALSE);
}

static bool frame_resize_enabled(WindowState* st) {
    if (!st) return true;
    if (!st->frame_flags_explicit) return true;
    if (st->frame_flags == EU_WINDOW_FRAME_DEFAULT) return true;
    return (st->frame_flags & EU_WINDOW_FRAME_RESIZABLE) != 0;
}

static int get_resize_dir(HWND hwnd, int x, int y) {
    WindowState* st = window_state(hwnd);
    if (!frame_resize_enabled(st)) return 0;
    RECT rc;
    GetClientRectForWindowDpi(hwnd, &rc);
    float scale = st ? st->dpi_scale : 1.0f;
    int left = st ? (int)std::lround(st->resize_border_left * scale) : 6;
    int top = st ? (int)std::lround(st->resize_border_top * scale) : 6;
    int right = st ? (int)std::lround(st->resize_border_right * scale) : 6;
    int bottom = st ? (int)std::lround(st->resize_border_bottom * scale) : 6;
    if (left < 0) left = 0; if (top < 0) top = 0; if (right < 0) right = 0; if (bottom < 0) bottom = 0;
    if (x < left && y < top)                         return HTTOPLEFT;
    if (x > rc.right - right && y < top)              return HTTOPRIGHT;
    if (x < left && y > rc.bottom - bottom)           return HTBOTTOMLEFT;
    if (x > rc.right - right && y > rc.bottom - bottom) return HTBOTTOMRIGHT;
    if (x < left)                                     return HTLEFT;
    if (x > rc.right - right)                         return HTRIGHT;
    if (y < top)                                      return HTTOP;
    if (y > rc.bottom - bottom)                       return HTBOTTOM;
    return 0;
}

static TitleBar* get_title_bar(WindowState* st) {
    if (!st || !st->element_tree || !st->element_tree->root()) return nullptr;
    auto& children = st->element_tree->root()->children;
    if (children.empty()) return nullptr;
    return dynamic_cast<TitleBar*>(children.front().get());
}

static bool is_titlebar_drag_point(WindowState* st, int x, int y) {
    if (st) {
        for (const auto& r : st->no_drag_regions) {
            if (r.contains(x, y)) return false;
        }
    }
    if (st && !st->drag_regions.empty()) {
        for (const auto& r : st->drag_regions) {
            if (r.contains(x, y)) return true;
        }
    }
    TitleBar* tb = get_title_bar(st);
    if (!tb || !tb->visible || !tb->enabled) return false;
    if (!tb->bounds.contains(x, y)) return false;

    int lx = x - tb->bounds.x;
    int ly = y - tb->bounds.y;
    return !tb->hit_test_button(lx, ly);
}

static bool is_no_drag_point(WindowState* st, int x, int y) {
    if (!st) return false;
    for (const auto& r : st->no_drag_regions) {
        if (r.contains(x, y)) return true;
    }
    return false;
}

static bool is_titlebar_button_point(WindowState* st, int x, int y) {
    TitleBar* tb = get_title_bar(st);
    if (!tb || !tb->visible || !tb->enabled) return false;
    if (!tb->bounds.contains(x, y)) return false;

    int lx = x - tb->bounds.x;
    int ly = y - tb->bounds.y;
    return tb->hit_test_button(lx, ly);
}

static bool is_modal_overlay_point(WindowState* st, int x, int y) {
    return st && st->element_tree && st->element_tree->has_modal_overlay_at(x, y);
}

static Upload* upload_from_hit(Element* hit) {
    while (hit) {
        if (auto* upload = dynamic_cast<Upload*>(hit)) return upload;
        hit = hit->parent;
    }
    return nullptr;
}

static Upload* find_drop_upload_at(Element* el, int x, int y) {
    if (!el || !el->visible || !el->enabled) return nullptr;
    int lx = x - el->bounds.x;
    int ly = y - el->bounds.y;
    if (el->parent && (lx < 0 || ly < 0 || lx >= el->bounds.w || ly >= el->bounds.h)) return nullptr;

    for (auto it = el->children.rbegin(); it != el->children.rend(); ++it) {
        if (auto* upload = find_drop_upload_at(it->get(), lx, ly)) return upload;
    }
    auto* upload = dynamic_cast<Upload*>(el);
    if (upload && upload->wants_dropped_files() && lx >= 0 && ly >= 0 &&
        lx < upload->bounds.w && ly < upload->bounds.h) {
        return upload;
    }
    return nullptr;
}

static void handle_drop_files(HWND hwnd, HDROP drop) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree || !drop) {
        if (drop) DragFinish(drop);
        return;
    }

    POINT pt = {};
    DragQueryPoint(drop, &pt);
    Upload* upload = st->element_tree->root() ? find_drop_upload_at(st->element_tree->root(), pt.x, pt.y) : nullptr;
    if (!upload) {
        Element* hit = st->element_tree->root() ? st->element_tree->root()->hit_test(pt.x, pt.y) : nullptr;
        upload = upload_from_hit(hit);
    }
    if (!upload || !upload->wants_dropped_files()) {
        DragFinish(drop);
        return;
    }

    std::vector<std::wstring> files;
    UINT count = DragQueryFileW(drop, 0xFFFFFFFF, nullptr, 0);
    for (UINT i = 0; i < count; ++i) {
        UINT len = DragQueryFileW(drop, i, nullptr, 0);
        if (len == 0) continue;
        std::wstring path((size_t)len + 1, L'\0');
        DragQueryFileW(drop, i, path.data(), len + 1);
        path.resize(len);
        files.push_back(path);
    }
    DragFinish(drop);

    if (!files.empty()) {
        upload->accept_dropped_files(files);
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

// ── Window class registration ────────────────────────────────────────

void register_window_class() {
    static bool done = false;
    if (done) return;
    done = true;

    WNDCLASSEXW wc = {};
    wc.cbSize        = sizeof(wc);
    wc.style         = CS_DBLCLKS;
    wc.lpfnWndProc   = [](HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) -> LRESULT {
        ScopedWindowDpiAwareness dpi(hwnd);
        WindowState* st = window_state(hwnd);
        switch (msg) {
        case WM_CREATE: {
            st = new WindowState();
            st->hwnd = hwnd;
            WindowCreateParams* pending = g_pending_create_params;
            if (pending) {
                st->titlebar_color = pending->titlebar_color;
                st->frame_flags = pending->frame_flags;
                st->frame_flags_explicit = true;
            } else {
                st->titlebar_color = static_cast<Color>((UINT_PTR)((CREATESTRUCTW*)lp)->lpCreateParams & 0xFFFFFFFF);
            }
            st->dpi_scale = GetDpiForWindow(hwnd) / 96.0f;
            st->last_dpi = (float)GetDpiForWindow(hwnd);
            g_windows[hwnd] = st;
            if (pending) apply_window_frame_flags(st, pending->frame_flags, true);
            ensure_factories();
            init_themes();
            set_window_theme_mode(hwnd, st->theme_mode);
            recreate_render_target(st);
            st->element_tree = new ElementTree(hwnd, st->dpi_scale);
            st->element_tree->layout();
            DragAcceptFiles(hwnd, TRUE);
            ChangeWindowMessageFilterEx(hwnd, WM_DROPFILES, MSGFLT_ALLOW, nullptr);
            ChangeWindowMessageFilterEx(hwnd, WM_COPYDATA, MSGFLT_ALLOW, nullptr);
            ChangeWindowMessageFilterEx(hwnd, 0x0049, MSGFLT_ALLOW, nullptr);
            return 0;
        }
        case WM_SHOWWINDOW:
            if (wp && st && st->rounded_layered_active) {
                PostMessageW(hwnd, WM_NEWEMOJI_RENDER_LAYERED, 0, 0);
            }
            return 0;

        case WM_NEWEMOJI_RENDER_LAYERED:
            if (st && st->rounded_layered_active) {
                render_layered_window_or_retry(st, true);
            }
            return 0;

        case WM_SIZE: {
            UINT w = LOWORD(lp), h = HIWORD(lp);
            if (st && st->render_target && w > 0 && h > 0 && wp != SIZE_MINIMIZED) {
                st->render_target->Resize(D2D1::SizeU(w, h));
                if (st->element_tree) st->element_tree->layout();
                apply_window_rounded_corners(st);
                InvalidateRect(hwnd, nullptr, FALSE);
            }
            if (st && st->resize_cb && wp != SIZE_MINIMIZED) {
                RECT rc;
                GetClientRectForWindowDpi(hwnd, &rc);
                st->resize_cb(hwnd, rc.right - rc.left, rc.bottom - rc.top);
            }
            return 0;
        }

        case WM_DPICHANGED: {
            if (st) {
                UINT newDpi = HIWORD(wp);
                st->dpi_scale = newDpi / 96.0f;
                st->last_dpi = (float)newDpi;
                if (st->element_tree) st->element_tree->set_dpi_scale(st->dpi_scale);
                RECT* rc = reinterpret_cast<RECT*>(lp);
                SetWindowPos(hwnd, nullptr, rc->left, rc->top,
                             rc->right - rc->left, rc->bottom - rc->top,
                             SWP_NOZORDER | SWP_NOACTIVATE);
                recreate_render_target(st);
                if (st->element_tree) st->element_tree->layout();
                apply_window_rounded_corners(st);
                InvalidateRect(hwnd, nullptr, FALSE);
            }
            return 0;
        }
        // ── DPI polling (fallback when host blocks per-monitor awareness) ──
        case WM_WINDOWPOSCHANGED: {
            LRESULT r = DefWindowProcW(hwnd, msg, wp, lp);
            if (st && !st->pm_aware) {
                float cur = (float)GetDpiForWindow(hwnd);
                if (cur != st->last_dpi && cur > 0) {
                    st->last_dpi = cur;
                    st->dpi_scale = cur / 96.0f;
                    if (st->element_tree) st->element_tree->set_dpi_scale(st->dpi_scale);
                    recreate_render_target(st);
                    if (st->element_tree) st->element_tree->layout();
                    apply_window_rounded_corners(st);
                    InvalidateRect(hwnd, nullptr, FALSE);
                }
            }
            return r;
        }
        case WM_ERASEBKGND:
            return 1;

        case WM_DROPFILES:
            handle_drop_files(hwnd, reinterpret_cast<HDROP>(wp));
            return 0;

        case WM_GETMINMAXINFO: {
            auto* mmi = reinterpret_cast<MINMAXINFO*>(lp);
            HMONITOR mon = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST);
            MONITORINFO mi = {};
            mi.cbSize = sizeof(mi);
            if (GetMonitorInfoW(mon, &mi)) {
                mmi->ptMaxPosition.x = mi.rcWork.left - mi.rcMonitor.left;
                mmi->ptMaxPosition.y = mi.rcWork.top - mi.rcMonitor.top;
                mmi->ptMaxSize.x = mi.rcWork.right - mi.rcWork.left;
                mmi->ptMaxSize.y = mi.rcWork.bottom - mi.rcWork.top;
                mmi->ptMaxTrackSize = mmi->ptMaxSize;
            }
            return 0;
        }

        // ── Hit test: resize cursor only; D2D title bar stays in client area ──
        case WM_SETCURSOR: {
            if (LOWORD(lp) == HTCLIENT && st && st->element_tree && st->element_tree->root()) {
                POINT pt{};
                if (GetCursorPos(&pt)) {
                    ScreenToClient(hwnd, &pt);
                    Element* hit = st->element_tree->root()->hit_test(pt.x, pt.y);
                    if (auto* mb = dynamic_cast<MessageBoxElement*>(hit)) {
                        int ox = 0;
                        int oy = 0;
                        mb->get_absolute_pos(ox, oy);
                        if (mb->wants_text_cursor_at(pt.x - ox, pt.y - oy)) {
                            SetCursor(LoadCursorW(nullptr, IDC_IBEAM));
                            return TRUE;
                        }
                    }
                }
            }
            break;
        }

        case WM_NCHITTEST: {
            POINT pt = { GET_X_LPARAM(lp), GET_Y_LPARAM(lp) };
            ScreenToClient(hwnd, &pt);
            if (!point_inside_window_shape(st, pt.x, pt.y)) return HTTRANSPARENT;
            if (is_modal_overlay_point(st, pt.x, pt.y)) return HTCLIENT;
            if (is_titlebar_button_point(st, pt.x, pt.y)) return HTCLIENT;
            if (is_no_drag_point(st, pt.x, pt.y)) return HTCLIENT;
            int dir = get_resize_dir(hwnd, pt.x, pt.y);
            if (dir) return dir;
            return HTCLIENT;
        }

        // ── Paint ──
        case WM_PAINT: {
            PAINTSTRUCT ps;
            BeginPaint(hwnd, &ps);
            if (st && st->rounded_layered_active) {
                render_layered_window_or_retry(st, true);
                EndPaint(hwnd, &ps);
                return 0;
            }
            if (st && st->render_target) {
                st->render_target->BeginDraw();
                const Theme* t = theme_for_window(hwnd);
                st->render_target->Clear(D2D1::ColorF(
                    ((t->panel_bg >> 16) & 0xFF) / 255.0f,
                    ((t->panel_bg >> 8) & 0xFF) / 255.0f,
                    (t->panel_bg & 0xFF) / 255.0f,
                    ((t->panel_bg >> 24) & 0xFF) / 255.0f));
                if (st->element_tree && g_dwrite_factory) {
                    RenderContext ctx(st->render_target, g_dwrite_factory);
                    st->element_tree->paint(ctx);
                }
                HRESULT hr = st->render_target->EndDraw();
                if (hr == D2DERR_RECREATE_TARGET) {
                    recreate_render_target(st);
                    InvalidateRect(hwnd, nullptr, FALSE);
                }
            }
            EndPaint(hwnd, &ps);
            return 0;
        }

        case WM_ENTERSIZEMOVE: if (st) st->in_live_resize = true; return 0;
        case WM_EXITSIZEMOVE:
            if (st) {
                st->in_live_resize = false;
                RECT rc;
                GetClientRectForWindowDpi(hwnd, &rc);
                if (st->render_target) st->render_target->Resize(
                    D2D1::SizeU(rc.right - rc.left, rc.bottom - rc.top));
                if (st->element_tree) st->element_tree->layout();
                apply_window_rounded_corners(st);
                InvalidateRect(hwnd, nullptr, FALSE);
            }
            return 0;

        // ── Manual resize ───────────────────────────────────────────
        case WM_LBUTTONDOWN: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            bool modal_point = is_modal_overlay_point(st, x, y);
            bool no_drag_point = is_no_drag_point(st, x, y);
            int dir = get_resize_dir(hwnd, x, y);
            if (!modal_point && !no_drag_point && dir && st) {
                st->sizing = true;
                st->size_dir = dir;
                st->size_start.x = x; st->size_start.y = y;
                GetWindowRect(hwnd, &st->size_rect);
                SetCapture(hwnd);
                return 0;
            }
            if (!modal_point && !no_drag_point && is_titlebar_drag_point(st, x, y)) {
                SetFocus(hwnd);
                ReleaseCapture();
                SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0);
                return 0;
            }
            if (st && st->element_tree) { SetFocus(hwnd); st->element_tree->dispatch_lbutton_down(x, y); }
            return 0;
        }
        case WM_LBUTTONDBLCLK: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            if (!is_modal_overlay_point(st, x, y) && is_titlebar_drag_point(st, x, y)) {
                ShowWindow(hwnd, IsZoomed(hwnd) ? SW_RESTORE : SW_MAXIMIZE);
            }
            return 0;
        }
        case WM_MOUSEMOVE: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            if (st && st->sizing) {
                int dx = x - st->size_start.x, dy = y - st->size_start.y;
                RECT r = st->size_rect;
                int dir = st->size_dir;
                if (dir == HTLEFT || dir == HTTOPLEFT || dir == HTBOTTOMLEFT)       { r.left   += dx; }
                if (dir == HTRIGHT || dir == HTTOPRIGHT || dir == HTBOTTOMRIGHT)    { r.right  += dx; }
                if (dir == HTTOP || dir == HTTOPLEFT || dir == HTTOPRIGHT)          { r.top    += dy; }
                if (dir == HTBOTTOM || dir == HTBOTTOMLEFT || dir == HTBOTTOMRIGHT) { r.bottom += dy; }
                int mw = 100, mh = 100;  // minimum window size
                if (r.right - r.left < mw) { if (dir & 1) r.left = r.right - mw; else r.right = r.left + mw; }
                if (r.bottom - r.top < mh) { if (dir & 4) r.top = r.bottom - mh; else r.bottom = r.top + mh; }
                SetWindowPos(hwnd, nullptr, r.left, r.top, r.right - r.left, r.bottom - r.top, SWP_NOZORDER);
                return 0;
            }
            if (st && st->element_tree) st->element_tree->dispatch_mouse_move(x, y);
            return 0;
        }
        case WM_MOUSEWHEEL: {
            POINT pt = { GET_X_LPARAM(lp), GET_Y_LPARAM(lp) };
            ScreenToClient(hwnd, &pt);
            if (st && st->element_tree) {
                st->element_tree->dispatch_mouse_wheel(pt.x, pt.y, GET_WHEEL_DELTA_WPARAM(wp));
            }
            return 0;
        }
        case WM_TIMER:
            if (auto it = g_carousel_timer_map.find((UINT_PTR)wp); it != g_carousel_timer_map.end()) {
                if (it->second) it->second->tick(33);
                return 0;
            }
            if (auto it = g_notification_timer_map.find((UINT_PTR)wp); it != g_notification_timer_map.end()) {
                if (it->second) it->second->tick(50);
                return 0;
            }
            if (auto it = g_message_timer_map.find((UINT_PTR)wp); it != g_message_timer_map.end()) {
                if (it->second) it->second->tick(50);
                return 0;
            }
            if (auto it = g_messagebox_timer_map.find((UINT_PTR)wp); it != g_messagebox_timer_map.end()) {
                if (it->second) it->second->tick(50);
                return 0;
            }
            if (auto it = g_loading_timer_map.find((UINT_PTR)wp); it != g_loading_timer_map.end()) {
                if (it->second) it->second->tick(33);
                return 0;
            }
            if (auto it = g_skeleton_timer_map.find((UINT_PTR)wp); it != g_skeleton_timer_map.end()) {
                if (it->second) it->second->tick(16);
                return 0;
            }
            if (auto it = g_button_timer_map.find((UINT_PTR)wp); it != g_button_timer_map.end()) {
                if (it->second) it->second->tick(33);
                return 0;
            }
            if (auto it = g_statistic_timer_map.find((UINT_PTR)wp); it != g_statistic_timer_map.end()) {
                if (it->second) it->second->tick(200);
                return 0;
            }
            if (auto it = g_drawer_timer_map.find((UINT_PTR)wp); it != g_drawer_timer_map.end()) {
                if (it->second) it->second->tick(16);
                return 0;
            }
            if (auto it = g_tooltip_timer_map.find((UINT_PTR)wp); it != g_tooltip_timer_map.end()) {
                if (it->second) it->second->tick(33);
                return 0;
            }
            InvalidateRect(hwnd, nullptr, FALSE);
            return 0;
        case WM_LBUTTONUP: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            if (st && st->sizing) { st->sizing = false; ReleaseCapture(); return 0; }
            if (st && st->element_tree) st->element_tree->dispatch_lbutton_up(x, y);
            return 0;
        }
        case WM_RBUTTONDOWN: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            if (st && st->element_tree) { SetFocus(hwnd); st->element_tree->dispatch_rbutton_down(x, y); }
            return 0;
        }
        case WM_RBUTTONUP: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            if (st && st->element_tree) st->element_tree->dispatch_rbutton_up(x, y);
            return 0;
        }
        // ── Keyboard ────────────────────────────────────────────────
        case WM_KEYDOWN: {
            if (st && st->element_tree) {
                int mods = 0;
                if (GetKeyState(VK_SHIFT) & 0x8000) mods |= KeyMod::Shift;
                if (GetKeyState(VK_CONTROL) & 0x8000) mods |= KeyMod::Control;
                if (GetKeyState(VK_MENU) & 0x8000) mods |= KeyMod::Alt;
                st->element_tree->dispatch_key_down((int)wp, mods);
            }
            return 0;
        }
        case WM_KEYUP:
            if (st && st->element_tree) st->element_tree->dispatch_key_up((int)wp, 0);
            return 0;
        case WM_CHAR:
            if (st && st->element_tree) st->element_tree->dispatch_char((wchar_t)wp);
            return 0;
        case WM_IME_STARTCOMPOSITION: {
            if (st && st->element_tree) {
                if (auto* edit = dynamic_cast<EditBox*>(st->element_tree->focused())) {
                    edit->set_composition_text(L"");
                }
            }
            return 0;
        }
        case WM_IME_COMPOSITION: {
            if (st && st->element_tree) {
                if (auto* edit = dynamic_cast<EditBox*>(st->element_tree->focused())) {
                    HIMC imc = ImmGetContext(hwnd);
                    if (imc) {
                        if (lp & GCS_RESULTSTR) {
                            edit->commit_text(get_ime_string(hwnd, imc, GCS_RESULTSTR));
                        }
                        if (lp & GCS_COMPSTR) {
                            edit->set_composition_text(get_ime_string(hwnd, imc, GCS_COMPSTR));
                        }
                        ImmReleaseContext(hwnd, imc);
                    }
                } else if (auto* input = dynamic_cast<Input*>(st->element_tree->focused())) {
                    HIMC imc = ImmGetContext(hwnd);
                    if (imc) {
                        if (lp & GCS_RESULTSTR) {
                            input->commit_text(get_ime_string(hwnd, imc, GCS_RESULTSTR));
                        }
                        ImmReleaseContext(hwnd, imc);
                    }
                } else if (auto* input_tag = dynamic_cast<InputTag*>(st->element_tree->focused())) {
                    HIMC imc = ImmGetContext(hwnd);
                    if (imc) {
                        if (lp & GCS_RESULTSTR) {
                            input_tag->commit_text(get_ime_string(hwnd, imc, GCS_RESULTSTR));
                        }
                        ImmReleaseContext(hwnd, imc);
                    }
                } else if (auto* mentions = dynamic_cast<Mentions*>(st->element_tree->focused())) {
                    HIMC imc = ImmGetContext(hwnd);
                    if (imc) {
                        if (lp & GCS_RESULTSTR) {
                            mentions->commit_text(get_ime_string(hwnd, imc, GCS_RESULTSTR));
                        }
                        ImmReleaseContext(hwnd, imc);
                    }
                }
            }
            return 0;
        }
        case WM_IME_ENDCOMPOSITION: {
            if (st && st->element_tree) {
                if (auto* edit = dynamic_cast<EditBox*>(st->element_tree->focused())) {
                    edit->end_composition();
                }
            }
            return 0;
        }
        // Blink timer
        case WM_USER + 100: {
            auto it = g_blink_map.find((UINT_PTR)lp);
            if (it != g_blink_map.end()) { it->second->m_cursor_on = !it->second->m_cursor_on; it->second->invalidate(); }
            return 0;
        }
        case WM_USER + 110: {
            if (st && st->element_tree) {
                int messagebox_id = (int)wp;
                int result = (int)lp;
                Element* el = st->element_tree->find_by_id(messagebox_id);
                if (auto* mb = dynamic_cast<MessageBoxElement*>(el)) {
                    MessageBoxResultCallback cb = mb->result_cb;
                    MessageBoxExCallback ex_cb = mb->result_ex_cb;
                    std::string value = wide_to_utf8(mb->input_value);
                    st->element_tree->remove_child(mb);
                    InvalidateRect(hwnd, nullptr, FALSE);
                    if (cb) cb(messagebox_id, result);
                    if (ex_cb) {
                        ex_cb(messagebox_id, result,
                              reinterpret_cast<const unsigned char*>(value.data()),
                              (int)value.size());
                    }
                }
            }
            return 0;
        }
        // Cleanup
        case WM_CLOSE:
            if (st && st->close_cb) {
                st->close_cb(hwnd);
                if (!IsWindow(hwnd)) return 0;
            }
            DestroyWindow(hwnd); return 0;
        case WM_DESTROY:
            if (st) {
                DragAcceptFiles(hwnd, FALSE);
                delete st->element_tree; st->element_tree = nullptr;
                if (st->render_target) { st->render_target->Release(); st->render_target = nullptr; }
                if (st->window_icon_big) DestroyIcon(st->window_icon_big);
                if (st->window_icon_small && st->window_icon_small != st->window_icon_big) DestroyIcon(st->window_icon_small);
                g_windows.erase(hwnd); delete st;
            }
            PostQuitMessage(0); return 0;
        }
        return DefWindowProcW(hwnd, msg, wp, lp);
    };
    wc.hInstance     = g_module;
    wc.hCursor       = LoadCursorW(nullptr, IDC_ARROW);
    wc.hbrBackground = nullptr;
    wc.lpszClassName = kWindowClass;
    RegisterClassExW(&wc);
}

// ── Recreate render target ───────────────────────────────────────────

void recreate_render_target(WindowState* st) {
    if (st->render_target) { st->render_target->Release(); st->render_target = nullptr; }
    if (!g_d2d_factory) return;
    RECT rc;
    GetClientRectForWindowDpi(st->hwnd, &rc);
    D2D1_SIZE_U size = D2D1::SizeU(rc.right - rc.left, rc.bottom - rc.top);
    if (size.width < 1) size.width = 1;
    if (size.height < 1) size.height = 1;
    D2D1_RENDER_TARGET_PROPERTIES props = D2D1::RenderTargetProperties(
        D2D1_RENDER_TARGET_TYPE_DEFAULT,
        D2D1::PixelFormat(DXGI_FORMAT_B8G8R8A8_UNORM, D2D1_ALPHA_MODE_PREMULTIPLIED));
    D2D1_HWND_RENDER_TARGET_PROPERTIES hwnd_props = D2D1::HwndRenderTargetProperties(st->hwnd, size);
    HRESULT hr = g_d2d_factory->CreateHwndRenderTarget(props, hwnd_props, &st->render_target);
    if (SUCCEEDED(hr) && st->render_target) st->render_target->SetDpi(96.0f, 96.0f);
}
