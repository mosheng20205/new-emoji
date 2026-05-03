#include "element_upload.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <commdlg.h>
#include <cstring>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
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
    if (upload_cb) upload_cb(id, action, index, value);
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
        item.status = 1;
        item.progress = 100;
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
    }
    sync_files_from_items();
    invalidate();
}

void Upload::set_options(int multiple_enabled, int auto_upload_enabled) {
    multiple = multiple_enabled != 0 ? 1 : 0;
    auto_upload = auto_upload_enabled != 0 ? 1 : 0;
    invalidate();
}

void Upload::set_selected_files(const std::vector<std::wstring>& values) {
    file_items.clear();
    for (const auto& value : values) {
        if (value.empty()) continue;
        UploadFileItem item;
        item.name = display_name_for_path(value);
        item.full_path = value;
        item.status = auto_upload ? 2 : 0;
        item.progress = auto_upload ? 0 : 0;
        file_items.push_back(item);
    }
    sync_files_from_items();
    last_selected_files = selected_files_text();
    last_selected_count = (int)file_items.size();
    selected_count += last_selected_count;
    last_action = 2;
    notify_select();
    if (auto_upload && !file_items.empty()) {
        upload_request_count += (int)file_items.size();
        last_action = 3;
        notify_upload(3, -1, (int)file_items.size());
    }
    invalidate();
}

void Upload::set_file_status(int index, int status, int progress) {
    if (index < 0 || index >= (int)file_items.size()) return;
    if (status < 0) status = 0;
    if (status > 3) status = 3;
    if (progress < 0) progress = 0;
    if (progress > 100) progress = 100;
    file_items[index].status = status;
    file_items[index].progress = progress;
    last_action = 7;
    notify_upload(7, index, progress);
    invalidate();
}

void Upload::remove_file(int index) {
    if (index < 0 || index >= (int)file_items.size()) return;
    file_items.erase(file_items.begin() + index);
    sync_files_from_items();
    ++remove_count;
    last_action = 5;
    notify_upload(5, index, (int)file_items.size());
    invalidate();
}

void Upload::retry_file(int index) {
    if (index < 0 || index >= (int)file_items.size()) return;
    file_items[index].status = 2;
    file_items[index].progress = 0;
    ++retry_count;
    ++upload_request_count;
    last_action = 4;
    notify_upload(4, index, 0);
    invalidate();
}

void Upload::clear_files() {
    file_items.clear();
    files.clear();
    last_selected_files.clear();
    last_selected_count = 0;
    last_action = 6;
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
        last_action = 3;
        invalidate();
    }
    return started;
}

int Upload::open_file_dialog(HWND hwnd) {
    wchar_t buffer[32768];
    std::memset(buffer, 0, sizeof(buffer));
    OPENFILENAMEW ofn = {};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = L"所有文件 (*.*)\0*.*\0\0";
    ofn.lpstrFile = buffer;
    ofn.nMaxFile = 32768;
    ofn.lpstrTitle = L"请选择要上传的文件";
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
    set_selected_files(selected);
    return (int)selected.size();
}

void Upload::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

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

    float pad = 12.0f;
    float drop_h = (std::min)(118.0f, (std::max)(78.0f, (float)bounds.h * 0.48f));
    if (drop_h > (float)bounds.h - 24.0f) drop_h = (float)bounds.h - 24.0f;
    D2D1_RECT_F drop = { pad, pad, (float)bounds.w - pad, pad + drop_h };
    ctx.rt->FillRoundedRectangle(ROUNDED(drop, radius, radius), ctx.get_brush(drop_bg));

    float dash = 7.0f;
    float gap = 5.0f;
    for (float x = drop.left + 1.0f; x < drop.right - 1.0f; x += dash + gap) {
        ctx.rt->DrawLine(D2D1::Point2F(x, drop.top + 0.5f),
                         D2D1::Point2F((std::min)(x + dash, drop.right - 1.0f), drop.top + 0.5f),
                         ctx.get_brush(border), 1.0f);
        ctx.rt->DrawLine(D2D1::Point2F(x, drop.bottom - 0.5f),
                         D2D1::Point2F((std::min)(x + dash, drop.right - 1.0f), drop.bottom - 0.5f),
                         ctx.get_brush(border), 1.0f);
    }
    for (float y = drop.top + 1.0f; y < drop.bottom - 1.0f; y += dash + gap) {
        ctx.rt->DrawLine(D2D1::Point2F(drop.left + 0.5f, y),
                         D2D1::Point2F(drop.left + 0.5f, (std::min)(y + dash, drop.bottom - 1.0f)),
                         ctx.get_brush(border), 1.0f);
        ctx.rt->DrawLine(D2D1::Point2F(drop.right - 0.5f, y),
                         D2D1::Point2F(drop.right - 0.5f, (std::min)(y + dash, drop.bottom - 1.0f)),
                         ctx.get_brush(border), 1.0f);
    }

    float cx = (drop.left + drop.right) * 0.5f;
    float icon_y = drop.top + 24.0f;
    ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx, icon_y + 34.0f),
                     ctx.get_brush(t->accent), 2.2f);
    ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx - 12.0f, icon_y + 14.0f),
                     ctx.get_brush(t->accent), 2.2f);
    ctx.rt->DrawLine(D2D1::Point2F(cx, icon_y + 2.0f), D2D1::Point2F(cx + 12.0f, icon_y + 14.0f),
                     ctx.get_brush(t->accent), 2.2f);
    ctx.rt->DrawLine(D2D1::Point2F(cx - 20.0f, icon_y + 38.0f),
                     D2D1::Point2F(cx + 20.0f, icon_y + 38.0f),
                     ctx.get_brush(t->accent), 2.0f);

    std::wstring title_text = title.empty() ? L"📤 点击或拖拽文件到此处上传" : title;
    draw_text(ctx, title_text, style, fg, drop.left + 12.0f, drop.top + 62.0f,
              drop.right - drop.left - 24.0f, 24.0f, 1.0f, DWRITE_TEXT_ALIGNMENT_CENTER);
    if (!tip.empty()) {
        draw_text(ctx, tip, style, muted, drop.left + 12.0f, drop.top + 88.0f,
                  drop.right - drop.left - 24.0f, 22.0f, 0.88f, DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    float list_top = drop.bottom + 10.0f;
    float row_h = 26.0f;
    int max_rows = (int)(((float)bounds.h - list_top - pad) / row_h);
    max_rows = (std::max)(0, max_rows);
    int count = (std::min)((int)file_items.size(), max_rows);
    if (file_items.empty() && max_rows > 0) {
        draw_text(ctx, L"\U0001F4ED \u6682\u65E0\u4E0A\u4F20\u6587\u4EF6", style, muted,
                  pad + 8.0f, list_top, (float)bounds.w - pad * 2.0f - 16.0f,
                  row_h, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    for (int i = 0; i < count; ++i) {
        const UploadFileItem& item = file_items[i];
        float y = list_top + row_h * (float)i;
        D2D1_RECT_F row = { pad, y, (float)bounds.w - pad, y + row_h - 4.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
            ctx.get_brush(i % 2 == 0 ? with_alpha(t->accent, dark ? 0x12 : 0x0C) : bg));
        std::wstring mark = item.status == 2 ? L"…" : (item.status == 3 ? L"!" : (item.status == 0 ? L"○" : L"✓"));
        Color mark_color = item.status == 3 ? 0xFFE74C3C : (item.status == 2 ? 0xFFE6A23C : t->accent);
        draw_text(ctx, mark, style, mark_color, row.left + 8.0f, row.top, 20.0f,
                  row.bottom - row.top, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);
        float progress_w = 0.0f;
        if (item.status == 2 || item.status == 3) progress_w = 48.0f;
        draw_text(ctx, item.name, style, fg, row.left + 34.0f, row.top,
                  row.right - row.left - 44.0f - progress_w, row.bottom - row.top, 0.92f);
        if (item.status == 2 || item.status == 3) {
            std::wstring progress = item.status == 3 ? L"\u91CD\u8BD5" : std::to_wstring(item.progress) + L"%";
            draw_text(ctx, progress, style, t->text_secondary, row.right - 56.0f, row.top,
                      48.0f, row.bottom - row.top, 0.82f, DWRITE_TEXT_ALIGNMENT_TRAILING);
        }
    }
    if ((int)file_items.size() > count && max_rows > 0) {
        std::wstring more = L"还有 " + std::to_wstring((int)file_items.size() - count) + L" 个文件";
        float y = list_top + row_h * (float)count;
        draw_text(ctx, more, style, muted, pad + 8.0f, y,
                  (float)bounds.w - pad * 2.0f - 16.0f, row_h, 0.86f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Upload::on_mouse_enter() {
    hovered = true;
    invalidate();
}

void Upload::on_mouse_leave() {
    hovered = false;
    pressed = false;
    invalidate();
}

void Upload::on_mouse_down(int, int, MouseButton) {
    pressed = true;
    invalidate();
}

void Upload::on_mouse_up(int, int, MouseButton) {
    pressed = false;
    if (owner_hwnd) open_file_dialog(owner_hwnd);
    invalidate();
}
