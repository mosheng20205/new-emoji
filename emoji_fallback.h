#pragma once
#include <dwrite.h>
#include <string>

void apply_emoji_font_fallback(IDWriteTextLayout* layout, const std::wstring& text);
