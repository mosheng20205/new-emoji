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
#include "element_inputtag.h"
#include "element_mentions.h"
#include "element_upload.h"
#include "element_message.h"
#include "element_messagebox.h"
#include "element_carousel.h"
#include "element_notification.h"
#include "element_loading.h"
#include "element_drawer.h"
#include "element_tooltip.h"
#include "element_statistic.h"
#include "theme.h"
#include "dpi_context.h"
#include "utf8_helpers.h"
#include <map>
#include <vector>

extern HMODULE g_module;

std::map<HWND, WindowState*> g_windows;
static const wchar_t* kWindowClass = L"NewEmojiWindow";
extern std::map<UINT_PTR, EditBox*> g_blink_map;
extern std::map<UINT_PTR, Button*> g_button_timer_map;
extern std::map<UINT_PTR, Statistic*> g_statistic_timer_map;
extern std::map<UINT_PTR, Carousel*> g_carousel_timer_map;
extern std::map<UINT_PTR, Message*> g_message_timer_map;
extern std::map<UINT_PTR, MessageBoxElement*> g_messagebox_timer_map;
extern std::map<UINT_PTR, Notification*> g_notification_timer_map;
extern std::map<UINT_PTR, Loading*> g_loading_timer_map;
extern std::map<UINT_PTR, Drawer*> g_drawer_timer_map;
extern std::map<UINT_PTR, Tooltip*> g_tooltip_timer_map;

WindowState* window_state(HWND hwnd) {
    auto it = g_windows.find(hwnd);
    return it != g_windows.end() ? it->second : nullptr;
}

static std::wstring get_ime_string(HWND hwnd, HIMC imc, DWORD index) {
    LONG bytes = ImmGetCompositionStringW(imc, index, nullptr, 0);
    if (bytes <= 0) return L"";
    std::wstring value((size_t)bytes / sizeof(wchar_t), L'\0');
    ImmGetCompositionStringW(imc, index, value.data(), bytes);
    return value;
}

// ── Hit test helpers ─────────────────────────────────────────────────

static int get_resize_dir(HWND hwnd, int x, int y) {
    RECT rc;
    GetClientRectForWindowDpi(hwnd, &rc);
    int b = 6;
    if (x < b && y < b)                         return HTTOPLEFT;
    if (x > rc.right - b && y < b)              return HTTOPRIGHT;
    if (x < b && y > rc.bottom - b)             return HTBOTTOMLEFT;
    if (x > rc.right - b && y > rc.bottom - b)  return HTBOTTOMRIGHT;
    if (x < b)                                  return HTLEFT;
    if (x > rc.right - b)                       return HTRIGHT;
    if (y < b)                                  return HTTOP;
    if (y > rc.bottom - b)                      return HTBOTTOM;
    return 0;
}

static TitleBar* get_title_bar(WindowState* st) {
    if (!st || !st->element_tree || !st->element_tree->root()) return nullptr;
    auto& children = st->element_tree->root()->children;
    if (children.empty()) return nullptr;
    return dynamic_cast<TitleBar*>(children.front().get());
}

static bool is_titlebar_drag_point(WindowState* st, int x, int y) {
    TitleBar* tb = get_title_bar(st);
    if (!tb || !tb->visible || !tb->enabled) return false;
    if (!tb->bounds.contains(x, y)) return false;

    int lx = x - tb->bounds.x;
    int ly = y - tb->bounds.y;
    return !tb->hit_test_button(lx, ly);
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
            st->titlebar_color = static_cast<Color>((UINT_PTR)((CREATESTRUCTW*)lp)->lpCreateParams & 0xFFFFFFFF);
            st->dpi_scale = GetDpiForWindow(hwnd) / 96.0f;
            st->last_dpi = (float)GetDpiForWindow(hwnd);
            g_windows[hwnd] = st;
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
        case WM_SIZE: {
            UINT w = LOWORD(lp), h = HIWORD(lp);
            if (st && st->render_target && w > 0 && h > 0 && wp != SIZE_MINIMIZED) {
                st->render_target->Resize(D2D1::SizeU(w, h));
                if (st->element_tree) st->element_tree->layout();
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
            if (is_modal_overlay_point(st, pt.x, pt.y)) return HTCLIENT;
            if (is_titlebar_button_point(st, pt.x, pt.y)) return HTCLIENT;
            int dir = get_resize_dir(hwnd, pt.x, pt.y);
            if (dir) return dir;
            return HTCLIENT;
        }

        // ── Paint ──
        case WM_PAINT: {
            PAINTSTRUCT ps;
            BeginPaint(hwnd, &ps);
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
                InvalidateRect(hwnd, nullptr, FALSE);
            }
            return 0;

        // ── Manual resize ───────────────────────────────────────────
        case WM_LBUTTONDOWN: {
            int x = GET_X_LPARAM(lp), y = GET_Y_LPARAM(lp);
            bool modal_point = is_modal_overlay_point(st, x, y);
            int dir = get_resize_dir(hwnd, x, y);
            if (!modal_point && dir && st) {
                st->sizing = true;
                st->size_dir = dir;
                st->size_start.x = x; st->size_start.y = y;
                GetWindowRect(hwnd, &st->size_rect);
                SetCapture(hwnd);
                return 0;
            }
            if (!modal_point && is_titlebar_drag_point(st, x, y)) {
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
            if (auto it = g_button_timer_map.find((UINT_PTR)wp); it != g_button_timer_map.end()) {
                if (it->second) it->second->tick(33);
                return 0;
            }
            if (auto it = g_statistic_timer_map.find((UINT_PTR)wp); it != g_statistic_timer_map.end()) {
                if (it->second) it->second->tick(200);
                return 0;
            }
            if (auto it = g_drawer_timer_map.find((UINT_PTR)wp); it != g_drawer_timer_map.end()) {
                if (it->second) it->second->tick(33);
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
