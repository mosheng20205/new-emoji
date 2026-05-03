#include "element_inputgroup.h"
#include "element_button.h"
#include "element_input.h"
#include "element_select.h"
#include <algorithm>

static int clamp_inputgroup_size(int size) {
    if (size < 0) return 0;
    if (size > 3) return 3;
    return size;
}

static int estimate_text_units(const std::wstring& text, int fallback) {
    int units = fallback;
    if (!text.empty()) {
        units = (int)text.size();
    }
    return units;
}

void InputGroup::set_input_element_id(int id) {
    input_element_id = id;
}

int InputGroup::addon_element_id(int side) const {
    const AddonSpec* spec = addon_spec(side);
    return spec ? spec->element_id : 0;
}

InputGroup::AddonSpec* InputGroup::addon_spec_mut(int side) {
    if (side == 0) return &prepend;
    if (side == 1) return &append;
    return nullptr;
}

const InputGroup::AddonSpec* InputGroup::addon_spec(int side) const {
    if (side == 0) return &prepend;
    if (side == 1) return &append;
    return nullptr;
}

void InputGroup::set_addon_spec(int side, const AddonSpec& spec) {
    if (auto* dest = addon_spec_mut(side)) {
        *dest = spec;
        invalidate();
    }
}

void InputGroup::clear_addon_spec(int side) {
    if (auto* dest = addon_spec_mut(side)) {
        *dest = AddonSpec{};
        invalidate();
    }
}

void InputGroup::set_options(int next_size, bool next_clearable, bool next_password,
                             bool next_show_word_limit, bool next_autosize,
                             int next_min_rows, int next_max_rows) {
    size = clamp_inputgroup_size(next_size);
    clearable = next_clearable;
    password = next_password;
    show_word_limit = next_show_word_limit;
    autosize = next_autosize;
    min_rows = (std::max)(0, next_min_rows);
    max_rows = (std::max)(0, next_max_rows);
    if (max_rows > 0 && min_rows > max_rows) min_rows = max_rows;
    sync_child_styles();
    invalidate();
}

Input* InputGroup::input_child() const {
    for (const auto& child : children) {
        if (child && child->id == input_element_id) {
            return dynamic_cast<Input*>(child.get());
        }
    }
    return nullptr;
}

int InputGroup::preferred_addon_width(const AddonSpec& spec) const {
    if (spec.type == AddonNone || spec.element_id == 0) return 0;
    int scale = size == 3 ? 12 : (size == 2 ? 13 : 14);
    if (spec.type == AddonText) {
        int units = estimate_text_units(spec.text, 5);
        return (std::max)(74, units * scale + 24);
    }
    if (spec.type == AddonButton) {
        int text_units = estimate_text_units(spec.text, spec.emoji.empty() ? 4 : 2);
        int emoji_bonus = spec.emoji.empty() ? 0 : 18;
        return (std::max)(46, text_units * scale + emoji_bonus + 22);
    }
    if (spec.type == AddonSelect) {
        int widest = 5;
        for (const auto& item : spec.select_items) {
            widest = (std::max)(widest, estimate_text_units(item, widest));
        }
        widest = (std::max)(widest, estimate_text_units(spec.select_placeholder, widest));
        return (std::max)(120, widest * scale + 40);
    }
    return 0;
}

void InputGroup::sync_child_styles() const {
    if (auto* input = input_child()) {
        input->set_clearable(clearable);
        input->set_options(input->readonly, password, input->multiline, input->validate_state);
        input->set_visual_options(size, password, show_word_limit, autosize, min_rows, max_rows);
    }

    auto sync_button = [this](const AddonSpec& spec) {
        if (spec.element_id == 0) return;
        for (const auto& child : children) {
            if (!child || child->id != spec.element_id) continue;
            if (auto* button = dynamic_cast<Button*>(child.get())) {
                bool plain = spec.type == AddonText;
                int variant = spec.type == AddonText ? 0 : spec.variant;
                button->set_options(variant, plain ? 1 : 0, 0, 0, 0, size);
            } else if (auto* select = dynamic_cast<Select*>(child.get())) {
                ElementStyle logical_style = select->has_logical_style ? select->logical_style : select->style;
                logical_style.corner_radius = 4.0f;
                logical_style.font_size = size == 3 ? 12.0f : (size == 2 ? 13.0f : 14.0f);
                logical_style.pad_left = size == 3 ? 8 : 10;
                logical_style.pad_right = size == 3 ? 8 : 10;
                logical_style.pad_top = 4;
                logical_style.pad_bottom = 4;
                select->set_logical_style(logical_style);
                select->set_placeholder(spec.select_placeholder);
            }
        }
    };
    sync_button(prepend);
    sync_button(append);
}

void InputGroup::layout(const Rect& available) {
    bounds = available;
    sync_child_styles();

    int prepend_w = preferred_addon_width(prepend);
    int append_w = preferred_addon_width(append);
    int input_x = prepend_w > 0 ? prepend_w - 1 : 0;
    int input_w = bounds.w - input_x - (append_w > 0 ? append_w - 1 : 0);
    if (input_w < 40) input_w = 40;

    for (auto& child : children) {
        if (!child || !child->visible) continue;
        if (child->id == input_element_id) {
            child->bounds = { input_x, 0, input_w, bounds.h };
        } else if (child->id == prepend.element_id) {
            child->bounds = { 0, 0, prepend_w, bounds.h };
        } else if (child->id == append.element_id) {
            child->bounds = { bounds.w - append_w, 0, append_w, bounds.h };
        }
        child->layout(child->bounds);
    }
}
