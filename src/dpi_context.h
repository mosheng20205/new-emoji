#pragma once
#include <windows.h>

class ScopedWindowDpiAwareness {
public:
    explicit ScopedWindowDpiAwareness(HWND hwnd) {
        if (!hwnd || !IsWindow(hwnd)) return;
        DPI_AWARENESS_CONTEXT ctx = GetWindowDpiAwarenessContext(hwnd);
        if (ctx) m_old = SetThreadDpiAwarenessContext(ctx);
    }

    ~ScopedWindowDpiAwareness() {
        if (m_old) SetThreadDpiAwarenessContext(m_old);
    }

    ScopedWindowDpiAwareness(const ScopedWindowDpiAwareness&) = delete;
    ScopedWindowDpiAwareness& operator=(const ScopedWindowDpiAwareness&) = delete;

private:
    DPI_AWARENESS_CONTEXT m_old = nullptr;
};

inline BOOL GetClientRectForWindowDpi(HWND hwnd, RECT* rc) {
    ScopedWindowDpiAwareness dpi(hwnd);
    return GetClientRect(hwnd, rc);
}
