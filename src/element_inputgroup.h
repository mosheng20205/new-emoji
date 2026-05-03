#pragma once
#include "element_base.h"
#include <string>
#include <vector>

class Input;

class InputGroup : public Element {
public:
    enum AddonType {
        AddonNone = 0,
        AddonText = 1,
        AddonButton = 2,
        AddonSelect = 3,
    };

    struct AddonSpec {
        int type = AddonNone;
        int element_id = 0;
        std::wstring text;
        std::wstring emoji;
        int variant = 0;
        std::vector<std::wstring> select_items;
        std::wstring select_placeholder = L"请选择";
        int selected_index = -1;
    };

    int input_element_id = 0;
    int size = 0; // 0 default, 1 medium, 2 small, 3 mini
    bool clearable = false;
    bool password = false;
    bool show_word_limit = false;
    bool autosize = false;
    int min_rows = 0;
    int max_rows = 0;

    AddonSpec prepend;
    AddonSpec append;

    const wchar_t* type_name() const override { return L"InputGroup"; }
    void layout(const Rect& available) override;
    bool accepts_input() const override { return false; }

    void set_input_element_id(int id);
    int addon_element_id(int side) const;
    void set_addon_spec(int side, const AddonSpec& spec);
    void clear_addon_spec(int side);
    void set_options(int next_size, bool next_clearable, bool next_password,
                     bool next_show_word_limit, bool next_autosize,
                     int next_min_rows, int next_max_rows);

    Input* input_child() const;

private:
    AddonSpec* addon_spec_mut(int side);
    const AddonSpec* addon_spec(int side) const;
    int preferred_addon_width(const AddonSpec& spec) const;
    void sync_child_styles() const;
};
