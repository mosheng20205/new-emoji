#pragma once
#include "element_panel.h"

class Container : public Panel {
public:
    Container() { fill_parent = true; }
    const wchar_t* type_name() const override { return L"Container"; }
};
