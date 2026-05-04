#include "element_upload.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"

#include <algorithm>
#include <commdlg.h>
#include <cstdlib>
#include <cstring>
#include <cwctype>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

namespace {

enum UploadPart {
    kPartNone = 0,
    kPartChoose = 1,
    kPartSubmit = 2,
    kPartPreview = 3,
    kPartDownload = 4,
    kPartRemove = 5,
};

Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

std::wstring trim_copy(const std::wstring& value) {
    size_t first = 0;
    while (first < value.size() && iswspace(value[first])) ++first;
    size_t last = value.size();
    while (last > first && iswspace(value[last - 1])) --last;
    return value.substr(first, last - first);
}

std::wstring lower_copy(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(), [](wchar_t ch) {
        return (wchar_t)towlower(ch);
    });
    return value;
}

std::wstring file_extension(const std::wstring& path) {
    size_t slash = path.find_last_of(L"\\/");
    size_t dot = path.find_last_of(L'.');
    if (dot == std::wstring::npos || (slash != std::wstring::npos && dot < slash)) return L"";
    return lower_copy(path.substr(dot));
}

bool rect_contains(const D2D1_RECT_F& r, float x, float y) {
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
}

float upload_button_width_for_label(const std::wstring& label, float min_w, float max_w) {
    float units = 0.0f;
    for (size_t i = 0; i < label.size(); ++i) {
        wchar_t ch = label[i];
        if (ch >= 0xD800 && ch <= 0xDBFF && i + 1 < label.size()) {
            units += 1.15f;
            ++i;
        } else if (ch < 0x0080) {
            units += (ch == L' ' ? 0.35f : 0.56f);
        } else {
            units += 1.0f;
        }
    }
    float desired = 30.0f + units * 13.5f;
    if (max_w < 48.0f) return (std::max)(0.0f, max_w);
    return (std::min)(max_w, (std::max)(min_w, desired));
}

std::vector<std::wstring> split_accept_tokens(const std::wstring& accept) {
    std::vector<std::wstring> result;
    std::wstring token;
    for (wchar_t ch : accept) {
        if (ch == L',' || ch == L';' || ch == L'|') {
            token = trim_copy(token);
            if (!token.empty()) result.push_back(lower_copy(token));
            token.clear();
        } else {
            token.push_back(ch);
        }
    }
    token = trim_copy(token);
    if (!token.empty()) result.push_back(lower_copy(token));
    return result;
}

bool is_image_ext(const std::wstring& ext) {
    return ext == L".jpg" || ext == L".jpeg" || ext == L".png" || ext == L".gif" ||
           ext == L".bmp" || ext == L".webp" || ext == L".tif" || ext == L".tiff";
}

std::wstring dialog_pattern_for_token(const std::wstring& token) {
    if (token.empty()) return L"";
    if (token == L"image/*" || token == L"image/jpeg" || token == L"image/png" ||
        token == L"image/gif" || token == L"image/bmp" || token == L"image/webp") {
        if (token == L"image/jpeg") return L"*.jpg;*.jpeg";
        if (token == L"image/png") return L"*.png";
        if (token == L"image/gif") return L"*.gif";
        if (token == L"image/bmp") return L"*.bmp";
        if (token == L"image/webp") return L"*.webp";
        return L"*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.webp;*.tif;*.tiff";
    }
    if (token.size() > 2 && token[0] == L'*' && token[1] == L'.') return token;
    if (token[0] == L'.') return L"*" + token;
    if (token.find(L'/') == std::wstring::npos) return L"*." + token;
    return L"";
}

std::wstring join_patterns(const std::vector<std::wstring>& tokens) {
    std::wstring result;
    for (const auto& token : tokens) {
        std::wstring pattern = dialog_pattern_for_token(token);
        if (pattern.empty()) continue;
        if (!result.empty()) result += L";";
        result += pattern;
    }
    return result;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void draw_dashed_rect(RenderContext& ctx, const D2D1_RECT_F& r, Color color) {
    const float dash = 7.0f;
    const float gap = 5.0f;
    for (float x = r.left + 1.0f; x < r.right - 1.0f; x += dash + gap) {
        ctx.rt->DrawLine(D2D1::Point2F(x, r.top + 0.5f),
                         D2D1::Point2F((std::min)(x + dash, r.right - 1.0f), r.top + 0.5f),
                         ctx.get_brush(color), 1.0f);
        ctx.rt->DrawLine(D2D1::Point2F(x, r.bottom - 0.5f),
                         D2D1::Point2F((std::min)(x + dash, r.right - 1.0f), r.bottom - 0.5f),
                         ctx.get_brush(color), 1.0f);
    }
    for (float y = r.top + 1.0f; y < r.bottom - 1.0f; y += dash + gap) {
        ctx.rt->DrawLine(D2D1::Point2F(r.left + 0.5f, y),
                         D2D1::Point2F(r.left + 0.5f, (std::min)(y + dash, r.bottom - 1.0f)),
                         ctx.get_brush(color), 1.0f);
        ctx.rt->DrawLine(D2D1::Point2F(r.right - 0.5f, y),
                         D2D1::Point2F(r.right - 0.5f, (std::min)(y + dash, r.bottom - 1.0f)),
                         ctx.get_brush(color), 1.0f);
    }
}

} // namespace

std::wstring Upload::display_name_for_path(const std::wstring& path) {
    size_t pos = path.find_last_of(L"\\/");
    return pos == std::wstring::npos ? path : path.substr(pos + 1);
}

void Upload::sync_files_from_items() {
    files.clear();
    for (const auto& item : file_items) {
        files.push_back(item.full_path.empty() ? item.name : item.full_path);
    }
}

std::wstring Upload::selected_files_text() const {
    std::wstring result;
    for (size_t i = 0; i < files.size(); ++i) {
        if (i) result += L"|";
        result += files[i];
    }
    return result;
}

void Upload::notify_select() {
    if (!select_cb) return;
    std::string utf8 = wide_to_utf8(last_selected_files);
    select_cb(id, reinterpret_cast<const unsigned char*>(utf8.data()), (int)utf8.size());
}

void Upload::notify_upload(int action, int index, int value) {
    last_action = action;
    if (upload_cb) upload_cb(id, action, index, value);
}

long long Upload::file_size_bytes(const std::wstring& path) const {
    WIN32_FILE_ATTRIBUTE_DATA data = {};
    if (!GetFileAttributesExW(path.c_str(), GetFileExInfoStandard, &data)) return 0;
    ULARGE_INTEGER size = {};
    size.HighPart = data.nFileSizeHigh;
    size.LowPart = data.nFileSizeLow;
    return (long long)size.QuadPart;
}

bool Upload::is_image_file(const std::wstring& path) const {
    return is_image_ext(file_extension(path));
}

bool Upload::is_allowed_file_type(const std::wstring& path) const {
    auto tokens = split_accept_tokens(accept_filter);
    if (tokens.empty()) return true;
    std::wstring ext = file_extension(path);
    std::wstring ext_no_dot = ext.empty() ? L"" : ext.substr(1);
    for (const auto& token : tokens) {
        if (token == L"*/*" || token == L"*") return true;
        if (token == L"image/*" && is_image_ext(ext)) return true;
        if (token == L"image/jpeg" && (ext == L".jpg" || ext == L".jpeg")) return true;
        if (token == L"image/png" && ext == L".png") return true;
        if (token == L"image/gif" && ext == L".gif") return true;
        if (token == L"image/bmp" && ext == L".bmp") return true;
        if (token == L"image/webp" && ext == L".webp") return true;
        if (!ext.empty() && token == ext) return true;
        if (!ext.empty() && token == L"*" + ext) return true;
        if (!ext_no_dot.empty() && token == ext_no_dot) return true;
    }
    return false;
}

bool Upload::validate_files(const std::vector<std::wstring>& values, std::vector<UploadFileItem>& accepted) {
    accepted.clear();
    std::vector<std::wstring> nonempty;
    for (const auto& value : values) {
        if (!trim_copy(value).empty()) nonempty.push_back(value);
    }
    int effective_limit = multiple ? limit : 1;
    if (effective_limit > 0 && (int)nonempty.size() > effective_limit) {
        notify_upload(10, -1, (int)nonempty.size());
        invalidate();
        return false;
    }

    for (size_t i = 0; i < nonempty.size(); ++i) {
        const std::wstring& value = nonempty[i];
        if (!is_allowed_file_type(value)) {
            notify_upload(11, (int)i, 1);
            continue;
        }
        long long size = file_size_bytes(value);
        if (max_size_kb > 0 && size > (long long)max_size_kb * 1024LL) {
            notify_upload(11, (int)i, 2);
            continue;
        }
        UploadFileItem item;
        item.name = display_name_for_path(value);
        item.full_path = value;
        item.thumbnail_path = value;
        item.status = auto_upload ? 2 : 0;
        item.progress = 0;
        item.size_bytes = size;
        accepted.push_back(item);
    }

    return !accepted.empty();
}

int Upload::accept_selected_files(const std::vector<std::wstring>& values, int action) {
    std::vector<UploadFileItem> accepted;
    if (!validate_files(values, accepted)) {
        invalidate();
        return 0;
    }
    file_items = accepted;
    sync_files_from_items();
    last_selected_files = selected_files_text();
    last_selected_count = (int)file_items.size();
    selected_count += last_selected_count;
    last_action = action;
    notify_select();
    if (action == 12) notify_upload(12, -1, last_selected_count);
    if (auto_upload && !file_items.empty()) {
        upload_request_count += (int)file_items.size();
        notify_upload(3, -1, (int)file_items.size());
    }
    invalidate();
    return last_selected_count;
}

void Upload::set_title(const std::wstring& value) {
    title = value;
    text = value;
    invalidate();
}

void Upload::set_tip(const std::wstring& value) {
    tip = value;
    invalidate();
}

void Upload::set_files(const std::vector<std::wstring>& values) {
    files = values;
    file_items.clear();
    for (const auto& value : values) {
        UploadFileItem item;
        item.name = display_name_for_path(value);
        item.full_path = value;
        item.thumbnail_path = value;
        item.status = 1;
        item.progress = 100;
        item.size_bytes = file_size_bytes(value);
        file_items.push_back(item);
    }
    sync_files_from_items();
    invalidate();
}

void Upload::set_file_items(const std::vector<UploadFileItem>& values) {
    file_items = values;
    for (auto& item : file_items) {
        if (item.full_path.empty()) item.full_path = item.name;
        if (item.name.empty()) item.name = display_name_for_path(item.full_path);
        if (item.thumbnail_path.empty()) item.thumbnail_path = item.full_path;
        if (item.size_bytes <= 0) item.size_bytes = file_size_bytes(item.full_path);
    }
    sync_files_from_items();
    invalidate();
}

void Upload::set_options(int multiple_enabled, int auto_upload_enabled) {
    multiple = multiple_enabled != 0 ? 1 : 0;
    auto_upload = auto_upload_enabled != 0 ? 1 : 0;
    invalidate();
}

void Upload::set_style(int next_style, int next_show_file_list, int next_show_tip,
                       int next_show_actions, int next_drop_enabled) {
    style_mode = (std::max)(0, (std::min)(6, next_style));
    show_file_list = next_show_file_list != 0 ? 1 : 0;
    show_tip = next_show_tip != 0 ? 1 : 0;
    show_actions = next_show_actions != 0 ? 1 : 0;
    drop_enabled = next_drop_enabled != 0 ? 1 : 0;
    invalidate();
}

void Upload::set_texts(const std::wstring& next_title, const std::wstring& next_tip,
                       const std::wstring& next_trigger, const std::wstring& next_submit) {
    title = next_title;
    text = next_title;
    tip = next_tip;
    trigger_text = next_trigger;
    submit_text = next_submit;
    invalidate();
}

void Upload::set_constraints(int next_limit, int next_max_size_kb, const std::wstring& next_accept) {
    limit = (std::max)(0, next_limit);
    max_size_kb = (std::max)(0, next_max_size_kb);
    accept_filter = next_accept;
    invalidate();
}

void Upload::set_selected_files(const std::vector<std::wstring>& values) {
    accept_selected_files(values, 2);
}

void Upload::set_file_status(int index, int status, int progress) {
    if (index < 0 || index >= (int)file_items.size()) return;
    if (status < 0) status = 0;
    if (status > 3) status = 3;
    if (progress < 0) progress = 0;
    if (progress > 100) progress = 100;
    file_items[index].status = status;
    file_items[index].progress = progress;
    notify_upload(7, index, progress);
    invalidate();
}

void Upload::set_preview_open(int index, bool open) {
    if (!open) {
        preview_open = 0;
        preview_index = -1;
    } else if (index >= 0 && index < (int)file_items.size()) {
        preview_open = 1;
        preview_index = index;
        notify_upload(8, index, 1);
    }
    invalidate();
}

void Upload::remove_file(int index) {
    if (index < 0 || index >= (int)file_items.size()) return;
    file_items.erase(file_items.begin() + index);
    sync_files_from_items();
    ++remove_count;
    if (preview_index == index) set_preview_open(-1, false);
    else if (preview_index > index) --preview_index;
    notify_upload(5, index, (int)file_items.size());
    invalidate();
}

void Upload::retry_file(int index) {
    if (index < 0 || index >= (int)file_items.size()) return;
    file_items[index].status = 2;
    file_items[index].progress = 0;
    ++retry_count;
    ++upload_request_count;
    notify_upload(4, index, 0);
    invalidate();
}

void Upload::clear_files() {
    file_items.clear();
    files.clear();
    last_selected_files.clear();
    last_selected_count = 0;
    preview_open = 0;
    preview_index = -1;
    notify_upload(6, -1, 0);
    invalidate();
}

int Upload::start_upload(int index) {
    int started = 0;
    if (index >= 0) {
        if (index < (int)file_items.size()) {
            file_items[index].status = 2;
            file_items[index].progress = 0;
            started = 1;
            notify_upload(3, index, 1);
        }
    } else {
        for (auto& item : file_items) {
            if (item.status == 0 || item.status == 3) {
                item.status = 2;
                item.progress = 0;
                ++started;
            }
        }
        if (started > 0) notify_upload(3, -1, started);
    }
    if (started > 0) {
        upload_request_count += started;
        invalidate();
    }
    return started;
}

std::wstring Upload::dialog_filter_text() const {
    std::wstring patterns = join_patterns(split_accept_tokens(accept_filter));
    if (patterns.empty()) patterns = L"*.*";
    std::wstring label = patterns == L"*.*" ? L"\u6240\u6709\u6587\u4EF6 (*.*)" :
        L"\u53EF\u9009\u6587\u4EF6 (" + patterns + L")";
    std::wstring filter;
    filter += label;
    filter.push_back(L'\0');
    filter += patterns;
    filter.push_back(L'\0');
    filter += L"\u6240\u6709\u6587\u4EF6 (*.*)";
    filter.push_back(L'\0');
    filter += L"*.*";
    filter.push_back(L'\0');
    filter.push_back(L'\0');
    return filter;
}

int Upload::open_file_dialog(HWND hwnd) {
    wchar_t buffer[32768];
    std::memset(buffer, 0, sizeof(buffer));
    std::wstring filter = dialog_filter_text();
    OPENFILENAMEW ofn = {};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = filter.c_str();
    ofn.lpstrFile = buffer;
    ofn.nMaxFile = 32768;
    ofn.lpstrTitle = L"\u8BF7\u9009\u62E9\u8981\u4E0A\u4F20\u7684\u6587\u4EF6";
    ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    if (multiple) ofn.Flags |= OFN_ALLOWMULTISELECT;
    last_action = 1;
    if (!GetOpenFileNameW(&ofn)) {
        invalidate();
        return 0;
    }

    std::vector<std::wstring> selected;
    std::wstring first = buffer;
    wchar_t* p = buffer + first.size() + 1;
    if (*p == L'\0') {
        selected.push_back(first);
    } else {
        std::wstring dir = first;
        while (*p) {
            std::wstring name = p;
            selected.push_back(dir + L"\\" + name);
            p += name.size() + 1;
        }
    }
    return accept_selected_files(selected, 2);
}

int Upload::accept_dropped_files(const std::vector<std::wstring>& values) {
    if (!wants_dropped_files()) return 0;
    return accept_selected_files(values, 12);
}

bool Upload::wants_dropped_files() const {
    return visible && enabled && drop_enabled != 0;
}

bool Upload::load_bitmap(RenderContext& ctx, const std::wstring& path, ID2D1Bitmap** out_bitmap) const {
    if (!out_bitmap) return false;
    *out_bitmap = nullptr;
    if (path.empty() || !is_image_file(path)) return false;
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
    if (SUCCEEDED(hr)) hr = ctx.rt->CreateBitmapFromWicBitmap(converter, nullptr, out_bitmap);

    if (converter) converter->Release();
    if (frame) frame->Release();
    if (decoder) decoder->Release();
    return SUCCEEDED(hr) && *out_bitmap != nullptr;
}

void Upload::draw_bitmap_fit(RenderContext& ctx, const std::wstring& path, const D2D1_RECT_F& rect, bool cover) const {
    ID2D1Bitmap* bitmap = nullptr;
    if (!load_bitmap(ctx, path, &bitmap)) {
        const Theme* t = theme_for_window(owner_hwnd);
        draw_text(ctx, L"\U0001F5BC\uFE0F", style, t->text_secondary,
                  rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top,
                  1.4f, DWRITE_TEXT_ALIGNMENT_CENTER);
        return;
    }
    D2D1_SIZE_F size = bitmap->GetSize();
    D2D1_RECT_F dest = rect;
    float bw = rect.right - rect.left;
    float bh = rect.bottom - rect.top;
    if (size.width > 0 && size.height > 0 && bw > 0 && bh > 0) {
        float sx = bw / size.width;
        float sy = bh / size.height;
        float s = cover ? (std::max)(sx, sy) : (std::min)(sx, sy);
        float dw = size.width * s;
        float dh = size.height * s;
        dest = D2D1::RectF(rect.left + (bw - dw) * 0.5f,
                           rect.top + (bh - dh) * 0.5f,
                           rect.left + (bw + dw) * 0.5f,
                           rect.top + (bh + dh) * 0.5f);
    }
    ctx.push_clip(rect);
    ctx.rt->DrawBitmap(bitmap, dest, 1.0f, D2D1_BITMAP_INTERPOLATION_MODE_LINEAR);
    ctx.pop_clip();
    bitmap->Release();
}

void Upload::paint_trigger_button(RenderContext& ctx, const D2D1_RECT_F& rect,
                                  const std::wstring& label, Color bg, Color fg, Color border) {
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
    ctx.push_clip(rect);
    draw_text(ctx, label, style, fg, rect.left + 8.0f, rect.top, rect.right - rect.left - 16.0f,
              rect.bottom - rect.top, 0.92f, DWRITE_TEXT_ALIGNMENT_CENTER);
    ctx.pop_clip();
}

void Upload::paint_file_rows(RenderContext& ctx, float x, float y, float w, float h, bool thumbnails) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    float row_h = thumbnails ? 54.0f : 28.0f;
    int max_rows = (int)(h / row_h);
    max_rows = (std::max)(0, max_rows);
    int count = (std::min)((int)file_items.size(), max_rows);
    if (file_items.empty() && max_rows > 0) {
        draw_text(ctx, L"\U0001F4ED \u6682\u65E0\u4E0A\u4F20\u6587\u4EF6", style, muted,
                  x, y, w, row_h, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);
        return;
    }
    for (int i = 0; i < count; ++i) {
        const UploadFileItem& item = file_items[i];
        float row_y = y + row_h * (float)i;
        D2D1_RECT_F row = { x, row_y, x + w, row_y + row_h - 5.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
            ctx.get_brush(i % 2 == 0 ? with_alpha(t->accent, dark ? 0x12 : 0x0C) : bg));
        float text_x = row.left + 10.0f;
        if (thumbnails) {
            D2D1_RECT_F thumb = { row.left + 8.0f, row.top + 6.0f, row.left + 48.0f, row.bottom - 6.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(thumb, 4.0f, 4.0f),
                ctx.get_brush(dark ? 0xFF202230 : 0xFFF2F6FC));
            draw_bitmap_fit(ctx, item.thumbnail_path.empty() ? item.full_path : item.thumbnail_path, thumb, true);
            text_x = row.left + 58.0f;
        }
        std::wstring mark = item.status == 2 ? L"\u2026" : (item.status == 3 ? L"!" : (item.status == 0 ? L"\u25CB" : L"\u2713"));
        Color mark_color = item.status == 3 ? 0xFFE74C3C : (item.status == 2 ? 0xFFE6A23C : t->accent);
        draw_text(ctx, mark, style, mark_color, text_x, row.top, 18.0f,
                  row.bottom - row.top, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);
        float actions_w = show_actions ? 78.0f : 48.0f;
        draw_text(ctx, item.name, style, fg, text_x + 24.0f, row.top,
                  row.right - text_x - 30.0f - actions_w, row.bottom - row.top, thumbnails ? 0.88f : 0.92f);
        if (item.status == 2 || item.status == 3) {
            std::wstring progress = item.status == 3 ? L"\u91CD\u8BD5" : std::to_wstring(item.progress) + L"%";
            draw_text(ctx, progress, style, muted, row.right - actions_w - 48.0f, row.top,
                      46.0f, row.bottom - row.top, 0.82f, DWRITE_TEXT_ALIGNMENT_TRAILING);
        }
        if (show_actions) {
            draw_text(ctx, L"\U0001F50D", style, muted, row.right - 76.0f, row.top, 24.0f, row.bottom - row.top, 0.8f, DWRITE_TEXT_ALIGNMENT_CENTER);
            draw_text(ctx, L"\U0001F4E5", style, muted, row.right - 50.0f, row.top, 24.0f, row.bottom - row.top, 0.8f, DWRITE_TEXT_ALIGNMENT_CENTER);
            draw_text(ctx, L"\u00D7", style, 0xFFE74C3C, row.right - 24.0f, row.top, 20.0f, row.bottom - row.top, 1.0f, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
    }
    if ((int)file_items.size() > count && max_rows > 0) {
        std::wstring more = L"\u8FD8\u6709 " + std::to_wstring((int)file_items.size() - count) + L" \u4E2A\u6587\u4EF6";
        draw_text(ctx, more, style, muted, x, y + row_h * (float)count, w, row_h, 0.86f);
    }
}

void Upload::paint_picture_cards(RenderContext& ctx, float x, float y, float w, float h, bool custom_actions) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color border = hovered || pressed ? t->accent : t->border_default;
    float card = (std::min)(104.0f, (std::max)(74.0f, (std::min)(w, h) * 0.42f));
    float gap = 10.0f;
    int cols = (std::max)(1, (int)((w + gap) / (card + gap)));
    int draw_count = (int)file_items.size();
    bool can_add = limit <= 0 || draw_count < limit;
    int total = draw_count + (can_add ? 1 : 0);
    for (int i = 0; i < total; ++i) {
        int col = i % cols;
        int row = i / cols;
        D2D1_RECT_F r = { x + col * (card + gap), y + row * (card + gap),
                          x + col * (card + gap) + card, y + row * (card + gap) + card };
        if (r.bottom > y + h) break;
        ctx.rt->FillRoundedRectangle(ROUNDED(r, 6.0f, 6.0f),
            ctx.get_brush(dark ? 0xFF202230 : 0xFFF8FAFE));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(r.left + 0.5f, r.top + 0.5f, r.right - 0.5f, r.bottom - 0.5f),
            6.0f, 6.0f), ctx.get_brush(i < draw_count ? t->border_default : border), 1.0f);
        if (i < draw_count) {
            draw_bitmap_fit(ctx, file_items[i].thumbnail_path.empty() ? file_items[i].full_path : file_items[i].thumbnail_path,
                            D2D1::RectF(r.left + 4.0f, r.top + 4.0f, r.right - 4.0f, r.bottom - 4.0f), true);
            if (show_actions || custom_actions) {
                D2D1_RECT_F mask = { r.left + 4.0f, r.bottom - 32.0f, r.right - 4.0f, r.bottom - 4.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(mask, 4.0f, 4.0f), ctx.get_brush(0xAA000000));
                draw_text(ctx, L"\U0001F50D", style, 0xFFFFFFFF, mask.left, mask.top, (mask.right - mask.left) / 3.0f, mask.bottom - mask.top, 0.8f, DWRITE_TEXT_ALIGNMENT_CENTER);
                draw_text(ctx, L"\U0001F4E5", style, 0xFFFFFFFF, mask.left + (mask.right - mask.left) / 3.0f, mask.top, (mask.right - mask.left) / 3.0f, mask.bottom - mask.top, 0.8f, DWRITE_TEXT_ALIGNMENT_CENTER);
                draw_text(ctx, L"\U0001F5D1\uFE0F", style, 0xFFFFFFFF, mask.left + (mask.right - mask.left) * 2.0f / 3.0f, mask.top, (mask.right - mask.left) / 3.0f, mask.bottom - mask.top, 0.8f, DWRITE_TEXT_ALIGNMENT_CENTER);
            }
        } else {
            draw_text(ctx, L"+", style, t->accent, r.left, r.top + 14.0f, card, 36.0f, 2.0f, DWRITE_TEXT_ALIGNMENT_CENTER);
            draw_text(ctx, L"\u9009\u62E9\u56FE\u7247", style, t->text_secondary, r.left + 4.0f, r.top + 54.0f, card - 8.0f, 24.0f, 0.82f, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
    }
}

void Upload::paint_avatar(RenderContext& ctx, float x, float y, float w, float h) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float side = (std::min)((std::min)(w, h), 178.0f);
    D2D1_RECT_F r = { x, y, x + side, y + side };
    ctx.rt->FillRoundedRectangle(ROUNDED(r, 6.0f, 6.0f),
        ctx.get_brush(dark ? 0xFF202230 : 0xFFF8FAFE));
    draw_dashed_rect(ctx, r, hovered || pressed ? t->accent : t->border_default);
    if (!file_items.empty()) {
        draw_bitmap_fit(ctx, file_items[0].thumbnail_path.empty() ? file_items[0].full_path : file_items[0].thumbnail_path, r, true);
        if (show_actions) {
            D2D1_RECT_F mask = { r.left, r.bottom - 34.0f, r.right, r.bottom };
            ctx.rt->FillRoundedRectangle(ROUNDED(mask, 0.0f, 0.0f), ctx.get_brush(0xAA000000));
            draw_text(ctx, L"\U0001F50D  \u00D7", style, 0xFFFFFFFF, mask.left, mask.top, mask.right - mask.left, mask.bottom - mask.top, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
    } else {
        draw_text(ctx, L"+", style, t->accent, r.left, r.top + side * 0.28f, side, 44.0f, 2.4f, DWRITE_TEXT_ALIGNMENT_CENTER);
        draw_text(ctx, trigger_text.empty() ? L"\u4E0A\u4F20\u5934\u50CF" : trigger_text, style, t->text_secondary,
                  r.left + 8.0f, r.top + side * 0.58f, side - 16.0f, 28.0f, 0.86f, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
}

D2D1_RECT_F Upload::preview_rect() const {
    int root_w = bounds.w;
    int root_h = bounds.h;
    Element* p = parent;
    while (p) {
        root_w = p->bounds.w;
        root_h = p->bounds.h;
        p = p->parent;
    }
    float margin_x = (std::max)(28.0f, (std::min)(96.0f, (float)root_w * 0.06f));
    float margin_y = (std::max)(34.0f, (std::min)(96.0f, (float)root_h * 0.07f));
    float w = (std::max)(280.0f, (float)root_w - margin_x * 2.0f);
    float h = (std::max)(220.0f, (float)root_h - margin_y * 2.0f);
    if (w > (float)root_w) w = (float)root_w;
    if (h > (float)root_h) h = (float)root_h;
    return D2D1::RectF(((float)root_w - w) * 0.5f, ((float)root_h - h) * 0.5f,
                       ((float)root_w + w) * 0.5f, ((float)root_h + h) * 0.5f);
}

void Upload::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color drop_bg = hovered ? with_alpha(t->accent, dark ? 0x24 : 0x14)
                            : (dark ? 0xFF202230 : 0xFFFAFCFF);
    Color border = hovered || pressed ? t->accent : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);
    D2D1_RECT_F root = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(root, radius, radius), ctx.get_brush(bg));

    const float pad = 12.0f;
    if (style_mode == 1) {
        paint_avatar(ctx, pad, pad, (float)bounds.w - pad * 2.0f, (float)bounds.h - pad * 2.0f);
    } else if (style_mode == 2 || style_mode == 3) {
        paint_picture_cards(ctx, pad, pad, (float)bounds.w - pad * 2.0f, (float)bounds.h - pad * 2.0f, style_mode == 3);
    } else if (style_mode == 5) {
        float drop_h = (std::min)(126.0f, (std::max)(88.0f, (float)bounds.h * 0.50f));
        if (drop_h > (float)bounds.h - 24.0f) drop_h = (float)bounds.h - 24.0f;
        D2D1_RECT_F drop = { pad, pad, (float)bounds.w - pad, pad + drop_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(drop, radius, radius), ctx.get_brush(drop_bg));
        draw_dashed_rect(ctx, drop, border);
        float cx = (drop.left + drop.right) * 0.5f;
        float icon_y = drop.top + 22.0f;
        ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx, icon_y + 34.0f), ctx.get_brush(t->accent), 2.2f);
        ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx - 12.0f, icon_y + 14.0f), ctx.get_brush(t->accent), 2.2f);
        ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx + 12.0f, icon_y + 14.0f), ctx.get_brush(t->accent), 2.2f);
        ctx.rt->DrawLine(D2D1::Point2F(cx - 20.0f, icon_y + 38.0f), D2D1::Point2F(cx + 20.0f, icon_y + 38.0f), ctx.get_brush(t->accent), 2.0f);
        std::wstring title_text = title.empty() ? L"\U0001F4E4 \u70B9\u51FB\u6216\u62D6\u62FD\u6587\u4EF6\u5230\u6B64\u5904\u4E0A\u4F20" : title;
        draw_text(ctx, title_text, style, fg, drop.left + 12.0f, drop.top + 62.0f, drop.right - drop.left - 24.0f, 24.0f, 1.0f, DWRITE_TEXT_ALIGNMENT_CENTER);
        if (show_tip && !tip.empty()) {
            draw_text(ctx, tip, style, muted, drop.left + 12.0f, drop.top + 88.0f, drop.right - drop.left - 24.0f, 22.0f, 0.88f, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
        if (show_file_list) paint_file_rows(ctx, pad, drop.bottom + 10.0f, (float)bounds.w - pad * 2.0f, (float)bounds.h - drop.bottom - 20.0f, false);
    } else {
        D2D1_RECT_F choose = { pad, pad, pad + 112.0f, pad + 34.0f };
        std::wstring choose_label = trigger_text.empty() ? L"\U0001F4E4 \u70B9\u51FB\u4E0A\u4F20" : trigger_text;
        paint_trigger_button(ctx, choose, choose_label, t->accent, 0xFFFFFFFF, t->accent);
        float next_x = choose.right + 10.0f;
        if (style_mode == 6) {
            std::wstring submit_label = submit_text.empty() ? L"\U0001F680 \u4E0A\u4F20\u5230\u670D\u52A1\u5668" : submit_text;
            float submit_w = upload_button_width_for_label(submit_label, 152.0f, (float)bounds.w - next_x - pad);
            D2D1_RECT_F submit = { next_x, pad, next_x + submit_w, pad + 34.0f };
            paint_trigger_button(ctx, submit, submit_label, 0xFF67C23A, 0xFFFFFFFF, 0xFF67C23A);
            next_x = submit.right + 10.0f;
        }
        if (show_tip && !tip.empty()) {
            draw_text(ctx, tip, style, muted, next_x, pad, (float)bounds.w - next_x - pad, 34.0f, 0.86f);
        }
        if (show_file_list) {
            paint_file_rows(ctx, pad, pad + 46.0f, (float)bounds.w - pad * 2.0f,
                            (float)bounds.h - pad - 46.0f, style_mode == 4);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Upload::paint_overlay(RenderContext& ctx) {
    if (!visible || !preview_open || preview_index < 0 || preview_index >= (int)file_items.size()) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    int px = 0, py = 0;
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
    ctx.rt->FillRoundedRectangle(ROUNDED(panel, 8.0f, 8.0f), ctx.get_brush(dark ? 0xFF202230 : 0xFFFFFFFF));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(panel.left + 0.5f, panel.top + 0.5f, panel.right - 0.5f, panel.bottom - 0.5f), 8.0f, 8.0f),
        ctx.get_brush(t->border_default), 1.0f);
    D2D1_RECT_F close = { panel.right - 44.0f, panel.top + 8.0f, panel.right - 12.0f, panel.top + 40.0f };
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((close.left + close.right) * 0.5f, (close.top + close.bottom) * 0.5f),
        15.0f, 15.0f), ctx.get_brush(t->button_hover));
    draw_text(ctx, L"X", style, t->text_primary, close.left, close.top, close.right - close.left, close.bottom - close.top, 1.0f, DWRITE_TEXT_ALIGNMENT_CENTER);
    D2D1_RECT_F media = { panel.left + 22.0f, panel.top + 52.0f, panel.right - 22.0f, panel.bottom - 50.0f };
    ctx.rt->FillRoundedRectangle(ROUNDED(media, 6.0f, 6.0f), ctx.get_brush(dark ? 0xFF242637 : 0xFFF5F7FA));
    const UploadFileItem& item = file_items[preview_index];
    draw_bitmap_fit(ctx, item.thumbnail_path.empty() ? item.full_path : item.thumbnail_path, media, false);
    draw_text(ctx, item.name.empty() ? L"\U0001F5BC\uFE0F \u56FE\u7247\u9884\u89C8" : item.name,
              style, t->text_primary, panel.left + 22.0f, panel.bottom - 40.0f,
              panel.right - panel.left - 44.0f, 28.0f, 0.96f);
    ctx.rt->SetTransform(saved);
}

Element* Upload::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !preview_open) return nullptr;
    int px = 0, py = 0;
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

int Upload::hit_part(int x, int y, int& index) const {
    index = -1;
    const float pad = 12.0f;
    if (preview_open) return kPartPreview;
    if (style_mode == 1) {
        float side = (std::min)((float)(std::min)(bounds.w, bounds.h) - pad * 2.0f, 178.0f);
        D2D1_RECT_F r = { pad, pad, pad + side, pad + side };
        if (!rect_contains(r, (float)x, (float)y)) return kPartNone;
        if (!file_items.empty() && show_actions && y >= r.bottom - 34.0f) {
            index = 0;
            return x < (r.left + r.right) * 0.5f ? kPartPreview : kPartRemove;
        }
        return kPartChoose;
    }
    if (style_mode == 2 || style_mode == 3) {
        float w = (float)bounds.w - pad * 2.0f;
        float h = (float)bounds.h - pad * 2.0f;
        float card = (std::min)(104.0f, (std::max)(74.0f, (std::min)(w, h) * 0.42f));
        float gap = 10.0f;
        int cols = (std::max)(1, (int)((w + gap) / (card + gap)));
        int draw_count = (int)file_items.size();
        bool can_add = limit <= 0 || draw_count < limit;
        int total = draw_count + (can_add ? 1 : 0);
        for (int i = 0; i < total; ++i) {
            int col = i % cols;
            int row = i / cols;
            D2D1_RECT_F r = { pad + col * (card + gap), pad + row * (card + gap),
                              pad + col * (card + gap) + card, pad + row * (card + gap) + card };
            if (!rect_contains(r, (float)x, (float)y)) continue;
            if (i >= draw_count) return kPartChoose;
            index = i;
            if (show_actions && y >= r.bottom - 32.0f) {
                float third = (r.right - r.left) / 3.0f;
                if (x < r.left + third) return kPartPreview;
                if (x < r.left + third * 2.0f) return kPartDownload;
                return kPartRemove;
            }
            return kPartPreview;
        }
        return kPartNone;
    }
    if (style_mode == 5) {
        float drop_h = (std::min)(126.0f, (std::max)(88.0f, (float)bounds.h * 0.50f));
        if (drop_h > (float)bounds.h - 24.0f) drop_h = (float)bounds.h - 24.0f;
        D2D1_RECT_F drop = { pad, pad, (float)bounds.w - pad, pad + drop_h };
        if (rect_contains(drop, (float)x, (float)y)) return kPartChoose;
        float rows_y = drop.bottom + 10.0f;
        float row_h = 28.0f;
        int row = (int)(((float)y - rows_y) / row_h);
        if (row >= 0 && row < (int)file_items.size() && show_actions && x > bounds.w - pad - 78) {
            index = row;
            if (x < bounds.w - pad - 52) return kPartPreview;
            if (x < bounds.w - pad - 26) return kPartDownload;
            return kPartRemove;
        }
        return kPartNone;
    }
    D2D1_RECT_F choose = { pad, pad, pad + 112.0f, pad + 34.0f };
    if (rect_contains(choose, (float)x, (float)y)) return kPartChoose;
    if (style_mode == 6) {
        std::wstring submit_label = submit_text.empty() ? L"\U0001F680 \u4E0A\u4F20\u5230\u670D\u52A1\u5668" : submit_text;
        float next_x = choose.right + 10.0f;
        float submit_w = upload_button_width_for_label(submit_label, 152.0f, (float)bounds.w - next_x - pad);
        D2D1_RECT_F submit = { next_x, pad, next_x + submit_w, pad + 34.0f };
        if (rect_contains(submit, (float)x, (float)y)) return kPartSubmit;
    }
    float rows_y = pad + 46.0f;
    float row_h = style_mode == 4 ? 54.0f : 28.0f;
    int row = (int)(((float)y - rows_y) / row_h);
    if (row >= 0 && row < (int)file_items.size() && show_actions && x > bounds.w - pad - 78) {
        index = row;
        if (x < bounds.w - pad - 52) return kPartPreview;
        if (x < bounds.w - pad - 26) return kPartDownload;
        return kPartRemove;
    }
    return kPartNone;
}

void Upload::on_mouse_enter() {
    hovered = true;
    invalidate();
}

void Upload::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_press_part = kPartNone;
    m_press_index = -1;
    invalidate();
}

void Upload::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_part = hit_part(x, y, m_press_index);
    invalidate();
}

void Upload::on_mouse_up(int x, int y, MouseButton) {
    int index = -1;
    int part = hit_part(x, y, index);
    if (preview_open) {
        D2D1_RECT_F pr = preview_rect();
        D2D1_RECT_F close = { pr.right - 44.0f, pr.top + 8.0f, pr.right - 12.0f, pr.top + 40.0f };
        D2D1_RECT_F media = { pr.left + 22.0f, pr.top + 52.0f, pr.right - 22.0f, pr.bottom - 50.0f };
        int ox = 0, oy = 0;
        get_absolute_pos(ox, oy);
        float cx = (float)(x + ox);
        float cy = (float)(y + oy);
        if (rect_contains(close, cx, cy) || !rect_contains(media, cx, cy)) set_preview_open(-1, false);
    } else if (part == m_press_part && (index == m_press_index || part == kPartChoose || part == kPartSubmit)) {
        if (part == kPartChoose) {
            if (owner_hwnd) open_file_dialog(owner_hwnd);
        } else if (part == kPartSubmit) {
            start_upload(-1);
        } else if (part == kPartPreview && index >= 0) {
            set_preview_open(index, true);
        } else if (part == kPartDownload && index >= 0) {
            notify_upload(9, index, 1);
        } else if (part == kPartRemove && index >= 0) {
            remove_file(index);
        }
    }
    pressed = false;
    m_press_part = kPartNone;
    m_press_index = -1;
    invalidate();
}

void Upload::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE) set_preview_open(-1, false);
    else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (preview_open) set_preview_open(-1, false);
        else if (owner_hwnd) open_file_dialog(owner_hwnd);
    }
}

void Upload::on_blur() {
    has_focus = false;
    pressed = false;
    invalidate();
}
