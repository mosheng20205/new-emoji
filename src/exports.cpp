#include "exports.h"
#include "factory.h"
#include "window_state.h"
#include <shellscalingapi.h>
#include <algorithm>
#include <set>

extern HMODULE g_module;
#include "render_context.h"
#include "theme.h"
#include "element_tree.h"
#include "element_panel.h"
#include "element_button.h"
#include "element_editbox.h"
#include "element_infobox.h"
#include "element_message.h"
#include "element_messagebox.h"
#include "element_text.h"
#include "element_link.h"
#include "element_icon.h"
#include "element_space.h"
#include "element_container.h"
#include "element_layout.h"
#include "element_border.h"
#include "element_checkbox.h"
#include "element_radio.h"
#include "element_switch.h"
#include "element_slider.h"
#include "element_inputnumber.h"
#include "element_input.h"
#include "element_inputgroup.h"
#include "element_inputtag.h"
#include "element_select.h"
#include "element_rate.h"
#include "element_colorpicker.h"
#include "element_tag.h"
#include "element_badge.h"
#include "element_progress.h"
#include "element_avatar.h"
#include "element_empty.h"
#include "element_skeleton.h"
#include "element_descriptions.h"
#include "element_table.h"
#include "xlsx_table_io.h"
#include "element_card.h"
#include "element_collapse.h"
#include "element_timeline.h"
#include "element_statistic.h"
#include "element_metrics.h"
#include "element_dashboard.h"
#include "element_charts.h"
#include "element_divider.h"
#include "element_calendar.h"
#include "element_treeview.h"
#include "element_transfer.h"
#include "element_autocomplete.h"
#include "element_mentions.h"
#include "element_cascader.h"
#include "element_datepicker.h"
#include "element_daterangepicker.h"
#include "element_timepicker.h"
#include "element_datetimepicker.h"
#include "element_timeselect.h"
#include "element_treeselect.h"
#include "element_selectv2.h"
#include "element_dropdown.h"
#include "element_menu.h"
#include "element_anchor.h"
#include "element_backtop.h"
#include "element_segmented.h"
#include "element_pageheader.h"
#include "element_affix.h"
#include "element_watermark.h"
#include "element_image.h"
#include "element_carousel.h"
#include "element_upload.h"
#include "element_infinite_scroll.h"
#include "element_breadcrumb.h"
#include "element_tabs.h"
#include "element_pagination.h"
#include "element_steps.h"
#include "element_alert.h"
#include "element_result.h"
#include "element_notification.h"
#include "element_loading.h"
#include "element_dialog.h"
#include "element_drawer.h"
#include "element_tooltip.h"
#include "element_popover.h"
#include "element_popconfirm.h"
#include "element_tour.h"
#include "utf8_helpers.h"
#include "dpi_context.h"
#include <map>
#include <string>
#include <vector>
#include <cstring>
#include <cmath>
#include <cstdlib>
#include <cwchar>

static int scale_to_px(int v, float scale) {
    return (int)std::lround((float)v * scale);
}

// ── Window management ────────────────────────────────────────────────

HWND __stdcall EU_CreateWindow(const unsigned char* title_bytes, int title_len,
                               int x, int y, int w, int h, Color titlebar_color) {
    register_window_class();
    ensure_factories();
    init_themes();

    std::wstring title = utf8_to_wide(title_bytes, title_len);

    // Enter per-monitor DPI awareness before querying monitor DPI. Otherwise the
    // first window can be created at 100% physical size while its elements scale up.
    DPI_AWARENESS_CONTEXT oldCtx = SetThreadDpiAwarenessContext(
        DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    bool pmAware = (GetThreadDpiAwarenessContext() == DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

    // Detect DPI at target position, scale window size
    POINT pt = { x, y };
    HMONITOR mon = MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST);
    UINT dpiX = 96, dpiY = 96;
    GetDpiForMonitor(mon, MDT_EFFECTIVE_DPI, &dpiX, &dpiY);
    float scale = dpiX / 96.0f;
    int sw = scale_to_px(w, scale);
    int sh = scale_to_px(h, scale);

    // Pure popup — no native frame; resize and DPI handled manually
    DWORD style = WS_POPUP | WS_CLIPCHILDREN;

    HWND hwnd = CreateWindowExW(
        WS_EX_ACCEPTFILES, L"NewEmojiWindow", title.c_str(), style,
        x, y, sw, sh,
        nullptr, nullptr, g_module,
        (LPVOID)(UINT_PTR)titlebar_color);
    if (oldCtx) SetThreadDpiAwarenessContext(oldCtx);
    if (pmAware) {
        WindowState* st = window_state(hwnd);
        if (st) st->pm_aware = true;
    }

    return hwnd;
}

HWND __stdcall EU_CreateWindowDark(const unsigned char* title_bytes, int title_len,
                                   int x, int y, int w, int h, Color titlebar_color) {
    HWND hwnd = EU_CreateWindow(title_bytes, title_len, x, y, w, h, titlebar_color);
    set_window_theme_mode(hwnd, THEME_MODE_DARK);
    InvalidateRect(hwnd, nullptr, FALSE);
    return hwnd;
}

void __stdcall EU_DestroyWindow(HWND hwnd) {
    if (hwnd && IsWindow(hwnd)) {
        DestroyWindow(hwnd);
    }
}

void __stdcall EU_ShowWindow(HWND hwnd, int visible) {
    ShowWindow(hwnd, visible ? SW_SHOW : SW_HIDE);
}

void __stdcall EU_SetWindowTitle(HWND hwnd, const unsigned char* bytes, int len) {
    std::wstring title = utf8_to_wide(bytes, len);
    SetWindowTextW(hwnd, title.c_str());
    InvalidateRect(hwnd, nullptr, FALSE);
}

void __stdcall EU_SetWindowBounds(HWND hwnd, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    float scale = st ? st->dpi_scale : 1.0f;
    SetWindowPos(hwnd, nullptr, x, y, scale_to_px(w, scale), scale_to_px(h, scale),
                 SWP_NOZORDER | SWP_NOACTIVATE);
}

int __stdcall EU_GetWindowBounds(HWND hwnd, int* x, int* y, int* w, int* h) {
    ScopedWindowDpiAwareness dpi(hwnd);
    RECT rc;
    if (!GetWindowRect(hwnd, &rc)) return 0;
    WindowState* st = window_state(hwnd);
    float scale = (st && st->dpi_scale > 0.0f) ? st->dpi_scale : 1.0f;
    if (x) *x = rc.left;
    if (y) *y = rc.top;
    if (w) *w = (int)std::lround((rc.right - rc.left) / scale);
    if (h) *h = (int)std::lround((rc.bottom - rc.top) / scale);
    return 1;
}

// ── Element creation ─────────────────────────────────────────────────

static int next_element_id = 1;

int __stdcall EU_CreatePanel(HWND hwnd, int parent_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = st->element_tree->find_by_id(parent_id);
    if (!parent) parent = st->element_tree->root();

    auto panel = std::make_unique<Panel>();
    panel->set_logical_bounds({ x, y, w, h });
    ElementStyle logical_style = panel->style;
    logical_style.bg_color = 0;  // Transparent by default
    logical_style.corner_radius = 6.0f;
    panel->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(panel));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateButton(HWND hwnd, int parent_id,
                              const unsigned char* emoji_bytes, int emoji_len,
                              const unsigned char* text_bytes, int text_len,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = st->element_tree->find_by_id(parent_id);
    if (!parent) parent = st->element_tree->root();

    auto btn = std::make_unique<Button>();
    btn->set_logical_bounds({ x, y, w, h });
    btn->emoji = utf8_to_wide(emoji_bytes, emoji_len);
    btn->text  = utf8_to_wide(text_bytes, text_len);

    ElementStyle logical_style = btn->style;
    logical_style.bg_color     = 0;
    logical_style.border_color = 0;
    logical_style.fg_color     = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size    = 14.0f;
    logical_style.pad_left     = 6;
    logical_style.pad_right    = 6;
    logical_style.pad_top      = 4;
    logical_style.pad_bottom   = 4;
    btn->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(btn));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateEditBox(HWND hwnd, int parent_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = st->element_tree->find_by_id(parent_id);
    if (!parent) parent = st->element_tree->root();

    auto eb = std::make_unique<EditBox>();
    eb->set_logical_bounds({ x, y, w, h });

    ElementStyle logical_style = eb->style;
    logical_style.bg_color     = 0;
    logical_style.border_color = 0;
    logical_style.fg_color     = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size    = 14.0f;
    logical_style.pad_left     = 6;
    logical_style.pad_right    = 6;
    logical_style.pad_top      = 4;
    logical_style.pad_bottom   = 4;
    eb->set_logical_style(logical_style);
    eb->focus_border       = 0;

    Element* raw = st->element_tree->add_child(parent, std::move(eb));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateInfoBox(HWND hwnd, int parent_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* text_bytes, int text_len,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = st->element_tree->find_by_id(parent_id);
    if (!parent) parent = st->element_tree->root();

    auto box = std::make_unique<InfoBox>();
    box->set_logical_bounds({ x, y, w, h });
    box->header = utf8_to_wide(title_bytes, title_len);
    box->text = utf8_to_wide(text_bytes, text_len);

    ElementStyle logical_style = box->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 8.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_right = 12;
    logical_style.pad_top = 10;
    logical_style.pad_bottom = 10;
    box->set_logical_style(logical_style);
    box->accent_color = 0;

    Element* raw = st->element_tree->add_child(parent, std::move(box));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static Element* find_parent_or_root(WindowState* st, int parent_id) {
    if (!st || !st->element_tree) return nullptr;
    Element* parent = st->element_tree->find_by_id(parent_id);
    return parent ? parent : st->element_tree->root();
}

template <typename T>
static int create_text_like(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<T>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

template <typename T>
static T* find_typed_element(HWND hwnd, int element_id) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return nullptr;
    Element* el = st->element_tree->find_by_id(element_id);
    return dynamic_cast<T*>(el);
}

static std::vector<std::wstring> split_option_list(const unsigned char* bytes, int len) {
    std::vector<std::wstring> items;
    std::wstring full = utf8_to_wide(bytes, len);
    std::wstring current;
    for (wchar_t ch : full) {
        if (ch == L'|' || ch == L'\n' || ch == L'\r') {
            if (!current.empty()) {
                items.push_back(current);
                current.clear();
            }
        } else {
            current.push_back(ch);
        }
    }
    if (!current.empty()) items.push_back(current);
    return items;
}

static std::vector<std::wstring> split_option_list_keep_empty(const unsigned char* bytes, int len) {
    std::vector<std::wstring> items;
    std::wstring full = utf8_to_wide(bytes, len);
    if (full.empty()) return items;
    std::wstring current;
    for (wchar_t ch : full) {
        if (ch == L'|' || ch == L'\n' || ch == L'\r') {
            items.push_back(current);
            current.clear();
        } else {
            current.push_back(ch);
        }
    }
    items.push_back(current);
    return items;
}

static std::vector<std::wstring> split_tab_fields(const std::wstring& line) {
    std::vector<std::wstring> fields;
    std::wstring current;
    for (wchar_t ch : line) {
        if (ch == L'\t') {
            fields.push_back(current);
            current.clear();
        } else {
            current.push_back(ch);
        }
    }
    fields.push_back(current);
    return fields;
}

static bool parse_bool_field(const std::wstring& value) {
    return value == L"1" || value == L"true" || value == L"True" ||
           value == L"TRUE" || value == L"是" || value == L"真";
}

static std::vector<TabsItem> parse_tabs_items_ex(const unsigned char* bytes, int len) {
    std::vector<TabsItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    std::wstring line;
    auto flush = [&]() {
        if (line.empty()) return;
        auto fields = split_tab_fields(line);
        TabsItem item;
        if (fields.size() > 0) item.label = fields[0];
        if (fields.size() > 1) item.name = fields[1];
        if (fields.size() > 2) item.content = fields[2];
        if (fields.size() > 3) item.icon = fields[3];
        if (fields.size() > 4) item.disabled = parse_bool_field(fields[4]);
        if (fields.size() > 5) item.closable = parse_bool_field(fields[5]);
        items.push_back(item);
        line.clear();
    };
    for (wchar_t ch : full) {
        if (ch == L'|' || ch == L'\n' || ch == L'\r') flush();
        else line.push_back(ch);
    }
    flush();
    return items;
}

static std::vector<std::wstring> split_wide_list(const std::wstring& full,
                                                 const std::wstring& separators) {
    std::vector<std::wstring> items;
    std::wstring current;
    for (wchar_t ch : full) {
        if (separators.find(ch) != std::wstring::npos) {
            items.push_back(current);
            current.clear();
        } else {
            current.push_back(ch);
        }
    }
    items.push_back(current);
    return items;
}

static std::vector<RadioGroupItem> parse_radio_group_items(const unsigned char* bytes, int len) {
    std::vector<RadioGroupItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        RadioGroupItem item;
        item.text = fields.empty() ? row : fields[0];
        item.value = fields.size() >= 2 ? fields[1] : item.text;
        item.disabled = fields.size() >= 3 && _wtoi(fields[2].c_str()) != 0;
        if (!item.text.empty()) items.push_back(item);
    }
    return items;
}

static std::vector<CheckboxGroupItem> parse_checkbox_group_items(const unsigned char* bytes, int len) {
    std::vector<CheckboxGroupItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        CheckboxGroupItem item;
        item.text = fields.empty() ? row : fields[0];
        item.value = fields.size() >= 2 ? fields[1] : item.text;
        item.disabled = fields.size() >= 3 && _wtoi(fields[2].c_str()) != 0;
        if (!item.text.empty()) items.push_back(item);
    }
    return items;
}

static std::vector<std::wstring> parse_checkbox_checked_values(const unsigned char* bytes, int len) {
    std::vector<std::wstring> values;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& value : split_wide_list(full, L"\n\r")) {
        if (!value.empty()) values.push_back(value);
    }
    return values;
}

static std::vector<AutocompleteSuggestion> parse_autocomplete_suggestions(const unsigned char* bytes, int len) {
    std::vector<AutocompleteSuggestion> items;
    std::wstring full = utf8_to_wide(bytes, len);
    if (full.find(L'\t') == std::wstring::npos) {
        for (const auto& value : split_option_list(bytes, len)) {
            if (value.empty()) continue;
            items.push_back({ value, L"", value });
        }
        return items;
    }
    for (const auto& row : split_wide_list(full, L"\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        AutocompleteSuggestion item;
        item.title = fields.empty() ? row : fields[0];
        item.subtitle = fields.size() >= 2 ? fields[1] : L"";
        item.value = fields.size() >= 3 ? fields[2] : item.title;
        if (!item.title.empty()) items.push_back(item);
    }
    return items;
}

static std::vector<std::pair<std::wstring, std::wstring>> parse_select_pairs(const unsigned char* bytes, int len) {
    std::vector<std::pair<std::wstring, std::wstring>> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        std::wstring label = fields.empty() ? row : fields[0];
        std::wstring value = fields.size() >= 2 ? fields[1] : label;
        if (!label.empty()) items.push_back({ label, value });
    }
    return items;
}

static std::vector<std::pair<std::wstring, std::wstring>>
parse_description_items(const unsigned char* bytes, int len) {
    std::vector<std::pair<std::wstring, std::wstring>> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        size_t pos = entry.find(L':');
        if (pos == std::wstring::npos) pos = entry.find(L'=');
        if (pos == std::wstring::npos) pos = entry.find(L'：');
        if (pos == std::wstring::npos) {
            items.push_back({ L"", entry });
        } else {
            items.push_back({ entry.substr(0, pos), entry.substr(pos + 1) });
        }
    }
    return items;
}

static int parse_int_field(const std::wstring& value, int fallback = 0) {
    if (value.empty()) return fallback;
    wchar_t* end = nullptr;
    long parsed = std::wcstol(value.c_str(), &end, 10);
    return end == value.c_str() ? fallback : (int)parsed;
}

static Color parse_description_color_field(const std::wstring& value) {
    if (value.empty() || value == L"0") return 0;
    std::wstring v = value;
    if (!v.empty() && v[0] == L'#') v = L"0xFF" + v.substr(1);
    int base = 10;
    const wchar_t* start = v.c_str();
    if (v.size() > 2 && v[0] == L'0' && (v[1] == L'x' || v[1] == L'X')) {
        base = 16;
        start += 2;
    }
    wchar_t* end = nullptr;
    unsigned long parsed = std::wcstoul(start, &end, base);
    if (end == start) return 0;
    return (Color)parsed;
}

static std::vector<DescriptionItem>
parse_description_items_ex(const unsigned char* bytes, int len) {
    std::vector<DescriptionItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        DescriptionItem item;
        if (fields.size() >= 1) item.label = fields[0];
        if (fields.size() >= 2) item.content = fields[1];
        if (fields.size() >= 3) item.span = (std::max)(1, parse_int_field(fields[2], 1));
        if (fields.size() >= 4) item.label_icon = fields[3];
        if (fields.size() >= 5) item.content_type = (std::max)(0, (std::min)(1, parse_int_field(fields[4])));
        if (fields.size() >= 6) item.tag_type = (std::max)(0, (std::min)(4, parse_int_field(fields[5])));
        if (fields.size() >= 7) item.content_align = (std::max)(0, (std::min)(2, parse_int_field(fields[6])));
        if (fields.size() >= 8) item.label_bg = parse_description_color_field(fields[7]);
        if (fields.size() >= 9) item.content_bg = parse_description_color_field(fields[8]);
        if (fields.size() >= 10) item.label_fg = parse_description_color_field(fields[9]);
        if (fields.size() >= 11) item.content_fg = parse_description_color_field(fields[10]);
        items.push_back(item);
    }
    return items;
}

static std::vector<std::vector<std::wstring>>
parse_table_rows(const unsigned char* bytes, int len) {
    std::vector<std::vector<std::wstring>> rows;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"|\n\r")) {
        if (row.empty()) continue;
        rows.push_back(split_wide_list(row, L",\t;"));
    }
    return rows;
}

static std::vector<CollapseItem> parse_collapse_items(const unsigned char* bytes, int len) {
    std::vector<CollapseItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        size_t pos = entry.find(L':');
        if (pos == std::wstring::npos) pos = entry.find(L'=');
        if (pos == std::wstring::npos) {
            items.push_back({ entry, L"" });
        } else {
            items.push_back({ entry.substr(0, pos), entry.substr(pos + 1) });
        }
    }
    return items;
}

static std::wstring trim_wide(const std::wstring& value) {
    const wchar_t* ws = L" \t\r\n";
    size_t first = value.find_first_not_of(ws);
    if (first == std::wstring::npos) return L"";
    size_t last = value.find_last_not_of(ws);
    return value.substr(first, last - first + 1);
}

static int parse_timeline_placement(const std::wstring& value, int fallback) {
    std::wstring v = trim_wide(value);
    if (v.empty()) return fallback;
    if (v == L"top" || v == L"顶部" || v == L"上方") return 0;
    if (v == L"bottom" || v == L"底部" || v == L"下方") return 1;
    int parsed = _wtoi(v.c_str());
    return parsed == 1 ? 1 : 0;
}

static int parse_timeline_size(const std::wstring& value) {
    std::wstring v = trim_wide(value);
    if (v == L"large" || v == L"大" || v == L"大号") return 1;
    return _wtoi(v.c_str()) > 0 ? 1 : 0;
}

static Color parse_timeline_color(const std::wstring& value) {
    std::wstring v = trim_wide(value);
    if (v.empty()) return 0;
    int base = 10;
    if (!v.empty() && v[0] == L'#') {
        v = v.substr(1);
        base = 16;
    } else if (v.size() > 2 && v[0] == L'0' && (v[1] == L'x' || v[1] == L'X')) {
        v = v.substr(2);
        base = 16;
    }
    wchar_t* end = nullptr;
    unsigned long parsed = std::wcstoul(v.c_str(), &end, base);
    if (!end || *end != L'\0') return 0;
    Color color = (Color)parsed;
    if (base == 16 && v.size() <= 6) color |= 0xFF000000;
    if ((color >> 24) == 0) color |= 0xFF000000;
    return color;
}

static std::wstring normalize_timeline_icon(const std::wstring& value) {
    std::wstring icon = trim_wide(value);
    if (icon == L"el-icon-more") return L"⋯";
    return icon;
}

static std::vector<TimelineItem> parse_timeline_items(const unsigned char* bytes, int len) {
    std::vector<TimelineItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        bool colon_fallback = false;
        if (fields.size() < 2) {
            fields = split_wide_list(entry, L":");
            colon_fallback = true;
        }
        TimelineItem item;
        if (!fields.empty()) item.time = fields[0];
        if (fields.size() >= 2) item.content = fields[1];
        if (fields.size() >= 3 && !fields[2].empty()) {
            item.item_type = _wtoi(fields[2].c_str());
        }
        if (fields.size() >= 4) item.icon = normalize_timeline_icon(fields[3]);
        if (colon_fallback && fields.size() > 4) {
            for (size_t i = 4; i < fields.size(); ++i) {
                item.content += L":";
                item.content += fields[i];
            }
        } else {
            if (fields.size() >= 5) item.color = parse_timeline_color(fields[4]);
            if (fields.size() >= 6) item.size = parse_timeline_size(fields[5]);
            if (fields.size() >= 7) item.placement = parse_timeline_placement(fields[6], -1);
            if (fields.size() >= 8) item.card_title = fields[7];
            if (fields.size() >= 9) item.card_body = fields[8];
        }
        items.push_back(item);
    }
    return items;
}

static std::set<int> parse_index_set(const unsigned char* bytes, int len) {
    std::set<int> values;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& item : split_wide_list(full, L",;|\t\n\r")) {
        if (item.empty()) continue;
        values.insert(_wtoi(item.c_str()));
    }
    return values;
}

static float parse_chart_value(const std::wstring& text) {
    if (text.empty()) return 0.0f;
    return (float)_wtof(text.c_str());
}

static std::vector<ChartPoint> parse_chart_points_wide(const std::wstring& full) {
    std::vector<ChartPoint> points;
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        if (fields.size() < 2) fields = split_wide_list(entry, L":=,");
        ChartPoint item;
        item.label = fields.empty() ? entry : fields[0];
        item.value = fields.size() >= 2 ? parse_chart_value(fields[1]) : 0.0f;
        if (item.value < 0.0f) item.value = 0.0f;
        points.push_back(item);
    }
    return points;
}

static std::vector<ChartPoint> parse_chart_points(const unsigned char* bytes, int len) {
    return parse_chart_points_wide(utf8_to_wide(bytes, len));
}

static std::vector<std::vector<ChartPoint>> parse_chart_series(const unsigned char* bytes, int len) {
    std::vector<std::vector<ChartPoint>> series;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& part : split_wide_list(full, L"#")) {
        auto points = parse_chart_points_wide(part);
        if (!points.empty()) series.push_back(points);
    }
    return series;
}

static std::vector<TreeViewItem> parse_tree_items(const unsigned char* bytes, int len) {
    std::vector<TreeViewItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        TreeViewItem item;
        item.label = fields.empty() ? entry : fields[0];
        if (fields.size() >= 2 && !fields[1].empty()) item.level = _wtoi(fields[1].c_str());
        if (fields.size() >= 3 && !fields[2].empty()) item.expanded = _wtoi(fields[2].c_str()) != 0;
        if (fields.size() >= 4 && !fields[3].empty()) item.checked = _wtoi(fields[3].c_str()) != 0;
        if (fields.size() >= 5 && !fields[4].empty()) item.lazy = _wtoi(fields[4].c_str()) != 0;
        if (fields.size() >= 6 && !fields[5].empty()) item.key = fields[5];
        if (fields.size() >= 7 && !fields[6].empty()) item.disabled = _wtoi(fields[6].c_str()) != 0;
        if (fields.size() >= 8 && !fields[7].empty()) item.leaf = _wtoi(fields[7].c_str()) != 0;
        if (fields.size() >= 9) item.icon = fields[8];
        if (fields.size() >= 10) item.tag = fields[9];
        if (fields.size() >= 11) item.actions = fields[10];
        if (item.level < 0) item.level = 0;
        if (item.level > 12) item.level = 12;
        items.push_back(item);
    }
    return items;
}

static std::vector<TransferItem> parse_transfer_items_ex(const unsigned char* bytes, int len) {
    std::vector<TransferItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        TransferItem item;
        item.key = fields.size() >= 1 ? fields[0] : L"";
        item.label = fields.size() >= 2 ? fields[1] : item.key;
        item.value = fields.size() >= 3 ? fields[2] : item.key;
        item.desc = fields.size() >= 4 ? fields[3] : L"";
        item.pinyin = fields.size() >= 5 ? fields[4] : L"";
        item.disabled = fields.size() >= 6 && _wtoi(fields[5].c_str()) != 0;
        if (item.key.empty()) item.key = !item.value.empty() ? item.value : item.label;
        if (item.label.empty()) item.label = !item.desc.empty() ? item.desc : item.key;
        if (item.value.empty()) item.value = item.key;
        items.push_back(item);
    }
    return items;
}

static std::vector<TourStep> parse_tour_steps(const unsigned char* bytes, int len) {
    std::vector<TourStep> steps;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        if (fields.size() < 2) fields = split_wide_list(entry, L":");
        TourStep step;
        if (!fields.empty()) step.title = fields[0];
        if (fields.size() >= 2) {
            step.body = fields[1];
            for (size_t i = 2; i < fields.size(); ++i) {
                step.body += L":";
                step.body += fields[i];
            }
        }
        steps.push_back(step);
    }
    return steps;
}

static std::vector<UploadFileItem> parse_upload_file_items(const unsigned char* bytes, int len) {
    std::vector<UploadFileItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        UploadFileItem item;
        item.name = fields.empty() ? entry : fields[0];
        item.full_path = fields.size() >= 4 ? fields[3] : item.name;
        item.thumbnail_path = fields.size() >= 5 ? fields[4] : item.full_path;
        item.status = fields.size() >= 2 ? _wtoi(fields[1].c_str()) : 1;
        item.progress = fields.size() >= 3 ? _wtoi(fields[2].c_str()) : (item.status == 2 ? 50 : 100);
        item.size_bytes = fields.size() >= 6 ? _wtoi64(fields[5].c_str()) : 0;
        if (item.status < 0) item.status = 0;
        if (item.status > 3) item.status = 3;
        if (item.progress < 0) item.progress = 0;
        if (item.progress > 100) item.progress = 100;
        items.push_back(item);
    }
    return items;
}

static int copy_wide_as_utf8(const std::wstring& value, unsigned char* buffer, int buffer_size) {
    std::string utf8 = wide_to_utf8(value);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return needed;
}

static std::vector<std::pair<std::wstring, std::wstring>>
parse_pair_items(const unsigned char* bytes, int len) {
    std::vector<std::pair<std::wstring, std::wstring>> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        std::wstring title = fields.empty() ? entry : fields[0];
        std::wstring desc = fields.size() >= 2 ? fields[1] : L"";
        items.push_back({ title, desc });
    }
    return items;
}

static std::vector<StepsVisualItem> parse_steps_visual_items(const unsigned char* bytes, int len) {
    std::vector<StepsVisualItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        StepsVisualItem item;
        item.title = fields.empty() ? entry : fields[0];
        if (fields.size() >= 2) item.description = fields[1];
        if (fields.size() >= 3) item.icon = fields[2];
        if (!item.title.empty()) items.push_back(item);
    }
    return items;
}

static std::vector<InfiniteScrollItem> parse_infinite_scroll_items(const unsigned char* bytes, int len) {
    std::vector<InfiniteScrollItem> items;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& row : split_wide_list(full, L"|\n\r")) {
        if (row.empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(row, L"\t");
        InfiniteScrollItem item;
        item.title = fields.empty() ? row : fields[0];
        item.subtitle = fields.size() >= 2 ? fields[1] : L"";
        item.tag = fields.size() >= 3 ? fields[2] : L"";
        if (!item.title.empty()) items.push_back(item);
    }
    return items;
}

static std::vector<CascaderOption> parse_cascader_options(const unsigned char* bytes, int len) {
    std::vector<CascaderOption> options;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (entry.empty()) continue;
        CascaderOption opt;
        for (const auto& field : split_wide_list(entry, L"/>\\\t,")) {
            if (!field.empty()) opt.parts.push_back(field);
        }
        if (!opt.parts.empty()) options.push_back(opt);
    }
    return options;
}

int __stdcall EU_CreateText(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h) {
    return create_text_like<Text>(hwnd, parent_id, text_bytes, text_len, x, y, w, h);
}

int __stdcall EU_CreateLink(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h) {
    return create_text_like<Link>(hwnd, parent_id, text_bytes, text_len, x, y, w, h);
}

int __stdcall EU_CreateIcon(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h) {
    return create_text_like<Icon>(hwnd, parent_id, text_bytes, text_len, x, y, w, h);
}

int __stdcall EU_CreateSpace(HWND hwnd, int parent_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Space>();
    el->set_logical_bounds({ x, y, w, h });
    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateContainer(HWND hwnd, int parent_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Container>();
    el->set_logical_bounds({ x, y, w, h });

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.corner_radius = 0.0f;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateLayout(HWND hwnd, int parent_id, int orientation, int gap,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Layout>();
    el->orientation = orientation == 1 ? Layout::Vertical : Layout::Horizontal;
    el->set_logical_gap(gap);
    el->set_logical_bounds({ x, y, w, h });

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBorder(HWND hwnd, int parent_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Border>();
    el->set_logical_bounds({ x, y, w, h });

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.border_width = 1.0f;
    logical_style.corner_radius = 6.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 10;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCheckbox(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                int checked, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Checkbox>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->checked = checked != 0;

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCheckboxGroup(HWND hwnd, int parent_id,
                                     const unsigned char* items_bytes, int items_len,
                                     const unsigned char* checked_bytes, int checked_len,
                                     int style_mode, int size, int group_disabled,
                                     int min_checked, int max_checked,
                                     int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<CheckboxGroup>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_checkbox_group_items(items_bytes, items_len));
    el->set_options(group_disabled != 0, style_mode, size, min_checked, max_checked);
    el->set_checked_values(parse_checkbox_checked_values(checked_bytes, checked_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateRadio(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             int checked, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Radio>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->checked = checked != 0;

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    static_cast<Radio*>(raw)->set_checked(checked != 0);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateRadioGroup(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  const unsigned char* value_bytes, int value_len,
                                  int style_mode, int size, int group_disabled,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<RadioGroup>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_radio_group_items(items_bytes, items_len));
    el->set_options(group_disabled != 0, style_mode, size);
    std::wstring value = utf8_to_wide(value_bytes, value_len);
    if (!value.empty()) el->set_value(value);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSwitch(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int checked, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Switch>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->checked = checked != 0;

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSlider(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int min_value, int max_value, int value,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Slider>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_range(min_value, max_value);
    el->set_value(value);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 0;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateInputNumber(HWND hwnd, int parent_id,
                                   const unsigned char* text_bytes, int text_len,
                                   int value, int min_value, int max_value, int step,
                                   int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<InputNumber>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_range(min_value, max_value);
    el->set_step(step);
    el->set_value(value);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static void init_default_input_style(Input* el) {
    if (!el) return;
    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 0;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);
    el->set_visual_options(0, false, false, false, 0, 0);
}

static void init_default_button_style(Button* el) {
    if (!el) return;
    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 0;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);
}

static void init_default_select_style(Select* el) {
    if (!el) return;
    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);
}

int __stdcall EU_CreateInput(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             const unsigned char* placeholder_bytes, int placeholder_len,
                             const unsigned char* prefix_bytes, int prefix_len,
                             const unsigned char* suffix_bytes, int suffix_len,
                             int clearable,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Input>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_value(utf8_to_wide(text_bytes, text_len));
    el->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));
    el->set_affixes(utf8_to_wide(prefix_bytes, prefix_len), utf8_to_wide(suffix_bytes, suffix_len));
    el->set_clearable(clearable != 0);
    init_default_input_style(el.get());

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateInputGroup(HWND hwnd, int parent_id,
                                  const unsigned char* value_bytes, int value_len,
                                  const unsigned char* placeholder_bytes, int placeholder_len,
                                  int size, int clearable, int password,
                                  int show_word_limit, int autosize,
                                  int min_rows, int max_rows,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto group = std::make_unique<InputGroup>();
    group->set_logical_bounds({ x, y, w, h });
    group->mouse_passthrough = true;
    group->set_options(size, clearable != 0, password != 0,
                       show_word_limit != 0, autosize != 0,
                       min_rows, max_rows);

    InputGroup* group_ptr = group.get();
    Element* raw_group = st->element_tree->add_child(parent, std::move(group));

    auto input = std::make_unique<Input>();
    input->set_value(utf8_to_wide(value_bytes, value_len));
    input->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));
    init_default_input_style(input.get());
    input->set_clearable(clearable != 0);
    input->set_options(false, password != 0, false, 0);
    input->set_visual_options(size, password != 0, show_word_limit != 0, autosize != 0, min_rows, max_rows);
    Element* raw_input = st->element_tree->add_child(group_ptr, std::move(input));
    group_ptr->set_input_element_id(raw_input->id);

    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw_group->id;
}

int __stdcall EU_CreateInputTag(HWND hwnd, int parent_id,
                                const unsigned char* tags_bytes, int tags_len,
                                const unsigned char* placeholder_bytes, int placeholder_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<InputTag>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_tags(split_option_list(tags_bytes, tags_len));
    el->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 8;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateMentions(HWND hwnd, int parent_id,
                                const unsigned char* value_bytes, int value_len,
                                const unsigned char* suggestions_bytes, int suggestions_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Mentions>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_value(utf8_to_wide(value_bytes, value_len));
    el->set_suggestions(split_option_list(suggestions_bytes, suggestions_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTimeSelect(HWND hwnd, int parent_id,
                                  int hour, int minute,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<TimeSelect>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_time(hour, minute);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSelect(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              const unsigned char* options_bytes, int options_len,
                              int selected_index, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Select>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_options(split_option_list(options_bytes, options_len));
    el->set_selected_index(selected_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSelectV2(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* options_bytes, int options_len,
                                int selected_index, int visible_count,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<SelectV2>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_visible_count(visible_count);
    el->set_options(split_option_list(options_bytes, options_len));
    el->set_selected_index(selected_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 0;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateRate(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int value, int max_value,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Rate>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_max_value(max_value);
    el->set_value(value);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateColorPicker(HWND hwnd, int parent_id,
                                   const unsigned char* text_bytes, int text_len,
                                   Color value, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<ColorPicker>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_color(value);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTag(HWND hwnd, int parent_id,
                           const unsigned char* text_bytes, int text_len,
                           int tag_type, int effect, int closable,
                           int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Tag>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_type(tag_type);
    el->set_effect(effect);
    el->set_closable(closable != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 13.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 0;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBadge(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             const unsigned char* value_bytes, int value_len,
                             int max_value, int dot,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Badge>();
    el->set_logical_bounds({ x, y, w, h });
    el->mouse_passthrough = true;
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_value(utf8_to_wide(value_bytes, value_len));
    el->set_max_value(max_value);
    el->set_dot(dot != 0);
    el->set_type(0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateProgress(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                int percentage, int status,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Progress>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_percentage(percentage);
    el->set_status(status);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateAvatar(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int shape, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Avatar>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_shape(shape);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 16.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateEmpty(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* desc_bytes, int desc_len,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Empty>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_description(utf8_to_wide(desc_bytes, desc_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 10;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSkeleton(HWND hwnd, int parent_id,
                                int rows, int animated,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Skeleton>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_rows(rows);
    el->set_animated(animated != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 12;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDescriptions(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* items_bytes, int items_len,
                                    int columns, int bordered,
                                    int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Descriptions>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_items(parse_description_items(items_bytes, items_len));
    el->set_columns(columns);
    el->set_bordered(bordered != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 4;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTable(HWND hwnd, int parent_id,
                             const unsigned char* columns_bytes, int columns_len,
                             const unsigned char* rows_bytes, int rows_len,
                             int striped, int bordered,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Table>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_columns(split_option_list(columns_bytes, columns_len));
    el->set_rows(parse_table_rows(rows_bytes, rows_len));
    el->set_striped(striped != 0);
    el->set_bordered(bordered != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCard(HWND hwnd, int parent_id,
                            const unsigned char* title_bytes, int title_len,
                            const unsigned char* body_bytes, int body_len,
                            int shadow, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Card>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_shadow(shadow);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 18;
    logical_style.pad_top = 14;
    logical_style.pad_right = 18;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCollapse(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int active_index, int accordion,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Collapse>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_collapse_items(items_bytes, items_len));
    el->set_active_index(active_index);
    el->set_accordion(accordion != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTimeline(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Timeline>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_timeline_items(items_bytes, items_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 10;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateStatistic(HWND hwnd, int parent_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* prefix_bytes, int prefix_len,
                                 const unsigned char* suffix_bytes, int suffix_len,
                                 int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Statistic>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_value(utf8_to_wide(value_bytes, value_len));
    el->set_prefix(utf8_to_wide(prefix_bytes, prefix_len));
    el->set_suffix(utf8_to_wide(suffix_bytes, suffix_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 18;
    logical_style.pad_top = 14;
    logical_style.pad_right = 18;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateKpiCard(HWND hwnd, int parent_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* subtitle_bytes, int subtitle_len,
                               const unsigned char* trend_bytes, int trend_len,
                               int trend_type, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<KpiCard>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_value(utf8_to_wide(value_bytes, value_len));
    el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
    el->set_trend(utf8_to_wide(trend_bytes, trend_len), trend_type);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 14;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTrend(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* value_bytes, int value_len,
                             const unsigned char* percent_bytes, int percent_len,
                             const unsigned char* detail_bytes, int detail_len,
                             int direction, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Trend>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_value(utf8_to_wide(value_bytes, value_len));
    el->set_percent(utf8_to_wide(percent_bytes, percent_len));
    el->set_detail(utf8_to_wide(detail_bytes, detail_len));
    el->set_direction(direction);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 8;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateStatusDot(HWND hwnd, int parent_id,
                                 const unsigned char* label_bytes, int label_len,
                                 const unsigned char* desc_bytes, int desc_len,
                                 int status, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<StatusDot>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_label(utf8_to_wide(label_bytes, label_len));
    el->set_description(utf8_to_wide(desc_bytes, desc_len));
    el->set_status(status);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 6;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateGauge(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             int value,
                             const unsigned char* caption_bytes, int caption_len,
                             int status, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Gauge>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_value(value);
    el->set_caption(utf8_to_wide(caption_bytes, caption_len));
    el->set_status(status);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateRingProgress(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    int value,
                                    const unsigned char* label_bytes, int label_len,
                                    int status, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<RingProgress>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_value(value);
    el->set_label(utf8_to_wide(label_bytes, label_len));
    el->set_status(status);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBulletProgress(HWND hwnd, int parent_id,
                                      const unsigned char* title_bytes, int title_len,
                                      const unsigned char* desc_bytes, int desc_len,
                                      int value, int target, int status,
                                      int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<BulletProgress>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_description(utf8_to_wide(desc_bytes, desc_len));
    el->set_value(value);
    el->set_target(target);
    el->set_status(status);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateLineChart(HWND hwnd, int parent_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* points_bytes, int points_len,
                                 int chart_style, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<LineChart>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_points(parse_chart_points(points_bytes, points_len));
    el->set_chart_style(chart_style);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBarChart(HWND hwnd, int parent_id,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* bars_bytes, int bars_len,
                                int orientation, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<BarChart>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_bars(parse_chart_points(bars_bytes, bars_len));
    el->set_orientation(orientation);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDonutChart(HWND hwnd, int parent_id,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* slices_bytes, int slices_len,
                                  int active_index, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<DonutChart>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_slices(parse_chart_points(slices_bytes, slices_len));
    el->set_active_index(active_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 10;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDivider(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int direction, int content_position,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Divider>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_direction(direction);
    el->set_content_position(content_position);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCalendar(HWND hwnd, int parent_id,
                                int year, int month, int selected_day,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Calendar>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_date(year, month, selected_day);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 14;
    logical_style.pad_top = 10;
    logical_style.pad_right = 14;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTree(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int selected_index,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<TreeView>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_tree_items(items_bytes, items_len));
    el->set_selected_index(selected_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 8;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTreeSelect(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  int selected_index,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<TreeSelect>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_tree_items(items_bytes, items_len));
    el->set_selected_index(selected_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTransfer(HWND hwnd, int parent_id,
                                const unsigned char* left_bytes, int left_len,
                                const unsigned char* right_bytes, int right_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Transfer>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(left_bytes, left_len), split_option_list(right_bytes, right_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateAutocomplete(HWND hwnd, int parent_id,
                                    const unsigned char* value_bytes, int value_len,
                                    const unsigned char* suggestions_bytes, int suggestions_len,
                                    int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Autocomplete>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_suggestions(parse_autocomplete_suggestions(suggestions_bytes, suggestions_len));
    el->set_value(utf8_to_wide(value_bytes, value_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCascader(HWND hwnd, int parent_id,
                                const unsigned char* options_bytes, int options_len,
                                const unsigned char* selected_bytes, int selected_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Cascader>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_options(parse_cascader_options(options_bytes, options_len));
    std::wstring selected = utf8_to_wide(selected_bytes, selected_len);
    if (!selected.empty()) {
        el->set_selected_path(split_wide_list(selected, L"/>\\\t,"));
    }

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDatePicker(HWND hwnd, int parent_id,
                                  int year, int month, int selected_day,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<DatePicker>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_date(year, month, selected_day);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTimePicker(HWND hwnd, int parent_id,
                                  int hour, int minute,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<TimePicker>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_time(hour, minute);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDateTimePicker(HWND hwnd, int parent_id,
                                      int year, int month, int day,
                                      int hour, int minute,
                                      int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<DateTimePicker>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_datetime(year, month, day, hour, minute);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDropdown(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* items_bytes, int items_len,
                                int selected_index,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Dropdown>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_selected_index(selected_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 4;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateMenu(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int active_index, int orientation,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Menu>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);
    el->set_orientation(orientation);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 6;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateAnchor(HWND hwnd, int parent_id,
                              const unsigned char* items_bytes, int items_len,
                              int active_index,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Anchor>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 8;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBacktop(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Backtop>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 20.0f;
    logical_style.font_size = 18.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSegmented(HWND hwnd, int parent_id,
                                 const unsigned char* items_bytes, int items_len,
                                 int active_index,
                                 int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Segmented>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 4;
    logical_style.pad_top = 4;
    logical_style.pad_right = 4;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreatePageHeader(HWND hwnd, int parent_id,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* subtitle_bytes, int subtitle_len,
                                  const unsigned char* back_bytes, int back_len,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<PageHeader>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
    el->set_back_text(utf8_to_wide(back_bytes, back_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 14;
    logical_style.pad_top = 6;
    logical_style.pad_right = 14;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateAffix(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* body_bytes, int body_len,
                             int offset,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Affix>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_offset(offset);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 18;
    logical_style.pad_top = 10;
    logical_style.pad_right = 18;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateWatermark(HWND hwnd, int parent_id,
                                 const unsigned char* content_bytes, int content_len,
                                 int gap_x, int gap_y,
                                 int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Watermark>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_content(utf8_to_wide(content_bytes, content_len));
    el->set_gap(gap_x, gap_y);
    el->set_layer_options(parent_id, 1, 1, 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 0;
    logical_style.pad_top = 0;
    logical_style.pad_right = 0;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTour(HWND hwnd, int parent_id,
                            const unsigned char* steps_bytes, int steps_len,
                            int active_index, int open,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Tour>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_steps(parse_tour_steps(steps_bytes, steps_len));
    el->set_active_index(active_index);
    el->set_open(open != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 8.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 14;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateImage(HWND hwnd, int parent_id,
                             const unsigned char* src_bytes, int src_len,
                             const unsigned char* alt_bytes, int alt_len,
                             int fit,
                             int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Image>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_source(utf8_to_wide(src_bytes, src_len));
    el->set_alt(utf8_to_wide(alt_bytes, alt_len));
    el->set_fit(fit);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 10;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateCarousel(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int active_index, int indicator_position,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Carousel>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);
    el->set_indicator_position(indicator_position);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 15.0f;
    logical_style.pad_left = 10;
    logical_style.pad_top = 10;
    logical_style.pad_right = 10;
    logical_style.pad_bottom = 10;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateUpload(HWND hwnd, int parent_id,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* tip_bytes, int tip_len,
                              const unsigned char* files_bytes, int files_len,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Upload>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_tip(utf8_to_wide(tip_bytes, tip_len));
    el->set_files(split_option_list(files_bytes, files_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 12;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateInfiniteScroll(HWND hwnd, int parent_id,
                                      const unsigned char* items_bytes, int items_len,
                                      int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<InfiniteScroll>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(parse_infinite_scroll_items(items_bytes, items_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0x00000000;
    logical_style.border_color = 0;
    logical_style.border_width = 1.0f;
    logical_style.corner_radius = 8.0f;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 12;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateBreadcrumb(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  const unsigned char* separator_bytes, int separator_len,
                                  int current_index, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Breadcrumb>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_separator(utf8_to_wide(separator_bytes, separator_len));
    el->set_current_index(current_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTabs(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int active_index, int tab_type,
                            int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Tabs>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);
    el->set_tab_type(tab_type);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreatePagination(HWND hwnd, int parent_id,
                                  int total, int page_size, int current_page,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Pagination>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_total(total);
    el->set_page_size(page_size);
    el->set_current_page(current_page);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 0;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 0;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateSteps(HWND hwnd, int parent_id,
                             const unsigned char* items_bytes, int items_len,
                             int active_index, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Steps>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_items(split_option_list(items_bytes, items_len));
    el->set_active_index(active_index);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 8;
    logical_style.pad_top = 4;
    logical_style.pad_right = 8;
    logical_style.pad_bottom = 4;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static int create_alert_element(HWND hwnd, int parent_id,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* desc_bytes, int desc_len,
                                int alert_type, int effect, int closable,
                                int show_icon, int center, int wrap_description,
                                const unsigned char* close_text_bytes, int close_text_len,
                                int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Alert>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_description(utf8_to_wide(desc_bytes, desc_len));
    el->set_type(alert_type);
    el->set_effect(effect);
    el->set_closable(closable != 0);
    el->set_advanced_options(show_icon != 0, center != 0, wrap_description != 0);
    el->set_close_text(utf8_to_wide(close_text_bytes, close_text_len));

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 14;
    logical_style.pad_top = 8;
    logical_style.pad_right = 14;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateAlert(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* desc_bytes, int desc_len,
                             int alert_type, int effect, int closable,
                             int x, int y, int w, int h) {
    return create_alert_element(hwnd, parent_id,
                                title_bytes, title_len, desc_bytes, desc_len,
                                alert_type, effect, closable,
                                1, 0, 0, nullptr, 0,
                                x, y, w, h);
}

int __stdcall EU_CreateAlertEx(HWND hwnd, int parent_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* desc_bytes, int desc_len,
                               int alert_type, int effect, int closable,
                               int show_icon, int center, int wrap_description,
                               const unsigned char* close_text_bytes, int close_text_len,
                               int x, int y, int w, int h) {
    return create_alert_element(hwnd, parent_id,
                                title_bytes, title_len, desc_bytes, desc_len,
                                alert_type, effect, closable,
                                show_icon, center, wrap_description,
                                close_text_bytes, close_text_len,
                                x, y, w, h);
}

int __stdcall EU_CreateResult(HWND hwnd, int parent_id,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* subtitle_bytes, int subtitle_len,
                              int result_type,
                              int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Result>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
    el->set_type(result_type);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_top = 12;
    logical_style.pad_right = 16;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateNotification(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* body_bytes, int body_len,
                                    int notify_type, int closable,
                                    int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Notification>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_type(notify_type);
    el->set_closable(closable != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 18;
    logical_style.pad_top = 14;
    logical_style.pad_right = 14;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static Rect logical_client_rect(WindowState* st) {
    RECT rc{};
    if (!st || !st->hwnd) return { 0, 0, 800, 600 };
    GetClientRect(st->hwnd, &rc);
    float scale = st->dpi_scale > 0.0f ? st->dpi_scale : 1.0f;
    return { 0, 0, (int)std::lround((rc.right - rc.left) / scale),
             (int)std::lround((rc.bottom - rc.top) / scale) };
}

template <typename T>
static int visible_service_count(Element* root) {
    if (!root) return 0;
    int count = 0;
    for (auto& ch : root->children) {
        if (ch && ch->visible && dynamic_cast<T*>(ch.get())) ++count;
    }
    return count;
}

int __stdcall EU_ShowMessage(HWND hwnd,
                             const unsigned char* text_bytes, int text_len,
                             int message_type, int closable, int center, int rich,
                             int duration_ms, int offset) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Rect client = logical_client_rect(st);
    int w = (std::min)(420, (std::max)(260, client.w - 48));
    int h = 46;
    int gap = 12;
    int index = visible_service_count<Message>(st->element_tree->root());
    int x = (client.w - w) / 2;
    int y = (std::max)(0, offset) + index * (h + gap);

    auto el = std::make_unique<Message>();
    el->set_logical_bounds({ x, y, w, h });
    el->set_text(utf8_to_wide(text_bytes, text_len));
    el->set_options(message_type, closable != 0, center != 0, rich != 0, duration_ms, offset);
    el->stack_index = index;
    el->stack_gap = gap;

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 16;
    logical_style.pad_right = 12;
    logical_style.pad_top = 8;
    logical_style.pad_bottom = 8;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static Rect notification_service_rect(WindowState* st, int placement, int offset, int w, int h, int index, int gap) {
    Rect client = logical_client_rect(st);
    if (w <= 0) w = 330;
    if (h <= 0) h = 96;
    int off = (std::max)(0, offset);
    bool left = placement == 2 || placement == 3;
    bool bottom = placement == 1 || placement == 2;
    int x = left ? off : client.w - w - off;
    int y = bottom ? client.h - h - off - index * (h + gap) : off + index * (h + gap);
    if (x < 0) x = 0;
    if (y < 0) y = 0;
    return { x, y, w, h };
}

static int visible_notification_count(Element* root, int placement) {
    if (!root) return 0;
    int count = 0;
    for (auto& ch : root->children) {
        auto* n = ch ? dynamic_cast<Notification*>(ch.get()) : nullptr;
        if (n && n->visible && !n->closed && n->placement == placement) ++count;
    }
    return count;
}

int __stdcall EU_ShowNotification(HWND hwnd,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* body_bytes, int body_len,
                                  int notify_type, int closable, int duration_ms,
                                  int placement, int offset, int rich, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    int gap = 14;
    int normalized_placement = placement >= 0 && placement <= 3 ? placement : 0;
    int index = visible_notification_count(st->element_tree->root(), normalized_placement);
    Rect r = notification_service_rect(st, normalized_placement, offset, w, h, index, gap);

    auto el = std::make_unique<Notification>();
    el->set_logical_bounds(r);
    el->text = utf8_to_wide(title_bytes, title_len);
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_options(notify_type, closable != 0, duration_ms < 0 ? 4500 : duration_ms);
    el->set_placement(normalized_placement, offset);
    el->set_rich(rich != 0);
    el->stack_index = index;
    el->stack_gap = gap;

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 18;
    logical_style.pad_top = 14;
    logical_style.pad_right = 14;
    logical_style.pad_bottom = 14;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateLoading(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int active,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Loading>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(text_bytes, text_len);
    el->set_active(active != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 12;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static std::wstring utf8_or_default(const unsigned char* bytes, int len, const wchar_t* fallback);

int __stdcall EU_CreateDialog(HWND hwnd,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* body_bytes, int body_len,
                              int modal, int closable,
                              int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    auto el = std::make_unique<Dialog>();
    el->set_logical_bounds({ 0, 0, w, h });
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_modal(modal != 0);
    el->set_closable(closable != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 6.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 20;
    logical_style.pad_top = 16;
    logical_style.pad_right = 20;
    logical_style.pad_bottom = 16;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(el));
    if (auto* dlg = dynamic_cast<Dialog*>(raw)) {
        auto content = std::make_unique<Panel>();
        content->mouse_passthrough = true;
        Element* content_raw = st->element_tree->add_child(dlg, std::move(content));
        dlg->content_parent_id = content_raw ? content_raw->id : 0;
        auto footer = std::make_unique<Panel>();
        footer->mouse_passthrough = true;
        Element* footer_raw = st->element_tree->add_child(dlg, std::move(footer));
        dlg->footer_parent_id = footer_raw ? footer_raw->id : 0;
    }
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateDrawer(HWND hwnd,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* body_bytes, int body_len,
                              int placement, int modal, int closable,
                              int size) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    auto el = std::make_unique<Drawer>();
    el->set_logical_bounds({ 0, 0, size, size });
    el->size_value = size;
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_body(utf8_to_wide(body_bytes, body_len));
    el->set_placement(placement);
    el->set_modal(modal != 0);
    el->set_closable(closable != 0);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 20;
    logical_style.pad_top = 16;
    logical_style.pad_right = 20;
    logical_style.pad_bottom = 16;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(el));
    if (auto* drawer = dynamic_cast<Drawer*>(raw)) {
        auto content = std::make_unique<Panel>();
        content->mouse_passthrough = true;
        Element* content_raw = st->element_tree->add_child(drawer, std::move(content));
        drawer->content_parent_id = content_raw ? content_raw->id : 0;
        auto footer = std::make_unique<Panel>();
        footer->mouse_passthrough = true;
        Element* footer_raw = st->element_tree->add_child(drawer, std::move(footer));
        drawer->footer_parent_id = footer_raw ? footer_raw->id : 0;
    }
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreateTooltip(HWND hwnd, int parent_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* content_bytes, int content_len,
                               int placement,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Tooltip>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(label_bytes, label_len);
    el->set_content(utf8_to_wide(content_bytes, content_len));
    el->set_placement(placement);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 6;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreatePopover(HWND hwnd, int parent_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* content_bytes, int content_len,
                               int placement,
                               int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Popover>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(label_bytes, label_len);
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_content(utf8_to_wide(content_bytes, content_len));
    el->set_placement(placement);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 6;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    if (auto* pop = dynamic_cast<Popover*>(raw)) {
        auto content = std::make_unique<Panel>();
        content->mouse_passthrough = true;
        Element* content_raw = st->element_tree->add_child(pop, std::move(content));
        pop->content_parent_id = content_raw ? content_raw->id : 0;
    }
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CreatePopconfirm(HWND hwnd, int parent_id,
                                  const unsigned char* label_bytes, int label_len,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* content_bytes, int content_len,
                                  const unsigned char* confirm_bytes, int confirm_len,
                                  const unsigned char* cancel_bytes, int cancel_len,
                                  int placement,
                                  int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<Popconfirm>();
    el->set_logical_bounds({ x, y, w, h });
    el->text = utf8_to_wide(label_bytes, label_len);
    el->set_title(utf8_to_wide(title_bytes, title_len));
    el->set_content(utf8_to_wide(content_bytes, content_len));
    el->set_buttons(utf8_or_default(confirm_bytes, confirm_len, L"OK"),
                    utf8_or_default(cancel_bytes, cancel_len, L"Cancel"));
    el->set_placement(placement);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 4.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 6;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 6;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

static std::wstring utf8_or_default(const unsigned char* bytes, int len, const wchar_t* fallback) {
    std::wstring value = utf8_to_wide(bytes, len);
    return value.empty() ? std::wstring(fallback) : value;
}

static void relayout_and_invalidate(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    if (st && st->element_tree) st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

static int create_message_box(HWND hwnd,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* text_bytes, int text_len,
                              const unsigned char* confirm_bytes, int confirm_len,
                              const unsigned char* cancel_bytes, int cancel_len,
                              bool show_cancel,
                              MessageBoxResultCallback cb) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    auto box = std::make_unique<MessageBoxElement>();
    box->title = utf8_or_default(title_bytes, title_len, L"提示");
    box->text = utf8_to_wide(text_bytes, text_len);
    box->confirm_text = utf8_or_default(confirm_bytes, confirm_len, L"确定");
    box->cancel_text = utf8_or_default(cancel_bytes, cancel_len, L"取消");
    box->show_cancel = show_cancel;
    box->result_cb = cb;

    ElementStyle logical_style = box->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 8.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 20;
    logical_style.pad_right = 20;
    logical_style.pad_top = 18;
    logical_style.pad_bottom = 20;
    box->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(box));
    st->element_tree->layout();
    st->element_tree->set_focus(raw);
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_ShowMessageBox(HWND hwnd,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* confirm_bytes, int confirm_len,
                                MessageBoxResultCallback cb) {
    return create_message_box(hwnd, title_bytes, title_len, text_bytes, text_len,
                              confirm_bytes, confirm_len, nullptr, 0, false, cb);
}

int __stdcall EU_ShowConfirmBox(HWND hwnd,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* confirm_bytes, int confirm_len,
                                const unsigned char* cancel_bytes, int cancel_len,
                                MessageBoxResultCallback cb) {
    return create_message_box(hwnd, title_bytes, title_len, text_bytes, text_len,
                              confirm_bytes, confirm_len, cancel_bytes, cancel_len, true, cb);
}

static int create_message_box_ex(HWND hwnd,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* text_bytes, int text_len,
                                 const unsigned char* confirm_bytes, int confirm_len,
                                 const unsigned char* cancel_bytes, int cancel_len,
                                 int box_type, int show_cancel, int center, int rich,
                                 int distinguish_cancel_and_close,
                                 MessageBoxExCallback cb) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    auto box = std::make_unique<MessageBoxElement>();
    box->title = utf8_or_default(title_bytes, title_len, L"提示");
    box->text = utf8_to_wide(text_bytes, text_len);
    box->confirm_text = utf8_or_default(confirm_bytes, confirm_len, L"确定");
    box->cancel_text = utf8_or_default(cancel_bytes, cancel_len, L"取消");
    box->show_cancel = show_cancel != 0;
    box->result_ex_cb = cb;
    box->set_options(box_type, center != 0, rich != 0, distinguish_cancel_and_close != 0);

    ElementStyle logical_style = box->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 8.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 20;
    logical_style.pad_right = 20;
    logical_style.pad_top = 18;
    logical_style.pad_bottom = 20;
    box->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(box));
    st->element_tree->layout();
    st->element_tree->set_focus(raw);
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_ShowMessageBoxEx(HWND hwnd,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* text_bytes, int text_len,
                                  const unsigned char* confirm_bytes, int confirm_len,
                                  const unsigned char* cancel_bytes, int cancel_len,
                                  int box_type, int show_cancel, int center, int rich,
                                  int distinguish_cancel_and_close,
                                  MessageBoxExCallback cb) {
    return create_message_box_ex(hwnd, title_bytes, title_len, text_bytes, text_len,
                                 confirm_bytes, confirm_len, cancel_bytes, cancel_len,
                                 box_type, show_cancel, center, rich,
                                 distinguish_cancel_and_close, cb);
}

int __stdcall EU_ShowPromptBox(HWND hwnd,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* text_bytes, int text_len,
                               const unsigned char* placeholder_bytes, int placeholder_len,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* pattern_bytes, int pattern_len,
                               const unsigned char* error_bytes, int error_len,
                               const unsigned char* confirm_bytes, int confirm_len,
                               const unsigned char* cancel_bytes, int cancel_len,
                               int box_type, int center, int rich,
                               int distinguish_cancel_and_close,
                               MessageBoxExCallback cb) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    auto box = std::make_unique<MessageBoxElement>();
    box->title = utf8_or_default(title_bytes, title_len, L"提示");
    box->text = utf8_to_wide(text_bytes, text_len);
    box->confirm_text = utf8_or_default(confirm_bytes, confirm_len, L"确定");
    box->cancel_text = utf8_or_default(cancel_bytes, cancel_len, L"取消");
    box->show_cancel = true;
    box->result_ex_cb = cb;
    box->set_options(box_type, center != 0, rich != 0, distinguish_cancel_and_close != 0);
    box->set_input(utf8_to_wide(value_bytes, value_len),
                   utf8_or_default(placeholder_bytes, placeholder_len, L"请输入内容"),
                   utf8_to_wide(pattern_bytes, pattern_len),
                   utf8_or_default(error_bytes, error_len, L"输入内容格式不正确"));

    ElementStyle logical_style = box->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.corner_radius = 8.0f;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 20;
    logical_style.pad_right = 20;
    logical_style.pad_top = 18;
    logical_style.pad_bottom = 20;
    box->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(st->element_tree->root(), std::move(box));
    st->element_tree->layout();
    st->element_tree->set_focus(raw);
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

// ── Element properties ───────────────────────────────────────────────

void __stdcall EU_SetElementText(HWND hwnd, int element_id, const unsigned char* bytes, int len) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        el->text = utf8_to_wide(bytes, len);
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetElementText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* el = st->element_tree->find_by_id(element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->text);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int copy = needed < buffer_size ? needed : buffer_size - 1;
    memcpy(buffer, utf8.data(), copy);
    buffer[copy] = 0;
    return needed;
}

void __stdcall EU_SetElementBounds(HWND hwnd, int element_id, int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        el->set_logical_bounds({ x, y, w, h });
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetElementBounds(HWND hwnd, int element_id, int* x, int* y, int* w, int* h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* el = st->element_tree->find_by_id(element_id);
    if (!el) return 0;
    const Rect& r = el->has_logical_bounds ? el->logical_bounds : el->bounds;
    if (x) *x = r.x;
    if (y) *y = r.y;
    if (w) *w = r.w;
    if (h) *h = r.h;
    return 1;
}

void __stdcall EU_SetElementVisible(HWND hwnd, int element_id, int visible) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        el->visible = (visible != 0);
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetElementVisible(HWND hwnd, int element_id) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* el = st->element_tree->find_by_id(element_id);
    return (el && el->visible) ? 1 : 0;
}

void __stdcall EU_SetElementEnabled(HWND hwnd, int element_id, int enabled) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        el->enabled = (enabled != 0);
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetElementEnabled(HWND hwnd, int element_id) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* el = st->element_tree->find_by_id(element_id);
    return (el && el->enabled) ? 1 : 0;
}

void __stdcall EU_SetElementColor(HWND hwnd, int element_id, Color bg, Color fg) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        if (el->has_logical_style) {
            el->logical_style.bg_color = bg;
            el->logical_style.fg_color = fg;
            el->apply_dpi_scale(st->dpi_scale);
        } else {
            el->style.bg_color = bg;
            el->style.fg_color = fg;
        }
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

void __stdcall EU_SetElementFont(HWND hwnd, int element_id,
                                 const unsigned char* font_bytes, int font_len, float size) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        if (el->has_logical_style) {
            el->logical_style.font_name = utf8_to_wide(font_bytes, font_len);
            el->logical_style.font_size = size;
            el->apply_dpi_scale(st->dpi_scale);
        } else {
            el->style.font_name = utf8_to_wide(font_bytes, font_len);
            el->style.font_size = size;
        }
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

void __stdcall EU_SetTextOptions(HWND hwnd, int element_id, int align, int valign, int wrap, int ellipsis) {
    if (auto* el = find_typed_element<Text>(hwnd, element_id)) {
        el->set_options(align, valign, wrap, ellipsis);
    }
}

int __stdcall EU_GetTextOptions(HWND hwnd, int element_id, int* align, int* valign, int* wrap, int* ellipsis) {
    auto* el = find_typed_element<Text>(hwnd, element_id);
    if (!el) return 0;
    if (align) *align = el->horizontal_align;
    if (valign) *valign = el->vertical_align;
    if (wrap) *wrap = el->wrap ? 1 : 0;
    if (ellipsis) *ellipsis = el->ellipsis ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLinkOptions(HWND hwnd, int element_id, int type, int underline, int auto_open, int visited) {
    if (auto* el = find_typed_element<Link>(hwnd, element_id)) {
        el->set_options(type, underline, auto_open, visited);
    }
}

int __stdcall EU_GetLinkOptions(HWND hwnd, int element_id, int* type, int* underline, int* auto_open, int* visited) {
    auto* el = find_typed_element<Link>(hwnd, element_id);
    if (!el) return 0;
    if (type) *type = el->link_type;
    if (underline) *underline = el->underline_enabled ? 1 : 0;
    if (auto_open) *auto_open = el->auto_open ? 1 : 0;
    if (visited) *visited = el->visited ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLinkContent(HWND hwnd, int element_id,
                                 const unsigned char* prefix_bytes, int prefix_len,
                                 const unsigned char* suffix_bytes, int suffix_len,
                                 const unsigned char* href_bytes, int href_len,
                                 const unsigned char* target_bytes, int target_len) {
    if (auto* el = find_typed_element<Link>(hwnd, element_id)) {
        el->set_content(utf8_to_wide(prefix_bytes, prefix_len),
                        utf8_to_wide(suffix_bytes, suffix_len),
                        utf8_to_wide(href_bytes, href_len),
                        utf8_to_wide(target_bytes, target_len));
    }
}

int __stdcall EU_GetLinkContent(HWND hwnd, int element_id,
                                unsigned char* prefix_buffer, int prefix_buffer_size,
                                unsigned char* suffix_buffer, int suffix_buffer_size,
                                unsigned char* href_buffer, int href_buffer_size,
                                unsigned char* target_buffer, int target_buffer_size) {
    auto* el = find_typed_element<Link>(hwnd, element_id);
    if (!el) return 0;
    copy_wide_as_utf8(el->prefix_icon, prefix_buffer, prefix_buffer_size);
    copy_wide_as_utf8(el->suffix_icon, suffix_buffer, suffix_buffer_size);
    copy_wide_as_utf8(el->href, href_buffer, href_buffer_size);
    copy_wide_as_utf8(el->target, target_buffer, target_buffer_size);
    return 1;
}

void __stdcall EU_SetLinkVisited(HWND hwnd, int element_id, int visited) {
    if (auto* el = find_typed_element<Link>(hwnd, element_id)) {
        el->visited = visited != 0;
        el->invalidate();
    }
}

int __stdcall EU_GetLinkVisited(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Link>(hwnd, element_id);
    return (el && el->visited) ? 1 : 0;
}

void __stdcall EU_SetIconOptions(HWND hwnd, int element_id, float scale, float rotation_degrees) {
    if (auto* el = find_typed_element<Icon>(hwnd, element_id)) {
        el->icon_scale = scale > 0.1f ? scale : 1.25f;
        el->rotation = rotation_degrees;
        el->invalidate();
    }
}

int __stdcall EU_GetIconOptions(HWND hwnd, int element_id, float* scale, float* rotation_degrees) {
    auto* el = find_typed_element<Icon>(hwnd, element_id);
    if (!el) return 0;
    if (scale) *scale = el->icon_scale;
    if (rotation_degrees) *rotation_degrees = el->rotation;
    return 1;
}

void __stdcall EU_SetPanelStyle(HWND hwnd, int element_id, Color bg, Color border, float border_width, float radius, int padding) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* base = st->element_tree->find_by_id(element_id);
    auto* el = dynamic_cast<Panel*>(base);
    if (!el) return;

    ElementStyle next = el->has_logical_style ? el->logical_style : el->style;
    next.bg_color = bg;
    next.border_color = border;
    next.border_width = border_width >= 0.0f ? border_width : 0.0f;
    next.corner_radius = radius >= 0.0f ? radius : 0.0f;
    int pad = padding >= 0 ? padding : 0;
    next.pad_left = pad;
    next.pad_top = pad;
    next.pad_right = pad;
    next.pad_bottom = pad;
    el->set_logical_style(next);
    el->apply_dpi_scale(st->dpi_scale);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetPanelStyle(HWND hwnd, int element_id, Color* bg, Color* border, float* border_width, float* radius, int* padding) {
    auto* el = find_typed_element<Panel>(hwnd, element_id);
    if (!el) return 0;
    const ElementStyle& s = el->has_logical_style ? el->logical_style : el->style;
    if (bg) *bg = s.bg_color;
    if (border) *border = s.border_color;
    if (border_width) *border_width = s.border_width;
    if (radius) *radius = s.corner_radius;
    if (padding) *padding = s.pad_left;
    return 1;
}

void __stdcall EU_SetPanelLayout(HWND hwnd, int element_id, int fill_parent, int content_layout) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Panel>(hwnd, element_id)) {
        el->set_layout_options(fill_parent != 0, content_layout != 0);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetPanelLayout(HWND hwnd, int element_id, int* fill_parent, int* content_layout) {
    auto* el = find_typed_element<Panel>(hwnd, element_id);
    if (!el) return 0;
    if (fill_parent) *fill_parent = el->fill_parent ? 1 : 0;
    if (content_layout) *content_layout = el->layout_children_in_content ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLayoutOptions(HWND hwnd, int element_id, int orientation, int gap, int stretch, int align, int wrap) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Layout>(hwnd, element_id)) {
        el->set_options(orientation, gap, stretch, align, wrap);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetLayoutOptions(HWND hwnd, int element_id, int* orientation, int* gap, int* stretch, int* align, int* wrap) {
    auto* el = find_typed_element<Layout>(hwnd, element_id);
    if (!el) return 0;
    if (orientation) *orientation = el->orientation;
    if (gap) *gap = el->get_logical_gap();
    if (stretch) *stretch = el->stretch_cross_axis ? 1 : 0;
    if (align) *align = el->cross_align;
    if (wrap) *wrap = el->wrap_items ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLayoutChildWeight(HWND hwnd, int layout_id, int child_id, int weight) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    auto* layout = find_typed_element<Layout>(hwnd, layout_id);
    Element* child = st->element_tree->find_by_id(child_id);
    if (!layout || !child || child->parent != layout) return;
    layout->set_child_weight(child_id, weight);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetLayoutChildWeight(HWND hwnd, int layout_id, int child_id) {
    auto* layout = find_typed_element<Layout>(hwnd, layout_id);
    if (!layout) return 0;
    return layout->get_child_weight(child_id);
}

void __stdcall EU_SetBorderOptions(HWND hwnd, int element_id, int sides, Color color, float width, float radius,
                                   const unsigned char* title_bytes, int title_len) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Border>(hwnd, element_id)) {
        el->set_options(sides, color, width, radius, utf8_to_wide(title_bytes, title_len));
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetBorderOptions(HWND hwnd, int element_id, int* sides, Color* color, float* width, float* radius) {
    auto* el = find_typed_element<Border>(hwnd, element_id);
    if (!el) return 0;
    int side_mask = 15;
    Color border_color = 0;
    float border_width = 0.0f;
    float corner_radius = 0.0f;
    el->get_options(side_mask, border_color, border_width, corner_radius);
    if (sides) *sides = side_mask;
    if (color) *color = border_color;
    if (width) *width = border_width;
    if (radius) *radius = corner_radius;
    return 1;
}

void __stdcall EU_SetBorderDashed(HWND hwnd, int element_id, int dashed) {
    if (auto* el = find_typed_element<Border>(hwnd, element_id)) {
        el->set_dashed(dashed != 0);
    }
}

int __stdcall EU_GetBorderDashed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Border>(hwnd, element_id);
    return (el && el->dashed) ? 1 : 0;
}

void __stdcall EU_SetInfoBoxText(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<InfoBox>(hwnd, element_id)) {
        el->set_texts(utf8_to_wide(title_bytes, title_len), utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetInfoBoxOptions(HWND hwnd, int element_id, int type, int closable, Color accent,
                                    const unsigned char* icon_bytes, int icon_len) {
    if (auto* el = find_typed_element<InfoBox>(hwnd, element_id)) {
        el->set_options(type, closable, accent, utf8_to_wide(icon_bytes, icon_len));
    }
}

void __stdcall EU_SetInfoBoxClosed(HWND hwnd, int element_id, int closed) {
    if (auto* el = find_typed_element<InfoBox>(hwnd, element_id)) {
        el->set_closed(closed != 0);
    }
}

int __stdcall EU_GetInfoBoxClosed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<InfoBox>(hwnd, element_id);
    return (el && el->is_closed()) ? 1 : 0;
}

int __stdcall EU_GetInfoBoxPreferredHeight(HWND hwnd, int element_id) {
    WindowState* st = window_state(hwnd);
    auto* el = find_typed_element<InfoBox>(hwnd, element_id);
    if (!st || !el) return 0;
    int px = el->preferred_height();
    float scale = st->dpi_scale > 0.0f ? st->dpi_scale : 1.0f;
    return (int)std::lround((float)px / scale);
}

void __stdcall EU_SetSpaceSize(HWND hwnd, int element_id, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Space>(hwnd, element_id)) {
        el->set_size(w, h);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetSpaceSize(HWND hwnd, int element_id, int* w, int* h) {
    auto* el = find_typed_element<Space>(hwnd, element_id);
    if (!el) return 0;
    int width = 0;
    int height = 0;
    el->get_size(width, height);
    if (w) *w = width;
    if (h) *h = height;
    return 1;
}

void __stdcall EU_SetDividerOptions(HWND hwnd, int element_id,
                                    int direction, int content_position, Color color,
                                    float width, int dashed,
                                    const unsigned char* text_bytes, int text_len) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Divider>(hwnd, element_id)) {
        el->set_options(direction, content_position, color, width, dashed,
                        utf8_to_wide(text_bytes, text_len));
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetDividerOptions(HWND hwnd, int element_id,
                                   int* direction, int* content_position, Color* color,
                                   float* width, int* dashed) {
    auto* el = find_typed_element<Divider>(hwnd, element_id);
    if (!el) return 0;
    int out_direction = 0;
    int position = 1;
    Color line_color = 0;
    float line_width = 1.0f;
    int is_dashed = 0;
    el->get_options(out_direction, position, line_color, line_width, is_dashed);
    if (direction) *direction = out_direction;
    if (content_position) *content_position = position;
    if (color) *color = line_color;
    if (width) *width = line_width;
    if (dashed) *dashed = is_dashed;
    return 1;
}

void __stdcall EU_SetDividerSpacing(HWND hwnd, int element_id, int margin, int gap) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Divider>(hwnd, element_id)) {
        el->set_spacing(margin, gap);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetDividerSpacing(HWND hwnd, int element_id, int* margin, int* gap) {
    auto* el = find_typed_element<Divider>(hwnd, element_id);
    if (!el) return 0;
    int out_margin = 0;
    int out_gap = 0;
    el->get_spacing(out_margin, out_gap);
    if (margin) *margin = out_margin;
    if (gap) *gap = out_gap;
    return 1;
}

void __stdcall EU_SetDividerLineStyle(HWND hwnd, int element_id, int line_style) {
    if (auto* el = find_typed_element<Divider>(hwnd, element_id)) {
        el->set_line_style(line_style);
    }
}

int __stdcall EU_GetDividerLineStyle(HWND hwnd, int element_id, int* line_style) {
    auto* el = find_typed_element<Divider>(hwnd, element_id);
    if (!el) return 0;
    if (line_style) *line_style = el->line_style;
    return 1;
}

void __stdcall EU_SetDividerContent(HWND hwnd, int element_id,
                                    const unsigned char* icon_bytes, int icon_len,
                                    const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Divider>(hwnd, element_id)) {
        el->set_content(utf8_to_wide(icon_bytes, icon_len),
                        utf8_to_wide(text_bytes, text_len));
    }
}

int __stdcall EU_GetDividerContent(HWND hwnd, int element_id,
                                   unsigned char* icon_buffer, int icon_buffer_size,
                                   unsigned char* text_buffer, int text_buffer_size) {
    auto* el = find_typed_element<Divider>(hwnd, element_id);
    if (!el) return 0;
    std::wstring icon;
    std::wstring label;
    el->get_content(icon, label);
    copy_wide_as_utf8(icon, icon_buffer, icon_buffer_size);
    copy_wide_as_utf8(label, text_buffer, text_buffer_size);
    return 1;
}

void __stdcall EU_SetButtonEmoji(HWND hwnd, int element_id, const unsigned char* bytes, int len) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el && el->type_name() == std::wstring(L"Button")) {
        static_cast<Button*>(el)->emoji = utf8_to_wide(bytes, len);
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

void __stdcall EU_SetButtonVariant(HWND hwnd, int element_id, int variant) {
    if (auto* el = find_typed_element<Button>(hwnd, element_id)) {
        el->set_variant(variant);
    }
}

int __stdcall EU_GetButtonState(HWND hwnd, int element_id, int* pressed, int* focused, int* variant) {
    auto* el = find_typed_element<Button>(hwnd, element_id);
    if (!el) return 0;
    if (pressed) *pressed = el->pressed ? 1 : 0;
    if (focused) *focused = el->has_focus ? 1 : 0;
    if (variant) *variant = el->variant;
    return 1;
}

void __stdcall EU_SetButtonOptions(HWND hwnd, int element_id,
                                   int variant, int plain, int round,
                                   int circle, int loading, int size) {
    if (auto* el = find_typed_element<Button>(hwnd, element_id)) {
        el->set_options(variant, plain, round, circle, loading, size);
    }
}

int __stdcall EU_GetButtonOptions(HWND hwnd, int element_id,
                                  int* variant, int* plain, int* round,
                                  int* circle, int* loading, int* size) {
    auto* el = find_typed_element<Button>(hwnd, element_id);
    if (!el) return 0;
    if (variant) *variant = el->variant;
    if (plain) *plain = el->plain ? 1 : 0;
    if (round) *round = el->round ? 1 : 0;
    if (circle) *circle = el->circle ? 1 : 0;
    if (loading) *loading = el->loading ? 1 : 0;
    if (size) *size = el->size;
    return 1;
}

void __stdcall EU_SetEditBoxText(HWND hwnd, int element_id, const unsigned char* bytes, int len) {
    if (auto* el = find_typed_element<EditBox>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(bytes, len));
    }
}

void __stdcall EU_SetEditBoxOptions(HWND hwnd, int element_id, int readonly, int password, int multiline,
                                    Color focus_border, const unsigned char* placeholder_bytes, int placeholder_len) {
    if (auto* el = find_typed_element<EditBox>(hwnd, element_id)) {
        el->set_options(readonly, password, multiline, focus_border,
                        utf8_to_wide(placeholder_bytes, placeholder_len));
    }
}

int __stdcall EU_GetEditBoxOptions(HWND hwnd, int element_id, int* readonly, int* password, int* multiline,
                                   Color* focus_border) {
    auto* el = find_typed_element<EditBox>(hwnd, element_id);
    if (!el) return 0;
    if (readonly) *readonly = el->readonly ? 1 : 0;
    if (password) *password = el->password ? 1 : 0;
    if (multiline) *multiline = el->multiline ? 1 : 0;
    if (focus_border) *focus_border = el->focus_border;
    return 1;
}

int __stdcall EU_GetEditBoxState(HWND hwnd, int element_id, int* cursor, int* sel_start, int* sel_end, int* text_length) {
    auto* el = find_typed_element<EditBox>(hwnd, element_id);
    if (!el) return 0;
    int c = 0;
    int ss = -1;
    int se = -1;
    int len = 0;
    el->get_state(c, ss, se, len);
    if (cursor) *cursor = c;
    if (sel_start) *sel_start = ss;
    if (sel_end) *sel_end = se;
    if (text_length) *text_length = len;
    return 1;
}

int __stdcall EU_GetEditBoxText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* el = st->element_tree->find_by_id(element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->text);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int copy = needed < buffer_size ? needed : buffer_size;
    if (copy > 0) memcpy(buffer, utf8.data(), copy);
    return needed;
}

void __stdcall EU_SetEditBoxTextCallback(HWND hwnd, int element_id, ElementTextCallback cb) {
    if (auto* el = find_typed_element<EditBox>(hwnd, element_id)) {
        el->text_cb = cb;
    }
}

void __stdcall EU_SetElementFocus(HWND hwnd, int element_id) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) {
        SetFocus(hwnd);
        st->element_tree->set_focus(el);
    }
}

void __stdcall EU_InvalidateElement(HWND hwnd, int /*element_id*/) {
    InvalidateRect(hwnd, nullptr, FALSE);
}

void __stdcall EU_SetCheckboxChecked(HWND hwnd, int element_id, int checked) {
    if (auto* el = find_typed_element<Checkbox>(hwnd, element_id)) {
        el->set_checked(checked != 0);
    }
}

int __stdcall EU_GetCheckboxChecked(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Checkbox>(hwnd, element_id);
    return (el && el->checked) ? 1 : 0;
}

void __stdcall EU_SetCheckboxIndeterminate(HWND hwnd, int element_id, int indeterminate) {
    if (auto* el = find_typed_element<Checkbox>(hwnd, element_id)) {
        el->set_indeterminate(indeterminate != 0);
    }
}

int __stdcall EU_GetCheckboxIndeterminate(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Checkbox>(hwnd, element_id);
    return (el && el->indeterminate) ? 1 : 0;
}

void __stdcall EU_SetCheckboxOptions(HWND hwnd, int element_id, int border, int size) {
    if (auto* el = find_typed_element<Checkbox>(hwnd, element_id)) {
        el->set_options(border != 0, size);
    }
}

int __stdcall EU_GetCheckboxOptions(HWND hwnd, int element_id, int* border, int* size) {
    auto* el = find_typed_element<Checkbox>(hwnd, element_id);
    if (!el) return 0;
    if (border) *border = el->border ? 1 : 0;
    if (size) *size = el->size;
    return 1;
}

void __stdcall EU_SetCheckboxGroupItems(HWND hwnd, int element_id,
                                        const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id)) {
        el->set_items(parse_checkbox_group_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetCheckboxGroupValue(HWND hwnd, int element_id,
                                        const unsigned char* values_bytes, int values_len) {
    if (auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id)) {
        el->set_checked_values(parse_checkbox_checked_values(values_bytes, values_len));
    }
}

int __stdcall EU_GetCheckboxGroupValue(HWND hwnd, int element_id,
                                       unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->checked_values(), buffer, buffer_size);
}

void __stdcall EU_SetCheckboxGroupOptions(HWND hwnd, int element_id,
                                          int group_disabled, int style_mode, int size,
                                          int min_checked, int max_checked) {
    if (auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id)) {
        el->set_options(group_disabled != 0, style_mode, size, min_checked, max_checked);
    }
}

int __stdcall EU_GetCheckboxGroupOptions(HWND hwnd, int element_id,
                                         int* group_disabled, int* style_mode, int* size,
                                         int* min_checked, int* max_checked) {
    auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id);
    if (!el) return 0;
    if (group_disabled) *group_disabled = el->group_disabled ? 1 : 0;
    if (style_mode) *style_mode = el->style_mode;
    if (size) *size = el->size;
    if (min_checked) *min_checked = el->min_checked;
    if (max_checked) *max_checked = el->max_checked;
    return 1;
}

int __stdcall EU_GetCheckboxGroupState(HWND hwnd, int element_id,
                                       int* checked_count, int* item_count,
                                       int* disabled_count, int* group_disabled,
                                       int* style_mode, int* size,
                                       int* min_checked, int* max_checked,
                                       int* hover_index, int* press_index,
                                       int* focus_index, int* last_action) {
    auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id);
    if (!el) return 0;
    if (checked_count) *checked_count = el->checked_count();
    if (item_count) *item_count = el->item_count();
    if (disabled_count) *disabled_count = el->disabled_count();
    if (group_disabled) *group_disabled = el->group_disabled ? 1 : 0;
    if (style_mode) *style_mode = el->style_mode;
    if (size) *size = el->size;
    if (min_checked) *min_checked = el->min_checked;
    if (max_checked) *max_checked = el->max_checked;
    if (hover_index) *hover_index = el->hover_index();
    if (press_index) *press_index = el->press_index();
    if (focus_index) *focus_index = el->focus_index();
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetCheckboxGroupChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<CheckboxGroup>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetRadioChecked(HWND hwnd, int element_id, int checked) {
    if (auto* el = find_typed_element<Radio>(hwnd, element_id)) {
        el->set_checked(checked != 0);
    }
}

int __stdcall EU_GetRadioChecked(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Radio>(hwnd, element_id);
    return (el && el->checked) ? 1 : 0;
}

void __stdcall EU_SetRadioGroup(HWND hwnd, int element_id,
                                const unsigned char* group_bytes, int group_len) {
    if (auto* el = find_typed_element<Radio>(hwnd, element_id)) {
        el->set_group_name(utf8_to_wide(group_bytes, group_len));
    }
}

int __stdcall EU_GetRadioGroup(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Radio>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->group_name, buffer, buffer_size);
}

void __stdcall EU_SetRadioValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Radio>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

int __stdcall EU_GetRadioValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Radio>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->value, buffer, buffer_size);
}

void __stdcall EU_SetRadioOptions(HWND hwnd, int element_id, int border, int size) {
    if (auto* el = find_typed_element<Radio>(hwnd, element_id)) {
        el->set_options(border != 0, size);
    }
}

int __stdcall EU_GetRadioOptions(HWND hwnd, int element_id, int* border, int* size) {
    auto* el = find_typed_element<Radio>(hwnd, element_id);
    if (!el) return 0;
    if (border) *border = el->border ? 1 : 0;
    if (size) *size = el->size;
    return 1;
}

void __stdcall EU_SetRadioGroupItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<RadioGroup>(hwnd, element_id)) {
        el->set_items(parse_radio_group_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetRadioGroupValue(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<RadioGroup>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

int __stdcall EU_GetRadioGroupValue(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<RadioGroup>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->selected_value(), buffer, buffer_size);
}

int __stdcall EU_GetRadioGroupSelectedIndex(HWND hwnd, int element_id) {
    auto* el = find_typed_element<RadioGroup>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

void __stdcall EU_SetRadioGroupOptions(HWND hwnd, int element_id,
                                       int group_disabled, int style_mode, int size) {
    if (auto* el = find_typed_element<RadioGroup>(hwnd, element_id)) {
        el->set_options(group_disabled != 0, style_mode, size);
    }
}

int __stdcall EU_GetRadioGroupOptions(HWND hwnd, int element_id,
                                      int* group_disabled, int* style_mode, int* size) {
    auto* el = find_typed_element<RadioGroup>(hwnd, element_id);
    if (!el) return 0;
    if (group_disabled) *group_disabled = el->group_disabled ? 1 : 0;
    if (style_mode) *style_mode = el->style_mode;
    if (size) *size = el->size;
    return 1;
}

int __stdcall EU_GetRadioGroupState(HWND hwnd, int element_id,
                                    int* selected_index, int* item_count,
                                    int* disabled_count, int* group_disabled,
                                    int* style_mode, int* size,
                                    int* hover_index, int* press_index,
                                    int* last_action) {
    auto* el = find_typed_element<RadioGroup>(hwnd, element_id);
    if (!el) return 0;
    if (selected_index) *selected_index = el->selected_index;
    if (item_count) *item_count = el->item_count();
    if (disabled_count) *disabled_count = el->disabled_count();
    if (group_disabled) *group_disabled = el->group_disabled ? 1 : 0;
    if (style_mode) *style_mode = el->style_mode;
    if (size) *size = el->size;
    if (hover_index) *hover_index = el->hover_index();
    if (press_index) *press_index = el->press_index();
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetRadioGroupChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<RadioGroup>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetSwitchChecked(HWND hwnd, int element_id, int checked) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_checked(checked != 0);
    }
}

int __stdcall EU_GetSwitchChecked(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Switch>(hwnd, element_id);
    return (el && el->checked) ? 1 : 0;
}

void __stdcall EU_SetSwitchLoading(HWND hwnd, int element_id, int loading) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_loading(loading != 0);
    }
}

int __stdcall EU_GetSwitchLoading(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Switch>(hwnd, element_id);
    return (el && el->loading) ? 1 : 0;
}

void __stdcall EU_SetSwitchTexts(HWND hwnd, int element_id,
                                 const unsigned char* active_bytes, int active_len,
                                 const unsigned char* inactive_bytes, int inactive_len) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_texts(utf8_to_wide(active_bytes, active_len),
                      utf8_to_wide(inactive_bytes, inactive_len));
    }
}

int __stdcall EU_GetSwitchOptions(HWND hwnd, int element_id,
                                  int* checked, int* loading, int* has_active_text, int* has_inactive_text) {
    auto* el = find_typed_element<Switch>(hwnd, element_id);
    if (!el) return 0;
    if (checked) *checked = el->checked ? 1 : 0;
    if (loading) *loading = el->loading ? 1 : 0;
    if (has_active_text) *has_active_text = el->active_text.empty() ? 0 : 1;
    if (has_inactive_text) *has_inactive_text = el->inactive_text.empty() ? 0 : 1;
    return 1;
}

void __stdcall EU_SetSwitchActiveColor(HWND hwnd, int element_id, Color color) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_active_color(color);
    }
}

Color __stdcall EU_GetSwitchActiveColor(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        return el->active_color;
    }
    return 0;
}

void __stdcall EU_SetSwitchInactiveColor(HWND hwnd, int element_id, Color color) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_inactive_color(color);
    }
}

Color __stdcall EU_GetSwitchInactiveColor(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        return el->inactive_color;
    }
    return 0;
}

void __stdcall EU_SetSwitchValue(HWND hwnd, int element_id, int value) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_value(value);
    }
}

int __stdcall EU_GetSwitchValue(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        return el->get_value();
    }
    return 0;
}

void __stdcall EU_SetSwitchSize(HWND hwnd, int element_id, int size) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        el->set_size(size);
    }
}

int __stdcall EU_GetSwitchSize(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Switch>(hwnd, element_id)) {
        return el->size;
    }
    return 0;
}

void __stdcall EU_SetSliderRange(HWND hwnd, int element_id, int min_value, int max_value) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->set_range(min_value, max_value);
    }
}

void __stdcall EU_SetSliderValue(HWND hwnd, int element_id, int value) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->set_value(value);
    }
}

int __stdcall EU_GetSliderValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Slider>(hwnd, element_id);
    return el ? el->value : 0;
}

void __stdcall EU_SetSliderOptions(HWND hwnd, int element_id, int step, int show_tooltip) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->set_options(step, show_tooltip != 0);
    }
}

int __stdcall EU_GetSliderStep(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Slider>(hwnd, element_id);
    return el ? el->step : 0;
}

int __stdcall EU_GetSliderOptions(HWND hwnd, int element_id, int* min_value, int* max_value, int* step, int* show_tooltip) {
    auto* el = find_typed_element<Slider>(hwnd, element_id);
    if (!el) return 0;
    if (min_value) *min_value = el->min_value;
    if (max_value) *max_value = el->max_value;
    if (step) *step = el->step;
    if (show_tooltip) *show_tooltip = el->show_tooltip ? 1 : 0;
    return 1;
}

void __stdcall EU_SetSliderRangeValue(HWND hwnd, int element_id, int start_value, int end_value) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->set_range_value(start_value, end_value);
    }
}

int __stdcall EU_GetSliderRangeValue(HWND hwnd, int element_id, int* start_value, int* end_value) {
    auto* el = find_typed_element<Slider>(hwnd, element_id);
    if (!el) return 0;
    if (start_value) *start_value = el->range_start;
    if (end_value) *end_value = el->range_end;
    return 1;
}

void __stdcall EU_SetSliderRangeMode(HWND hwnd, int element_id, int enabled, int start_value, int end_value) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->set_range_mode(enabled != 0, start_value, end_value);
    }
}

int __stdcall EU_GetSliderRangeMode(HWND hwnd, int element_id, int* enabled, int* start_value, int* end_value) {
    auto* el = find_typed_element<Slider>(hwnd, element_id);
    if (!el) return 0;
    if (enabled) *enabled = el->range_mode ? 1 : 0;
    if (start_value) *start_value = el->range_start;
    if (end_value) *end_value = el->range_end;
    return 1;
}

void __stdcall EU_SetSliderValueCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Slider>(hwnd, element_id)) {
        el->value_cb = cb;
    }
}

void __stdcall EU_SetInputNumberRange(HWND hwnd, int element_id, int min_value, int max_value) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->set_range(min_value, max_value);
    }
}

void __stdcall EU_SetInputNumberStep(HWND hwnd, int element_id, int step) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->set_step(step);
    }
}

void __stdcall EU_SetInputNumberValue(HWND hwnd, int element_id, int value) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->set_value(value);
    }
}

int __stdcall EU_GetInputNumberValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    return el ? el->value : 0;
}

int __stdcall EU_GetInputNumberCanStep(HWND hwnd, int element_id, int delta) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    return (el && el->can_step(delta)) ? 1 : 0;
}

int __stdcall EU_GetInputNumberOptions(HWND hwnd, int element_id, int* min_value, int* max_value, int* step) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    if (!el) return 0;
    if (min_value) *min_value = el->min_value;
    if (max_value) *max_value = el->max_value;
    if (step) *step = el->step;
    return 1;
}

void __stdcall EU_SetInputNumberPrecision(HWND hwnd, int element_id, int precision) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->set_precision(precision);
    }
}

int __stdcall EU_GetInputNumberPrecision(HWND hwnd, int element_id) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    return el ? el->precision : 0;
}

int __stdcall EU_SetInputNumberText(HWND hwnd, int element_id,
                                    const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        return el->set_value_from_text(utf8_to_wide(value_bytes, value_len)) ? 1 : 0;
    }
    return 0;
}

int __stdcall EU_GetInputNumberText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->display_value());
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return needed;
}

int __stdcall EU_GetInputNumberState(HWND hwnd, int element_id,
                                     int* precision, int* editing, int* valid,
                                     int* can_decrease, int* can_increase) {
    auto* el = find_typed_element<InputNumber>(hwnd, element_id);
    if (!el) return 0;
    if (precision) *precision = el->precision;
    if (editing) *editing = el->is_editing() ? 1 : 0;
    if (valid) *valid = el->last_input_valid ? 1 : 0;
    if (can_decrease) *can_decrease = el->can_step(-el->step) ? 1 : 0;
    if (can_increase) *can_increase = el->can_step(el->step) ? 1 : 0;
    return 1;
}

void __stdcall EU_SetInputNumberValueCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->value_cb = cb;
    }
}

void __stdcall EU_SetInputNumberStepStrictly(HWND hwnd, int element_id, int strict) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        el->set_step_strictly(strict != 0);
    }
}

int __stdcall EU_GetInputNumberStepStrictly(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<InputNumber>(hwnd, element_id)) {
        return el->step_strictly ? 1 : 0;
    }
    return 0;
}

static InputGroup* find_input_group(HWND hwnd, int element_id) {
    return find_typed_element<InputGroup>(hwnd, element_id);
}

static Input* find_input_group_child(HWND hwnd, int element_id) {
    auto* group = find_input_group(hwnd, element_id);
    return group ? group->input_child() : nullptr;
}

static void remove_input_group_addon(WindowState* st, InputGroup* group, int side) {
    if (!st || !st->element_tree || !group) return;
    int addon_id = group->addon_element_id(side);
    if (addon_id != 0) {
        if (Element* addon = st->element_tree->find_by_id(addon_id)) {
            st->element_tree->remove_child(addon);
        }
    }
    group->clear_addon_spec(side);
}

void __stdcall EU_SetInputValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

int __stdcall EU_GetInputValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->value);
    if (!buffer || buffer_size <= 0) return (int)utf8.size();
    int n = (std::min)((int)utf8.size(), buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return n;
}

void __stdcall EU_SetInputPlaceholder(HWND hwnd, int element_id,
                                      const unsigned char* placeholder_bytes, int placeholder_len) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));
    }
}

void __stdcall EU_SetInputAffixes(HWND hwnd, int element_id,
                                  const unsigned char* prefix_bytes, int prefix_len,
                                  const unsigned char* suffix_bytes, int suffix_len) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_affixes(utf8_to_wide(prefix_bytes, prefix_len),
                        utf8_to_wide(suffix_bytes, suffix_len));
    }
}

void __stdcall EU_SetInputIcons(HWND hwnd, int element_id,
                                const unsigned char* prefix_icon_bytes, int prefix_icon_len,
                                const unsigned char* suffix_icon_bytes, int suffix_icon_len) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_icons(utf8_to_wide(prefix_icon_bytes, prefix_icon_len),
                      utf8_to_wide(suffix_icon_bytes, suffix_icon_len));
    }
}

int __stdcall EU_GetInputIcons(HWND hwnd, int element_id,
                               unsigned char* prefix_icon_buffer, int prefix_icon_buffer_size,
                               unsigned char* suffix_icon_buffer, int suffix_icon_buffer_size) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    if (!el) return 0;
    copy_wide_as_utf8(el->prefix_icon, prefix_icon_buffer, prefix_icon_buffer_size);
    copy_wide_as_utf8(el->suffix_icon, suffix_icon_buffer, suffix_icon_buffer_size);
    return 1;
}

void __stdcall EU_SetInputClearable(HWND hwnd, int element_id, int clearable) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_clearable(clearable != 0);
    }
}

void __stdcall EU_SetInputOptions(HWND hwnd, int element_id, int readonly, int password, int multiline, int validate_state) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_options(readonly != 0, password != 0, multiline != 0, validate_state);
    }
}

void __stdcall EU_SetInputVisualOptions(HWND hwnd, int element_id,
                                        int size, int show_password_toggle,
                                        int show_word_limit, int autosize,
                                        int min_rows, int max_rows) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_visual_options(size, show_password_toggle != 0,
                               show_word_limit != 0, autosize != 0,
                               min_rows, max_rows);
        if (WindowState* st = window_state(hwnd)) {
            if (st->element_tree) st->element_tree->layout();
        }
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetInputVisualOptions(HWND hwnd, int element_id,
                                       int* size, int* show_password_toggle,
                                       int* show_word_limit, int* autosize,
                                       int* min_rows, int* max_rows) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    if (!el) return 0;
    if (size) *size = el->size;
    if (show_password_toggle) *show_password_toggle = el->show_password_toggle ? 1 : 0;
    if (show_word_limit) *show_word_limit = el->show_word_limit ? 1 : 0;
    if (autosize) *autosize = el->autosize ? 1 : 0;
    if (min_rows) *min_rows = el->min_rows;
    if (max_rows) *max_rows = el->max_rows;
    return 1;
}

void __stdcall EU_SetInputSelection(HWND hwnd, int element_id, int start, int end) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_selection(start, end);
    }
}

int __stdcall EU_GetInputSelection(HWND hwnd, int element_id, int* start, int* end) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    if (!el) return 0;
    int s = 0;
    int e = 0;
    el->get_selection(s, e);
    if (start) *start = s;
    if (end) *end = e;
    return 1;
}

void __stdcall EU_SetInputContextMenuEnabled(HWND hwnd, int element_id, int enabled) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_context_menu_enabled(enabled != 0);
    }
}

int __stdcall EU_GetInputContextMenuEnabled(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    return (el && el->context_menu_enabled) ? 1 : 0;
}

int __stdcall EU_GetInputState(HWND hwnd, int element_id, int* cursor, int* length, int* clearable,
                               int* readonly, int* password, int* multiline, int* validate_state) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    if (!el) return 0;
    int c = 0;
    int len = 0;
    el->get_state(c, len);
    if (cursor) *cursor = c;
    if (length) *length = len;
    if (clearable) *clearable = el->clearable ? 1 : 0;
    if (readonly) *readonly = el->readonly ? 1 : 0;
    if (password) *password = el->password ? 1 : 0;
    if (multiline) *multiline = el->multiline ? 1 : 0;
    if (validate_state) *validate_state = el->validate_state;
    return 1;
}

void __stdcall EU_SetInputMaxLength(HWND hwnd, int element_id, int max_length) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->set_max_length(max_length);
    }
}

int __stdcall EU_GetInputMaxLength(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Input>(hwnd, element_id);
    return el ? el->max_length : 0;
}

void __stdcall EU_SetInputTextCallback(HWND hwnd, int element_id, ElementTextCallback cb) {
    if (auto* el = find_typed_element<Input>(hwnd, element_id)) {
        el->text_cb = cb;
    }
}

void __stdcall EU_SetInputGroupValue(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len) {
    if (auto* input = find_input_group_child(hwnd, element_id)) {
        input->set_value(utf8_to_wide(value_bytes, value_len));
        if (WindowState* st = window_state(hwnd)) {
            if (st->element_tree) st->element_tree->layout();
        }
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetInputGroupValue(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size) {
    auto* input = find_input_group_child(hwnd, element_id);
    if (!input) return 0;
    return copy_wide_as_utf8(input->value, buffer, buffer_size);
}

void __stdcall EU_SetInputGroupOptions(HWND hwnd, int element_id,
                                       int size, int clearable, int password,
                                       int show_word_limit, int autosize,
                                       int min_rows, int max_rows) {
    auto* group = find_input_group(hwnd, element_id);
    if (!group) return;
    group->set_options(size, clearable != 0, password != 0,
                       show_word_limit != 0, autosize != 0,
                       min_rows, max_rows);
    if (WindowState* st = window_state(hwnd)) {
        if (st->element_tree) st->element_tree->layout();
    }
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetInputGroupOptions(HWND hwnd, int element_id,
                                      int* size, int* clearable, int* password,
                                      int* show_word_limit, int* autosize,
                                      int* min_rows, int* max_rows) {
    auto* group = find_input_group(hwnd, element_id);
    if (!group) return 0;
    if (size) *size = group->size;
    if (clearable) *clearable = group->clearable ? 1 : 0;
    if (password) *password = group->password ? 1 : 0;
    if (show_word_limit) *show_word_limit = group->show_word_limit ? 1 : 0;
    if (autosize) *autosize = group->autosize ? 1 : 0;
    if (min_rows) *min_rows = group->min_rows;
    if (max_rows) *max_rows = group->max_rows;
    return 1;
}

void __stdcall EU_SetInputGroupTextAddon(HWND hwnd, int element_id, int side,
                                         const unsigned char* text_bytes, int text_len) {
    WindowState* st = window_state(hwnd);
    auto* group = find_input_group(hwnd, element_id);
    if (!st || !st->element_tree || !group) return;
    remove_input_group_addon(st, group, side);

    auto addon = std::make_unique<Button>();
    addon->text = utf8_to_wide(text_bytes, text_len);
    addon->emoji.clear();
    addon->set_options(0, 1, 0, 0, 0, group->size);
    init_default_button_style(addon.get());
    Element* raw = st->element_tree->add_child(group, std::move(addon));

    InputGroup::AddonSpec spec;
    spec.type = InputGroup::AddonText;
    spec.element_id = raw->id;
    spec.text = utf8_to_wide(text_bytes, text_len);
    group->set_addon_spec(side, spec);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

void __stdcall EU_SetInputGroupButtonAddon(HWND hwnd, int element_id, int side,
                                           const unsigned char* emoji_bytes, int emoji_len,
                                           const unsigned char* text_bytes, int text_len,
                                           int variant) {
    WindowState* st = window_state(hwnd);
    auto* group = find_input_group(hwnd, element_id);
    if (!st || !st->element_tree || !group) return;
    remove_input_group_addon(st, group, side);

    auto addon = std::make_unique<Button>();
    addon->text = utf8_to_wide(text_bytes, text_len);
    addon->emoji = utf8_to_wide(emoji_bytes, emoji_len);
    addon->set_options(variant, 0, 0, 0, 0, group->size);
    init_default_button_style(addon.get());
    Element* raw = st->element_tree->add_child(group, std::move(addon));

    InputGroup::AddonSpec spec;
    spec.type = InputGroup::AddonButton;
    spec.element_id = raw->id;
    spec.text = utf8_to_wide(text_bytes, text_len);
    spec.emoji = utf8_to_wide(emoji_bytes, emoji_len);
    spec.variant = variant;
    group->set_addon_spec(side, spec);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

void __stdcall EU_SetInputGroupSelectAddon(HWND hwnd, int element_id, int side,
                                           const unsigned char* items_bytes, int items_len,
                                           int selected_index,
                                           const unsigned char* placeholder_bytes, int placeholder_len) {
    WindowState* st = window_state(hwnd);
    auto* group = find_input_group(hwnd, element_id);
    if (!st || !st->element_tree || !group) return;
    remove_input_group_addon(st, group, side);

    auto parsed = parse_select_pairs(items_bytes, items_len);
    std::vector<std::wstring> labels;
    labels.reserve(parsed.size());
    for (const auto& pair : parsed) labels.push_back(pair.first);

    auto addon = std::make_unique<Select>();
    addon->set_options(labels);
    addon->set_selected_index(selected_index);
    addon->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));
    init_default_select_style(addon.get());
    Element* raw = st->element_tree->add_child(group, std::move(addon));

    InputGroup::AddonSpec spec;
    spec.type = InputGroup::AddonSelect;
    spec.element_id = raw->id;
    spec.select_items = labels;
    spec.select_placeholder = utf8_to_wide(placeholder_bytes, placeholder_len);
    if (spec.select_placeholder.empty()) spec.select_placeholder = L"请选择";
    spec.selected_index = selected_index;
    group->set_addon_spec(side, spec);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

void __stdcall EU_ClearInputGroupAddon(HWND hwnd, int element_id, int side) {
    WindowState* st = window_state(hwnd);
    auto* group = find_input_group(hwnd, element_id);
    if (!st || !st->element_tree || !group) return;
    remove_input_group_addon(st, group, side);
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetInputGroupInputElementId(HWND hwnd, int element_id) {
    auto* group = find_input_group(hwnd, element_id);
    return group ? group->input_element_id : 0;
}

int __stdcall EU_GetInputGroupAddonElementId(HWND hwnd, int element_id, int side) {
    auto* group = find_input_group(hwnd, element_id);
    return group ? group->addon_element_id(side) : 0;
}

void __stdcall EU_SetInputTagTags(HWND hwnd, int element_id,
                                  const unsigned char* tags_bytes, int tags_len) {
    if (auto* el = find_typed_element<InputTag>(hwnd, element_id)) {
        el->set_tags(split_option_list(tags_bytes, tags_len));
    }
}

void __stdcall EU_SetInputTagPlaceholder(HWND hwnd, int element_id,
                                         const unsigned char* placeholder_bytes, int placeholder_len) {
    if (auto* el = find_typed_element<InputTag>(hwnd, element_id)) {
        el->set_placeholder(utf8_to_wide(placeholder_bytes, placeholder_len));
    }
}

void __stdcall EU_SetInputTagOptions(HWND hwnd, int element_id, int max_count, int allow_duplicates) {
    if (auto* el = find_typed_element<InputTag>(hwnd, element_id)) {
        el->set_options(max_count, allow_duplicates != 0);
    }
}

int __stdcall EU_GetInputTagCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    return el ? el->tag_count() : 0;
}

int __stdcall EU_GetInputTagOptions(HWND hwnd, int element_id, int* max_count, int* allow_duplicates) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    if (!el) return 0;
    if (max_count) *max_count = el->max_count;
    if (allow_duplicates) *allow_duplicates = el->allow_duplicates ? 1 : 0;
    return 1;
}

int __stdcall EU_AddInputTagItem(HWND hwnd, int element_id,
                                 const unsigned char* tag_bytes, int tag_len) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    if (!el) return 0;
    return el->add_tag(utf8_to_wide(tag_bytes, tag_len)) ? 1 : 0;
}

int __stdcall EU_RemoveInputTagItem(HWND hwnd, int element_id, int tag_index) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    if (!el) return 0;
    return el->remove_tag(tag_index) ? 1 : 0;
}

void __stdcall EU_SetInputTagInputValue(HWND hwnd, int element_id,
                                        const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<InputTag>(hwnd, element_id)) {
        el->set_input_value(utf8_to_wide(value_bytes, value_len));
    }
}

int __stdcall EU_GetInputTagInputValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->input_value);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return needed;
}

int __stdcall EU_GetInputTagItem(HWND hwnd, int element_id, int tag_index, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<InputTag>(hwnd, element_id);
    if (!el || tag_index < 0 || tag_index >= (int)el->tags.size()) return 0;
    std::string utf8 = wide_to_utf8(el->tags[tag_index]);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return needed;
}

void __stdcall EU_SetInputTagChangeCallback(HWND hwnd, int element_id, ElementTextCallback cb) {
    if (auto* el = find_typed_element<InputTag>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetSelectOptions(HWND hwnd, int element_id,
                                   const unsigned char* options_bytes, int options_len) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_options(split_option_list(options_bytes, options_len));
    }
}

void __stdcall EU_SetSelectIndex(HWND hwnd, int element_id, int index) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_selected_index(index);
    }
}

int __stdcall EU_GetSelectIndex(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

void __stdcall EU_SetSelectOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

int __stdcall EU_GetSelectOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return (el && el->open) ? 1 : 0;
}

void __stdcall EU_SetSelectSearch(HWND hwnd, int element_id,
                                  const unsigned char* search_bytes, int search_len) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_search_text(utf8_to_wide(search_bytes, search_len));
    }
}

void __stdcall EU_SetSelectOptionDisabled(HWND hwnd, int element_id, int option_index, int disabled) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_option_disabled(option_index, disabled != 0);
    }
}

int __stdcall EU_GetSelectOptionCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return el ? el->option_count() : 0;
}

int __stdcall EU_GetSelectMatchedCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return el ? el->matched_count() : 0;
}

int __stdcall EU_GetSelectOptionDisabled(HWND hwnd, int element_id, int option_index) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return (el && el->is_option_disabled(option_index)) ? 1 : 0;
}

static std::vector<int> parse_index_list(const unsigned char* bytes, int len) {
    std::wstring text = utf8_to_wide(bytes, len);
    std::vector<int> values;
    std::wstring token;
    auto flush = [&]() {
        if (token.empty()) return;
        try {
            values.push_back(std::stoi(token));
        } catch (...) {
        }
        token.clear();
    };
    for (wchar_t ch : text) {
        if (ch == L',' || ch == L'|' || ch == L';' || ch == L' ' || ch == L'\t' || ch == L'\r' || ch == L'\n') {
            flush();
        } else {
            token.push_back(ch);
        }
    }
    flush();
    return values;
}

void __stdcall EU_SetSelectMultiple(HWND hwnd, int element_id, int multiple) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_multiple(multiple != 0);
    }
}

int __stdcall EU_GetSelectMultiple(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return (el && el->multiple) ? 1 : 0;
}

void __stdcall EU_SetSelectSelectedIndices(HWND hwnd, int element_id,
                                           const unsigned char* indices_bytes, int indices_len) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->set_selected_indices(parse_index_list(indices_bytes, indices_len));
    }
}

int __stdcall EU_GetSelectSelectedCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return el ? el->selected_count() : 0;
}

int __stdcall EU_GetSelectSelectedAt(HWND hwnd, int element_id, int position) {
    auto* el = find_typed_element<Select>(hwnd, element_id);
    return el ? el->selected_at(position) : -1;
}

void __stdcall EU_SetSelectChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Select>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetSelectV2Options(HWND hwnd, int element_id,
                                     const unsigned char* options_bytes, int options_len) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_options(split_option_list(options_bytes, options_len));
    }
}

void __stdcall EU_SetSelectV2Index(HWND hwnd, int element_id, int index) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_selected_index(index);
    }
}

void __stdcall EU_SetSelectV2VisibleCount(HWND hwnd, int element_id, int visible_count) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_visible_count(visible_count);
    }
}

int __stdcall EU_GetSelectV2Index(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

int __stdcall EU_GetSelectV2VisibleCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return el ? el->visible_count : 0;
}

void __stdcall EU_SetSelectV2Open(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

int __stdcall EU_GetSelectV2Open(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return (el && el->open) ? 1 : 0;
}

void __stdcall EU_SetSelectV2Search(HWND hwnd, int element_id,
                                    const unsigned char* search_bytes, int search_len) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_search_text(utf8_to_wide(search_bytes, search_len));
    }
}

void __stdcall EU_SetSelectV2OptionDisabled(HWND hwnd, int element_id, int option_index, int disabled) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_option_disabled(option_index, disabled != 0);
    }
}

int __stdcall EU_GetSelectV2OptionCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return el ? el->option_count() : 0;
}

int __stdcall EU_GetSelectV2MatchedCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return el ? el->matched_count() : 0;
}

int __stdcall EU_GetSelectV2OptionDisabled(HWND hwnd, int element_id, int option_index) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return (el && el->is_option_disabled(option_index)) ? 1 : 0;
}

void __stdcall EU_SetSelectV2ScrollIndex(HWND hwnd, int element_id, int scroll_index) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->set_scroll_index(scroll_index);
    }
}

int __stdcall EU_GetSelectV2ScrollIndex(HWND hwnd, int element_id) {
    auto* el = find_typed_element<SelectV2>(hwnd, element_id);
    return el ? el->scroll_index() : 0;
}

void __stdcall EU_SetSelectV2ChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<SelectV2>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetRateValue(HWND hwnd, int element_id, int value) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_value(value);
    }
}

int __stdcall EU_GetRateValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    return el ? el->value : 0;
}

void __stdcall EU_SetRateMax(HWND hwnd, int element_id, int max_value) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_max_value(max_value);
    }
}

int __stdcall EU_GetRateMax(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    return el ? el->max_value : 0;
}

void __stdcall EU_SetRateValueX2(HWND hwnd, int element_id, int value_x2) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_value_x2(value_x2);
    }
}

int __stdcall EU_GetRateValueX2(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    return el ? el->value_x2 : 0;
}

void __stdcall EU_SetRateOptions(HWND hwnd, int element_id, int allow_clear, int allow_half, int readonly) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_options(allow_clear != 0, allow_half != 0, readonly != 0);
    }
}

int __stdcall EU_GetRateOptions(HWND hwnd, int element_id,
                                int* allow_clear, int* allow_half, int* readonly, int* show_score) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    if (!el) return 0;
    if (allow_clear) *allow_clear = el->allow_clear ? 1 : 0;
    if (allow_half) *allow_half = el->allow_half ? 1 : 0;
    if (readonly) *readonly = el->readonly ? 1 : 0;
    if (show_score) *show_score = el->show_score_text ? 1 : 0;
    return 1;
}

void __stdcall EU_SetRateTexts(HWND hwnd, int element_id,
                               const unsigned char* low_bytes, int low_len,
                               const unsigned char* high_bytes, int high_len,
                               int show_score) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_texts(utf8_to_wide(low_bytes, low_len),
                      utf8_to_wide(high_bytes, high_len),
                      show_score != 0);
    }
}

void __stdcall EU_SetRateColors(HWND hwnd, int element_id, Color low_color, Color mid_color, Color high_color) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_colors(low_color, mid_color, high_color);
    }
}

int __stdcall EU_GetRateColors(HWND hwnd, int element_id, Color* low_color, Color* mid_color, Color* high_color) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    if (!el) return 0;
    if (low_color) *low_color = el->low_color;
    if (mid_color) *mid_color = el->mid_color;
    if (high_color) *high_color = el->high_color;
    return 1;
}

void __stdcall EU_SetRateIcons(HWND hwnd, int element_id,
                               const unsigned char* full_bytes, int full_len,
                               const unsigned char* void_bytes, int void_len,
                               const unsigned char* low_bytes, int low_len,
                               const unsigned char* mid_bytes, int mid_len,
                               const unsigned char* high_bytes, int high_len) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_icons(utf8_to_wide(full_bytes, full_len),
                      utf8_to_wide(void_bytes, void_len),
                      utf8_to_wide(low_bytes, low_len),
                      utf8_to_wide(mid_bytes, mid_len),
                      utf8_to_wide(high_bytes, high_len));
    }
}

int __stdcall EU_GetRateIcons(HWND hwnd, int element_id,
                              unsigned char* full_buffer, int full_buffer_size,
                              unsigned char* void_buffer, int void_buffer_size,
                              unsigned char* low_buffer, int low_buffer_size,
                              unsigned char* mid_buffer, int mid_buffer_size,
                              unsigned char* high_buffer, int high_buffer_size) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    if (!el) return 0;
    copy_wide_as_utf8(el->full_icon, full_buffer, full_buffer_size);
    copy_wide_as_utf8(el->void_icon, void_buffer, void_buffer_size);
    copy_wide_as_utf8(el->low_icon, low_buffer, low_buffer_size);
    copy_wide_as_utf8(el->mid_icon, mid_buffer, mid_buffer_size);
    copy_wide_as_utf8(el->high_icon, high_buffer, high_buffer_size);
    return 1;
}

void __stdcall EU_SetRateTextItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_text_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetRateDisplayOptions(HWND hwnd, int element_id,
                                        int show_text, int show_score, Color text_color,
                                        const unsigned char* template_bytes, int template_len) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->set_display_options(show_text != 0, show_score != 0, text_color,
                                utf8_to_wide(template_bytes, template_len));
    }
}

int __stdcall EU_GetRateDisplayOptions(HWND hwnd, int element_id,
                                       int* show_text, int* show_score, Color* text_color,
                                       unsigned char* template_buffer, int template_buffer_size) {
    auto* el = find_typed_element<Rate>(hwnd, element_id);
    if (!el) return 0;
    if (show_text) *show_text = el->show_text ? 1 : 0;
    if (show_score) *show_score = el->show_score ? 1 : 0;
    if (text_color) *text_color = el->score_text_color;
    copy_wide_as_utf8(el->score_template, template_buffer, template_buffer_size);
    return 1;
}

void __stdcall EU_SetRateChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Rate>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetColorPickerColor(HWND hwnd, int element_id, Color color) {
    if (auto* el = find_typed_element<ColorPicker>(hwnd, element_id)) {
        el->set_color(color);
    }
}

int __stdcall EU_GetColorPickerColor(HWND hwnd, int element_id) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    return el ? (int)el->value : 0;
}

void __stdcall EU_SetColorPickerAlpha(HWND hwnd, int element_id, int alpha) {
    if (auto* el = find_typed_element<ColorPicker>(hwnd, element_id)) {
        el->set_alpha(alpha);
    }
}

int __stdcall EU_GetColorPickerAlpha(HWND hwnd, int element_id) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    return el ? el->alpha() : 0;
}

int __stdcall EU_SetColorPickerHex(HWND hwnd, int element_id,
                                   const unsigned char* hex_bytes, int hex_len) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    if (!el) return 0;
    return el->set_hex_text(utf8_to_wide(hex_bytes, hex_len)) ? 1 : 0;
}

int __stdcall EU_GetColorPickerHex(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->get_hex_text());
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), (size_t)n);
    buffer[n] = 0;
    return needed;
}

void __stdcall EU_SetColorPickerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<ColorPicker>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

int __stdcall EU_GetColorPickerOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    return (el && el->open) ? 1 : 0;
}

void __stdcall EU_SetColorPickerPalette(HWND hwnd, int element_id, const Color* colors, int count) {
    if (!colors || count <= 0) return;
    if (count > 32) count = 32;
    if (auto* el = find_typed_element<ColorPicker>(hwnd, element_id)) {
        std::vector<Color> palette;
        palette.reserve((size_t)count);
        for (int i = 0; i < count; ++i) {
            Color color = colors[i];
            if ((color >> 24) == 0) color |= 0xFF000000;
            palette.push_back(color);
        }
        el->set_palette(palette);
    }
}

int __stdcall EU_GetColorPickerPaletteCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<ColorPicker>(hwnd, element_id);
    return el ? el->palette_count() : 0;
}

void __stdcall EU_SetColorPickerChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<ColorPicker>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetTagType(HWND hwnd, int element_id, int tag_type) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_type(tag_type);
    }
}

void __stdcall EU_SetTagEffect(HWND hwnd, int element_id, int effect) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_effect(effect);
    }
}

void __stdcall EU_SetTagClosable(HWND hwnd, int element_id, int closable) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_closable(closable != 0);
    }
}

void __stdcall EU_SetTagClosed(HWND hwnd, int element_id, int closed) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_closed(closed != 0);
    }
}

int __stdcall EU_GetTagClosed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tag>(hwnd, element_id);
    return (el && el->closed) ? 1 : 0;
}

int __stdcall EU_GetTagOptions(HWND hwnd, int element_id,
                               int* tag_type, int* effect, int* closable, int* closed) {
    auto* el = find_typed_element<Tag>(hwnd, element_id);
    if (!el) return 0;
    if (tag_type) *tag_type = el->tag_type;
    if (effect) *effect = el->effect;
    if (closable) *closable = el->closable ? 1 : 0;
    if (closed) *closed = el->closed ? 1 : 0;
    return 1;
}

void __stdcall EU_SetTagSize(HWND hwnd, int element_id, int size_preset) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_size_preset(size_preset);
    }
}

void __stdcall EU_SetTagThemeColor(HWND hwnd, int element_id, Color color) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->set_theme_color(color);
    }
}

int __stdcall EU_GetTagVisualOptions(HWND hwnd, int element_id,
                                     int* size_preset, Color* theme_color) {
    auto* el = find_typed_element<Tag>(hwnd, element_id);
    if (!el) return 0;
    if (size_preset) *size_preset = el->size_preset;
    if (theme_color) *theme_color = el->theme_color;
    return 1;
}

void __stdcall EU_SetTagCloseCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    if (auto* el = find_typed_element<Tag>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetBadgeValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_SetBadgeMax(HWND hwnd, int element_id, int max_value) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_max_value(max_value);
    }
}

void __stdcall EU_SetBadgeType(HWND hwnd, int element_id, int badge_type) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_type(badge_type);
    }
}

void __stdcall EU_SetBadgeDot(HWND hwnd, int element_id, int dot) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_dot(dot != 0);
    }
}

void __stdcall EU_SetBadgeOptions(HWND hwnd, int element_id,
                                  int dot, int show_zero, int offset_x, int offset_y) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_options(dot != 0, show_zero != 0, offset_x, offset_y);
    }
}

int __stdcall EU_GetBadgeHidden(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Badge>(hwnd, element_id);
    return (el && el->is_hidden()) ? 1 : 0;
}

int __stdcall EU_GetBadgeOptions(HWND hwnd, int element_id,
                                 int* max_value, int* dot, int* show_zero, int* offset_x, int* offset_y) {
    auto* el = find_typed_element<Badge>(hwnd, element_id);
    if (!el) return 0;
    if (max_value) *max_value = el->max_value;
    if (dot) *dot = el->dot ? 1 : 0;
    if (show_zero) *show_zero = el->show_zero ? 1 : 0;
    if (offset_x) *offset_x = el->offset_x;
    if (offset_y) *offset_y = el->offset_y;
    return 1;
}

int __stdcall EU_GetBadgeType(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Badge>(hwnd, element_id);
    return el ? el->get_type() : 0;
}

void __stdcall EU_SetBadgeLayoutOptions(HWND hwnd, int element_id,
                                        int placement, int standalone) {
    if (auto* el = find_typed_element<Badge>(hwnd, element_id)) {
        el->set_layout_options(placement, standalone != 0);
    }
}

int __stdcall EU_GetBadgeLayoutOptions(HWND hwnd, int element_id,
                                       int* placement, int* standalone) {
    auto* el = find_typed_element<Badge>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (standalone) *standalone = el->standalone ? 1 : 0;
    return 1;
}

static std::vector<std::pair<Color, int>> parse_progress_color_stops(const unsigned char* bytes, int len) {
    std::vector<std::pair<Color, int>> stops;
    std::wstring full = utf8_to_wide(bytes, len);
    for (const auto& entry : split_wide_list(full, L"|\n\r")) {
        if (trim_wide(entry).empty()) continue;
        std::vector<std::wstring> fields = split_wide_list(entry, L"\t");
        if (fields.size() < 2) fields = split_wide_list(entry, L":,");
        if (fields.size() < 2) continue;
        Color color = parse_timeline_color(fields[0]);
        int percentage = _wtoi(trim_wide(fields[1]).c_str());
        if (percentage < 0) percentage = 0;
        if (percentage > 100) percentage = 100;
        if (color) stops.push_back({ color, percentage });
    }
    std::sort(stops.begin(), stops.end(),
        [](const auto& a, const auto& b) { return a.second < b.second; });
    return stops;
}

void __stdcall EU_SetProgressPercentage(HWND hwnd, int element_id, int percentage) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_percentage(percentage);
    }
}

int __stdcall EU_GetProgressPercentage(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return el ? el->percentage : 0;
}

void __stdcall EU_SetProgressStatus(HWND hwnd, int element_id, int status) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_status(status);
    }
}

int __stdcall EU_GetProgressStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return el ? el->status : 0;
}

void __stdcall EU_SetProgressShowText(HWND hwnd, int element_id, int show_text) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_show_text(show_text != 0);
    }
}

void __stdcall EU_SetProgressOptions(HWND hwnd, int element_id,
                                     int progress_type, int stroke_width, int show_text) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_options(progress_type, stroke_width, show_text != 0);
    }
}

int __stdcall EU_GetProgressOptions(HWND hwnd, int element_id,
                                    int* progress_type, int* stroke_width, int* show_text) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    if (!el) return 0;
    if (progress_type) *progress_type = el->progress_type;
    if (stroke_width) *stroke_width = el->stroke_width;
    if (show_text) *show_text = el->show_text ? 1 : 0;
    return 1;
}

void __stdcall EU_SetProgressFormatOptions(HWND hwnd, int element_id,
                                           int text_format, int striped) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_format_options(text_format, striped != 0);
    }
}

int __stdcall EU_GetProgressFormatOptions(HWND hwnd, int element_id,
                                           int* text_format, int* striped) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    if (!el) return 0;
    if (text_format) *text_format = el->text_format;
    if (striped) *striped = el->striped ? 1 : 0;
    return 1;
}

void __stdcall EU_SetProgressTextInside(HWND hwnd, int element_id, int text_inside) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_text_inside(text_inside != 0);
    }
}

int __stdcall EU_GetProgressTextInside(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return (el && el->text_inside) ? 1 : 0;
}

void __stdcall EU_SetProgressColors(HWND hwnd, int element_id, Color fill, Color track, Color text) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_colors(fill, track, text);
    }
}

int __stdcall EU_GetProgressColors(HWND hwnd, int element_id, Color* fill, Color* track, Color* text) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    if (!el) return 0;
    if (fill) *fill = el->fill_color;
    if (track) *track = el->track_color;
    if (text) *text = el->text_color;
    return 1;
}

void __stdcall EU_SetProgressColorStops(HWND hwnd, int element_id,
                                        const unsigned char* stops_bytes, int stops_len) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_color_stops(parse_progress_color_stops(stops_bytes, stops_len));
    }
}

int __stdcall EU_GetProgressColorStopCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return el ? (int)el->color_stops.size() : 0;
}

int __stdcall EU_GetProgressColorStop(HWND hwnd, int element_id, int index,
                                      Color* color, int* percentage) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    if (!el || index < 0 || index >= (int)el->color_stops.size()) return 0;
    if (color) *color = el->color_stops[index].first;
    if (percentage) *percentage = el->color_stops[index].second;
    return 1;
}

void __stdcall EU_SetProgressCompleteText(HWND hwnd, int element_id,
                                          const unsigned char* bytes, int len) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_complete_text(utf8_to_wide(bytes, len));
    }
}

int __stdcall EU_GetProgressCompleteText(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->complete_text, buffer, buffer_size) : 0;
}

void __stdcall EU_SetProgressTextTemplate(HWND hwnd, int element_id,
                                          const unsigned char* bytes, int len) {
    if (auto* el = find_typed_element<Progress>(hwnd, element_id)) {
        el->set_text_template(utf8_to_wide(bytes, len));
    }
}

int __stdcall EU_GetProgressTextTemplate(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Progress>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->text_template, buffer, buffer_size) : 0;
}

void __stdcall EU_SetAvatarShape(HWND hwnd, int element_id, int shape) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_shape(shape);
    }
}

void __stdcall EU_SetAvatarSource(HWND hwnd, int element_id,
                                  const unsigned char* src_bytes, int src_len) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_source(utf8_to_wide(src_bytes, src_len));
    }
}

void __stdcall EU_SetAvatarFallbackSource(HWND hwnd, int element_id,
                                          const unsigned char* src_bytes, int src_len) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_fallback_source(utf8_to_wide(src_bytes, src_len));
    }
}

void __stdcall EU_SetAvatarIcon(HWND hwnd, int element_id,
                                const unsigned char* icon_bytes, int icon_len) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_icon(utf8_to_wide(icon_bytes, icon_len));
    }
}

void __stdcall EU_SetAvatarErrorText(HWND hwnd, int element_id,
                                     const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_error_text(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_SetAvatarFit(HWND hwnd, int element_id, int fit) {
    if (auto* el = find_typed_element<Avatar>(hwnd, element_id)) {
        el->set_fit(fit);
    }
}

int __stdcall EU_GetAvatarImageStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Avatar>(hwnd, element_id);
    if (!el) return 0;
    return el->image_status;
}

int __stdcall EU_GetAvatarOptions(HWND hwnd, int element_id, int* shape, int* fit) {
    auto* el = find_typed_element<Avatar>(hwnd, element_id);
    if (!el) return 0;
    if (shape) *shape = el->shape;
    if (fit) *fit = el->fit;
    return 1;
}

void __stdcall EU_SetEmptyDescription(HWND hwnd, int element_id,
                                      const unsigned char* desc_bytes, int desc_len) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->set_description(utf8_to_wide(desc_bytes, desc_len));
    }
}

void __stdcall EU_SetEmptyOptions(HWND hwnd, int element_id,
                                  const unsigned char* icon_bytes, int icon_len,
                                  const unsigned char* action_bytes, int action_len) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->set_icon(utf8_to_wide(icon_bytes, icon_len));
        el->set_action(utf8_to_wide(action_bytes, action_len));
    }
}

void __stdcall EU_SetEmptyActionClicked(HWND hwnd, int element_id, int clicked) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->set_action_clicked(clicked != 0);
    }
}

int __stdcall EU_GetEmptyActionClicked(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Empty>(hwnd, element_id);
    return (el && el->action_clicked) ? 1 : 0;
}

void __stdcall EU_SetEmptyActionCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->action_cb = cb;
    }
}

void __stdcall EU_SetEmptyImage(HWND hwnd, int element_id,
                                const unsigned char* image_bytes, int image_len) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->set_image(utf8_to_wide(image_bytes, image_len));
    }
}

void __stdcall EU_SetEmptyImageSize(HWND hwnd, int element_id, int image_size) {
    if (auto* el = find_typed_element<Empty>(hwnd, element_id)) {
        el->set_image_size(image_size);
        if (WindowState* st = window_state(hwnd)) {
            el->apply_dpi_scale(st->dpi_scale);
        }
    }
}

int __stdcall EU_GetEmptyImageStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Empty>(hwnd, element_id);
    return el ? el->image_status : -1;
}

int __stdcall EU_GetEmptyImageSize(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Empty>(hwnd, element_id);
    return el ? el->logical_image_size : -1;
}

void __stdcall EU_SetSkeletonRows(HWND hwnd, int element_id, int rows) {
    if (auto* el = find_typed_element<Skeleton>(hwnd, element_id)) {
        el->set_rows(rows);
    }
}

void __stdcall EU_SetSkeletonAnimated(HWND hwnd, int element_id, int animated) {
    if (auto* el = find_typed_element<Skeleton>(hwnd, element_id)) {
        el->set_animated(animated != 0);
    }
}

void __stdcall EU_SetSkeletonLoading(HWND hwnd, int element_id, int loading) {
    if (auto* el = find_typed_element<Skeleton>(hwnd, element_id)) {
        el->set_loading(loading != 0);
    }
}

void __stdcall EU_SetSkeletonOptions(HWND hwnd, int element_id,
                                     int rows, int animated, int loading, int show_avatar) {
    if (auto* el = find_typed_element<Skeleton>(hwnd, element_id)) {
        el->set_options(rows, animated != 0, loading != 0, show_avatar != 0);
    }
}

int __stdcall EU_GetSkeletonLoading(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Skeleton>(hwnd, element_id);
    return (el && el->loading) ? 1 : 0;
}

int __stdcall EU_GetSkeletonOptions(HWND hwnd, int element_id,
                                    int* rows, int* animated, int* loading, int* show_avatar) {
    auto* el = find_typed_element<Skeleton>(hwnd, element_id);
    if (!el) return 0;
    if (rows) *rows = el->rows;
    if (animated) *animated = el->animated ? 1 : 0;
    if (loading) *loading = el->loading ? 1 : 0;
    if (show_avatar) *show_avatar = el->show_avatar ? 1 : 0;
    return 1;
}

void __stdcall EU_SetDescriptionsItems(HWND hwnd, int element_id,
                                       const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_items(parse_description_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetDescriptionsColumns(HWND hwnd, int element_id, int columns) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_columns(columns);
    }
}

void __stdcall EU_SetDescriptionsBordered(HWND hwnd, int element_id, int bordered) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_bordered(bordered != 0);
    }
}

void __stdcall EU_SetDescriptionsLayout(HWND hwnd, int element_id, int direction,
                                        int size, int columns, int bordered) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_layout(direction, size, columns, bordered != 0);
    }
}

void __stdcall EU_SetDescriptionsItemsEx(HWND hwnd, int element_id,
                                         const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_rich_items(parse_description_items_ex(items_bytes, items_len));
    }
}

void __stdcall EU_SetDescriptionsOptions(HWND hwnd, int element_id, int columns,
                                         int bordered, int label_width,
                                         int min_row_height, int wrap_values) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_options(columns, bordered != 0, label_width, min_row_height, wrap_values != 0);
    }
}

int __stdcall EU_GetDescriptionsItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Descriptions>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

void __stdcall EU_SetDescriptionsAdvancedOptions(HWND hwnd, int element_id,
                                                 int responsive, int last_item_span) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_advanced_options(responsive != 0, last_item_span != 0);
    }
}

void __stdcall EU_SetDescriptionsColors(HWND hwnd, int element_id,
                                        Color border, Color label_bg, Color content_bg,
                                        Color label_fg, Color content_fg, Color title_fg) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_colors(border, label_bg, content_bg, label_fg, content_fg, title_fg);
    }
}

void __stdcall EU_SetDescriptionsExtra(HWND hwnd, int element_id,
                                       const unsigned char* emoji_bytes, int emoji_len,
                                       const unsigned char* text_bytes, int text_len,
                                       int visible, int variant) {
    if (auto* el = find_typed_element<Descriptions>(hwnd, element_id)) {
        el->set_extra(utf8_to_wide(emoji_bytes, emoji_len),
                      utf8_to_wide(text_bytes, text_len),
                      visible != 0, variant);
    }
}

int __stdcall EU_GetDescriptionsOptions(HWND hwnd, int element_id,
                                        int* columns, int* bordered,
                                        int* label_width, int* min_row_height,
                                        int* wrap_values, int* responsive,
                                        int* last_item_span) {
    auto* el = find_typed_element<Descriptions>(hwnd, element_id);
    if (!el) return 0;
    if (columns) *columns = el->columns;
    if (bordered) *bordered = el->bordered ? 1 : 0;
    if (label_width) *label_width = el->label_width;
    if (min_row_height) *min_row_height = el->min_row_height;
    if (wrap_values) *wrap_values = el->wrap_values ? 1 : 0;
    if (responsive) *responsive = el->responsive ? 1 : 0;
    if (last_item_span) *last_item_span = el->last_item_span ? 1 : 0;
    return 1;
}

int __stdcall EU_GetDescriptionsFullState(HWND hwnd, int element_id,
                                          int* direction, int* size,
                                          int* columns, int* bordered,
                                          int* item_count, int* extra_click_count,
                                          int* responsive, int* wrap_values) {
    auto* el = find_typed_element<Descriptions>(hwnd, element_id);
    if (!el) return 0;
    if (direction) *direction = el->direction;
    if (size) *size = el->size;
    if (columns) *columns = el->columns;
    if (bordered) *bordered = el->bordered ? 1 : 0;
    if (item_count) *item_count = (int)el->rich_items.size();
    if (extra_click_count) *extra_click_count = el->extra_click_count;
    if (responsive) *responsive = el->responsive ? 1 : 0;
    if (wrap_values) *wrap_values = el->wrap_values ? 1 : 0;
    return 1;
}

void __stdcall EU_SetTableData(HWND hwnd, int element_id,
                               const unsigned char* columns_bytes, int columns_len,
                               const unsigned char* rows_bytes, int rows_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_columns(split_option_list(columns_bytes, columns_len));
        el->set_rows(parse_table_rows(rows_bytes, rows_len));
    }
}

void __stdcall EU_SetTableStriped(HWND hwnd, int element_id, int striped) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_striped(striped != 0);
    }
}

void __stdcall EU_SetTableBordered(HWND hwnd, int element_id, int bordered) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_bordered(bordered != 0);
    }
}

void __stdcall EU_SetTableEmptyText(HWND hwnd, int element_id,
                                    const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_empty_text(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_SetTableSelectedRow(HWND hwnd, int element_id, int row_index) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_selected_row(row_index);
    }
}

int __stdcall EU_GetTableSelectedRow(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    return el ? el->selected_row : -1;
}

int __stdcall EU_GetTableRowCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    return el ? el->row_count() : 0;
}

int __stdcall EU_GetTableColumnCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    return el ? (int)el->columns.size() : 0;
}

void __stdcall EU_SetTableOptions(HWND hwnd, int element_id, int striped,
                                  int bordered, int row_height,
                                  int header_height, int selectable) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_options(striped != 0, bordered != 0, row_height, header_height, selectable != 0);
    }
}

void __stdcall EU_SetTableSort(HWND hwnd, int element_id, int column_index, int desc) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_sort(column_index, desc != 0);
    }
}

void __stdcall EU_SetTableScrollRow(HWND hwnd, int element_id, int scroll_row) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_scroll_row(scroll_row);
    }
}

void __stdcall EU_SetTableColumnWidth(HWND hwnd, int element_id, int column_width) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_column_width(column_width);
    }
}

int __stdcall EU_GetTableOptions(HWND hwnd, int element_id,
                                 int* striped, int* bordered,
                                 int* row_height, int* header_height,
                                 int* selectable, int* sort_column,
                                 int* sort_desc, int* scroll_row,
                                 int* column_width) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    if (!el) return 0;
    if (striped) *striped = el->striped ? 1 : 0;
    if (bordered) *bordered = el->bordered ? 1 : 0;
    if (row_height) *row_height = el->row_height_value;
    if (header_height) *header_height = el->header_height_value;
    if (selectable) *selectable = el->selectable ? 1 : 0;
    if (sort_column) *sort_column = el->sort_column;
    if (sort_desc) *sort_desc = el->sort_desc ? 1 : 0;
    if (scroll_row) *scroll_row = el->scroll_row;
    if (column_width) *column_width = el->fixed_column_width;
    return 1;
}

void __stdcall EU_SetTableColumnsEx(HWND hwnd, int element_id,
                                    const unsigned char* columns_bytes, int columns_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_columns_ex(utf8_to_wide(columns_bytes, columns_len));
    }
}

void __stdcall EU_SetTableRowsEx(HWND hwnd, int element_id,
                                 const unsigned char* rows_bytes, int rows_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_rows_ex(utf8_to_wide(rows_bytes, rows_len));
    }
}

void __stdcall EU_SetTableCellEx(HWND hwnd, int element_id, int row, int col, int type,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* options_bytes, int options_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_cell_ex(row, col, type, utf8_to_wide(value_bytes, value_len),
                        utf8_to_wide(options_bytes, options_len));
    }
}

void __stdcall EU_SetTableRowStyle(HWND hwnd, int element_id, int row,
                                   unsigned int bg, unsigned int fg,
                                   int align, int font_flags, int font_size) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_row_style(row, (Color)bg, (Color)fg, align, font_flags, font_size);
    }
}

void __stdcall EU_SetTableCellStyle(HWND hwnd, int element_id, int row, int col,
                                    unsigned int bg, unsigned int fg,
                                    int align, int font_flags, int font_size) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_cell_style(row, col, (Color)bg, (Color)fg, align, font_flags, font_size);
    }
}

void __stdcall EU_SetTableSelectionMode(HWND hwnd, int element_id, int mode) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->set_selection_mode(mode);
}

void __stdcall EU_SetTableSelectedRows(HWND hwnd, int element_id,
                                       const unsigned char* rows_bytes, int rows_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_selected_rows_text(utf8_to_wide(rows_bytes, rows_len));
    }
}

void __stdcall EU_SetTableFilter(HWND hwnd, int element_id, int col,
                                 const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_filter(col, utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_ClearTableFilter(HWND hwnd, int element_id, int col) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->clear_filter(col);
}

void __stdcall EU_SetTableSearch(HWND hwnd, int element_id,
                                 const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_search(utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_SetTableSpan(HWND hwnd, int element_id, int row, int col,
                               int rowspan, int colspan) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_span(row, col, rowspan, colspan);
    }
}

void __stdcall EU_ClearTableSpans(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->clear_spans();
}

void __stdcall EU_SetTableSummary(HWND hwnd, int element_id,
                                  const unsigned char* values_bytes, int values_len) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_summary(utf8_to_wide(values_bytes, values_len));
    }
}

void __stdcall EU_SetTableRowExpanded(HWND hwnd, int element_id, int row, int expanded) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->set_row_expanded(row, expanded != 0);
}

void __stdcall EU_SetTableTreeOptions(HWND hwnd, int element_id, int enabled, int indent, int lazy) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_tree_options(enabled != 0, indent, lazy != 0);
    }
}

void __stdcall EU_SetTableViewportOptions(HWND hwnd, int element_id, int max_height,
                                          int fixed_header, int horizontal_scroll,
                                          int show_summary) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_viewport_options(max_height, fixed_header != 0, horizontal_scroll != 0, show_summary != 0);
    }
}

void __stdcall EU_SetTableScroll(HWND hwnd, int element_id, int scroll_row_value, int scroll_x) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->set_scroll(scroll_row_value, scroll_x);
}

void __stdcall EU_SetTableHeaderDragOptions(HWND hwnd, int element_id, int column_resize,
                                            int header_height_resize, int min_col_width,
                                            int max_col_width, int min_header_height,
                                            int max_header_height) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_header_drag_options(column_resize != 0, header_height_resize != 0,
                                    min_col_width, max_col_width,
                                    min_header_height, max_header_height);
    }
}

int __stdcall EU_ExportTableExcel(HWND hwnd, int element_id,
                                  const unsigned char* path_bytes, int path_len, int flags) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        return export_table_to_xlsx(*el, utf8_to_wide(path_bytes, path_len), flags) ? 1 : 0;
    }
    return 0;
}

int __stdcall EU_ImportTableExcel(HWND hwnd, int element_id,
                                  const unsigned char* path_bytes, int path_len, int flags) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        return import_table_from_xlsx(*el, utf8_to_wide(path_bytes, path_len), flags) ? 1 : 0;
    }
    return 0;
}

void __stdcall EU_SetTableCellClickCallback(HWND hwnd, int element_id, TableCellCallback cb) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->cell_click_cb = cb;
}

void __stdcall EU_SetTableCellActionCallback(HWND hwnd, int element_id, TableCellCallback cb) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) el->cell_cb = cb;
}

void __stdcall EU_SetTableVirtualOptions(HWND hwnd, int element_id, int enabled,
                                         int row_count, int cache_window) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_virtual_options(enabled != 0, row_count, cache_window);
    }
}

void __stdcall EU_SetTableVirtualRowProvider(HWND hwnd, int element_id, TableVirtualRowCallback cb) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->set_virtual_row_provider(cb);
    }
}

void __stdcall EU_ClearTableVirtualCache(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Table>(hwnd, element_id)) {
        el->clear_virtual_cache();
    }
}

int __stdcall EU_GetTableCellValue(HWND hwnd, int element_id, int row, int col,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->get_cell_value(row, col), buffer, buffer_size) : 0;
}

int __stdcall EU_GetTableFullState(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Table>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->full_state_text(), buffer, buffer_size) : 0;
}

void __stdcall EU_SetCardBody(HWND hwnd, int element_id,
                              const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        el->set_body(utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetCardFooter(HWND hwnd, int element_id,
                                const unsigned char* footer_bytes, int footer_len) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        el->set_footer(utf8_to_wide(footer_bytes, footer_len));
    }
}

void __stdcall EU_SetCardActions(HWND hwnd, int element_id,
                                 const unsigned char* actions_bytes, int actions_len) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        std::vector<std::wstring> actions;
        for (const auto& item : split_wide_list(utf8_to_wide(actions_bytes, actions_len), L"|\t\n\r")) {
            if (!item.empty()) actions.push_back(item);
        }
        el->set_actions(actions);
    }
}

int __stdcall EU_GetCardAction(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Card>(hwnd, element_id);
    return el ? el->action_index : -1;
}

void __stdcall EU_ResetCardAction(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        el->reset_action();
    }
}

void __stdcall EU_SetCardShadow(HWND hwnd, int element_id, int shadow) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        el->set_shadow(shadow);
    }
}

void __stdcall EU_SetCardOptions(HWND hwnd, int element_id, int shadow, int hoverable) {
    if (auto* el = find_typed_element<Card>(hwnd, element_id)) {
        el->set_options(shadow, hoverable != 0);
    }
}

int __stdcall EU_GetCardOptions(HWND hwnd, int element_id,
                                int* shadow, int* hoverable, int* action_count) {
    auto* el = find_typed_element<Card>(hwnd, element_id);
    if (!el) return 0;
    if (shadow) *shadow = el->shadow;
    if (hoverable) *hoverable = el->hoverable ? 1 : 0;
    if (action_count) *action_count = (int)el->actions.size();
    return 1;
}

void __stdcall EU_SetCollapseItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Collapse>(hwnd, element_id)) {
        el->set_items(parse_collapse_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetCollapseActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Collapse>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

int __stdcall EU_GetCollapseActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Collapse>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetCollapseItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Collapse>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

void __stdcall EU_SetCollapseOptions(HWND hwnd, int element_id, int accordion,
                                     int allow_collapse,
                                     const unsigned char* disabled_bytes,
                                     int disabled_len) {
    if (auto* el = find_typed_element<Collapse>(hwnd, element_id)) {
        el->set_options(accordion != 0, allow_collapse != 0,
                        parse_index_set(disabled_bytes, disabled_len));
    }
}

void __stdcall EU_SetCollapseAdvancedOptions(HWND hwnd, int element_id, int accordion,
                                             int allow_collapse, int animated,
                                             const unsigned char* disabled_bytes,
                                             int disabled_len) {
    if (auto* el = find_typed_element<Collapse>(hwnd, element_id)) {
        el->set_options(accordion != 0, allow_collapse != 0,
                        parse_index_set(disabled_bytes, disabled_len),
                        animated != 0);
    }
}

int __stdcall EU_GetCollapseOptions(HWND hwnd, int element_id,
                                    int* accordion, int* allow_collapse,
                                    int* animated, int* disabled_count) {
    auto* el = find_typed_element<Collapse>(hwnd, element_id);
    if (!el) return 0;
    if (accordion) *accordion = el->accordion ? 1 : 0;
    if (allow_collapse) *allow_collapse = el->allow_collapse ? 1 : 0;
    if (animated) *animated = el->animated ? 1 : 0;
    if (disabled_count) *disabled_count = (int)el->disabled_indices.size();
    return 1;
}

void __stdcall EU_SetTimelineItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Timeline>(hwnd, element_id)) {
        el->set_items(parse_timeline_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetTimelineOptions(HWND hwnd, int element_id, int position, int show_time) {
    if (auto* el = find_typed_element<Timeline>(hwnd, element_id)) {
        el->set_options(position, show_time != 0);
    }
}

int __stdcall EU_GetTimelineItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Timeline>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

int __stdcall EU_GetTimelineOptions(HWND hwnd, int element_id,
                                    int* position, int* show_time) {
    auto* el = find_typed_element<Timeline>(hwnd, element_id);
    if (!el) return 0;
    if (position) *position = el->position;
    if (show_time) *show_time = el->show_time ? 1 : 0;
    return 1;
}

void __stdcall EU_SetTimelineAdvancedOptions(HWND hwnd, int element_id,
                                             int position, int show_time,
                                             int reverse, int default_placement) {
    if (auto* el = find_typed_element<Timeline>(hwnd, element_id)) {
        el->set_advanced_options(position, show_time != 0,
                                 reverse != 0, default_placement);
    }
}

int __stdcall EU_GetTimelineAdvancedOptions(HWND hwnd, int element_id,
                                            int* position, int* show_time,
                                            int* reverse, int* default_placement) {
    auto* el = find_typed_element<Timeline>(hwnd, element_id);
    if (!el) return 0;
    if (position) *position = el->position;
    if (show_time) *show_time = el->show_time ? 1 : 0;
    if (reverse) *reverse = el->reverse ? 1 : 0;
    if (default_placement) *default_placement = el->default_placement;
    return 1;
}

void __stdcall EU_SetStatisticValue(HWND hwnd, int element_id,
                                    const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_SetStatisticFormat(HWND hwnd, int element_id,
                                     const unsigned char* title_bytes, int title_len,
                                     const unsigned char* prefix_bytes, int prefix_len,
                                     const unsigned char* suffix_bytes, int suffix_len) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_format(utf8_to_wide(title_bytes, title_len),
                       utf8_to_wide(prefix_bytes, prefix_len),
                       utf8_to_wide(suffix_bytes, suffix_len));
    }
}

void __stdcall EU_SetStatisticOptions(HWND hwnd, int element_id,
                                      int precision, int animated) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_options(precision, animated != 0);
    }
}

int __stdcall EU_GetStatisticOptions(HWND hwnd, int element_id,
                                     int* precision, int* animated) {
    auto* el = find_typed_element<Statistic>(hwnd, element_id);
    if (!el) return 0;
    if (precision) *precision = el->precision;
    if (animated) *animated = el->animated ? 1 : 0;
    return 1;
}

void __stdcall EU_SetStatisticNumberOptions(HWND hwnd, int element_id,
                                            int precision, int animated, int use_group_separator,
                                            const unsigned char* group_separator_bytes, int group_separator_len,
                                            const unsigned char* decimal_separator_bytes, int decimal_separator_len) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        std::wstring group = utf8_to_wide(group_separator_bytes, group_separator_len);
        std::wstring decimal = utf8_to_wide(decimal_separator_bytes, decimal_separator_len);
        wchar_t group_ch = group.empty() ? L',' : group[0];
        wchar_t decimal_ch = decimal.empty() ? L'.' : decimal[0];
        el->set_number_options(precision, animated != 0, use_group_separator != 0,
                               group_ch, decimal_ch);
    }
}

void __stdcall EU_SetStatisticAffixOptions(HWND hwnd, int element_id,
                                           const unsigned char* prefix_bytes, int prefix_len,
                                           const unsigned char* suffix_bytes, int suffix_len,
                                           Color prefix_color, Color suffix_color, Color value_color,
                                           int suffix_clickable) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_affix_options(utf8_to_wide(prefix_bytes, prefix_len),
                              utf8_to_wide(suffix_bytes, suffix_len),
                              prefix_color, suffix_color, value_color,
                              suffix_clickable != 0);
    }
}

void __stdcall EU_SetStatisticDisplayText(HWND hwnd, int element_id,
                                          const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_display_text(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_SetStatisticCountdown(HWND hwnd, int element_id,
                                        long long target_unix_ms,
                                        const unsigned char* format_bytes, int format_len) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_countdown(target_unix_ms, utf8_to_wide(format_bytes, format_len));
    }
}

void __stdcall EU_SetStatisticCountdownState(HWND hwnd, int element_id, int paused) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->set_countdown_paused(paused != 0);
    }
}

void __stdcall EU_AddStatisticCountdownTime(HWND hwnd, int element_id, long long delta_ms) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->add_countdown_time(delta_ms);
    }
}

void __stdcall EU_SetStatisticFinishCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->finish_cb = cb;
    }
}

void __stdcall EU_SetStatisticSuffixClickCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    if (auto* el = find_typed_element<Statistic>(hwnd, element_id)) {
        el->suffix_click_cb = cb;
    }
}

int __stdcall EU_GetStatisticFullState(HWND hwnd, int element_id,
                                       int* mode, int* precision, int* animated,
                                       int* use_group_separator, int* countdown_paused,
                                       int* countdown_finished, int* suffix_click_count,
                                       long long* remaining_ms) {
    auto* el = find_typed_element<Statistic>(hwnd, element_id);
    if (!el) return 0;
    if (mode) *mode = el->mode;
    if (precision) *precision = el->precision;
    if (animated) *animated = el->animated ? 1 : 0;
    if (use_group_separator) *use_group_separator = el->group_separator ? 1 : 0;
    if (countdown_paused) *countdown_paused = el->countdown_paused ? 1 : 0;
    if (countdown_finished) *countdown_finished = el->countdown_finished ? 1 : 0;
    if (suffix_click_count) *suffix_click_count = el->suffix_click_count;
    if (remaining_ms) *remaining_ms = el->remaining_ms();
    return 1;
}

void __stdcall EU_SetKpiCardData(HWND hwnd, int element_id,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* subtitle_bytes, int subtitle_len,
                                 const unsigned char* trend_bytes, int trend_len,
                                 int trend_type) {
    if (auto* el = find_typed_element<KpiCard>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
        el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
        el->set_trend(utf8_to_wide(trend_bytes, trend_len), trend_type);
    }
}

void __stdcall EU_SetKpiCardOptions(HWND hwnd, int element_id, int loading,
                                    const unsigned char* helper_bytes, int helper_len) {
    if (auto* el = find_typed_element<KpiCard>(hwnd, element_id)) {
        el->set_options(loading != 0, utf8_to_wide(helper_bytes, helper_len));
    }
}

int __stdcall EU_GetKpiCardOptions(HWND hwnd, int element_id, int* loading, int* trend_type) {
    auto* el = find_typed_element<KpiCard>(hwnd, element_id);
    if (!el) return 0;
    if (loading) *loading = el->loading ? 1 : 0;
    if (trend_type) *trend_type = el->trend_type;
    return 1;
}

void __stdcall EU_SetTrendData(HWND hwnd, int element_id,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* percent_bytes, int percent_len,
                               const unsigned char* detail_bytes, int detail_len,
                               int direction) {
    if (auto* el = find_typed_element<Trend>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
        el->set_percent(utf8_to_wide(percent_bytes, percent_len));
        el->set_detail(utf8_to_wide(detail_bytes, detail_len));
        el->set_direction(direction);
    }
}

void __stdcall EU_SetTrendOptions(HWND hwnd, int element_id, int inverse, int show_icon) {
    if (auto* el = find_typed_element<Trend>(hwnd, element_id)) {
        el->set_options(inverse != 0, show_icon != 0);
    }
}

int __stdcall EU_GetTrendDirection(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Trend>(hwnd, element_id);
    return el ? el->direction : 0;
}

int __stdcall EU_GetTrendOptions(HWND hwnd, int element_id, int* inverse, int* show_icon) {
    auto* el = find_typed_element<Trend>(hwnd, element_id);
    if (!el) return 0;
    if (inverse) *inverse = el->inverse ? 1 : 0;
    if (show_icon) *show_icon = el->show_icon ? 1 : 0;
    return 1;
}

void __stdcall EU_SetStatusDot(HWND hwnd, int element_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* desc_bytes, int desc_len,
                               int status) {
    if (auto* el = find_typed_element<StatusDot>(hwnd, element_id)) {
        el->set_label(utf8_to_wide(label_bytes, label_len));
        el->set_description(utf8_to_wide(desc_bytes, desc_len));
        el->set_status(status);
    }
}

void __stdcall EU_SetStatusDotOptions(HWND hwnd, int element_id, int pulse, int compact) {
    if (auto* el = find_typed_element<StatusDot>(hwnd, element_id)) {
        el->set_options(pulse != 0, compact != 0);
    }
}

int __stdcall EU_GetStatusDotStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<StatusDot>(hwnd, element_id);
    return el ? el->status : 0;
}

int __stdcall EU_GetStatusDotOptions(HWND hwnd, int element_id, int* pulse, int* compact) {
    auto* el = find_typed_element<StatusDot>(hwnd, element_id);
    if (!el) return 0;
    if (pulse) *pulse = el->pulse ? 1 : 0;
    if (compact) *compact = el->compact ? 1 : 0;
    return 1;
}

void __stdcall EU_SetGaugeValue(HWND hwnd, int element_id, int value,
                                const unsigned char* caption_bytes, int caption_len,
                                int status) {
    if (auto* el = find_typed_element<Gauge>(hwnd, element_id)) {
        el->set_value(value);
        el->set_caption(utf8_to_wide(caption_bytes, caption_len));
        el->set_status(status);
    }
}

void __stdcall EU_SetGaugeOptions(HWND hwnd, int element_id, int min_value, int max_value,
                                  int warning_value, int danger_value, int stroke_width) {
    if (auto* el = find_typed_element<Gauge>(hwnd, element_id)) {
        el->set_options(min_value, max_value, warning_value, danger_value, stroke_width);
    }
}

int __stdcall EU_GetGaugeValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Gauge>(hwnd, element_id);
    return el ? el->value : 0;
}

int __stdcall EU_GetGaugeStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Gauge>(hwnd, element_id);
    return el ? el->status : 0;
}

int __stdcall EU_GetGaugeOptions(HWND hwnd, int element_id, int* min_value, int* max_value,
                                 int* warning_value, int* danger_value, int* stroke_width) {
    auto* el = find_typed_element<Gauge>(hwnd, element_id);
    if (!el) return 0;
    if (min_value) *min_value = el->min_value;
    if (max_value) *max_value = el->max_value;
    if (warning_value) *warning_value = el->warning_value;
    if (danger_value) *danger_value = el->danger_value;
    if (stroke_width) *stroke_width = el->stroke_width;
    return 1;
}

void __stdcall EU_SetRingProgressValue(HWND hwnd, int element_id, int value,
                                       const unsigned char* label_bytes, int label_len,
                                       int status) {
    if (auto* el = find_typed_element<RingProgress>(hwnd, element_id)) {
        el->set_value(value);
        el->set_label(utf8_to_wide(label_bytes, label_len));
        el->set_status(status);
    }
}

void __stdcall EU_SetRingProgressOptions(HWND hwnd, int element_id,
                                         int stroke_width, int show_center) {
    if (auto* el = find_typed_element<RingProgress>(hwnd, element_id)) {
        el->set_options(stroke_width, show_center != 0);
    }
}

int __stdcall EU_GetRingProgressValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<RingProgress>(hwnd, element_id);
    return el ? el->value : 0;
}

int __stdcall EU_GetRingProgressStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<RingProgress>(hwnd, element_id);
    return el ? el->status : 0;
}

int __stdcall EU_GetRingProgressOptions(HWND hwnd, int element_id,
                                        int* stroke_width, int* show_center) {
    auto* el = find_typed_element<RingProgress>(hwnd, element_id);
    if (!el) return 0;
    if (stroke_width) *stroke_width = el->stroke_width;
    if (show_center) *show_center = el->show_center ? 1 : 0;
    return 1;
}

void __stdcall EU_SetBulletProgressValue(HWND hwnd, int element_id,
                                         int value, int target,
                                         const unsigned char* desc_bytes, int desc_len,
                                         int status) {
    if (auto* el = find_typed_element<BulletProgress>(hwnd, element_id)) {
        el->set_value(value);
        el->set_target(target);
        el->set_description(utf8_to_wide(desc_bytes, desc_len));
        el->set_status(status);
    }
}

void __stdcall EU_SetBulletProgressOptions(HWND hwnd, int element_id,
                                           int good_threshold, int warn_threshold,
                                           int show_target) {
    if (auto* el = find_typed_element<BulletProgress>(hwnd, element_id)) {
        el->set_options(good_threshold, warn_threshold, show_target != 0);
    }
}

int __stdcall EU_GetBulletProgressValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BulletProgress>(hwnd, element_id);
    return el ? el->value : 0;
}

int __stdcall EU_GetBulletProgressTarget(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BulletProgress>(hwnd, element_id);
    return el ? el->target : 0;
}

int __stdcall EU_GetBulletProgressStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BulletProgress>(hwnd, element_id);
    return el ? el->status : 0;
}

int __stdcall EU_GetBulletProgressOptions(HWND hwnd, int element_id,
                                          int* good_threshold, int* warn_threshold,
                                          int* show_target) {
    auto* el = find_typed_element<BulletProgress>(hwnd, element_id);
    if (!el) return 0;
    if (good_threshold) *good_threshold = el->good_threshold;
    if (warn_threshold) *warn_threshold = el->warn_threshold;
    if (show_target) *show_target = el->show_target ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLineChartData(HWND hwnd, int element_id,
                                   const unsigned char* points_bytes, int points_len) {
    if (auto* el = find_typed_element<LineChart>(hwnd, element_id)) {
        el->set_points(parse_chart_points(points_bytes, points_len));
    }
}

void __stdcall EU_SetLineChartSeries(HWND hwnd, int element_id,
                                     const unsigned char* series_bytes, int series_len) {
    if (auto* el = find_typed_element<LineChart>(hwnd, element_id)) {
        el->set_series(parse_chart_series(series_bytes, series_len));
    }
}

void __stdcall EU_SetLineChartOptions(HWND hwnd, int element_id,
                                      int chart_style, int show_axis,
                                      int show_area, int show_tooltip) {
    if (auto* el = find_typed_element<LineChart>(hwnd, element_id)) {
        el->set_options(chart_style, show_axis != 0, show_area != 0, show_tooltip != 0);
    }
}

void __stdcall EU_SetLineChartSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<LineChart>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

int __stdcall EU_GetLineChartPointCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<LineChart>(hwnd, element_id);
    return el ? (int)el->points.size() : 0;
}

int __stdcall EU_GetLineChartSeriesCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<LineChart>(hwnd, element_id);
    return el ? (int)el->series.size() : 0;
}

int __stdcall EU_GetLineChartSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<LineChart>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

int __stdcall EU_GetLineChartOptions(HWND hwnd, int element_id,
                                     int* chart_style, int* show_axis,
                                     int* show_area, int* show_tooltip) {
    auto* el = find_typed_element<LineChart>(hwnd, element_id);
    if (!el) return 0;
    if (chart_style) *chart_style = el->chart_style;
    if (show_axis) *show_axis = el->show_axis ? 1 : 0;
    if (show_area) *show_area = el->show_area ? 1 : 0;
    if (show_tooltip) *show_tooltip = el->show_tooltip ? 1 : 0;
    return 1;
}

void __stdcall EU_SetBarChartData(HWND hwnd, int element_id,
                                  const unsigned char* bars_bytes, int bars_len) {
    if (auto* el = find_typed_element<BarChart>(hwnd, element_id)) {
        el->set_bars(parse_chart_points(bars_bytes, bars_len));
    }
}

void __stdcall EU_SetBarChartSeries(HWND hwnd, int element_id,
                                    const unsigned char* series_bytes, int series_len) {
    if (auto* el = find_typed_element<BarChart>(hwnd, element_id)) {
        el->set_series(parse_chart_series(series_bytes, series_len));
    }
}

void __stdcall EU_SetBarChartOptions(HWND hwnd, int element_id,
                                     int orientation, int show_values, int show_axis) {
    if (auto* el = find_typed_element<BarChart>(hwnd, element_id)) {
        el->set_options(orientation, show_values != 0, show_axis != 0);
    }
}

void __stdcall EU_SetBarChartSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<BarChart>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

int __stdcall EU_GetBarChartBarCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BarChart>(hwnd, element_id);
    return el ? (int)el->bars.size() : 0;
}

int __stdcall EU_GetBarChartSeriesCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BarChart>(hwnd, element_id);
    return el ? (int)el->series.size() : 0;
}

int __stdcall EU_GetBarChartSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<BarChart>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

int __stdcall EU_GetBarChartOptions(HWND hwnd, int element_id,
                                    int* orientation, int* show_values, int* show_axis) {
    auto* el = find_typed_element<BarChart>(hwnd, element_id);
    if (!el) return 0;
    if (orientation) *orientation = el->orientation;
    if (show_values) *show_values = el->show_values ? 1 : 0;
    if (show_axis) *show_axis = el->show_axis ? 1 : 0;
    return 1;
}

void __stdcall EU_SetDonutChartData(HWND hwnd, int element_id,
                                    const unsigned char* slices_bytes, int slices_len,
                                    int active_index) {
    if (auto* el = find_typed_element<DonutChart>(hwnd, element_id)) {
        el->set_slices(parse_chart_points(slices_bytes, slices_len));
        el->set_active_index(active_index);
    }
}

void __stdcall EU_SetDonutChartOptions(HWND hwnd, int element_id,
                                       int show_legend, int ring_width) {
    if (auto* el = find_typed_element<DonutChart>(hwnd, element_id)) {
        el->set_options(show_legend != 0, ring_width);
    }
}

void __stdcall EU_SetDonutChartAdvancedOptions(HWND hwnd, int element_id,
                                               int show_legend, int ring_width,
                                               int show_labels) {
    if (auto* el = find_typed_element<DonutChart>(hwnd, element_id)) {
        el->set_options(show_legend != 0, ring_width, show_labels != 0);
    }
}

void __stdcall EU_SetDonutChartActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<DonutChart>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

int __stdcall EU_GetDonutChartSliceCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DonutChart>(hwnd, element_id);
    return el ? (int)el->slices.size() : 0;
}

int __stdcall EU_GetDonutChartActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DonutChart>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetDonutChartOptions(HWND hwnd, int element_id,
                                      int* show_legend, int* ring_width) {
    auto* el = find_typed_element<DonutChart>(hwnd, element_id);
    if (!el) return 0;
    if (show_legend) *show_legend = el->show_legend ? 1 : 0;
    if (ring_width) *ring_width = el->ring_width;
    return 1;
}

int __stdcall EU_GetDonutChartAdvancedOptions(HWND hwnd, int element_id,
                                              int* show_legend, int* ring_width,
                                              int* show_labels) {
    auto* el = find_typed_element<DonutChart>(hwnd, element_id);
    if (!el) return 0;
    if (show_legend) *show_legend = el->show_legend ? 1 : 0;
    if (ring_width) *ring_width = el->ring_width;
    if (show_labels) *show_labels = el->show_labels ? 1 : 0;
    return 1;
}

void __stdcall EU_SetCalendarDate(HWND hwnd, int element_id, int year, int month, int selected_day) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_date(year, month, selected_day);
    }
}

void __stdcall EU_SetCalendarRange(HWND hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_range(min_yyyymmdd, max_yyyymmdd);
    }
}

void __stdcall EU_SetCalendarOptions(HWND hwnd, int element_id, int today_yyyymmdd, int show_today) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_options(today_yyyymmdd, show_today != 0);
    }
}

void __stdcall EU_CalendarMoveMonth(HWND hwnd, int element_id, int delta_months) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->move_month(delta_months);
    }
}

int __stdcall EU_GetCalendarValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    return el ? el->value() : 0;
}

int __stdcall EU_GetCalendarRange(HWND hwnd, int element_id, int* min_yyyymmdd, int* max_yyyymmdd) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    if (min_yyyymmdd) *min_yyyymmdd = el->min_value;
    if (max_yyyymmdd) *max_yyyymmdd = el->max_value;
    return 1;
}

int __stdcall EU_GetCalendarOptions(HWND hwnd, int element_id, int* today_yyyymmdd, int* show_today) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    if (today_yyyymmdd) *today_yyyymmdd = el->today_value;
    if (show_today) *show_today = el->show_today ? 1 : 0;
    return 1;
}

void __stdcall EU_SetCalendarSelectionRange(HWND hwnd, int element_id,
                                            int start_yyyymmdd, int end_yyyymmdd,
                                            int enabled) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_selection_range(start_yyyymmdd, end_yyyymmdd, enabled != 0);
    }
}

int __stdcall EU_GetCalendarSelectionRange(HWND hwnd, int element_id,
                                           int* start_yyyymmdd, int* end_yyyymmdd,
                                           int* enabled) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    int start = 0;
    int end = 0;
    bool is_enabled = false;
    el->get_selection_range(start, end, is_enabled);
    if (start_yyyymmdd) *start_yyyymmdd = start;
    if (end_yyyymmdd) *end_yyyymmdd = end;
    if (enabled) *enabled = is_enabled ? 1 : 0;
    return 1;
}

void __stdcall EU_SetCalendarDisplayRange(HWND hwnd, int element_id,
                                          int start_yyyymmdd, int end_yyyymmdd) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_display_range(start_yyyymmdd, end_yyyymmdd);
    }
}

int __stdcall EU_GetCalendarDisplayRange(HWND hwnd, int element_id,
                                         int* start_yyyymmdd, int* end_yyyymmdd) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    int start = 0;
    int end = 0;
    el->get_display_range(start, end);
    if (start_yyyymmdd) *start_yyyymmdd = start;
    if (end_yyyymmdd) *end_yyyymmdd = end;
    return 1;
}

void __stdcall EU_SetCalendarCellItems(HWND hwnd, int element_id,
                                       const unsigned char* spec_bytes, int spec_len) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_cell_items(utf8_to_wide(spec_bytes, spec_len));
    }
}

int __stdcall EU_GetCalendarCellItems(HWND hwnd, int element_id,
                                      unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->cell_items_spec, buffer, buffer_size);
}

void __stdcall EU_ClearCalendarCellItems(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->clear_cell_items();
    }
}

void __stdcall EU_SetCalendarVisualOptions(HWND hwnd, int element_id,
                                           int show_header, int show_week_header,
                                           int label_mode, int show_adjacent_days,
                                           float cell_radius) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_visual_options(show_header != 0, show_week_header != 0,
                               label_mode, show_adjacent_days != 0,
                               cell_radius);
    }
}

int __stdcall EU_GetCalendarVisualOptions(HWND hwnd, int element_id,
                                          int* show_header, int* show_week_header,
                                          int* label_mode, int* show_adjacent_days,
                                          float* cell_radius) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    int header = 0;
    int week = 0;
    int mode = 0;
    int adjacent = 0;
    float radius = 0.0f;
    el->get_visual_options(header, week, mode, adjacent, radius);
    if (show_header) *show_header = header;
    if (show_week_header) *show_week_header = week;
    if (label_mode) *label_mode = mode;
    if (show_adjacent_days) *show_adjacent_days = adjacent;
    if (cell_radius) *cell_radius = radius;
    return 1;
}

void __stdcall EU_SetCalendarStateColors(HWND hwnd, int element_id,
                                         Color selected_bg, Color selected_fg,
                                         Color range_bg, Color today_border,
                                         Color hover_bg, Color disabled_fg,
                                         Color adjacent_fg) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_state_colors(selected_bg, selected_fg, range_bg, today_border,
                             hover_bg, disabled_fg, adjacent_fg);
    }
}

int __stdcall EU_GetCalendarStateColors(HWND hwnd, int element_id,
                                        Color* selected_bg, Color* selected_fg,
                                        Color* range_bg, Color* today_border,
                                        Color* hover_bg, Color* disabled_fg,
                                        Color* adjacent_fg) {
    auto* el = find_typed_element<Calendar>(hwnd, element_id);
    if (!el) return 0;
    Color sb = 0;
    Color sf = 0;
    Color rb = 0;
    Color tb = 0;
    Color hb = 0;
    Color df = 0;
    Color af = 0;
    el->get_state_colors(sb, sf, rb, tb, hb, df, af);
    if (selected_bg) *selected_bg = sb;
    if (selected_fg) *selected_fg = sf;
    if (range_bg) *range_bg = rb;
    if (today_border) *today_border = tb;
    if (hover_bg) *hover_bg = hb;
    if (disabled_fg) *disabled_fg = df;
    if (adjacent_fg) *adjacent_fg = af;
    return 1;
}

void __stdcall EU_SetCalendarSelectedMarker(HWND hwnd, int element_id,
                                            const unsigned char* marker_bytes, int marker_len) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->set_selected_marker(utf8_to_wide(marker_bytes, marker_len));
    }
}

void __stdcall EU_SetCalendarChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Calendar>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetTreeItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_items(parse_tree_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetTreeSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

int __stdcall EU_GetTreeSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

void __stdcall EU_SetTreeOptions(HWND hwnd, int element_id,
                                 int show_checkbox, int keyboard_navigation, int lazy_mode) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_options(show_checkbox != 0, keyboard_navigation != 0, lazy_mode != 0);
    }
}

int __stdcall EU_GetTreeOptions(HWND hwnd, int element_id,
                                int* show_checkbox, int* keyboard_navigation,
                                int* lazy_mode, int* checked_count, int* last_lazy_index) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    if (!el) return 0;
    if (show_checkbox) *show_checkbox = el->show_checkbox() ? 1 : 0;
    if (keyboard_navigation) *keyboard_navigation = el->keyboard_navigation() ? 1 : 0;
    if (lazy_mode) *lazy_mode = el->lazy_mode() ? 1 : 0;
    if (checked_count) *checked_count = el->checked_count();
    if (last_lazy_index) *last_lazy_index = el->last_lazy_index();
    return 1;
}

void __stdcall EU_SetTreeItemExpanded(HWND hwnd, int element_id, int item_index, int expanded) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_item_expanded(item_index, expanded != 0);
    }
}

void __stdcall EU_ToggleTreeItemExpanded(HWND hwnd, int element_id, int item_index) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->toggle_item_expanded(item_index);
    }
}

int __stdcall EU_GetTreeItemExpanded(HWND hwnd, int element_id, int item_index) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return (el && el->get_item_expanded(item_index)) ? 1 : 0;
}

void __stdcall EU_SetTreeItemChecked(HWND hwnd, int element_id, int item_index, int checked) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_item_checked(item_index, checked != 0);
    }
}

int __stdcall EU_GetTreeItemChecked(HWND hwnd, int element_id, int item_index) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return (el && el->get_item_checked(item_index)) ? 1 : 0;
}

void __stdcall EU_SetTreeItemLazy(HWND hwnd, int element_id, int item_index, int lazy) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_item_lazy(item_index, lazy != 0);
    }
}

int __stdcall EU_GetTreeItemLazy(HWND hwnd, int element_id, int item_index) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return (el && el->get_item_lazy(item_index)) ? 1 : 0;
}

int __stdcall EU_GetTreeVisibleCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? el->visible_count() : 0;
}

void __stdcall EU_SetTreeSelectItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_items(parse_tree_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetTreeSelectSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

int __stdcall EU_GetTreeSelectSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

void __stdcall EU_SetTreeSelectOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

int __stdcall EU_GetTreeSelectOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

void __stdcall EU_SetTreeSelectOptions(HWND hwnd, int element_id,
                                       int multiple, int clearable, int searchable) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_options(multiple != 0, clearable != 0, searchable != 0);
    }
}

int __stdcall EU_GetTreeSelectOptions(HWND hwnd, int element_id,
                                      int* multiple, int* clearable, int* searchable,
                                      int* selected_count, int* matched_count) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    if (!el) return 0;
    if (multiple) *multiple = el->multiple ? 1 : 0;
    if (clearable) *clearable = el->clearable ? 1 : 0;
    if (searchable) *searchable = el->searchable ? 1 : 0;
    if (selected_count) *selected_count = el->selected_count();
    if (matched_count) *matched_count = el->matched_count();
    return 1;
}

void __stdcall EU_SetTreeSelectSearch(HWND hwnd, int element_id,
                                      const unsigned char* search_bytes, int search_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_search_text(utf8_to_wide(search_bytes, search_len));
    }
}

int __stdcall EU_GetTreeSelectSearch(HWND hwnd, int element_id,
                                     unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->search_text);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int copy_len = (std::min)(needed, buffer_size - 1);
    if (copy_len > 0) memcpy(buffer, utf8.data(), copy_len);
    buffer[copy_len] = 0;
    return needed;
}

void __stdcall EU_ClearTreeSelect(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->clear_selection();
    }
}

void __stdcall EU_SetTreeSelectSelectedItems(HWND hwnd, int element_id,
                                             const unsigned char* indices_bytes, int indices_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_selected_items(parse_index_list(indices_bytes, indices_len));
    }
}

int __stdcall EU_GetTreeSelectSelectedCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? el->selected_count() : 0;
}

int __stdcall EU_GetTreeSelectSelectedItem(HWND hwnd, int element_id, int position) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? el->selected_item(position) : -1;
}

void __stdcall EU_SetTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index, int expanded) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_item_expanded(item_index, expanded != 0);
    }
}

void __stdcall EU_ToggleTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->toggle_item_expanded(item_index);
    }
}

int __stdcall EU_GetTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return (el && el->get_item_expanded(item_index)) ? 1 : 0;
}

void __stdcall EU_SetTreeDataJson(HWND hwnd, int element_id,
                                  const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_data_json(utf8_to_wide(json_bytes, json_len));
    }
}

int __stdcall EU_GetTreeDataJson(HWND hwnd, int element_id,
                                 unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->data_json(), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeOptionsJson(HWND hwnd, int element_id,
                                     const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_options_json(utf8_to_wide(json_bytes, json_len));
    }
}

int __stdcall EU_GetTreeStateJson(HWND hwnd, int element_id,
                                  unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->state_json(), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeCheckedKeysJson(HWND hwnd, int element_id,
                                         const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_checked_keys(parse_tree_key_array_json(utf8_to_wide(json_bytes, json_len)));
    }
}

int __stdcall EU_GetTreeCheckedKeysJson(HWND hwnd, int element_id,
                                        unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? copy_wide_as_utf8(serialize_tree_key_array_json(el->checked_keys()), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeExpandedKeysJson(HWND hwnd, int element_id,
                                          const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->set_expanded_keys(parse_tree_key_array_json(utf8_to_wide(json_bytes, json_len)));
    }
}

int __stdcall EU_GetTreeExpandedKeysJson(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeView>(hwnd, element_id);
    return el ? copy_wide_as_utf8(serialize_tree_key_array_json(el->expanded_keys()), buffer, buffer_size) : 0;
}

void __stdcall EU_AppendTreeNodeJson(HWND hwnd, int element_id,
                                     const unsigned char* parent_key_bytes, int parent_key_len,
                                     const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->append_node_json(utf8_to_wide(parent_key_bytes, parent_key_len),
                             utf8_to_wide(json_bytes, json_len));
    }
}

void __stdcall EU_UpdateTreeNodeJson(HWND hwnd, int element_id,
                                     const unsigned char* key_bytes, int key_len,
                                     const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->update_node_json(utf8_to_wide(key_bytes, key_len),
                             utf8_to_wide(json_bytes, json_len));
    }
}

void __stdcall EU_RemoveTreeNodeByKey(HWND hwnd, int element_id,
                                      const unsigned char* key_bytes, int key_len) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) {
        el->remove_node_by_key(utf8_to_wide(key_bytes, key_len));
    }
}

void __stdcall EU_SetTreeNodeEventCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) el->event_cb = cb;
}

void __stdcall EU_SetTreeLazyLoadCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) el->lazy_cb = cb;
}

void __stdcall EU_SetTreeDragCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) el->drag_cb = cb;
}

void __stdcall EU_SetTreeAllowDragCallback(HWND hwnd, int element_id, TreeNodeAllowDragCallback cb) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) el->allow_drag_cb = cb;
}

void __stdcall EU_SetTreeAllowDropCallback(HWND hwnd, int element_id, TreeNodeAllowDropCallback cb) {
    if (auto* el = find_typed_element<TreeView>(hwnd, element_id)) el->allow_drop_cb = cb;
}

void __stdcall EU_SetTreeSelectDataJson(HWND hwnd, int element_id,
                                        const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_data_json(utf8_to_wide(json_bytes, json_len));
    }
}

int __stdcall EU_GetTreeSelectDataJson(HWND hwnd, int element_id,
                                       unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->data_json(), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeSelectOptionsJson(HWND hwnd, int element_id,
                                           const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_options_json(utf8_to_wide(json_bytes, json_len));
    }
}

int __stdcall EU_GetTreeSelectStateJson(HWND hwnd, int element_id,
                                        unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->state_json(), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeSelectSelectedKeysJson(HWND hwnd, int element_id,
                                                const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_selected_keys(parse_tree_key_array_json(utf8_to_wide(json_bytes, json_len)));
    }
}

int __stdcall EU_GetTreeSelectSelectedKeysJson(HWND hwnd, int element_id,
                                               unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? copy_wide_as_utf8(serialize_tree_key_array_json(el->selected_keys()), buffer, buffer_size) : 0;
}

void __stdcall EU_SetTreeSelectExpandedKeysJson(HWND hwnd, int element_id,
                                                const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->set_expanded_keys(parse_tree_key_array_json(utf8_to_wide(json_bytes, json_len)));
    }
}

int __stdcall EU_GetTreeSelectExpandedKeysJson(HWND hwnd, int element_id,
                                               unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<TreeSelect>(hwnd, element_id);
    return el ? copy_wide_as_utf8(serialize_tree_key_array_json(el->expanded_keys()), buffer, buffer_size) : 0;
}

void __stdcall EU_AppendTreeSelectNodeJson(HWND hwnd, int element_id,
                                           const unsigned char* parent_key_bytes, int parent_key_len,
                                           const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->append_node_json(utf8_to_wide(parent_key_bytes, parent_key_len),
                             utf8_to_wide(json_bytes, json_len));
    }
}

void __stdcall EU_UpdateTreeSelectNodeJson(HWND hwnd, int element_id,
                                           const unsigned char* key_bytes, int key_len,
                                           const unsigned char* json_bytes, int json_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->update_node_json(utf8_to_wide(key_bytes, key_len),
                             utf8_to_wide(json_bytes, json_len));
    }
}

void __stdcall EU_RemoveTreeSelectNodeByKey(HWND hwnd, int element_id,
                                            const unsigned char* key_bytes, int key_len) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) {
        el->remove_node_by_key(utf8_to_wide(key_bytes, key_len));
    }
}

void __stdcall EU_SetTreeSelectNodeEventCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) el->event_cb = cb;
}

void __stdcall EU_SetTreeSelectLazyLoadCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) el->lazy_cb = cb;
}

void __stdcall EU_SetTreeSelectDragCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) el->drag_cb = cb;
}

void __stdcall EU_SetTreeSelectAllowDragCallback(HWND hwnd, int element_id, TreeNodeAllowDragCallback cb) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) el->allow_drag_cb = cb;
}

void __stdcall EU_SetTreeSelectAllowDropCallback(HWND hwnd, int element_id, TreeNodeAllowDropCallback cb) {
    if (auto* el = find_typed_element<TreeSelect>(hwnd, element_id)) el->allow_drop_cb = cb;
}

void __stdcall EU_SetTransferItems(HWND hwnd, int element_id,
                                   const unsigned char* left_bytes, int left_len,
                                   const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_items(split_option_list(left_bytes, left_len), split_option_list(right_bytes, right_len));
    }
}

void __stdcall EU_TransferMoveRight(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->move_selected_right();
    }
}

void __stdcall EU_TransferMoveLeft(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->move_selected_left();
    }
}

void __stdcall EU_TransferMoveAllRight(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->move_all_right();
    }
}

void __stdcall EU_TransferMoveAllLeft(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->move_all_left();
    }
}

void __stdcall EU_SetTransferSelected(HWND hwnd, int element_id, int side, int selected_index) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        if (side == 1) el->set_right_selected(selected_index);
        else el->set_left_selected(selected_index);
    }
}

int __stdcall EU_GetTransferSelected(HWND hwnd, int element_id, int side) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    if (!el) return -1;
    return side == 1 ? el->right_selected : el->left_selected;
}

int __stdcall EU_GetTransferCount(HWND hwnd, int element_id, int side) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    if (!el) return 0;
    return side == 1 ? el->right_count() : el->left_count();
}

void __stdcall EU_SetTransferFilters(HWND hwnd, int element_id,
                                     const unsigned char* left_bytes, int left_len,
                                     const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_filters(utf8_to_wide(left_bytes, left_len), utf8_to_wide(right_bytes, right_len));
    }
}

int __stdcall EU_GetTransferMatchedCount(HWND hwnd, int element_id, int side) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return el ? el->matched_count(side) : 0;
}

void __stdcall EU_SetTransferItemDisabled(HWND hwnd, int element_id,
                                          int side, int item_index, int disabled) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_item_disabled(side, item_index, disabled != 0);
    }
}

int __stdcall EU_GetTransferItemDisabled(HWND hwnd, int element_id,
                                         int side, int item_index) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return (el && el->get_item_disabled(side, item_index)) ? 1 : 0;
}

int __stdcall EU_GetTransferDisabledCount(HWND hwnd, int element_id, int side) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return el ? el->disabled_count(side) : 0;
}

void __stdcall EU_SetTransferDataEx(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len,
                                    const unsigned char* target_bytes, int target_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_data_ex(parse_transfer_items_ex(items_bytes, items_len),
                        split_option_list(target_bytes, target_len));
    }
}

void __stdcall EU_SetTransferOptions(HWND hwnd, int element_id,
                                     int filterable, int multiple, int show_footer,
                                     int show_select_all, int show_count, int render_mode) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_options(filterable != 0, multiple != 0, show_footer != 0,
                        show_select_all != 0, show_count != 0, render_mode);
    }
}

int __stdcall EU_GetTransferOptions(HWND hwnd, int element_id,
                                    int* filterable, int* multiple, int* show_footer,
                                    int* show_select_all, int* show_count, int* render_mode) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    if (!el) return 0;
    if (filterable) *filterable = el->filterable ? 1 : 0;
    if (multiple) *multiple = el->multiple ? 1 : 0;
    if (show_footer) *show_footer = el->show_footer ? 1 : 0;
    if (show_select_all) *show_select_all = el->show_select_all ? 1 : 0;
    if (show_count) *show_count = el->show_count ? 1 : 0;
    if (render_mode) *render_mode = el->render_mode;
    return 1;
}

void __stdcall EU_SetTransferTitles(HWND hwnd, int element_id,
                                    const unsigned char* left_bytes, int left_len,
                                    const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_titles(utf8_to_wide(left_bytes, left_len), utf8_to_wide(right_bytes, right_len));
    }
}

void __stdcall EU_SetTransferButtonTexts(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_button_texts(utf8_to_wide(left_bytes, left_len), utf8_to_wide(right_bytes, right_len));
    }
}

void __stdcall EU_SetTransferFormat(HWND hwnd, int element_id,
                                    const unsigned char* no_checked_bytes, int no_checked_len,
                                    const unsigned char* has_checked_bytes, int has_checked_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_format(utf8_to_wide(no_checked_bytes, no_checked_len),
                       utf8_to_wide(has_checked_bytes, has_checked_len));
    }
}

void __stdcall EU_SetTransferItemTemplate(HWND hwnd, int element_id,
                                          const unsigned char* template_bytes, int template_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_item_template(utf8_to_wide(template_bytes, template_len));
    }
}

void __stdcall EU_SetTransferFooterTexts(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_footer_texts(utf8_to_wide(left_bytes, left_len), utf8_to_wide(right_bytes, right_len));
    }
}

void __stdcall EU_SetTransferFilterPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_filter_placeholder(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_SetTransferCheckedKeys(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len) {
    if (auto* el = find_typed_element<Transfer>(hwnd, element_id)) {
        el->set_checked_keys(split_option_list(left_bytes, left_len),
                             split_option_list(right_bytes, right_len));
    }
}

int __stdcall EU_GetTransferCheckedCount(HWND hwnd, int element_id, int side) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return el ? el->checked_count(side) : 0;
}

int __stdcall EU_GetTransferValueKeys(HWND hwnd, int element_id,
                                      unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->value_keys_text(), buffer, buffer_size) : 0;
}

int __stdcall EU_GetTransferText(HWND hwnd, int element_id, int text_type,
                                 unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Transfer>(hwnd, element_id);
    return el ? copy_wide_as_utf8(el->text_value(text_type), buffer, buffer_size) : 0;
}

void __stdcall EU_SetAutocompleteSuggestions(HWND hwnd, int element_id,
                                             const unsigned char* suggestions_bytes, int suggestions_len) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_suggestions(parse_autocomplete_suggestions(suggestions_bytes, suggestions_len));
    }
}

void __stdcall EU_SetAutocompleteValue(HWND hwnd, int element_id,
                                       const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_SetAutocompleteOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetAutocompleteSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

void __stdcall EU_SetAutocompleteAsyncState(HWND hwnd, int element_id, int loading, int request_id) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_async_state(loading != 0, request_id);
    }
}

void __stdcall EU_SetAutocompleteEmptyText(HWND hwnd, int element_id,
                                           const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_empty_text(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_SetAutocompletePlaceholder(HWND hwnd, int element_id,
                                             const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_placeholder(utf8_to_wide(text_bytes, text_len));
    }
}

int __stdcall EU_GetAutocompletePlaceholder(HWND hwnd, int element_id,
                                            unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->placeholder, buffer, buffer_size);
}

void __stdcall EU_SetAutocompleteIcons(HWND hwnd, int element_id,
                                       const unsigned char* prefix_icon_bytes, int prefix_icon_len,
                                       const unsigned char* suffix_icon_bytes, int suffix_icon_len) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_icons(utf8_to_wide(prefix_icon_bytes, prefix_icon_len),
                      utf8_to_wide(suffix_icon_bytes, suffix_icon_len));
    }
}

int __stdcall EU_GetAutocompleteIcons(HWND hwnd, int element_id,
                                      unsigned char* prefix_icon_buffer, int prefix_icon_buffer_size,
                                      unsigned char* suffix_icon_buffer, int suffix_icon_buffer_size) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    if (!el) return 0;
    copy_wide_as_utf8(el->prefix_icon, prefix_icon_buffer, prefix_icon_buffer_size);
    copy_wide_as_utf8(el->suffix_icon, suffix_icon_buffer, suffix_icon_buffer_size);
    return 1;
}

void __stdcall EU_SetAutocompleteBehaviorOptions(HWND hwnd, int element_id, int trigger_on_focus) {
    if (auto* el = find_typed_element<Autocomplete>(hwnd, element_id)) {
        el->set_behavior(trigger_on_focus != 0);
    }
}

int __stdcall EU_GetAutocompleteBehaviorOptions(HWND hwnd, int element_id, int* trigger_on_focus) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    if (!el) return 0;
    if (trigger_on_focus) *trigger_on_focus = el->trigger_on_focus ? 1 : 0;
    return 1;
}

int __stdcall EU_GetAutocompleteValue(HWND hwnd, int element_id,
                                      unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->value);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int copy_len = (std::min)(needed, buffer_size - 1);
    if (copy_len > 0) memcpy(buffer, utf8.data(), copy_len);
    buffer[copy_len] = 0;
    return needed;
}

int __stdcall EU_GetAutocompleteOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetAutocompleteSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

int __stdcall EU_GetAutocompleteSuggestionCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    return el ? el->suggestion_count() : 0;
}

int __stdcall EU_GetAutocompleteOptions(HWND hwnd, int element_id,
                                        int* open, int* selected_index,
                                        int* suggestion_count, int* loading,
                                        int* request_id) {
    auto* el = find_typed_element<Autocomplete>(hwnd, element_id);
    if (!el) return 0;
    if (open) *open = el->is_open() ? 1 : 0;
    if (selected_index) *selected_index = el->selected_index;
    if (suggestion_count) *suggestion_count = el->suggestion_count();
    if (loading) *loading = el->async_loading ? 1 : 0;
    if (request_id) *request_id = el->async_request_id;
    return 1;
}

void __stdcall EU_SetMentionsValue(HWND hwnd, int element_id,
                                   const unsigned char* value_bytes, int value_len) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->set_value(utf8_to_wide(value_bytes, value_len));
    }
}

void __stdcall EU_SetMentionsSuggestions(HWND hwnd, int element_id,
                                         const unsigned char* suggestions_bytes, int suggestions_len) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->set_suggestions(split_option_list(suggestions_bytes, suggestions_len));
    }
}

void __stdcall EU_SetMentionsOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetMentionsSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

void __stdcall EU_SetMentionsOptions(HWND hwnd, int element_id,
                                     const unsigned char* trigger_bytes, int trigger_len,
                                     int filter_enabled, int insert_space) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        std::wstring trigger = utf8_to_wide(trigger_bytes, trigger_len);
        el->set_options(trigger.empty() ? L'@' : trigger[0], filter_enabled != 0, insert_space != 0);
    }
}

void __stdcall EU_SetMentionsFilter(HWND hwnd, int element_id,
                                    const unsigned char* filter_bytes, int filter_len) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->set_filter_text(utf8_to_wide(filter_bytes, filter_len));
    }
}

void __stdcall EU_InsertMentionsSelected(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Mentions>(hwnd, element_id)) {
        el->insert_selected();
    }
}

int __stdcall EU_GetMentionsValue(HWND hwnd, int element_id,
                                  unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Mentions>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->value);
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int copy_len = (std::min)(needed, buffer_size - 1);
    if (copy_len > 0) memcpy(buffer, utf8.data(), copy_len);
    buffer[copy_len] = 0;
    return needed;
}

int __stdcall EU_GetMentionsOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Mentions>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetMentionsSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Mentions>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

int __stdcall EU_GetMentionsSuggestionCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Mentions>(hwnd, element_id);
    return el ? el->suggestion_count() : 0;
}

int __stdcall EU_GetMentionsOptions(HWND hwnd, int element_id,
                                    int* open, int* selected_index,
                                    int* suggestion_count, int* matched_count,
                                    int* trigger_code) {
    auto* el = find_typed_element<Mentions>(hwnd, element_id);
    if (!el) return 0;
    if (open) *open = el->is_open() ? 1 : 0;
    if (selected_index) *selected_index = el->selected_index;
    if (suggestion_count) *suggestion_count = el->suggestion_count();
    if (matched_count) *matched_count = el->matched_count();
    if (trigger_code) *trigger_code = (int)el->trigger_char;
    return 1;
}

void __stdcall EU_SetCascaderOptions(HWND hwnd, int element_id,
                                     const unsigned char* options_bytes, int options_len) {
    if (auto* el = find_typed_element<Cascader>(hwnd, element_id)) {
        el->set_options(parse_cascader_options(options_bytes, options_len));
    }
}

void __stdcall EU_SetCascaderValue(HWND hwnd, int element_id,
                                   const unsigned char* selected_bytes, int selected_len) {
    if (auto* el = find_typed_element<Cascader>(hwnd, element_id)) {
        el->set_selected_path(split_wide_list(utf8_to_wide(selected_bytes, selected_len), L"/>\\\t,"));
    }
}

void __stdcall EU_SetCascaderOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Cascader>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetCascaderAdvancedOptions(HWND hwnd, int element_id,
                                             int searchable, int lazy_mode) {
    if (auto* el = find_typed_element<Cascader>(hwnd, element_id)) {
        el->set_advanced_options(searchable != 0, lazy_mode != 0);
    }
}

void __stdcall EU_SetCascaderSearch(HWND hwnd, int element_id,
                                    const unsigned char* search_bytes, int search_len) {
    if (auto* el = find_typed_element<Cascader>(hwnd, element_id)) {
        el->set_search_text(utf8_to_wide(search_bytes, search_len));
    }
}

int __stdcall EU_GetCascaderOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Cascader>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetCascaderOptionCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Cascader>(hwnd, element_id);
    return el ? el->option_count() : 0;
}

int __stdcall EU_GetCascaderSelectedDepth(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Cascader>(hwnd, element_id);
    return el ? el->selected_depth() : 0;
}

int __stdcall EU_GetCascaderLevelCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Cascader>(hwnd, element_id);
    return el ? el->active_level_count() : 0;
}

int __stdcall EU_GetCascaderAdvancedOptions(HWND hwnd, int element_id,
                                            int* searchable, int* lazy_mode,
                                            int* matched_count, int* last_lazy_level) {
    auto* el = find_typed_element<Cascader>(hwnd, element_id);
    if (!el) return 0;
    if (searchable) *searchable = el->searchable ? 1 : 0;
    if (lazy_mode) *lazy_mode = el->lazy_mode ? 1 : 0;
    if (matched_count) *matched_count = el->matched_count();
    if (last_lazy_level) *last_lazy_level = el->last_lazy_level;
    return 1;
}

void __stdcall EU_SetDatePickerDate(HWND hwnd, int element_id, int year, int month, int selected_day) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->set_date(year, month, selected_day);
    }
}

void __stdcall EU_SetDatePickerRange(HWND hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->set_range(min_yyyymmdd, max_yyyymmdd);
    }
}

void __stdcall EU_SetDatePickerOptions(HWND hwnd, int element_id,
                                       int today_yyyymmdd, int show_today, int date_format) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->set_options(today_yyyymmdd, show_today != 0, date_format);
    }
}

void __stdcall EU_SetDatePickerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_ClearDatePicker(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->clear_date();
    }
}

void __stdcall EU_DatePickerSelectToday(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->select_today();
    }
}

int __stdcall EU_GetDatePickerOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetDatePickerValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    return el ? el->value() : 0;
}

void __stdcall EU_DatePickerMoveMonth(HWND hwnd, int element_id, int delta_months) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->move_month(delta_months);
    }
}

int __stdcall EU_GetDatePickerRange(HWND hwnd, int element_id, int* min_yyyymmdd, int* max_yyyymmdd) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    if (!el) return 0;
    if (min_yyyymmdd) *min_yyyymmdd = el->min_value;
    if (max_yyyymmdd) *max_yyyymmdd = el->max_value;
    return 1;
}

int __stdcall EU_GetDatePickerOptions(HWND hwnd, int element_id,
                                      int* today_yyyymmdd, int* show_today, int* date_format) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    if (!el) return 0;
    if (today_yyyymmdd) *today_yyyymmdd = el->today_value;
    if (show_today) *show_today = el->show_today ? 1 : 0;
    if (date_format) *date_format = el->date_format;
    return 1;
}

void __stdcall EU_SetDatePickerSelectionRange(HWND hwnd, int element_id,
                                              int start_yyyymmdd, int end_yyyymmdd,
                                              int enabled) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->set_selection_range(start_yyyymmdd, end_yyyymmdd, enabled != 0);
    }
}

int __stdcall EU_GetDatePickerSelectionRange(HWND hwnd, int element_id,
                                             int* start_yyyymmdd, int* end_yyyymmdd,
                                             int* enabled) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    if (!el) return 0;
    int start_value = 0;
    int end_value = 0;
    bool range_enabled = false;
    el->get_selection_range(start_value, end_value, range_enabled);
    if (start_yyyymmdd) *start_yyyymmdd = start_value;
    if (end_yyyymmdd) *end_yyyymmdd = end_value;
    if (enabled) *enabled = range_enabled ? 1 : 0;
    return 1;
}
void __stdcall EU_SetDatePickerPlaceholder(HWND hwnd, int element_id,
                                            const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerRangeSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->range_separator = utf8_to_wide(sep_bytes, sep_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerStartPlaceholder(HWND hwnd, int element_id,
                                                 const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->start_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerEndPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->end_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerFormat(HWND hwnd, int element_id,
                                       const unsigned char* fmt_bytes, int fmt_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        el->date_format_str = utf8_to_wide(fmt_bytes, fmt_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerAlign(HWND hwnd, int element_id, int align) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        if (align < 0) align = 0; else if (align > 2) align = 2;
        el->text_align = align;
        el->invalidate();
    }
}
void __stdcall EU_SetDatePickerMode(HWND hwnd, int element_id, int mode) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) el->set_mode(mode);
}
int __stdcall EU_GetDatePickerMode(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) return el->mode();
    return 0;
}
void __stdcall EU_SetDatePickerMultiSelect(HWND hwnd, int element_id, int enabled) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) el->set_multi_select(enabled != 0);
}
int __stdcall EU_GetDatePickerSelectedDates(HWND hwnd, int element_id, unsigned char* buffer, int buf_size) {
    auto* el = find_typed_element<DatePicker>(hwnd, element_id);
    if (!el || el->selected_dates.empty()) return 0;
    std::wstring result;
    for (size_t i = 0; i < el->selected_dates.size(); ++i) {
        if (i > 0) result += L",";
        result += std::to_wstring(el->selected_dates[i]);
    }
    std::string utf8 = wide_to_utf8(result);
    int needed = (int)utf8.size();
    if (buffer && buf_size > needed) { memcpy(buffer, utf8.data(), needed + 1); }
    return needed;
}
void __stdcall EU_SetDatePickerShortcuts(HWND hwnd, int element_id,
                                          const unsigned char* sc_bytes, int sc_len) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) {
        std::wstring text = utf8_to_wide(sc_bytes, sc_len);
        std::vector<DatePicker::DateShortcut> items;
        size_t pos = 0;
        while (pos < text.size()) {
            size_t nl = text.find(L'\n', pos);
            if (nl == std::wstring::npos) nl = text.size();
            std::wstring line = text.substr(pos, nl - pos);
            size_t p1 = line.find(L'|');
            if (p1 != std::wstring::npos) {
                DatePicker::DateShortcut s;
                s.text = line.substr(0, p1);
                size_t p2 = line.find(L'|', p1 + 1);
                std::wstring val1 = (p1 + 1 < line.size()) ? line.substr(p1 + 1, p2 != std::wstring::npos ? p2 - p1 - 1 : std::wstring::npos) : L"";
                s.yyyymmdd = _wtoi(val1.c_str());
                s.yyyymmdd_end = (p2 != std::wstring::npos && p2 + 1 < line.size()) ? _wtoi(line.substr(p2 + 1).c_str()) : 0;
                items.push_back(s);
            }
            pos = nl + 1;
        }
        el->set_shortcuts(items);
    }
}
void __stdcall EU_SetDatePickerDisabledDateCallback(HWND hwnd, int element_id,
                                                     int (*cb)(int id, int yyyymmdd)) {
    if (auto* el = find_typed_element<DatePicker>(hwnd, element_id)) el->disabled_date_cb = cb;
}

int __stdcall EU_CreateDateRangePicker(HWND hwnd, int parent_id,
                                        int start_yyyymmdd, int end_yyyymmdd,
                                        int x, int y, int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    Element* parent = find_parent_or_root(st, parent_id);
    auto el = std::make_unique<DateRangePicker>();
    el->set_logical_bounds({ x, y, w, h });
    if (start_yyyymmdd > 0 || end_yyyymmdd > 0) el->set_value(start_yyyymmdd, end_yyyymmdd);
    ElementStyle ls = el->style;
    ls.bg_color = 0; ls.border_color = 0; ls.fg_color = 0;
    ls.corner_radius = 4.0f; ls.font_size = 14.0f;
    ls.pad_left = 10; ls.pad_top = 4; ls.pad_right = 10; ls.pad_bottom = 4;
    el->set_logical_style(ls);
    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}
void __stdcall EU_SetDateRangePickerValue(HWND hwnd, int element_id, int start, int end) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) el->set_value(start, end);
}
int __stdcall EU_GetDateRangePickerValue(HWND hwnd, int element_id, int* start, int* end) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) {
        if (start) *start = el->range_start; if (end) *end = el->range_end; return 1;
    } return 0;
}
void __stdcall EU_SetDateRangePickerRange(HWND hwnd, int element_id, int min, int max) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) el->set_range(min, max);
}
void __stdcall EU_SetDateRangePickerPlaceholders(HWND hwnd, int element_id,
                                                  const unsigned char* start_bytes, int start_len,
                                                  const unsigned char* end_bytes, int end_len) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) {
        el->start_placeholder = utf8_to_wide(start_bytes, start_len);
        el->end_placeholder = utf8_to_wide(end_bytes, end_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDateRangePickerSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) {
        el->range_separator = utf8_to_wide(sep_bytes, sep_len); el->invalidate();
    }
}
void __stdcall EU_SetDateRangePickerFormat(HWND hwnd, int element_id, int fmt) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) { el->date_format = fmt; el->invalidate(); }
}
void __stdcall EU_SetDateRangePickerAlign(HWND hwnd, int element_id, int align) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) { el->text_align = align; el->invalidate(); }
}
void __stdcall EU_SetDateRangePickerShortcuts(HWND hwnd, int element_id,
                                               const unsigned char* sc_bytes, int sc_len) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) {
        std::wstring text = utf8_to_wide(sc_bytes, sc_len);
        std::vector<DateRangePicker::Shortcut> items;
        size_t pos = 0;
        while (pos < text.size()) {
            size_t nl = text.find(L'\n', pos); if (nl == std::wstring::npos) nl = text.size();
            std::wstring line = text.substr(pos, nl - pos);
            size_t p1 = line.find(L'|');
            if (p1 != std::wstring::npos) {
                DateRangePicker::Shortcut s; s.text = line.substr(0, p1);
                size_t p2 = line.find(L'|', p1 + 1);
                s.yyyymmdd = _wtoi(line.substr(p1 + 1, p2 != std::wstring::npos ? p2 - p1 - 1 : std::wstring::npos).c_str());
                s.yyyymmdd_end = (p2 != std::wstring::npos) ? _wtoi(line.substr(p2 + 1).c_str()) : 0;
                items.push_back(s);
            } pos = nl + 1;
        }
        el->shortcuts = items; el->invalidate();
    }
}
void __stdcall EU_SetDateRangePickerDisabledDateCallback(HWND hwnd, int element_id,
                                                          int (*cb)(int id, int yyyymmdd)) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) el->disabled_date_cb = cb;
}
void __stdcall EU_SetDateRangePickerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) el->set_open(open != 0);
}
int __stdcall EU_GetDateRangePickerOpen(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) return el->open ? 1 : 0; return 0;
}
void __stdcall EU_DateRangePickerClear(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DateRangePicker>(hwnd, element_id)) el->clear_value();
}

void __stdcall EU_SetTimePickerTime(HWND hwnd, int element_id, int hour, int minute) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_time(hour, minute);
    }
}

void __stdcall EU_SetTimePickerRange(HWND hwnd, int element_id, int min_hhmm, int max_hhmm) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_range(min_hhmm, max_hhmm);
    }
}

void __stdcall EU_SetTimePickerOptions(HWND hwnd, int element_id, int step_minutes, int time_format) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_options(step_minutes, time_format);
    }
}

void __stdcall EU_SetTimePickerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetTimePickerScroll(HWND hwnd, int element_id, int hour_scroll, int minute_scroll) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_scroll(hour_scroll, minute_scroll);
    }
}

int __stdcall EU_GetTimePickerOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TimePicker>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetTimePickerValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TimePicker>(hwnd, element_id);
    return el ? el->value() : -1;
}

int __stdcall EU_GetTimePickerRange(HWND hwnd, int element_id, int* min_hhmm, int* max_hhmm) {
    auto* el = find_typed_element<TimePicker>(hwnd, element_id);
    if (!el) return 0;
    if (min_hhmm) *min_hhmm = el->min_time;
    if (max_hhmm) *max_hhmm = el->max_time;
    return 1;
}

int __stdcall EU_GetTimePickerOptions(HWND hwnd, int element_id, int* step_minutes, int* time_format) {
    auto* el = find_typed_element<TimePicker>(hwnd, element_id);
    if (!el) return 0;
    if (step_minutes) *step_minutes = el->step_minutes;
    if (time_format) *time_format = el->time_format;
    return 1;
}

int __stdcall EU_GetTimePickerScroll(HWND hwnd, int element_id, int* hour_scroll, int* minute_scroll) {
    auto* el = find_typed_element<TimePicker>(hwnd, element_id);
    if (!el) return 0;
    int h = 0;
    int m = 0;
    el->get_scroll(h, m);
    if (hour_scroll) *hour_scroll = h;
    if (minute_scroll) *minute_scroll = m;
    return 1;
}

void __stdcall EU_SetDateTimePickerDateTime(HWND hwnd, int element_id,
                                            int year, int month, int day,
                                            int hour, int minute) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_datetime(year, month, day, hour, minute);
    }
}

void __stdcall EU_SetDateTimePickerRange(HWND hwnd, int element_id,
                                         int min_yyyymmdd, int max_yyyymmdd,
                                         int min_hhmm, int max_hhmm) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_range(min_yyyymmdd, max_yyyymmdd, min_hhmm, max_hhmm);
    }
}

void __stdcall EU_SetDateTimePickerOptions(HWND hwnd, int element_id,
                                           int today_yyyymmdd, int show_today,
                                           int minute_step, int date_format) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_options(today_yyyymmdd, show_today != 0, minute_step, date_format);
    }
}

void __stdcall EU_SetDateTimePickerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_ClearDateTimePicker(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->clear_datetime();
    }
}

void __stdcall EU_DateTimePickerSelectToday(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->select_today();
    }
}

void __stdcall EU_DateTimePickerSelectNow(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->select_now();
    }
}

void __stdcall EU_SetDateTimePickerScroll(HWND hwnd, int element_id, int hour_scroll, int minute_scroll) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_scroll(hour_scroll, minute_scroll);
    }
}

int __stdcall EU_GetDateTimePickerOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetDateTimePickerDateValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    return el ? el->date_value() : 0;
}

int __stdcall EU_GetDateTimePickerTimeValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    return el ? el->time_value() : -1;
}

void __stdcall EU_DateTimePickerMoveMonth(HWND hwnd, int element_id, int delta_months) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->move_month(delta_months);
    }
}

int __stdcall EU_GetDateTimePickerRange(HWND hwnd, int element_id,
                                        int* min_yyyymmdd, int* max_yyyymmdd,
                                        int* min_hhmm, int* max_hhmm) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    if (!el) return 0;
    if (min_yyyymmdd) *min_yyyymmdd = el->min_date;
    if (max_yyyymmdd) *max_yyyymmdd = el->max_date;
    if (min_hhmm) *min_hhmm = el->min_time;
    if (max_hhmm) *max_hhmm = el->max_time;
    return 1;
}

int __stdcall EU_GetDateTimePickerOptions(HWND hwnd, int element_id,
                                          int* today_yyyymmdd, int* show_today,
                                          int* minute_step, int* date_format) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    if (!el) return 0;
    if (today_yyyymmdd) *today_yyyymmdd = el->today_value;
    if (show_today) *show_today = el->show_today ? 1 : 0;
    if (minute_step) *minute_step = el->minute_step;
    if (date_format) *date_format = el->date_format;
    return 1;
}

int __stdcall EU_GetDateTimePickerScroll(HWND hwnd, int element_id,
                                         int* hour_scroll, int* minute_scroll) {
    auto* el = find_typed_element<DateTimePicker>(hwnd, element_id);
    if (!el) return 0;
    int h = 0;
    int m = 0;
    el->get_scroll(h, m);
    if (hour_scroll) *hour_scroll = h;
    if (minute_scroll) *minute_scroll = m;
    return 1;
}

void __stdcall EU_SetDateTimePickerShortcuts(HWND hwnd, int element_id,
                                              const unsigned char* sc_bytes, int sc_len) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        std::wstring text = utf8_to_wide(sc_bytes, sc_len);
        std::vector<DateTimePicker::DateShortcut> items;
        size_t pos = 0;
        while (pos < text.size()) {
            size_t nl = text.find(L'\n', pos);
            if (nl == std::wstring::npos) nl = text.size();
            std::wstring line = text.substr(pos, nl - pos);
            size_t p1 = line.find(L'|');
            if (p1 != std::wstring::npos) {
                DateTimePicker::DateShortcut s;
                s.text = line.substr(0, p1);
                size_t p2 = line.find(L'|', p1 + 1);
                std::wstring val1 = (p1 + 1 < line.size()) ? line.substr(p1 + 1, p2 != std::wstring::npos ? p2 - p1 - 1 : std::wstring::npos) : L"";
                s.yyyymmdd = _wtoi(val1.c_str());
                s.yyyymmdd_end = (p2 != std::wstring::npos && p2 + 1 < line.size()) ? _wtoi(line.substr(p2 + 1).c_str()) : 0;
                items.push_back(s);
            }
            pos = nl + 1;
        }
        el->set_shortcuts(items);
    }
}
void __stdcall EU_SetDateTimePickerStartPlaceholder(HWND hwnd, int element_id,
                                                     const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->start_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDateTimePickerEndPlaceholder(HWND hwnd, int element_id,
                                                   const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->end_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDateTimePickerDefaultTime(HWND hwnd, int element_id, int hour, int minute) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_default_time(hour, minute);
    }
}
void __stdcall EU_SetDateTimePickerRangeDefaultTime(HWND hwnd, int element_id,
                                                     int start_hour, int start_minute,
                                                     int end_hour, int end_minute) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_range_default_time(start_hour, start_minute, end_hour, end_minute);
    }
}
void __stdcall EU_SetDateTimePickerRangeSeparator(HWND hwnd, int element_id,
                                                   const unsigned char* sep_bytes, int sep_len) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->range_separator = utf8_to_wide(sep_bytes, sep_len);
        el->invalidate();
    }
}
void __stdcall EU_SetDateTimePickerRangeSelect(HWND hwnd, int element_id, int enabled,
                                                int start_date, int start_time,
                                                int end_date, int end_time) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        el->set_selection_range(start_date, start_time, end_date, end_time, enabled != 0);
    }
}
int __stdcall EU_GetDateTimePickerRangeValue(HWND hwnd, int element_id,
                                              int* start_date, int* start_time,
                                              int* end_date, int* end_time, int* enabled) {
    if (auto* el = find_typed_element<DateTimePicker>(hwnd, element_id)) {
        int sd = 0, st = 0, ed = 0, et = 0;
        bool en = false;
        el->get_selection_range(sd, st, ed, et, en);
        if (start_date) *start_date = sd;
        if (start_time) *start_time = st;
        if (end_date) *end_date = ed;
        if (end_time) *end_time = et;
        if (enabled) *enabled = en ? 1 : 0;
        return 1;
    }
    return 0;
}

void __stdcall EU_SetTimePickerArrowControl(HWND hwnd, int element_id, int enabled) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->arrow_control = enabled != 0;
        el->invalidate();
    }
}
int __stdcall EU_GetTimePickerArrowControl(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) return el->arrow_control ? 1 : 0;
    return 0;
}
void __stdcall EU_SetTimePickerRangeSelect(HWND hwnd, int element_id, int enabled,
                                            int start_hhmm, int end_hhmm) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->set_selection_range(start_hhmm, end_hhmm, enabled != 0);
    }
}
int __stdcall EU_GetTimePickerRangeValue(HWND hwnd, int element_id,
                                          int* start_hhmm, int* end_hhmm, int* enabled) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        if (start_hhmm) *start_hhmm = el->range_start_has_value ? el->range_start : 0;
        if (end_hhmm) *end_hhmm = el->range_end_has_value ? el->range_end : 0;
        if (enabled) *enabled = el->range_select ? 1 : 0;
        return 1;
    }
    return 0;
}
void __stdcall EU_SetTimePickerStartPlaceholder(HWND hwnd, int element_id,
                                                 const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->start_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetTimePickerEndPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->end_placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}
void __stdcall EU_SetTimePickerRangeSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len) {
    if (auto* el = find_typed_element<TimePicker>(hwnd, element_id)) {
        el->range_separator = utf8_to_wide(sep_bytes, sep_len);
        el->invalidate();
    }
}
void __stdcall EU_SetTimeSelectPlaceholder(HWND hwnd, int element_id,
                                            const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->placeholder = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}

void __stdcall EU_SetTimeSelectTime(HWND hwnd, int element_id, int hour, int minute) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->set_time(hour, minute);
    }
}

void __stdcall EU_SetTimeSelectRange(HWND hwnd, int element_id, int min_hhmm, int max_hhmm) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->set_range(min_hhmm, max_hhmm);
    }
}

void __stdcall EU_SetTimeSelectOptions(HWND hwnd, int element_id, int step_minutes, int time_format) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->set_options(step_minutes, time_format);
    }
}

void __stdcall EU_SetTimeSelectOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetTimeSelectScroll(HWND hwnd, int element_id, int scroll_row) {
    if (auto* el = find_typed_element<TimeSelect>(hwnd, element_id)) {
        el->set_scroll(scroll_row);
    }
}

int __stdcall EU_GetTimeSelectOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TimeSelect>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetTimeSelectValue(HWND hwnd, int element_id) {
    auto* el = find_typed_element<TimeSelect>(hwnd, element_id);
    return el ? el->value() : -1;
}

int __stdcall EU_GetTimeSelectRange(HWND hwnd, int element_id, int* min_hhmm, int* max_hhmm) {
    auto* el = find_typed_element<TimeSelect>(hwnd, element_id);
    if (!el) return 0;
    if (min_hhmm) *min_hhmm = el->min_time;
    if (max_hhmm) *max_hhmm = el->max_time;
    return 1;
}

int __stdcall EU_GetTimeSelectOptions(HWND hwnd, int element_id, int* step_minutes, int* time_format) {
    auto* el = find_typed_element<TimeSelect>(hwnd, element_id);
    if (!el) return 0;
    if (step_minutes) *step_minutes = el->step_minutes;
    if (time_format) *time_format = el->time_format;
    return 1;
}

int __stdcall EU_GetTimeSelectState(HWND hwnd, int element_id,
                                    int* scroll_row, int* candidate_count,
                                    int* group_count, int* active_index) {
    auto* el = find_typed_element<TimeSelect>(hwnd, element_id);
    if (!el) return 0;
    if (scroll_row) *scroll_row = el->scroll();
    if (candidate_count) *candidate_count = el->candidate_count();
    if (group_count) *group_count = el->group_count();
    if (active_index) *active_index = el->active_index();
    return 1;
}

void __stdcall EU_SetDropdownItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetDropdownSelected(HWND hwnd, int element_id, int selected_index) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->set_selected_index(selected_index);
    }
}

int __stdcall EU_GetDropdownSelected(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    return el ? el->selected_index : -1;
}

void __stdcall EU_SetDropdownOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

int __stdcall EU_GetDropdownOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    return (el && el->is_open()) ? 1 : 0;
}

int __stdcall EU_GetDropdownItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    return el ? el->item_count() : 0;
}

void __stdcall EU_SetDropdownDisabled(HWND hwnd, int element_id, const int* indices, int count) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        std::vector<int> disabled;
        if (indices && count > 0) {
            disabled.assign(indices, indices + count);
        }
        el->set_disabled_indices(disabled);
    }
}

int __stdcall EU_GetDropdownState(HWND hwnd, int element_id,
                                  int* selected_index, int* item_count,
                                  int* disabled_count, int* selected_level,
                                  int* hover_index) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    if (!el) return 0;
    if (selected_index) *selected_index = el->selected_index;
    if (item_count) *item_count = el->item_count();
    if (disabled_count) *disabled_count = el->disabled_count();
    if (selected_level) *selected_level = el->selected_level();
    if (hover_index) *hover_index = el->hover_index();
    return 1;
}

void __stdcall EU_SetDropdownOptions(HWND hwnd, int element_id,
                                     int trigger_mode, int hide_on_click,
                                     int split_button, int button_variant,
                                     int size, int trigger_style) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->set_options(trigger_mode, hide_on_click, split_button,
                        button_variant, size, trigger_style);
    }
}

int __stdcall EU_GetDropdownOptions(HWND hwnd, int element_id,
                                    int* trigger_mode, int* hide_on_click,
                                    int* split_button, int* button_variant,
                                    int* size, int* trigger_style) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    if (!el) return 0;
    if (trigger_mode) *trigger_mode = el->trigger_mode;
    if (hide_on_click) *hide_on_click = el->hide_on_click ? 1 : 0;
    if (split_button) *split_button = el->split_button ? 1 : 0;
    if (button_variant) *button_variant = el->button_variant;
    if (size) *size = el->size;
    if (trigger_style) *trigger_style = el->trigger_style;
    return 1;
}

void __stdcall EU_SetDropdownItemMeta(HWND hwnd, int element_id,
                                      const unsigned char* icons_bytes, int icons_len,
                                      const unsigned char* commands_bytes, int commands_len,
                                      const int* divided_indices, int divided_count) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        std::vector<int> divided;
        if (divided_indices && divided_count > 0) {
            divided.assign(divided_indices, divided_indices + divided_count);
        }
        el->set_item_meta(split_option_list_keep_empty(icons_bytes, icons_len),
                          split_option_list_keep_empty(commands_bytes, commands_len),
                          divided);
    }
}

int __stdcall EU_GetDropdownItemMeta(HWND hwnd, int element_id, int item_index,
                                     unsigned char* icon_buffer, int icon_buffer_size,
                                     unsigned char* command_buffer, int command_buffer_size,
                                     int* divided, int* disabled, int* level) {
    auto* el = find_typed_element<Dropdown>(hwnd, element_id);
    if (!el || item_index < 0 || item_index >= el->item_count()) return 0;
    copy_wide_as_utf8(el->item_icon(item_index), icon_buffer, icon_buffer_size);
    copy_wide_as_utf8(el->item_command(item_index), command_buffer, command_buffer_size);
    if (divided) *divided = el->is_divided(item_index) ? 1 : 0;
    if (disabled) *disabled = (item_index < (int)el->disabled_items.size() && el->disabled_items[item_index]) ? 1 : 0;
    if (level) *level = (item_index < (int)el->item_levels.size()) ? el->item_levels[item_index] : 0;
    return 1;
}

void __stdcall EU_SetDropdownCommandCallback(HWND hwnd, int element_id, DropdownCommandCallback cb) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->command_cb = cb;
    }
}

void __stdcall EU_SetDropdownMainClickCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    if (auto* el = find_typed_element<Dropdown>(hwnd, element_id)) {
        el->main_click_cb = cb;
    }
}

void __stdcall EU_SetMenuItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetMenuActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

int __stdcall EU_GetMenuActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    return el ? el->active_index : -1;
}

void __stdcall EU_SetMenuOrientation(HWND hwnd, int element_id, int orientation) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->set_orientation(orientation);
    }
}

int __stdcall EU_GetMenuOrientation(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    return el ? el->orientation : 0;
}

int __stdcall EU_GetMenuItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    return el ? el->item_count() : 0;
}

void __stdcall EU_SetMenuExpanded(HWND hwnd, int element_id, const int* indices, int count) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        std::vector<int> expanded;
        if (indices && count > 0) {
            expanded.assign(indices, indices + count);
        }
        el->set_expanded_indices(expanded);
    }
}

int __stdcall EU_GetMenuState(HWND hwnd, int element_id,
                              int* active_index, int* item_count,
                              int* orientation, int* active_level,
                              int* visible_count, int* expanded_count,
                              int* hover_index) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = el->item_count();
    if (orientation) *orientation = el->orientation;
    if (active_level) *active_level = el->active_level();
    if (visible_count) *visible_count = el->visible_count();
    if (expanded_count) *expanded_count = el->expanded_count();
    if (hover_index) *hover_index = el->hover_index();
    return 1;
}

int __stdcall EU_GetMenuActivePath(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    if (!el) return 0;
    std::string utf8 = wide_to_utf8(el->active_path());
    int needed = (int)utf8.size();
    if (!buffer || buffer_size <= 0) return needed;
    int n = (std::min)(needed, buffer_size - 1);
    if (n > 0) memcpy(buffer, utf8.data(), n);
    buffer[n] = 0;
    return needed;
}

void __stdcall EU_SetMenuColors(HWND hwnd, int element_id,
                                Color bg, Color text_color, Color active_text_color,
                                Color hover_bg, Color disabled_text_color, Color border) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->set_colors(bg, text_color, active_text_color, hover_bg, disabled_text_color, border);
    }
}

int __stdcall EU_GetMenuColors(HWND hwnd, int element_id,
                               Color* bg, Color* text_color, Color* active_text_color,
                               Color* hover_bg, Color* disabled_text_color, Color* border) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    if (!el) return 0;
    if (bg) *bg = el->menu_bg_color;
    if (text_color) *text_color = el->menu_text_color;
    if (active_text_color) *active_text_color = el->menu_active_text_color;
    if (hover_bg) *hover_bg = el->menu_hover_bg_color;
    if (disabled_text_color) *disabled_text_color = el->menu_disabled_text_color;
    if (border) *border = el->menu_border_color;
    return 1;
}

void __stdcall EU_SetMenuCollapsed(HWND hwnd, int element_id, int collapsed) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->set_collapsed(collapsed != 0);
    }
}

int __stdcall EU_GetMenuCollapsed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    return (el && el->collapsed) ? 1 : 0;
}

void __stdcall EU_SetMenuItemMeta(HWND hwnd, int element_id,
                                  const unsigned char* icons_bytes, int icons_len,
                                  const int* group_indices, int group_count,
                                  const unsigned char* hrefs_bytes, int hrefs_len,
                                  const unsigned char* targets_bytes, int targets_len,
                                  const unsigned char* commands_bytes, int commands_len) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        std::vector<int> groups;
        if (group_indices && group_count > 0) {
            groups.assign(group_indices, group_indices + group_count);
        }
        el->set_item_meta(split_option_list_keep_empty(icons_bytes, icons_len),
                          groups,
                          split_option_list_keep_empty(hrefs_bytes, hrefs_len),
                          split_option_list_keep_empty(targets_bytes, targets_len),
                          split_option_list_keep_empty(commands_bytes, commands_len));
    }
}

int __stdcall EU_GetMenuItemMeta(HWND hwnd, int element_id, int item_index,
                                 unsigned char* icon_buffer, int icon_buffer_size,
                                 unsigned char* href_buffer, int href_buffer_size,
                                 unsigned char* target_buffer, int target_buffer_size,
                                 unsigned char* command_buffer, int command_buffer_size,
                                 int* is_group, int* disabled, int* level) {
    auto* el = find_typed_element<Menu>(hwnd, element_id);
    if (!el || item_index < 0 || item_index >= el->item_count()) return 0;
    copy_wide_as_utf8(el->item_icon(item_index), icon_buffer, icon_buffer_size);
    copy_wide_as_utf8(el->item_href(item_index), href_buffer, href_buffer_size);
    copy_wide_as_utf8(el->item_target(item_index), target_buffer, target_buffer_size);
    copy_wide_as_utf8(el->item_command(item_index), command_buffer, command_buffer_size);
    if (is_group) *is_group = el->is_group(item_index) ? 1 : 0;
    if (disabled) *disabled = (item_index < (int)el->disabled_items.size() &&
                               (el->disabled_items[item_index] || el->is_group(item_index))) ? 1 : 0;
    if (level) *level = (item_index < (int)el->item_levels.size()) ? el->item_levels[item_index] : 0;
    return 1;
}

void __stdcall EU_SetMenuSelectCallback(HWND hwnd, int element_id, MenuSelectCallback cb) {
    if (auto* el = find_typed_element<Menu>(hwnd, element_id)) {
        el->select_cb = cb;
    }
}

void __stdcall EU_SetAnchorItems(HWND hwnd, int element_id,
                                 const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Anchor>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetAnchorActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Anchor>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

int __stdcall EU_GetAnchorActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Anchor>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetAnchorItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Anchor>(hwnd, element_id);
    return el ? el->item_count() : 0;
}

void __stdcall EU_SetAnchorTargets(HWND hwnd, int element_id, const int* positions, int count) {
    if (auto* el = find_typed_element<Anchor>(hwnd, element_id)) {
        std::vector<int> targets;
        if (positions && count > 0) {
            targets.assign(positions, positions + count);
        }
        el->set_targets(targets);
    }
}

void __stdcall EU_SetAnchorOptions(HWND hwnd, int element_id, int scroll_offset, int target_container_id) {
    if (auto* el = find_typed_element<Anchor>(hwnd, element_id)) {
        el->set_options(scroll_offset, target_container_id);
    }
}

void __stdcall EU_SetAnchorScroll(HWND hwnd, int element_id, int scroll_position) {
    if (auto* el = find_typed_element<Anchor>(hwnd, element_id)) {
        el->set_scroll_position(scroll_position);
    }
}

int __stdcall EU_GetAnchorState(HWND hwnd, int element_id,
                                int* active_index, int* item_count,
                                int* scroll_position, int* offset,
                                int* target_position, int* container_id,
                                int* hover_index) {
    auto* el = find_typed_element<Anchor>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = el->item_count();
    if (scroll_position) *scroll_position = el->scroll_position;
    if (offset) *offset = el->offset;
    if (target_position) *target_position = el->last_target_position;
    if (container_id) *container_id = el->container_id;
    if (hover_index) *hover_index = el->hover_index();
    return 1;
}

void __stdcall EU_SetBacktopState(HWND hwnd, int element_id,
                                  int scroll_position, int threshold, int target_position) {
    if (auto* el = find_typed_element<Backtop>(hwnd, element_id)) {
        el->set_state(scroll_position, threshold, target_position);
    }
}

int __stdcall EU_GetBacktopVisible(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Backtop>(hwnd, element_id);
    return el ? el->is_shown() : 0;
}

int __stdcall EU_GetBacktopState(HWND hwnd, int element_id,
                                 int* scroll_position, int* threshold, int* target_position) {
    auto* el = find_typed_element<Backtop>(hwnd, element_id);
    if (!el) return 0;
    if (scroll_position) *scroll_position = el->scroll_position;
    if (threshold) *threshold = el->threshold;
    if (target_position) *target_position = el->target_position;
    return 1;
}

void __stdcall EU_SetBacktopOptions(HWND hwnd, int element_id,
                                    int scroll_position, int threshold,
                                    int target_position, int container_id,
                                    int duration_ms) {
    if (auto* el = find_typed_element<Backtop>(hwnd, element_id)) {
        el->set_options(scroll_position, threshold, target_position, container_id, duration_ms);
    }
}

void __stdcall EU_SetBacktopScroll(HWND hwnd, int element_id, int scroll_position) {
    if (auto* el = find_typed_element<Backtop>(hwnd, element_id)) {
        el->set_scroll_position(scroll_position);
    }
}

void __stdcall EU_TriggerBacktop(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Backtop>(hwnd, element_id)) {
        el->trigger_backtop();
    }
}

int __stdcall EU_GetBacktopFullState(HWND hwnd, int element_id,
                                     int* scroll_position, int* threshold,
                                     int* target_position, int* container_id,
                                     int* visible, int* duration_ms,
                                     int* last_scroll_before_jump,
                                     int* activated_count) {
    auto* el = find_typed_element<Backtop>(hwnd, element_id);
    if (!el) return 0;
    if (scroll_position) *scroll_position = el->scroll_position;
    if (threshold) *threshold = el->threshold;
    if (target_position) *target_position = el->target_position;
    if (container_id) *container_id = el->container_id;
    if (visible) *visible = el->is_shown();
    if (duration_ms) *duration_ms = el->duration_ms;
    if (last_scroll_before_jump) *last_scroll_before_jump = el->last_scroll_before_jump;
    if (activated_count) *activated_count = el->activated_count;
    return 1;
}

void __stdcall EU_SetSegmentedItems(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Segmented>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetSegmentedActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Segmented>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

int __stdcall EU_GetSegmentedActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Segmented>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetSegmentedItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Segmented>(hwnd, element_id);
    return el ? el->item_count() : 0;
}

void __stdcall EU_SetSegmentedDisabled(HWND hwnd, int element_id, const int* indices, int count) {
    if (auto* el = find_typed_element<Segmented>(hwnd, element_id)) {
        std::vector<int> disabled;
        if (indices && count > 0) {
            disabled.assign(indices, indices + count);
        }
        el->set_disabled_indices(disabled);
    }
}

int __stdcall EU_GetSegmentedState(HWND hwnd, int element_id,
                                   int* active_index, int* item_count,
                                   int* disabled_count, int* hover_index) {
    auto* el = find_typed_element<Segmented>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = el->item_count();
    if (disabled_count) *disabled_count = el->disabled_count();
    if (hover_index) *hover_index = el->hover_index();
    return 1;
}

void __stdcall EU_SetPageHeaderText(HWND hwnd, int element_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* subtitle_bytes, int subtitle_len) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
        el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
    }
}

void __stdcall EU_SetPageHeaderBreadcrumbs(HWND hwnd, int element_id,
                                           const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_breadcrumbs(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetPageHeaderActions(HWND hwnd, int element_id,
                                       const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_actions(split_option_list(items_bytes, items_len));
    }
}

int __stdcall EU_GetPageHeaderAction(HWND hwnd, int element_id) {
    auto* el = find_typed_element<PageHeader>(hwnd, element_id);
    return el ? el->get_active_action() : -1;
}

void __stdcall EU_SetPageHeaderBackText(HWND hwnd, int element_id,
                                        const unsigned char* back_bytes, int back_len) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_back_text(utf8_to_wide(back_bytes, back_len));
    }
}

void __stdcall EU_SetPageHeaderActiveAction(HWND hwnd, int element_id, int action_index) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_active_action(action_index);
    }
}

void __stdcall EU_SetPageHeaderBreadcrumbActive(HWND hwnd, int element_id, int breadcrumb_index) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->set_active_breadcrumb(breadcrumb_index);
    }
}

void __stdcall EU_TriggerPageHeaderBack(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->trigger_back();
    }
}

void __stdcall EU_ResetPageHeaderResult(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<PageHeader>(hwnd, element_id)) {
        el->reset_result();
    }
}

int __stdcall EU_GetPageHeaderState(HWND hwnd, int element_id,
                                    int* active_action, int* action_count,
                                    int* active_breadcrumb, int* breadcrumb_count,
                                    int* back_clicked_count,
                                    int* back_hovered, int* action_hover,
                                    int* breadcrumb_hover) {
    auto* el = find_typed_element<PageHeader>(hwnd, element_id);
    if (!el) return 0;
    if (active_action) *active_action = el->active_action;
    if (action_count) *action_count = el->action_count();
    if (active_breadcrumb) *active_breadcrumb = el->active_breadcrumb;
    if (breadcrumb_count) *breadcrumb_count = el->breadcrumb_count();
    if (back_clicked_count) *back_clicked_count = el->back_clicked_count;
    if (back_hovered) *back_hovered = el->back_hovered();
    if (action_hover) *action_hover = el->hovered_action();
    if (breadcrumb_hover) *breadcrumb_hover = el->hovered_breadcrumb();
    return 1;
}

void __stdcall EU_SetAffixText(HWND hwnd, int element_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<Affix>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
        el->set_body(utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetAffixState(HWND hwnd, int element_id, int scroll_position, int offset) {
    if (auto* el = find_typed_element<Affix>(hwnd, element_id)) {
        el->set_state(scroll_position, offset);
    }
}

int __stdcall EU_GetAffixFixed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Affix>(hwnd, element_id);
    return el ? el->is_fixed() : 0;
}

int __stdcall EU_GetAffixState(HWND hwnd, int element_id,
                               int* scroll_position, int* offset, int* fixed) {
    auto* el = find_typed_element<Affix>(hwnd, element_id);
    if (!el) return 0;
    if (scroll_position) *scroll_position = el->scroll_position;
    if (offset) *offset = el->offset;
    if (fixed) *fixed = el->is_fixed();
    return 1;
}

void __stdcall EU_SetAffixOptions(HWND hwnd, int element_id,
                                  int scroll_position, int offset, int container_id,
                                  int placeholder_height, int z_index) {
    if (auto* el = find_typed_element<Affix>(hwnd, element_id)) {
        el->set_options(scroll_position, offset, container_id, placeholder_height, z_index);
    }
}

int __stdcall EU_GetAffixOptions(HWND hwnd, int element_id,
                                 int* scroll_position, int* offset, int* fixed,
                                 int* container_id, int* placeholder_height,
                                 int* fixed_top, int* z_index) {
    auto* el = find_typed_element<Affix>(hwnd, element_id);
    if (!el) return 0;
    if (scroll_position) *scroll_position = el->scroll_position;
    if (offset) *offset = el->offset;
    if (fixed) *fixed = el->is_fixed();
    if (container_id) *container_id = el->container_id;
    if (placeholder_height) *placeholder_height = el->placeholder_height;
    if (fixed_top) *fixed_top = el->fixed_top;
    if (z_index) *z_index = el->fixed_z_index;
    return 1;
}

void __stdcall EU_SetWatermarkContent(HWND hwnd, int element_id,
                                      const unsigned char* content_bytes, int content_len) {
    if (auto* el = find_typed_element<Watermark>(hwnd, element_id)) {
        el->set_content(utf8_to_wide(content_bytes, content_len));
    }
}

void __stdcall EU_SetWatermarkOptions(HWND hwnd, int element_id,
                                      int gap_x, int gap_y, int rotation_degrees, int alpha) {
    if (auto* el = find_typed_element<Watermark>(hwnd, element_id)) {
        el->set_options(gap_x, gap_y, rotation_degrees, alpha);
    }
}

int __stdcall EU_GetWatermarkOptions(HWND hwnd, int element_id,
                                     int* gap_x, int* gap_y, int* rotation_degrees, int* alpha) {
    auto* el = find_typed_element<Watermark>(hwnd, element_id);
    if (!el) return 0;
    if (gap_x) *gap_x = el->gap_x;
    if (gap_y) *gap_y = el->gap_y;
    if (rotation_degrees) *rotation_degrees = (int)std::lround(el->rotation);
    if (alpha) *alpha = (int)el->alpha;
    return 1;
}

void __stdcall EU_SetWatermarkLayer(HWND hwnd, int element_id,
                                    int container_id, int overlay, int pass_through, int z_index) {
    if (auto* el = find_typed_element<Watermark>(hwnd, element_id)) {
        el->set_layer_options(container_id, overlay, pass_through, z_index);
    }
}

int __stdcall EU_GetWatermarkFullOptions(HWND hwnd, int element_id,
                                         int* gap_x, int* gap_y, int* rotation_degrees, int* alpha,
                                         int* container_id, int* overlay, int* pass_through,
                                         int* z_index, int* tile_count_x, int* tile_count_y) {
    auto* el = find_typed_element<Watermark>(hwnd, element_id);
    if (!el) return 0;
    if (gap_x) *gap_x = el->gap_x;
    if (gap_y) *gap_y = el->gap_y;
    if (rotation_degrees) *rotation_degrees = (int)std::lround(el->rotation);
    if (alpha) *alpha = (int)el->alpha;
    if (container_id) *container_id = el->container_id;
    if (overlay) *overlay = el->overlay ? 1 : 0;
    if (pass_through) *pass_through = el->pass_through ? 1 : 0;
    if (z_index) *z_index = el->z_index;
    if (tile_count_x) *tile_count_x = el->tile_count_x;
    if (tile_count_y) *tile_count_y = el->tile_count_y;
    return 1;
}

void __stdcall EU_SetTourSteps(HWND hwnd, int element_id,
                               const unsigned char* steps_bytes, int steps_len) {
    if (auto* el = find_typed_element<Tour>(hwnd, element_id)) {
        el->set_steps(parse_tour_steps(steps_bytes, steps_len));
    }
}

void __stdcall EU_SetTourActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Tour>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

void __stdcall EU_SetTourOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Tour>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetTourOptions(HWND hwnd, int element_id,
                                 int open, int mask,
                                 int target_x, int target_y, int target_w, int target_h) {
    if (auto* el = find_typed_element<Tour>(hwnd, element_id)) {
        el->set_options(open != 0, mask != 0, target_x, target_y, target_w, target_h);
    }
}

void __stdcall EU_SetTourTargetElement(HWND hwnd, int element_id, int target_element_id, int padding) {
    auto* tour = find_typed_element<Tour>(hwnd, element_id);
    WindowState* st = window_state(hwnd);
    if (!tour || !st || !st->element_tree) return;
    Element* target = st->element_tree->find_by_id(target_element_id);
    if (!target) {
        tour->set_target_element(0, { 0, 0, 0, 0 });
        return;
    }
    int pad = padding < 0 ? 0 : padding;
    int ax = 0;
    int ay = 0;
    target->get_absolute_pos(ax, ay);
    tour->set_target_element(target_element_id,
        { ax - pad, ay - pad, target->bounds.w + pad * 2, target->bounds.h + pad * 2 });
}

void __stdcall EU_SetTourMaskBehavior(HWND hwnd, int element_id, int pass_through, int close_on_mask) {
    if (auto* el = find_typed_element<Tour>(hwnd, element_id)) {
        el->set_mask_behavior(pass_through != 0, close_on_mask != 0);
    }
}

int __stdcall EU_GetTourActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tour>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetTourOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tour>(hwnd, element_id);
    return el ? (el->open ? 1 : 0) : 0;
}

int __stdcall EU_GetTourStepCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tour>(hwnd, element_id);
    return el ? (int)el->steps.size() : 0;
}

int __stdcall EU_GetTourOptions(HWND hwnd, int element_id,
                                int* open, int* mask,
                                int* target_x, int* target_y, int* target_w, int* target_h) {
    auto* el = find_typed_element<Tour>(hwnd, element_id);
    if (!el) return 0;
    if (open) *open = el->open ? 1 : 0;
    if (mask) *mask = el->mask ? 1 : 0;
    if (target_x) *target_x = el->has_target ? el->target_rect.x : 0;
    if (target_y) *target_y = el->has_target ? el->target_rect.y : 0;
    if (target_w) *target_w = el->has_target ? el->target_rect.w : 0;
    if (target_h) *target_h = el->has_target ? el->target_rect.h : 0;
    return 1;
}

int __stdcall EU_GetTourFullState(HWND hwnd, int element_id,
                                  int* active_index, int* step_count,
                                  int* open, int* mask,
                                  int* target_x, int* target_y, int* target_w, int* target_h,
                                  int* target_element_id, int* mask_passthrough,
                                  int* close_on_mask, int* last_action, int* change_count) {
    auto* el = find_typed_element<Tour>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (step_count) *step_count = (int)el->steps.size();
    if (open) *open = el->open ? 1 : 0;
    if (mask) *mask = el->mask ? 1 : 0;
    if (target_x) *target_x = el->has_target ? el->target_rect.x : 0;
    if (target_y) *target_y = el->has_target ? el->target_rect.y : 0;
    if (target_w) *target_w = el->has_target ? el->target_rect.w : 0;
    if (target_h) *target_h = el->has_target ? el->target_rect.h : 0;
    if (target_element_id) *target_element_id = el->target_element_id;
    if (mask_passthrough) *mask_passthrough = el->mask_passthrough ? 1 : 0;
    if (close_on_mask) *close_on_mask = el->close_on_mask ? 1 : 0;
    if (last_action) *last_action = el->last_action;
    if (change_count) *change_count = el->change_count;
    return 1;
}

void __stdcall EU_SetImageSource(HWND hwnd, int element_id,
                                 const unsigned char* src_bytes, int src_len,
                                 const unsigned char* alt_bytes, int alt_len) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_source(utf8_to_wide(src_bytes, src_len));
        el->set_alt(utf8_to_wide(alt_bytes, alt_len));
    }
}

void __stdcall EU_SetImageFit(HWND hwnd, int element_id, int fit) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_fit(fit);
    }
}

void __stdcall EU_SetImagePreview(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_preview_open(open != 0);
    }
}

void __stdcall EU_SetImagePreviewEnabled(HWND hwnd, int element_id, int enabled) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_preview_enabled(enabled != 0);
    }
}

void __stdcall EU_SetImagePreviewTransform(HWND hwnd, int element_id,
                                           int scale_percent, int offset_x, int offset_y) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_preview_transform(scale_percent, offset_x, offset_y);
    }
}

void __stdcall EU_SetImageCacheEnabled(HWND hwnd, int element_id, int enabled) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_cache_enabled(enabled != 0);
    }
}

void __stdcall EU_SetImageLazy(HWND hwnd, int element_id, int lazy) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_lazy(lazy != 0);
    }
}

void __stdcall EU_SetImagePlaceholder(HWND hwnd, int element_id,
                                      const unsigned char* icon_bytes, int icon_len,
                                      const unsigned char* text_bytes, int text_len,
                                      Color fg, Color bg) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_placeholder(utf8_to_wide(icon_bytes, icon_len),
                            utf8_to_wide(text_bytes, text_len),
                            fg, bg);
    }
}

void __stdcall EU_SetImageErrorContent(HWND hwnd, int element_id,
                                       const unsigned char* icon_bytes, int icon_len,
                                       const unsigned char* text_bytes, int text_len,
                                       Color fg, Color bg) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_error_content(utf8_to_wide(icon_bytes, icon_len),
                              utf8_to_wide(text_bytes, text_len),
                              fg, bg);
    }
}

void __stdcall EU_SetImagePreviewList(HWND hwnd, int element_id,
                                      const unsigned char* sources_bytes, int sources_len,
                                      int selected_index) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_preview_list(split_option_list(sources_bytes, sources_len), selected_index);
    }
}

void __stdcall EU_SetImagePreviewIndex(HWND hwnd, int element_id, int index) {
    if (auto* el = find_typed_element<Image>(hwnd, element_id)) {
        el->set_preview_index(index);
    }
}

int __stdcall EU_GetImageStatus(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Image>(hwnd, element_id);
    return el ? el->load_status : -1;
}

int __stdcall EU_GetImagePreviewOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Image>(hwnd, element_id);
    return (el && el->is_preview_open()) ? 1 : 0;
}

int __stdcall EU_GetImageOptions(HWND hwnd, int element_id,
                                 int* fit, int* preview_enabled, int* preview_open, int* status) {
    auto* el = find_typed_element<Image>(hwnd, element_id);
    if (!el) return 0;
    if (fit) *fit = el->fit;
    if (preview_enabled) *preview_enabled = el->preview_enabled ? 1 : 0;
    if (preview_open) *preview_open = el->is_preview_open() ? 1 : 0;
    if (status) *status = el->load_status;
    return 1;
}

int __stdcall EU_GetImageFullOptions(HWND hwnd, int element_id,
                                     int* fit, int* preview_enabled, int* preview_open, int* status,
                                     int* scale_percent, int* offset_x, int* offset_y,
                                     int* cache_enabled, int* reload_count,
                                     int* bitmap_width, int* bitmap_height) {
    auto* el = find_typed_element<Image>(hwnd, element_id);
    if (!el) return 0;
    if (fit) *fit = el->fit;
    if (preview_enabled) *preview_enabled = el->preview_enabled ? 1 : 0;
    if (preview_open) *preview_open = el->is_preview_open() ? 1 : 0;
    if (status) *status = el->load_status;
    if (scale_percent) *scale_percent = el->preview_scale_percent;
    if (offset_x) *offset_x = el->preview_offset_x;
    if (offset_y) *offset_y = el->preview_offset_y;
    if (cache_enabled) *cache_enabled = el->cache_enabled ? 1 : 0;
    if (reload_count) *reload_count = el->reload_count;
    if (bitmap_width) *bitmap_width = el->bitmap_width;
    if (bitmap_height) *bitmap_height = el->bitmap_height;
    return 1;
}

int __stdcall EU_GetImageAdvancedOptions(HWND hwnd, int element_id,
                                         int* fit, int* lazy, int* preview_enabled,
                                         int* preview_open, int* preview_index,
                                         int* preview_count, int* status,
                                         int* scale_percent, int* offset_x, int* offset_y) {
    auto* el = find_typed_element<Image>(hwnd, element_id);
    if (!el) return 0;
    if (fit) *fit = el->fit;
    if (lazy) *lazy = el->lazy ? 1 : 0;
    if (preview_enabled) *preview_enabled = el->preview_enabled ? 1 : 0;
    if (preview_open) *preview_open = el->is_preview_open() ? 1 : 0;
    if (preview_index) *preview_index = el->preview_index;
    if (preview_count) *preview_count = el->preview_count();
    if (status) *status = el->load_status;
    if (scale_percent) *scale_percent = el->preview_scale_percent;
    if (offset_x) *offset_x = el->preview_offset_x;
    if (offset_y) *offset_y = el->preview_offset_y;
    return 1;
}

void __stdcall EU_SetCarouselItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetCarouselActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

void __stdcall EU_SetCarouselOptions(HWND hwnd, int element_id,
                                     int loop, int indicator_position,
                                     int show_arrows, int show_indicators) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->set_options(loop, indicator_position, show_arrows, show_indicators);
    }
}

void __stdcall EU_SetCarouselAutoplay(HWND hwnd, int element_id, int enabled, int interval_ms) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->set_autoplay(enabled, interval_ms);
    }
}

void __stdcall EU_SetCarouselAnimation(HWND hwnd, int element_id, int transition_ms) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->set_animation(transition_ms);
    }
}

void __stdcall EU_CarouselAdvance(HWND hwnd, int element_id, int delta) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->advance(delta);
    }
}

void __stdcall EU_CarouselTick(HWND hwnd, int element_id, int elapsed_ms) {
    if (auto* el = find_typed_element<Carousel>(hwnd, element_id)) {
        el->tick(elapsed_ms);
    }
}

int __stdcall EU_GetCarouselActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Carousel>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetCarouselItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Carousel>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

int __stdcall EU_GetCarouselOptions(HWND hwnd, int element_id,
                                    int* loop, int* indicator_position,
                                    int* show_arrows, int* show_indicators,
                                    int* autoplay, int* interval_ms) {
    auto* el = find_typed_element<Carousel>(hwnd, element_id);
    if (!el) return 0;
    if (loop) *loop = el->loop ? 1 : 0;
    if (indicator_position) *indicator_position = el->indicator_position;
    if (show_arrows) *show_arrows = el->show_arrows ? 1 : 0;
    if (show_indicators) *show_indicators = el->show_indicators ? 1 : 0;
    if (autoplay) *autoplay = el->autoplay ? 1 : 0;
    if (interval_ms) *interval_ms = el->interval_ms;
    return 1;
}

int __stdcall EU_GetCarouselFullState(HWND hwnd, int element_id,
                                      int* active_index, int* previous_index,
                                      int* item_count, int* loop,
                                      int* indicator_position,
                                      int* show_arrows, int* show_indicators,
                                      int* autoplay, int* interval_ms,
                                      int* autoplay_tick, int* autoplay_elapsed_ms,
                                      int* transition_ms, int* transition_progress,
                                      int* transition_direction,
                                      int* last_action, int* change_count) {
    auto* el = find_typed_element<Carousel>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (previous_index) *previous_index = el->previous_index;
    if (item_count) *item_count = (int)el->items.size();
    if (loop) *loop = el->loop ? 1 : 0;
    if (indicator_position) *indicator_position = el->indicator_position;
    if (show_arrows) *show_arrows = el->show_arrows ? 1 : 0;
    if (show_indicators) *show_indicators = el->show_indicators ? 1 : 0;
    if (autoplay) *autoplay = el->autoplay ? 1 : 0;
    if (interval_ms) *interval_ms = el->interval_ms;
    if (autoplay_tick) *autoplay_tick = el->autoplay_tick;
    if (autoplay_elapsed_ms) *autoplay_elapsed_ms = el->autoplay_elapsed_ms;
    if (transition_ms) *transition_ms = el->transition_ms;
    if (transition_progress) *transition_progress = el->transition_progress;
    if (transition_direction) *transition_direction = el->transition_direction;
    if (last_action) *last_action = el->last_action;
    if (change_count) *change_count = el->change_count;
    return 1;
}

void __stdcall EU_SetUploadFiles(HWND hwnd, int element_id,
                                 const unsigned char* files_bytes, int files_len) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_files(split_option_list(files_bytes, files_len));
    }
}

void __stdcall EU_SetUploadFileItems(HWND hwnd, int element_id,
                                     const unsigned char* files_bytes, int files_len) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_file_items(parse_upload_file_items(files_bytes, files_len));
    }
}

void __stdcall EU_SetUploadOptions(HWND hwnd, int element_id, int multiple, int auto_upload) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_options(multiple, auto_upload);
    }
}

void __stdcall EU_SetUploadStyle(HWND hwnd, int element_id, int style_mode,
                                 int show_file_list, int show_tip, int show_actions,
                                 int drop_enabled) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_style(style_mode, show_file_list, show_tip, show_actions, drop_enabled);
    }
}

int __stdcall EU_GetUploadStyle(HWND hwnd, int element_id, int* style_mode,
                                int* show_file_list, int* show_tip,
                                int* show_actions, int* drop_enabled) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el) return 0;
    if (style_mode) *style_mode = el->style_mode;
    if (show_file_list) *show_file_list = el->show_file_list;
    if (show_tip) *show_tip = el->show_tip;
    if (show_actions) *show_actions = el->show_actions;
    if (drop_enabled) *drop_enabled = el->drop_enabled;
    return 1;
}

void __stdcall EU_SetUploadTexts(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* tip_bytes, int tip_len,
                                 const unsigned char* trigger_bytes, int trigger_len,
                                 const unsigned char* submit_bytes, int submit_len) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_texts(utf8_to_wide(title_bytes, title_len),
                      utf8_to_wide(tip_bytes, tip_len),
                      utf8_to_wide(trigger_bytes, trigger_len),
                      utf8_to_wide(submit_bytes, submit_len));
    }
}

void __stdcall EU_SetUploadConstraints(HWND hwnd, int element_id, int limit,
                                       int max_size_kb,
                                       const unsigned char* accept_bytes, int accept_len) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_constraints(limit, max_size_kb, utf8_to_wide(accept_bytes, accept_len));
    }
}

int __stdcall EU_GetUploadConstraints(HWND hwnd, int element_id, int* limit,
                                      int* max_size_kb,
                                      unsigned char* accept_buffer, int accept_buffer_size) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el) return 0;
    if (limit) *limit = el->limit;
    if (max_size_kb) *max_size_kb = el->max_size_kb;
    return copy_wide_as_utf8(el->accept_filter, accept_buffer, accept_buffer_size);
}

void __stdcall EU_SetUploadPreviewOpen(HWND hwnd, int element_id, int file_index, int open) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_preview_open(file_index, open != 0);
    }
}

int __stdcall EU_GetUploadPreviewState(HWND hwnd, int element_id, int* file_index, int* open) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el) return 0;
    if (file_index) *file_index = el->preview_index;
    if (open) *open = el->preview_open;
    return 1;
}

void __stdcall EU_SetUploadSelectedFiles(HWND hwnd, int element_id,
                                         const unsigned char* files_bytes, int files_len) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_selected_files(split_option_list(files_bytes, files_len));
    }
}

void __stdcall EU_SetUploadFileStatus(HWND hwnd, int element_id,
                                      int file_index, int status, int progress) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->set_file_status(file_index, status, progress);
    }
}

void __stdcall EU_RemoveUploadFile(HWND hwnd, int element_id, int file_index) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->remove_file(file_index);
    }
}

void __stdcall EU_RetryUploadFile(HWND hwnd, int element_id, int file_index) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->retry_file(file_index);
    }
}

void __stdcall EU_ClearUploadFiles(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->clear_files();
    }
}

int __stdcall EU_OpenUploadFileDialog(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    return el ? el->open_file_dialog(hwnd) : 0;
}

int __stdcall EU_StartUpload(HWND hwnd, int element_id, int file_index) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    return el ? el->start_upload(file_index) : 0;
}

int __stdcall EU_GetUploadFileCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    return el ? (int)el->file_items.size() : 0;
}

int __stdcall EU_GetUploadFileStatus(HWND hwnd, int element_id,
                                     int file_index, int* status, int* progress) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el || file_index < 0 || file_index >= (int)el->file_items.size()) return 0;
    const auto& item = el->file_items[(size_t)file_index];
    if (status) *status = item.status;
    if (progress) *progress = item.progress;
    return 1;
}

int __stdcall EU_GetUploadSelectedFiles(HWND hwnd, int element_id,
                                        unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->selected_files_text(), buffer, buffer_size);
}

int __stdcall EU_GetUploadFileName(HWND hwnd, int element_id, int file_index,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el || file_index < 0 || file_index >= (int)el->file_items.size()) return 0;
    return copy_wide_as_utf8(el->file_items[(size_t)file_index].name, buffer, buffer_size);
}

int __stdcall EU_GetUploadFullState(HWND hwnd, int element_id,
                                    int* file_count, int* selected_count,
                                    int* last_selected_count, int* upload_request_count,
                                    int* retry_count, int* remove_count,
                                    int* last_action, int* waiting_count,
                                    int* uploading_count, int* success_count,
                                    int* failed_count, int* multiple,
                                    int* auto_upload) {
    auto* el = find_typed_element<Upload>(hwnd, element_id);
    if (!el) return 0;
    int waiting = 0;
    int uploading = 0;
    int success = 0;
    int failed = 0;
    for (const auto& item : el->file_items) {
        if (item.status == 0) ++waiting;
        else if (item.status == 2) ++uploading;
        else if (item.status == 3) ++failed;
        else ++success;
    }
    if (file_count) *file_count = (int)el->file_items.size();
    if (selected_count) *selected_count = el->selected_count;
    if (last_selected_count) *last_selected_count = el->last_selected_count;
    if (upload_request_count) *upload_request_count = el->upload_request_count;
    if (retry_count) *retry_count = el->retry_count;
    if (remove_count) *remove_count = el->remove_count;
    if (last_action) *last_action = el->last_action;
    if (waiting_count) *waiting_count = waiting;
    if (uploading_count) *uploading_count = uploading;
    if (success_count) *success_count = success;
    if (failed_count) *failed_count = failed;
    if (multiple) *multiple = el->multiple;
    if (auto_upload) *auto_upload = el->auto_upload;
    return 1;
}

void __stdcall EU_SetUploadSelectCallback(HWND hwnd, int element_id, ElementTextCallback cb) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->select_cb = cb;
    }
}

void __stdcall EU_SetUploadActionCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Upload>(hwnd, element_id)) {
        el->upload_cb = cb;
    }
}

void __stdcall EU_SetInfiniteScrollItems(HWND hwnd, int element_id,
                                         const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->set_items(parse_infinite_scroll_items(items_bytes, items_len));
    }
}

void __stdcall EU_AppendInfiniteScrollItems(HWND hwnd, int element_id,
                                            const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->append_items(parse_infinite_scroll_items(items_bytes, items_len));
    }
}

void __stdcall EU_ClearInfiniteScrollItems(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->clear_items();
    }
}

void __stdcall EU_SetInfiniteScrollState(HWND hwnd, int element_id,
                                         int loading, int no_more, int disabled) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->set_state(loading != 0, no_more != 0, disabled != 0);
    }
}

void __stdcall EU_SetInfiniteScrollOptions(HWND hwnd, int element_id,
                                           int item_height, int gap, int threshold,
                                           int style_mode, int show_scrollbar, int show_index) {
    WindowState* st = window_state(hwnd);
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->set_options(item_height, gap, threshold, style_mode,
                        show_scrollbar != 0, show_index != 0,
                        st ? st->dpi_scale : 1.0f);
    }
}

void __stdcall EU_SetInfiniteScrollTexts(HWND hwnd, int element_id,
                                         const unsigned char* loading_bytes, int loading_len,
                                         const unsigned char* no_more_bytes, int no_more_len,
                                         const unsigned char* empty_bytes, int empty_len) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->set_texts(utf8_to_wide(loading_bytes, loading_len),
                      utf8_to_wide(no_more_bytes, no_more_len),
                      utf8_to_wide(empty_bytes, empty_len));
    }
}

void __stdcall EU_SetInfiniteScrollScroll(HWND hwnd, int element_id, int scroll_y) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->set_scroll(scroll_y);
    }
}

int __stdcall EU_GetInfiniteScrollFullState(HWND hwnd, int element_id,
                                            int* item_count, int* scroll_y, int* max_scroll,
                                            int* content_height, int* viewport_height,
                                            int* loading, int* no_more, int* disabled,
                                            int* load_count, int* change_count,
                                            int* last_action, int* threshold,
                                            int* style_mode, int* show_scrollbar,
                                            int* show_index) {
    auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id);
    if (!el) return 0;
    if (item_count) *item_count = (int)el->items.size();
    if (scroll_y) *scroll_y = el->scroll_y;
    if (max_scroll) *max_scroll = el->max_scroll();
    if (content_height) *content_height = el->content_height();
    if (viewport_height) *viewport_height = el->viewport_height();
    if (loading) *loading = el->loading ? 1 : 0;
    if (no_more) *no_more = el->no_more ? 1 : 0;
    if (disabled) *disabled = el->disabled ? 1 : 0;
    if (load_count) *load_count = el->load_count;
    if (change_count) *change_count = el->change_count;
    if (last_action) *last_action = el->last_action;
    if (threshold) *threshold = el->threshold;
    if (style_mode) *style_mode = el->style_mode;
    if (show_scrollbar) *show_scrollbar = el->show_scrollbar ? 1 : 0;
    if (show_index) *show_index = el->show_index ? 1 : 0;
    return 1;
}

void __stdcall EU_SetInfiniteScrollLoadCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<InfiniteScroll>(hwnd, element_id)) {
        el->load_cb = cb;
    }
}

void __stdcall EU_SetBreadcrumbItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Breadcrumb>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetBreadcrumbSeparator(HWND hwnd, int element_id,
                                         const unsigned char* separator_bytes, int separator_len) {
    if (auto* el = find_typed_element<Breadcrumb>(hwnd, element_id)) {
        el->set_separator(utf8_to_wide(separator_bytes, separator_len));
    }
}

void __stdcall EU_SetBreadcrumbCurrent(HWND hwnd, int element_id, int current_index) {
    if (auto* el = find_typed_element<Breadcrumb>(hwnd, element_id)) {
        el->set_current_index(current_index);
    }
}

void __stdcall EU_TriggerBreadcrumbClick(HWND hwnd, int element_id, int item_index) {
    if (auto* el = find_typed_element<Breadcrumb>(hwnd, element_id)) {
        el->activate_index(item_index, 4);
    }
}

int __stdcall EU_GetBreadcrumbCurrent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Breadcrumb>(hwnd, element_id);
    return el ? el->current_index : -1;
}

int __stdcall EU_GetBreadcrumbItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Breadcrumb>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

int __stdcall EU_GetBreadcrumbState(HWND hwnd, int element_id,
                                    int* current_index, int* item_count) {
    auto* el = find_typed_element<Breadcrumb>(hwnd, element_id);
    if (!el) return 0;
    if (current_index) *current_index = el->current_index;
    if (item_count) *item_count = (int)el->items.size();
    return 1;
}

int __stdcall EU_GetBreadcrumbItem(HWND hwnd, int element_id, int item_index,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Breadcrumb>(hwnd, element_id);
    if (!el || item_index < 0 || item_index >= (int)el->items.size()) return 0;
    return copy_wide_as_utf8(el->items[(size_t)item_index], buffer, buffer_size);
}

int __stdcall EU_GetBreadcrumbFullState(HWND hwnd, int element_id,
                                        int* current_index, int* item_count,
                                        int* hover_index, int* press_index,
                                        int* last_clicked_index,
                                        int* click_count, int* last_action) {
    auto* el = find_typed_element<Breadcrumb>(hwnd, element_id);
    if (!el) return 0;
    if (current_index) *current_index = el->current_index;
    if (item_count) *item_count = (int)el->items.size();
    if (hover_index) *hover_index = el->hover_index();
    if (press_index) *press_index = el->press_index();
    if (last_clicked_index) *last_clicked_index = el->last_clicked_index;
    if (click_count) *click_count = el->click_count;
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetBreadcrumbSelectCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Breadcrumb>(hwnd, element_id)) {
        el->select_cb = cb;
    }
}

void __stdcall EU_SetTabsItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetTabsItemsEx(HWND hwnd, int element_id,
                                 const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_items_ex(parse_tabs_items_ex(items_bytes, items_len));
    }
}

void __stdcall EU_SetTabsActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

void __stdcall EU_SetTabsActiveName(HWND hwnd, int element_id,
                                    const unsigned char* name_bytes, int name_len) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_active_name(utf8_to_wide(name_bytes, name_len));
    }
}

void __stdcall EU_SetTabsType(HWND hwnd, int element_id, int tab_type) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_tab_type(tab_type);
    }
}

void __stdcall EU_SetTabsPosition(HWND hwnd, int element_id, int tab_position) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_tab_position(tab_position);
    }
}

void __stdcall EU_SetTabsOptions(HWND hwnd, int element_id,
                                 int tab_type, int closable, int addable) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_options(tab_type, closable != 0, addable != 0);
    }
}

void __stdcall EU_SetTabsEditable(HWND hwnd, int element_id, int editable) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_editable(editable != 0);
    }
}

void __stdcall EU_SetTabsContentVisible(HWND hwnd, int element_id, int visible) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_content_visible(visible != 0);
    }
}

void __stdcall EU_AddTabsItem(HWND hwnd, int element_id,
                              const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->add_tab(utf8_to_wide(text_bytes, text_len));
    }
}

void __stdcall EU_CloseTabsItem(HWND hwnd, int element_id, int item_index) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->close_tab(item_index);
    }
}

void __stdcall EU_SetTabsScroll(HWND hwnd, int element_id, int offset) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->set_scroll_offset(offset);
    }
}

void __stdcall EU_TabsScroll(HWND hwnd, int element_id, int delta) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->scroll_delta(delta);
    }
}

int __stdcall EU_GetTabsActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetTabsItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

int __stdcall EU_GetTabsState(HWND hwnd, int element_id,
                              int* active_index, int* item_count, int* tab_type) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = (int)el->items.size();
    if (tab_type) *tab_type = el->tab_type;
    return 1;
}

int __stdcall EU_GetTabsItem(HWND hwnd, int element_id, int item_index,
                             unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el || item_index < 0 || item_index >= (int)el->items.size()) return 0;
    return copy_wide_as_utf8(el->items[item_index], buffer, buffer_size);
}

int __stdcall EU_GetTabsActiveName(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->active_name(), buffer, buffer_size);
}

int __stdcall EU_GetTabsItemContent(HWND hwnd, int element_id, int item_index,
                                    unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->item_content(item_index), buffer, buffer_size);
}

int __stdcall EU_GetTabsFullState(HWND hwnd, int element_id,
                                  int* active_index, int* item_count, int* tab_type,
                                  int* closable, int* addable,
                                  int* scroll_offset, int* max_scroll_offset,
                                  int* hover_index, int* press_index,
                                  int* hover_part, int* press_part,
                                  int* last_closed_index, int* last_added_index,
                                  int* close_count, int* add_count,
                                  int* select_count, int* scroll_count,
                                  int* last_action) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = (int)el->items.size();
    if (tab_type) *tab_type = el->tab_type;
    if (closable) *closable = el->closable ? 1 : 0;
    if (addable) *addable = el->addable ? 1 : 0;
    if (scroll_offset) *scroll_offset = el->scroll_offset;
    if (max_scroll_offset) *max_scroll_offset = el->max_scroll_offset;
    if (hover_index) *hover_index = el->hover_index();
    if (press_index) *press_index = el->press_index();
    if (hover_part) *hover_part = el->hover_part();
    if (press_part) *press_part = el->press_part();
    if (last_closed_index) *last_closed_index = el->last_closed_index;
    if (last_added_index) *last_added_index = el->last_added_index;
    if (close_count) *close_count = el->close_count;
    if (add_count) *add_count = el->add_count;
    if (select_count) *select_count = el->select_count;
    if (scroll_count) *scroll_count = el->scroll_count;
    if (last_action) *last_action = el->last_action;
    return 1;
}

int __stdcall EU_GetTabsFullStateEx(HWND hwnd, int element_id,
                                    int* active_index, int* item_count, int* tab_type,
                                    int* closable, int* addable,
                                    int* scroll_offset, int* max_scroll_offset,
                                    int* hover_index, int* press_index,
                                    int* hover_part, int* press_part,
                                    int* last_closed_index, int* last_added_index,
                                    int* close_count, int* add_count,
                                    int* select_count, int* scroll_count,
                                    int* last_action, int* tab_position,
                                    int* editable, int* content_visible,
                                    int* active_disabled, int* active_closable) {
    auto* el = find_typed_element<Tabs>(hwnd, element_id);
    if (!el) return 0;
    EU_GetTabsFullState(hwnd, element_id, active_index, item_count, tab_type,
                        closable, addable, scroll_offset, max_scroll_offset,
                        hover_index, press_index, hover_part, press_part,
                        last_closed_index, last_added_index, close_count, add_count,
                        select_count, scroll_count, last_action);
    if (tab_position) *tab_position = el->tab_position;
    if (editable) *editable = el->editable ? 1 : 0;
    if (content_visible) *content_visible = el->content_visible ? 1 : 0;
    bool has_active = el->active_index >= 0 && el->active_index < (int)el->tab_items.size();
    if (active_disabled) *active_disabled = has_active && el->tab_items[el->active_index].disabled ? 1 : 0;
    if (active_closable) *active_closable = has_active && el->tab_items[el->active_index].closable ? 1 : 0;
    return 1;
}

void __stdcall EU_SetTabsChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetTabsCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetTabsAddCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Tabs>(hwnd, element_id)) {
        el->add_cb = cb;
    }
}

void __stdcall EU_SetPagination(HWND hwnd, int element_id,
                                int total, int page_size, int current_page) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_total(total);
        el->set_page_size(page_size);
        el->set_current_page(current_page);
    }
}

void __stdcall EU_SetPaginationCurrent(HWND hwnd, int element_id, int current_page) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_current_page(current_page);
    }
}

void __stdcall EU_SetPaginationPageSize(HWND hwnd, int element_id, int page_size) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_page_size(page_size);
    }
}

void __stdcall EU_SetPaginationOptions(HWND hwnd, int element_id,
                                       int show_jumper, int show_size_changer,
                                       int visible_page_count) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_options(show_jumper, show_size_changer, visible_page_count);
    }
}

void __stdcall EU_SetPaginationAdvancedOptions(HWND hwnd, int element_id,
                                               int background, int small_style,
                                               int hide_on_single_page) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_advanced_options(background, small_style, hide_on_single_page);
    }
}

void __stdcall EU_SetPaginationPageSizeOptions(HWND hwnd, int element_id,
                                               const int* sizes, int count) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        std::vector<int> values;
        if (sizes && count > 0) {
            for (int i = 0; i < count && i < 32; ++i) values.push_back(sizes[i]);
        }
        el->set_page_size_options(values);
    }
}

void __stdcall EU_SetPaginationJumpPage(HWND hwnd, int element_id, int jump_page) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->set_jump_page(jump_page);
    }
}

void __stdcall EU_TriggerPaginationJump(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->trigger_jump(5);
    }
}

void __stdcall EU_NextPaginationPageSize(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->next_page_size();
    }
}

int __stdcall EU_GetPaginationCurrent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Pagination>(hwnd, element_id);
    return el ? el->current_page : 0;
}

int __stdcall EU_GetPaginationPageCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Pagination>(hwnd, element_id);
    return el ? el->page_count() : 0;
}

int __stdcall EU_GetPaginationState(HWND hwnd, int element_id,
                                    int* total, int* page_size,
                                    int* current_page, int* page_count) {
    auto* el = find_typed_element<Pagination>(hwnd, element_id);
    if (!el) return 0;
    if (total) *total = el->total;
    if (page_size) *page_size = el->page_size;
    if (current_page) *current_page = el->current_page;
    if (page_count) *page_count = el->page_count();
    return 1;
}

int __stdcall EU_GetPaginationFullState(HWND hwnd, int element_id,
                                        int* total, int* page_size,
                                        int* current_page, int* page_count,
                                        int* jump_page, int* visible_page_count,
                                        int* show_jumper, int* show_size_changer,
                                        int* hover_part, int* press_part,
                                        int* change_count, int* size_change_count,
                                        int* jump_count, int* last_action) {
    auto* el = find_typed_element<Pagination>(hwnd, element_id);
    if (!el) return 0;
    if (total) *total = el->total;
    if (page_size) *page_size = el->page_size;
    if (current_page) *current_page = el->current_page;
    if (page_count) *page_count = el->page_count();
    if (jump_page) *jump_page = el->jump_page;
    if (visible_page_count) *visible_page_count = el->visible_page_count;
    if (show_jumper) *show_jumper = el->show_jumper ? 1 : 0;
    if (show_size_changer) *show_size_changer = el->show_size_changer ? 1 : 0;
    if (hover_part) *hover_part = el->hover_part();
    if (press_part) *press_part = el->press_part();
    if (change_count) *change_count = el->change_count;
    if (size_change_count) *size_change_count = el->size_change_count;
    if (jump_count) *jump_count = el->jump_count;
    if (last_action) *last_action = el->last_action;
    return 1;
}

int __stdcall EU_GetPaginationAdvancedOptions(HWND hwnd, int element_id,
                                              int* background, int* small_style,
                                              int* hide_on_single_page) {
    auto* el = find_typed_element<Pagination>(hwnd, element_id);
    if (!el) return 0;
    if (background) *background = el->background ? 1 : 0;
    if (small_style) *small_style = el->small_style ? 1 : 0;
    if (hide_on_single_page) *hide_on_single_page = el->hide_on_single_page ? 1 : 0;
    return 1;
}

void __stdcall EU_SetPaginationChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Pagination>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetStepsItems(HWND hwnd, int element_id,
                                const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_items(split_option_list(items_bytes, items_len));
    }
}

void __stdcall EU_SetStepsDetailItems(HWND hwnd, int element_id,
                                      const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_step_items(parse_pair_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetStepsIconItems(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_icon_items(parse_steps_visual_items(items_bytes, items_len));
    }
}

void __stdcall EU_SetStepsActive(HWND hwnd, int element_id, int active_index) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_active_index(active_index);
    }
}

void __stdcall EU_SetStepsDirection(HWND hwnd, int element_id, int direction) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_direction(direction);
    }
}

void __stdcall EU_SetStepsOptions(HWND hwnd, int element_id, int space,
                                  int align_center, int simple,
                                  int finish_status, int process_status) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->set_options(space, align_center != 0, simple != 0,
                        finish_status, process_status);
    }
}

int __stdcall EU_GetStepsOptions(HWND hwnd, int element_id, int* space,
                                 int* align_center, int* simple,
                                 int* finish_status, int* process_status) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    if (!el) return 0;
    if (space) *space = el->space;
    if (align_center) *align_center = el->align_center ? 1 : 0;
    if (simple) *simple = el->simple ? 1 : 0;
    if (finish_status) *finish_status = el->finish_status;
    if (process_status) *process_status = el->process_status;
    return 1;
}

void __stdcall EU_SetStepsStatuses(HWND hwnd, int element_id, const int* statuses, int count) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        std::vector<int> values;
        if (statuses && count > 0) {
            for (int i = 0; i < count && i < 128; ++i) values.push_back(statuses[i]);
        }
        el->set_statuses(values);
    }
}

void __stdcall EU_TriggerStepsClick(HWND hwnd, int element_id, int item_index) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->last_clicked_index = item_index;
        ++el->click_count;
        el->activate_index(item_index, 4);
    }
}

int __stdcall EU_GetStepsActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    return el ? el->active_index : -1;
}

int __stdcall EU_GetStepsItemCount(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    return el ? (int)el->items.size() : 0;
}

int __stdcall EU_GetStepsState(HWND hwnd, int element_id,
                               int* active_index, int* item_count, int* direction) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = (int)el->items.size();
    if (direction) *direction = el->direction;
    return 1;
}

int __stdcall EU_GetStepsItem(HWND hwnd, int element_id, int item_index, int text_kind,
                              unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    if (!el || item_index < 0 || item_index >= (int)el->items.size()) return 0;
    const std::wstring& value = (text_kind == 1 && item_index < (int)el->descriptions.size())
        ? el->descriptions[item_index]
        : el->items[item_index];
    return copy_wide_as_utf8(value, buffer, buffer_size);
}

int __stdcall EU_GetStepsFullState(HWND hwnd, int element_id,
                                   int* active_index, int* item_count, int* direction,
                                   int* hover_index, int* press_index,
                                   int* last_clicked_index, int* click_count,
                                   int* change_count, int* last_action,
                                   int* active_status, int* failed_count) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    if (!el) return 0;
    if (active_index) *active_index = el->active_index;
    if (item_count) *item_count = (int)el->items.size();
    if (direction) *direction = el->direction;
    if (hover_index) *hover_index = el->hover_index();
    if (press_index) *press_index = el->press_index();
    if (last_clicked_index) *last_clicked_index = el->last_clicked_index;
    if (click_count) *click_count = el->click_count;
    if (change_count) *change_count = el->change_count;
    if (last_action) *last_action = el->last_action;
    if (active_status) *active_status = el->status_at(el->active_index);
    if (failed_count) *failed_count = el->failed_count();
    return 1;
}

int __stdcall EU_GetStepsVisualState(HWND hwnd, int element_id,
                                     int* space, int* align_center, int* simple,
                                     int* finish_status, int* process_status,
                                     int* icon_count) {
    auto* el = find_typed_element<Steps>(hwnd, element_id);
    if (!el) return 0;
    if (space) *space = el->space;
    if (align_center) *align_center = el->align_center ? 1 : 0;
    if (simple) *simple = el->simple ? 1 : 0;
    if (finish_status) *finish_status = el->finish_status;
    if (process_status) *process_status = el->process_status;
    int count = 0;
    for (const auto& icon : el->icons) {
        if (!icon.empty()) ++count;
    }
    if (icon_count) *icon_count = count;
    return 1;
}

void __stdcall EU_SetStepsChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Steps>(hwnd, element_id)) {
        el->change_cb = cb;
    }
}

void __stdcall EU_SetAlertDescription(HWND hwnd, int element_id,
                                      const unsigned char* desc_bytes, int desc_len) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_description(utf8_to_wide(desc_bytes, desc_len));
    }
}

void __stdcall EU_SetAlertType(HWND hwnd, int element_id, int alert_type) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_type(alert_type);
    }
}

void __stdcall EU_SetAlertEffect(HWND hwnd, int element_id, int effect) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_effect(effect);
    }
}

void __stdcall EU_SetAlertClosable(HWND hwnd, int element_id, int closable) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_closable(closable != 0);
    }
}

void __stdcall EU_SetAlertAdvancedOptions(HWND hwnd, int element_id,
                                          int show_icon, int center, int wrap_description) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_advanced_options(show_icon != 0, center != 0, wrap_description != 0);
    }
}

int __stdcall EU_GetAlertAdvancedOptions(HWND hwnd, int element_id,
                                         int* show_icon, int* center,
                                         int* wrap_description) {
    auto* el = find_typed_element<Alert>(hwnd, element_id);
    if (!el) return 0;
    if (show_icon) *show_icon = el->show_icon ? 1 : 0;
    if (center) *center = el->center ? 1 : 0;
    if (wrap_description) *wrap_description = el->wrap_description ? 1 : 0;
    return 1;
}

void __stdcall EU_SetAlertCloseText(HWND hwnd, int element_id,
                                    const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_close_text(utf8_to_wide(text_bytes, text_len));
    }
}

int __stdcall EU_GetAlertText(HWND hwnd, int element_id, int text_type,
                              unsigned char* out_bytes, int out_len) {
    auto* el = find_typed_element<Alert>(hwnd, element_id);
    if (!el) return 0;
    const std::wstring* value = &el->text;
    if (text_type == 1) value = &el->description;
    else if (text_type == 2) value = &el->close_text;
    return copy_wide_as_utf8(*value, out_bytes, out_len);
}

void __stdcall EU_SetAlertClosed(HWND hwnd, int element_id, int closed) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->set_closed(closed != 0);
    }
}

void __stdcall EU_TriggerAlertClose(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->close_alert(4);
    }
}

int __stdcall EU_GetAlertClosed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Alert>(hwnd, element_id);
    return el ? (el->closed ? 1 : 0) : 0;
}

int __stdcall EU_GetAlertOptions(HWND hwnd, int element_id,
                                 int* alert_type, int* effect,
                                 int* closable, int* closed) {
    auto* el = find_typed_element<Alert>(hwnd, element_id);
    if (!el) return 0;
    if (alert_type) *alert_type = el->alert_type;
    if (effect) *effect = el->effect;
    if (closable) *closable = el->closable ? 1 : 0;
    if (closed) *closed = el->closed ? 1 : 0;
    return 1;
}

int __stdcall EU_GetAlertFullState(HWND hwnd, int element_id,
                                   int* alert_type, int* effect,
                                   int* closable, int* closed,
                                   int* close_hover, int* close_down,
                                   int* close_count, int* last_action) {
    auto* el = find_typed_element<Alert>(hwnd, element_id);
    if (!el) return 0;
    if (alert_type) *alert_type = el->alert_type;
    if (effect) *effect = el->effect;
    if (closable) *closable = el->closable ? 1 : 0;
    if (closed) *closed = el->closed ? 1 : 0;
    if (close_hover) *close_hover = el->close_hover() ? 1 : 0;
    if (close_down) *close_down = el->close_down() ? 1 : 0;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetAlertCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Alert>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetResultSubtitle(HWND hwnd, int element_id,
                                    const unsigned char* subtitle_bytes, int subtitle_len) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->set_subtitle(utf8_to_wide(subtitle_bytes, subtitle_len));
    }
}

void __stdcall EU_SetResultType(HWND hwnd, int element_id, int result_type) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->set_type(result_type);
    }
}

void __stdcall EU_SetResultActions(HWND hwnd, int element_id,
                                   const unsigned char* actions_bytes, int actions_len) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->set_actions(split_option_list(actions_bytes, actions_len));
    }
}

int __stdcall EU_GetResultAction(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Result>(hwnd, element_id);
    return el ? el->last_action : -1;
}

int __stdcall EU_GetResultOptions(HWND hwnd, int element_id,
                                  int* result_type, int* action_count, int* last_action) {
    auto* el = find_typed_element<Result>(hwnd, element_id);
    if (!el) return 0;
    if (result_type) *result_type = el->result_type;
    if (action_count) *action_count = (int)el->actions.size();
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetResultExtraContent(HWND hwnd, int element_id,
                                        const unsigned char* content_bytes, int content_len) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->set_extra_content(utf8_to_wide(content_bytes, content_len));
    }
}

void __stdcall EU_TriggerResultAction(HWND hwnd, int element_id, int action_index) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->trigger_action(action_index, 4);
    }
}

int __stdcall EU_GetResultText(HWND hwnd, int element_id, int text_kind,
                               unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Result>(hwnd, element_id);
    if (!el) return 0;
    if (text_kind == 1) return copy_wide_as_utf8(el->subtitle, buffer, buffer_size);
    if (text_kind == 2) return copy_wide_as_utf8(el->extra_content, buffer, buffer_size);
    return copy_wide_as_utf8(el->text, buffer, buffer_size);
}

int __stdcall EU_GetResultActionText(HWND hwnd, int element_id, int action_index,
                                     unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Result>(hwnd, element_id);
    if (!el || action_index < 0 || action_index >= (int)el->actions.size()) return 0;
    return copy_wide_as_utf8(el->actions[(size_t)action_index], buffer, buffer_size);
}

int __stdcall EU_GetResultFullState(HWND hwnd, int element_id,
                                    int* result_type, int* action_count, int* last_action,
                                    int* hover_action, int* press_action,
                                    int* action_click_count, int* last_action_source,
                                    int* has_extra_content) {
    auto* el = find_typed_element<Result>(hwnd, element_id);
    if (!el) return 0;
    if (result_type) *result_type = el->result_type;
    if (action_count) *action_count = (int)el->actions.size();
    if (last_action) *last_action = el->last_action;
    if (hover_action) *hover_action = el->hover_action();
    if (press_action) *press_action = el->press_action();
    if (action_click_count) *action_click_count = el->action_click_count;
    if (last_action_source) *last_action_source = el->last_action_source;
    if (has_extra_content) *has_extra_content = el->extra_content.empty() ? 0 : 1;
    return 1;
}

void __stdcall EU_SetResultActionCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Result>(hwnd, element_id)) {
        el->action_cb = cb;
    }
}

void __stdcall EU_SetMessageBoxBeforeClose(HWND hwnd, int element_id,
                                           int delay_ms,
                                           const unsigned char* loading_bytes, int loading_len) {
    if (auto* el = find_typed_element<MessageBoxElement>(hwnd, element_id)) {
        el->set_before_close(delay_ms, utf8_to_wide(loading_bytes, loading_len));
    }
}

void __stdcall EU_SetMessageBoxInput(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len,
                                     const unsigned char* placeholder_bytes, int placeholder_len,
                                     const unsigned char* pattern_bytes, int pattern_len,
                                     const unsigned char* error_bytes, int error_len) {
    if (auto* el = find_typed_element<MessageBoxElement>(hwnd, element_id)) {
        el->set_input(utf8_to_wide(value_bytes, value_len),
                      utf8_to_wide(placeholder_bytes, placeholder_len),
                      utf8_to_wide(pattern_bytes, pattern_len),
                      utf8_to_wide(error_bytes, error_len));
    }
}

int __stdcall EU_GetMessageBoxInput(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<MessageBoxElement>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->input_value, buffer, buffer_size);
}

int __stdcall EU_GetMessageBoxFullState(HWND hwnd, int element_id,
                                        int* box_type, int* show_cancel, int* center,
                                        int* rich, int* distinguish, int* prompt,
                                        int* confirm_loading, int* input_error_visible,
                                        int* last_action, int* timer_elapsed_ms) {
    auto* el = find_typed_element<MessageBoxElement>(hwnd, element_id);
    if (!el) return 0;
    if (box_type) *box_type = el->box_type;
    if (show_cancel) *show_cancel = el->show_cancel ? 1 : 0;
    if (center) *center = el->center ? 1 : 0;
    if (rich) *rich = el->rich ? 1 : 0;
    if (distinguish) *distinguish = el->distinguish_cancel_and_close ? 1 : 0;
    if (prompt) *prompt = el->prompt ? 1 : 0;
    if (confirm_loading) *confirm_loading = el->confirm_loading ? 1 : 0;
    if (input_error_visible) *input_error_visible = el->input_error_visible ? 1 : 0;
    if (last_action) *last_action = el->last_action;
    if (timer_elapsed_ms) *timer_elapsed_ms = el->timer_elapsed_ms;
    return 1;
}

void __stdcall EU_SetMessageText(HWND hwnd, int element_id, const unsigned char* bytes, int len) {
    if (auto* el = find_typed_element<Message>(hwnd, element_id)) {
        el->set_text(utf8_to_wide(bytes, len));
    }
}

void __stdcall EU_SetMessageOptions(HWND hwnd, int element_id, int message_type,
                                    int closable, int center, int rich,
                                    int duration_ms, int offset) {
    if (auto* el = find_typed_element<Message>(hwnd, element_id)) {
        el->set_options(message_type, closable != 0, center != 0, rich != 0, duration_ms, offset);
    }
}

void __stdcall EU_SetMessageClosed(HWND hwnd, int element_id, int closed) {
    if (auto* el = find_typed_element<Message>(hwnd, element_id)) {
        el->set_closed(closed != 0);
    }
}

int __stdcall EU_GetMessageOptions(HWND hwnd, int element_id, int* message_type,
                                   int* closable, int* center, int* rich,
                                   int* duration_ms, int* closed, int* offset) {
    auto* el = find_typed_element<Message>(hwnd, element_id);
    if (!el) return 0;
    if (message_type) *message_type = el->message_type;
    if (closable) *closable = el->closable ? 1 : 0;
    if (center) *center = el->center ? 1 : 0;
    if (rich) *rich = el->rich ? 1 : 0;
    if (duration_ms) *duration_ms = el->duration_ms;
    if (closed) *closed = el->closed ? 1 : 0;
    if (offset) *offset = el->offset;
    return 1;
}

int __stdcall EU_GetMessageFullState(HWND hwnd, int element_id, int* message_type,
                                     int* closable, int* center, int* rich,
                                     int* duration_ms, int* closed,
                                     int* close_hover, int* close_down,
                                     int* close_count, int* last_action,
                                     int* timer_elapsed_ms, int* timer_running,
                                     int* stack_index, int* stack_gap, int* offset) {
    auto* el = find_typed_element<Message>(hwnd, element_id);
    if (!el) return 0;
    if (message_type) *message_type = el->message_type;
    if (closable) *closable = el->closable ? 1 : 0;
    if (center) *center = el->center ? 1 : 0;
    if (rich) *rich = el->rich ? 1 : 0;
    if (duration_ms) *duration_ms = el->duration_ms;
    if (closed) *closed = el->closed ? 1 : 0;
    if (close_hover) *close_hover = el->close_hover() ? 1 : 0;
    if (close_down) *close_down = el->close_down() ? 1 : 0;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (timer_elapsed_ms) *timer_elapsed_ms = el->timer_elapsed_ms;
    if (timer_running) *timer_running = el->timer_running() ? 1 : 0;
    if (stack_index) *stack_index = el->stack_index;
    if (stack_gap) *stack_gap = el->stack_gap;
    if (offset) *offset = el->offset;
    return 1;
}

void __stdcall EU_TriggerMessageClose(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Message>(hwnd, element_id)) {
        el->close_message(4);
    }
}

void __stdcall EU_SetMessageCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Message>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetNotificationBody(HWND hwnd, int element_id,
                                      const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_body(utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetNotificationType(HWND hwnd, int element_id, int notify_type) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_type(notify_type);
    }
}

void __stdcall EU_SetNotificationClosable(HWND hwnd, int element_id, int closable) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_closable(closable != 0);
    }
}

void __stdcall EU_SetNotificationPlacement(HWND hwnd, int element_id, int placement, int offset) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_placement(placement, offset);
    }
}

void __stdcall EU_SetNotificationRichMode(HWND hwnd, int element_id, int rich) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_rich(rich != 0);
    }
}

void __stdcall EU_SetNotificationOptions(HWND hwnd, int element_id,
                                         int notify_type, int closable, int duration_ms) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_options(notify_type, closable != 0, duration_ms);
    }
}

void __stdcall EU_SetNotificationClosed(HWND hwnd, int element_id, int closed) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_closed(closed != 0);
    }
}

int __stdcall EU_GetNotificationClosed(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Notification>(hwnd, element_id);
    return el ? (el->closed ? 1 : 0) : 0;
}

int __stdcall EU_GetNotificationOptions(HWND hwnd, int element_id,
                                        int* notify_type, int* closable,
                                        int* duration_ms, int* closed) {
    auto* el = find_typed_element<Notification>(hwnd, element_id);
    if (!el) return 0;
    if (notify_type) *notify_type = el->notify_type;
    if (closable) *closable = el->closable ? 1 : 0;
    if (duration_ms) *duration_ms = el->duration_ms;
    if (closed) *closed = el->closed ? 1 : 0;
    return 1;
}

void __stdcall EU_SetNotificationStack(HWND hwnd, int element_id, int stack_index, int stack_gap) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->set_stack(stack_index, stack_gap);
    }
}

void __stdcall EU_TriggerNotificationClose(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->close_notification(4);
    }
}

int __stdcall EU_GetNotificationText(HWND hwnd, int element_id, int text_kind,
                                     unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Notification>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(text_kind == 1 ? el->body : el->text, buffer, buffer_size);
}

int __stdcall EU_GetNotificationFullState(HWND hwnd, int element_id,
                                          int* notify_type, int* closable,
                                          int* duration_ms, int* closed,
                                          int* close_hover, int* close_down,
                                          int* close_count, int* last_action,
                                          int* timer_elapsed_ms, int* timer_running,
                                          int* stack_index, int* stack_gap) {
    auto* el = find_typed_element<Notification>(hwnd, element_id);
    if (!el) return 0;
    if (notify_type) *notify_type = el->notify_type;
    if (closable) *closable = el->closable ? 1 : 0;
    if (duration_ms) *duration_ms = el->duration_ms;
    if (closed) *closed = el->closed ? 1 : 0;
    if (close_hover) *close_hover = el->close_hover() ? 1 : 0;
    if (close_down) *close_down = el->close_down() ? 1 : 0;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (timer_elapsed_ms) *timer_elapsed_ms = el->timer_elapsed_ms;
    if (timer_running) *timer_running = el->timer_running() ? 1 : 0;
    if (stack_index) *stack_index = el->stack_index;
    if (stack_gap) *stack_gap = el->stack_gap;
    return 1;
}

int __stdcall EU_GetNotificationFullStateEx(HWND hwnd, int element_id,
                                            int* notify_type, int* closable,
                                            int* duration_ms, int* closed,
                                            int* close_hover, int* close_down,
                                            int* close_count, int* last_action,
                                            int* timer_elapsed_ms, int* timer_running,
                                            int* stack_index, int* stack_gap,
                                            int* placement, int* offset, int* rich) {
    auto* el = find_typed_element<Notification>(hwnd, element_id);
    if (!el) return 0;
    EU_GetNotificationFullState(hwnd, element_id, notify_type, closable, duration_ms, closed,
                                close_hover, close_down, close_count, last_action,
                                timer_elapsed_ms, timer_running, stack_index, stack_gap);
    if (placement) *placement = el->placement;
    if (offset) *offset = el->offset;
    if (rich) *rich = el->rich ? 1 : 0;
    return 1;
}

void __stdcall EU_SetNotificationCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Notification>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetLoadingActive(HWND hwnd, int element_id, int active) {
    if (auto* el = find_typed_element<Loading>(hwnd, element_id)) {
        el->set_active(active != 0);
    }
}

void __stdcall EU_SetLoadingText(HWND hwnd, int element_id,
                                 const unsigned char* text_bytes, int text_len) {
    if (auto* el = find_typed_element<Loading>(hwnd, element_id)) {
        el->text = utf8_to_wide(text_bytes, text_len);
        el->invalidate();
    }
}

void __stdcall EU_SetLoadingOptions(HWND hwnd, int element_id,
                                    int active, int fullscreen, int progress) {
    if (auto* el = find_typed_element<Loading>(hwnd, element_id)) {
        el->set_options(active != 0, fullscreen != 0, progress);
        if (fullscreen != 0 && !el->lock_input) {
            el->set_style(el->overlay_color, el->spinner_color, el->text_color,
                          el->spinner_type, true);
        }
        relayout_and_invalidate(hwnd);
    }
}

void __stdcall EU_SetLoadingStyle(HWND hwnd, int element_id,
                                  Color background, Color spinner_color,
                                  Color text_color, int spinner_type,
                                  int lock_input) {
    if (auto* el = find_typed_element<Loading>(hwnd, element_id)) {
        el->set_style(background, spinner_color, text_color, spinner_type, lock_input != 0);
    }
}

int __stdcall EU_GetLoadingActive(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    return el ? (el->active ? 1 : 0) : 0;
}

int __stdcall EU_GetLoadingOptions(HWND hwnd, int element_id,
                                   int* active, int* fullscreen, int* progress) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    if (!el) return 0;
    if (active) *active = el->active ? 1 : 0;
    if (fullscreen) *fullscreen = el->fullscreen ? 1 : 0;
    if (progress) *progress = el->progress;
    return 1;
}

int __stdcall EU_GetLoadingStyle(HWND hwnd, int element_id,
                                 Color* background, Color* spinner_color,
                                 Color* text_color, int* spinner_type,
                                 int* lock_input) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    if (!el) return 0;
    if (background) *background = el->overlay_color;
    if (spinner_color) *spinner_color = el->spinner_color;
    if (text_color) *text_color = el->text_color;
    if (spinner_type) *spinner_type = el->spinner_type;
    if (lock_input) *lock_input = el->lock_input ? 1 : 0;
    return 1;
}

void __stdcall EU_SetLoadingTarget(HWND hwnd, int element_id, int target_element_id, int padding) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    WindowState* st = window_state(hwnd);
    if (!el || !st || !st->element_tree) return;
    el->set_target(target_element_id, padding);
    if (target_element_id > 0) {
        Element* target = st->element_tree->find_by_id(target_element_id);
        if (target) {
            Rect r = target->logical_bounds;
            r.x -= el->target_padding;
            r.y -= el->target_padding;
            r.w += el->target_padding * 2;
            r.h += el->target_padding * 2;
            el->set_logical_bounds(r);
            st->element_tree->layout();
        }
    }
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetLoadingText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(el->text, buffer, buffer_size);
}

int __stdcall EU_ShowLoading(HWND hwnd, int target_element_id,
                             const unsigned char* text_bytes, int text_len,
                             int fullscreen, int lock_input,
                             Color background, Color spinner_color,
                             Color text_color, int spinner_type) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;

    Element* parent = st->element_tree->root();
    Rect r = {0, 0, 260, 150};
    if (target_element_id > 0) {
        Element* target = st->element_tree->find_by_id(target_element_id);
        if (target) {
            parent = target->parent ? target->parent : st->element_tree->root();
            r = target->has_logical_bounds ? target->logical_bounds : target->bounds;
        }
    }
    if (fullscreen != 0) parent = st->element_tree->root();

    auto el = std::make_unique<Loading>();
    el->set_logical_bounds(r);
    el->text = utf8_to_wide(text_bytes, text_len);
    el->fullscreen = fullscreen != 0;
    el->service_owned = true;
    el->set_target(target_element_id, 0);
    el->set_style(background, spinner_color, text_color, spinner_type,
                  lock_input != 0 || fullscreen != 0);
    el->set_active(true);

    ElementStyle logical_style = el->style;
    logical_style.bg_color = 0;
    logical_style.border_color = 0;
    logical_style.fg_color = 0;
    logical_style.font_size = 14.0f;
    logical_style.pad_left = 12;
    logical_style.pad_top = 12;
    logical_style.pad_right = 12;
    logical_style.pad_bottom = 12;
    el->set_logical_style(logical_style);

    Element* raw = st->element_tree->add_child(parent, std::move(el));
    st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return raw->id;
}

int __stdcall EU_CloseLoading(HWND hwnd, int loading_id) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return 0;
    auto* el = find_typed_element<Loading>(hwnd, loading_id);
    if (!el) return 0;
    el->set_active(false);
    if (el->service_owned && el->parent) {
        st->element_tree->remove_child(el);
        InvalidateRect(hwnd, nullptr, FALSE);
        return 1;
    }
    el->visible = false;
    InvalidateRect(hwnd, nullptr, FALSE);
    return 1;
}

int __stdcall EU_GetLoadingFullState(HWND hwnd, int element_id,
                                     int* active, int* fullscreen, int* progress,
                                     int* target_element_id, int* target_padding,
                                     int* animation_angle, int* tick_count,
                                     int* timer_running, int* last_action) {
    auto* el = find_typed_element<Loading>(hwnd, element_id);
    if (!el) return 0;
    if (active) *active = el->active ? 1 : 0;
    if (fullscreen) *fullscreen = el->fullscreen ? 1 : 0;
    if (progress) *progress = el->progress;
    if (target_element_id) *target_element_id = el->target_id;
    if (target_padding) *target_padding = el->target_padding;
    if (animation_angle) *animation_angle = el->animation_angle;
    if (tick_count) *tick_count = el->tick_count;
    if (timer_running) *timer_running = el->timer_running() ? 1 : 0;
    if (last_action) *last_action = el->last_action;
    return 1;
}

void __stdcall EU_SetDialogOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_open(open != 0);
        relayout_and_invalidate(hwnd);
    }
}

void __stdcall EU_SetDialogTitle(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
    }
}

void __stdcall EU_SetDialogBody(HWND hwnd, int element_id,
                                const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_body(utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetDialogOptions(HWND hwnd, int element_id, int open, int modal,
                                   int closable, int close_on_mask, int draggable,
                                   int w, int h) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_options(open != 0, modal != 0, closable != 0,
                        close_on_mask != 0, draggable != 0, w, h);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

void __stdcall EU_SetDialogAdvancedOptions(HWND hwnd, int element_id,
                                           int width_mode, int width_value,
                                           int center, int footer_center,
                                           int content_padding, int footer_height) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_advanced_options(width_mode, width_value, center != 0, footer_center != 0,
                                 content_padding, footer_height);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetDialogAdvancedOptions(HWND hwnd, int element_id,
                                          int* width_mode, int* width_value,
                                          int* center, int* footer_center,
                                          int* content_padding, int* footer_height,
                                          int* content_parent_id, int* footer_parent_id,
                                          int* close_pending) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    if (!el) return 0;
    if (width_mode) *width_mode = el->width_mode;
    if (width_value) *width_value = el->width_value;
    if (center) *center = el->center ? 1 : 0;
    if (footer_center) *footer_center = el->footer_center ? 1 : 0;
    if (content_padding) *content_padding = el->content_padding;
    if (footer_height) *footer_height = el->footer_height;
    if (content_parent_id) *content_parent_id = el->content_parent_id;
    if (footer_parent_id) *footer_parent_id = el->footer_parent_id;
    if (close_pending) *close_pending = el->close_pending ? 1 : 0;
    return 1;
}

int __stdcall EU_GetDialogContentParent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    return el ? el->content_parent_id : 0;
}

int __stdcall EU_GetDialogFooterParent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    return el ? el->footer_parent_id : 0;
}

void __stdcall EU_SetDialogBeforeCloseCallback(HWND hwnd, int element_id,
                                               ElementBeforeCloseCallback cb) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->before_close_cb = cb;
    }
}

void __stdcall EU_ConfirmDialogClose(HWND hwnd, int element_id, int allow) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->confirm_pending_close(allow != 0);
        relayout_and_invalidate(hwnd);
    }
}

int __stdcall EU_GetDialogOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    return el && el->is_open() ? 1 : 0;
}

int __stdcall EU_GetDialogOptions(HWND hwnd, int element_id,
                                  int* open, int* modal, int* closable,
                                  int* close_on_mask, int* draggable,
                                  int* w, int* h) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    if (!el) return 0;
    if (open) *open = el->is_open() ? 1 : 0;
    if (modal) *modal = el->modal ? 1 : 0;
    if (closable) *closable = el->closable ? 1 : 0;
    if (close_on_mask) *close_on_mask = el->close_on_mask ? 1 : 0;
    if (draggable) *draggable = el->draggable ? 1 : 0;
    if (w) *w = el->logical_bounds.w;
    if (h) *h = el->logical_bounds.h;
    return 1;
}

void __stdcall EU_SetDialogButtons(HWND hwnd, int element_id,
                                   const unsigned char* buttons_bytes, int buttons_len) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->set_buttons(split_option_list(buttons_bytes, buttons_len));
    }
}

void __stdcall EU_TriggerDialogButton(HWND hwnd, int element_id, int button_index) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->trigger_button(button_index, 4);
    }
}

int __stdcall EU_GetDialogText(HWND hwnd, int element_id, int text_kind,
                               unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(text_kind == 1 ? el->text : el->title, buffer, buffer_size);
}

int __stdcall EU_GetDialogButtonText(HWND hwnd, int element_id, int button_index,
                                     unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    if (!el || button_index < 0 || button_index >= (int)el->buttons.size()) return 0;
    return copy_wide_as_utf8(el->buttons[(size_t)button_index], buffer, buffer_size);
}

int __stdcall EU_GetDialogFullState(HWND hwnd, int element_id,
                                    int* open, int* modal, int* closable,
                                    int* close_on_mask, int* draggable,
                                    int* w, int* h, int* button_count,
                                    int* active_button, int* last_button,
                                    int* button_click_count, int* close_count,
                                    int* last_action, int* offset_x, int* offset_y,
                                    int* hover_part, int* press_part) {
    auto* el = find_typed_element<Dialog>(hwnd, element_id);
    if (!el) return 0;
    if (open) *open = el->is_open() ? 1 : 0;
    if (modal) *modal = el->modal ? 1 : 0;
    if (closable) *closable = el->closable ? 1 : 0;
    if (close_on_mask) *close_on_mask = el->close_on_mask ? 1 : 0;
    if (draggable) *draggable = el->draggable ? 1 : 0;
    if (w) *w = el->logical_bounds.w;
    if (h) *h = el->logical_bounds.h;
    if (button_count) *button_count = (int)el->buttons.size();
    if (active_button) *active_button = el->active_button;
    if (last_button) *last_button = el->last_button;
    if (button_click_count) *button_click_count = el->button_click_count;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (offset_x) *offset_x = el->offset_x();
    if (offset_y) *offset_y = el->offset_y();
    if (hover_part) *hover_part = el->hover_part();
    if (press_part) *press_part = el->press_part();
    return 1;
}

void __stdcall EU_SetDialogButtonCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Dialog>(hwnd, element_id)) {
        el->button_cb = cb;
    }
}

void __stdcall EU_SetDrawerOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_open(open != 0);
        relayout_and_invalidate(hwnd);
    }
}

void __stdcall EU_SetDrawerTitle(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
    }
}

void __stdcall EU_SetDrawerBody(HWND hwnd, int element_id,
                                const unsigned char* body_bytes, int body_len) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_body(utf8_to_wide(body_bytes, body_len));
    }
}

void __stdcall EU_SetDrawerPlacement(HWND hwnd, int element_id, int placement) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_placement(placement);
        relayout_and_invalidate(hwnd);
    }
}

void __stdcall EU_SetDrawerOptions(HWND hwnd, int element_id, int placement, int open,
                                   int modal, int closable, int close_on_mask, int size) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_options(placement, open != 0, modal != 0, closable != 0,
                        close_on_mask != 0, size);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

void __stdcall EU_SetDrawerAdvancedOptions(HWND hwnd, int element_id,
                                           int show_header, int show_close,
                                           int close_on_escape, int content_padding,
                                           int footer_height, int size_mode,
                                           int size_value) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_advanced_options(show_header != 0, show_close != 0,
                                 close_on_escape != 0, content_padding,
                                 footer_height, size_mode, size_value);
        el->apply_dpi_scale(st->dpi_scale);
        st->element_tree->layout();
        InvalidateRect(hwnd, nullptr, FALSE);
    }
}

int __stdcall EU_GetDrawerAdvancedOptions(HWND hwnd, int element_id,
                                          int* show_header, int* show_close,
                                          int* close_on_escape, int* content_padding,
                                          int* footer_height, int* size_mode,
                                          int* size_value, int* content_parent_id,
                                          int* footer_parent_id, int* close_pending) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    if (!el) return 0;
    if (show_header) *show_header = el->show_header ? 1 : 0;
    if (show_close) *show_close = el->show_close ? 1 : 0;
    if (close_on_escape) *close_on_escape = el->close_on_escape ? 1 : 0;
    if (content_padding) *content_padding = el->content_padding;
    if (footer_height) *footer_height = el->footer_height;
    if (size_mode) *size_mode = el->size_mode;
    if (size_value) *size_value = el->size_value > 0
        ? el->size_value
        : ((el->placement == 0 || el->placement == 1)
            ? el->logical_bounds.w : el->logical_bounds.h);
    if (content_parent_id) *content_parent_id = el->content_parent_id;
    if (footer_parent_id) *footer_parent_id = el->footer_parent_id;
    if (close_pending) *close_pending = el->close_pending ? 1 : 0;
    return 1;
}

int __stdcall EU_GetDrawerContentParent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    return el ? el->content_parent_id : 0;
}

int __stdcall EU_GetDrawerFooterParent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    return el ? el->footer_parent_id : 0;
}

void __stdcall EU_SetDrawerBeforeCloseCallback(HWND hwnd, int element_id,
                                               ElementBeforeCloseCallback cb) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->before_close_cb = cb;
    }
}

void __stdcall EU_ConfirmDrawerClose(HWND hwnd, int element_id, int allow) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->confirm_pending_close(allow != 0);
        relayout_and_invalidate(hwnd);
    }
}

int __stdcall EU_GetDrawerOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    return el && el->is_open() ? 1 : 0;
}

int __stdcall EU_GetDrawerOptions(HWND hwnd, int element_id,
                                  int* placement, int* open, int* modal,
                                  int* closable, int* close_on_mask, int* size) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (modal) *modal = el->modal ? 1 : 0;
    if (closable) *closable = el->closable ? 1 : 0;
    if (close_on_mask) *close_on_mask = el->close_on_mask ? 1 : 0;
    if (size) *size = (el->placement == 0 || el->placement == 1)
        ? el->logical_bounds.w
        : el->logical_bounds.h;
    return 1;
}

void __stdcall EU_SetDrawerAnimation(HWND hwnd, int element_id, int duration_ms) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->set_animation(duration_ms);
    }
}

void __stdcall EU_TriggerDrawerClose(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->close_drawer(4);
    }
}

int __stdcall EU_GetDrawerText(HWND hwnd, int element_id, int text_kind,
                               unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(text_kind == 1 ? el->text : el->title, buffer, buffer_size);
}

int __stdcall EU_GetDrawerFullState(HWND hwnd, int element_id,
                                    int* placement, int* open, int* modal,
                                    int* closable, int* close_on_mask, int* size,
                                    int* animation_progress, int* animation_ms,
                                    int* tick_count, int* timer_running,
                                    int* close_count, int* last_action,
                                    int* hover_part, int* press_part) {
    auto* el = find_typed_element<Drawer>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (modal) *modal = el->modal ? 1 : 0;
    if (closable) *closable = el->closable ? 1 : 0;
    if (close_on_mask) *close_on_mask = el->close_on_mask ? 1 : 0;
    if (size) *size = (el->placement == 0 || el->placement == 1)
        ? el->logical_bounds.w
        : el->logical_bounds.h;
    if (animation_progress) *animation_progress = el->animation_progress;
    if (animation_ms) *animation_ms = el->animation_ms;
    if (tick_count) *tick_count = el->tick_count;
    if (timer_running) *timer_running = el->timer_running() ? 1 : 0;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (hover_part) *hover_part = el->hover_part();
    if (press_part) *press_part = el->press_part();
    return 1;
}

void __stdcall EU_SetDrawerCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Drawer>(hwnd, element_id)) {
        el->close_cb = cb;
    }
}

void __stdcall EU_SetTooltipContent(HWND hwnd, int element_id,
                                    const unsigned char* content_bytes, int content_len) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->set_content(utf8_to_wide(content_bytes, content_len));
    }
}

void __stdcall EU_SetTooltipOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetTooltipOptions(HWND hwnd, int element_id, int placement, int open, int max_width) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->set_options(placement, open, max_width);
    }
}

int __stdcall EU_GetTooltipOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Tooltip>(hwnd, element_id);
    return el && el->is_open() ? 1 : 0;
}

int __stdcall EU_GetTooltipOptions(HWND hwnd, int element_id,
                                   int* placement, int* open, int* max_width) {
    auto* el = find_typed_element<Tooltip>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (max_width) *max_width = el->max_width();
    return 1;
}

void __stdcall EU_SetTooltipBehavior(HWND hwnd, int element_id,
                                     int show_delay, int hide_delay,
                                     int trigger_mode, int show_arrow) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->set_behavior(show_delay, hide_delay, trigger_mode, show_arrow);
    }
}

void __stdcall EU_SetTooltipAdvancedOptions(HWND hwnd, int element_id,
                                            int placement, int effect,
                                            int disabled, int show_arrow,
                                            int offset, int max_width) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->set_advanced_options(placement, effect, disabled, show_arrow, offset, max_width);
    }
}

int __stdcall EU_GetTooltipAdvancedOptions(HWND hwnd, int element_id,
                                           int* placement, int* effect,
                                           int* disabled, int* show_arrow,
                                           int* offset, int* max_width) {
    auto* el = find_typed_element<Tooltip>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->use_advanced_placement ? el->advanced_placement : -1;
    if (effect) *effect = el->effect;
    if (disabled) *disabled = el->tooltip_disabled ? 1 : 0;
    if (show_arrow) *show_arrow = el->show_arrow ? 1 : 0;
    if (offset) *offset = el->offset;
    if (max_width) *max_width = el->max_width();
    return 1;
}

void __stdcall EU_TriggerTooltip(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Tooltip>(hwnd, element_id)) {
        el->trigger_open(open != 0, 5);
    }
}

int __stdcall EU_GetTooltipText(HWND hwnd, int element_id, int text_kind,
                                unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Tooltip>(hwnd, element_id);
    if (!el) return 0;
    return copy_wide_as_utf8(text_kind == 1 ? el->content : el->text, buffer, buffer_size);
}

int __stdcall EU_GetTooltipFullState(HWND hwnd, int element_id,
                                     int* placement, int* open, int* max_width,
                                     int* show_arrow, int* show_delay,
                                     int* hide_delay, int* trigger_mode,
                                     int* timer_running, int* timer_phase,
                                     int* open_count, int* close_count,
                                     int* last_action, int* popup_x,
                                     int* popup_y, int* popup_w, int* popup_h) {
    auto* el = find_typed_element<Tooltip>(hwnd, element_id);
    if (!el) return 0;
    Rect popup = el->popup_rect();
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (max_width) *max_width = el->max_width();
    if (show_arrow) *show_arrow = el->show_arrow ? 1 : 0;
    if (show_delay) *show_delay = el->show_delay_ms;
    if (hide_delay) *hide_delay = el->hide_delay_ms;
    if (trigger_mode) *trigger_mode = el->trigger_mode;
    if (timer_running) *timer_running = el->timer_running() ? 1 : 0;
    if (timer_phase) *timer_phase = el->timer_phase();
    if (open_count) *open_count = el->open_count;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (popup_x) *popup_x = popup.x;
    if (popup_y) *popup_y = popup.y;
    if (popup_w) *popup_w = popup.w;
    if (popup_h) *popup_h = popup.h;
    return 1;
}

void __stdcall EU_SetPopoverOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetPopoverContent(HWND hwnd, int element_id,
                                    const unsigned char* content_bytes, int content_len) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->set_content(utf8_to_wide(content_bytes, content_len));
    }
}

void __stdcall EU_SetPopoverTitle(HWND hwnd, int element_id,
                                  const unsigned char* title_bytes, int title_len) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
    }
}

void __stdcall EU_SetPopoverOptions(HWND hwnd, int element_id, int placement, int open,
                                    int popup_width, int popup_height, int closable) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->set_options(placement, open, popup_width, popup_height, closable);
    }
}

void __stdcall EU_SetPopoverAdvancedOptions(HWND hwnd, int element_id,
                                            int placement, int open,
                                            int popup_width, int popup_height,
                                            int closable) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        if (placement < 0) placement = 0;
        if (placement > 11) placement = 11;
        el->advanced_placement = placement;
        el->use_advanced_placement = true;
        el->popup_width = popup_width > 120 ? popup_width : 250;
        el->popup_height = popup_height > 80 ? popup_height : 132;
        el->close_enabled = closable != 0;
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetPopoverBehavior(HWND hwnd, int element_id,
                                     int trigger_mode, int close_on_outside,
                                     int show_arrow, int offset) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->set_behavior(trigger_mode, close_on_outside, show_arrow, offset);
    }
}

int __stdcall EU_GetPopoverBehavior(HWND hwnd, int element_id,
                                    int* trigger_mode, int* close_on_outside,
                                    int* show_arrow, int* offset) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    if (!el) return 0;
    if (trigger_mode) *trigger_mode = el->trigger_mode;
    if (close_on_outside) *close_on_outside = el->close_on_outside ? 1 : 0;
    if (show_arrow) *show_arrow = el->show_arrow ? 1 : 0;
    if (offset) *offset = el->offset;
    return 1;
}

int __stdcall EU_GetPopoverContentParent(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    return el ? el->content_parent_id : 0;
}

int __stdcall EU_GetPopoverOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    return el && el->is_open() ? 1 : 0;
}

int __stdcall EU_GetPopoverOptions(HWND hwnd, int element_id,
                                   int* placement, int* open,
                                   int* popup_width, int* popup_height, int* closable) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (popup_width) *popup_width = el->popup_width;
    if (popup_height) *popup_height = el->popup_height;
    if (closable) *closable = el->close_enabled ? 1 : 0;
    return 1;
}

void __stdcall EU_TriggerPopover(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->trigger_open(open != 0, 5);
    }
}

int __stdcall EU_GetPopoverText(HWND hwnd, int element_id, int text_kind,
                                unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    if (!el) return 0;
    const std::wstring& value = text_kind == 1 ? el->title : (text_kind == 2 ? el->content : el->text);
    return copy_wide_as_utf8(value, buffer, buffer_size);
}

int __stdcall EU_GetPopoverFullState(HWND hwnd, int element_id,
                                     int* placement, int* open,
                                     int* popup_width, int* popup_height,
                                     int* closable, int* open_count,
                                     int* close_count, int* last_action,
                                     int* focus_part, int* close_hover,
                                     int* popup_x, int* popup_y,
                                     int* popup_w, int* popup_h) {
    auto* el = find_typed_element<Popover>(hwnd, element_id);
    if (!el) return 0;
    Rect popup = el->get_popup_rect();
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (popup_width) *popup_width = el->popup_width;
    if (popup_height) *popup_height = el->popup_height;
    if (closable) *closable = el->close_enabled ? 1 : 0;
    if (open_count) *open_count = el->open_count;
    if (close_count) *close_count = el->close_count;
    if (last_action) *last_action = el->last_action;
    if (focus_part) *focus_part = el->focus_part;
    if (close_hover) *close_hover = el->close_hot() ? 1 : 0;
    if (popup_x) *popup_x = popup.x;
    if (popup_y) *popup_y = popup.y;
    if (popup_w) *popup_w = popup.w;
    if (popup_h) *popup_h = popup.h;
    return 1;
}

void __stdcall EU_SetPopoverActionCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Popover>(hwnd, element_id)) {
        el->action_cb = cb;
    }
}

void __stdcall EU_SetPopconfirmOpen(HWND hwnd, int element_id, int open) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetPopconfirmOptions(HWND hwnd, int element_id, int placement, int open,
                                       int popup_width, int popup_height) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->set_options(placement, open, popup_width, popup_height, 0);
    }
}

void __stdcall EU_SetPopconfirmAdvancedOptions(HWND hwnd, int element_id,
                                               int placement, int open,
                                               int popup_width, int popup_height,
                                               int trigger_mode, int close_on_outside,
                                               int show_arrow, int offset) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        if (placement < 0) placement = 0;
        if (placement > 11) placement = 11;
        el->advanced_placement = placement;
        el->use_advanced_placement = true;
        el->popup_width = popup_width > 120 ? popup_width : 286;
        el->popup_height = popup_height > 80 ? popup_height : 146;
        el->set_behavior(trigger_mode, close_on_outside, show_arrow, offset);
        el->set_open(open != 0);
    }
}

void __stdcall EU_SetPopconfirmContent(HWND hwnd, int element_id,
                                       const unsigned char* title_bytes, int title_len,
                                       const unsigned char* content_bytes, int content_len) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->set_title(utf8_to_wide(title_bytes, title_len));
        el->set_content(utf8_to_wide(content_bytes, content_len));
    }
}

void __stdcall EU_SetPopconfirmButtons(HWND hwnd, int element_id,
                                       const unsigned char* confirm_bytes, int confirm_len,
                                       const unsigned char* cancel_bytes, int cancel_len) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->set_buttons(utf8_or_default(confirm_bytes, confirm_len, L"确定"),
                        utf8_or_default(cancel_bytes, cancel_len, L"取消"));
    }
}

void __stdcall EU_SetPopconfirmIcon(HWND hwnd, int element_id,
                                    const unsigned char* icon_bytes, int icon_len,
                                    Color icon_color, int visible) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->set_icon(utf8_or_default(icon_bytes, icon_len, L"!"), icon_color, visible != 0);
    }
}

int __stdcall EU_GetPopconfirmIcon(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size,
                                   Color* icon_color, int* visible) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    if (!el) return 0;
    if (icon_color) *icon_color = el->icon_color;
    if (visible) *visible = el->show_icon ? 1 : 0;
    return copy_wide_as_utf8(el->icon_text, buffer, buffer_size);
}

void __stdcall EU_ResetPopconfirmResult(HWND hwnd, int element_id) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->reset_result();
    }
}

int __stdcall EU_GetPopconfirmOpen(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    return el && el->is_open() ? 1 : 0;
}

int __stdcall EU_GetPopconfirmResult(HWND hwnd, int element_id) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    return el ? el->get_last_result() : -1;
}

int __stdcall EU_GetPopconfirmOptions(HWND hwnd, int element_id,
                                      int* placement, int* open,
                                      int* popup_width, int* popup_height, int* result) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    if (!el) return 0;
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (popup_width) *popup_width = el->popup_width;
    if (popup_height) *popup_height = el->popup_height;
    if (result) *result = el->get_last_result();
    return 1;
}

void __stdcall EU_TriggerPopconfirmResult(HWND hwnd, int element_id, int result) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->choose_result(result != 0 ? 1 : 0, 4);
    }
}

int __stdcall EU_GetPopconfirmText(HWND hwnd, int element_id, int text_kind,
                                   unsigned char* buffer, int buffer_size) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    if (!el) return 0;
    const std::wstring& value =
        text_kind == 1 ? el->title :
        text_kind == 2 ? el->content :
        text_kind == 3 ? el->confirm_text :
        text_kind == 4 ? el->cancel_text : el->text;
    return copy_wide_as_utf8(value, buffer, buffer_size);
}

int __stdcall EU_GetPopconfirmFullState(HWND hwnd, int element_id,
                                        int* placement, int* open,
                                        int* popup_width, int* popup_height,
                                        int* result, int* confirm_count,
                                        int* cancel_count, int* result_action,
                                        int* focus_part, int* hover_button,
                                        int* press_button, int* popup_x,
                                        int* popup_y, int* popup_w, int* popup_h) {
    auto* el = find_typed_element<Popconfirm>(hwnd, element_id);
    if (!el) return 0;
    Rect popup = el->get_popup_rect();
    if (placement) *placement = el->placement;
    if (open) *open = el->is_open() ? 1 : 0;
    if (popup_width) *popup_width = el->popup_width;
    if (popup_height) *popup_height = el->popup_height;
    if (result) *result = el->get_last_result();
    if (confirm_count) *confirm_count = el->confirm_count;
    if (cancel_count) *cancel_count = el->cancel_count;
    if (result_action) *result_action = el->result_action;
    if (focus_part) *focus_part = el->focus_part;
    if (hover_button) *hover_button = el->hover_button_part();
    if (press_button) *press_button = el->press_button_part();
    if (popup_x) *popup_x = popup.x;
    if (popup_y) *popup_y = popup.y;
    if (popup_w) *popup_w = popup.w;
    if (popup_h) *popup_h = popup.h;
    return 1;
}

void __stdcall EU_SetPopconfirmResultCallback(HWND hwnd, int element_id, ElementValueCallback cb) {
    if (auto* el = find_typed_element<Popconfirm>(hwnd, element_id)) {
        el->result_cb = cb;
    }
}

// ── Callbacks ────────────────────────────────────────────────────────

void __stdcall EU_SetElementClickCallback(HWND hwnd, int element_id, ElementClickCallback cb) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) el->click_cb = cb;
}

void __stdcall EU_SetElementKeyCallback(HWND hwnd, int element_id, ElementKeyCallback cb) {
    WindowState* st = window_state(hwnd);
    if (!st || !st->element_tree) return;
    Element* el = st->element_tree->find_by_id(element_id);
    if (el) el->key_cb = cb;
}

void __stdcall EU_SetWindowResizeCallback(HWND hwnd, WindowResizeCallback cb) {
    WindowState* st = window_state(hwnd);
    if (st) st->resize_cb = cb;
}

void __stdcall EU_SetWindowCloseCallback(HWND hwnd, WindowCloseCallback cb) {
    WindowState* st = window_state(hwnd);
    if (st) st->close_cb = cb;
}

// ── Theme ────────────────────────────────────────────────────────────

void __stdcall EU_SetDarkMode(HWND hwnd, int dark_mode) {
    EU_SetThemeMode(hwnd, dark_mode ? THEME_MODE_DARK : THEME_MODE_LIGHT);
}

void __stdcall EU_SetThemeMode(HWND hwnd, int mode) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    set_window_theme_mode(hwnd, mode);
    if (st->element_tree) st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}

int __stdcall EU_GetThemeMode(HWND hwnd) {
    return get_window_theme_mode(hwnd);
}

int __stdcall EU_SetThemeColor(HWND hwnd, const unsigned char* token_bytes, int token_len, Color value) {
    WindowState* st = window_state(hwnd);
    if (!st || !token_bytes || token_len <= 0) return 0;
    std::string token(reinterpret_cast<const char*>(token_bytes),
                      token_len);
    if (!set_window_theme_color(hwnd, token, value)) return 0;
    if (st->element_tree) st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
    return 1;
}

void __stdcall EU_ResetTheme(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    reset_window_theme(hwnd);
    if (st->element_tree) st->element_tree->layout();
    InvalidateRect(hwnd, nullptr, FALSE);
}
