#include "emoji_fallback.h"
#include <cstdint>

static const wchar_t* kEmojiFont = L"Segoe UI Emoji";

static uint32_t decode_codepoint(const std::wstring& text, size_t index, size_t& next) {
    wchar_t ch = text[index];
    if (ch >= 0xD800 && ch <= 0xDBFF && index + 1 < text.size()) {
        wchar_t lo = text[index + 1];
        if (lo >= 0xDC00 && lo <= 0xDFFF) {
            next = index + 2;
            return 0x10000u + (((uint32_t)(ch - 0xD800) << 10) | (uint32_t)(lo - 0xDC00));
        }
    }
    next = index + 1;
    return (uint32_t)ch;
}

static bool is_variation_selector(uint32_t cp) {
    return cp == 0xFE0E || cp == 0xFE0F || (cp >= 0xE0100 && cp <= 0xE01EF);
}

static bool is_regional_indicator(uint32_t cp) {
    return cp >= 0x1F1E6 && cp <= 0x1F1FF;
}

static bool is_keycap_base(uint32_t cp) {
    return (cp >= L'0' && cp <= L'9') || cp == L'#' || cp == L'*';
}

static bool is_emoji_modifier(uint32_t cp) {
    return cp >= 0x1F3FB && cp <= 0x1F3FF;
}

static bool is_emoji_tag(uint32_t cp) {
    return cp >= 0xE0020 && cp <= 0xE007F;
}

static bool is_emoji_base(uint32_t cp) {
    return (cp >= 0x1F000 && cp <= 0x1FAFF) ||
           (cp >= 0x1FC00 && cp <= 0x1FFFF) ||
           (cp >= 0x2600  && cp <= 0x27BF)  ||
           (cp >= 0x2B00  && cp <= 0x2BFF)  ||
           (cp >= 0x2300  && cp <= 0x23FF)  ||
           cp == 0x00A9 || cp == 0x00AE || cp == 0x203C || cp == 0x2049 ||
           cp == 0x2122 || cp == 0x2139 || cp == 0x24C2 || cp == 0x3030 ||
           cp == 0x303D || cp == 0x3297 || cp == 0x3299 ||
           (cp >= 0x2194 && cp <= 0x21AA) ||
           (cp >= 0x25AA && cp <= 0x25AB) ||
           cp == 0x25B6 || cp == 0x25C0 || (cp >= 0x25FB && cp <= 0x25FE);
}

static void consume_variation_selector(const std::wstring& text, size_t& index) {
    if (index >= text.size()) return;
    size_t next = index;
    uint32_t cp = decode_codepoint(text, index, next);
    if (is_variation_selector(cp)) index = next;
}

static void consume_emoji_modifiers(const std::wstring& text, size_t& index) {
    while (index < text.size()) {
        size_t next = index;
        uint32_t cp = decode_codepoint(text, index, next);
        if (!is_emoji_modifier(cp)) break;
        index = next;
    }
}

static void consume_emoji_tags(const std::wstring& text, size_t& index) {
    while (index < text.size()) {
        size_t next = index;
        uint32_t cp = decode_codepoint(text, index, next);
        if (!is_emoji_tag(cp)) break;
        index = next;
        if (cp == 0xE007F) break;
    }
}

static void consume_emoji_tail(const std::wstring& text, size_t& index) {
    consume_variation_selector(text, index);
    consume_emoji_modifiers(text, index);
    consume_emoji_tags(text, index);
}

static bool find_emoji_cluster(const std::wstring& text, size_t start, size_t& end) {
    size_t next = start;
    uint32_t cp = decode_codepoint(text, start, next);

    if (is_keycap_base(cp)) {
        size_t keycap_end = next;
        consume_variation_selector(text, keycap_end);
        if (keycap_end < text.size()) {
            size_t mark_next = keycap_end;
            uint32_t mark = decode_codepoint(text, keycap_end, mark_next);
            if (mark == 0x20E3) {
                end = mark_next;
                return true;
            }
        }
        return false;
    }

    if (is_regional_indicator(cp)) {
        end = next;
        if (end < text.size()) {
            size_t second_next = end;
            uint32_t second = decode_codepoint(text, end, second_next);
            if (is_regional_indicator(second)) end = second_next;
        }
        return true;
    }

    if (!is_emoji_base(cp)) return false;

    end = next;
    consume_emoji_tail(text, end);

    while (end < text.size()) {
        size_t joiner_next = end;
        uint32_t joiner = decode_codepoint(text, end, joiner_next);
        if (joiner != 0x200D || joiner_next >= text.size()) break;

        size_t part_next = joiner_next;
        uint32_t part = decode_codepoint(text, joiner_next, part_next);
        if (!is_emoji_base(part) && !is_regional_indicator(part) && !is_keycap_base(part)) break;

        end = part_next;
        consume_emoji_tail(text, end);
    }

    return true;
}

void apply_emoji_font_fallback(IDWriteTextLayout* layout, const std::wstring& text) {
    if (!layout || text.empty()) return;

    size_t i = 0;
    while (i < text.size()) {
        size_t end = i;
        if (!find_emoji_cluster(text, i, end)) {
            decode_codepoint(text, i, end);
            i = end;
            continue;
        }

        DWRITE_TEXT_RANGE range = { (UINT32)i, (UINT32)(end - i) };
        layout->SetFontFamilyName(kEmojiFont, range);
        i = end;
    }
}
