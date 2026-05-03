#pragma once
#include "element_base.h"

class MessageBoxElement : public Element {
public:
    enum Result {
        ResultCancel = 0,
        ResultConfirm = 1,
        ResultClose = -1
    };

    std::wstring title;
    std::wstring confirm_text = L"确定";
    std::wstring cancel_text = L"取消";
    bool show_cancel = false;
    MessageBoxResultCallback result_cb = nullptr;

    const wchar_t* type_name() const override { return L"MessageBox"; }
    void layout(const Rect& available) override;
    void paint(RenderContext& ctx) override;
    void on_mouse_move(int x, int y) override;
    void on_mouse_leave() override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

private:
    enum Part {
        PartNone,
        PartClose,
        PartConfirm,
        PartCancel
    };

    Rect m_dialog_rect;
    Rect m_close_rect;
    Rect m_confirm_rect;
    Rect m_cancel_rect;
    Part m_hover_part = PartNone;
    Part m_press_part = PartNone;
    bool m_close_requested = false;

    float scale() const;
    void update_layout();
    Part part_at(int x, int y) const;
    void request_result(Result result);
    void draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                     bool primary, bool hot, bool pressed);
};
