#pragma once
#include "element_base.h"

class Space : public Element {
public:
    Space() { mouse_passthrough = true; }
    const wchar_t* type_name() const override { return L"Space"; }
    void paint(RenderContext& ctx) override {}
    Element* hit_test(int x, int y) override { return nullptr; }
    void set_size(int w, int h);
    void get_size(int& w, int& h) const;
};
