#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#include "element_image.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <memory>
#include <mutex>
#include <thread>
#include <unordered_map>
#include <winhttp.h>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static bool rect_contains(const D2D1_RECT_F& r, float x, float y) {
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static bool is_remote_source(const std::wstring& value) {
    return _wcsnicmp(value.c_str(), L"http://", 7) == 0
        || _wcsnicmp(value.c_str(), L"https://", 8) == 0;
}

struct RemoteImageEntry {
    std::mutex mutex;
    int status = 0; // 0 idle, 1 ready, 2 failed, 3 loading
    bool started = false;
    std::wstring cache_path;
    std::vector<HWND> hwnds;
};

static std::mutex g_remote_image_mutex;
static std::unordered_map<std::wstring, std::shared_ptr<RemoteImageEntry>> g_remote_images;

static void remember_hwnd(RemoteImageEntry& entry, HWND hwnd) {
    if (!hwnd) return;
    if (std::find(entry.hwnds.begin(), entry.hwnds.end(), hwnd) == entry.hwnds.end()) {
        entry.hwnds.push_back(hwnd);
    }
}

static std::string wide_to_utf8_narrow(const std::wstring& value) {
    if (value.empty()) return std::string();
    int len = WideCharToMultiByte(CP_UTF8, 0, value.c_str(), (int)value.size(), nullptr, 0, nullptr, nullptr);
    if (len <= 0) return std::string();
    std::string out((size_t)len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, value.c_str(), (int)value.size(), &out[0], len, nullptr, nullptr);
    return out;
}

static bool write_bytes_to_temp_file(const std::vector<unsigned char>& bytes, std::wstring& out_path) {
    if (bytes.empty()) return false;
    wchar_t temp_dir[MAX_PATH] = {};
    wchar_t temp_file[MAX_PATH] = {};
    if (GetTempPathW((DWORD)_countof(temp_dir), temp_dir) == 0) return false;
    if (GetTempFileNameW(temp_dir, L"eui", 0, temp_file) == 0) return false;
    HANDLE file = CreateFileW(temp_file, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS,
                              FILE_ATTRIBUTE_TEMPORARY, nullptr);
    if (file == INVALID_HANDLE_VALUE) {
        DeleteFileW(temp_file);
        return false;
    }
    DWORD written = 0;
    bool ok = WriteFile(file, bytes.data(), (DWORD)bytes.size(), &written, nullptr) && written == bytes.size();
    CloseHandle(file);
    if (ok) {
        out_path = temp_file;
    } else {
        DeleteFileW(temp_file);
    }
    return ok;
}

static bool download_http_to_temp_file(const std::wstring& host_w, INTERNET_PORT port,
                                       const std::wstring& object_path_w,
                                       std::wstring& out_path) {
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return false;

    std::string host = wide_to_utf8_narrow(host_w);
    std::string object_path = wide_to_utf8_narrow(object_path_w.empty() ? L"/" : object_path_w);
    std::string port_text = std::to_string((unsigned)port);
    addrinfo hints{};
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    addrinfo* results = nullptr;
    bool ok = false;
    SOCKET s = INVALID_SOCKET;
    if (getaddrinfo(host.c_str(), port_text.c_str(), &hints, &results) == 0) {
        for (addrinfo* it = results; it; it = it->ai_next) {
            s = socket(it->ai_family, it->ai_socktype, it->ai_protocol);
            if (s == INVALID_SOCKET) continue;
            DWORD timeout_ms = 10000;
            setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout_ms, sizeof(timeout_ms));
            setsockopt(s, SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout_ms, sizeof(timeout_ms));
            if (connect(s, it->ai_addr, (int)it->ai_addrlen) == 0) break;
            closesocket(s);
            s = INVALID_SOCKET;
        }
    }
    if (s != INVALID_SOCKET) {
        std::string host_header = host;
        if (port != INTERNET_DEFAULT_HTTP_PORT) host_header += ":" + port_text;
        std::string request = "GET " + object_path + " HTTP/1.1\r\n"
                            + "Host: " + host_header + "\r\n"
                            + "User-Agent: new_emoji/1.0\r\n"
                            + "Connection: close\r\n\r\n";
        int sent_total = 0;
        ok = true;
        while (ok && sent_total < (int)request.size()) {
            int sent = send(s, request.data() + sent_total, (int)request.size() - sent_total, 0);
            if (sent <= 0) ok = false;
            else sent_total += sent;
        }
        std::vector<unsigned char> response;
        char buffer[8192];
        while (ok) {
            int got = recv(s, buffer, (int)sizeof(buffer), 0);
            if (got == 0) break;
            if (got < 0) {
                ok = false;
                break;
            }
            response.insert(response.end(), buffer, buffer + got);
        }
        closesocket(s);

        if (ok) {
            const char marker[] = "\r\n\r\n";
            auto header_end = std::search(response.begin(), response.end(), marker, marker + 4);
            if (header_end != response.end()) {
                std::string header(response.begin(), header_end);
                bool status_ok = header.find(" 200 ") != std::string::npos
                              || header.find(" 201 ") != std::string::npos
                              || header.find(" 202 ") != std::string::npos
                              || header.find(" 204 ") != std::string::npos
                              || header.find(" 206 ") != std::string::npos;
                if (status_ok) {
                    std::vector<unsigned char> body(header_end + 4, response.end());
                    ok = write_bytes_to_temp_file(body, out_path);
                } else {
                    ok = false;
                }
            } else {
                ok = false;
            }
        }
    }
    if (results) freeaddrinfo(results);
    WSACleanup();
    return ok;
}

static int hex_value(wchar_t ch) {
    if (ch >= L'0' && ch <= L'9') return ch - L'0';
    if (ch >= L'a' && ch <= L'f') return ch - L'a' + 10;
    if (ch >= L'A' && ch <= L'F') return ch - L'A' + 10;
    return -1;
}

static std::wstring decode_url_path_leaf(const std::wstring& object_path) {
    std::wstring clean = object_path;
    size_t query = clean.find_first_of(L"?#");
    if (query != std::wstring::npos) clean.resize(query);
    size_t slash = clean.find_last_of(L"/\\");
    std::wstring leaf = (slash == std::wstring::npos) ? clean : clean.substr(slash + 1);
    std::string bytes;
    for (size_t i = 0; i < leaf.size(); ++i) {
        if (leaf[i] == L'%' && i + 2 < leaf.size()) {
            int hi = hex_value(leaf[i + 1]);
            int lo = hex_value(leaf[i + 2]);
            if (hi >= 0 && lo >= 0) {
                bytes.push_back((char)((hi << 4) | lo));
                i += 2;
                continue;
            }
        }
        if (leaf[i] < 0x80) {
            bytes.push_back((char)leaf[i]);
        } else {
            std::wstring one(1, leaf[i]);
            bytes += wide_to_utf8_narrow(one);
        }
    }

    if (bytes.empty()) return std::wstring();
    int len = MultiByteToWideChar(CP_UTF8, 0, bytes.data(), (int)bytes.size(), nullptr, 0);
    if (len <= 0) return leaf;
    std::wstring decoded((size_t)len, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, bytes.data(), (int)bytes.size(), &decoded[0], len);
    return decoded;
}

static bool try_localhost_temp_file(const std::wstring& host, const std::wstring& object_path,
                                    std::wstring& out_path) {
    if (_wcsicmp(host.c_str(), L"127.0.0.1") != 0
        && _wcsicmp(host.c_str(), L"localhost") != 0
        && _wcsicmp(host.c_str(), L"::1") != 0) {
        return false;
    }

    std::wstring leaf = decode_url_path_leaf(object_path);
    if (leaf.empty() || leaf.find_first_of(L":/\\") != std::wstring::npos) return false;

    wchar_t temp_dir[MAX_PATH] = {};
    if (GetTempPathW((DWORD)_countof(temp_dir), temp_dir) == 0) return false;
    std::wstring candidate = temp_dir;
    if (!candidate.empty() && candidate.back() != L'\\' && candidate.back() != L'/') {
        candidate += L'\\';
    }
    candidate += leaf;

    DWORD attr = GetFileAttributesW(candidate.c_str());
    if (attr == INVALID_FILE_ATTRIBUTES || (attr & FILE_ATTRIBUTE_DIRECTORY)) return false;
    out_path = candidate;
    return true;
}

static bool download_remote_to_temp_file(const std::wstring& source, std::wstring& out_path) {
    wchar_t host[512] = {};
    wchar_t url_path[4096] = {};
    wchar_t extra[2048] = {};
    URL_COMPONENTSW parts{};
    parts.dwStructSize = sizeof(parts);
    parts.lpszHostName = host;
    parts.dwHostNameLength = (DWORD)_countof(host);
    parts.lpszUrlPath = url_path;
    parts.dwUrlPathLength = (DWORD)_countof(url_path);
    parts.lpszExtraInfo = extra;
    parts.dwExtraInfoLength = (DWORD)_countof(extra);
    if (!WinHttpCrackUrl(source.c_str(), 0, 0, &parts)) return false;

    std::wstring object_path = url_path;
    object_path += extra;
    if (object_path.empty()) object_path = L"/";
    std::wstring host_name(host, parts.dwHostNameLength);

    if (try_localhost_temp_file(host_name, object_path, out_path)) {
        return true;
    }

    if (parts.nScheme == INTERNET_SCHEME_HTTP) {
        return download_http_to_temp_file(host_name, parts.nPort, object_path, out_path);
    }

    HINTERNET session = WinHttpOpen(L"new_emoji/1.0",
                                    WINHTTP_ACCESS_TYPE_NO_PROXY,
                                    WINHTTP_NO_PROXY_NAME,
                                    WINHTTP_NO_PROXY_BYPASS,
                                    0);
    if (!session) return false;
    WinHttpSetTimeouts(session, 5000, 5000, 10000, 20000);

    HINTERNET connect = WinHttpConnect(session, host_name.c_str(), parts.nPort, 0);
    if (!connect) {
        WinHttpCloseHandle(session);
        return false;
    }

    DWORD flags = parts.nScheme == INTERNET_SCHEME_HTTPS ? WINHTTP_FLAG_SECURE : 0;
    HINTERNET request = WinHttpOpenRequest(connect, L"GET", object_path.c_str(),
                                           nullptr, WINHTTP_NO_REFERER,
                                           WINHTTP_DEFAULT_ACCEPT_TYPES, flags);
    bool ok = false;
    wchar_t temp_dir[MAX_PATH] = {};
    wchar_t temp_file[MAX_PATH] = {};
    HANDLE file = INVALID_HANDLE_VALUE;
    if (request
        && WinHttpSendRequest(request, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                              WINHTTP_NO_REQUEST_DATA, 0, 0, 0)
        && WinHttpReceiveResponse(request, nullptr)) {
        DWORD status = 0;
        DWORD status_len = sizeof(status);
        WinHttpQueryHeaders(request,
                            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                            WINHTTP_HEADER_NAME_BY_INDEX,
                            &status, &status_len, WINHTTP_NO_HEADER_INDEX);
        if (status >= 200 && status < 300
            && GetTempPathW((DWORD)_countof(temp_dir), temp_dir) > 0
            && GetTempFileNameW(temp_dir, L"eui", 0, temp_file) > 0) {
            file = CreateFileW(temp_file, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS,
                               FILE_ATTRIBUTE_TEMPORARY, nullptr);
            if (file != INVALID_HANDLE_VALUE) {
                std::vector<unsigned char> buffer(8192);
                DWORD available = 0;
                ok = true;
                while (ok && WinHttpQueryDataAvailable(request, &available) && available > 0) {
                    DWORD to_read = (std::min)(available, (DWORD)buffer.size());
                    DWORD read = 0;
                    if (!WinHttpReadData(request, buffer.data(), to_read, &read)) {
                        ok = false;
                        break;
                    }
                    if (read == 0) break;
                    DWORD written = 0;
                    if (!WriteFile(file, buffer.data(), read, &written, nullptr) || written != read) {
                        ok = false;
                        break;
                    }
                }
            }
        }
    }

    if (file != INVALID_HANDLE_VALUE) CloseHandle(file);
    if (request) WinHttpCloseHandle(request);
    WinHttpCloseHandle(connect);
    WinHttpCloseHandle(session);
    if (ok) {
        out_path = temp_file;
    } else if (temp_file[0]) {
        DeleteFileW(temp_file);
    }
    return ok;
}

static void start_remote_download(const std::wstring& source, std::shared_ptr<RemoteImageEntry> entry) {
    std::thread([source, entry]() {
        std::wstring cache_path;
        bool ok = download_remote_to_temp_file(source, cache_path);

        std::vector<HWND> hwnds;
        {
            std::lock_guard<std::mutex> lock(entry->mutex);
            entry->status = ok ? 1 : 2;
            entry->cache_path = ok ? cache_path : L"";
            hwnds = entry->hwnds;
        }

        for (HWND hwnd : hwnds) {
            if (IsWindow(hwnd)) InvalidateRect(hwnd, nullptr, FALSE);
        }
    }).detach();
}

static int remote_source_state(HWND hwnd, const std::wstring& source, std::wstring& cache_path) {
    std::shared_ptr<RemoteImageEntry> entry;
    {
        std::lock_guard<std::mutex> lock(g_remote_image_mutex);
        auto& slot = g_remote_images[source];
        if (!slot) slot = std::make_shared<RemoteImageEntry>();
        entry = slot;
    }

    bool should_start = false;
    int state = 0;
    {
        std::lock_guard<std::mutex> lock(entry->mutex);
        remember_hwnd(*entry, hwnd);
        if (!entry->started) {
            entry->started = true;
            entry->status = 3;
            should_start = true;
        }
        state = entry->status;
        cache_path = entry->cache_path;
    }

    if (should_start) start_remote_download(source, entry);
    return state;
}

bool is_shared_remote_image_source(const std::wstring& value) {
    return is_remote_source(value);
}

int resolve_shared_image_source(HWND hwnd, const std::wstring& source, std::wstring& local_path) {
    if (source.empty()) {
        local_path.clear();
        return 0;
    }
    if (!is_remote_source(source)) {
        local_path = source;
        return 1;
    }
    return remote_source_state(hwnd, source, local_path);
}

static void release_bitmap_slot(ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                std::wstring& cached_src, int* out_w, int* out_h) {
    if (bitmap) {
        bitmap->Release();
        bitmap = nullptr;
    }
    rt = nullptr;
    cached_src.clear();
    if (out_w) *out_w = 0;
    if (out_h) *out_h = 0;
}

static bool load_bitmap_from_path(RenderContext& ctx, const std::wstring& path,
                                  ID2D1Bitmap** out_bitmap, int* out_w, int* out_h) {
    if (!g_wic_factory) ensure_factories();
    if (!g_wic_factory) return false;

    IWICBitmapDecoder* decoder = nullptr;
    IWICBitmapFrameDecode* frame = nullptr;
    IWICFormatConverter* converter = nullptr;
    HRESULT hr = g_wic_factory->CreateDecoderFromFilename(
        path.c_str(), nullptr, GENERIC_READ, WICDecodeMetadataCacheOnLoad, &decoder);
    if (SUCCEEDED(hr)) hr = decoder->GetFrame(0, &frame);
    if (SUCCEEDED(hr)) hr = g_wic_factory->CreateFormatConverter(&converter);
    if (SUCCEEDED(hr)) {
        hr = converter->Initialize(frame, GUID_WICPixelFormat32bppPBGRA,
            WICBitmapDitherTypeNone, nullptr, 0.0f, WICBitmapPaletteTypeMedianCut);
    }
    if (SUCCEEDED(hr)) {
        hr = ctx.rt->CreateBitmapFromWicBitmap(converter, nullptr, out_bitmap);
    }

    if (converter) converter->Release();
    if (frame) frame->Release();
    if (decoder) decoder->Release();

    if (SUCCEEDED(hr) && *out_bitmap) {
        D2D1_SIZE_F size = (*out_bitmap)->GetSize();
        if (out_w) *out_w = (int)size.width;
        if (out_h) *out_h = (int)size.height;
        return true;
    }
    return false;
}

void Image::set_source(const std::wstring& value) {
    src = value;
    load_status = src.empty() ? 0 : 3;
    ++reload_count;
    release_bitmap();
    release_preview_bitmap();
    invalidate();
}

void Image::set_alt(const std::wstring& value) {
    alt = value;
    text = value;
    invalidate();
}

void Image::set_fit(int value) {
    if (value < 0) value = 0;
    if (value > 4) value = 4;
    fit = value;
    invalidate();
}

void Image::set_preview_open(bool value) {
    preview_open = value && preview_enabled && preview_count() > 0;
    invalidate();
}

void Image::set_preview_enabled(bool value) {
    preview_enabled = value;
    if (!preview_enabled) preview_open = false;
    invalidate();
}

void Image::set_preview_transform(int scale_percent, int offset_x, int offset_y) {
    preview_scale_percent = (std::max)(25, (std::min)(400, scale_percent));
    preview_offset_x = (std::max)(-2000, (std::min)(2000, offset_x));
    preview_offset_y = (std::max)(-2000, (std::min)(2000, offset_y));
    invalidate();
}

void Image::set_cache_enabled(bool value) {
    cache_enabled = value;
    if (!cache_enabled) {
        release_bitmap();
        release_preview_bitmap();
    }
    invalidate();
}

void Image::set_lazy(bool value) {
    lazy = value;
    if (lazy && !is_in_viewport() && !m_bitmap) load_status = 4;
    invalidate();
}

void Image::set_placeholder(const std::wstring& icon, const std::wstring& value, Color fg, Color bg) {
    placeholder_icon = icon.empty() ? L"\U0001F5BC\uFE0F" : icon;
    placeholder_text = value.empty() ? L"\u56FE\u7247\u52A0\u8F7D\u4E2D" : value;
    placeholder_fg = fg;
    placeholder_bg = bg;
    invalidate();
}

void Image::set_error_content(const std::wstring& icon, const std::wstring& value, Color fg, Color bg) {
    error_icon = icon.empty() ? L"\u26A0\uFE0F" : icon;
    error_text = value.empty() ? L"\u56FE\u7247\u52A0\u8F7D\u5931\u8D25" : value;
    error_fg = fg;
    error_bg = bg;
    invalidate();
}

void Image::set_preview_list(const std::vector<std::wstring>& sources, int selected_index) {
    preview_sources = sources;
    set_preview_index(selected_index);
    release_preview_bitmap();
    invalidate();
}

void Image::set_preview_index(int index) {
    int count = preview_count();
    if (count <= 0) {
        preview_index = 0;
        preview_open = false;
    } else {
        preview_index = (std::max)(0, (std::min)(count - 1, index));
    }
    release_preview_bitmap();
    preview_offset_x = 0;
    preview_offset_y = 0;
    invalidate();
}

bool Image::is_preview_open() const {
    return preview_open;
}

int Image::preview_count() const {
    if (!preview_sources.empty()) return (int)preview_sources.size();
    return src.empty() ? 0 : 1;
}

Image::~Image() {
    release_bitmap();
    release_preview_bitmap();
}

void Image::release_bitmap() {
    release_bitmap_slot(m_bitmap, m_bitmap_rt, m_bitmap_src, &bitmap_width, &bitmap_height);
}

void Image::release_preview_bitmap() {
    release_bitmap_slot(m_preview_bitmap, m_preview_bitmap_rt, m_preview_bitmap_src, nullptr, nullptr);
}

bool Image::is_in_viewport() const {
    if (!owner_hwnd || !IsWindow(owner_hwnd)) return true;
    RECT rc{};
    GetClientRect(owner_hwnd, &rc);
    int ox = 0;
    int oy = 0;
    get_absolute_pos(ox, oy);
    return ox < rc.right && ox + bounds.w > rc.left && oy < rc.bottom && oy + bounds.h > rc.top;
}

bool Image::ensure_bitmap_for_source(RenderContext& ctx, const std::wstring& value,
                                     ID2D1Bitmap*& bitmap, ID2D1RenderTarget*& rt,
                                     std::wstring& cached_src, int* out_w, int* out_h,
                                     bool update_status, bool honor_lazy) {
    if (value.empty()) {
        if (update_status) load_status = 0;
        release_bitmap_slot(bitmap, rt, cached_src, out_w, out_h);
        return false;
    }
    if (cache_enabled && bitmap && rt == ctx.rt && cached_src == value) {
        if (update_status) load_status = 1;
        return true;
    }
    if (honor_lazy && lazy && !is_in_viewport()) {
        if (update_status) load_status = 4;
        return false;
    }

    std::wstring decode_path = value;
    if (is_remote_source(value)) {
        std::wstring cache_path;
        int state = remote_source_state(owner_hwnd, value, cache_path);
        if (state == 1 && !cache_path.empty()) {
            decode_path = cache_path;
        } else {
            if (update_status) load_status = (state == 2) ? 2 : 3;
            return false;
        }
    }

    release_bitmap_slot(bitmap, rt, cached_src, out_w, out_h);
    ID2D1Bitmap* loaded = nullptr;
    int w = 0;
    int h = 0;
    if (load_bitmap_from_path(ctx, decode_path, &loaded, &w, &h)) {
        bitmap = loaded;
        rt = ctx.rt;
        cached_src = value;
        if (out_w) *out_w = w;
        if (out_h) *out_h = h;
        if (update_status) load_status = 1;
        return true;
    }

    if (update_status) load_status = 2;
    return false;
}

bool Image::ensure_bitmap(RenderContext& ctx) {
    return ensure_bitmap_for_source(ctx, src, m_bitmap, m_bitmap_rt, m_bitmap_src,
                                    &bitmap_width, &bitmap_height, true, true);
}

std::wstring Image::current_preview_source() const {
    if (!preview_sources.empty()) {
        int index = (std::max)(0, (std::min)((int)preview_sources.size() - 1, preview_index));
        return preview_sources[index];
    }
    return src;
}

bool Image::ensure_preview_bitmap(RenderContext& ctx) {
    return ensure_bitmap_for_source(ctx, current_preview_source(), m_preview_bitmap,
                                    m_preview_bitmap_rt, m_preview_bitmap_src,
                                    nullptr, nullptr, false, false);
}

D2D1_RECT_F Image::fitted_rect(const D2D1_RECT_F& box, D2D1_SIZE_F size, int fit_mode) const {
    float box_w = box.right - box.left;
    float box_h = box.bottom - box.top;
    if (size.width <= 0.0f || size.height <= 0.0f || box_w <= 0.0f || box_h <= 0.0f) {
        return box;
    }

    float dw = box_w;
    float dh = box_h;
    if (fit_mode == 3 || (fit_mode == 4 && size.width <= box_w && size.height <= box_h)) {
        dw = size.width;
        dh = size.height;
    } else if (fit_mode != 2) {
        float sx = box_w / size.width;
        float sy = box_h / size.height;
        float s = fit_mode == 1 ? (std::max)(sx, sy) : (std::min)(sx, sy);
        dw = size.width * s;
        dh = size.height * s;
    }
    return D2D1::RectF(box.left + (box_w - dw) * 0.5f,
                       box.top + (box_h - dh) * 0.5f,
                       box.left + (box_w + dw) * 0.5f,
                       box.top + (box_h + dh) * 0.5f);
}

void Image::draw_state(RenderContext& ctx, const D2D1_RECT_F& rect, bool error_state) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color accent = error_state ? 0xFFF56C6C : t->accent;
    Color fg = error_state
        ? (error_fg ? error_fg : t->text_secondary)
        : (placeholder_fg ? placeholder_fg : t->text_secondary);
    Color bg = error_state ? error_bg : placeholder_bg;
    if (bg) {
        ctx.rt->FillRoundedRectangle(ROUNDED(rect, 5.0f, 5.0f), ctx.get_brush(bg));
    }

    float cx = (rect.left + rect.right) * 0.5f;
    float cy = (rect.top + rect.bottom) * 0.5f;
    D2D1_RECT_F sun = { rect.right - 58.0f, rect.top + 22.0f,
                        rect.right - 34.0f, rect.top + 46.0f };
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((sun.left + sun.right) * 0.5f,
        (sun.top + sun.bottom) * 0.5f), 12.0f, 12.0f), ctx.get_brush(with_alpha(accent, dark ? 0x88 : 0x66)));
    ctx.rt->DrawLine(D2D1::Point2F(rect.left + 24.0f, rect.bottom - 24.0f),
                     D2D1::Point2F(cx - 12.0f, cy + 12.0f),
                     ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);
    ctx.rt->DrawLine(D2D1::Point2F(cx - 12.0f, cy + 12.0f),
                     D2D1::Point2F(cx + 28.0f, rect.bottom - 34.0f),
                     ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);
    ctx.rt->DrawLine(D2D1::Point2F(cx + 28.0f, rect.bottom - 34.0f),
                     D2D1::Point2F(rect.right - 26.0f, rect.bottom - 20.0f),
                     ctx.get_brush(with_alpha(accent, 0xAA)), 2.0f);

    std::wstring icon = error_state ? error_icon : placeholder_icon;
    std::wstring label = error_state ? error_text : placeholder_text;
    if (!error_state && load_status == 4 && label == L"\u56FE\u7247\u52A0\u8F7D\u4E2D") {
        label = L"\u7B49\u5F85\u8FDB\u5165\u53EF\u89C1\u533A\u57DF";
    } else if (!error_state && src.empty() && label == L"\u56FE\u7247\u52A0\u8F7D\u4E2D") {
        label = L"\u56FE\u7247\u5360\u4F4D";
    }
    std::wstring hint = icon.empty() ? label : (icon + L" " + label);
    draw_text(ctx, hint, style, fg, rect.left + 8.0f, cy - 16.0f,
              rect.right - rect.left - 16.0f, 32.0f, 0.95f);
}

D2D1_RECT_F Image::image_rect() const {
    float inset = 14.0f;
    D2D1_RECT_F r = { inset, inset, (float)bounds.w - inset, (float)bounds.h - inset - 34.0f };
    if (r.bottom < r.top + 24.0f) r.bottom = (float)bounds.h - inset;
    return r;
}

D2D1_RECT_F Image::preview_rect() const {
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }
    float margin_x = (std::max)(30.0f, (std::min)(96.0f, (float)root_w * 0.07f));
    float margin_y = (std::max)(34.0f, (std::min)(92.0f, (float)root_h * 0.08f));
    float w = (std::max)(300.0f, (float)root_w - margin_x * 2.0f);
    float h = (std::max)(220.0f, (float)root_h - margin_y * 2.0f);
    if (w > (float)root_w) w = (float)root_w;
    if (h > (float)root_h) h = (float)root_h;
    return D2D1::RectF(((float)root_w - w) * 0.5f, ((float)root_h - h) * 0.5f,
                       ((float)root_w + w) * 0.5f, ((float)root_h + h) * 0.5f);
}

void Image::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFF5F7FA);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color muted = t->text_secondary;
    Color accent = t->accent;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    D2D1_RECT_F img_rect = image_rect();
    ctx.rt->FillRoundedRectangle(ROUNDED(img_rect, 5.0f, 5.0f),
        ctx.get_brush(with_alpha(accent, dark ? 0x24 : 0x18)));

    if (ensure_bitmap(ctx)) {
        D2D1_SIZE_F size = m_bitmap->GetSize();
        D2D1_RECT_F dest = fitted_rect(img_rect, size, fit);
        ctx.push_clip(img_rect);
        ctx.rt->DrawBitmap(m_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
        ctx.pop_clip();
    } else {
        draw_state(ctx, img_rect, load_status == 2);
    }
    ctx.rt->DrawRoundedRectangle(ROUNDED(img_rect, 5.0f, 5.0f),
        ctx.get_brush(with_alpha(accent, 0x88)), 1.0f);

    std::wstring caption = alt.empty() ? (src.empty() ? L"\U0001F5BC\uFE0F \u56FE\u7247" : src) : alt;
    draw_text(ctx, caption, style, muted,
              (float)style.pad_left, (float)bounds.h - 34.0f,
              (float)bounds.w - style.pad_left - style.pad_right, 28.0f,
              0.92f);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Image::paint_overlay(RenderContext& ctx) {
    if (!visible || !preview_open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);

    int px = 0;
    int py = 0;
    if (parent) parent->get_absolute_pos(px, py);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)-px, (float)-py));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }

    D2D1_RECT_F shade = { 0.0f, 0.0f, (float)root_w, (float)root_h };
    ctx.rt->FillRectangle(shade, ctx.get_brush(dark ? 0xCC000000 : 0x99000000));

    D2D1_RECT_F panel = preview_rect();
    Color bg = dark ? 0xFF202230 : 0xFFFFFFFF;
    ctx.rt->FillRoundedRectangle(ROUNDED(panel, 8.0f, 8.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(panel.left + 0.5f, panel.top + 0.5f,
        panel.right - 0.5f, panel.bottom - 0.5f), 8.0f, 8.0f),
        ctx.get_brush(t->border_default), 1.0f);

    D2D1_RECT_F close = { panel.right - 44.0f, panel.top + 8.0f, panel.right - 12.0f, panel.top + 40.0f };
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((close.left + close.right) * 0.5f,
        (close.top + close.bottom) * 0.5f), 15.0f, 15.0f), ctx.get_brush(t->button_hover));
    draw_text(ctx, L"\u00D7", style, t->text_primary, close.left, close.top,
              close.right - close.left, close.bottom - close.top);

    D2D1_RECT_F media = { panel.left + 22.0f, panel.top + 52.0f, panel.right - 22.0f, panel.bottom - 54.0f };
    ctx.rt->FillRoundedRectangle(ROUNDED(media, 6.0f, 6.0f),
        ctx.get_brush(dark ? 0xFF242637 : 0xFFF5F7FA));

    if (ensure_preview_bitmap(ctx)) {
        D2D1_SIZE_F size = m_preview_bitmap->GetSize();
        D2D1_RECT_F dest = media;
        float box_w = media.right - media.left;
        float box_h = media.bottom - media.top;
        if (size.width > 0.0f && size.height > 0.0f) {
            float s = (std::min)(box_w / size.width, box_h / size.height);
            s *= (float)preview_scale_percent / 100.0f;
            float dw = size.width * s;
            float dh = size.height * s;
            dest = D2D1::RectF(media.left + (box_w - dw) * 0.5f + (float)preview_offset_x,
                               media.top + (box_h - dh) * 0.5f + (float)preview_offset_y,
                               media.left + (box_w + dw) * 0.5f + (float)preview_offset_x,
                               media.top + (box_h + dh) * 0.5f + (float)preview_offset_y);
        }
        ctx.push_clip(media);
        ctx.rt->DrawBitmap(m_preview_bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
        ctx.pop_clip();
    } else {
        std::wstring unavailable = is_remote_source(current_preview_source())
            ? L"\U0001F504 \u56FE\u7247\u6B63\u5728\u52A0\u8F7D"
            : L"\u26A0\uFE0F \u56FE\u7247\u9884\u89C8\u4E0D\u53EF\u7528";
        draw_text(ctx, unavailable, style, t->text_secondary,
                  media.left, media.top, media.right - media.left, media.bottom - media.top);
    }

    if (preview_count() > 1) {
        float mid_y = (panel.top + panel.bottom) * 0.5f;
        D2D1_RECT_F prev = { panel.left + 12.0f, mid_y - 28.0f, panel.left + 52.0f, mid_y + 28.0f };
        D2D1_RECT_F next = { panel.right - 52.0f, mid_y - 28.0f, panel.right - 12.0f, mid_y + 28.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(prev, 20.0f, 20.0f), ctx.get_brush(with_alpha(t->button_hover, 0xDD)));
        ctx.rt->FillRoundedRectangle(ROUNDED(next, 20.0f, 20.0f), ctx.get_brush(with_alpha(t->button_hover, 0xDD)));
        draw_text(ctx, L"\u2039", style, t->text_primary, prev.left, prev.top, prev.right - prev.left, prev.bottom - prev.top, 1.7f);
        draw_text(ctx, L"\u203A", style, t->text_primary, next.left, next.top, next.right - next.left, next.bottom - next.top, 1.7f);
        std::wstring count_text = std::to_wstring(preview_index + 1) + L" / " + std::to_wstring(preview_count());
        draw_text(ctx, count_text, style, t->text_secondary, panel.left + 22.0f, panel.top + 14.0f,
                  panel.right - panel.left - 88.0f, 24.0f, 0.90f, DWRITE_TEXT_ALIGNMENT_LEADING);
    }

    std::wstring caption = alt.empty() ? L"\U0001F5BC\uFE0F \u56FE\u7247\u9884\u89C8" : alt;
    draw_text(ctx, caption, style, t->text_primary, panel.left + 22.0f, panel.bottom - 42.0f,
              panel.right - panel.left - 44.0f, 28.0f, 0.96f);

    ctx.rt->SetTransform(saved);
}

Element* Image::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) ? this : nullptr;
}

Element* Image::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !preview_open) return nullptr;
    int px = 0;
    int py = 0;
    if (parent) parent->get_absolute_pos(px, py);
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }
    float cx = (float)(x + px);
    float cy = (float)(y + py);
    return (cx >= 0.0f && cy >= 0.0f && cx <= (float)root_w && cy <= (float)root_h) ? this : nullptr;
}

void Image::on_mouse_down(int, int, MouseButton) {
    pressed = true;
    m_pressed_preview = preview_open;
    invalidate();
}

bool Image::change_preview_index(int delta) {
    int count = preview_count();
    if (count <= 1) return false;
    int next = preview_index + delta;
    if (next < 0) next = count - 1;
    if (next >= count) next = 0;
    if (next == preview_index) return false;
    set_preview_index(next);
    return true;
}

void Image::on_mouse_up(int x, int y, MouseButton) {
    if (m_pressed_preview || preview_open) {
        D2D1_RECT_F pr = preview_rect();
        D2D1_RECT_F close = { pr.right - 44.0f, pr.top + 8.0f, pr.right - 12.0f, pr.top + 40.0f };
        D2D1_RECT_F media = { pr.left + 22.0f, pr.top + 52.0f, pr.right - 22.0f, pr.bottom - 54.0f };
        float mid_y = (pr.top + pr.bottom) * 0.5f;
        D2D1_RECT_F prev = { pr.left + 12.0f, mid_y - 28.0f, pr.left + 52.0f, mid_y + 28.0f };
        D2D1_RECT_F next = { pr.right - 52.0f, mid_y - 28.0f, pr.right - 12.0f, mid_y + 28.0f };
        int ox = 0;
        int oy = 0;
        get_absolute_pos(ox, oy);
        float cx = (float)(x + ox);
        float cy = (float)(y + oy);
        if (rect_contains(close, cx, cy) || !rect_contains(pr, cx, cy)) {
            preview_open = false;
        } else if (preview_count() > 1 && rect_contains(prev, cx, cy)) {
            change_preview_index(-1);
        } else if (preview_count() > 1 && rect_contains(next, cx, cy)) {
            change_preview_index(1);
        } else if (!rect_contains(media, cx, cy)) {
            // Keep toolbar clicks inside the panel from closing the preview.
        }
    } else if (preview_enabled && load_status == 1 && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        preview_open = preview_count() > 0;
    }
    pressed = false;
    m_pressed_preview = false;
    invalidate();
}

void Image::on_key_down(int vk, int mods) {
    if (preview_open) {
        if (vk == VK_ESCAPE || vk == VK_RETURN || vk == VK_SPACE) {
            preview_open = false;
        } else if (vk == VK_OEM_PLUS || vk == VK_ADD) {
            set_preview_transform(preview_scale_percent + 10, preview_offset_x, preview_offset_y);
        } else if (vk == VK_OEM_MINUS || vk == VK_SUBTRACT) {
            set_preview_transform(preview_scale_percent - 10, preview_offset_x, preview_offset_y);
        } else if (preview_count() > 1 && vk == VK_LEFT && (mods & KeyMod::Control) == 0) {
            change_preview_index(-1);
        } else if (preview_count() > 1 && vk == VK_RIGHT && (mods & KeyMod::Control) == 0) {
            change_preview_index(1);
        } else if (vk == VK_LEFT) {
            set_preview_transform(preview_scale_percent, preview_offset_x - 10, preview_offset_y);
        } else if (vk == VK_RIGHT) {
            set_preview_transform(preview_scale_percent, preview_offset_x + 10, preview_offset_y);
        } else if (vk == VK_UP) {
            set_preview_transform(preview_scale_percent, preview_offset_x, preview_offset_y - 10);
        } else if (vk == VK_DOWN) {
            set_preview_transform(preview_scale_percent, preview_offset_x, preview_offset_y + 10);
        }
    } else if ((vk == VK_RETURN || vk == VK_SPACE) && preview_enabled && load_status == 1) {
        preview_open = preview_count() > 0;
    }
    invalidate();
}

void Image::on_blur() {
    has_focus = false;
    invalidate();
}
