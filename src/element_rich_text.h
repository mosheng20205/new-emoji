#pragma once
#include "element_base.h"
#include "render_context.h"

std::wstring strip_rich_text_markup(const std::wstring& text, bool rich);

void draw_rich_text(RenderContext& ctx,
                    const std::wstring& text,
                    const ElementStyle& style,
                    Color fallback_color,
                    float x, float y, float w, float h,
                    bool rich,
                    DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                    bool wrap = true,
                    float font_scale = 1.0f,
                    bool vertical_center = false);
