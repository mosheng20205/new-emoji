#include "element_rich_text.h"
#include "emoji_fallback.h"
#include <algorithm>
#include <cwctype>
#include <vector>

struct RichRun {
    std::wstring text;
    Color color = 0;
    bool bold = false;
    bool italic = false;
};

static std::wstring lower_ascii(std::wstring s) {
    for (auto& ch : s) {
        if (ch >= L'A' && ch <= L'Z') ch = ch - L'A' + L'a';
    }
    return s;
}

static bool starts_with(const std::wstring& s, const wchar_t* prefix) {
    return s.rfind(prefix, 0) == 0;
}

static Color parse_color_token(const std::wstring& value, Color fallback) {
    std::wstring v = lower_ascii(value);
    v.erase(std::remove_if(v.begin(), v.end(), [](wchar_t ch) {
        return iswspace(ch) != 0;
    }), v.end());
    if (v == L"teal") return 0xFF008080;
    if (v == L"red") return 0xFFF56C6C;
    if (v == L"green") return 0xFF67C23A;
    if (v == L"orange") return 0xFFE6A23C;
    if (v == L"blue") return 0xFF409EFF;
    if (v.size() == 7 && v[0] == L'#') {
        unsigned value = 0;
        for (int i = 1; i < 7; ++i) {
            wchar_t c = v[i];
            value <<= 4;
            if (c >= L'0' && c <= L'9') value += (unsigned)(c - L'0');
            else if (c >= L'a' && c <= L'f') value += (unsigned)(c - L'a' + 10);
            else return fallback;
        }
        return 0xFF000000 | value;
    }
    return fallback;
}

static Color parse_span_color(const std::wstring& tag, Color fallback) {
    std::wstring t = lower_ascii(tag);
    size_t color_pos = t.find(L"color");
    if (color_pos == std::wstring::npos) return fallback;
    size_t colon = t.find(L':', color_pos);
    if (colon == std::wstring::npos) return fallback;
    size_t end = t.find_first_of(L";'\"", colon + 1);
    std::wstring value = tag.substr(colon + 1, end == std::wstring::npos ? end : end - colon - 1);
    return parse_color_token(value, fallback);
}

static void append_entity(std::wstring& out, const std::wstring& e) {
    std::wstring v = lower_ascii(e);
    if (v == L"amp") out.push_back(L'&');
    else if (v == L"lt") out.push_back(L'<');
    else if (v == L"gt") out.push_back(L'>');
    else if (v == L"quot") out.push_back(L'"');
    else if (v == L"apos") out.push_back(L'\'');
    else {
        out.push_back(L'&');
        out.append(e);
        out.push_back(L';');
    }
}

static std::vector<RichRun> parse_rich_runs(const std::wstring& input, Color color, bool rich) {
    std::vector<RichRun> runs;
    RichRun cur;
    cur.color = color;
    if (!rich) {
        cur.text = input;
        runs.push_back(cur);
        return runs;
    }

    std::vector<RichRun> stack;
    auto flush = [&]() {
        if (!cur.text.empty()) {
            runs.push_back(cur);
            cur.text.clear();
        }
    };

    for (size_t i = 0; i < input.size();) {
        if (input[i] == L'&') {
            size_t semi = input.find(L';', i + 1);
            if (semi != std::wstring::npos && semi - i < 12) {
                append_entity(cur.text, input.substr(i + 1, semi - i - 1));
                i = semi + 1;
                continue;
            }
        }
        if (input[i] != L'<') {
            cur.text.push_back(input[i++]);
            continue;
        }

        size_t end = input.find(L'>', i + 1);
        if (end == std::wstring::npos) {
            cur.text.push_back(input[i++]);
            continue;
        }

        std::wstring tag = input.substr(i + 1, end - i - 1);
        std::wstring low = lower_ascii(tag);
        low.erase(0, low.find_first_not_of(L" \t\r\n"));
        bool closing = starts_with(low, L"/");
        if (closing) low.erase(0, 1);

        if (!closing && (starts_with(low, L"strong") || starts_with(low, L"b") ||
                         starts_with(low, L"i") || starts_with(low, L"em") ||
                         starts_with(low, L"span"))) {
            flush();
            stack.push_back(cur);
            if (starts_with(low, L"strong") || starts_with(low, L"b")) cur.bold = true;
            if (starts_with(low, L"i") || starts_with(low, L"em")) cur.italic = true;
            if (starts_with(low, L"span")) cur.color = parse_span_color(tag, cur.color);
        } else if (closing && !stack.empty()) {
            flush();
            cur = stack.back();
            stack.pop_back();
            cur.text.clear();
        } else if (!closing && starts_with(low, L"br")) {
            cur.text.push_back(L'\n');
        }
        i = end + 1;
    }
    flush();
    if (runs.empty()) runs.push_back(cur);
    return runs;
}

std::wstring strip_rich_text_markup(const std::wstring& text, bool rich) {
    auto runs = parse_rich_runs(text, 0xFFFFFFFF, rich);
    std::wstring out;
    for (const auto& run : runs) out += run.text;
    return out;
}

struct DrawRun {
    RichRun run;
    float width = 0.0f;
};

static float measure_run(RenderContext& ctx, const RichRun& run, const ElementStyle& style, float font_scale) {
    if (run.text.empty()) return 0.0f;
    auto* layout = ctx.create_text_layout(run.text, style.font_name, style.font_size * font_scale, 4096.0f,
                                          style.font_size * font_scale * 1.6f);
    if (!layout) return 0.0f;
    apply_emoji_font_fallback(layout, run.text);
    DWRITE_TEXT_RANGE range{ 0, (UINT32)run.text.size() };
    if (run.bold) layout->SetFontWeight(DWRITE_FONT_WEIGHT_SEMI_BOLD, range);
    if (run.italic) layout->SetFontStyle(DWRITE_FONT_STYLE_ITALIC, range);
    DWRITE_TEXT_METRICS metrics{};
    layout->GetMetrics(&metrics);
    layout->Release();
    return metrics.widthIncludingTrailingWhitespace;
}

static void draw_run(RenderContext& ctx, const RichRun& run, const ElementStyle& style,
                     float x, float y, float w, float h, float font_scale) {
    if (run.text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(run.text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, run.text);
    DWRITE_TEXT_RANGE range{ 0, (UINT32)run.text.size() };
    if (run.bold) layout->SetFontWeight(DWRITE_FONT_WEIGHT_SEMI_BOLD, range);
    if (run.italic) layout->SetFontStyle(DWRITE_FONT_STYLE_ITALIC, range);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout, ctx.get_brush(run.color),
        D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void draw_rich_text(RenderContext& ctx,
                    const std::wstring& text,
                    const ElementStyle& style,
                    Color fallback_color,
                    float x, float y, float w, float h,
                    bool rich,
                    DWRITE_TEXT_ALIGNMENT align,
                    bool wrap,
                    float font_scale,
                    bool vertical_center) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto runs = parse_rich_runs(text, fallback_color, rich);
    float line_h = style.font_size * font_scale * 1.45f;
    if (line_h < 16.0f) line_h = 16.0f;

    std::vector<std::vector<DrawRun>> lines(1);
    float current_w = 0.0f;
    for (auto& run : runs) {
        size_t start = 0;
        while (start <= run.text.size()) {
            size_t nl = run.text.find(L'\n', start);
            std::wstring part = run.text.substr(start, nl == std::wstring::npos ? nl : nl - start);
            if (!part.empty()) {
                RichRun r = run;
                r.text = part;
                float rw = measure_run(ctx, r, style, font_scale);
                if (wrap && current_w > 0.0f && current_w + rw > w) {
                    lines.emplace_back();
                    current_w = 0.0f;
                }
                lines.back().push_back({ r, rw });
                current_w += rw;
            }
            if (nl == std::wstring::npos) break;
            lines.emplace_back();
            current_w = 0.0f;
            start = nl + 1;
        }
    }

    float line_y = y;
    float total_h = line_h * (float)lines.size();
    if (vertical_center && total_h < h) {
        line_y = y + (h - total_h) * 0.5f;
    }
    for (const auto& line : lines) {
        if (line_y + line_h > y + h + 0.1f) break;
        float line_w = 0.0f;
        for (const auto& run : line) line_w += run.width;
        float line_x = x;
        if (align == DWRITE_TEXT_ALIGNMENT_CENTER) line_x = x + (w - line_w) * 0.5f;
        else if (align == DWRITE_TEXT_ALIGNMENT_TRAILING) line_x = x + w - line_w;
        if (line_x < x) line_x = x;
        for (const auto& run : line) {
            draw_run(ctx, run.run, style, line_x, line_y, (std::max)(run.width + 4.0f, 4.0f), line_h, font_scale);
            line_x += run.width;
        }
        line_y += line_h;
    }
}
