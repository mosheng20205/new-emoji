#pragma once
#include "element_panel.h"

class Container : public Panel {
public:
    int flow_enabled = 0;
    int flow_direction = 0; // 0 auto, 1 horizontal, 2 vertical
    int flow_gap = 0;
    int actual_direction = 0; // 1 horizontal, 2 vertical
    int flex_align_items = 0;
    int flex_justify_content = 0;

    Container() { fill_parent = true; }
    const wchar_t* type_name() const override { return L"Container"; }
    void layout(const Rect& available) override;
    void apply_dpi_scale(float scale) override;
    void set_flow_options(int enabled, int direction, int gap);
    void set_flex_options(int direction, int gap, int align_items, int justify_content);
    int get_logical_gap() const { return logical_flow_gap; }

private:
    int logical_flow_gap = 0;
};

class ContainerRegion : public Panel {
public:
    enum Role {
        HeaderRole = 1,
        AsideRole = 2,
        MainRole = 3,
        FooterRole = 4
    };

    int region_role = MainRole;
    int horizontal_align = 1; // 0 start, 1 center, 2 end
    int vertical_align = 1;   // 0 start, 1 center, 2 end

    explicit ContainerRegion(int role);
    void paint(RenderContext& ctx) override;
    void set_text_options(int align, int valign);
};

class Header : public ContainerRegion {
public:
    Header() : ContainerRegion(HeaderRole) {}
    const wchar_t* type_name() const override { return L"Header"; }
};

class Aside : public ContainerRegion {
public:
    Aside() : ContainerRegion(AsideRole) {}
    const wchar_t* type_name() const override { return L"Aside"; }
};

class Main : public ContainerRegion {
public:
    Main() : ContainerRegion(MainRole) {}
    const wchar_t* type_name() const override { return L"Main"; }
};

class Footer : public ContainerRegion {
public:
    Footer() : ContainerRegion(FooterRole) {}
    const wchar_t* type_name() const override { return L"Footer"; }
};
